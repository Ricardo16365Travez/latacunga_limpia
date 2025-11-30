import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection

cursor = connection.cursor()

print("\n📊 Conteo de datos en Supabase:\n")

# Contar incidents
cursor.execute("SELECT COUNT(*) FROM public.incidents")
incidents = cursor.fetchone()[0]
print(f"  Incidencias: {incidents}")

# Contar cleaning_zones
cursor.execute("SELECT COUNT(*) FROM public.cleaning_zones")
zones = cursor.fetchone()[0]
print(f"  Zonas: {zones}")

# Contar users
cursor.execute("SELECT COUNT(*) FROM public.users")
users = cursor.fetchone()[0]
print(f"  Usuarios: {users}")

# Contar routes
cursor.execute("SELECT COUNT(*) FROM public.routes")
routes = cursor.fetchone()[0]
print(f"  Rutas: {routes}")

# Contar tasks
cursor.execute("SELECT COUNT(*) FROM public.tasks")
tasks = cursor.fetchone()[0]
print(f"  Tareas: {tasks}")

print(f"\n  Total registros: {incidents + zones + users + routes + tasks}")

if incidents > 0:
    print("\n📍 Muestra de incidencias:")
    cursor.execute("SELECT incident_type, status, address FROM public.incidents LIMIT 3")
    for row in cursor.fetchall():
        print(f"    - {row[0]}: {row[1]} en {row[2]}")

if zones > 0:
    print("\n🗺️ Muestra de zonas:")
    cursor.execute("SELECT zone_name, priority, frequency FROM public.cleaning_zones LIMIT 3")
    for row in cursor.fetchall():
        print(f"    - {row[0]}: Prioridad {row[1]}, {row[2]}")

print()
