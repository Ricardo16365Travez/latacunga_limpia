# Stack Tecnológico - EPAGAL Latacunga

## Resumen Ejecutivo

| Capa | Tecnología | Versión | Justificación |
|------|------------|---------|---------------|
| **Backend** | FastAPI | 0.115.5 | Rendimiento, async, validación automática |
| **Database** | PostgreSQL + PostGIS | 16 / 3.4 | ACID, geoespacial, open-source |
| **Frontend** | React + TypeScript | 18.3.1 / 4.9.5 | Ecosistema, type-safety |
| **ORM** | SQLAlchemy | 2.0.36 | Flexibility, migrations |
| **Auth** | JWT + Passlib | - | Stateless, bcrypt hashing |
| **API Routing** | OSRM | Latest | Optimización de rutas, open-source |
| **DevOps** | Docker + Render.com | Latest | Containerización, deploy simple |
| **CI/CD** | GitHub Actions | - | Integrado con GitHub |
| **Testing** | Pytest + Behave | - | Unit testing, BDD |

---

## Backend Stack

### FastAPI 0.115.5
**Por qué:** 
- Performance 10x vs Django/Flask (ASGI)
- Type hints + Pydantic validation
- Async/await nativo
- Auto-documentation (Swagger)

```python
# Ejemplo de ventajas
@router.post("/incidencias/", response_model=IncidenciaResponse)
async def crear_incidencia(
    inc: IncidenciaCreate,  # Validado automáticamente
    db: Session = Depends(get_db),  # Inyección de dependencias
    user: Usuario = Depends(get_current_user)  # Auth automático
) -> IncidenciaResponse:
    pass
```

### SQLAlchemy 2.0.36
**Características:**
- ORM declarativo
- Lazy/eager loading
- Relationship management
- Query API moderna (2.0+)

### PostgreSQL 16 + PostGIS 3.4
**Ventajas Geoespaciales:**
```sql
-- Consultas espaciales
SELECT * FROM incidencias
WHERE ST_DWithin(location, point, 1000);  -- 1km radio

-- Distancias
SELECT ST_Distance(loc1, loc2)::geography AS distance_m;
```

### Uvicorn + Gunicorn
- **Uvicorn**: ASGI server (desarrollo)
- **Gunicorn**: Production (con workers)

```bash
# Producción
gunicorn -w 4 -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8081 app.main:app
```

---

## Frontend Stack

### React 18.3.1
**Razones:**
- Hooks API moderno
- Virtual DOM eficiente
- Comunidad gigante
- Integración TypeScript perfecta

### TypeScript 4.9.5
**Beneficios:**
- Type safety en compile-time
- Mejor IDE autocomplete
- Documentación viva
- Menos bugs en producción

```typescript
interface Ruta {
  id: number;
  zona: 'oriental' | 'occidental';
  suma_gravedad: number;
  estado: 'planeada' | 'en_ejecucion' | 'completada';
}

// Error en compile-time si zona !== 'oriental' | 'occidental'
const ruta: Ruta = {
  zona: 'centro'  // ❌ Error: Type '"centro"' is not assignable
};
```

### Material-UI 6.2.0
**Componentes:**
- Button, Card, Dialog, DataGrid
- Theming system
- Responsive design
- Accesibilidad (A11y)

### React Router 7.1.1
**Routing:**
```typescript
<BrowserRouter>
  <Routes>
    <Route path="/" element={<Dashboard />} />
    <Route path="/rutas/:id" element={<RutaDetalle />} />
    <Route path="*" element={<NotFound />} />
  </Routes>
</BrowserRouter>
```

### Axios 1.7.9
**HTTP Client:**
```typescript
const api = axios.create({
  baseURL: 'https://api.epagal.com',
  headers: { Authorization: `Bearer ${token}` }
});

const response = await api.get('/incidencias');
```

### Leaflet 1.9.4
**Mapeo:**
- Markers con popups
- Polylines para rutas
- Clustering de puntos
- Custom tile layers

### Recharts 2.15.0
**Gráficos:**
- Line charts (tendencias)
- Bar charts (comparativas)
- Pie charts (distribución)

---

## DevOps Stack

### Docker & Docker Compose

**Backend Dockerfile:**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ./app ./app
EXPOSE 8081
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8081"]
```

**Docker Compose:**
```yaml
version: '3.8'
services:
  backend:
    build: ./backend_prod
    ports:
      - "8081:8081"
    environment:
      DATABASE_URL: postgresql://user:pass@postgres:5432/epagal
    depends_on:
      - postgres
  
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
  
  postgres:
    image: postgis/postgis:16-3.4
    environment:
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### GitHub Actions

**Triggers:**
- Push a main/develop
- Pull requests
- Scheduled (nightly tests)

**Jobs:**
1. Lint & Format
2. Unit Tests
3. Integration Tests
4. BDD Tests
5. Docker Build
6. Deploy (si es main)

### Render.com

**Ventajas:**
- Auto-deploy desde GitHub
- SSL automático
- PostgreSQL incluida
- Free tier para demo

**Configuración:**
```yaml
# render.yaml
services:
  - type: web
    name: epagal-backend
    runtime: python:3.11
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0
    envVars:
      - key: DATABASE_URL
        value: postgresql://...
```

---

## Herramientas de Desarrollo

### Testing
| Herramienta | Propósito |
|------------|-----------|
| **pytest** | Unit testing (backend) |
| **Behave** | BDD / Cucumber (Python) |
| **Jest** | Unit testing (frontend) |
| **React Testing Library** | Component testing |
| **pytest-cov** | Coverage reporting |

### Linting & Formatting
| Herramienta | Para | Config |
|------------|------|--------|
| **Flake8** | Python | max-line-length=100 |
| **Black** | Python | Formatter automático |
| **ESLint** | JavaScript/TypeScript | Airbnb config |
| **Prettier** | JS/TS/CSS | Formatter automático |

### Version Control
```bash
# Git Flow Strategy
main       ← producción (releases)
develop    ← integración (merges de features)
feature/*  ← desarrollo (User Stories)
hotfix/*   ← fixes críticos

# Convenciones
feat(scope): description
fix(scope): description
docs: update README
test: add unit tests
```

### Database Tools
- **pgAdmin**: GUI para PostgreSQL
- **DBeaver**: Query tool universal
- **Alembic**: Migrations para SQLAlchemy
- **Adminer**: Web-based DB admin

### Monitoring
- **Sentry**: Error tracking
- **DataDog**: Infrastructure monitoring
- **New Relic**: Application performance
- **LogRocket**: Session replay (frontend)

---

## Comparativa de Alternativas

### FastAPI vs Django vs Flask

```
                FastAPI    Django    Flask
────────────────────────────────────────────
Performance     ⭐⭐⭐⭐⭐  ⭐⭐⭐     ⭐⭐⭐
Learning Curve  ⭐⭐⭐     ⭐⭐      ⭐⭐⭐⭐
Built-in ORM    ❌        ✅ ORM     ❌
Async Support   ✅ Nativo ⚠️ Limitado ⚠️
Documentation   ✅ Excelente ✅ Excelente ✅ Buena
Community       ✅ Creciente ✅ Enorme   ✅ Buena
Type Hints      ✅ Integrado ❌        ❌
Auto API Docs   ✅ Swagger ⚠️ Third-party ❌
Best For        APIs modernas  Monolitos  Prototipes
```

**Decisión:** FastAPI porque necesitamos API de alto rendimiento con validación automática.

### React vs Vue vs Angular

```
                React      Vue        Angular
────────────────────────────────────────────
Learning Curve  ⭐⭐⭐     ⭐⭐⭐⭐    ⭐⭐
Bundle Size     ⭐⭐⭐     ⭐⭐⭐⭐    ⭐⭐
Performance     ⭐⭐⭐⭐   ⭐⭐⭐⭐    ⭐⭐⭐
Ecosystem       ⭐⭐⭐⭐⭐  ⭐⭐⭐     ⭐⭐⭐
TypeScript      ✅ Excelente ✅ Bueno ✅ Excelente
Community Size  ✅ Enorme   ✅ Grande  ✅ Grande
Job Market      ⭐⭐⭐⭐⭐  ⭐⭐⭐     ⭐⭐⭐⭐
Flexibility     ⭐⭐⭐⭐⭐  ⭐⭐⭐⭐    ⭐⭐
```

**Decisión:** React por ecosistema, TypeScript support, y demanda laboral.

### PostgreSQL vs MongoDB vs MySQL

```
                PostgreSQL  MongoDB    MySQL
─────────────────────────────────────────────
ACID Compliance ✅ Completo  ⚠️ Multi-doc  ✅
Relational      ✅ Excelente ❌         ✅
Geospatial      ✅ PostGIS   ❌         ⚠️ Limitado
JSON Support    ✅ Nativo    ✅ Nativo    ⚠️
Scaling         ⭐⭐⭐     ⭐⭐⭐⭐    ⭐⭐⭐
Transactions    ✅ Full ACID ⚠️ Sessions  ✅
Open Source     ✅           ✅         ✅
Cost            ✅ Gratuito   ✅ Gratuito  ✅ Gratuito
```

**Decisión:** PostgreSQL + PostGIS porque nuestro dominio es geoespacial.

---

## Requisitos del Sistema

### Backend Server
- **OS:** Linux (Render), Windows/Mac (desarrollo)
- **Python:** 3.11+
- **RAM:** 512 MB mínimo, 2 GB recomendado
- **CPU:** 1 core mínimo, 2+ recomendado
- **Disk:** 2 GB para código + dependencias

### Database
- **PostgreSQL:** 16+
- **RAM:** 1 GB mínimo
- **Storage:** 10 GB inicialmente, escalable
- **Conexión:** 50 concurrent connections

### Frontend Build
- **Node.js:** 18+
- **npm:** 9+
- **Disk:** 2 GB node_modules, 100 MB build output

### Browser Support
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+
- Mobile: iOS Safari 14+, Chrome Android

---

## Licencias y Compliance

| Tecnología | Licencia | Uso Comercial | Modificación |
|-----------|----------|:-------------:|:------------:|
| FastAPI | MIT | ✅ | ✅ |
| React | MIT | ✅ | ✅ |
| PostgreSQL | PostgreSQL | ✅ | ✅ |
| Docker | Apache 2.0 | ✅ | ✅ |
| Material-UI | MIT | ✅ | ✅ |
| Leaflet | BSD-2 | ✅ | ✅ |

**Conclusión:** Todas las licencias permiten uso comercial y modificación. Proyecto totalmente open-source compatible.

---

## Plan de Actualización

```
2026 Q1: Upgrading
├─► Python 3.12 (cuando Render lo soporte)
├─► FastAPI 0.120+
├─► React 19 (cuando sea estable)
└─► PostgreSQL 17

2026 Q2-Q3: Features
├─► WebSockets para real-time tracking
├─► GraphQL como alternativa a REST
├─► Kubernetes para horizontal scaling
└─► Mobile app nativa (React Native)

2026 Q4+: Optimization
├─► Machine Learning para predicción de rutas
├─► Caching distribuido con Redis
├─► Serverless functions (AWS Lambda)
└─► Multi-tenancy support
```

---

**Conclusión:** El stack tecnológico elegido es moderno, escalable, open-source y está optimizado para el dominio de gestión de residuos sólidos con componente geoespacial importante.
