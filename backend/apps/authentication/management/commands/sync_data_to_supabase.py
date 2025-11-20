"""
Comando para sincronizar datos de Django a tablas de Supabase.
Usa la API REST de Supabase para insertar datos.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import requests
import json
from django.conf import settings

User = get_user_model()


class Command(BaseCommand):
    help = 'Sincroniza datos de Django a tablas de Supabase'

    def add_arguments(self, parser):
        parser.add_argument('--table', type=str, default='all',
                          help='Especifica la tabla a sincronizar (django_users, all)')
        parser.add_argument('--force', action='store_true',
                          help='Forzar sincronización incluso si ya existen datos')

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('📊 Iniciando sincronización de datos a Supabase...'))
        
        # Configuración de Supabase
        supabase_url = settings.SUPABASE_URL
        supabase_anon_key = settings.SUPABASE_ANON_KEY
        
        headers = {
            'apikey': supabase_anon_key,
            'Authorization': f'Bearer {supabase_anon_key}',
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        }

        if options['table'] in ['django_users', 'all']:
            self.sync_users(supabase_url, headers)

        self.stdout.write(self.style.SUCCESS('✅ Sincronización completada'))

    def sync_users(self, supabase_url, headers):
        """Sincroniza usuarios de Django a Supabase"""
        self.stdout.write('👥 Sincronizando usuarios...')
        
        users = User.objects.all()
        success_count = 0
        error_count = 0

        for user in users:
            try:
                # Preparar datos del usuario usando los campos correctos
                user_data = {
                    'email': user.email,
                    'phone': user.phone or '',
                    'first_name': user.first_name or '',
                    'last_name': user.last_name or '',
                    'display_name': user.display_name or user.get_full_name(),
                    'role': user.role,
                    'status': user.status,
                    'is_active': user.is_active,
                    'is_staff': user.is_staff,
                    'created_at': user.created_at.isoformat() if user.created_at else None,
                    'updated_at': user.updated_at.isoformat() if user.updated_at else None,
                    'last_login_at': user.last_login_at.isoformat() if user.last_login_at else None
                }

                # Hacer request a Supabase
                response = requests.post(
                    f'{supabase_url}/rest/v1/django_users',
                    headers=headers,
                    data=json.dumps(user_data)
                )

                if response.status_code in [200, 201]:
                    self.stdout.write(f'  ✅ {user.email}: Sincronizado')
                    success_count += 1
                else:
                    self.stdout.write(f'  ❌ {user.email}: Error {response.status_code} - {response.text}')
                    error_count += 1

            except Exception as e:
                self.stdout.write(f'  ❌ {user.email}: Error - {str(e)}')
                error_count += 1

        self.stdout.write(f'📊 Usuarios sincronizados: {success_count} exitosos, {error_count} errores')

    def check_table_exists(self, supabase_url, headers, table_name):
        """Verifica si una tabla existe en Supabase"""
        try:
            response = requests.get(
                f'{supabase_url}/rest/v1/{table_name}?limit=1',
                headers=headers
            )
            return response.status_code == 200
        except:
            return False