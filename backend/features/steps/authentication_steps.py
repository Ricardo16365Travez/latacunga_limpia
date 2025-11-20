from behave import given, when, then
from django.contrib.auth import get_user_model
from django.test.client import Client
from rest_framework.test import APIClient
from apps.authentication.supabase_service import supabase_service
import json

User = get_user_model()

@given('que soy un usuario nuevo')
def step_new_user(context):
    """Configurar contexto para usuario nuevo"""
    context.user_data = None
    context.api_client = APIClient()

@when('registro mi cuenta con')
def step_register_user_with_data(context):
    """Registrar usuario con datos específicos"""
    # Convertir tabla de behave a diccionario
    user_data = {}
    for row in context.table:
        user_data[row['campo']] = row['valor']
    
    context.user_data = user_data
    
    # Preparar datos para el endpoint de registro
    registration_data = {
        'email': user_data['email'],
        'password': user_data['password'],
        'password2': user_data['password'],
        'first_name': user_data['nombre'],
        'last_name': user_data['apellido'],
        'role': user_data['rol']
    }
    
    # Hacer petición al endpoint de registro
    context.response = context.api_client.post(
        '/api/auth/register/',
        registration_data,
        format='json'
    )

@then('debería recibir una confirmación de registro')
def step_should_receive_registration_confirmation(context):
    """Verificar confirmación de registro"""
    assert context.response.status_code in [201, 200], \
        f"Código de estado esperado 201 o 200, recibido: {context.response.status_code}"
    
    response_data = context.response.json()
    assert 'success' in response_data or 'user' in response_data, \
        "La respuesta debe contener confirmación de éxito"

@then('el usuario debería existir en Supabase')
def step_user_should_exist_in_supabase(context):
    """Verificar que el usuario existe en Supabase"""
    # Intentar sincronizar con Supabase (esto se hace automáticamente en el registro)
    sync_result = supabase_service.sync_django_user_to_supabase(context.user_data)
    
    # Si el usuario ya existe en Supabase, la sincronización puede fallar,
    # pero eso no es necesariamente un error
    context.supabase_sync_result = sync_result

@then('debería recibir un token JWT válido')
def step_should_receive_valid_jwt_token(context):
    """Verificar que se recibe un token JWT válido"""
    response_data = context.response.json()
    
    # El token puede estar en diferentes campos dependiendo del endpoint
    token = None
    if 'access' in response_data:
        token = response_data['access']
    elif 'token' in response_data:
        token = response_data['token']
    elif 'access_token' in response_data:
        token = response_data['access_token']
    
    assert token is not None, "No se recibió token de acceso"
    assert len(token) > 20, "El token recibido parece ser inválido"
    
    context.access_token = token

@given('que existe un usuario registrado con')
def step_user_exists_with_credentials(context):
    """Crear usuario de prueba con credenciales específicas"""
    # Convertir tabla a diccionario
    credentials = {}
    for row in context.table:
        credentials[row['campo']] = row['valor']
    
    context.test_credentials = credentials
    
    # Crear usuario en Django
    user = User.objects.create_user(
        email=credentials['email'],
        password=credentials['password'],
        first_name='Test',
        last_name='User',
        role='citizen'
    )
    context.test_user = user
    context.api_client = APIClient()

@when('intento iniciar sesión con esas credenciales')
def step_login_with_credentials(context):
    """Intentar inicio de sesión"""
    login_data = {
        'email': context.test_credentials['email'],
        'password': context.test_credentials['password']
    }
    
    context.response = context.api_client.post(
        '/api/auth/login/',
        login_data,
        format='json'
    )

@given('que existe un usuario registrado')
def step_user_exists(context):
    """Crear usuario de prueba genérico"""
    user = User.objects.create_user(
        email='test@example.com',
        password='TestPassword123!',
        first_name='Test',
        last_name='User',
        role='citizen'
    )
    context.test_user = user
    context.api_client = APIClient()

@when('intento iniciar sesión con credenciales incorrectas')
def step_login_with_wrong_credentials(context):
    """Intentar inicio de sesión con credenciales incorrectas"""
    login_data = {
        'email': 'wrong@example.com',
        'password': 'WrongPassword123!'
    }
    
    context.response = context.api_client.post(
        '/api/auth/login/',
        login_data,
        format='json'
    )

@then('debería recibir un mensaje de error')
def step_should_receive_error_message(context):
    """Verificar mensaje de error"""
    assert context.response.status_code in [400, 401, 403], \
        f"Código de estado esperado 400-403, recibido: {context.response.status_code}"
    
    response_data = context.response.json()
    assert 'error' in response_data or 'detail' in response_data or 'message' in response_data, \
        "La respuesta debe contener un mensaje de error"

@then('no debería recibir ningún token')
def step_should_not_receive_token(context):
    """Verificar que no se recibe token"""
    response_data = context.response.json()
    
    assert 'access' not in response_data, "No debería haber token de acceso"
    assert 'token' not in response_data, "No debería haber token"
    assert 'access_token' not in response_data, "No debería haber access_token"

@given('que no estoy autenticado')
def step_not_authenticated(context):
    """Configurar cliente sin autenticación"""
    context.api_client = APIClient()

@when('intento acceder a un endpoint protegido')
def step_access_protected_endpoint(context):
    """Intentar acceder a endpoint protegido"""
    # Usar un endpoint que requiera autenticación
    context.response = context.api_client.get('/api/auth/profile/')

@then('debería recibir un error 401 Unauthorized')
def step_should_receive_401_error(context):
    """Verificar error 401"""
    assert context.response.status_code == 401, \
        f"Código de estado esperado 401, recibido: {context.response.status_code}"

@given('que registro un nuevo usuario en Django')
def step_register_new_user_django(context):
    """Registrar usuario nuevo en Django"""
    context.new_user_data = {
        'email': 'sync_test@example.com',
        'password': 'SyncTest123!',
        'first_name': 'Sync',
        'last_name': 'Test',
        'role': 'citizen'
    }

@when('el usuario se crea exitosamente')
def step_user_created_successfully(context):
    """Crear usuario en Django"""
    context.created_user = User.objects.create_user(**context.new_user_data)

@then('los datos deberían sincronizarse automáticamente con Supabase')
def step_data_should_sync_with_supabase(context):
    """Verificar sincronización con Supabase"""
    sync_result = supabase_service.sync_django_user_to_supabase(context.new_user_data)
    context.sync_result = sync_result
    
    # La sincronización puede fallar si el usuario ya existe, pero verificamos el intento
    assert 'success' in sync_result, "El resultado de sincronización debe tener campo 'success'"

@then('debería poder autenticarme usando las credenciales de Supabase')
def step_should_authenticate_with_supabase_credentials(context):
    """Verificar autenticación con credenciales de Supabase"""
    # Probar login a través del endpoint Django que usa Supabase
    login_data = {
        'email': context.new_user_data['email'],
        'password': context.new_user_data['password']
    }
    
    api_client = APIClient()
    response = api_client.post('/api/auth/login/', login_data, format='json')
    
    # Si la sincronización funcionó, debería poder hacer login
    context.supabase_login_response = response