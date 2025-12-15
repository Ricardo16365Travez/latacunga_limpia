# Dockerfile para desplegar Backend en Render
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend ./backend
COPY database ./database

# Create necessary directories
RUN mkdir -p /app/backend/logs /app/backend/media

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=config.settings
ENV PORT=8000

EXPOSE 8000

# Run migrations and start server
CMD ["sh", "-c", "cd /app/backend && python manage.py migrate --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:${PORT} --workers 4 --timeout 60 --access-logfile - --error-logfile -"]
