from django.core.management.base import BaseCommand
from django.conf import settings
import requests


class Command(BaseCommand):
    help = 'Crear tablas en Supabase PostgreSQL'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--create-tables',
            action='store_true',
            help='Crear las tablas en Supabase',
        )
        parser.add_argument(
            '--sync-data',
            action='store_true', 
            help='Sincronizar datos a las tablas de Supabase',
        )

    def handle(self, *args, **options):
        if options['create_tables']:
            self.create_tables()
        elif options['sync_data']:
            self.sync_data_to_tables()
        else:
            self.stdout.write('Usar --create-tables o --sync-data')

    def create_tables(self):
        """Crear tablas en Supabase usando REST API"""
        self.stdout.write('🏗️  Creando tablas en Supabase...')
        
        # SQL para crear tabla de usuarios
        create_users_table_sql = """
        CREATE TABLE IF NOT EXISTS django_users (
            id UUID PRIMARY KEY,
            email VARCHAR(254) UNIQUE,
            phone VARCHAR(20),
            first_name VARCHAR(50),
            last_name VARCHAR(50),
            display_name VARCHAR(100),
            role VARCHAR(20) DEFAULT 'user',
            status VARCHAR(20) DEFAULT 'ACTIVE',
            is_active BOOLEAN DEFAULT true,
            is_staff BOOLEAN DEFAULT false,
            created_at TIMESTAMP WITH TIME ZONE,
            updated_at TIMESTAMP WITH TIME ZONE,
            last_login_at TIMESTAMP WITH TIME ZONE
        );
        
        -- Crear índices
        CREATE INDEX IF NOT EXISTS idx_django_users_email ON django_users(email);
        CREATE INDEX IF NOT EXISTS idx_django_users_role ON django_users(role);
        CREATE INDEX IF NOT EXISTS idx_django_users_status ON django_users(status);
        """
        
        # También crear tabla para OTP codes
        create_otp_table_sql = """
        CREATE TABLE IF NOT EXISTS django_otp_codes (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID REFERENCES django_users(id),
            code VARCHAR(6),
            purpose VARCHAR(20),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            expires_at TIMESTAMP WITH TIME ZONE,
            is_used BOOLEAN DEFAULT false
        );
        
        CREATE INDEX IF NOT EXISTS idx_django_otp_user_id ON django_otp_codes(user_id);
        CREATE INDEX IF NOT EXISTS idx_django_otp_code ON django_otp_codes(code);
        """
        
        try:
            # Ejecutar SQL usando la REST API de PostgREST
            url = f"{settings.SUPABASE_URL}/rest/v1/rpc/exec_sql"
            headers = {
                'apikey': settings.SUPABASE_ANON_KEY,
                'Authorization': f'Bearer {settings.SUPABASE_ANON_KEY}',
                'Content-Type': 'application/json'
            }
            
            # Intentar crear las tablas usando diferentes métodos
            self.stdout.write('📡 Intentando crear tablas...')
            
            # Método 1: Usando función SQL personalizada
            sql_payload = {
                'sql': create_users_table_sql + create_otp_table_sql
            }
            
            response = requests.post(url, json=sql_payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                self.stdout.write(
                    self.style.SUCCESS('✅ Tablas creadas exitosamente en Supabase')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠️  Método directo falló: {response.status_code} - {response.text}')
                )
                
                # Método 2: Crear directamente las tablas usando inserción
                self.create_tables_via_insert()
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error al crear tablas: {str(e)}')
            )
            
    def create_tables_via_insert(self):
        """Crear tablas insertando una fila de ejemplo y luego borrarla"""
        self.stdout.write('🔄 Intentando método alternativo...')
        
        try:
            # Crear tabla usuarios insertando un registro de ejemplo
            url = f"{settings.SUPABASE_URL}/rest/v1/django_users"
            headers = {
                'apikey': settings.SUPABASE_ANON_KEY,
                'Authorization': f'Bearer {settings.SUPABASE_ANON_KEY}',
                'Content-Type': 'application/json',
                'Prefer': 'return=minimal'
            }
            
            # Datos de ejemplo para crear la estructura
            example_user = {
                'id': '00000000-0000-0000-0000-000000000000',
                'email': 'example@example.com',
                'phone': None,
                'first_name': 'Example',
                'last_name': 'User',
                'display_name': 'Example User',
                'role': 'user',
                'status': 'ACTIVE',
                'is_active': True,
                'is_staff': False,
                'created_at': '2025-11-20T10:00:00Z',
                'updated_at': '2025-11-20T10:00:00Z',
                'last_login_at': None
            }
            
            # Intentar insertar
            response = requests.post(url, json=example_user, headers=headers, timeout=10)
            
            if response.status_code in [200, 201]:
                self.stdout.write('✅ Tabla django_users creada')
                
                # Borrar el registro de ejemplo
                delete_url = f"{url}?id=eq.00000000-0000-0000-0000-000000000000"
                requests.delete(delete_url, headers=headers, timeout=10)
                
            else:
                self.stdout.write(f'⚠️  No se pudo crear tabla: {response.status_code} - {response.text}')
                
        except Exception as e:
            self.stdout.write(f'❌ Error en método alternativo: {str(e)}')

    def sync_data_to_tables(self):
        """Sincronizar datos de Django a tablas de Supabase"""
        self.stdout.write('📤 Sincronizando datos a Supabase...')
        
        from apps.authentication.models import User
        
        try:
            users = User.objects.filter(is_active=True)
            self.stdout.write(f'👥 Sincronizando {users.count()} usuarios')
            
            url = f"{settings.SUPABASE_URL}/rest/v1/django_users"
            headers = {
                'apikey': settings.SUPABASE_ANON_KEY,
                'Authorization': f'Bearer {settings.SUPABASE_ANON_KEY}',
                'Content-Type': 'application/json',
                'Prefer': 'resolution=merge-duplicates'
            }
            
            success_count = 0
            error_count = 0
            
            for user in users:
                try:
                    user_data = {
                        'id': str(user.id),
                        'email': user.email,
                        'phone': user.phone,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'display_name': user.display_name,
                        'role': user.role,
                        'status': user.status,
                        'is_active': user.is_active,
                        'is_staff': user.is_staff,
                        'created_at': user.created_at.isoformat(),
                        'updated_at': user.updated_at.isoformat(),
                        'last_login_at': user.last_login_at.isoformat() if user.last_login_at else None
                    }
                    
                    response = requests.post(url, json=user_data, headers=headers, timeout=10)
                    
                    if response.status_code in [200, 201]:
                        success_count += 1
                        self.stdout.write(f'  ✅ {user.email}')
                    else:
                        error_count += 1
                        self.stdout.write(f'  ❌ {user.email}: {response.status_code}')
                        
                except Exception as e:
                    error_count += 1
                    self.stdout.write(f'  ❌ {user.email}: {str(e)}')
                    
            self.stdout.write(
                self.style.SUCCESS(f'📊 Sincronización completa: {success_count} exitosos, {error_count} errores')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error en sincronización de datos: {str(e)}')
            )