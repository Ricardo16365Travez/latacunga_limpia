#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Script para diagnosticar y resolver el problema de "Error al cargar datos"
    Paso 1: Reiniciar Docker Desktop
    Paso 2: Iniciar servicios
    Paso 3: Cargar datos
    Paso 4: Probar endpoints
#>

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " DIAGNOSTICO: Error al cargar datos" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[PASO 1] Verificando Docker..." -ForegroundColor Yellow
try {
    $version = docker --version
    Write-Host "✅ Docker: $version" -ForegroundColor Green
    
    $compose = docker-compose --version
    Write-Host "✅ Docker Compose: $compose" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker no está disponible: $_" -ForegroundColor Red
    Write-Host "Por favor, inicia Docker Desktop" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "[PASO 2] Limpiando problemas de conexión..." -ForegroundColor Yellow
Write-Host "Deteniendo contenedores..." -ForegroundColor Gray
docker-compose down 2>$null | Out-Null
Start-Sleep -Seconds 2

Write-Host ""
Write-Host "[PASO 3] Iniciando servicios..." -ForegroundColor Yellow
Write-Host "Esto puede tomar 30-60 segundos..." -ForegroundColor Gray
docker-compose up -d
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Error al iniciar servicios" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[PASO 4] Esperando que servicios estén listos..." -ForegroundColor Yellow
Write-Host "Esperando 20 segundos..." -ForegroundColor Gray
Start-Sleep -Seconds 20

Write-Host ""
Write-Host "[PASO 5] Verificando estado de contenedores..." -ForegroundColor Yellow
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>$null

Write-Host ""
Write-Host "[PASO 6] Probando endpoints..." -ForegroundColor Yellow

$endpoints = @{
    "Incidencias" = "http://localhost:8000/api/incidents/?limit=1"
    "Tareas" = "http://localhost:8000/api/tasks/?limit=1"
    "Rutas" = "http://localhost:8000/api/routes/?limit=1"
    "Notificaciones" = "http://localhost:8000/api/notifications/?limit=1"
    "Reportes/Estadísticas" = "http://localhost:8000/api/reports/statistics/"
}

foreach ($name in $endpoints.Keys) {
    $url = $endpoints[$name]
    try {
        $response = Invoke-WebRequest -Uri $url -TimeoutSec 5 -ErrorAction Stop
        $statusCode = $response.StatusCode
        Write-Host "  ✅ $name : $statusCode" -ForegroundColor Green
    } catch {
        $status = $_.Exception.Response.StatusCode.Value__
        if ($status -eq 401) {
            Write-Host "  ⚠️  $name : 401 (Se necesita autenticación - normal)" -ForegroundColor Yellow
        } elseif ($status -eq 403) {
            Write-Host "  ⚠️  $name : 403 (Acceso prohibido)" -ForegroundColor Yellow
        } else {
            Write-Host "  ❌ $name : Error $status - $_" -ForegroundColor Red
        }
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " ACCESO A APLICACION" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Frontend: http://localhost:3001" -ForegroundColor Cyan
Write-Host "Backend:  http://localhost:8000/api" -ForegroundColor Cyan
Write-Host "Docs:     http://localhost:8000/api/docs/" -ForegroundColor Cyan
Write-Host ""

Write-Host "Si sigue habiendo errores en el frontend:" -ForegroundColor Yellow
Write-Host "  1. Abre http://localhost:3001 en el navegador" -ForegroundColor Gray
Write-Host "  2. Abre las herramientas de desarrollador (F12)" -ForegroundColor Gray
Write-Host "  3. Ve a la pestaña 'Console' para ver errores exactos" -ForegroundColor Gray
Write-Host "  4. Ve a la pestaña 'Network' y observa las llamadas HTTP" -ForegroundColor Gray
Write-Host "  5. Copia los errores y comparte conmigo" -ForegroundColor Gray
Write-Host ""

Write-Host "Para ver logs del backend:" -ForegroundColor Yellow
Write-Host "  docker-compose logs -f backend" -ForegroundColor Gray
Write-Host ""
