from behave import given, when, then
from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.authentication.supabase_service import supabase_service
from django.conf import settings
import json

User = get_user_model()

@given('que las credenciales de Supabase están configuradas')
def step_supabase_credentials_configured(context):
    """Verificar que las credenciales de Supabase estén configuradas"""
    context.supabase_url = getattr(settings, 'SUPABASE_URL', None)
    context.supabase_key = getattr(settings, 'SUPABASE_ANON_KEY', None)
    context.supabase_service_key = getattr(settings, 'SUPABASE_SERVICE_ROLE_KEY', None)
    
    assert context.supabase_url is not None, "SUPABASE_URL no está configurada"
    assert context.supabase_key is not None, "SUPABASE_ANON_KEY no está configurada"
    assert context.supabase_service_key is not None, "SUPABASE_SERVICE_ROLE_KEY no está configurada"

@when('pruebo la conexión con la base de datos')
def step_test_database_connection(context):
    """Probar conexión con Supabase"""
    context.connection_result = supabase_service.test_connection()

@then('la conexión debería ser exitosa')
def step_connection_should_be_successful(context):
    """Verificar que la conexión sea exitosa"""
    assert context.connection_result['success'], f"Conexión fallida: {context.connection_result['message']}"

@then('debería poder ejecutar consultas básicas')
def step_should_execute_basic_queries(context):
    """Verificar que se pueden ejecutar consultas básicas"""
    # La conexión exitosa ya implica que se pueden ejecutar consultas
    assert 'data' in context.connection_result, "No se recibieron datos de la consulta"

@given('que el sistema está iniciado')
def step_system_is_started(context):
    """El sistema Django está iniciado"""
    pass

@when('reviso las variables de configuración de Supabase')
def step_check_supabase_configuration(context):
    """Revisar variables de configuración"""
    context.config_check = {
        'supabase_url': getattr(settings, 'SUPABASE_URL', None),
        'supabase_anon_key': getattr(settings, 'SUPABASE_ANON_KEY', None),
        'supabase_service_role_key': getattr(settings, 'SUPABASE_SERVICE_ROLE_KEY', None)
    }

@then('SUPABASE_URL debería estar definida')
def step_supabase_url_should_be_defined(context):
    """Verificar que SUPABASE_URL esté definida"""
    assert context.config_check['supabase_url'] is not None, "SUPABASE_URL no está definida"
    assert context.config_check['supabase_url'].startswith('https://'), "SUPABASE_URL debe ser una URL HTTPS válida"

@then('SUPABASE_ANON_KEY debería estar definida')
def step_supabase_anon_key_should_be_defined(context):
    """Verificar que SUPABASE_ANON_KEY esté definida"""
    assert context.config_check['supabase_anon_key'] is not None, "SUPABASE_ANON_KEY no está definida"
    assert len(context.config_check['supabase_anon_key']) > 50, "SUPABASE_ANON_KEY parece ser inválida"

@then('SUPABASE_SERVICE_ROLE_KEY debería estar definida')
def step_supabase_service_role_key_should_be_defined(context):
    """Verificar que SUPABASE_SERVICE_ROLE_KEY esté definida"""
    assert context.config_check['supabase_service_role_key'] is not None, "SUPABASE_SERVICE_ROLE_KEY no está definida"
    assert len(context.config_check['supabase_service_role_key']) > 50, "SUPABASE_SERVICE_ROLE_KEY parece ser inválida"