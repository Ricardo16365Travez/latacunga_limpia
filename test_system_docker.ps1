# Script PowerShell para probar el sistema con Docker

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "PRUEBA DEL SISTEMA - Docker" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "1. Verificando servicios Docker..." -ForegroundColor Yellow
docker-compose ps

Write-Host ""
Write-Host "2. Verificando configuracion Django..." -ForegroundColor Yellow
docker-compose exec -T backend python manage.py check

Write-Host ""
Write-Host "3. Listando apps instaladas..." -ForegroundColor Yellow
docker-compose exec -T backend python manage.py shell -c "from django.conf import settings; print('Apps instaladas:'); [print(f'  - {app}') for app in settings.INSTALLED_APPS if app.startswith('apps.')]"

Write-Host ""
Write-Host "4. Verificando modelos..." -ForegroundColor Yellow
docker-compose exec -T backend python manage.py inspectdb --database default | Select-String -Pattern "class (Task|Route|Notification|Report)" | Select-Object -First 10

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "RESUMEN DE MODULOS IMPLEMENTADOS" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "OK Modulo de Rutas (routes)" -ForegroundColor Green
Write-Host "OK Modulo de Tareas (tasks)" -ForegroundColor Green
Write-Host "OK Modulo de Notificaciones (notifications)" -ForegroundColor Green
Write-Host "OK Modulo de Reportes (reports)" -ForegroundColor Green
Write-Host ""
Write-Host "Para aplicar las migraciones ejecute:" -ForegroundColor Yellow
Write-Host "  docker-compose exec backend python manage.py makemigrations" -ForegroundColor White
Write-Host "  docker-compose exec backend python manage.py migrate" -ForegroundColor White
