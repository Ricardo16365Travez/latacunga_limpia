"""
Supabase Service for Django Integration
"""
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class SupabaseService:
    """
    Servicio para interactuar con Supabase desde Django
    """
    
    def __init__(self):
        self.url = settings.SUPABASE_URL
        self.key = settings.SUPABASE_ANON_KEY
        self.service_role_key = settings.SUPABASE_SERVICE_ROLE_KEY
        
        # Inicialización diferida para evitar errores de importación
        self.admin_client = None
        self.client = None
    
    def _init_clients(self):
        """Inicializar clientes de Supabase solo cuando se necesiten"""
        if self.client is None:
            try:
                from supabase import create_client
                
                # Cliente con permisos de administrador
                self.admin_client = create_client(self.url, self.service_role_key)
                
                # Cliente anónimo para operaciones públicas  
                self.client = create_client(self.url, self.key)
                
                logger.info("✅ Clientes Supabase inicializados correctamente")
                
            except Exception as e:
                logger.error(f"❌ Error inicializando clientes Supabase: {e}")
                raise e
    
    def get_client(self, admin=False):
        """
        Obtener cliente de Supabase
        
        Args:
            admin (bool): Si True, devuelve el cliente con permisos de admin
        
        Returns:
            Client: Cliente de Supabase
        """
        self._init_clients()
        return self.admin_client if admin else self.client
    
    def test_connection(self) -> dict:
        """
        Probar conexión con Supabase
        
        Returns:
            dict: Resultado de la prueba
        """
        try:
            # Inicializar clientes si no están inicializados
            self._init_clients()
            
            # Intentar una operación simple con el cliente público
            response = self.client.auth.get_session()
            
            logger.info("✅ Conexión con Supabase exitosa")
            return {
                'success': True,
                'message': 'Conexión con Supabase establecida correctamente',
                'data': response.data
            }
        except Exception as e:
            logger.error(f"❌ Error conectando con Supabase: {str(e)}")
            return {
                'success': False,
                'message': f'Error de conexión: {str(e)}',
                'data': None
            }
    
    def sync_django_user_to_supabase(self, user_data: dict) -> dict:
        """
        Sincronizar usuario de Django con Supabase Auth
        
        Args:
            user_data (dict): Datos del usuario
            
        Returns:
            dict: Resultado de la sincronización
        """
        try:
            # Crear usuario en Supabase Auth
            auth_response = self.admin_client.auth.admin.create_user({
                'email': user_data.get('email'),
                'password': user_data.get('password'),
                'email_confirm': True,
                'user_metadata': {
                    'first_name': user_data.get('first_name'),
                    'last_name': user_data.get('last_name'),
                    'role': user_data.get('role', 'citizen')
                }
            })
            
            logger.info(f"✅ Usuario sincronizado con Supabase: {user_data.get('email')}")
            return {
                'success': True,
                'message': 'Usuario sincronizado correctamente',
                'supabase_user': auth_response.user
            }
        except Exception as e:
            logger.error(f"❌ Error sincronizando usuario: {str(e)}")
            return {
                'success': False,
                'message': f'Error de sincronización: {str(e)}',
                'supabase_user': None
            }

# Instancia global del servicio
supabase_service = SupabaseService()