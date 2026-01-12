"""
Script para inspeccionar el schema real de Neon y cargar datos compatibles
"""
import os
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import uuid
import bcrypt

DB_URL = "postgresql://neondb_owner:npg_jnw3bVupEP5i@ep-gentle-pond-adcmrdsv-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

print("=" * 80)
print("INSPECCIÓN Y CARGA INTELIGENTE - BASE DE DATOS NEON")
print("=" * 80)

engine = create_engine(DB_URL, pool_pre_ping=True)
Session = sessionmaker(bind=engine)
session = Session()

inspector = inspect(engine)
existing_tables = inspector.get_table_names()

print(f"\n✅ Conectado a Neon - {len(existing_tables)} tablas encontradas\n")

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Revisar estructura de users
print("🔍 Estructura de 'users':")
columns_users = inspector.get_columns('users')
for col in columns_users:
    print(f"   - {col['name']}: {col['type']}")

# Revisar estructura de conductores
print("\n🔍 Estructura de 'conductores':")
columns_conductores = inspector.get_columns('conductores')
for col in columns_conductores:
    print(f"   - {col['name']}: {col['type']}")

# Revisar estructura de reports
print("\n🔍 Estructura de 'reports':")
columns_reports = inspector.get_columns('reports')
for col in columns_reports:
    print(f"   - {col['name']}: {col['type']}")

# Revisar estructura de tasks
print("\n🔍 Estructura de 'tasks':")
columns_tasks = inspector.get_columns('tasks')
for col in columns_tasks:
    print(f"   - {col['name']}: {col['type']}")

# Revisar estructura de incidencias
print("\n🔍 Estructura de 'incidencias':")
columns_incidencias = inspector.get_columns('incidencias')
for col in columns_incidencias:
    print(f"   - {col['name']}: {col['type']}")

print("\n" + "=" * 80)
print("INSERTANDO DATOS ADAPTADOS AL SCHEMA REAL")
print("=" * 80)

# 1. USUARIOS - verificar si admin ya existe
print("\n1️⃣  Usuarios...")
try:
    existing_admin = session.execute(text("SELECT email FROM users WHERE email = 'admin@epagal.gob.ec'")).fetchone()
    if existing_admin:
        print("   ℹ️  Admin ya existe, saltando...")
    else:
        session.execute(text("""
            INSERT INTO users (id, email, username, password_hash, role, display_name, 
                             phone, is_active, status, created_at, updated_at)
            VALUES (:id, :email, :username, :password_hash, :role, :display_name,
                    :phone, :is_active, :status, NOW(), NOW())
        """), {
            "id": str(uuid.uuid4()),
            "email": "admin@epagal.gob.ec",
            "username": "admin",
            "password_hash": hash_password("Admin123!"),
            "role": "ADMIN",
            "display_name": "Administrador EPAGAL",
            "phone": "+593987654321",
            "is_active": True,
            "status": "ACTIVE"
        })
        session.commit()
        print("   ✓ Admin creado")
except Exception as e:
    session.rollback()
    print(f"   ⚠️  Admin: {str(e)[:100]}")

# Operadores
for i in [1, 2]:
    try:
        email = f"operador{i}@epagal.gob.ec"
        existing = session.execute(text(f"SELECT email FROM users WHERE email = '{email}'")).fetchone()
        if existing:
            print(f"   ℹ️  Operador{i} ya existe")
        else:
            session.execute(text("""
                INSERT INTO users (id, email, username, password_hash, role, display_name, 
                                 phone, is_active, status, created_at, updated_at)
                VALUES (:id, :email, :username, :password_hash, :role, :display_name,
                        :phone, :is_active, :status, NOW(), NOW())
            """), {
                "id": str(uuid.uuid4()),
                "email": email,
                "username": f"operador{i}",
                "password_hash": hash_password("Operador123!"),
                "role": "OPERADOR",
                "display_name": f"Operador {i} EPAGAL",
                "phone": f"+59398765432{i+1}",
                "is_active": True,
                "status": "ACTIVE"
            })
            session.commit()
            print(f"   ✓ Operador{i} creado")
    except Exception as e:
        session.rollback()
        print(f"   ⚠️  Operador{i}: {str(e)[:100]}")

# 2. CONDUCTORES - adaptar a schema real
print("\n2️⃣  Conductores...")
conductor_columns = [col['name'] for col in columns_conductores]
print(f"   Columnas disponibles: {', '.join(conductor_columns)}")

conductores_basicos = [
    {"cedula": "1803456789", "nombre_completo": "Carlos Martínez", "telefono": "+593998765432", "username": "cmartinez"},
    {"cedula": "1804567890", "nombre_completo": "Luis Vega", "telefono": "+593998765433", "username": "lvega"},
    {"cedula": "1805678901", "nombre_completo": "Pedro Rojas", "telefono": "+593998765434", "username": "projas"},
]

for c in conductores_basicos:
    try:
        # Construir INSERT dinámico basado en columnas existentes
        cols_to_insert = []
        vals_to_insert = []
        
        if 'cedula' in conductor_columns:
            cols_to_insert.append('cedula')
            vals_to_insert.append(f"'{c['cedula']}'")
        if 'nombre_completo' in conductor_columns:
            cols_to_insert.append('nombre_completo')
            vals_to_insert.append(f"'{c['nombre_completo']}'")
        if 'telefono' in conductor_columns:
            cols_to_insert.append('telefono')
            vals_to_insert.append(f"'{c['telefono']}'")
        if 'username' in conductor_columns:
            cols_to_insert.append('username')
            vals_to_insert.append(f"'{c['username']}'")
        if 'estado' in conductor_columns:
            cols_to_insert.append('estado')
            vals_to_insert.append("'disponible'")
        if 'created_at' in conductor_columns:
            cols_to_insert.append('created_at')
            vals_to_insert.append("NOW()")
            
        if cols_to_insert:
            query = f"INSERT INTO conductores ({', '.join(cols_to_insert)}) VALUES ({', '.join(vals_to_insert)}) ON CONFLICT (cedula) DO NOTHING"
            session.execute(text(query))
            session.commit()
            print(f"   ✓ {c['nombre_completo']}")
    except Exception as e:
        session.rollback()
        print(f"   ⚠️  {c['nombre_completo']}: {str(e)[:80]}")

# 3. REPORTES APK - adaptar a schema real
print("\n3️⃣  Reportes APK...")
report_columns = [col['name'] for col in columns_reports]
print(f"   Columnas disponibles: {', '.join(report_columns)}")

# Obtener un user_id válido
user_id_result = session.execute(text("SELECT id FROM users LIMIT 1")).fetchone()
if user_id_result:
    user_id = user_id_result[0]
    
    reportes = [
        {"type": "ZONA_CRITICA", "description": "Basura acumulada en esquina", 
         "priority_score": 8.5, "lat": -0.934464, "lon": -78.616127, 
         "address": "Av. Los Chasquis", "state": "ENVIADO"},
        {"type": "PUNTO_ACOPIO_LLENO", "description": "Contenedor desbordado",
         "priority_score": 6.0, "lat": -0.935166, "lon": -78.617333,
         "address": "Mercado La Merced", "state": "EN_PROCESO"},
    ]
    
    for r in reportes:
        try:
            cols = []
            vals = {}
            
            if 'id' in report_columns:
                cols.append('id')
                vals['id'] = str(uuid.uuid4())
            if 'user_id' in report_columns:
                cols.append('user_id')
                vals['user_id'] = user_id
            if 'type' in report_columns:
                cols.append('type')
                vals['type'] = r['type']
            if 'description' in report_columns:
                cols.append('description')
                vals['description'] = r['description']
            if 'priority_score' in report_columns:
                cols.append('priority_score')
                vals['priority_score'] = r['priority_score']
            if 'address' in report_columns:
                cols.append('address')
                vals['address'] = r['address']
            if 'state' in report_columns:
                cols.append('state')
                vals['state'] = r['state']
            if 'location' in report_columns:
                cols.append('location')
                # Usar parámetros para geometry
                query = f"""
                    INSERT INTO reports ({', '.join(cols)}, created_at, updated_at)
                    VALUES ({', '.join([':' + c for c in cols])}, 
                            ST_SetSRID(ST_MakePoint(:lon, :lat), 4326), NOW(), NOW())
                """
                vals['lon'] = r['lon']
                vals['lat'] = r['lat']
            else:
                query = f"""
                    INSERT INTO reports ({', '.join(cols)}, created_at, updated_at)
                    VALUES ({', '.join([':' + c for c in cols])}, NOW(), NOW())
                """
            
            session.execute(text(query), vals)
            session.commit()
            print(f"   ✓ {r['type']} - {r['description'][:40]}...")
        except Exception as e:
            session.rollback()
            print(f"   ⚠️  {str(e)[:100]}")

# 4. TAREAS
print("\n4️⃣  Tareas...")
task_columns = [col['name'] for col in columns_tasks]
print(f"   Columnas disponibles: {', '.join(task_columns)}")

# Obtener conductor_id si existe
conductor_result = session.execute(text("SELECT id FROM conductores LIMIT 1")).fetchone()
conductor_id = conductor_result[0] if conductor_result else None

tareas = [
    {"titulo": "Recolección Centro", "descripcion": "Zona centro", "tipo": "RECOLECCION", 
     "prioridad": "ALTA", "estado": "EN_PROGRESO", "progreso": 45},
    {"titulo": "Recolección Norte", "descripcion": "Barrios norte", "tipo": "RECOLECCION",
     "prioridad": "MEDIA", "estado": "PENDIENTE", "progreso": 0},
]

for t in tareas:
    try:
        cols = []
        vals = {}
        
        if 'id' in task_columns:
            cols.append('id')
            vals['id'] = str(uuid.uuid4())
        if 'titulo' in task_columns:
            cols.append('titulo')
            vals['titulo'] = t['titulo']
        if 'descripcion' in task_columns:
            cols.append('descripcion')
            vals['descripcion'] = t['descripcion']
        if 'tipo' in task_columns:
            cols.append('tipo')
            vals['tipo'] = t['tipo']
        if 'prioridad' in task_columns:
            cols.append('prioridad')
            vals['prioridad'] = t['prioridad']
        if 'estado' in task_columns:
            cols.append('estado')
            vals['estado'] = t['estado']
        if 'progreso' in task_columns:
            cols.append('progreso')
            vals['progreso'] = t['progreso']
        if 'conductor_id' in task_columns and conductor_id:
            cols.append('conductor_id')
            vals['conductor_id'] = conductor_id
            
        query = f"""
            INSERT INTO tasks ({', '.join(cols)}, created_at, updated_at)
            VALUES ({', '.join([':' + c for c in cols])}, NOW(), NOW())
        """
        
        session.execute(text(query), vals)
        session.commit()
        print(f"   ✓ {t['titulo']}")
    except Exception as e:
        session.rollback()
        print(f"   ⚠️  {str(e)[:100]}")

# RESUMEN
print("\n" + "=" * 80)
print("RESUMEN")
print("=" * 80)

try:
    counts = {
        "users": session.execute(text("SELECT COUNT(*) FROM users")).scalar(),
        "conductores": session.execute(text("SELECT COUNT(*) FROM conductores")).scalar(),
        "reports": session.execute(text("SELECT COUNT(*) FROM reports")).scalar(),
        "tasks": session.execute(text("SELECT COUNT(*) FROM tasks")).scalar(),
    }
    
    for table, count in counts.items():
        print(f"   ✓ {table:15s}: {count:3d} registros")
except:
    pass

print("\n" + "=" * 80)
print("🔐 CREDENCIALES")
print("=" * 80)
print("\n   Admin: admin@epagal.gob.ec / Admin123!")
print("   Operador1: operador1@epagal.gob.ec / Operador123!")
print("   Operador2: operador2@epagal.gob.ec / Operador123!")

print("\n✅ Configuración completada!")
print("=" * 80)

session.close()
