#!/bin/bash

# Script de ejecución para sistema con Supabase y pruebas BDD

echo "🚀 Iniciando Sistema de Gestión de Residuos Latacunga con Supabase"
echo "================================================================="

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir con colores
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# 1. Verificar dependencias
print_info "Verificando dependencias del sistema..."

# Verificar Docker
if ! command -v docker &> /dev/null; then
    print_error "Docker no está instalado"
    exit 1
else
    print_status "Docker está disponible"
fi

# Verificar Docker Compose
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose no está instalado"
    exit 1
else
    print_status "Docker Compose está disponible"
fi

# 2. Limpiar contenedores existentes
print_info "Limpiando contenedores existentes..."
docker-compose down --remove-orphans
docker system prune -f

# 3. Construir e iniciar servicios
print_info "Construyendo e iniciando servicios..."
docker-compose up --build -d

# 4. Esperar a que los servicios estén listos
print_info "Esperando a que los servicios estén listos..."

# Esperar RabbitMQ
print_info "Esperando RabbitMQ..."
timeout 60 bash -c 'until curl -s http://localhost:15672/api/alarms > /dev/null 2>&1; do sleep 2; done'
if [ $? -eq 0 ]; then
    print_status "RabbitMQ está listo"
else
    print_warning "RabbitMQ tardó más de lo esperado"
fi

# Esperar Redis
print_info "Esperando Redis..."
timeout 30 bash -c 'until docker exec residuos_redis redis-cli ping > /dev/null 2>&1; do sleep 2; done'
if [ $? -eq 0 ]; then
    print_status "Redis está listo"
else
    print_warning "Redis tardó más de lo esperado"
fi

# Esperar Backend
print_info "Esperando Backend..."
timeout 120 bash -c 'until curl -s http://localhost:8000/api/health/ > /dev/null 2>&1; do sleep 3; done'
if [ $? -eq 0 ]; then
    print_status "Backend está listo"
else
    print_warning "Backend tardó más de lo esperado"
fi

# 5. Ejecutar migraciones y configuración inicial
print_info "Ejecutando migraciones de base de datos en Supabase..."
docker exec -i residuos_backend python manage.py migrate

# Crear superusuario si no existe
print_info "Configurando usuario administrador..."
docker exec -i residuos_backend python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email='admin@latacunga.gob.ec').exists():
    User.objects.create_superuser(
        email='admin@latacunga.gob.ec',
        password='admin123',
        first_name='Admin',
        last_name='Sistema',
        role='admin'
    )
    print('✅ Superusuario creado')
else:
    print('ℹ️  Superusuario ya existe')
EOF

# 6. Verificar conexión con Supabase
print_info "Verificando conexión con Supabase..."
docker exec -i residuos_backend python manage.py shell << EOF
from apps.authentication.supabase_service import supabase_service
result = supabase_service.test_connection()
if result['success']:
    print('✅ Conexión con Supabase exitosa')
else:
    print(f'❌ Error conectando con Supabase: {result["message"]}')
EOF

# 7. Instalar dependencias para pruebas BDD
print_info "Instalando dependencias para pruebas BDD..."
docker exec -i residuos_backend pip install -r requirements.test.txt

# 8. Ejecutar pruebas BDD con Cucumber/Behave
print_info "Ejecutando pruebas BDD con metodología Cucumber..."
echo ""
echo "🧪 INICIANDO PRUEBAS DE COMPORTAMIENTO (BDD)"
echo "============================================="

# Ejecutar pruebas de integración con Supabase
print_info "Probando integración con Supabase..."
docker exec -i residuos_backend python manage.py behave features/supabase_integration.feature --format=pretty

# Ejecutar pruebas de autenticación
print_info "Probando sistema de autenticación..."
docker exec -i residuos_backend python manage.py behave features/authentication.feature --format=pretty

# 9. Ejecutar pruebas unitarias existentes
print_info "Ejecutando pruebas unitarias del sistema..."
docker exec -i residuos_backend python manage.py test apps.authentication.tests --verbosity=2

# 10. Verificar endpoints principales
print_info "Verificando endpoints principales..."

# Health check
if curl -s http://localhost:8000/api/health/ | grep -q "healthy"; then
    print_status "Endpoint de salud funcionando"
else
    print_error "Endpoint de salud no responde"
fi

# API docs
if curl -s http://localhost:8000/api/schema/swagger-ui/ > /dev/null; then
    print_status "Documentación API disponible"
else
    print_error "Documentación API no disponible"
fi

# 11. Mostrar resumen del sistema
echo ""
print_info "📋 RESUMEN DEL SISTEMA"
echo "======================"
print_status "🌐 Frontend: http://localhost:3001"
print_status "🔧 Backend API: http://localhost:8000"
print_status "📚 Documentación API: http://localhost:8000/api/schema/swagger-ui/"
print_status "🐰 RabbitMQ Management: http://localhost:15672 (admin/admin123)"
print_status "🗄️  Base de datos: Supabase Cloud PostgreSQL"
print_status "🔐 Admin Panel: http://localhost:8000/admin/ (admin@latacunga.gob.ec/admin123)"

# 12. Mostrar logs en tiempo real (opcional)
print_info "Mostrando logs del sistema (Ctrl+C para salir)..."
echo ""
print_warning "Presiona Ctrl+C para detener el monitoreo de logs"
sleep 3
docker-compose logs -f --tail=50