#!/usr/bin/env python3
"""
Script simple para probar endpoints de autenticación.
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_single_endpoint():
    """Probar un endpoint individual."""
    
    print("🔍 Probando endpoint de registro...")
    
    registration_data = {
        "email": "test@wasteapp.com",
        "password": "test123456",
        "password_confirm": "test123456",
        "phone": "+593987654321",
        "first_name": "Usuario",
        "last_name": "Prueba"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/register/",
            json=registration_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        # Intentar decodificar como JSON
        try:
            data = response.json()
            print("Response JSON:")
            print(json.dumps(data, indent=2))
        except:
            print("Response Text:")
            print(response.text[:1000])  # Primeros 1000 caracteres
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

if __name__ == "__main__":
    test_single_endpoint()