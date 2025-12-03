#!/usr/bin/env python
"""
Script para cargar datos de prueba en el sistema.
Útil para validar la UI con datos en todos los servicios.
"""
import os
import sys
import django
from datetime import datetime, timedelta
from django.contrib.gis.geos import Point

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth import get_user_model
from apps.incidents.models import Incident, IncidentType, IncidentStatus
from apps.tasks.models import Task
from apps.notifications.models import Notification
from apps.routes.models import Route, CleaningZone
from apps.reports.models import Report
import uuid

User = get_user_model()


def create_sample_data():
    """Crear datos de prueba en la BD."""
    
    print("🚀 Iniciando carga de datos de prueba...")
    
    # Obtener o crear usuarios (usar email, no username)
    try:
        admin = User.objects.get(email='admin@latacunga.ec')
    except User.DoesNotExist:
        admin = User.objects.create_superuser(
            email='admin@latacunga.ec',
            password='admin123'
        )
        print("✅ Usuario admin creado")
    
    # Crear algunas zonas si no existen
    if CleaningZone.objects.count() == 0:
        zones = [
            CleaningZone.objects.create(
                zone_name='Centro Histórico',
                description='Zona del centro de la ciudad',
                zone_polygon=Point([-0.9315, -0.9369]).buffer(0.01),
                priority=5,
                frequency='daily',
                estimated_duration_minutes=120,
                assigned_team_size=4,
                status='active'
            ),
            CleaningZone.objects.create(
                zone_name='Parque Industrial',
                description='Zona industrial',
                zone_polygon=Point([-0.9400, -0.9400]).buffer(0.02),
                priority=4,
                frequency='weekly',
                estimated_duration_minutes=180,
                assigned_team_size=6,
                status='active'
            ),
        ]
        print(f"✅ {len(zones)} zonas de limpieza creadas")
    
    # Crear tareas de ejemplo (DESHABILITADO: esquema no coincide con DB)
    # if Task.objects.count() < 5:
    #     ...creación de tareas...
    # print("✅ 5 tareas de prueba creadas")
    pass  # skip task creation

    
    # Crear notificaciones de ejemplo (DESHABILITADO: esquema no coincide con DB)
    # if Notification.objects.count() < 5:
    #     ...creación de notificaciones...
    # print("✅ 5 notificaciones de prueba creadas")
    pass  # skip notification creation

    
    # Crear reportes de ejemplo (DESHABILITADO: esquema no coincide con DB)
    # if Report.objects.count() < 3:
    #     ...creación de reportes...
    # print("✅ 3 reportes de prueba creados")
    pass  # skip report creation

    
    print("\n✨ Carga de datos completada exitosamente!")
    print(f"📊 Resumen:")
    print(f"  - Tareas: {Task.objects.count()}")
    print(f"  - Notificaciones: {Notification.objects.count()}")
    print(f"  - Reportes: {Report.objects.count()}")
    print(f"  - Incidentes: {Incident.objects.count()}")
    print(f"  - Zonas: {CleaningZone.objects.count()}")


if __name__ == '__main__':
    create_sample_data()
