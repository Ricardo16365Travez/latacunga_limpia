#!/bin/bash
# Script de despliegue para Render
# Este script se ejecuta durante el build en Render

set -e

echo "=== 🚀 RENDER DEPLOYMENT SCRIPT ==="
echo "Step 1: Installing dependencies..."
cd /app/backend
pip install --no-cache-dir -r requirements.txt

echo "Step 2: Running migrations..."
python manage.py migrate --no-input || true

echo "Step 3: Collecting static files..."
python manage.py collectstatic --noinput --clear || true

echo "Step 4: Creating superuser if needed..."
python << END
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

# Check if admin exists
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(
        username='admin',
        email='admin@latacunga.gob.ec',
        password='admin123'
    )
    print("✅ Admin user created")
else:
    print("✅ Admin user already exists")
END

echo "Step 5: Loading sample data..."
python load_sample_data.py || true

echo "✅ Deployment preparation complete!"
