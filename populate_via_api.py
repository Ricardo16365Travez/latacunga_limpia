"""Poblar datos usando la API REST del backend"""
import requests
import random
from datetime import datetime

BASE_URL = "http://localhost:8000/api"

print("="*80)
print("POBLANDO DATOS VÍA API REST")
print("="*80)

# ============================================================================
# 1. REPORTES DESDE APK
# ============================================================================
print("\n📱 CREANDO REPORTES...")

reportes = [
    {
        "description": "Zona crítica con acumulación excesiva de residuos en Av. Unidad Nacional",
        "type": "critico",
        "location_lat": -0.934915,
        "location_lon": -78.617142,
        "photo_url": "https://example.com/photos/zona1.jpg"
    },
    {
        "description": "Punto de acopio lleno necesita recolección urgente - Sector La Matriz",
        "type": "acopio",
        "location_lat": -0.936120,
        "location_lon": -78.619890,
        "photo_url": "https://example.com/photos/acopio1.jpg"
    },
    {
        "description": "Basura dispersa en parque central, zona critica residencial",
        "type": "critico",
        "location_lat": -0.925318,
        "location_lon": -78.615067,
        "photo_url": None
    },
    {
        "description": "Contenedor de reciclaje desbordado en mercado municipal",
        "type": "acopio",
        "location_lat": -0.940250,
        "location_lon": -78.620145,
        "photo_url": "https://example.com/photos/contenedor.jpg"
    },
    {
        "description": "Animales dispersando basura, zona crítica comercial urgente",
        "type": "critico",
        "location_lat": -0.938901,
        "location_lon": -78.616789,
        "photo_url": None
    },
    {
        "description": "Punto de acopio en mal estado, requiere reparación inmediata",
        "type": "acopio",
        "location_lat": -0.932500,
        "location_lon": -78.618900,
        "photo_url": "https://example.com/photos/acopio2.jpg"
    }
]

for reporte in reportes:
    try:
        response = requests.post(f"{BASE_URL}/reportes/", json=reporte, timeout=10)
        if response.status_code in [200, 201]:
            data = response.json()
            print(f"   ✓ {reporte['type']:8} - {reporte['description'][:50]}...")
        else:
            print(f"   ⚠️  Error {response.status_code}: {response.text[:70]}")
    except Exception as e:
        print(f"   ❌ Error: {str(e)[:60]}")

# ============================================================================
# RESUMEN
# ============================================================================
print("\n" + "="*80)
print("📊 VERIFICANDO DATOS CREADOS")
print("="*80)

try:
    response = requests.get(f"{BASE_URL}/reportes/", timeout=10)
    if response.status_code == 200:
        reportes_list = response.json()
        print(f"   • Reportes totales: {len(reportes_list)}")
        print(f"   • Tipo 'critico': {len([r for r in reportes_list if r['type'] == 'critico'])}")
        print(f"   • Tipo 'acopio': {len([r for r in reportes_list if r['type'] == 'acopio'])}")
except Exception as e:
    print(f"   ❌ Error al verificar: {e}")

print("\n✅ Proceso completado")
print("="*80)
