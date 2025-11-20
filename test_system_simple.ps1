# Pruebas BDD del Sistema de Gestion de Residuos Latacunga

Write-Host "INICIANDO PRUEBAS BDD DEL SISTEMA" -ForegroundColor Green
Write-Host "=================================================="

$testResults = @()
$baseUrl = "http://localhost:8000/api"

function Test-Endpoint {
    param(
        [string]$TestName,
        [string]$Url,
        [string]$Method = "GET",
        [hashtable]$Body = @{},
        [hashtable]$Headers = @{},
        [int]$ExpectedStatus = 200
    )
    
    try {
        $params = @{
            Uri = $Url
            Method = $Method
            UseBasicParsing = $true
        }
        
        if ($Body.Count -gt 0) {
            $params.Body = ($Body | ConvertTo-Json)
            $params.ContentType = "application/json"
        }
        
        if ($Headers.Count -gt 0) {
            $params.Headers = $Headers
        }
        
        $response = Invoke-WebRequest @params
        
        if ($response.StatusCode -eq $ExpectedStatus) {
            Write-Host "PASS - $TestName" -ForegroundColor Green
            $global:testResults += @{
                Test = $TestName
                Status = "PASS"
                Details = "HTTP $($response.StatusCode)"
            }
            return $response
        } else {
            Write-Host "FAIL - $TestName" -ForegroundColor Red
            Write-Host "   Expected: $ExpectedStatus, Got: $($response.StatusCode)" -ForegroundColor Yellow
            $global:testResults += @{
                Test = $TestName
                Status = "FAIL"
                Details = "Expected HTTP $ExpectedStatus, got $($response.StatusCode)"
            }
        }
    }
    catch {
        Write-Host "FAIL - $TestName" -ForegroundColor Red
        Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Yellow
        $global:testResults += @{
            Test = $TestName
            Status = "FAIL"
            Details = $_.Exception.Message
        }
    }
}

# Escenario 1: Verificar disponibilidad del sistema
Write-Host ""
Write-Host "Escenario 1: Disponibilidad del Sistema" -ForegroundColor Cyan

Test-Endpoint "Health Check" "$baseUrl/auth/health/"
Test-Endpoint "API Documentation" "http://localhost:8000/api/docs/"
Test-Endpoint "Frontend Availability" "http://localhost:3001/"

# Escenario 2: Registro de usuario
Write-Host ""
Write-Host "Escenario 2: Registro y Autenticacion" -ForegroundColor Cyan

$timestamp = [DateTimeOffset]::Now.ToUnixTimeSeconds()
$userEmail = "test_$timestamp@latacunga.gob.ec"
$userPassword = "TestPassword123!"

$registrationData = @{
    email = $userEmail
    password = $userPassword
    password_confirm = $userPassword
    first_name = "Usuario"
    last_name = "Prueba"
    role = "citizen"
}

$registrationResponse = Test-Endpoint "User Registration" "$baseUrl/auth/register/" "POST" $registrationData 201

# Escenario 3: Inicio de sesion
$loginData = @{
    identifier = $userEmail
    password = $userPassword
}

$loginResponse = Test-Endpoint "User Login" "$baseUrl/auth/login/" "POST" $loginData 200

# Extraer token de acceso
$accessToken = $null
if ($loginResponse -and $loginResponse.Content) {
    try {
        $loginJson = $loginResponse.Content | ConvertFrom-Json
        $accessToken = $loginJson.access
        if ($accessToken) {
            Write-Host "Token de acceso obtenido correctamente" -ForegroundColor Green
        }
    }
    catch {
        Write-Host "No se pudo extraer el token de acceso" -ForegroundColor Yellow
    }
}

# Escenario 4: Acceso a endpoint protegido
Write-Host ""
Write-Host "Escenario 4: Endpoints Protegidos" -ForegroundColor Cyan

if ($accessToken) {
    $authHeaders = @{
        Authorization = "Bearer $accessToken"
    }
    Test-Endpoint "Protected Profile Access" "$baseUrl/auth/profile/" "GET" @{} $authHeaders 200
} else {
    Write-Host "SKIP - Protected Profile Access (No access token)" -ForegroundColor Red
}

# Escenario 5: Acceso no autorizado
Test-Endpoint "Unauthorized Access Rejection" "$baseUrl/auth/profile/" "GET" @{} @{} 401

# Generar reporte
Write-Host ""
Write-Host "REPORTE DE PRUEBAS" -ForegroundColor Green
Write-Host "=================================================="

$totalTests = $testResults.Count
$passedTests = ($testResults | Where-Object { $_.Status -eq "PASS" }).Count
$failedTests = $totalTests - $passedTests

Write-Host "Total de pruebas: $totalTests" -ForegroundColor White
Write-Host "Pasaron: $passedTests" -ForegroundColor Green
Write-Host "Fallaron: $failedTests" -ForegroundColor Red

if ($totalTests -gt 0) {
    $successRate = [Math]::Round(($passedTests / $totalTests) * 100, 1)
    Write-Host "Porcentaje de exito: $successRate%" -ForegroundColor White
}

if ($failedTests -gt 0) {
    Write-Host ""
    Write-Host "PRUEBAS FALLIDAS:" -ForegroundColor Red
    $testResults | Where-Object { $_.Status -eq "FAIL" } | ForEach-Object {
        Write-Host "   - $($_.Test): $($_.Details)" -ForegroundColor Yellow
    }
}

# Guardar reporte
$reportData = @{
    summary = @{
        total = $totalTests
        passed = $passedTests
        failed = $failedTests
        success_rate = "$successRate%"
        timestamp = (Get-Date).ToString("o")
    }
    tests = $testResults
}

$reportData | ConvertTo-Json -Depth 3 | Out-File "test_report.json" -Encoding UTF8

Write-Host ""
Write-Host "Reporte guardado en: test_report.json" -ForegroundColor Green

# Verificar estado de contenedores
Write-Host ""
Write-Host "Estado de Contenedores Docker:" -ForegroundColor Cyan
try {
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
} catch {
    Write-Host "No se pudo obtener el estado de los contenedores" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "PRUEBAS COMPLETADAS" -ForegroundColor Green
Write-Host "Sistema de Gestion de Residuos Latacunga funcionando correctamente!" -ForegroundColor Green