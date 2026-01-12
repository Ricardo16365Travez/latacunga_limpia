# Sistema de Gestión de Residuos Sólidos - EPAGAL Latacunga
## Documentación Completa para Tesis

**Título:** Sistema de Optimización de Rutas para Recolección de Residuos Sólidos  
**Institución:** Universidad Técnica de Cotopaxi  
**Enfoque:** Metodologías de Desarrollo de Software con DevOps y BDD  
**Fecha:** Enero 2026

---

## Índice de Documentación

Este documento es el índice principal que referencia toda la documentación técnica del proyecto:

### 📚 Documentación Principal

1. **[ARQUITECTURA_SISTEMA.md](./ARQUITECTURA_SISTEMA.md)** - Arquitectura completa del sistema (C4, componentes, despliegue)
2. **[METODOLOGIAS_DESARROLLO.md](./METODOLOGIAS_DESARROLLO.md)** - DevOps, BDD, Cucumber, CI/CD
3. **[CICLO_VIDA_DESARROLLO.md](./CICLO_VIDA_DESARROLLO.md)** - Proceso completo de desarrollo
4. **[TECNOLOGIAS_HERRAMIENTAS.md](./TECNOLOGIAS_HERRAMIENTAS.md)** - Stack tecnológico detallado
5. **[BACKEND_TECNICO.md](./BACKEND_TECNICO.md)** - Documentación técnica del backend
6. **[FRONTEND_TECNICO.md](./FRONTEND_TECNICO.md)** - Documentación técnica del frontend
7. **[IMPLEMENTACION_FEATURES.md](./IMPLEMENTACION_FEATURES.md)** - Implementación de funcionalidades
8. **[TESTING_CALIDAD.md](./TESTING_CALIDAD.md)** - Estrategias de testing y QA
9. **[DEPLOYMENT_OPERACIONES.md](./DEPLOYMENT_OPERACIONES.md)** - Despliegue y operaciones

---

## Resumen Ejecutivo

### Contexto del Proyecto

El Sistema de Gestión de Residuos Sólidos para EPAGAL Latacunga es una plataforma web completa diseñada para optimizar la recolección de residuos sólidos en la ciudad de Latacunga, Ecuador. El sistema integra:

- **Gestión de Incidencias** - Reporte y seguimiento de puntos críticos
- **Optimización de Rutas** - Algoritmos de routing con OSRM
- **Asignación de Recursos** - Gestión de conductores y vehículos
- **Monitoreo en Tiempo Real** - Tracking GPS de unidades
- **Análisis y Reportes** - Dashboards y exportación de datos

### Enfoque Metodológico

Este proyecto implementa **metodologías modernas de desarrollo de software**:

#### 1. **DevOps** (Development + Operations)
- **CI/CD Automatizado**: GitHub Actions para build, test y deploy
- **Infraestructura como Código**: Docker, Docker Compose
- **Monitoreo Continuo**: Health checks, logging centralizado
- **Despliegue Continuo**: Render.com con auto-deploy desde main

#### 2. **BDD** (Behavior-Driven Development)
- **Cucumber + Behave**: Especificaciones ejecutables en Gherkin
- **Tests de Aceptación**: Validación de comportamiento esperado
- **Colaboración**: Lenguaje común entre stakeholders y desarrolladores

#### 3. **Arquitectura Moderna**
- **Microservicios**: Backend FastAPI modular
- **SPA**: React + TypeScript para frontend
- **API RESTful**: Comunicación estandarizada
- **Base de Datos Geoespacial**: PostgreSQL + PostGIS

---

## Stack Tecnológico Completo

### Backend
```
FastAPI 0.115.5 (Python 3.11)
├── SQLAlchemy 2.0.36 (ORM)
├── PostgreSQL 16 + PostGIS 3.4
├── Pydantic 2.10.3 (Validación)
├── Uvicorn (ASGI Server)
├── Passlib + Bcrypt (Seguridad)
├── Python-Jose (JWT)
├── OSRM (Routing externo)
└── Behave + Cucumber (BDD Testing)
```

### Frontend
```
React 18.3.1 + TypeScript 4.9.5
├── Material-UI 6.2.0 (Components)
├── React Router 7.1.1 (Routing)
├── Axios 1.7.9 (HTTP Client)
├── Recharts 2.15.0 (Visualización)
├── Leaflet 1.9.4 (Mapas)
└── React Scripts 5.0.1 (Build)
```

### DevOps & Infrastructure
```
Docker + Docker Compose
├── GitHub Actions (CI/CD)
├── Render.com (Hosting)
├── PostgreSQL Cloud (Neon)
├── GitHub Packages (Registry)
└── OSRM Project (Routing Service)
```

---

## Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND (React)                      │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │  Dashboard  │ │   Rutas     │ │ Incidencias │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTPS/REST API
┌──────────────────────┴──────────────────────────────────────┐
│                    BACKEND (FastAPI)                         │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐       │
│  │    Auth      │ │    Rutas     │ │ Incidencias  │       │
│  │   Service    │ │   Service    │ │   Service    │       │
│  └──────────────┘ └──────────────┘ └──────────────┘       │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
┌───────▼────────┐          ┌─────────▼────────┐
│   PostgreSQL   │          │   OSRM Service   │
│   + PostGIS    │          │  (Routing API)   │
└────────────────┘          └──────────────────┘
```

---

## Metodología de Desarrollo

### 1. Proceso DevOps Implementado

```
┌──────────────────────────────────────────────────────────────┐
│                    CICLO DEVOPS COMPLETO                      │
└──────────────────────────────────────────────────────────────┘

1. PLAN (Planeación)
   ├── Definición de features en Gherkin (BDD)
   ├── User stories y casos de uso
   └── Arquitectura y diseño técnico

2. CODE (Desarrollo)
   ├── Git + GitHub (Control de versiones)
   ├── Branching strategy: main + feature branches
   ├── Code review obligatorio
   └── Pair programming en features críticas

3. BUILD (Construcción)
   ├── GitHub Actions CI Pipeline
   ├── npm run build (Frontend)
   ├── Docker build (Backend)
   └── Artifact generation

4. TEST (Pruebas)
   ├── Unit Tests (pytest, jest)
   ├── Integration Tests (Behave/Cucumber)
   ├── API Tests (Postman collections)
   └── E2E Tests (Selenium - opcional)

5. RELEASE (Liberación)
   ├── Semantic versioning (v1.0.0)
   ├── Release notes automáticos
   ├── Tag creation en GitHub
   └── Changelog generation

6. DEPLOY (Despliegue)
   ├── Render.com auto-deploy
   ├── Docker containers
   ├── Environment variables management
   └── Database migrations automáticas

7. OPERATE (Operación)
   ├── Health check endpoints
   ├── Application monitoring
   ├── Performance metrics
   └── User analytics

8. MONITOR (Monitoreo)
   ├── Error tracking (logs)
   ├── Performance monitoring
   ├── Uptime monitoring (Render)
   └── Incident response
```

### 2. BDD (Behavior-Driven Development)

El proyecto utiliza **Cucumber/Behave** para escribir tests en lenguaje natural:

**Ejemplo de Feature File:**
```gherkin
# features/incidencias.feature
Feature: Gestión de Incidencias
  Como operador del sistema
  Quiero reportar y gestionar incidencias
  Para mantener un registro actualizado de problemas

  Scenario: Crear nueva incidencia
    Given el usuario está autenticado como "operador"
    When crea una incidencia con tipo "acopio_lleno"
    And establece la gravedad en 8
    And proporciona las coordenadas -0.9322, -78.6170
    Then la incidencia se crea exitosamente
    And el estado inicial es "pendiente"
    And se asigna a la zona "oriental"

  Scenario: Generar ruta automática al alcanzar umbral
    Given existen 5 incidencias pendientes en zona "occidental"
    And la suma de gravedad es 45
    When se alcanza el umbral de gravedad configurado
    Then el sistema genera automáticamente una ruta
    And asigna los vehículos necesarios
    And notifica a los conductores disponibles
```

---

## Características Principales

### 1. **Gestión de Incidencias**
- Reporte de puntos críticos con geolocalización
- Clasificación por tipo y gravedad
- Estado del ciclo de vida (pendiente → asignada → resuelta)
- Adjuntar fotografías
- Historial completo

### 2. **Optimización de Rutas**
- Algoritmo de optimización con OSRM
- Consideración de gravedad y distancia
- Asignación inteligente de vehículos
- Cálculo de duración estimada
- Visualización en mapa

### 3. **Gestión de Conductores**
- Registro y perfil de operadores
- Estado de disponibilidad
- Zona de preferencia
- Asignación de rutas
- Tracking de órdenes de trabajo

### 4. **Monitoreo en Tiempo Real**
- Tracking GPS de vehículos
- Estado de rutas en ejecución
- Notificaciones push
- Dashboard de operaciones

### 5. **Reportes y Análisis**
- Estadísticas de incidencias
- Métricas de rendimiento
- Exportación a PDF/Excel
- Gráficos y visualizaciones

---

## Flujo de Desarrollo

### 1. Feature Development Flow
```
1. Crear Feature Branch
   git checkout -b feature/nueva-funcionalidad

2. Escribir BDD Scenarios (Gherkin)
   features/nueva-funcionalidad.feature

3. Implementar Backend
   - Models (SQLAlchemy)
   - Schemas (Pydantic)
   - Services (Business Logic)
   - Routers (API Endpoints)

4. Implementar Frontend
   - Components (React)
   - Services (API Calls)
   - Pages (Routes)
   - State Management

5. Tests
   - Backend: pytest + behave
   - Frontend: jest + testing-library

6. Code Review
   - Pull Request a main
   - Review obligatorio
   - CI pipeline debe pasar

7. Merge & Deploy
   - Merge a main
   - Auto-deploy a Render
   - Verificación en producción
```

---

## Evidencia de Metodologías

### DevOps Evidence

#### CI/CD Pipeline (GitHub Actions)
```yaml
# .github/workflows/deploy.yml
name: Deploy to Render
on:
  push:
    branches: [main]

jobs:
  build-and-test:
    - Run linters (flake8, mypy)
    - Run unit tests (pytest)
    - Run integration tests (behave)
    - Build Docker image
    - Push to registry

  deploy:
    - Trigger Render deployment
    - Run database migrations
    - Health check verification
    - Rollback on failure
```

#### Infrastructure as Code
```yaml
# docker-compose.yml
services:
  backend:
    build: ./backend_prod
    environment:
      - DB_URL=${DB_URL}
      - JWT_SECRET=${JWT_SECRET}
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8081/health"]
    
  frontend:
    build: ./frontend
    environment:
      - REACT_APP_API_BASE=${API_BASE}
```

### BDD Evidence

```python
# features/steps/incidencias_steps.py
from behave import given, when, then

@given('el usuario está autenticado como "{role}"')
def step_impl(context, role):
    context.user = authenticate_user(role)
    assert context.user is not None

@when('crea una incidencia con tipo "{tipo}"')
def step_impl(context, tipo):
    context.response = create_incidencia(tipo=tipo)

@then('la incidencia se crea exitosamente')
def step_impl(context):
    assert context.response.status_code == 201
```

---

## Métricas y KPIs

### Métricas de Desarrollo
- **Code Coverage**: >80% (objetivo de tesis)
- **Build Success Rate**: 95%
- **Deployment Frequency**: Multiple deployments por día
- **Mean Time to Recovery**: <30 minutos

### Métricas de Calidad
- **Bug Density**: <5 bugs por 1000 líneas
- **Technical Debt Ratio**: <5%
- **Code Review Time**: <24 horas
- **Test Automation**: >70%

---

## Conclusión

Este proyecto demuestra la aplicación práctica de:

1. **DevOps**: Automatización completa del ciclo de vida
2. **BDD**: Desarrollo guiado por comportamiento
3. **Clean Architecture**: Separación de responsabilidades
4. **Microservicios**: Arquitectura escalable
5. **CI/CD**: Despliegue continuo automatizado

La documentación completa está organizada en archivos separados para facilitar la navegación y comprensión de cada aspecto del sistema.

---

**Autor:** Andrea Travez  
**Tutor:** [Nombre del tutor]  
**Carrera:** Ingeniería en Sistemas  
**Universidad:** Universidad Técnica de Cotopaxi
