#!/usr/bin/env python
"""
Script de prueba para verificar que FastAPI se inicia correctamente
"""
import sys
import os

# Agregar el directorio backend al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app.main import app
    print("✅ FastAPI app cargó correctamente")
    print("Rutas disponibles:")
    for route in app.routes:
        if hasattr(route, 'path'):
            print(f"  - {route.path}")
except Exception as e:
    print(f"❌ Error al cargar FastAPI: {e}")
    import traceback
    traceback.print_exc()
