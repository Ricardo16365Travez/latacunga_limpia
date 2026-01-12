# Script de prueba para los endpoints de la API

Write-Host "=== Prueba de Endpoints API ===" -ForegroundColor Green
Write-Host ""

$baseUrl = "http://localhost:8000/api"

# Test 1: Listar operadores
Write-Host "1. Listando operadores..." -ForegroundColor Cyan
try {
    $operadores = Invoke-RestMethod -Uri "$baseUrl/operadores/" -Method Get
    Write-Host "✓ Operadores obtenidos: $($operadores.Count)" -ForegroundColor Green
} catch {
    Write-Host "✗ Error: $_" -ForegroundColor Red
}

Write-Host ""

# Test 2: Crear operador
Write-Host "2. Creando operador de prueba..." -ForegroundColor Cyan
$nuevoOperador = @{
    email = "juan.perez@latacunga.gob.ec"
    username = "jperez"
    password = "password123"
    phone = "0987654321"
    display_name = "Juan Pérez"
} | ConvertTo-Json

try {
    $resultado = Invoke-RestMethod -Uri "$baseUrl/operadores/" `
        -Method Post `
        -ContentType "application/json" `
        -Body $nuevoOperador
    Write-Host "✓ Operador creado con ID: $($resultado.id)" -ForegroundColor Green
    $operadorId = $resultado.id
} catch {
    Write-Host "✗ Error al crear operador: $_" -ForegroundColor Red
}

Write-Host ""

# Test 3: Listar reportes
Write-Host "3. Listando reportes..." -ForegroundColor Cyan
try {
    $reportes = Invoke-RestMethod -Uri "$baseUrl/reportes/" -Method Get
    Write-Host "✓ Reportes obtenidos: $($reportes.Count)" -ForegroundColor Green
} catch {
    Write-Host "✗ Error: $_" -ForegroundColor Red
}

Write-Host ""

# Test 4: Crear reporte
Write-Host "4. Creando reporte de prueba..." -ForegroundColor Cyan
$nuevoReporte = @{
    description = "Acumulación de basura en la esquina de Av. Los Chasquis y Calle Hermanas Páez"
    type = "ZONA_CRITICA"
    location_lat = -0.9328
    location_lon = -78.6146
    address = "Av. Los Chasquis y Calle Hermanas Páez"
    priority_score = 8.5
} | ConvertTo-Json

try {
    $reporte = Invoke-RestMethod -Uri "$baseUrl/reportes/" `
        -Method Post `
        -ContentType "application/json" `
        -Body $nuevoReporte
    Write-Host "✓ Reporte creado con ID: $($reporte.id)" -ForegroundColor Green
    $reporteId = $reporte.id
} catch {
    Write-Host "✗ Error al crear reporte: $_" -ForegroundColor Red
}

Write-Host ""

# Test 5: Asignar operador a reporte
if ($operadorId -and $reporteId) {
    Write-Host "5. Asignando operador a reporte..." -ForegroundColor Cyan
    try {
        $asignacion = Invoke-RestMethod -Uri "$baseUrl/reportes/$reporteId/asignar-operador?operador_id=$operadorId" `
            -Method Post
        Write-Host "✓ Operador asignado exitosamente" -ForegroundColor Green
    } catch {
        Write-Host "✗ Error al asignar: $_" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "=== Prueba Completada ===" -ForegroundColor Green
Write-Host ""
Write-Host "Abre el frontend en: http://localhost:3001" -ForegroundColor Yellow
Write-Host "Ve a 'Reportes APK' para ver el reporte creado" -ForegroundColor Yellow
Write-Host "Ve a 'Operadores' para ver el operador creado" -ForegroundColor Yellow
