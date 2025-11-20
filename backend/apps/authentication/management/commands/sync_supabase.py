"""
Comando para sincronizar datos entre Django local y Supabase
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from apps.authentication.models import User
import json
import sys

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False


class Command(BaseCommand):
    help = 'Sincroniza datos entre la base de datos local y Supabase'

    def add_arguments(self, parser):
        parser.add_argument(
            '--direction',
            choices=['to-supabase', 'from-supabase', 'test-connection'],
            default='test-connection',
            help='Dirección de sincronización'
        )
        parser.add_argument(
            '--model',
            choices=['users', 'all'],
            default='users',
            help='Modelo a sincronizar'
        )

    def handle(self, *args, **options):
        if not SUPABASE_AVAILABLE:
            self.stdout.write(
                self.style.ERROR('❌ Supabase no está disponible. Instalar: pip install supabase')
            )
            return

        direction = options['direction']
        model = options['model']

        self.stdout.write(f'🔄 Iniciando sincronización: {direction} - {model}')

        if direction == 'test-connection':
            self.test_supabase_connection()
        elif direction == 'to-supabase':
            self.sync_to_supabase(model)
        elif direction == 'from-supabase':
            self.sync_from_supabase(model)

    def get_supabase_client(self):
        """Crear cliente de Supabase"""
        try:
            # Importar solo lo que necesitamos
            from supabase import create_client
            
            url = settings.SUPABASE_URL
            key = getattr(settings, 'SUPABASE_SERVICE_ROLE_KEY', settings.SUPABASE_ANON_KEY)
            
            self.stdout.write(f'📡 Conectando a Supabase: {url}')
            
            # Crear cliente con configuración básica
            client = create_client(url, key)
            return client
            
        except ImportError:
            self.stdout.write(
                self.style.ERROR('❌ Supabase no está disponible. Instalar: pip install supabase')
            )
            return None
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error al crear cliente Supabase: {str(e)}')
            )
            return None

    def test_supabase_connection(self):
        """Probar conexión con Supabase"""
        self.stdout.write('🧪 Probando conexión con Supabase...')
        
        try:
            import requests
            
            # Probar conectividad básica con REST API
            url = f"{settings.SUPABASE_URL}/rest/v1/"
            headers = {
                'apikey': settings.SUPABASE_ANON_KEY,
                'Authorization': f'Bearer {settings.SUPABASE_ANON_KEY}'
            }
            
            self.stdout.write(f'📡 Probando conectividad a: {url}')
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                self.stdout.write(
                    self.style.SUCCESS('✅ Conexión con Supabase API exitosa!')
                )
                self.stdout.write(f'📊 Status Code: {response.status_code}')
                
                # Mostrar configuración
                self.stdout.write('\n📋 Configuración actual:')
                self.stdout.write(f'   URL: {settings.SUPABASE_URL}')
                self.stdout.write(f'   Key disponible: {"✅" if hasattr(settings, "SUPABASE_ANON_KEY") else "❌"}')
                self.stdout.write(f'   Service Key disponible: {"✅" if hasattr(settings, "SUPABASE_SERVICE_ROLE_KEY") else "❌"}')
                
                # Probar conexión PostgreSQL
                self.test_postgres_connection()
                
            else:
                self.stdout.write(
                    self.style.ERROR(f'❌ Error de API: Status {response.status_code}')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error al probar conexión: {str(e)}')
            )
    
    def test_postgres_connection(self):
        """Probar conexión directa a PostgreSQL de Supabase"""
        self.stdout.write('\n🐘 Probando conexión PostgreSQL directa...')
        
        try:
            import psycopg2
            
            # Configuración de conexión
            conn_config = {
                'host': 'aws-0-us-west-1.pooler.supabase.com',
                'port': 5432,
                'database': 'postgres',
                'user': 'postgres.ancwrsnnrchgwzrrbmwc',
                'password': 'SuwTHvwKqIlFeQ7y',
                'sslmode': 'require'
            }
            
            self.stdout.write(f'📡 Conectando a PostgreSQL: {conn_config["host"]}:{conn_config["port"]}')
            
            # Intentar conexión
            conn = psycopg2.connect(**conn_config)
            cursor = conn.cursor()
            
            # Ejecutar consulta simple
            cursor.execute('SELECT version();')
            version = cursor.fetchone()[0]
            
            self.stdout.write(
                self.style.SUCCESS('✅ Conexión PostgreSQL exitosa!')
            )
            self.stdout.write(f'📊 PostgreSQL version: {version[:50]}...')
            
            cursor.close()
            conn.close()
            
        except ImportError:
            self.stdout.write(
                self.style.WARNING('⚠️  psycopg2 no disponible para test PostgreSQL')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error PostgreSQL: {str(e)}')
            )

    def sync_to_supabase(self, model):
        """Sincronizar datos locales a Supabase"""
        self.stdout.write(f'📤 Sincronizando {model} hacia Supabase...')
        
        if model in ['users', 'all']:
            self.sync_users_to_supabase(None)  # No necesitamos cliente Supabase
        else:
            self.stdout.write(
                self.style.WARNING(f'⚠️  Modelo {model} no soportado')
            )

    def sync_users_to_supabase(self, client):
        """Sincronizar usuarios locales a Supabase usando signup API"""
        try:
            import requests
            
            users = User.objects.filter(is_active=True)
            self.stdout.write(f'👥 Encontrados {users.count()} usuarios locales activos')

            # URL de signup de Supabase (no requiere service_role)
            signup_url = f"{settings.SUPABASE_URL}/auth/v1/signup"
            headers = {
                'apikey': settings.SUPABASE_ANON_KEY,
                'Authorization': f'Bearer {settings.SUPABASE_ANON_KEY}',
                'Content-Type': 'application/json'
            }

            synced = 0
            errors = 0

            for user in users:
                try:
                    # Preparar datos del usuario para signup
                    user_data = {
                        'email': user.email,
                        'password': 'TempPassword123!',  # Contraseña temporal
                        'data': {
                            'display_name': user.display_name or user.email,
                            'first_name': user.first_name,
                            'last_name': user.last_name,
                            'role': user.role,
                            'phone': user.phone,
                            'django_user_id': str(user.id)
                        }
                    }
                    
                    # Enviar a Supabase Auth signup
                    response = requests.post(signup_url, json=user_data, headers=headers, timeout=10)
                    
                    if response.status_code in [200, 201]:
                        synced += 1
                        self.stdout.write(f'✅ Usuario registrado: {user.email}')
                    else:
                        # Si es error 422, probablemente el usuario ya existe
                        if response.status_code == 422:
                            error_data = response.json()
                            if 'already been registered' in str(error_data):
                                self.stdout.write(f'ℹ️  Usuario {user.email} ya está registrado en Supabase')
                                synced += 1
                            else:
                                errors += 1
                                self.stdout.write(f'❌ Error 422 para {user.email}: {error_data}')
                        else:
                            errors += 1
                            error_msg = response.text[:100] if response.text else 'Sin mensaje de error'
                            self.stdout.write(f'❌ Error {response.status_code} para {user.email}: {error_msg}')
                        
                except requests.RequestException as e:
                    errors += 1
                    self.stdout.write(f'❌ Error de conexión para {user.email}: {str(e)}')
                except Exception as e:
                    errors += 1
                    self.stdout.write(f'❌ Error al procesar {user.email}: {str(e)}')

            self.stdout.write(
                self.style.SUCCESS(f'📊 Sincronización completa: {synced} exitosos, {errors} errores')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error general en sincronización: {str(e)}')
            )

    def sync_from_supabase(self, model):
        """Sincronizar datos de Supabase a local"""
        self.stdout.write(f'📥 Sincronizando {model} desde Supabase...')
        
        client = self.get_supabase_client()
        if not client:
            return

        if model in ['users', 'all']:
            self.sync_users_from_supabase(client)

    def sync_users_from_supabase(self, client):
        """Sincronizar usuarios de Supabase a local"""
        try:
            response = client.table('django_users').select('*').execute()
            supabase_users = response.data
            
            self.stdout.write(f'👥 Encontrados {len(supabase_users)} usuarios en Supabase')

            synced = 0
            errors = 0

            for user_data in supabase_users:
                try:
                    # Buscar o crear usuario local
                    user, created = User.objects.get_or_create(
                        id=user_data['id'],
                        defaults={
                            'email': user_data.get('email'),
                            'phone': user_data.get('phone'),
                            'first_name': user_data.get('first_name', ''),
                            'last_name': user_data.get('last_name', ''),
                            'display_name': user_data.get('display_name', ''),
                            'role': user_data.get('role', 'user'),
                            'status': user_data.get('status', 'ACTIVE'),
                            'is_active': user_data.get('is_active', True),
                        }
                    )

                    if created:
                        self.stdout.write(f'✅ Usuario creado: {user.email}')
                    else:
                        self.stdout.write(f'📝 Usuario actualizado: {user.email}')
                    
                    synced += 1
                    
                except Exception as e:
                    errors += 1
                    self.stdout.write(
                        self.style.WARNING(f'⚠️  Error al procesar usuario: {str(e)}')
                    )

            self.stdout.write(
                self.style.SUCCESS(f'📊 Sincronización completa: {synced} procesados, {errors} errores')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error al obtener usuarios de Supabase: {str(e)}')
            )