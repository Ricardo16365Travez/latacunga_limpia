# Dockerfile de entrada para Render
# Este archivo es necesario para que Render detecte correctamente el proyecto
# El build real se hace en backend/Dockerfile

# Usar imagen base de Python
FROM python:3.11-slim as base

WORKDIR /app

# Instalar dependencias del sistema necesarias para PostgreSQL + GeoDjango
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gdal-bin \
    libgdal-dev \
    libgeos-dev \
    libproj-dev \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Stage de construcción
FROM base as builder

# Copiar requirements
COPY backend/requirements.txt /tmp/requirements.txt

# Instalar dependencias Python
RUN pip install --user --no-cache-dir -r /tmp/requirements.txt

# Stage final
FROM base

# Copiar usuario pip del builder
COPY --from=builder /root/.local /root/.local

# Actualizar PATH
ENV PATH=/root/.local/bin:$PATH

# Copiar todo el proyecto
COPY . .

# Variables de entorno para Django
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV DJANGO_SETTINGS_MODULE=config.settings

# Crear directorio para archivos estáticos
RUN mkdir -p /app/backend/staticfiles /app/backend/media

# Exponer puerto (Render usa 10000)
EXPOSE 10000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:10000/health/ || exit 1

# Comando de inicio
WORKDIR /app/backend

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:10000", "--workers", "2", "--timeout", "120"]
