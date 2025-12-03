@echo off
REM Script para completar la verificación final del sistema
REM Ejecuta: 1. Carga de datos, 2. Reinicio de servicios, 3. Pruebas de endpoints

setlocal enabledelayedexpansion

echo.
echo ==================================
echo  VERIFICACION FINAL DEL SISTEMA
echo ==================================
echo.

echo [1/4] Verificando estado de docker-compose...
docker-compose ps 2>nul
if errorlevel 1 (
    echo ERROR: Docker no está disponible
    exit /b 1
)

echo.
echo [2/4] Cargando datos de prueba...
docker-compose exec -T backend python load_sample_data.py
if errorlevel 1 (
    echo WARNING: No se pudo cargar datos de prueba (puede que backend no esté corriendo)
)

echo.
echo [3/4] Reiniciando servicios...
docker-compose restart backend frontend
if errorlevel 1 (
    echo WARNING: Error al reiniciar servicios
)

echo.
echo [4/4] Esperando que servicios estén listos (10 segundos)...
timeout /t 10 /nobreak

echo.
echo ==================================
echo  PRUEBAS DE ENDPOINTS
echo ==================================
echo.

echo Probando endpoints...
powershell -Command "
`$baseUrl = 'http://localhost:8000/api'
`$endpoints = @(
    'incidents/?limit=5',
    'tasks/?limit=5',
    'routes/?limit=5',
    'notifications/?limit=5',
    'reports/?limit=5',
    'reports/statistics/'
)

foreach (`$endpoint in `$endpoints) {
    try {
        `$url = `$baseUrl + '/' + `$endpoint
        `$response = Invoke-WebRequest -Uri `$url -Headers @{'Authorization' = 'Bearer dummy'} -TimeoutSec 5 2>nul
        `$count = (`$response.Content | ConvertFrom-Json).results.Count
        Write-Host \"✅ GET /`$endpoint -> 200 (`` + `$count + `` items)\"
    } catch {
        Write-Host \"❌ GET /`$endpoint -> Error: `$(`$_.Exception.Message)\"
    }
}
"

echo.
echo ==================================
echo  ACCESO A APLICACION
echo ==================================
echo.
echo Frontend: http://localhost:3001
echo Backend API: http://localhost:8000/api
echo Swagger Docs: http://localhost:8000/api/docs/
echo.
echo Para ver logs en tiempo real:
echo   docker-compose logs -f backend
echo   docker-compose logs -f frontend
echo.
