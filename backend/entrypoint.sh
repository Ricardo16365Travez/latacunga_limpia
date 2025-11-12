#!/bin/bash

# Esperar a que la base de datos esté disponible
echo "Esperando a que la base de datos esté disponible..."
while ! python -c "import psycopg2; psycopg2.connect(host='db', port=5432, user='postgres', password='postgres123', dbname='residuos_latacunga')" 2>/dev/null; do
  sleep 1
done
echo "Base de datos disponible!"

# Ejecutar migraciones
echo "Ejecutando migraciones..."
python manage.py migrate --noinput

# Crear superusuario si no existe
echo "Creando superusuario..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email='admin@residuos.com').exists():
    User.objects.create_superuser('admin@residuos.com', 'admin123')
    print('Superusuario creado')
else:
    print('Superusuario ya existe')
"

# Colectar archivos estáticos
echo "Colectando archivos estáticos..."
python manage.py collectstatic --noinput

# Iniciar servidor
echo "Iniciando servidor Django..."
python manage.py runserver 0.0.0.0:8000