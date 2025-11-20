import os
import django
from django.conf import settings

def before_all(context):
    """Configuración global antes de todas las pruebas"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()

def before_scenario(context, scenario):
    """Configuración antes de cada escenario"""
    # Limpiar la base de datos entre escenarios
    from django.core.management import call_command
    from django.test.utils import setup_test_environment, teardown_test_environment
    
    # Configurar entorno de pruebas
    setup_test_environment()
    
    # Crear base de datos temporal para pruebas
    from django.test import TransactionTestCase
    from django.db import connection
    
    context.test_db = connection.creation.create_test_db()

def after_scenario(context, scenario):
    """Limpieza después de cada escenario"""
    if hasattr(context, 'test_db'):
        from django.db import connection
        connection.creation.destroy_test_db(context.test_db)

def before_step(context, step):
    """Configuración antes de cada paso"""
    pass

def after_step(context, step):
    """Limpieza después de cada paso"""
    pass