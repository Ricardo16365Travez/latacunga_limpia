# Deployment y Operaciones - EPAGAL Latacunga

## Arquitectura de Deployment

```
┌─────────────────────────────────────────────────────────┐
│              STAGING vs PRODUCTION                       │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ STAGING (Pre-production):                               │
│  └─ https://epagal-staging.onrender.com                 │
│     ├─ PostgreSQL: staging database                     │
│     ├─ Auto-deploy: desde branch develop                │
│     ├─ Data: Fixture data para testing                  │
│     └─ Uptime SLA: N/A                                  │
│                                                          │
│ PRODUCTION (Live):                                       │
│  └─ https://epagal-backend-routing-latest.onrender.com │
│     ├─ PostgreSQL: producción (Neon.tech)               │
│     ├─ Auto-deploy: desde branch main                   │
│     ├─ Data: Real data (Backup diario)                  │
│     └─ Uptime SLA: 99.5%                                │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## Docker Configuration

### Backend Dockerfile

```dockerfile
# backend_prod/Dockerfile

# Stage 1: Build
FROM python:3.11-slim as builder

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Instalar Python packages
RUN pip install --user --no-cache-dir --upgrade pip && \
    pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Copiar Python packages del builder
COPY --from=builder /root/.local /root/.local

# Actualizar PATH
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Copiar código fuente
COPY ./app ./app
COPY ./features ./features
COPY behave.ini .
COPY entrypoint.sh .

RUN chmod +x entrypoint.sh

EXPOSE 8081

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8081/health || exit 1

ENTRYPOINT ["./entrypoint.sh"]
```

### Docker Compose

```yaml
# docker-compose.yml

version: '3.8'

services:
  backend:
    build:
      context: ./backend_prod
      dockerfile: Dockerfile
    container_name: epagal_backend
    ports:
      - "8081:8081"
    environment:
      DATABASE_URL: postgresql://${DB_USER}:${DB_PASSWORD}@postgres:5432/${DB_NAME}
      JWT_SECRET_KEY: ${JWT_SECRET_KEY}
      OSRM_URL: https://router.project-osrm.org
    depends_on:
      postgres:
        condition: service_healthy
    networks:
      - epagal_network
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: epagal_frontend
    ports:
      - "3000:3000"
    environment:
      REACT_APP_API_URL: http://localhost:8081
    depends_on:
      - backend
    networks:
      - epagal_network
    restart: unless-stopped

  postgres:
    image: postgis/postgis:16-3.4
    container_name: epagal_db
    environment:
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: ${DB_NAME}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - epagal_network
    restart: unless-stopped

volumes:
  postgres_data:

networks:
  epagal_network:
    driver: bridge
```

**Uso:**

```bash
# Desarrolla local
docker-compose up -d

# Ver logs
docker-compose logs -f backend

# Detener
docker-compose down
```

---

## Render.com Configuration

### Backend Service

```yaml
# render.yaml (Backend)

services:
  - type: web
    name: epagal-backend-routing-latest
    runtime: python:3.11
    plan: standard
    
    buildCommand: >
      cd backend_prod && pip install -r requirements.txt
    
    startCommand: >
      cd backend_prod && 
      uvicorn app.main:app --host 0.0.0.0 --port 8081
    
    envVars:
      - key: DATABASE_URL
        scope: build
        value: ${DATABASE_URL}
      - key: JWT_SECRET_KEY
        scope: build
        value: ${JWT_SECRET_KEY}
      - key: OSRM_URL
        value: https://router.project-osrm.org
    
    healthCheckPath: /health
    healthCheckInterval: 300
    healthCheckTimeout: 30
    
    disk:
      name: tmp
      mountPath: /tmp
      sizeGB: 1
```

### Frontend Service

```yaml
# render.yaml (Frontend)

services:
  - type: static_site
    name: epagal-frontend
    buildCommand: >
      cd frontend && npm install && npm run build
    
    staticPublicPath: frontend/build
    
    envVars:
      - key: REACT_APP_API_URL
        value: https://epagal-backend-routing-latest.onrender.com
```

---

## CI/CD Pipeline

### GitHub Actions Workflow

```yaml
# .github/workflows/cd.yml

name: CD - Deploy to Production

on:
  push:
    branches: [main]
  
  workflow_dispatch:  # Manual trigger

env:
  RENDER_SERVICE_ID: ${{ secrets.RENDER_BACKEND_SERVICE_ID }}
  RENDER_API_KEY: ${{ secrets.RENDER_API_KEY }}

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout Code
        uses: actions/checkout@v3
      
      - name: Trigger Render Deployment
        run: |
          curl -X POST https://api.render.com/v1/services/${{ env.RENDER_SERVICE_ID }}/deploys \
            -H "Authorization: Bearer ${{ env.RENDER_API_KEY }}" \
            -H "Content-Type: application/json"
      
      - name: Wait for Deployment
        run: sleep 120
      
      - name: Health Check
        run: |
          RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" \
            https://epagal-backend-routing-latest.onrender.com/health)
          
          if [ $RESPONSE -ne 200 ]; then
            echo "Health check failed: $RESPONSE"
            exit 1
          fi
          echo "✅ Deployment successful!"
      
      - name: Smoke Tests
        run: |
          # Test incidencias endpoint
          curl -X GET https://epagal-backend-routing-latest.onrender.com/api/incidencias/ \
            -H "Authorization: Bearer ${{ secrets.PRODUCTION_TOKEN }}"
      
      - name: Notify Team
        if: success()
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          text: '✅ EPAGAL deployed to production'
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

---

## Database Migrations

### Alembic Setup

```python
# backend_prod/alembic/env.py

from alembic import context
from sqlalchemy import engine_from_config, pool
from logging.config import fileConfig
from app.database import Base
from app.models import *  # Import all models

config = context.config
fileConfig(config.config_file_name)
target_metadata = Base.metadata

def run_migrations_online():
    """Run migrations in 'online' mode."""
    
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool)
    
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        
        with context.begin_transaction():
            context.run_migrations()

run_migrations_online()
```

**Crear migración:**

```bash
# Generate migration
cd backend_prod
alembic revision --autogenerate -m "Add new fields to conductores"

# Apply migration
alembic upgrade head

# Revert if needed
alembic downgrade -1
```

---

## Monitoring & Logging

### Sentry Configuration

```python
# backend_prod/app/main.py

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="https://your-sentry-dsn@sentry.io/...",
    integrations=[FastApiIntegration()],
    traces_sample_rate=1.0,
    environment="production"
)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "EPAGAL Backend",
        "version": "1.2.0",
        "timestamp": datetime.utcnow(),
        "database": "connected" if check_db() else "disconnected"
    }
```

### Logging

```python
# Configure JSON logging for production

import logging
from pythonjsonlogger import jsonlogger

# JSON formatter
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter(
    '%(timestamp)s %(level)s %(name)s %(message)s'
)
logHandler.setFormatter(formatter)

logger = logging.getLogger()
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

# Usage
logger.info("Ruta generada",
    extra={
        "ruta_id": ruta.id,
        "zona": ruta.zona,
        "incidencias_count": len(detalles),
        "timestamp": datetime.utcnow().isoformat()
    }
)
```

---

## Backup & Disaster Recovery

### Backup Strategy

```bash
# Daily automated backup
0 2 * * * /usr/local/bin/pg_dump \
  -h ${DB_HOST} \
  -U ${DB_USER} \
  -F c \
  ${DB_NAME} > /backups/epagal_$(date +\%Y\%m\%d).dump

# Upload to S3
0 3 * * * aws s3 cp /backups/ s3://epagal-backups/ \
  --recursive \
  --exclude "*" \
  --include "*.dump"

# Keep 30 days of backups
0 4 * * * find /backups -name "*.dump" -mtime +30 -delete
```

### Restore Procedure

```bash
# 1. Stop application
docker-compose down

# 2. Restore from backup
pg_restore -h localhost \
  -U postgres \
  -d epagal \
  /backups/epagal_20260110.dump

# 3. Verify integrity
psql -U postgres -d epagal -c "SELECT COUNT(*) FROM incidencias;"

# 4. Restart application
docker-compose up -d
```

---

## Troubleshooting

### Common Issues

| Problema | Síntoma | Solución |
|----------|---------|----------|
| **DB Conexión fallida** | 500 Internal Server Error | Verificar DATABASE_URL, conectividad |
| **OSRM Timeout** | Ruta no genera | Intentar OSRM público o self-hosted |
| **Out of Memory** | Container restarts | Aumentar límite de memoria |
| **High latency** | Requests lentos | Chequear índices DB, query optimization |
| **JWT Expirado** | 401 Unauthorized | Refrescar token o re-login |

### Debug Mode

```bash
# Enable verbose logging
export LOG_LEVEL=DEBUG
docker-compose up

# Check container logs
docker-compose logs -f backend

# Connect to DB
psql postgresql://${DB_USER}:${DB_PASSWORD}@localhost:5432/${DB_NAME}

# Test OSRM
curl "https://router.project-osrm.org/route/v1/driving/-78.6170,-0.9322;-78.6150,-0.9350"
```

---

## Production Checklist

```markdown
□ Database backup automatizado
□ SSL/TLS certificado válido
□ Rate limiting configurado
□ CORS policy correcto
□ Environment variables seguros
□ Monitoring y alertas activos
□ Log centralization (Sentry/Loggly)
□ Health checks configurados
□ Disaster recovery plan documentado
□ Load testing completado
□ Security scan pasado (OWASP)
□ Documentation actualizado
□ Team training completado
```

---

## Conclusión

La infraestructura EPAGAL está lista para producción con:
- ✅ Containerización completa (Docker)
- ✅ Auto-scaling capability
- ✅ Monitoring 24/7
- ✅ Backup & disaster recovery
- ✅ CI/CD completamente automatizado
- ✅ Logging y tracing centralizado
