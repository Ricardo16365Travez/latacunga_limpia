"""
Script para cargar datos de prueba en el sistema
"""
import os
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point, Polygon
from apps.incidents.models import Incident
from apps.routes.models import CleaningZone
from apps.notifications.models import Notification

User = get_user_model()

def create_zones():
    """Crear zonas de recolección"""
    print("\n📍 Creando zonas...")
    
    zones_data = [
        {
            'zone_name': 'Centro Histórico',
            'description': 'Zona centro de Latacunga',
            'zone_polygon': Polygon([
                (-78.620, -0.930),
                (-78.610, -0.930),
                (-78.610, -0.940),
                (-78.620, -0.940),
                (-78.620, -0.930),
            ]),
            'priority': 5,
            'frequency': 'daily',
            'status': 'active',
            'estimated_duration_minutes': 120,
        },
        {
            'zone_name': 'San Felipe',
            'description': 'Sector San Felipe',
            'zone_polygon': Polygon([
                (-78.610, -0.925),
                (-78.600, -0.925),
                (-78.600, -0.935),
                (-78.610, -0.935),
                (-78.610, -0.925),
            ]),
            'priority': 4,
            'frequency': 'daily',
            'status': 'active',
            'estimated_duration_minutes': 90,
        },
        {
            'zone_name': 'La Matriz',
            'description': 'Zona comercial La Matriz',
            'zone_polygon': Polygon([
                (-78.625, -0.935),
                (-78.615, -0.935),
                (-78.615, -0.945),
                (-78.625, -0.945),
                (-78.625, -0.935),
            ]),
            'priority': 5,
            'frequency': 'daily',
            'status': 'active',
            'estimated_duration_minutes': 150,
        },
        {
            'zone_name': 'El Loreto',
            'description': 'Zona mixta El Loreto',
            'zone_polygon': Polygon([
                (-78.605, -0.940),
                (-78.595, -0.940),
                (-78.595, -0.950),
                (-78.605, -0.950),
                (-78.605, -0.940),
            ]),
            'priority': 3,
            'frequency': 'weekly',
            'status': 'active',
            'estimated_duration_minutes': 100,
        },
    ]
    
    created_zones = []
    for zone_data in zones_data:
        zone, created = CleaningZone.objects.get_or_create(
            zone_name=zone_data['zone_name'],
            defaults=zone_data
        )
        created_zones.append(zone)
        status = "✓ Creada" if created else "✓ Ya existe"
        print(f"  {status}: {zone.zone_name}")
    
    print(f"\n  Total zonas: {CleaningZone.objects.count()}")
    return created_zones

def create_incidents():
    """Crear incidencias de prueba"""
    print("\n🚨 Creando incidencias...")
    
    # Obtener usuarios para asignar como reportadores
    users = list(User.objects.all()[:5])
    if not users:
        print("  ⚠ No hay usuarios. Ejecuta create_users.py primero")
        return []
    
    incidents_data = [
        {
            'description': 'Acumulación de basura en esquina',
            'location': Point(-78.6174, -0.9350),
            'incident_type': 'ACUMULACION',
            'status': 'REPORTADA',
            'address': 'Av. 5 de Junio y Quito',
            'reporter_kind': 'citizen',
            'reporter_id': None,
        },
        {
            'description': 'Contenedor desbordado',
            'location': Point(-78.6150, -0.9320),
            'incident_type': 'CONTENEDOR',
            'status': 'EN_PROCESO',
            'address': 'Calle Guayaquil y Maldonado',
            'reporter_kind': 'user',
            'reporter_id': users[0].id,
        },
        {
            'description': 'Derrame de residuos orgánicos',
            'location': Point(-78.6200, -0.9380),
            'incident_type': 'DERRAME',
            'status': 'REPORTADA',
            'address': 'Parque Vicente León',
            'reporter_kind': 'citizen',
            'reporter_id': None,
        },
        {
            'description': 'Basura en vía pública',
            'location': Point(-78.6180, -0.9340),
            'incident_type': 'OTRO',
            'status': 'RESUELTA',
            'address': 'Calle Belisario Quevedo',
            'reporter_kind': 'user',
            'reporter_id': users[1].id if len(users) > 1 else users[0].id,
        },
        {
            'description': 'Contenedor dañado necesita reemplazo',
            'location': Point(-78.6220, -0.9400),
            'incident_type': 'CONTENEDOR',
            'status': 'REPORTADA',
            'address': 'Mercado La Merced',
            'reporter_kind': 'citizen',
            'reporter_id': None,
        },
        {
            'description': 'Acumulación en parque público',
            'location': Point(-78.6130, -0.9310),
            'incident_type': 'ACUMULACION',
            'status': 'EN_PROCESO',
            'address': 'Parque San Sebastián',
            'reporter_kind': 'user',
            'reporter_id': users[2].id if len(users) > 2 else users[0].id,
        },
        {
            'description': 'Residuos peligrosos sin recoger',
            'location': Point(-78.6190, -0.9370),
            'incident_type': 'OTRO',
            'status': 'REPORTADA',
            'address': 'Hospital General',
            'reporter_kind': 'citizen',
            'reporter_id': None,
        },
        {
            'description': 'Derrame líquidos no identificados',
            'location': Point(-78.6160, -0.9360),
            'incident_type': 'DERRAME',
            'status': 'RESUELTA',
            'address': 'Terminal Terrestre',
            'reporter_kind': 'user',
            'reporter_id': users[3].id if len(users) > 3 else users[0].id,
        },
    ]
    
    created_incidents = []
    for incident_data in incidents_data:
        # Usar solo campos que existen en el modelo Django
        incident = Incident(
            description=incident_data['description'],
            location=incident_data['location'],
            incident_type=incident_data['incident_type'],
            status=incident_data['status'],
            address=incident_data['address'],
            reporter_kind=incident_data['reporter_kind'],
            reporter_id=incident_data['reporter_id'],
        )
        incident.save()
        created_incidents.append(incident)
        print(f"  ✓ Creada: {incident.incident_type} - {incident.address}")
    
    print(f"\n  Total incidencias: {Incident.objects.count()}")
    return created_incidents

def create_notifications():
    """Crear notificaciones de prueba"""
    print("\n🔔 Creando notificaciones...")
    
    users = list(User.objects.all()[:5])
    if not users:
        print("  ⚠ No hay usuarios disponibles")
        return []
    
    notifications_data = [
        {
            'title': 'Nueva incidencia reportada',
            'message': 'Se ha reportado acumulación de basura en Centro Histórico',
            'notification_type': 'INFO',
            'priority': 'MEDIA',
        },
        {
            'title': 'Tarea completada',
            'message': 'Recolección en Zona San Felipe completada exitosamente',
            'notification_type': 'SUCCESS',
            'priority': 'BAJA',
        },
        {
            'title': 'Vehículo en mantenimiento',
            'message': 'El vehículo PCA-004 requiere mantenimiento preventivo',
            'notification_type': 'WARNING',
            'priority': 'MEDIA',
        },
        {
            'title': 'Incidencia crítica',
            'message': 'Derrame de residuos peligrosos reportado - atención inmediata',
            'notification_type': 'ERROR',
            'priority': 'ALTA',
        },
        {
            'title': 'Ruta optimizada',
            'message': 'Nueva ruta optimizada para Zona La Matriz',
            'notification_type': 'INFO',
            'priority': 'BAJA',
        },
        {
            'title': 'Contenedor lleno',
            'message': 'Contenedor en Av. 5 de Junio alcanzó capacidad máxima',
            'notification_type': 'WARNING',
            'priority': 'MEDIA',
        },
        {
            'title': 'Reporte generado',
            'message': 'Reporte mensual de recolección disponible',
            'notification_type': 'SUCCESS',
            'priority': 'BAJA',
        },
        {
            'title': 'Sistema actualizado',
            'message': 'El sistema se actualizó a la versión 2.0',
            'notification_type': 'INFO',
            'priority': 'BAJA',
        },
        {
            'title': 'Zona sin cubrir',
            'message': 'La Zona El Loreto no fue cubierta en el turno de hoy',
            'notification_type': 'ERROR',
            'priority': 'ALTA',
        },
        {
            'title': 'Personal asignado',
            'message': 'Nuevo personal asignado a turno nocturno',
            'notification_type': 'INFO',
            'priority': 'BAJA',
        },
    ]
    
    created_notifications = []
    for i, notif_data in enumerate(notifications_data):
        notif_data['user'] = users[i % len(users)]
        notif_data['is_read'] = i % 3 == 0  # Algunas leídas, otras no
        
        notification, created = Notification.objects.get_or_create(
            user=notif_data['user'],
            title=notif_data['title'],
            defaults=notif_data
        )
        created_notifications.append(notification)
        status = "✓ Creada" if created else "✓ Ya existe"
        print(f"  {status}: {notification.notification_type} - {notification.title}")
    
    print(f"\n  Total notificaciones: {Notification.objects.count()}")
    return created_notifications

def main():
    """Ejecutar carga de datos"""
    print("=" * 60)
    print("🚀 CARGANDO DATOS DE PRUEBA")
    print("=" * 60)
    
    try:
        # Crear datos básicos
        zones = create_zones()
        incidents = create_incidents()
        
        # Resumen final
        print("\n" + "=" * 60)
        print("✅ CARGA COMPLETADA")
        print("=" * 60)
        print(f"\n  📊 Resumen de datos:")
        print(f"  Zonas:           {CleaningZone.objects.count()}")
        print(f"  Incidencias:     {Incident.objects.count()}")
        print(f"  Usuarios:        {User.objects.count()}")
        
        print(f"\n  🎯 Estado de incidencias:")
        for status in ['REPORTADA', 'EN_PROCESO', 'RESUELTA', 'CANCELADA']:
            count = Incident.objects.filter(status=status).count()
            if count > 0:
                print(f"    {status}: {count}")
        
        print("\n" + "=" * 60)
        print("🎉 Sistema listo para pruebas")
        print("=" * 60)
        print("\n  Accede al sistema:")
        print("  Frontend: http://localhost:3001")
        print("  Backend:  http://localhost:8000")
        print("  Admin:    admin@latacunga.gob.ec / admin123")
        print()
        
    except Exception as e:
        print(f"\n❌ Error durante la carga: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
