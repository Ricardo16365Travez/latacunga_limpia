"""
Script automatizado para poblar la base de datos Neon con datos de ejemplo
"""
import os
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import uuid
import bcrypt

# Leer DB_URL del archivo .env
DB_URL = "postgresql://neondb_owner:npg_jnw3bVupEP5i@ep-gentle-pond-adcmrdsv-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

print("=" * 80)
print("CONFIGURACIÓN BASE DE DATOS NEON - EPAGAL LATACUNGA")
print("=" * 80)
print(f"\n✅ Conectando a Neon: {DB_URL[:60]}...")

try:
    engine = create_engine(DB_URL, pool_pre_ping=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    session.execute(text("SELECT 1"))
    print("✅ Conexión exitosa a Neon\n")
except Exception as e:
    print(f"❌ Error de conexión: {e}")
    exit(1)

# Verificar tablas
print("=" * 80)
print("VERIFICANDO TABLAS EXISTENTES")
print("=" * 80)

inspector = inspect(engine)
existing_tables = inspector.get_table_names()

print(f"\n📋 Tablas encontradas ({len(existing_tables)}):")
for table in sorted(existing_tables):
    print(f"   ✓ {table}")

# Cargar datos
print("\n" + "=" * 80)
print("INSERTANDO DATOS DE EJEMPLO")
print("=" * 80)

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# 1. USUARIOS
print("\n1️⃣  Usuarios...")
usuarios_data = [
    {
        "id": str(uuid.uuid4()),
        "email": "admin@epagal.gob.ec",
        "username": "admin",
        "password_hash": hash_password("Admin123!"),
        "role": "ADMIN",
        "display_name": "Administrador EPAGAL",
        "phone": "+593987654321",
        "is_active": True,
        "status": "ACTIVE"
    },
    {
        "id": str(uuid.uuid4()),
        "email": "operador1@epagal.gob.ec",
        "username": "operador1",
        "password_hash": hash_password("Operador123!"),
        "role": "OPERADOR",
        "display_name": "Juan Pérez Operador",
        "phone": "+593987654322",
        "is_active": True,
        "status": "ACTIVE"
    },
    {
        "id": str(uuid.uuid4()),
        "email": "operador2@epagal.gob.ec",
        "username": "operador2",
        "password_hash": hash_password("Operador123!"),
        "role": "OPERADOR",
        "display_name": "María González",
        "phone": "+593987654323",
        "is_active": True,
        "status": "ACTIVE"
    },
]

for user in usuarios_data:
    try:
        session.execute(text("""
            INSERT INTO users (id, email, username, password_hash, role, display_name, 
                             phone, is_active, status, created_at, updated_at)
            VALUES (:id, :email, :username, :password_hash, :role, :display_name,
                    :phone, :is_active, :status, NOW(), NOW())
            ON CONFLICT (email) DO NOTHING
        """), user)
        print(f"   ✓ {user['display_name']} ({user['email']})")
    except Exception as e:
        print(f"   ⚠️  {user['username']}: {str(e)[:60]}")

session.commit()

# 2. CONDUCTORES
print("\n2️⃣  Conductores...")
conductores_data = [
    {"cedula": "1803456789", "nombre_completo": "Carlos Martínez", "email": "carlos.m@epagal.gob.ec", 
     "telefono": "+593998765432", "username": "cmartinez", "licencia_tipo": "C", "zona_preferida": "ORIENTAL"},
    {"cedula": "1804567890", "nombre_completo": "Luis Vega", "email": "luis.v@epagal.gob.ec",
     "telefono": "+593998765433", "username": "lvega", "licencia_tipo": "D", "zona_preferida": "OCCIDENTAL"},
    {"cedula": "1805678901", "nombre_completo": "Pedro Rojas", "email": "pedro.r@epagal.gob.ec",
     "telefono": "+593998765434", "username": "projas", "licencia_tipo": "C", "zona_preferida": "ORIENTAL"},
]

for conductor in conductores_data:
    try:
        session.execute(text("""
            INSERT INTO conductores (cedula, nombre_completo, email, telefono, username,
                                   licencia_tipo, zona_preferida, estado, created_at)
            VALUES (:cedula, :nombre_completo, :email, :telefono, :username,
                    :licencia_tipo, :zona_preferida, 'disponible', NOW())
            ON CONFLICT (cedula) DO NOTHING
        """), conductor)
        print(f"   ✓ {conductor['nombre_completo']}")
    except Exception as e:
        print(f"   ⚠️  {str(e)[:60]}")

session.commit()

# 3. VEHÍCULOS
print("\n3️⃣  Vehículos...")
vehiculos_data = [
    {"placa": "PBC-1234", "marca": "Hino", "modelo": "Serie 300", "capacidad_toneladas": 7.5, "año": 2020},
    {"placa": "PBC-5678", "marca": "Chevrolet", "modelo": "NPR", "capacidad_toneladas": 5.0, "año": 2021},
    {"placa": "PBC-9012", "marca": "International", "modelo": "4300", "capacidad_toneladas": 10.0, "año": 2019},
]

for v in vehiculos_data:
    try:
        session.execute(text("""
            INSERT INTO vehiculos (placa, marca, modelo, capacidad_toneladas, año, estado, created_at)
            VALUES (:placa, :marca, :modelo, :capacidad_toneladas, :año, 'disponible', NOW())
            ON CONFLICT (placa) DO NOTHING
        """), v)
        print(f"   ✓ {v['placa']} - {v['marca']} {v['modelo']}")
    except Exception as e:
        print(f"   ⚠️  {str(e)[:60]}")

session.commit()

# 4. INCIDENCIAS
print("\n4️⃣  Incidencias...")
incidencias_data = [
    {"tipo": "PUNTO_ACOPIO", "gravedad": 1, "descripcion": "Contenedor lleno Av. Eloy Alfaro",
     "lat": -0.934464, "lon": -78.616127, "zona": "ORIENTAL", "estado": "pendiente"},
    {"tipo": "ZONA_CRITICA", "gravedad": 3, "descripcion": "Basura acumulada mercado La Merced",
     "lat": -0.935166, "lon": -78.617333, "zona": "ORIENTAL", "estado": "validada"},
    {"tipo": "ANIMAL_MUERTO", "gravedad": 5, "descripcion": "Animal muerto vía pública",
     "lat": -0.934819, "lon": -78.619228, "zona": "OCCIDENTAL", "estado": "pendiente"},
    {"tipo": "ZONA_CRITICA", "gravedad": 3, "descripcion": "Basura Parque Vicente León",
     "lat": -0.933289, "lon": -78.615761, "zona": "ORIENTAL", "estado": "asignada"},
]

for inc in incidencias_data:
    try:
        session.execute(text("""
            INSERT INTO incidencias (tipo, gravedad, descripcion, lat, lon, zona, estado, 
                                   reportado_en, created_at, updated_at)
            VALUES (:tipo, :gravedad, :descripcion, :lat, :lon, :zona, :estado, NOW(), NOW(), NOW())
        """), inc)
        print(f"   ✓ {inc['tipo']} - {inc['descripcion'][:40]}...")
    except Exception as e:
        print(f"   ⚠️  {str(e)[:60]}")

session.commit()

# 5. REPORTES APK
print("\n5️⃣  Reportes APK...")
result = session.execute(text("SELECT id FROM users LIMIT 1")).fetchone()
if result:
    reporter_id = result[0]
    reportes_data = [
        {"id": str(uuid.uuid4()), "reporter_id": reporter_id, "type": "ZONA_CRITICA",
         "description": "Basura acumulada en esquina", "priority_score": 8.5,
         "lat": -0.934464, "lon": -78.616127, "address": "Av. Los Chasquis", "state": "ENVIADO"},
        {"id": str(uuid.uuid4()), "reporter_id": reporter_id, "type": "PUNTO_ACOPIO_LLENO",
         "description": "Contenedor desbordado", "priority_score": 6.0,
         "lat": -0.935166, "lon": -78.617333, "address": "Mercado La Merced", "state": "EN_PROCESO"},
    ]
    
    for r in reportes_data:
        try:
            session.execute(text("""
                INSERT INTO reports (id, reporter_id, type, description, priority_score,
                                   location, address, state, created_at, updated_at)
                VALUES (:id, :reporter_id, :type, :description, :priority_score,
                        ST_SetSRID(ST_MakePoint(:lon, :lat), 4326),
                        :address, :state, NOW(), NOW())
            """), r)
            print(f"   ✓ {r['type']} - {r['description'][:40]}...")
        except Exception as e:
            print(f"   ⚠️  {str(e)[:60]}")
    session.commit()

# 6. RUTAS
print("\n6️⃣  Rutas...")
rutas_data = [
    {"nombre": "Ruta Centro Histórico", "descripcion": "Centro de Latacunga", "distancia_km": 12.5, "tiempo_estimado_minutos": 90},
    {"nombre": "Ruta Zona Norte", "descripcion": "San Felipe y San Agustín", "distancia_km": 18.3, "tiempo_estimado_minutos": 120},
    {"nombre": "Ruta Zona Sur", "descripcion": "La Laguna y Eloy Alfaro", "distancia_km": 15.7, "tiempo_estimado_minutos": 105},
]

for ruta in rutas_data:
    try:
        session.execute(text("""
            INSERT INTO rutas (nombre, descripcion, distancia_km, tiempo_estimado_minutos, estado, created_at)
            VALUES (:nombre, :descripcion, :distancia_km, :tiempo_estimado_minutos, 'activa', NOW())
        """), ruta)
        print(f"   ✓ {ruta['nombre']} ({ruta['distancia_km']} km)")
    except Exception as e:
        print(f"   ⚠️  {str(e)[:60]}")

session.commit()

# 7. TAREAS
print("\n7️⃣  Tareas...")
conductores_ids = [r[0] for r in session.execute(text("SELECT id FROM conductores LIMIT 3")).fetchall()]
rutas_ids = [r[0] for r in session.execute(text("SELECT id FROM rutas LIMIT 3")).fetchall()]

if conductores_ids and rutas_ids:
    tareas_data = [
        {"id": str(uuid.uuid4()), "titulo": "Recolección Matutina - Centro",
         "descripcion": "Recolección zona centro", "tipo": "RECOLECCION", "prioridad": "ALTA",
         "estado": "EN_PROGRESO", "progreso": 45, "conductor_id": conductores_ids[0],
         "ruta_id": rutas_ids[0], "fecha_limite": datetime.now() + timedelta(days=1)},
        {"id": str(uuid.uuid4()), "titulo": "Recolección Zona Norte",
         "descripcion": "Barrios del norte", "tipo": "RECOLECCION", "prioridad": "MEDIA",
         "estado": "PENDIENTE", "progreso": 0, "conductor_id": conductores_ids[1] if len(conductores_ids) > 1 else conductores_ids[0],
         "ruta_id": rutas_ids[1] if len(rutas_ids) > 1 else rutas_ids[0],
         "fecha_limite": datetime.now() + timedelta(days=2)},
        {"id": str(uuid.uuid4()), "titulo": "Emergencia - Mercado",
         "descripcion": "Atención urgente", "tipo": "EMERGENCIA", "prioridad": "CRITICA",
         "estado": "PENDIENTE", "progreso": 0, "conductor_id": conductores_ids[2] if len(conductores_ids) > 2 else conductores_ids[0],
         "ruta_id": rutas_ids[2] if len(rutas_ids) > 2 else rutas_ids[0],
         "fecha_limite": datetime.now() + timedelta(hours=6)},
    ]
    
    for t in tareas_data:
        try:
            session.execute(text("""
                INSERT INTO tasks (id, titulo, descripcion, tipo, prioridad, estado, progreso,
                                 conductor_id, ruta_id, fecha_limite, created_at, updated_at)
                VALUES (:id, :titulo, :descripcion, :tipo, :prioridad, :estado, :progreso,
                        :conductor_id, :ruta_id, :fecha_limite, NOW(), NOW())
            """), t)
            print(f"   ✓ {t['titulo']} ({t['prioridad']})")
        except Exception as e:
            print(f"   ⚠️  {str(e)[:60]}")
    session.commit()

# RESUMEN
print("\n" + "=" * 80)
print("RESUMEN FINAL")
print("=" * 80)

counts = {
    "users": session.execute(text("SELECT COUNT(*) FROM users")).scalar(),
    "conductores": session.execute(text("SELECT COUNT(*) FROM conductores")).scalar(),
    "vehiculos": session.execute(text("SELECT COUNT(*) FROM vehiculos")).scalar(),
    "rutas": session.execute(text("SELECT COUNT(*) FROM rutas")).scalar(),
    "incidencias": session.execute(text("SELECT COUNT(*) FROM incidencias")).scalar(),
    "reports": session.execute(text("SELECT COUNT(*) FROM reports")).scalar(),
    "tasks": session.execute(text("SELECT COUNT(*) FROM tasks")).scalar(),
}

for table, count in counts.items():
    print(f"   ✓ {table:15s}: {count:3d} registros")

print("\n" + "=" * 80)
print("🔐 CREDENCIALES DE ACCESO")
print("=" * 80)
print("\n   Admin: admin@epagal.gob.ec / Admin123!")
print("   Operador1: operador1@epagal.gob.ec / Operador123!")
print("   Operador2: operador2@epagal.gob.ec / Operador123!")

print("\n" + "=" * 80)
print("✅ CONFIGURACIÓN COMPLETADA")
print("=" * 80)
print("\n🚀 Ahora reinicia Docker:")
print("   docker-compose -f docker-compose.local.yml down")
print("   docker-compose -f docker-compose.local.yml up -d")
print("\n📱 Accede a: http://localhost:3001")
print("=" * 80)

session.close()
