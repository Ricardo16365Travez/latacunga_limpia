"""
Servicio híbrido para integrar Django local con Supabase
- Autenticación: Supabase Auth
- Almacenamiento: Django local + Supabase sync
- Realtime: Supabase
"""

from django.conf import settings
import requests
import logging

logger = logging.getLogger(__name__)


class HybridSupabaseService:
    """Servicio híbrido Django + Supabase"""
    
    def __init__(self):
        self.supabase_url = settings.SUPABASE_URL
        self.anon_key = settings.SUPABASE_ANON_KEY
        self.service_key = getattr(settings, 'SUPABASE_SERVICE_ROLE_KEY', self.anon_key)
    
    def create_supabase_user(self, email, password, user_metadata=None):
        """Crear usuario en Supabase Auth"""
        try:
            url = f"{self.supabase_url}/auth/v1/signup"
            headers = {
                'apikey': self.anon_key,
                'Authorization': f'Bearer {self.anon_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'email': email,
                'password': password,
                'data': user_metadata or {}
            }
            
            response = requests.post(url, json=data, headers=headers, timeout=10)
            
            if response.status_code in [200, 201]:
                result = response.json()
                logger.info(f"Usuario creado en Supabase: {email}")
                return {
                    'success': True,
                    'user': result.get('user'),
                    'session': result.get('session')
                }
            else:
                logger.error(f"Error al crear usuario en Supabase: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': response.text
                }
                
        except Exception as e:
            logger.error(f"Excepción al crear usuario en Supabase: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def authenticate_with_supabase(self, email, password):
        """Autenticar usuario con Supabase"""
        try:
            url = f"{self.supabase_url}/auth/v1/token?grant_type=password"
            headers = {
                'apikey': self.anon_key,
                'Authorization': f'Bearer {self.anon_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'email': email,
                'password': password
            }
            
            response = requests.post(url, json=data, headers=headers, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Autenticación exitosa en Supabase: {email}")
                return {
                    'success': True,
                    'access_token': result.get('access_token'),
                    'refresh_token': result.get('refresh_token'),
                    'user': result.get('user')
                }
            else:
                logger.warning(f"Error de autenticación en Supabase: {response.status_code}")
                return {
                    'success': False,
                    'error': response.text
                }
                
        except Exception as e:
            logger.error(f"Excepción en autenticación Supabase: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_supabase_user_info(self, access_token):
        """Obtener información del usuario desde Supabase"""
        try:
            url = f"{self.supabase_url}/auth/v1/user"
            headers = {
                'apikey': self.anon_key,
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'user': response.json()
                }
            else:
                return {
                    'success': False,
                    'error': response.text
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def sync_user_to_supabase_storage(self, user_data):
        """Sincronizar datos de usuario a un storage personalizado en Supabase"""
        try:
            # Usar Supabase Storage para almacenar JSON de usuarios
            url = f"{self.supabase_url}/storage/v1/object/user-data/{user_data['email']}.json"
            headers = {
                'apikey': self.service_key,
                'Authorization': f'Bearer {self.service_key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.put(url, json=user_data, headers=headers, timeout=10)
            
            return response.status_code in [200, 201]
            
        except Exception as e:
            logger.error(f"Error sincronizando a Supabase Storage: {str(e)}")
            return False
    
    def test_connection(self):
        """Probar conectividad con Supabase"""
        try:
            url = f"{self.supabase_url}/rest/v1/"
            headers = {
                'apikey': self.anon_key,
                'Authorization': f'Bearer {self.anon_key}'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            return {
                'api_status': response.status_code == 200,
                'status_code': response.status_code,
                'url': self.supabase_url,
                'auth_available': True
            }
            
        except Exception as e:
            return {
                'api_status': False,
                'error': str(e),
                'url': self.supabase_url,
                'auth_available': False
            }


# Instancia global del servicio
hybrid_service = HybridSupabaseService()