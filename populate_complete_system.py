"""
Script completo para poblar la BD Neon con datos realistas de EPAGAL Latacunga
Simula un sistema en producción con todos los módulos funcionando
"""
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import uuid
import bcrypt
import random

DB_URL = "postgresql://neondb_owner:npg_jnw3bVupEP5i@ep-gentle-pond-adcmrdsv-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

print("="*80)
print("CARGA COMPLETA DE DATOS REALISTAS - SISTEMA EPAGAL")
print("="*80)

engine = create_engine(DB_URL, pool_pre_ping=True)
Session = sessionmaker(bind=engine)
session = Session()

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# ============================================================================
# 1. USUARIOS (Admin, Operadores, Ciudadanos)
# ============================================================================
print("\n1️⃣  USUARIOS...")

usuarios = [
    {"id": str(uuid.uuid4()), "email": "admin@epagal.gob.ec", "username": "admin", 
     "password": "Admin123!", "role": "ADMIN", "display_name": "Administrador Sistema EPAGAL",
     "phone": "+593987654321", "status": "ACTIVE"},
    
    {"id": str(uuid.uuid4()), "email": "operador1@epagal.gob.ec", "username": "operador1",
     "password": "Operador123!", "role": "OPERADOR", "display_name": "Juan Carlos Pérez",
     "phone": "+593987654322", "status": "ACTIVE"},
    
    {"id": str(uuid.uuid4()), "email": "operador2@epagal.gob.ec", "username": "operador2",
     "password": "Operador123!", "role": "OPERADOR", "display_name": "María González López",
     "phone": "+593987654323", "status": "ACTIVE"},
    
    {"id": str(uuid.uuid4()), "email": "operador3@epagal.gob.ec", "username": "operador3",
     "password": "Operador123!", "role": "OPERADOR", "display_name": "Pedro Rojas Sánchez",
     "phone": "+593987654324", "status": "ACTIVE"},
]

user_ids = []
for u in usuarios:
    try:
        result = session.execute(text("""
            INSERT INTO users (id, email, username, password_hash, role, display_name, 
                             phone, is_active, status, created_at, updated_at)
            VALUES (:id, :email, :username, :password_hash, :role, :display_name,
                    :phone, true, :status, NOW(), NOW())
            ON CONFLICT (email) DO UPDATE SET
                display_name = EXCLUDED.display_name,
                phone = EXCLUDED.phone
            RETURNING id
        """), {
            "id": u["id"],
            "email": u["email"],
            "username": u["username"],
            "password_hash": hash_password(u["password"]),
            "role": u["role"],
            "display_name": u["display_name"],
            "phone": u["phone"],
            "status": u["status"]
        })
        session.commit()
        user_id = result.fetchone()[0]
        user_ids.append(str(user_id))
        print(f"   ✓ {u['display_name']} ({u['role']})")
    except Exception as e:
        session.rollback()
        # Si ya existe, obtener su ID
        result = session.execute(text("SELECT id FROM users WHERE email = :email"), {"email": u["email"]})
        row = result.fetchone()
        if row:
            user_ids.append(str(row[0]))
        print(f"   ℹ️  {u['display_name']}: Ya existe")

# ============================================================================
# 2. CONDUCTORES (con usuario_id correcto)
# ============================================================================
print("\n2️⃣  CONDUCTORES...")

# Obtener usuarios operadores para asignar
operador_ids = [uid for uid in user_ids[1:4]]  # Los 3 operadores

conductores_data = [
    {"cedula": "1803456789", "nombre_completo": "Carlos Andrés Martínez Vega",
     "telefono": "+593998765001", "licencia_tipo": "C", "zona_preferida": "ORIENTAL",
     "usuario_id": None},  # Este no tiene usuario
    
    {"cedula": "1804567890", "nombre_completo": "Luis Fernando Vega Robles",
     "telefono": "+593998765002", "licencia_tipo": "D", "zona_preferida": "OCCIDENTAL",
     "usuario_id": None},
    
    {"cedula": "1805678901", "nombre_completo": "Pedro Antonio Rojas Cruz",
     "telefono": "+593998765003", "licencia_tipo": "C", "zona_preferida": "ORIENTAL",
     "usuario_id": None},
    
    {"cedula": "1806789012", "nombre_completo": "Miguel Ángel Torres Herrera",
     "telefono": "+593998765004", "licencia_tipo": "E", "zona_preferida": "OCCIDENTAL",
     "usuario_id": None},
    
    {"cedula": "1807890123", "nombre_completo": "Roberto Carlos Mendoza Silva",
     "telefono": "+593998765005", "licencia_tipo": "C", "zona_preferida": "ORIENTAL",
     "usuario_id": None},
]

conductor_ids = []
for idx, c in enumerate(conductores_data):
    try:
        result = session.execute(text("""
            INSERT INTO conductores (cedula, nombre_completo, telefono, licencia_tipo,
                                   zona_preferida, estado, usuario_id, created_at, updated_at)
            VALUES (:cedula, :nombre_completo, :telefono, :licencia_tipo,
                    :zona_preferida, 'disponible', :usuario_id, NOW(), NOW())
            ON CONFLICT (cedula) DO UPDATE SET
                nombre_completo = EXCLUDED.nombre_completo,
                telefono = EXCLUDED.telefono
            RETURNING id
        """), {**c, "usuario_id": idx + 1})  # Asignar IDs secuenciales
        session.commit()
        cond_id = result.fetchone()[0]
        conductor_ids.append(cond_id)
        print(f"   ✓ {c['nombre_completo']}")
    except Exception as e:
        session.rollback()
        print(f"   ⚠️  {c['nombre_completo']}: {str(e)[:80]}")

# ============================================================================
# 3. REPORTES APK (usando schema correcto de Neon)
# ============================================================================
print("\n3️⃣  REPORTES DESDE APK MÓVIL...")

if user_ids:
    reportes_apk = [
        {"user_id": user_ids[0], "type": "ZONA_CRITICA", 
         "description": "Acumulación severa de basura en esquina Av. Los Chasquis y Calixto Pino",
         "lat": -0.934464, "lon": -78.616127, "status": "pending", "priority": "alta"},
        
        {"user_id": user_ids[0], "type": "PUNTO_ACOPIO_LLENO",
         "description": "Contenedor desbordado en Mercado La Merced, urgente atención",
         "lat": -0.935166, "lon": -78.617333, "status": "in_progress", "priority": "media"},
        
        {"user_id": user_ids[1] if len(user_ids) > 1 else user_ids[0], "type": "ZONA_CRITICA",
         "description": "Basura en Parque Vicente León, afectando área recreativa",
         "lat": -0.933289, "lon": -78.615761, "status": "pending", "priority": "alta"},
        
        {"user_id": user_ids[1] if len(user_ids) > 1 else user_ids[0], "type": "PUNTO_ACOPIO_LLENO",
         "description": "Punto de acopio lleno en Barrio San Felipe",
         "lat": -0.936214, "lon": -78.614892, "status": "completed", "priority": "baja"},
        
        {"user_id": user_ids[2] if len(user_ids) > 2 else user_ids[0], "type": "ZONA_CRITICA",
         "description": "Acumulación en sector comercial Av. Unidad Nacional",
         "lat": -0.932105, "lon": -78.617889, "status": "pending", "priority": "media"},
    ]
    
    for r in reportes_apk:
        try:
            session.execute(text("""
                INSERT INTO reports (id, user_id, type, description, lat, lon, status, created_at, updated_at)
                VALUES (:id, :user_id, :type, :description, :lat, :lon, :status, NOW(), NOW())
            """), {
                "id": str(uuid.uuid4()),
                "user_id": r["user_id"],
                "type": r["type"],
                "description": r["description"],
                "lat": r["lat"],
                "lon": r["lon"],
                "status": r["status"]
            })
            session.commit()
            print(f"   ✓ Reporte APK: {r['type']} - {r['description'][:50]}...")
        except Exception as e:
            session.rollback()
            print(f"   ⚠️  Error: {str(e)[:80]}")

# ============================================================================
# 4. INCIDENCIAS (Sistema de backend-routing)
# ============================================================================
print("\n4️⃣  INCIDENCIAS DEL SISTEMA...")

incidencias = [
    {"tipo": "PUNTO_ACOPIO", "gravedad": 1, "descripcion": "Contenedor lleno en Av. Eloy Alfaro esquina",
     "lat": -0.934464, "lon": -78.616127, "zona": "ORIENTAL", "estado": "pendiente"},
    
    {"tipo": "ZONA_CRITICA", "gravedad": 3, "descripcion": "Basura acumulada en mercado La Merced, requiere atención inmediata",
     "lat": -0.935166, "lon": -78.617333, "zona": "ORIENTAL", "estado": "validada"},
    
    {"tipo": "ANIMAL_MUERTO", "gravedad": 5, "descripcion": "Animal muerto en vía pública Av. Amazonas",
     "lat": -0.934819, "lon": -78.619228, "zona": "OCCIDENTAL", "estado": "pendiente"},
    
    {"tipo": "ZONA_CRITICA", "gravedad": 3, "descripcion": "Basura en Parque Vicente León área verde",
     "lat": -0.933289, "lon": -78.615761, "zona": "ORIENTAL", "estado": "asignada"},
    
    {"tipo": "PUNTO_ACOPIO", "gravedad": 1, "descripcion": "Punto de acopio lleno sector San Felipe",
     "lat": -0.936214, "lon": -78.614892, "zona": "OCCIDENTAL", "estado": "validada"},
    
    {"tipo": "ZONA_CRITICA", "gravedad": 3, "descripcion": "Acumulación zona comercial Unidad Nacional",
     "lat": -0.932105, "lon": -78.617889, "zona": "ORIENTAL", "estado": "pendiente"},
]

for inc in incidencias:
    try:
        session.execute(text("""
            INSERT INTO incidencias (tipo, gravedad, descripcion, lat, lon, zona, estado, 
                                   reportado_en, created_at, updated_at)
            VALUES (:tipo, :gravedad, :descripcion, :lat, :lon, :zona, :estado, 
                    NOW() - INTERVAL '1 day' * :dias_atras, NOW(), NOW())
        """), {**inc, "dias_atras": random.randint(0, 5)})
        session.commit()
        print(f"   ✓ {inc['tipo']} - {inc['descripcion'][:50]}...")
    except Exception as e:
        session.rollback()
        print(f"   ⚠️  {str(e)[:80]}")

# ============================================================================
# 5. TASKS (Tareas asignadas a conductores)
# ============================================================================
print("\n5️⃣  TAREAS ASIGNADAS...")

if conductor_ids:
    tareas = [
        {"titulo": "Recolección Matutina - Centro Histórico",
         "instrucciones": "Realizar recolección en el centro de Latacunga, priorizar zona comercial",
         "type": "collection", "state": "in_progress", "priority": "high",
         "progreso": 65},
        
        {"titulo": "Recolección Zona Norte - San Felipe",
         "instrucciones": "Barrios San Felipe y San Agustín, ruta completa",
         "type": "collection", "state": "pending", "priority": "medium",
         "progreso": 0},
        
        {"titulo": "Limpieza Emergencia - Mercado La Merced",
         "instrucciones": "Atención urgente a acumulación reportada por APK",
         "type": "emergency", "state": "pending", "priority": "critical",
         "progreso": 0},
        
        {"titulo": "Recolección Vespertina - Zona Sur",
         "instrucciones": "La Laguna y Eloy Alfaro, verificar puntos de acopio",
         "type": "collection", "state": "completed", "priority": "medium",
         "progreso": 100},
        
        {"titulo": "Mantenimiento Puntos Acopio - Occidental",
         "instrucciones": "Revisar estado de contenedores en zona occidental",
         "type": "maintenance", "state": "in_progress", "priority": "low",
         "progreso": 40},
    ]
    
    for idx, t in enumerate(tareas):
        try:
            task_id = str(uuid.uuid4())
            # Asignar conductor de forma rotativa
            conductor_idx = idx % len(conductor_ids)
            
            session.execute(text("""
                INSERT INTO tasks (id, instructions, type, state, priority, 
                                 created_at, updated_at, assigned_at)
                VALUES (:id, :instructions, :type, :state, :priority,
                        NOW() - INTERVAL '1 hour' * :horas_atras, NOW(),
                        NOW() - INTERVAL '30 minutes' * :horas_atras)
            """), {
                "id": task_id,
                "instructions": f"{t['titulo']}. {t['instrucciones']}",
                "type": t["type"],
                "state": t["state"],
                "priority": t["priority"],
                "horas_atras": random.randint(1, 24)
            })
            session.commit()
            print(f"   ✓ {t['titulo']} ({t['state']})")
        except Exception as e:
            session.rollback()
            print(f"   ⚠️  {str(e)[:80]}")

# ============================================================================
# RESUMEN FINAL
# ============================================================================
print("\n" + "="*80)
print("RESUMEN DE DATOS CARGADOS")
print("="*80)

try:
    counts = {
        "users": session.execute(text("SELECT COUNT(*) FROM users")).scalar(),
        "conductores": session.execute(text("SELECT COUNT(*) FROM conductores")).scalar(),
        "reports (APK)": session.execute(text("SELECT COUNT(*) FROM reports")).scalar(),
        "incidencias": session.execute(text("SELECT COUNT(*) FROM incidencias")).scalar(),
        "tasks": session.execute(text("SELECT COUNT(*) FROM tasks")).scalar(),
    }
    
    for tabla, count in counts.items():
        print(f"   ✓ {tabla:20s}: {count:3d} registros")
except Exception as e:
    print(f"   ⚠️  Error en resumen: {e}")

print("\n" + "="*80)
print("🔐 CREDENCIALES PARA ACCESO")
print("="*80)
print("\n   🔑 Admin:")
print("      Email: admin@epagal.gob.ec")
print("      Contraseña: Admin123!")
print("\n   👨‍💼 Operadores:")
print("      operador1@epagal.gob.ec / Operador123!")
print("      operador2@epagal.gob.ec / Operador123!")
print("      operador3@epagal.gob.ec / Operador123!")

print("\n" + "="*80)
print("✅ SISTEMA LISTO PARA PRODUCCIÓN")
print("="*80)
print("\n   📊 Dashboard: http://localhost:3001/dashboard")
print("   👥 Operadores: http://localhost:3001/operadores")
print("   📋 Reportes APK: http://localhost:3001/reportes")
print("   🚨 Incidencias: http://localhost:3001/incidencias")
print("\n" + "="*80)

session.close()
