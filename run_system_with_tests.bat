@echo off
REM Script de ejecución para sistema con Supabase y pruebas BDD (Windows)

echo 🚀 Iniciando Sistema de Gestión de Residuos Latacunga con Supabase
echo =================================================================

REM 1. Verificar dependencias
echo ℹ️  Verificando dependencias del sistema...

docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker no está instalado
    exit /b 1
) else (
    echo ✅ Docker está disponible
)

docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose no está instalado
    exit /b 1
) else (
    echo ✅ Docker Compose está disponible
)

REM 2. Limpiar contenedores existentes
echo ℹ️  Limpiando contenedores existentes...
docker-compose down --remove-orphans
docker system prune -f

REM 3. Construir e iniciar servicios
echo ℹ️  Construyendo e iniciando servicios...
docker-compose up --build -d

REM 4. Esperar a que los servicios estén listos
echo ℹ️  Esperando a que los servicios estén listos...

REM Esperar un momento para que los servicios inicien
timeout /t 30 >nul

REM 5. Ejecutar migraciones
echo ℹ️  Ejecutando migraciones de base de datos en Supabase...
docker exec residuos_backend python manage.py migrate

REM 6. Crear superusuario
echo ℹ️  Configurando usuario administrador...
docker exec residuos_backend python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(email='admin@latacunga.gob.ec').exists() or User.objects.create_superuser(email='admin@latacunga.gob.ec', password='admin123', first_name='Admin', last_name='Sistema', role='admin')"

REM 7. Instalar dependencias para pruebas
echo ℹ️  Instalando dependencias para pruebas BDD...
docker exec residuos_backend pip install -r requirements.test.txt

REM 8. Ejecutar pruebas BDD
echo 🧪 INICIANDO PRUEBAS DE COMPORTAMIENTO (BDD)
echo ============================================

echo ℹ️  Probando integración con Supabase...
docker exec residuos_backend python manage.py behave features/supabase_integration.feature --format=pretty

echo ℹ️  Probando sistema de autenticación...
docker exec residuos_backend python manage.py behave features/authentication.feature --format=pretty

REM 9. Ejecutar pruebas unitarias
echo ℹ️  Ejecutando pruebas unitarias del sistema...
docker exec residuos_backend python manage.py test apps.authentication.tests --verbosity=2

REM 10. Mostrar resumen del sistema
echo.
echo 📋 RESUMEN DEL SISTEMA
echo ======================
echo ✅ 🌐 Frontend: http://localhost:3001
echo ✅ 🔧 Backend API: http://localhost:8000
echo ✅ 📚 Documentación API: http://localhost:8000/api/schema/swagger-ui/
echo ✅ 🐰 RabbitMQ Management: http://localhost:15672 (admin/admin123)
echo ✅ 🗄️  Base de datos: Supabase Cloud PostgreSQL
echo ✅ 🔐 Admin Panel: http://localhost:8000/admin/ (admin@latacunga.gob.ec/admin123)
echo.

echo ℹ️  Sistema iniciado correctamente. Presiona Ctrl+C para ver logs...
pause

REM Mostrar logs
docker-compose logs -f --tail=50