"""
Comando para verificar conectividad con tablas de Supabase
"""

from django.core.management.base import BaseCommand
import requests
from django.conf import settings


class Command(BaseCommand):
    help = 'Verifica si las tablas existen en Supabase'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔍 Verificando tablas en Supabase...'))
        
        # Configuración de Supabase
        supabase_url = settings.SUPABASE_URL
        supabase_anon_key = settings.SUPABASE_ANON_KEY
        
        headers = {
            'apikey': supabase_anon_key,
            'Authorization': f'Bearer {supabase_anon_key}',
            'Content-Type': 'application/json'
        }

        # Verificar tabla django_users
        try:
            response = requests.get(
                f'{supabase_url}/rest/v1/django_users?limit=1',
                headers=headers
            )
            
            if response.status_code == 200:
                self.stdout.write('✅ Tabla django_users existe en Supabase')
                data = response.json()
                self.stdout.write(f'📊 Registros encontrados: {len(data)}')
            elif response.status_code == 404:
                self.stdout.write('❌ Tabla django_users NO existe en Supabase')
                self.stdout.write('💡 Necesitas crearla usando el SQL Editor en tu dashboard de Supabase')
            else:
                self.stdout.write(f'⚠️  Error verificando tabla: {response.status_code} - {response.text}')
                
        except Exception as e:
            self.stdout.write(f'❌ Error conectando a Supabase: {str(e)}')
            
        self.stdout.write('🔗 Dashboard de Supabase: https://supabase.com/dashboard/projects')