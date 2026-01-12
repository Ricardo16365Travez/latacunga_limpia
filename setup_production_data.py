"""
Script para configurar y poblar la base de datos de producción
Verifica tablas existentes, crea las que faltan y carga datos de ejemplo
"""
import os
import sys
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import uuid
import bcrypt

# Pedir la URL de la base de datos de producción
print("=" * 80)
print("CONFIGURACIÓN DE BASE DE DATOS DE PRODUCCIÓN")
print("=" * 80)
print("\n📌 Ingresa la cadena de conexión a tu base de datos de producción")
print("   Ejemplos:")
print("   - Neon: postgresql://user:pass@ep-xxx.us-east-1.aws.neon.tech/neondb")
print("   - Render: postgresql://user:pass@dpg-xxx.oregon-postgres.render.com/dbname")
print("   - Supabase: postgresql://postgres:pass@db.xxx.supabase.co:5432/postgres")
print("\n")

DB_URL = input("DB_URL: ").strip()

if not DB_URL or not DB_URL.startswith("postgresql://"):
    print("❌ Error: URL de base de datos inválida")
    sys.exit(1)

print(f"\n✅ Conectando a: {DB_URL[:40]}...")

try:
    engine = create_engine(DB_URL, pool_pre_ping=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Test de conexión
    session.execute(text("SELECT 1"))
    print("✅ Conexión exitosa\n")
    
except Exception as e:
    print(f"❌ Error de conexión: {e}")
    sys.exit(1)


# ============================================================================
# VERIFICAR Y CREAR TABLAS
# ============================================================================
print("=" * 80)
print("VERIFICANDO TABLAS EXISTENTES")
print("=" * 80)

inspector = inspect(engine)
existing_tables = inspector.get_table_names()

print(f"\n📋 Tablas encontradas ({len(existing_tables)}):")
for table in sorted(existing_tables):
    print(f"   ✓ {table}")

required_tables = [
    "users",
    "conductores",
    "vehiculos",
    "rutas",
    "incidencias",
    "tasks",
    "reports"
]

missing_tables = [t for t in required_tables if t not in existing_tables]

if missing_tables:
    print(f"\n⚠️  Tablas faltantes: {', '.join(missing_tables)}")
    print("   Estas se deben crear manualmente o con migraciones")
else:
    print("\n✅ Todas las tablas requeridas existen")


# ============================================================================
# CARGAR DATOS DE EJEMPLO
# ============================================================================
print("\n" + "=" * 80)
print("INSERTANDO DATOS DE EJEMPLO")
print("=" * 80)

def hash_password(password: str) -> str:
    """Hash de contraseña con bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# 1. USUARIOS (Operadores y Administradores)
print("\n1️⃣  Insertando usuarios...")
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
        "status": "ACTIVE",
        "created_at": datetime.now(),
        "updated_at": datetime.now()
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
        "status": "ACTIVE",
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    },
    {
        "id": str(uuid.uuid4()),
        "email": "operador2@epagal.gob.ec",
        "username": "operador2",
        "password_hash": hash_password("Operador123!"),
        "role": "OPERADOR",
        "display_name": "María González Operador",
        "phone": "+593987654323",
        "is_active": True,
        "status": "ACTIVE",
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    },
]

for user in usuarios_data:
    try:
        session.execute(text("""
            INSERT INTO users (id, email, username, password_hash, role, display_name, 
                             phone, is_active, status, created_at, updated_at)
            VALUES (:id, :email, :username, :password_hash, :role, :display_name,
                    :phone, :is_active, :status, :created_at, :updated_at)
            ON CONFLICT (email) DO NOTHING
        """), user)
        print(f"   ✓ Usuario creado: {user['username']} ({user['email']})")
    except Exception as e:
        print(f"   ⚠️  Error con {user['username']}: {e}")

session.commit()

# 2. CONDUCTORES
print("\n2️⃣  Insertando conductores...")
conductores_data = [
    {
        "cedula": "1803456789",
        "nombre_completo": "Carlos Andrés Martínez",
        "email": "carlos.martinez@epagal.gob.ec",
        "telefono": "+593998765432",
        "username": "cmartinez",
        "licencia_tipo": "C",
        "zona_preferida": "ORIENTAL",
        "estado": "disponible"
    },
    {
        "cedula": "1804567890",
        "nombre_completo": "Luis Fernando Vega",
        "email": "luis.vega@epagal.gob.ec",
        "telefono": "+593998765433",
        "username": "lvega",
        "licencia_tipo": "D",
        "zona_preferida": "OCCIDENTAL",
        "estado": "disponible"
    },
    {
        "cedula": "1805678901",
        "nombre_completo": "Pedro Antonio Rojas",
        "email": "pedro.rojas@epagal.gob.ec",
        "telefono": "+593998765434",
        "username": "projas",
        "licencia_tipo": "C",
        "zona_preferida": "ORIENTAL",
        "estado": "ocupado"
    }
]

for conductor in conductores_data:
    try:
        session.execute(text("""
            INSERT INTO conductores (cedula, nombre_completo, email, telefono, username,
                                   licencia_tipo, zona_preferida, estado, created_at)
            VALUES (:cedula, :nombre_completo, :email, :telefono, :username,
                    :licencia_tipo, :zona_preferida, :estado, NOW())
            ON CONFLICT (cedula) DO NOTHING
        """), conductor)
        print(f"   ✓ Conductor: {conductor['nombre_completo']}")
    except Exception as e:
        print(f"   ⚠️  Error: {e}")

session.commit()

# 3. VEHÍCULOS
print("\n3️⃣  Insertando vehículos...")
vehiculos_data = [
    {
        "placa": "PBC-1234",
        "marca": "Hino",
        "modelo": "Serie 300",
        "capacidad_toneladas": 7.5,
        "año": 2020,
        "estado": "disponible"
    },
    {
        "placa": "PBC-5678",
        "marca": "Chevrolet",
        "modelo": "NPR",
        "capacidad_toneladas": 5.0,
        "año": 2021,
        "estado": "disponible"
    },
    {
        "placa": "PBC-9012",
        "marca": "International",
        "modelo": "4300",
        "capacidad_toneladas": 10.0,
        "año": 2019,
        "estado": "en_mantenimiento"
    }
]

for vehiculo in vehiculos_data:
    try:
        session.execute(text("""
            INSERT INTO vehiculos (placa, marca, modelo, capacidad_toneladas, año, estado, created_at)
            VALUES (:placa, :marca, :modelo, :capacidad_toneladas, :año, :estado, NOW())
            ON CONFLICT (placa) DO NOTHING
        """), vehiculo)
        print(f"   ✓ Vehículo: {vehiculo['placa']} - {vehiculo['marca']} {vehiculo['modelo']}")
    except Exception as e:
        print(f"   ⚠️  Error: {e}")

session.commit()

# 4. INCIDENCIAS (reportes ciudadanos)
print("\n4️⃣  Insertando incidencias...")
incidencias_data = [
    {
        "tipo": "PUNTO_ACOPIO",
        "gravedad": 1,
        "descripcion": "Contenedor lleno en Av. Eloy Alfaro",
        "lat": -0.934464,
        "lon": -78.616127,
        "zona": "ORIENTAL",
        "estado": "pendiente"
    },
    {
        "tipo": "ZONA_CRITICA",
        "gravedad": 3,
        "descripcion": "Acumulación de basura en mercado La Merced",
        "lat": -0.935166,
        "lon": -78.617333,
        "zona": "ORIENTAL",
        "estado": "validada"
    },
    {
        "tipo": "ANIMAL_MUERTO",
        "gravedad": 5,
        "descripcion": "Animal muerto en vía pública",
        "lat": -0.934819,
        "lon": -78.619228,
        "zona": "OCCIDENTAL",
        "estado": "pendiente"
    },
    {
        "tipo": "ZONA_CRITICA",
        "gravedad": 3,
        "descripcion": "Basura en Parque Vicente León",
        "lat": -0.933289,
        "lon": -78.615761,
        "zona": "ORIENTAL",
        "estado": "asignada"
    }
]

for inc in incidencias_data:
    try:
        session.execute(text("""
            INSERT INTO incidencias (tipo, gravedad, descripcion, lat, lon, zona, estado, 
                                   reportado_en, created_at, updated_at)
            VALUES (:tipo, :gravedad, :descripcion, :lat, :lon, :zona, :estado, 
                    NOW(), NOW(), NOW())
        """), inc)
        print(f"   ✓ Incidencia: {inc['tipo']} - {inc['descripcion'][:40]}...")
    except Exception as e:
        print(f"   ⚠️  Error: {e}")

session.commit()

# 5. REPORTES (desde APK móvil)
print("\n5️⃣  Insertando reportes APK...")

# Obtener primer usuario para asignar como reporter
result = session.execute(text("SELECT id FROM users LIMIT 1")).fetchone()
if result:
    reporter_id = result[0]
    
    reportes_data = [
        {
            "id": str(uuid.uuid4()),
            "reporter_id": reporter_id,
            "type": "ZONA_CRITICA",
            "description": "Acumulación de basura en esquina",
            "priority_score": 8.5,
            "lat": -0.934464,
            "lon": -78.616127,
            "address": "Av. Los Chasquis y Calixto Pino",
            "state": "ENVIADO"
        },
        {
            "id": str(uuid.uuid4()),
            "reporter_id": reporter_id,
            "type": "PUNTO_ACOPIO_LLENO",
            "description": "Contenedor desbordado",
            "priority_score": 6.0,
            "lat": -0.935166,
            "lon": -78.617333,
            "address": "Mercado La Merced",
            "state": "EN_PROCESO"
        }
    ]
    
    for report in reportes_data:
        try:
            session.execute(text("""
                INSERT INTO reports (id, reporter_id, type, description, priority_score,
                                   location, address, state, created_at, updated_at)
                VALUES (:id, :reporter_id, :type, :description, :priority_score,
                        ST_SetSRID(ST_MakePoint(:lon, :lat), 4326),
                        :address, :state, NOW(), NOW())
            """), report)
            print(f"   ✓ Reporte: {report['type']} - {report['description'][:40]}...")
        except Exception as e:
            print(f"   ⚠️  Error: {e}")
    
    session.commit()

# 6. RUTAS
print("\n6️⃣  Insertando rutas...")
rutas_data = [
    {
        "nombre": "Ruta Centro Histórico",
        "descripcion": "Recolección en el centro de Latacunga",
        "distancia_km": 12.5,
        "tiempo_estimado_minutos": 90,
        "estado": "activa"
    },
    {
        "nombre": "Ruta Zona Norte",
        "descripcion": "Barrios San Felipe y San Agustín",
        "distancia_km": 18.3,
        "tiempo_estimado_minutos": 120,
        "estado": "activa"
    },
    {
        "nombre": "Ruta Zona Sur",
        "descripcion": "Barrios La Laguna y Eloy Alfaro",
        "distancia_km": 15.7,
        "tiempo_estimado_minutos": 105,
        "estado": "activa"
    }
]

for ruta in rutas_data:
    try:
        session.execute(text("""
            INSERT INTO rutas (nombre, descripcion, distancia_km, tiempo_estimado_minutos, estado, created_at)
            VALUES (:nombre, :descripcion, :distancia_km, :tiempo_estimado_minutos, :estado, NOW())
        """), ruta)
        print(f"   ✓ Ruta: {ruta['nombre']} ({ruta['distancia_km']} km)")
    except Exception as e:
        print(f"   ⚠️  Error: {e}")

session.commit()

# 7. TAREAS
print("\n7️⃣  Insertando tareas...")

# Obtener IDs de conductores y rutas para asignaciones
conductores_ids = [r[0] for r in session.execute(text("SELECT id FROM conductores LIMIT 3")).fetchall()]
rutas_ids = [r[0] for r in session.execute(text("SELECT id FROM rutas LIMIT 3")).fetchall()]

if conductores_ids and rutas_ids:
    tareas_data = [
        {
            "id": str(uuid.uuid4()),
            "titulo": "Recolección Matutina - Centro",
            "descripcion": "Recolección de residuos en zona centro",
            "tipo": "RECOLECCION",
            "prioridad": "ALTA",
            "estado": "EN_PROGRESO",
            "progreso": 45,
            "conductor_id": conductores_ids[0],
            "ruta_id": rutas_ids[0],
            "fecha_limite": datetime.now() + timedelta(days=1)
        },
        {
            "id": str(uuid.uuid4()),
            "titulo": "Recolección Zona Norte",
            "descripcion": "Servicio de recolección en barrios del norte",
            "tipo": "RECOLECCION",
            "prioridad": "MEDIA",
            "estado": "PENDIENTE",
            "progreso": 0,
            "conductor_id": conductores_ids[1] if len(conductores_ids) > 1 else conductores_ids[0],
            "ruta_id": rutas_ids[1] if len(rutas_ids) > 1 else rutas_ids[0],
            "fecha_limite": datetime.now() + timedelta(days=2)
        },
        {
            "id": str(uuid.uuid4()),
            "titulo": "Limpieza Emergencia - Mercado",
            "descripcion": "Atención urgente de acumulación de basura",
            "tipo": "EMERGENCIA",
            "prioridad": "CRITICA",
            "estado": "PENDIENTE",
            "progreso": 0,
            "conductor_id": conductores_ids[2] if len(conductores_ids) > 2 else conductores_ids[0],
            "ruta_id": rutas_ids[2] if len(rutas_ids) > 2 else rutas_ids[0],
            "fecha_limite": datetime.now() + timedelta(hours=6)
        }
    ]
    
    for tarea in tareas_data:
        try:
            session.execute(text("""
                INSERT INTO tasks (id, titulo, descripcion, tipo, prioridad, estado, progreso,
                                 conductor_id, ruta_id, fecha_limite, created_at, updated_at)
                VALUES (:id, :titulo, :descripcion, :tipo, :prioridad, :estado, :progreso,
                        :conductor_id, :ruta_id, :fecha_limite, NOW(), NOW())
            """), tarea)
            print(f"   ✓ Tarea: {tarea['titulo']} (Prioridad: {tarea['prioridad']})")
        except Exception as e:
            print(f"   ⚠️  Error: {e}")
    
    session.commit()


# ============================================================================
# RESUMEN Y CONFIGURACIÓN DEL .env
# ============================================================================
print("\n" + "=" * 80)
print("RESUMEN DE DATOS INSERTADOS")
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
print("CREDENCIALES DE ACCESO")
print("=" * 80)
print("\n🔐 Usuarios creados:")
print("   Admin:")
print("     Usuario: admin")
print("     Email: admin@epagal.gob.ec")
print("     Contraseña: Admin123!")
print("\n   Operador 1:")
print("     Usuario: operador1")
print("     Email: operador1@epagal.gob.ec")
print("     Contraseña: Operador123!")
print("\n   Operador 2:")
print("     Usuario: operador2")
print("     Email: operador2@epagal.gob.ec")
print("     Contraseña: Operador123!")

print("\n" + "=" * 80)
print("ACTUALIZAR ARCHIVO .env")
print("=" * 80)
print("\n📝 Ahora voy a actualizar el archivo .env con la conexión de producción...")

env_path = os.path.join(os.path.dirname(__file__), ".env")
with open(env_path, "w", encoding="utf-8") as f:
    f.write(f"""# ======================================================
# BASE DE DATOS DE PRODUCCIÓN - CONFIGURADO
# ======================================================
DB_URL={DB_URL}

# JWT Secret para autenticación
JWT_SECRET=production_secret_key_epagal_2026

# ======================================================
# ✅ CONFIGURACIÓN COMPLETADA
# ======================================================
# Base de datos configurada y poblada con datos de ejemplo
# 
# Para usar esta configuración:
# 1. Detén los contenedores: docker-compose -f docker-compose.local.yml down
# 2. Reconstruye: docker-compose -f docker-compose.local.yml up --build -d
# 3. Accede al sistema en http://localhost:3001
# 
# Credenciales:
# - Admin: admin@epagal.gob.ec / Admin123!
# - Operador1: operador1@epagal.gob.ec / Operador123!
# - Operador2: operador2@epagal.gob.ec / Operador123!
# ======================================================
""")

print(f"\n✅ Archivo .env actualizado: {env_path}")

print("\n" + "=" * 80)
print("✨ CONFIGURACIÓN COMPLETADA")
print("=" * 80)
print("\n🚀 Siguiente paso: Reiniciar servicios Docker")
print("   docker-compose -f docker-compose.local.yml down")
print("   docker-compose -f docker-compose.local.yml up --build -d")
print("\n📱 Luego accede a: http://localhost:3001")
print("=" * 80)

session.close()
