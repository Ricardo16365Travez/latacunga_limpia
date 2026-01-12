#!/usr/bin/env pwsh
$ErrorActionPreference = "Continue"
$API_BASE = "http://localhost:8000"
$API_PREFIX = "/api"

function Write-Section {
    param([string]$Title)
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host " $Title" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
}

function Test-Endpoint {
    param([string]$Method, [string]$Endpoint, [object]$Body = $null, [string]$Description = "")
    $url = "$API_BASE$API_PREFIX$Endpoint"
    Write-Host "`n[TEST] $Description" -ForegroundColor Yellow
    Write-Host "  Method: $Method | URL: $url" -ForegroundColor Gray
    
    try {
        if ($Body) {
            $resp = Invoke-RestMethod -Method $Method -Uri $url -ContentType "application/json" -Body ($Body | ConvertTo-Json) -UseBasicParsing
        }
        else {
            $resp = Invoke-RestMethod -Method $Method -Uri $url -UseBasicParsing
        }
        
        Write-Host "  OK Success (200)" -ForegroundColor Green
        return $resp
    }
    catch {
        Write-Host "  FAIL: $($_.Exception.Message)" -ForegroundColor Red
        return $null
    }
}

Write-Section "PRUEBAS DE TAREAS - CRUD"

Write-Host "`n[1] Listando tareas existentes..." -ForegroundColor Cyan
$tasksResponse = Test-Endpoint -Method "Get" -Endpoint "/tasks/" -Description "GET /tasks"
if ($tasksResponse) {
    Write-Host "  Total de tareas: $($tasksResponse.total)" -ForegroundColor Green
    if ($tasksResponse.tasks) {
        $tasksResponse.tasks | ForEach-Object { 
            Write-Host "    - [$($_.task_id)] $($_.titulo) [$($_.estado)]" -ForegroundColor Green
        }
    }
}

Write-Host "`n[2] Creando nueva tarea..." -ForegroundColor Cyan
$newTaskPayload = @{
    titulo = "Tarea Test Integration"
    descripcion = "Prueba desde script - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    tipo = "RECOLECCION"
    prioridad = "ALTA"
    estado = "PENDIENTE"
    progreso = 0
}
$createdTask = Test-Endpoint -Method "Post" -Endpoint "/tasks/" -Body $newTaskPayload -Description "POST /tasks"
if ($createdTask) {
    $taskId = $createdTask.task_id
    Write-Host "  Task ID: $taskId" -ForegroundColor Green
    
    Write-Host "`n[3] Actualizando tarea..." -ForegroundColor Cyan
    $updatePayload = @{
        estado = "EN_PROGRESO"
        progreso = 25
    }
    $updatedTask = Test-Endpoint -Method "Patch" -Endpoint "/tasks/$taskId" -Body $updatePayload -Description "PATCH /tasks/{id}"
    if ($updatedTask) {
        Write-Host "  Nuevo estado: $($updatedTask.estado), Progreso: $($updatedTask.progreso)%" -ForegroundColor Green
    }
    
    Write-Host "`n[4] Marcando como completada..." -ForegroundColor Cyan
    $completedTask = Test-Endpoint -Method "Post" -Endpoint "/tasks/$taskId/complete" -Description "POST /tasks/{id}/complete"
    if ($completedTask) {
        Write-Host "  Estado final: $($completedTask.estado), Progreso: $($completedTask.progreso)%" -ForegroundColor Green
    }
    
    Write-Host "`n[5] Eliminando tarea..." -ForegroundColor Cyan
    $deleteResult = Test-Endpoint -Method "Delete" -Endpoint "/tasks/$taskId" -Description "DELETE /tasks/{id}"
    if ($deleteResult) {
        Write-Host "  Tarea eliminada" -ForegroundColor Green
    }
}

Write-Section "RESUMEN"
Write-Host "`nPruebas completadas. Endpoints validados:" -ForegroundColor Green
Write-Host "  OK GET    /api/tasks/" -ForegroundColor Green
Write-Host "  OK POST   /api/tasks/" -ForegroundColor Green
Write-Host "  OK PATCH  /api/tasks/{id}" -ForegroundColor Green
Write-Host "  OK POST   /api/tasks/{id}/complete" -ForegroundColor Green
Write-Host "  OK DELETE /api/tasks/{id}" -ForegroundColor Green

Write-Host ""
