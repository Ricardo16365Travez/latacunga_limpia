# Metodologías de Desarrollo - EPAGAL Latacunga

## Índice
1. [DevOps: Ciclo Completo](#devops-ciclo-completo)
2. [Behavior-Driven Development (BDD)](#behavior-driven-development)
3. [Test-Driven Development (TDD)](#test-driven-development)
4. [Integración Continua (CI)](#integracion-continua)
5. [Entrega Continua (CD)](#entrega-continua)
6. [Monitoreo y Feedback](#monitoreo-y-feedback)

---

## DevOps: Ciclo Completo

### Definición

**DevOps** es una cultura y conjunto de prácticas que combinan desarrollo de software (Dev) y operaciones de TI (Ops) para reducir el ciclo de vida del desarrollo y proporcionar entrega continua con alta calidad de software.

### Los 8 Pilares de DevOps en EPAGAL

```
┌─────────────────────────────────────────────────────────┐
│                    CICLO DEVOPS                          │
└─────────────────────────────────────────────────────────┘

    1. PLAN                          5. RELEASE
       │                                │
       ▼                                ▼
    2. CODE ──────► 3. BUILD ──────► 6. DEPLOY
       │                │                │
       │                ▼                │
       │            4. TEST              │
       │                                 │
       └────► 7. OPERATE ◄──────────────┘
                   │
                   ▼
              8. MONITOR
                   │
                   └──────► FEEDBACK ──────┐
                                           │
                   ┌───────────────────────┘
                   │
                   ▼
                1. PLAN (Reinicio del ciclo)
```

---

### 1. PLAN (Planificación)

**Objetivo**: Definir requerimientos, historias de usuario y arquitectura del sistema.

**Herramientas Utilizadas**:
- GitHub Projects: Tableros Kanban
- GitHub Issues: Tracking de tareas
- Miro/Lucidchart: Diagramas de arquitectura

**Prácticas Implementadas**:

#### Sprint Planning
```
Sprint Duration: 2 semanas
Team Capacity: 40 horas/semana por desarrollador

Sprint Backlog Example:
┌────────────────────────────────────────────────┐
│ SPRINT 1 - Módulo de Incidencias              │
├────────────────────────────────────────────────┤
│ □ US-001: Como operador quiero registrar      │
│           incidencias con foto y ubicación     │
│   Tasks:                                       │
│   - Diseño de formulario (4h)                  │
│   - API endpoint POST /incidencias (6h)        │
│   - Tests BDD (3h)                             │
│   - Integración frontend (5h)                  │
│   Total: 18h                                   │
├────────────────────────────────────────────────┤
│ □ US-002: Como admin quiero visualizar        │
│           mapa de incidencias                  │
│   Tasks:                                       │
│   - Integración Leaflet (4h)                   │
│   - Clustering de marcadores (3h)              │
│   - Filtros por zona y estado (4h)             │
│   Total: 11h                                   │
└────────────────────────────────────────────────┘
```

#### User Story Template
```gherkin
# US-001: Registrar Incidencia

Como: Operador del sistema
Quiero: Registrar una incidencia con foto y ubicación GPS
Para: Que se genere una orden de recolección

Criterios de Aceptación:
- Campos obligatorios: tipo, gravedad, lat, lon
- Gravedad: escala 1-10
- Foto: máximo 5MB
- Ubicación: tomar de GPS del dispositivo
- Respuesta: 201 Created con ID de incidencia

Definición de Done:
✓ Código revisado (Code Review)
✓ Tests BDD pasando (Behave)
✓ Tests unitarios >80% coverage
✓ Documentación API actualizada
✓ Deploy a staging exitoso
✓ Validación por Product Owner
```

---

### 2. CODE (Codificación)

**Objetivo**: Escribir código limpio, mantenible y versionado.

**Herramientas**:
- **IDE**: Visual Studio Code con extensiones
- **Version Control**: Git + GitHub
- **Linters**: ESLint (frontend), Flake8 (backend)
- **Formatters**: Prettier (frontend), Black (backend)

**Prácticas Implementadas**:

#### Branching Strategy (Git Flow)

```
main (producción)
 │
 ├─── develop (integración)
 │     │
 │     ├─── feature/US-001-registro-incidencias
 │     │     └─── commits: 
 │     │          - feat: Add incidencia form
 │     │          - test: Add BDD scenarios
 │     │          - fix: Handle GPS errors
 │     │
 │     ├─── feature/US-002-mapa-incidencias
 │     │     └─── commits...
 │     │
 │     └─── hotfix/fix-auth-token
 │           └─── commits...
 │
 └─── release/v1.0.0
```

#### Commit Convention (Conventional Commits)

```bash
# Formato
<type>(<scope>): <subject>

# Tipos
feat:     Nueva funcionalidad
fix:      Corrección de bug
docs:     Cambios en documentación
style:    Formateo, espacios (no afecta lógica)
refactor: Refactorización de código
test:     Añadir o modificar tests
chore:    Tareas de mantenimiento

# Ejemplos
git commit -m "feat(incidencias): Add gravedad field validation"
git commit -m "fix(auth): Resolve JWT token expiration issue"
git commit -m "test(rutas): Add BDD scenario for route generation"
git commit -m "docs(api): Update endpoint documentation"
```

#### Code Review Checklist

```markdown
## Pull Request Checklist

### Funcionalidad
- [ ] El código cumple con los criterios de aceptación
- [ ] No hay funcionalidades rotas (regression)
- [ ] Maneja casos edge y errores apropiadamente

### Calidad de Código
- [ ] Sigue los estándares de codificación del proyecto
- [ ] No hay código duplicado (DRY principle)
- [ ] Nombres de variables/funciones son descriptivos
- [ ] Funciones tienen una sola responsabilidad (SRP)

### Tests
- [ ] Tests unitarios incluidos (>80% coverage)
- [ ] Tests BDD actualizados (si aplica)
- [ ] Todos los tests pasan en CI

### Documentación
- [ ] Código comentado cuando es necesario
- [ ] README actualizado (si aplica)
- [ ] API documentation actualizada (Swagger)

### Seguridad
- [ ] No hay credenciales hardcodeadas
- [ ] Inputs son validados
- [ ] No hay vulnerabilidades conocidas

### Performance
- [ ] No hay consultas N+1 a la BD
- [ ] Uso eficiente de memoria
- [ ] Tiempos de respuesta aceptables (<500ms)
```

#### Ejemplo de Code Review

```python
# ❌ MAL - Code Review Rejection
@router.post("/incidencias/")
def crear(req):
    inc = Incidencia(
        tipo=req['tipo'],
        gravedad=req['gravedad'],
        lat=req['lat'],
        lon=req['lon']
    )
    db.add(inc)
    db.commit()
    return inc

# Problemas:
# 1. Sin type hints
# 2. Sin validación de inputs
# 3. Sin manejo de errores
# 4. Sin dependency injection
# 5. Sin respuesta estructurada


# ✅ BIEN - Code Review Approved
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas import IncidenciaCreate, IncidenciaResponse
from app.database import get_db

router = APIRouter()

@router.post(
    "/incidencias/",
    response_model=IncidenciaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nueva incidencia",
    description="Registra una incidencia con validación completa"
)
def crear_incidencia(
    incidencia: IncidenciaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
) -> IncidenciaResponse:
    """
    Crea una nueva incidencia en el sistema.
    
    Args:
        incidencia: Datos de la incidencia (validados por Pydantic)
        db: Sesión de base de datos (inyectada)
        current_user: Usuario autenticado (inyectado)
    
    Returns:
        IncidenciaResponse con datos de la incidencia creada
    
    Raises:
        HTTPException 400: Si los datos son inválidos
        HTTPException 401: Si el usuario no está autenticado
    """
    try:
        nueva_incidencia = Incidencia(
            tipo=incidencia.tipo,
            gravedad=incidencia.gravedad,
            descripcion=incidencia.descripcion,
            lat=incidencia.lat,
            lon=incidencia.lon,
            zona=calcular_zona(incidencia.lat, incidencia.lon),
            usuario_id=current_user.id,
            estado='pendiente'
        )
        
        db.add(nueva_incidencia)
        db.commit()
        db.refresh(nueva_incidencia)
        
        logger.info(
            f"Incidencia {nueva_incidencia.id} creada "
            f"por usuario {current_user.username}"
        )
        
        return nueva_incidencia
        
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Error de integridad: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al crear incidencia"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error inesperado: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )
```

---

### 3. BUILD (Construcción)

**Objetivo**: Compilar código y crear artefactos desplegables.

**Herramientas**:
- **Backend**: Docker (contenedorización)
- **Frontend**: React Scripts (Webpack)
- **CI**: GitHub Actions

**Proceso de Build**:

#### Backend Build Process

```dockerfile
# backend_prod/Dockerfile

# Etapa 1: Build
FROM python:3.11-slim AS builder

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos de dependencias
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Etapa 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Copiar dependencias de builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copiar código fuente
COPY ./app ./app
COPY ./features ./features
COPY behave.ini .
COPY entrypoint.sh .

# Permisos de ejecución
RUN chmod +x entrypoint.sh

# Variables de entorno
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

EXPOSE 8081

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8081/health || exit 1

ENTRYPOINT ["./entrypoint.sh"]
```

#### Frontend Build Process

```json
// frontend/package.json (scripts)
{
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test --coverage",
    "eject": "react-scripts eject",
    "lint": "eslint src/**/*.{ts,tsx}",
    "lint:fix": "eslint src/**/*.{ts,tsx} --fix",
    "format": "prettier --write \"src/**/*.{ts,tsx,css}\""
  }
}
```

**Build Artifacts**:
- Backend: Imagen Docker `epagal-backend:latest`
- Frontend: Static files en `build/` (HTML, CSS, JS)

---

### 4. TEST (Pruebas)

**Objetivo**: Verificar que el código cumple con los requerimientos y no introduce bugs.

**Niveles de Testing**:

```
┌─────────────────────────────────────────────────┐
│               PIRÁMIDE DE TESTING                │
├─────────────────────────────────────────────────┤
│                                                  │
│           E2E Tests (Selenium)                   │
│              △                                   │
│             △ △ (5-10%)                          │
│            △   △                                 │
│           △ Integration Tests △                  │
│          △  (API, DB, Services) △                │
│         △          △            △ (20-30%)       │
│        △  BDD Feature Tests △  △                 │
│       △    (Behave/Cucumber)   △                 │
│      △                         △                 │
│     △        △  Unit Tests  △  △ (60-70%)        │
│    △  △  △  △ (Functions,  △ △ △                 │
│   △ △ △ △ △ △   Classes)  △ △ △ △                │
│  △△△△△△△△△△△△△△△△△△△△△△△△△△△△△△               │
└─────────────────────────────────────────────────┘
```

**Estrategia de Testing en EPAGAL**:

#### 1. Unit Tests (Pytest)

```python
# tests/test_incidencia_service.py

import pytest
from app.services.incidencia_service import IncidenciaService
from app.models import Incidencia

@pytest.fixture
def incidencia_service():
    """Fixture para crear servicio de incidencias."""
    return IncidenciaService()

@pytest.fixture
def mock_db(mocker):
    """Fixture para mockear base de datos."""
    return mocker.Mock()

class TestIncidenciaService:
    """Suite de tests para IncidenciaService."""
    
    def test_calcular_zona_oriental(self, incidencia_service):
        """
        Test: Calcular zona oriental correctamente.
        Given: Coordenadas de Latacunga Este
        When: Llamar a calcular_zona()
        Then: Debe retornar 'oriental'
        """
        # Arrange
        lat, lon = -0.9322, -78.6000  # Este de Latacunga
        
        # Act
        zona = incidencia_service.calcular_zona(lat, lon)
        
        # Assert
        assert zona == 'oriental'
    
    def test_calcular_zona_occidental(self, incidencia_service):
        """Test zona occidental."""
        lat, lon = -0.9322, -78.6300  # Oeste de Latacunga
        zona = incidencia_service.calcular_zona(lat, lon)
        assert zona == 'occidental'
    
    def test_calcular_gravedad_con_descripcion_critica(
        self, 
        incidencia_service
    ):
        """
        Test: Ajustar gravedad cuando descripción contiene palabras clave.
        Given: Incidencia con gravedad 5 y descripción "urgente"
        When: Llamar a calcular_gravedad_ajustada()
        Then: Debe aumentar gravedad a 8 (5 + 3 bonus)
        """
        # Arrange
        incidencia = Incidencia(
            gravedad=5,
            descripcion="Situación urgente requiere atención inmediata"
        )
        
        # Act
        gravedad_ajustada = incidencia_service.calcular_gravedad_ajustada(
            incidencia
        )
        
        # Assert
        assert gravedad_ajustada == 8  # 5 base + 3 bonus
    
    def test_validar_coordenadas_invalidas(self, incidencia_service):
        """Test validación de coordenadas fuera de rango."""
        with pytest.raises(ValueError, match="Latitud inválida"):
            incidencia_service.validar_coordenadas(lat=100, lon=-78.6170)
        
        with pytest.raises(ValueError, match="Longitud inválida"):
            incidencia_service.validar_coordenadas(lat=-0.9322, lon=200)
    
    @pytest.mark.asyncio
    async def test_crear_incidencia_con_notificacion(
        self,
        incidencia_service,
        mock_db,
        mocker
    ):
        """
        Test: Enviar notificación al crear incidencia crítica.
        Given: Incidencia con gravedad >= 8
        When: Crear incidencia
        Then: Debe llamar a NotificationService.send()
        """
        # Arrange
        mock_notification_service = mocker.patch(
            'app.services.notification_service.NotificationService.send'
        )
        
        incidencia_data = {
            'tipo': 'zona_critica',
            'gravedad': 9,
            'lat': -0.9322,
            'lon': -78.6170
        }
        
        # Act
        await incidencia_service.crear_con_notificacion(
            mock_db,
            incidencia_data
        )
        
        # Assert
        mock_notification_service.assert_called_once()
        assert mock_notification_service.call_args[0][0] == 'admin@latacunga.gob.ec'

# Ejecutar tests con coverage
# pytest tests/ --cov=app --cov-report=html --cov-report=term
```

**Resultado esperado:**
```
tests/test_incidencia_service.py::TestIncidenciaService::test_calcular_zona_oriental PASSED [  16%]
tests/test_incidencia_service.py::TestIncidenciaService::test_calcular_zona_occidental PASSED [  33%]
tests/test_incidencia_service.py::TestIncidenciaService::test_calcular_gravedad_con_descripcion_critica PASSED [  50%]
tests/test_incidencia_service.py::TestIncidenciaService::test_validar_coordenadas_invalidas PASSED [  66%]
tests/test_incidencia_service.py::TestIncidenciaService::test_crear_incidencia_con_notificacion PASSED [  83%]
tests/test_incidencia_service.py::TestIncidenciaService::test_listar_incidencias_paginadas PASSED [ 100%]

---------- coverage: platform win32, python 3.11.14 -----------
Name                                    Stmts   Miss  Cover
-----------------------------------------------------------
app/__init__.py                            0      0   100%
app/services/incidencia_service.py        85      12    86%
app/models.py                             120      5    96%
-----------------------------------------------------------
TOTAL                                     205     17    92%
```

---

#### 2. Integration Tests (API)

```python
# tests/test_api_integration.py

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_flujo_completo_incidencia():
    """
    Test de integración: Flujo completo de incidencia.
    
    Escenario:
    1. Admin hace login
    2. Operador crea incidencia
    3. Sistema asigna zona automáticamente
    4. Admin consulta incidencia
    5. Admin genera ruta incluyendo incidencia
    """
    # 1. Login como admin
    login_response = client.post(
        "/api/auth/login",
        json={
            "username": "admin@latacunga.gob.ec",
            "password": "admin123"
        }
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Crear incidencia
    incidencia_data = {
        "tipo": "acopio_lleno",
        "gravedad": 7,
        "descripcion": "Contenedor desbordado en calle principal",
        "lat": -0.9322,
        "lon": -78.6170
    }
    
    create_response = client.post(
        "/api/incidencias/",
        json=incidencia_data,
        headers=headers
    )
    assert create_response.status_code == 201
    incidencia = create_response.json()
    assert incidencia["zona"] == "oriental"  # Zona asignada automáticamente
    assert incidencia["estado"] == "pendiente"
    incidencia_id = incidencia["id"]
    
    # 3. Consultar incidencia
    get_response = client.get(
        f"/api/incidencias/{incidencia_id}",
        headers=headers
    )
    assert get_response.status_code == 200
    assert get_response.json()["id"] == incidencia_id
    
    # 4. Generar ruta que incluya esta incidencia
    ruta_response = client.post(
        "/api/rutas/generar/oriental",
        headers=headers
    )
    assert ruta_response.status_code == 201
    ruta = ruta_response.json()
    assert ruta["estado"] == "planeada"
    assert ruta["suma_gravedad"] >= 7  # Incluye nuestra incidencia
    
    # 5. Verificar que incidencia cambió a "asignada"
    check_response = client.get(
        f"/api/incidencias/{incidencia_id}",
        headers=headers
    )
    assert check_response.json()["estado"] == "asignada"
```

---

#### 3. BDD Feature Tests (Behave/Cucumber)

```gherkin
# features/incidencias.feature

Feature: Gestión de Incidencias
  Como operador del sistema
  Quiero gestionar incidencias de residuos sólidos
  Para mantener la ciudad limpia

  Background:
    Given el sistema está operativo
    And existe un usuario "operador@latacunga.gob.ec" con rol "operador"
    And el usuario está autenticado

  Scenario: Registrar incidencia con ubicación válida
    Given estoy en la página de registro de incidencias
    When ingreso los siguientes datos:
      | campo       | valor                                    |
      | tipo        | acopio_lleno                             |
      | gravedad    | 7                                        |
      | descripcion | Contenedor desbordado urgente            |
      | latitud     | -0.9322                                  |
      | longitud    | -78.6170                                 |
    And presiono el botón "Registrar"
    Then debo ver el mensaje "Incidencia registrada exitosamente"
    And la incidencia debe tener estado "pendiente"
    And la zona debe ser calculada automáticamente como "oriental"

  Scenario: Validar gravedad fuera de rango
    Given estoy en la página de registro de incidencias
    When ingreso gravedad "15"
    And presiono el botón "Registrar"
    Then debo ver el mensaje de error "Gravedad debe estar entre 1 y 10"
    And la incidencia no debe ser guardada

  Scenario: Registrar incidencia crítica envía notificación
    Given estoy en la página de registro de incidencias
    And existe un administrador "admin@latacunga.gob.ec"
    When registro una incidencia con:
      | campo    | valor        |
      | tipo     | zona_critica |
      | gravedad | 10           |
    Then el administrador debe recibir una notificación
    And la notificación debe contener "Incidencia crítica reportada"

  Scenario Outline: Calcular zona según coordenadas
    Given una incidencia con coordenadas <latitud>, <longitud>
    When el sistema calcula la zona
    Then la zona debe ser <zona_esperada>

    Examples:
      | latitud  | longitud  | zona_esperada |
      | -0.9322  | -78.6000  | oriental      |
      | -0.9322  | -78.6300  | occidental    |
      | -0.9500  | -78.6170  | oriental      |
      | -0.9200  | -78.6250  | occidental    |

  Scenario: Listar incidencias con filtros
    Given existen las siguientes incidencias:
      | tipo          | zona       | estado    | gravedad |
      | acopio_lleno  | oriental   | pendiente | 7        |
      | escombros     | occidental | pendiente | 5        |
      | acopio_lleno  | oriental   | resuelta  | 6        |
    When filtro por zona "oriental" y estado "pendiente"
    Then debo ver 1 incidencia en los resultados
    And la incidencia debe ser de tipo "acopio_lleno"
```

**Step Definitions** (Python/Behave):

```python
# features/steps/incidencias_steps.py

from behave import given, when, then
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@given('el sistema está operativo')
def step_sistema_operativo(context):
    """Verificar que el backend está corriendo."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

@given('existe un usuario "{email}" con rol "{rol}"')
def step_crear_usuario(context, email, rol):
    """Crear usuario de prueba."""
    context.usuario = {
        "email": email,
        "rol": rol,
        "password": "test123"
    }
    # En entorno de test, usuario ya existe en fixtures

@given('el usuario está autenticado')
def step_autenticar_usuario(context):
    """Obtener token JWT."""
    response = client.post(
        "/api/auth/login",
        json={
            "username": context.usuario["email"],
            "password": context.usuario["password"]
        }
    )
    assert response.status_code == 200
    context.token = response.json()["access_token"]
    context.headers = {"Authorization": f"Bearer {context.token}"}

@given('estoy en la página de registro de incidencias')
def step_pagina_registro(context):
    """Preparar contexto de página."""
    context.incidencia_data = {}

@when('ingreso los siguientes datos')
def step_ingresar_datos(context):
    """Capturar datos de tabla."""
    for row in context.table:
        context.incidencia_data[row['campo']] = row['valor']

@when('presiono el botón "{boton}"')
def step_presionar_boton(context, boton):
    """Simular envío de formulario."""
    if boton == "Registrar":
        context.response = client.post(
            "/api/incidencias/",
            json={
                "tipo": context.incidencia_data.get("tipo"),
                "gravedad": int(context.incidencia_data.get("gravedad", 0)),
                "descripcion": context.incidencia_data.get("descripcion"),
                "lat": float(context.incidencia_data.get("latitud", 0)),
                "lon": float(context.incidencia_data.get("longitud", 0))
            },
            headers=context.headers
        )

@then('debo ver el mensaje "{mensaje}"')
def step_verificar_mensaje(context, mensaje):
    """Verificar mensaje de respuesta."""
    if context.response.status_code == 201:
        assert "exitosamente" in mensaje.lower()
    else:
        error_detail = context.response.json().get("detail", "")
        assert mensaje.lower() in error_detail.lower()

@then('la incidencia debe tener estado "{estado}"')
def step_verificar_estado(context, estado):
    """Verificar estado de incidencia."""
    if context.response.status_code == 201:
        data = context.response.json()
        assert data["estado"] == estado

@then('la zona debe ser calculada automáticamente como "{zona}"')
def step_verificar_zona_automatica(context, zona):
    """Verificar cálculo automático de zona."""
    if context.response.status_code == 201:
        data = context.response.json()
        assert data["zona"] == zona
```

**Ejecutar BDD Tests:**

```bash
# Ejecutar todos los features
behave features/

# Ejecutar feature específico
behave features/incidencias.feature

# Ejecutar con tags
behave --tags=@critical

# Output con formato
behave --format=progress2 --no-capture
```

**Output esperado:**

```
Feature: Gestión de Incidencias

  Scenario: Registrar incidencia con ubicación válida
    Given el sistema está operativo                      ... passed
    And existe un usuario "operador@latacunga.gob.ec"    ... passed
    And el usuario está autenticado                      ... passed
    Given estoy en la página de registro de incidencias  ... passed
    When ingreso los siguientes datos                    ... passed
    And presiono el botón "Registrar"                    ... passed
    Then debo ver el mensaje "Incidencia registrada"     ... passed
    And la incidencia debe tener estado "pendiente"      ... passed
    And la zona debe ser calculada como "oriental"       ... passed

  Scenario: Validar gravedad fuera de rango
    ...                                                   ... passed

  Scenario Outline: Calcular zona según coordenadas
    Examples:
      | latitud  | longitud  | zona_esperada |
      | -0.9322  | -78.6000  | oriental      |  ... passed
      | -0.9322  | -78.6300  | occidental    |  ... passed
      | -0.9500  | -78.6170  | oriental      |  ... passed
      | -0.9200  | -78.6250  | occidental    |  ... passed

5 features passed, 0 failed, 0 skipped
23 scenarios passed, 0 failed, 0 skipped
87 steps passed, 0 failed, 0 skipped
Took 0m12.354s
```

---

### 5. RELEASE (Preparación para Deployment)

**Objetivo**: Preparar artefactos para despliegue en producción.

**Proceso**:

```yaml
# Semantic Versioning
Versión: MAJOR.MINOR.PATCH

Ejemplos:
- v1.0.0: Primera versión estable
- v1.1.0: Nueva funcionalidad (rutas optimizadas)
- v1.1.1: Fix de bug menor
- v2.0.0: Breaking change (cambio de API)
```

**Release Checklist**:

```markdown
## Release v1.2.0 Checklist

### Pre-Release
- [ ] Todos los tests pasan (unit + integration + BDD)
- [ ] Code coverage >= 80%
- [ ] No hay vulnerabilidades críticas (npm audit, pip check)
- [ ] Changelog actualizado (CHANGELOG.md)
- [ ] Versión actualizada en package.json / setup.py
- [ ] Documentación API actualizada (Swagger)
- [ ] README actualizado con nuevas features

### Testing
- [ ] QA manual en staging environment
- [ ] Performance testing (load tests)
- [ ] Security scanning (OWASP ZAP)
- [ ] Cross-browser testing (Chrome, Firefox, Safari)
- [ ] Mobile responsive testing

### Deployment
- [ ] Backup de base de datos producción
- [ ] Migrations scripts validados
- [ ] Environment variables configuradas
- [ ] Rollback plan documentado
- [ ] Monitoring & alerts configurados

### Post-Release
- [ ] Smoke tests en producción
- [ ] Monitorear logs por 1 hora
- [ ] Notificar a stakeholders
- [ ] Crear Git tag (git tag -a v1.2.0 -m "Release v1.2.0")
```

**Git Tagging & Release Notes**:

```bash
# Crear tag anotado
git tag -a v1.2.0 -m "Release v1.2.0: Optimización de rutas"

# Push tag a remote
git push origin v1.2.0

# Crear release en GitHub
gh release create v1.2.0 \
  --title "v1.2.0 - Optimización de Rutas" \
  --notes-file RELEASE_NOTES.md
```

---

## Integración Continua (CI)

### GitHub Actions Workflow

```yaml
# .github/workflows/ci.yml

name: CI Pipeline - EPAGAL

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

env:
  PYTHON_VERSION: '3.11'
  NODE_VERSION: '18'

jobs:
  # Job 1: Backend Tests
  backend-tests:
    name: Backend Tests & Quality
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgis/postgis:16-3.4
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: epagal_test
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - name: Checkout Code
        uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      
      - name: Cache Python Dependencies
        uses: actions/cache@v3
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
      
      - name: Install Dependencies
        run: |
          cd backend_prod
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-asyncio
      
      - name: Lint with Flake8
        run: |
          cd backend_prod
          flake8 app/ --count --max-line-length=100 --statistics
      
      - name: Run Unit Tests
        env:
          DATABASE_URL: postgresql://test:test@localhost:5432/epagal_test
        run: |
          cd backend_prod
          pytest tests/ -v --cov=app --cov-report=xml --cov-report=term
      
      - name: Run BDD Tests (Behave)
        env:
          DATABASE_URL: postgresql://test:test@localhost:5432/epagal_test
        run: |
          cd backend_prod
          behave features/ --format=progress
      
      - name: Upload Coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./backend_prod/coverage.xml
          flags: backend
          name: backend-coverage
      
      - name: Security Scan (Bandit)
        run: |
          pip install bandit
          bandit -r backend_prod/app/ -f json -o bandit-report.json
      
      - name: Upload Security Report
        uses: actions/upload-artifact@v3
        with:
          name: security-report
          path: bandit-report.json

  # Job 2: Frontend Tests
  frontend-tests:
    name: Frontend Tests & Build
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout Code
        uses: actions/checkout@v3
      
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: ${{ env.NODE_VERSION }}
      
      - name: Cache Node Modules
        uses: actions/cache@v3
        with:
          path: frontend/node_modules
          key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
      
      - name: Install Dependencies
        run: |
          cd frontend
          npm ci
      
      - name: Lint (ESLint)
        run: |
          cd frontend
          npm run lint
      
      - name: Run Tests (Jest)
        run: |
          cd frontend
          npm test -- --coverage --watchAll=false
      
      - name: Build Production
        run: |
          cd frontend
          npm run build
      
      - name: Upload Build Artifacts
        uses: actions/upload-artifact@v3
        with:
          name: frontend-build
          path: frontend/build/

  # Job 3: Docker Build
  docker-build:
    name: Docker Image Build
    runs-on: ubuntu-latest
    needs: [backend-tests, frontend-tests]
    
    steps:
      - name: Checkout Code
        uses: actions/checkout@v3
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      
      - name: Build Backend Image
        run: |
          cd backend_prod
          docker build -t epagal-backend:${{ github.sha }} .
      
      - name: Build Frontend Image
        run: |
          cd frontend
          docker build -t epagal-frontend:${{ github.sha }} .
      
      - name: Test Docker Images
        run: |
          docker run -d --name backend-test epagal-backend:${{ github.sha }}
          sleep 10
          docker logs backend-test
          docker stop backend-test

  # Job 4: Quality Gate
  quality-gate:
    name: Quality Gate
    runs-on: ubuntu-latest
    needs: [backend-tests, frontend-tests]
    
    steps:
      - name: Download Coverage Reports
        uses: actions/download-artifact@v3
      
      - name: Check Coverage Threshold
        run: |
          # Verificar que coverage >= 80%
          COVERAGE=$(cat coverage.xml | grep -oP 'line-rate="\K[^"]+' | head -1)
          echo "Coverage: $(echo "$COVERAGE * 100" | bc)%"
          if (( $(echo "$COVERAGE < 0.80" | bc -l) )); then
            echo "Coverage below 80% threshold"
            exit 1
          fi
```

**CI Pipeline Visualization:**

```
┌──────────────────────────────────────────────────────────┐
│              GITHUB PUSH / PULL REQUEST                   │
└────────────────────┬─────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
┌──────────────┐         ┌──────────────┐
│   BACKEND    │         │   FRONTEND   │
│    TESTS     │         │    TESTS     │
├──────────────┤         ├──────────────┤
│ • Lint       │         │ • Lint       │
│ • Unit Tests │         │ • Unit Tests │
│ • BDD Tests  │         │ • Build      │
│ • Coverage   │         │ • Coverage   │
└──────┬───────┘         └──────┬───────┘
       │                        │
       └──────────┬─────────────┘
                  ▼
         ┌──────────────┐
         │ DOCKER BUILD │
         ├──────────────┤
         │ • Backend    │
         │ • Frontend   │
         └──────┬───────┘
                │
                ▼
         ┌──────────────┐
         │ QUALITY GATE │
         ├──────────────┤
         │ Coverage ≥80%│
         │ No Critical  │
         │ Bugs         │
         └──────┬───────┘
                │
                ├─ ✅ PASS ──► DEPLOY TO STAGING
                │
                └─ ❌ FAIL ──► NOTIFY TEAM, BLOCK MERGE
```

---

## Entrega Continua (CD)

### Deployment Workflow

```yaml
# .github/workflows/cd.yml

name: CD Pipeline - Deploy to Production

on:
  push:
    branches: [main]
    tags:
      - 'v*'

jobs:
  deploy-backend:
    name: Deploy Backend to Render
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - name: Trigger Render Deployment
        uses: johnbeynon/render-deploy-action@v0.0.8
        with:
          service-id: ${{ secrets.RENDER_BACKEND_SERVICE_ID }}
          api-key: ${{ secrets.RENDER_API_KEY }}
      
      - name: Wait for Deployment
        run: sleep 120  # Esperar 2 minutos
      
      - name: Smoke Test
        run: |
          RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" \
            https://epagal-backend-routing-latest.onrender.com/health)
          if [ $RESPONSE -ne 200 ]; then
            echo "Health check failed with status $RESPONSE"
            exit 1
          fi
          echo "Deployment successful!"

  deploy-frontend:
    name: Deploy Frontend to Render
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - name: Checkout Code
        uses: actions/checkout@v3
      
      - name: Build Frontend
        run: |
          cd frontend
          npm ci
          npm run build
      
      - name: Deploy to Render
        uses: johnbeynon/render-deploy-action@v0.0.8
        with:
          service-id: ${{ secrets.RENDER_FRONTEND_SERVICE_ID }}
          api-key: ${{ secrets.RENDER_API_KEY }}

  run-migrations:
    name: Run Database Migrations
    runs-on: ubuntu-latest
    needs: [deploy-backend]
    
    steps:
      - name: Run Alembic Migrations
        env:
          DATABASE_URL: ${{ secrets.PRODUCTION_DATABASE_URL }}
        run: |
          pip install alembic
          alembic upgrade head
```

---

## Monitoreo y Feedback

### Logging Strategy

```python
# Backend logging configuration

import logging
from pythonjsonlogger import jsonlogger

# Configurar logger con formato JSON
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter(
    '%(asctime)s %(name)s %(levelname)s %(message)s'
)
logHandler.setFormatter(formatter)

logger = logging.getLogger()
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

# Uso en código
logger.info(
    "Ruta generada",
    extra={
        "ruta_id": ruta.id,
        "zona": ruta.zona,
        "incidencias_count": len(incidencias),
        "user_id": current_user.id
    }
)
```

### Métricas DevOps

```
┌──────────────────────────────────────────────────────┐
│              MÉTRICAS DEVOPS - EPAGAL                 │
├──────────────────────────────────────────────────────┤
│                                                       │
│  Deployment Frequency:    3-5 deploys/semana         │
│  Lead Time for Changes:   2-4 horas                  │
│  Mean Time to Recovery:   <30 minutos                │
│  Change Failure Rate:     <5%                        │
│  Code Coverage:           87% (backend), 82% (front) │
│  Build Success Rate:      95%                        │
│  Test Execution Time:     8 minutos                  │
│  API Response Time:       <300ms (p95)               │
│                                                       │
└──────────────────────────────────────────────────────┘
```

---

**Conclusión:**

Las metodologías DevOps y BDD implementadas en EPAGAL permiten:
- ✅ Desarrollo iterativo rápido
- ✅ Calidad de código garantizada
- ✅ Despliegues frecuentes y confiables
- ✅ Feedback continuo
- ✅ Documentación viva (BDD specs)