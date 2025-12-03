#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Script para completar la verificación final del sistema.
    Ejecuta: 1. Carga de datos, 2. Reinicio de servicios, 3. Pruebas de endpoints
#>

Write-Host ""
Write-Host "==================================" -ForegroundColor Cyan
Write-Host " VERIFICACION FINAL DEL SISTEMA" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# [1/4] Verificar docker-compose
Write-Host "[1/4] Verificando estado de docker-compose..." -ForegroundColor Yellow
try {
    $dockerStatus = docker-compose ps 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Docker-compose está disponible" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ ERROR: Docker no está disponible" -ForegroundColor Red
    exit 1
}

# [2/4] Cargar datos de prueba
Write-Host ""
Write-Host "[2/4] Cargando datos de prueba..." -ForegroundColor Yellow
try {
    docker-compose exec -T backend python load_sample_data.py 2>nul
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Datos de prueba cargados" -ForegroundColor Green
    } else {
        Write-Host "⚠️  WARNING: No se pudo cargar datos (backend podría no estar corriendo)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  WARNING: Error cargando datos de prueba" -ForegroundColor Yellow
}

# [3/4] Reiniciar servicios
Write-Host ""
Write-Host "[3/4] Reiniciando servicios..." -ForegroundColor Yellow
docker-compose restart backend frontend
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Servicios reiniciados" -ForegroundColor Green
} else {
    Write-Host "⚠️  WARNING: Error al reiniciar servicios" -ForegroundColor Yellow
}

# [4/4] Esperar
Write-Host ""
Write-Host "[4/4] Esperando que servicios estén listos (20 segundos)..." -ForegroundColor Yellow
Start-Sleep -Seconds 20

# Pruebas de endpoints
Write-Host ""
Write-Host "==================================" -ForegroundColor Cyan
Write-Host " PRUEBAS DE ENDPOINTS" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

$baseUrl = 'http://localhost:8000/api'
$endpoints = @(
    'incidents/?limit=5',
    'tasks/?limit=5',
    'routes/?limit=5',
    'notifications/?limit=5',
    'reports/?limit=5',
    'reports/statistics/'
)

Write-Host "Probando endpoints..." -ForegroundColor Cyan
foreach ($endpoint in $endpoints) {
    try {
        $url = "$baseUrl/$endpoint"
        $response = Invoke-WebRequest -Uri $url -TimeoutSec 5 -ErrorAction Stop
        $json = $response.Content | ConvertFrom-Json
        $count = if ($json.results) { $json.results.Count } else { "N/A" }
        Write-Host "  ✅ GET /$endpoint -> 200 ($count items)" -ForegroundColor Green
    } catch {
        Write-Host "  ❌ GET /$endpoint -> Error: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Información de acceso
Write-Host ""
Write-Host "==================================" -ForegroundColor Cyan
Write-Host " ACCESO A APLICACION" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Frontend:      http://localhost:3001" -ForegroundColor Cyan
Write-Host "  Backend API:   http://localhost:8000/api" -ForegroundColor Cyan
Write-Host "  Swagger Docs:  http://localhost:8000/api/docs/" -ForegroundColor Cyan
Write-Host ""
Write-Host "Para ver logs en tiempo real:" -ForegroundColor Yellow
Write-Host "  docker-compose logs -f backend" -ForegroundColor Gray
Write-Host "  docker-compose logs -f frontend" -ForegroundColor Gray
Write-Host ""

Write-Host "✨ Verificación completada" -ForegroundColor Green
Write-Host ""
