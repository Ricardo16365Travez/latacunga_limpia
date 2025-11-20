#!/usr/bin/env python3
"""
Script simple para probar la conectividad del backend.
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_backend_health():
    """Probar conectividad básica del backend."""
    
    print("🔍 Probando conectividad del backend...")
    
    try:
        # Test health endpoint
        response = requests.get(f"{BASE_URL}/api/auth/health/")
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Backend está funcionando correctamente!")
            return True
        else:
            print("❌ Backend no responde correctamente")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar al backend - servicio no disponible")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def test_cors():
    """Probar si CORS está configurado correctamente."""
    
    print("\n🔍 Probando configuración CORS...")
    
    headers = {
        'Origin': 'http://localhost:3001',
        'Content-Type': 'application/json'
    }
    
    try:
        # Test OPTIONS request (preflight)
        response = requests.options(f"{BASE_URL}/api/auth/login/", headers=headers)
        
        print(f"OPTIONS Status Code: {response.status_code}")
        print(f"CORS Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ CORS configurado correctamente!")
            return True
        else:
            print("❌ Problema con configuración CORS")
            return False
            
    except Exception as e:
        print(f"❌ Error en test CORS: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Diagnosticando conectividad frontend-backend\n")
    
    health_ok = test_backend_health()
    cors_ok = test_cors()
    
    print(f"\n📊 Resultados:")
    print(f"Backend Health: {'✅' if health_ok else '❌'}")
    print(f"CORS Config: {'✅' if cors_ok else '❌'}")
    
    if health_ok and cors_ok:
        print("\n🎉 Todo está funcionando correctamente!")
    else:
        print("\n⚠️ Hay problemas de conectividad que necesitan ser resueltos.")