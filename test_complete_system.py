# Sistema de Pruebas Completas - BDD Manual

import json
import requests
import time
from datetime import datetime

class TestsLatacungaResiduos:
    """
    Pruebas BDD manuales para el sistema de gestión de residuos de Latacunga
    """
    
    def __init__(self):
        self.base_url = "http://localhost:8000/api"
        self.test_results = []
        
    def log_test(self, test_name, passed, details=""):
        """Registrar resultado de prueba"""
        result = {
            "test": test_name,
            "passed": passed,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
        if details:
            print(f"   Details: {details}")
    
    def test_health_check(self):
        """Prueba: Verificar que el servicio esté disponible"""
        try:
            response = requests.get(f"{self.base_url}/auth/health/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    self.log_test("Health Check", True, f"Service healthy, RabbitMQ: {data.get('rabbitmq_status')}")
                else:
                    self.log_test("Health Check", False, f"Service not healthy: {data}")
            else:
                self.log_test("Health Check", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Health Check", False, str(e))
    
    def test_user_registration(self):
        """Prueba: Registro de usuario"""
        user_data = {
            "email": f"test_{int(time.time())}@latacunga.gob.ec",
            "password": "TestPassword123!",
            "password_confirm": "TestPassword123!",
            "first_name": "Usuario",
            "last_name": "Prueba",
            "role": "citizen"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/auth/register/",
                json=user_data,
                timeout=10
            )
            
            if response.status_code == 201:
                data = response.json()
                if data.get("success"):
                    self.log_test("User Registration", True, f"User created: {data['user']['email']}")
                    return user_data["email"], user_data["password"]
                else:
                    self.log_test("User Registration", False, f"Registration failed: {data}")
            else:
                self.log_test("User Registration", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("User Registration", False, str(e))
        
        return None, None
    
    def test_user_login(self, email, password):
        """Prueba: Inicio de sesión"""
        if not email or not password:
            self.log_test("User Login", False, "No email/password from registration")
            return None
            
        login_data = {
            "identifier": email,
            "password": password
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/auth/login/",
                json=login_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if "access" in data:
                    self.log_test("User Login", True, "JWT tokens received")
                    return data["access"]
                else:
                    self.log_test("User Login", False, f"No access token: {data}")
            else:
                self.log_test("User Login", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("User Login", False, str(e))
        
        return None
    
    def test_protected_endpoint(self, access_token):
        """Prueba: Acceso a endpoint protegido"""
        if not access_token:
            self.log_test("Protected Endpoint", False, "No access token")
            return
            
        headers = {"Authorization": f"Bearer {access_token}"}
        
        try:
            response = requests.get(
                f"{self.base_url}/auth/profile/",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if "email" in data:
                    self.log_test("Protected Endpoint", True, f"Profile accessed: {data['email']}")
                else:
                    self.log_test("Protected Endpoint", False, f"Invalid profile data: {data}")
            else:
                self.log_test("Protected Endpoint", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Protected Endpoint", False, str(e))
    
    def test_unauthorized_access(self):
        """Prueba: Acceso sin autorización"""
        try:
            response = requests.get(f"{self.base_url}/auth/profile/", timeout=10)
            
            if response.status_code == 401:
                self.log_test("Unauthorized Access", True, "Correctly rejected unauthorized request")
            else:
                self.log_test("Unauthorized Access", False, f"Expected 401, got {response.status_code}")
        except Exception as e:
            self.log_test("Unauthorized Access", False, str(e))
    
    def test_api_documentation(self):
        """Prueba: Documentación de API disponible"""
        try:
            response = requests.get("http://localhost:8000/api/docs/", timeout=10)
            
            if response.status_code == 200:
                if "Swagger" in response.text or "API" in response.text:
                    self.log_test("API Documentation", True, "Swagger documentation available")
                else:
                    self.log_test("API Documentation", False, "Documentation page doesn't contain expected content")
            else:
                self.log_test("API Documentation", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("API Documentation", False, str(e))
    
    def test_frontend_availability(self):
        """Prueba: Frontend disponible"""
        try:
            response = requests.get("http://localhost:3001/", timeout=10)
            
            if response.status_code == 200:
                if "html" in response.text.lower():
                    self.log_test("Frontend Availability", True, "React frontend is accessible")
                else:
                    self.log_test("Frontend Availability", False, "Response doesn't contain HTML")
            else:
                self.log_test("Frontend Availability", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Frontend Availability", False, str(e))
    
    def run_all_tests(self):
        """Ejecutar todas las pruebas BDD"""
        print("🧪 INICIANDO PRUEBAS BDD DEL SISTEMA")
        print("=" * 50)
        
        # Escenario 1: Verificar disponibilidad del sistema
        self.test_health_check()
        self.test_api_documentation()
        self.test_frontend_availability()
        
        # Escenario 2: Flujo completo de autenticación
        email, password = self.test_user_registration()
        access_token = self.test_user_login(email, password)
        self.test_protected_endpoint(access_token)
        
        # Escenario 3: Seguridad
        self.test_unauthorized_access()
        
        # Generar reporte
        self.generate_report()
    
    def generate_report(self):
        """Generar reporte de pruebas"""
        print("\n📋 REPORTE DE PRUEBAS")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t["passed"]])
        failed_tests = total_tests - passed_tests
        
        print(f"Total de pruebas: {total_tests}")
        print(f"✅ Pasaron: {passed_tests}")
        print(f"❌ Fallaron: {failed_tests}")
        print(f"🎯 Porcentaje de éxito: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ PRUEBAS FALLIDAS:")
            for test in self.test_results:
                if not test["passed"]:
                    print(f"   - {test['test']}: {test['details']}")
        
        # Guardar reporte en archivo
        with open("test_report.json", "w", encoding="utf-8") as f:
            json.dump({
                "summary": {
                    "total": total_tests,
                    "passed": passed_tests,
                    "failed": failed_tests,
                    "success_rate": f"{(passed_tests/total_tests)*100:.1f}%",
                    "timestamp": datetime.now().isoformat()
                },
                "tests": self.test_results
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Reporte guardado en: test_report.json")

if __name__ == "__main__":
    tester = TestsLatacungaResiduos()
    tester.run_all_tests()