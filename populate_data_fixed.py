"""
Script simplificado para poblar el sistema con datos realistas
Tiene en cuenta todos los CHECK constraints de Neon
"""
import os
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta
import random

# Conectar a Neon
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://neondb_owner:npg_XBw8xVBZJRAm@ep-gentle-pond-a9dcmrdsv-pooler.us-east-1.aws.neon.tech/neondb")
engine = create_engine(DATABASE_URL)

print("="*80)
print("POBLANDO SISTEMA CON DATOS REALISTAS")
print("="*80)

# ============================================================================
# 1. REPORTES DESDE APK (Usar tipos correctos: 'acopio' o 'critico')
# ============================================================================
print("\n📱 REPORTES DESDE APK MÓVIL...")

# Obtener un user_id existente
with engine.connect() as conn:
    result = conn.execute(text("SELECT id FROM users LIMIT 1"))
    row = result.fetchone()
    if row:
        user_id = str(row[0])
    else:
        print("   ⚠️  No hay usuarios en la BD")
        user_id = None

if user_id:
    reportes = [
        {
            "user_id": user_id,
            "type": "critico",  # ✅ Valor válido según constraint
            "lat": -0.934915,
            "lon": -78.617142,
            "description": "Zona crítica con acumulación excesiva de residuos en Av. Unidad Nacional",
            "status": "ENVIADO",
            "photo_url": "https://example.com/photos/zona1.jpg"
        },
        {
            "user_id": user_id,
            "type": "acopio",  # ✅ Valor válido según constraint  
            "lat": -0.936120,
            "lon": -78.619890,
            "description": "Punto de acopio lleno necesita recolección urgente - Sector La Matriz",
            "status": "ENVIADO",
            "photo_url": "https://example.com/photos/acopio1.jpg"
        },
        {
            "user_id": user_id,
            "type": "critico",
            "lat": -0.925318,
            "lon": -78.615067,
            "description": "Basura dispersa en parque central, zona critica residencial",
            "status": "EN_PROCESO",
            "photo_url": None
        },
        {
            "user_id": user_id,
            "type": "acopio",
            "lat": -0.940250,
            "lon": -78.620145,
            "description": "Contenedor de reciclaje desbordado en mercado",
            "status": "ENVIADO",
            "photo_url": "https://example.com/photos/contenedor.jpg"
        },
        {
            "user_id": user_id,
            "type": "critico",
            "lat": -0.938901,
            "lon": -78.616789,
            "description": "Animales dispersando basura, zona crítica comercial",
            "status": "COMPLETADO",
            "photo_url": None
        }
    ]
    
    for r in reportes:
        try:
            with engine.connect() as conn:
                conn.execute(text("""
                    INSERT INTO reports (id, user_id, type, lat, lon, description, status, photo_url, 
                                       created_at, updated_at, synced)
                    VALUES (gen_random_uuid(), :user_id::uuid, :type, :lat, :lon, :description, 
                            :status, :photo_url, NOW() - INTERVAL '0 hours' * :days, NOW(), false)
                """), {
                    "user_id": user_id,
                    "type": r["type"],
                    "lat": r["lat"],
                    "lon": r["lon"],
                    "description": r["description"],
                    "status": r["status"],
                    "photo_url": r["photo_url"],
                    "days": random.randint(0, 5)
                })
                conn.commit()
                print(f"   ✓ Reporte {r['type']}: {r['description'][:50]}...")
        except Exception as e:
            print(f"   ⚠️  Error en reporte: {str(e)[:80]}")

# ============================================================================
# 2. INCIDENCIAS (con campo geom usando ST_SetSRID(ST_MakePoint))
# ============================================================================
print("\n🚨 INCIDENCIAS DEL SISTEMA...")

# Tipos válidos: 'acopio', 'zona_critica', 'animal_muerto'
# Gravedad válida: 1, 3, 5
# Zona válida: 'oriental', 'occidental'
# Estado válido: 'pendiente', 'validada', 'asignada', 'completada', 'cancelada'

incidencias = [
    {
        "tipo": "zona_critica",
        "gravedad": 5,
        "lat": -0.934915,
        "lon": -78.617142,
        "zona": "oriental",
        "descripcion": "Zona crítica con alto volumen de residuos",
        "estado": "pendiente"
    },
    {
        "tipo": "acopio",
        "gravedad": 3,
        "lat": -0.936120,
        "lon": -78.619890,
        "zona": "occidental",
        "descripcion": "Punto de acopio requiere mantenimiento",
        "estado": "validada"
    },
    {
        "tipo": "animal_muerto",
        "gravedad": 5,
        "lat": -0.925318,
        "lon": -78.615067,
        "zona": "oriental",
        "descripcion": "Animal muerto en vía pública",
        "estado": "asignada"
    },
    {
        "tipo": "zona_critica",
        "gravedad": 3,
        "lat": -0.940250,
        "lon": -78.620145,
        "zona": "occidental",
        "descripcion": "Acumulación moderada de residuos en calle principal",
        "estado": "completada"
    }
]

for inc in incidencias:
    try:
        with engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO incidencias (tipo, gravedad, descripcion, lat, lon, geom, zona, estado,
                                       ventana_inicio, ventana_fin, reportado_en, created_at, updated_at)
                VALUES (:tipo, :gravedad, :descripcion, :lat, :lon, 
                        ST_SetSRID(ST_MakePoint(:lon, :lat), 4326),
                        :zona, :estado,
                        NOW() + INTERVAL '1 day',
                        NOW() + INTERVAL '3 days',
                        NOW() - INTERVAL '0 hours' * :days,
                        NOW(), NOW())
            """), {
                "tipo": inc["tipo"],
                "gravedad": inc["gravedad"],
                "descripcion": inc["descripcion"],
                "lat": inc["lat"],
                "lon": inc["lon"],
                "zona": inc["zona"],
                "estado": inc["estado"],
                "days": random.randint(0, 3)
            })
            conn.commit()
            print(f"   ✓ {inc['tipo']} (gravedad {inc['gravedad']}): {inc['descripcion'][:50]}...")
    except Exception as e:
        print(f"   ⚠️  Error: {str(e)[:80]}")

# ============================================================================
# 3. CONDUCTORES (usuario_id es INTEGER, no UUID)
# ============================================================================
print("\n🚗 CONDUCTORES...")

# Obtener usuarios operadores (sus IDs son INTEGER en Neon)
with engine.connect() as conn:
    result = conn.execute(text("SELECT id FROM users WHERE role = 'operador' LIMIT 5"))
    usuario_ids = [row[0] for row in result]

if len(usuario_ids) < 3:
    print("   ⚠️  Necesitas al menos 3 operadores. Creando...")
    # Los IDs 1, 2, 3 suelen estar disponibles
    usuario_ids = [1, 2, 3]

# Estados válidos: 'disponible', 'ocupado', 'inactivo'
# Zonas válidas: 'oriental', 'occidental', 'ambas'
# Licencias válidas: 'C', 'D', 'E'

conductores = [
    {
        "nombre_completo": "Carlos Andrés Martínez Vega",
        "cedula": "1803456789",
        "telefono": "+593998765432",
        "licencia_tipo": "C",
        "estado": "disponible",
        "zona_preferida": "oriental",
        "usuario_id": usuario_ids[0]
    },
    {
        "nombre_completo": "Luis Fernando Vega Robles",
        "cedula": "1804567890",
        "telefono": "+593987654321",
        "licencia_tipo": "D",
        "estado": "ocupado",
        "zona_preferida": "occidental",
        "usuario_id": usuario_ids[1] if len(usuario_ids) > 1 else usuario_ids[0]
    },
    {
        "nombre_completo": "Pedro Antonio Rojas Cruz",
        "cedula": "1805678901",
        "telefono": "+593976543210",
        "licencia_tipo": "E",
        "estado": "disponible",
        "zona_preferida": "ambas",
        "usuario_id": usuario_ids[2] if len(usuario_ids) > 2 else usuario_ids[0]
    }
]

for c in conductores:
    try:
        with engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO conductores (nombre_completo, cedula, telefono, licencia_tipo, 
                                       estado, zona_preferida, usuario_id, 
                                       fecha_contratacion, created_at, updated_at)
                VALUES (:nombre_completo, :cedula, :telefono, :licencia_tipo,
                        :estado, :zona_preferida, :usuario_id,
                        NOW() - INTERVAL '1 year' * :years, NOW(), NOW())
                ON CONFLICT (cedula) DO UPDATE SET
                    telefono = EXCLUDED.telefono,
                    estado = EXCLUDED.estado
            """), {
                "nombre_completo": c["nombre_completo"],
                "cedula": c["cedula"],
                "telefono": c["telefono"],
                "licencia_tipo": c["licencia_tipo"],
                "estado": c["estado"],
                "zona_preferida": c["zona_preferida"],
                "usuario_id": c["usuario_id"],
                "years": random.uniform(0.5, 5)
            })
            conn.commit()
            print(f"   ✓ {c['nombre_completo']} ({c['licencia_tipo']}) - {c['estado']}")
    except Exception as e:
        print(f"   ⚠️  {c['nombre_completo']}: {str(e)[:60]}")

# ============================================================================
# RESUMEN FINAL
# ============================================================================
print("\n" + "="*80)
print("📊 RESUMEN DE DATOS")
print("="*80)

with engine.connect() as conn:
    for table in ['reports', 'incidencias', 'conductores']:
        result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
        count = result.fetchone()[0]
        print(f"   • {table:20}: {count:3} registros")

print("\n✅ Datos cargados correctamente")
print("="*80)
