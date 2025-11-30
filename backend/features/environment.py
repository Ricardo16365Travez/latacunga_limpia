import os
import django
from django.conf import settings

def before_all(context):
    """Configuración global antes de todas las pruebas"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()
    
    # Configurar cliente API
    from rest_framework.test import APIClient
    context.client = APIClient()

def before_scenario(context, scenario):
    """Configuración antes de cada escenario"""
    # Limpiar la base de datos entre escenarios
    from django.core.management import call_command
    from django.test.utils import setup_test_environment
    
    # Configurar entorno de pruebas
    setup_test_environment()
    
    # Variables de contexto
    context.response = None
    context.user = None
    context.task = None
    context.route = None
    context.notification = None

def after_scenario(context, scenario):
    """Limpieza después de cada escenario"""
    # Limpiar datos de prueba
    from django.test.utils import teardown_test_environment
    teardown_test_environment()


def before_step(context, step):
    """Configuración antes de cada paso"""
    pass

def after_step(context, step):
    """Limpieza después de cada paso"""
    pass