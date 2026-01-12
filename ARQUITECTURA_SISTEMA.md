# Arquitectura del Sistema - EPAGAL Latacunga

## Índice
1. [Modelo C4 - Arquitectura por Niveles](#modelo-c4)
2. [Arquitectura de Alto Nivel](#arquitectura-de-alto-nivel)
3. [Componentes del Sistema](#componentes-del-sistema)
4. [Patrones Arquitectónicos](#patrones-arquitectonicos)
5. [Decisiones de Diseño](#decisiones-de-diseno)

---

## Modelo C4 - Arquitectura por Niveles

### Nivel 1: Contexto del Sistema

```
┌──────────────────────────────────────────────────────────────┐
│                     SISTEMA EPAGAL                            │
│         Gestión de Residuos Sólidos Latacunga                │
└──────────────────────────────────────────────────────────────┘

Actores:
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│Administrador│         │  Operador   │         │  Conductor  │
│   Sistema   │         │  Incidencias│         │   Vehículo  │
└──────┬──────┘         └──────┬──────┘         └──────┬──────┘
       │                       │                        │
       │         ┌─────────────▼────────────┐          │
       └────────►│  Sistema de Gestión     │◄─────────┘
                 │  de Residuos Sólidos    │
                 └─────────────┬────────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │  PostgreSQL  │  │ OSRM Service │  │  SMS/Email   │
    │   Database   │  │   (Routing)  │  │   Gateway    │
    └──────────────┘  └──────────────┘  └──────────────┘
```

**Descripción:**
El sistema EPAGAL es una plataforma web que permite gestionar la recolección de residuos sólidos mediante:
- Registro y seguimiento de incidencias
- Generación automática de rutas optimizadas
- Asignación de conductores y vehículos
- Monitoreo en tiempo real de operaciones

---

### Nivel 2: Contenedores (Containers)

```
┌────────────────────────────────────────────────────────────────┐
│                    NAVEGADOR WEB (Chrome/Firefox/Safari)        │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │          APLICACIÓN SPA (React + TypeScript)             │ │
│  │                                                          │ │
│  │  Dashboard │ Rutas │ Incidencias │ Conductores │ Maps  │ │
│  └──────────────────────┬───────────────────────────────────┘ │
└─────────────────────────┼───────────────────────────────────────┘
                          │
                          │ HTTPS/JSON (REST API)
                          │ Authentication: JWT Bearer Token
                          │
┌─────────────────────────▼───────────────────────────────────────┐
│                 API BACKEND (FastAPI/Python)                     │
│                     Puerto 8081                                  │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                    API Gateway/Router                      │ │
│  └───────────────────────────┬───────────────────────────────┘ │
│                              │                                  │
│  ┌──────────────┬────────────┼───────────┬─────────────────┐  │
│  │              │            │           │                 │  │
│  ▼              ▼            ▼           ▼                 ▼  │
│ ┌─────┐   ┌────────┐   ┌────────┐   ┌────────┐   ┌────────┐ │
│ │Auth │   │ Rutas  │   │Inciden │   │Conduc  │   │Tracking│ │
│ │Serv │   │Service │   │Service │   │Service │   │Service │ │
│ └─────┘   └────────┘   └────────┘   └────────┘   └────────┘ │
└───────────────┬────────────────────────────────┬───────────────┘
                │                                │
                │                                │
    ┌───────────▼──────────┐          ┌─────────▼────────┐
    │  PostgreSQL 16       │          │  OSRM Routing    │
    │  + PostGIS 3.4       │          │  Service (HTTP)  │
    │                      │          │  router.project  │
    │  - usuarios          │          │  -osrm.org       │
    │  - incidencias       │          └──────────────────┘
    │  - rutas_generadas   │
    │  - conductores       │
    │  - asignaciones      │
    └──────────────────────┘
```

**Tecnologías por Contenedor:**

#### Frontend Container
- **Framework**: React 18.3.1
- **Lenguaje**: TypeScript 4.9.5
- **UI Library**: Material-UI 6.2.0
- **Routing**: React Router 7.1.1
- **HTTP Client**: Axios 1.7.9
- **Maps**: Leaflet 1.9.4
- **Charts**: Recharts 2.15.0
- **Build**: React Scripts 5.0.1
- **Deployment**: Render.com (Static Site)

#### Backend Container
- **Framework**: FastAPI 0.115.5
- **Lenguaje**: Python 3.11
- **ASGI Server**: Uvicorn 0.34.0
- **ORM**: SQLAlchemy 2.0.36
- **Validación**: Pydantic 2.10.3
- **Auth**: Python-Jose + Passlib
- **Testing**: Pytest + Behave
- **Deployment**: Render.com (Docker)

#### Database Container
- **RDBMS**: PostgreSQL 16
- **Extensiones**: PostGIS 3.4 (Geoespacial)
- **Hosting**: Neon.tech (Serverless)
- **Connection**: Pooling habilitado

---

### Nivel 3: Componentes (Backend)

```
┌──────────────────────────────────────────────────────────────┐
│                   BACKEND - FastAPI                           │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                      ROUTERS (API Layer)                      │
├──────────────────────────────────────────────────────────────┤
│  /api/auth/*         │  Login, Logout, Token Refresh         │
│  /api/incidencias/*  │  CRUD Incidencias, Stats              │
│  /api/rutas/*        │  Generar, Listar, Navegación          │
│  /api/conductores/*  │  CRUD Conductores, Asignaciones       │
│  /api/tracking/*     │  GPS Updates, Estado Real-time        │
│  /api/reports/*      │  Estadísticas, Exportar PDF/Excel     │
│  /api/notifications/*│  Push Notifications, Alerts           │
└──────────────────────┬───────────────────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────────────────┐
│                   SERVICES (Business Logic)                   │
├──────────────────────────────────────────────────────────────┤
│  AuthService         │ • Autenticación JWT                   │
│                      │ • Validación de permisos              │
│                      │ • Password hashing (bcrypt)           │
├──────────────────────┼───────────────────────────────────────┤
│  IncidenciaService   │ • Validación de datos                 │
│                      │ • Cálculo de gravedad                 │
│                      │ • Verificación de umbrales            │
├──────────────────────┼───────────────────────────────────────┤
│  RutaService         │ • Generación automática de rutas      │
│                      │ • Llamadas a OSRM para routing        │
│                      │ • Asignación de vehículos             │
│                      │ • Cálculo de costos y duración        │
├──────────────────────┼───────────────────────────────────────┤
│  ConductorService    │ • Gestión de disponibilidad           │
│                      │ • Asignación de rutas                 │
│                      │ • Historial de desempeño              │
├──────────────────────┼───────────────────────────────────────┤
│  OSRMService         │ • Integración con OSRM API            │
│                      │ • Cálculo de distancias               │
│                      │ • Optimización de secuencia           │
└──────────────────────┬───────────────────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────────────────┐
│                 MODELS & SCHEMAS (Data Layer)                 │
├──────────────────────────────────────────────────────────────┤
│  Models (SQLAlchemy) │ Schemas (Pydantic)                    │
├──────────────────────┼───────────────────────────────────────┤
│  Usuario             │ LoginRequest, TokenResponse           │
│  Conductor           │ ConductorCreate, ConductorResponse    │
│  Incidencia          │ IncidenciaCreate, IncidenciaResponse  │
│  RutaGenerada        │ RutaCreate, RutaResponse              │
│  RutaDetalle         │ RutaDetalleResponse                   │
│  AsignacionConductor │ AsignacionCreate, AsignacionResponse  │
│  PuntoFijo           │ PuntoFijoCreate                       │
└──────────────────────┴───────────────────────────────────────┘
```

**Estructura de Directorios Backend:**
```
backend_prod/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app initialization
│   ├── database.py             # SQLAlchemy engine & session
│   ├── models.py               # SQLAlchemy models
│   │
│   ├── routers/                # API Endpoints
│   │   ├── __init__.py
│   │   ├── auth.py             # /api/auth/*
│   │   ├── incidencias.py      # /api/incidencias/*
│   │   ├── rutas.py            # /api/rutas/*
│   │   ├── conductores.py      # /api/conductores/*
│   │   ├── tracking.py         # /api/tracking/*
│   │   ├── notifications.py    # /api/notifications/*
│   │   └── reports.py          # /api/reports/*
│   │
│   ├── services/               # Business Logic
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── ruta_service.py
│   │   ├── conductor_service.py
│   │   └── osrm_service.py
│   │
│   └── schemas/                # Pydantic Schemas
│       ├── __init__.py
│       └── conductores.py
│
├── features/                   # BDD Tests (Behave)
│   ├── incidencias.feature
│   ├── rutas.feature
│   └── steps/
│       └── incidencias_steps.py
│
├── tests/                      # Unit Tests (Pytest)
│   ├── test_incidencias.py
│   └── test_rutas.py
│
├── database/
│   └── migrations/             # SQL Migrations
│
├── Dockerfile                  # Container definition
├── docker-compose.yml          # Multi-container setup
├── requirements.txt            # Python dependencies
└── behave.ini                  # BDD configuration
```

---

### Nivel 4: Código (Code Level)

#### Ejemplo: Servicio de Generación de Rutas

```python
# app/services/ruta_service.py

from sqlalchemy.orm import Session
from typing import List, Optional, Tuple
from app.models import Incidencia, RutaGenerada, RutaDetalle
from app.services.osrm_service import OSRMService
import logging

class RutaService:
    """
    Servicio para generación y gestión de rutas optimizadas.
    
    Responsabilidades:
    - Obtener incidencias pendientes por zona
    - Calcular ruta óptima usando OSRM
    - Asignar vehículos según capacidad
    - Persistir ruta y detalles en BD
    """
    
    def __init__(self):
        self.osrm_service = OSRMService()
        self.logger = logging.getLogger(__name__)
    
    def generar_ruta_automatica(
        self, 
        db: Session, 
        zona: str
    ) -> Optional[RutaGenerada]:
        """
        Genera una ruta optimizada para una zona específica.
        
        Args:
            db: Sesión de base de datos
            zona: 'oriental' u 'occidental'
            
        Returns:
            RutaGenerada con detalles completos o None si no hay incidencias
            
        Flujo:
        1. Obtener incidencias pendientes
        2. Ordenar por gravedad descendente
        3. Calcular ruta óptima con OSRM
        4. Asignar vehículos según necesidad
        5. Crear registros en BD
        """
        # 1. Obtener incidencias pendientes
        incidencias = db.query(Incidencia).filter(
            Incidencia.zona == zona,
            Incidencia.estado == 'pendiente'
        ).order_by(Incidencia.gravedad.desc()).all()
        
        if not incidencias:
            self.logger.info(f"No hay incidencias pendientes en zona {zona}")
            return None
        
        # 2. Preparar coordenadas para OSRM
        coordenadas = [(inc.lat, inc.lon) for inc in incidencias]
        
        # 3. Llamar a OSRM para calcular ruta óptima
        ruta_optimizada = self.osrm_service.calcular_ruta_optima(
            coordenadas
        )
        
        if not ruta_optimizada:
            self.logger.error("OSRM no pudo calcular ruta")
            return None
        
        # 4. Calcular métricas
        suma_gravedad = sum(inc.gravedad for inc in incidencias)
        camiones_necesarios = self._calcular_camiones(incidencias)
        
        # 5. Crear ruta en BD
        nueva_ruta = RutaGenerada(
            zona=zona,
            suma_gravedad=suma_gravedad,
            camiones_usados=camiones_necesarios,
            costo_total=ruta_optimizada['distance'],
            duracion_estimada=timedelta(
                seconds=ruta_optimizada['duration']
            ),
            estado='planeada'
        )
        
        db.add(nueva_ruta)
        db.flush()  # Obtener ID
        
        # 6. Crear detalles de ruta (puntos)
        for orden, inc in enumerate(incidencias, 1):
            detalle = RutaDetalle(
                ruta_id=nueva_ruta.id,
                orden=orden,
                incidencia_id=inc.id,
                lat=inc.lat,
                lon=inc.lon,
                tipo_punto='incidencia',
                camion_tipo=self._asignar_tipo_camion(inc)
            )
            db.add(detalle)
            
            # Marcar incidencia como asignada
            inc.estado = 'asignada'
        
        db.commit()
        db.refresh(nueva_ruta)
        
        self.logger.info(
            f"Ruta {nueva_ruta.id} generada: "
            f"{len(incidencias)} incidencias, "
            f"{camiones_necesarios} camiones"
        )
        
        return nueva_ruta
    
    def _calcular_camiones(
        self, 
        incidencias: List[Incidencia]
    ) -> int:
        """
        Calcula cantidad de camiones necesarios.
        
        Reglas:
        - Camión recolector: capacidad 10 puntos de gravedad
        - Camión compactador: capacidad 15 puntos
        - Volqueta: capacidad 20 puntos
        """
        total_gravedad = sum(inc.gravedad for inc in incidencias)
        
        # Usar camiones compactadores (capacidad 15)
        camiones = (total_gravedad // 15) + (1 if total_gravedad % 15 > 0 else 0)
        
        return max(camiones, 1)  # Mínimo 1 camión
    
    def _asignar_tipo_camion(self, incidencia: Incidencia) -> str:
        """Asigna tipo de camión según tipo de incidencia."""
        mapping = {
            'acopio_lleno': 'compactador',
            'animal_muerto': 'recolector',
            'escombros': 'volqueta',
            'zona_critica': 'compactador'
        }
        return mapping.get(incidencia.tipo, 'recolector')
```

---

## Arquitectura de Alto Nivel

### Patrón de Arquitectura: Layered Architecture + Service-Oriented

```
┌─────────────────────────────────────────────────────────────┐
│                   PRESENTATION LAYER                         │
│              (React Components + Pages)                      │
│  • UI Components (Material-UI)                              │
│  • Page Components (Dashboard, Rutas, etc.)                 │
│  • State Management (React Hooks)                           │
└───────────────────────┬─────────────────────────────────────┘
                        │ HTTP/REST
┌───────────────────────▼─────────────────────────────────────┐
│                    API LAYER                                 │
│              (FastAPI Routers)                               │
│  • Request Validation (Pydantic)                            │
│  • Response Serialization                                   │
│  • Authentication & Authorization (JWT)                     │
│  • Error Handling & Logging                                 │
└───────────────────────┬─────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│                  BUSINESS LOGIC LAYER                        │
│                 (Service Classes)                            │
│  • Domain Logic                                             │
│  • Business Rules Validation                                │
│  • Integration with External APIs (OSRM)                    │
│  • Complex Calculations                                     │
└───────────────────────┬─────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│                   DATA ACCESS LAYER                          │
│              (SQLAlchemy ORM + Models)                       │
│  • Database Queries                                         │
│  • Transactions                                             │
│  • Relationship Management                                  │
└───────────────────────┬─────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│                    DATABASE LAYER                            │
│          (PostgreSQL + PostGIS)                              │
│  • Data Persistence                                         │
│  • Geospatial Queries                                       │
│  • Indexes & Constraints                                    │
└─────────────────────────────────────────────────────────────┘
```

### Comunicación Entre Capas

**Reglas de Comunicación:**
1. Cada capa solo puede comunicarse con la capa inmediatamente inferior
2. No se permite "saltar" capas (ej: Presentation → Data Access)
3. La comunicación es siempre unidireccional (top-down)
4. Las respuestas fluyen de abajo hacia arriba

---

## Componentes del Sistema

### 1. Frontend Components

```
frontend/src/
├── components/
│   ├── Auth/
│   │   └── Login.tsx              # Formulario de login
│   ├── Dashboard/
│   │   └── Dashboard.tsx          # Panel principal
│   ├── Incidents/
│   │   └── IncidentsPage.tsx      # Gestión de incidencias
│   ├── Routes/
│   │   ├── GeneracionRutas.tsx    # Generación de rutas
│   │   ├── MisRutas.tsx           # Rutas asignadas
│   │   ├── RutaDetalle.tsx        # Detalle de ruta
│   │   └── LiveTracking.tsx       # Tracking en vivo
│   ├── Layout/
│   │   ├── Sidebar.tsx            # Menú lateral
│   │   └── Dashboard.tsx          # Layout wrapper
│   └── Reports/
│       └── ReportsPage.tsx        # Reportes y estadísticas
│
├── services/                       # API Clients
│   ├── apiService.ts              # Axios instance configurado
│   ├── incidenciasService.ts      # CRUD incidencias
│   ├── rutasService.ts            # CRUD rutas
│   ├── conductoresService.ts      # CRUD conductores
│   ├── reportesService.ts         # Estadísticas
│   └── routingMap.ts              # Integración con Leaflet
│
├── config/
│   └── api.ts                     # Endpoints configuration
│
└── pages/                         # Route-level components
    ├── ReportesPage.tsx
    ├── OperadoresPage.tsx
    ├── TrackingPage.tsx
    └── HorariosPage.tsx
```

### 2. Backend Components

#### 2.1 Routers (API Endpoints)

```python
# Estructura de routers
routers/
├── auth.py           # POST /api/auth/login
│                    # POST /api/auth/logout
│                    # GET  /api/auth/me
│
├── incidencias.py   # GET    /api/incidencias/
│                    # POST   /api/incidencias/
│                    # GET    /api/incidencias/{id}
│                    # PUT    /api/incidencias/{id}
│                    # DELETE /api/incidencias/{id}
│                    # GET    /api/incidencias/stats
│
├── rutas.py         # POST /api/rutas/generar/{zona}
│                    # GET  /api/rutas/{ruta_id}
│                    # GET  /api/rutas/{ruta_id}/detalles
│                    # GET  /api/rutas/zona/{zona}
│                    # GET  /api/rutas/historial/estado
│
├── conductores.py   # GET  /api/conductores/
│                    # POST /api/conductores/
│                    # GET  /api/conductores/{id}
│                    # PATCH /api/conductores/{id}
│                    # GET  /api/conductores/disponibles
│                    # GET  /api/conductores/mis-rutas/todas
│
└── tracking.py      # POST /api/tracking/update-location
                     # GET  /api/tracking/active-routes
                     # GET  /api/tracking/route/{ruta_id}/status
```

#### 2.2 Models (Database Schema)

```python
# Principales modelos SQLAlchemy

class Usuario(Base):
    __tablename__ = 'usuarios'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    tipo_usuario = Column(Enum('admin', 'operador', 'conductor'))
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Conductor(Base):
    __tablename__ = 'conductores'
    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'))
    nombre_completo = Column(String(100), nullable=False)
    cedula = Column(String(10), unique=True, nullable=False)
    telefono = Column(String(10))
    licencia_tipo = Column(String(5))
    estado = Column(Enum('disponible', 'ocupado', 'inactivo'))
    zona_preferida = Column(Enum('oriental', 'occidental', 'ambas'))
    
    # Relationships
    usuario = relationship("Usuario", back_populates="conductor")
    asignaciones = relationship("AsignacionConductor")

class Incidencia(Base):
    __tablename__ = 'incidencias'
    id = Column(Integer, primary_key=True)
    tipo = Column(Enum('acopio_lleno', 'animal_muerto', 'escombros', 'zona_critica'))
    gravedad = Column(Integer, CheckConstraint('gravedad >= 1 AND gravedad <= 10'))
    descripcion = Column(Text)
    foto_url = Column(String(500))
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    zona = Column(Enum('oriental', 'occidental'))
    estado = Column(Enum('pendiente', 'asignada', 'resuelta'))
    reportado_en = Column(DateTime, default=datetime.utcnow)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'))
    
    # PostGIS Geography Point
    location = Column(Geography(geometry_type='POINT', srid=4326))

class RutaGenerada(Base):
    __tablename__ = 'rutas_generadas'
    id = Column(Integer, primary_key=True)
    zona = Column(Enum('oriental', 'occidental'))
    fecha_generacion = Column(DateTime, default=datetime.utcnow)
    suma_gravedad = Column(Integer)
    camiones_usados = Column(Integer)
    costo_total = Column(Integer)  # metros
    duracion_estimada = Column(Interval)
    estado = Column(Enum('planeada', 'en_ejecucion', 'completada'))
    notas = Column(Text)
    
    # Relationships
    detalles = relationship("RutaDetalle")
    asignaciones = relationship("AsignacionConductor")

class RutaDetalle(Base):
    __tablename__ = 'rutas_detalles'
    id = Column(Integer, primary_key=True)
    ruta_id = Column(Integer, ForeignKey('rutas_generadas.id'))
    orden = Column(Integer)
    incidencia_id = Column(Integer, ForeignKey('incidencias.id'))
    punto_fijo_id = Column(Integer, ForeignKey('puntos_fijos.id'))
    lat = Column(Float)
    lon = Column(Float)
    tipo_punto = Column(Enum('incidencia', 'punto_fijo', 'inicio', 'fin'))
    camion_tipo = Column(String(20))
    camion_id = Column(String(10))

class AsignacionConductor(Base):
    __tablename__ = 'asignaciones_conductores'
    id = Column(Integer, primary_key=True)
    conductor_id = Column(Integer, ForeignKey('conductores.id'))
    ruta_id = Column(Integer, ForeignKey('rutas_generadas.id'))
    camion_id = Column(String(10))
    camion_tipo = Column(String(20))
    estado = Column(Enum('asignada', 'iniciada', 'completada'))
    fecha_asignacion = Column(DateTime, default=datetime.utcnow)
    fecha_inicio = Column(DateTime)
    fecha_fin = Column(DateTime)
```

---

## Patrones Arquitectónicos Implementados

### 1. Repository Pattern
```python
# Abstracción de acceso a datos
class IncidenciaRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, id: int) -> Optional[Incidencia]:
        return self.db.query(Incidencia).filter(Incidencia.id == id).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Incidencia]:
        return self.db.query(Incidencia).offset(skip).limit(limit).all()
    
    def create(self, incidencia: Incidencia) -> Incidencia:
        self.db.add(incidencia)
        self.db.commit()
        self.db.refresh(incidencia)
        return incidencia
```

### 2. Dependency Injection
```python
# FastAPI Depends para inyección de dependencias
def get_db():
    """Dependency para obtener sesión de BD."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/incidencias/")
def listar_incidencias(
    db: Session = Depends(get_db),           # Inyección de DB
    current_user: Usuario = Depends(get_current_user)  # Inyección de Auth
):
    return db.query(Incidencia).all()
```

### 3. Service Layer Pattern
```python
# Separación de lógica de negocio
class RutaService:
    def generar_ruta(self, db: Session, zona: str) -> RutaGenerada:
        # Lógica compleja aquí
        pass

# Router delega a Service
@router.post("/rutas/generar/{zona}")
def generar_ruta(zona: str, db: Session = Depends(get_db)):
    service = RutaService()
    return service.generar_ruta(db, zona)
```

### 4. DTO Pattern (Data Transfer Objects)
```python
# Pydantic schemas como DTOs
class IncidenciaCreate(BaseModel):
    """DTO para crear incidencia - input."""
    tipo: str
    gravedad: int
    descripcion: str
    lat: float
    lon: float

class IncidenciaResponse(BaseModel):
    """DTO para respuesta - output."""
    id: int
    tipo: str
    gravedad: int
    estado: str
    reportado_en: datetime
    
    class Config:
        from_attributes = True
```

### 5. Factory Pattern
```python
# Factory para crear servicios
class ServiceFactory:
    @staticmethod
    def create_ruta_service():
        return RutaService(osrm_url=settings.OSRM_URL)
    
    @staticmethod
    def create_notification_service():
        return NotificationService(
            smtp_server=settings.SMTP_SERVER
        )
```

---

## Decisiones de Diseño

### 1. ¿Por qué FastAPI en lugar de Django/Flask?

**Ventajas de FastAPI:**
- ✅ **Performance**: 10x más rápido que Flask (ASGI vs WSGI)
- ✅ **Type Safety**: Validación automática con Pydantic
- ✅ **Async Support**: Manejo nativo de operaciones asincrónicas
- ✅ **Auto Documentation**: Swagger UI y ReDoc out-of-the-box
- ✅ **Modern**: Python 3.6+ features (type hints, async/await)

**Comparación:**
```python
# Django REST Framework
class IncidenciaViewSet(viewsets.ModelViewSet):
    queryset = Incidencia.objects.all()
    serializer_class = IncidenciaSerializer

# FastAPI (más conciso, type-safe)
@router.get("/incidencias/", response_model=List[IncidenciaResponse])
def listar_incidencias(db: Session = Depends(get_db)):
    return db.query(Incidencia).all()
```

### 2. ¿Por qué React en lugar de Vue/Angular?

**Ventajas de React:**
- ✅ **Ecosistema**: Mayor cantidad de librerías y componentes
- ✅ **Community**: Comunidad más grande, más recursos
- ✅ **Performance**: Virtual DOM eficiente
- ✅ **TypeScript**: Excelente integración
- ✅ **Flexibilidad**: No es un framework rígido

### 3. ¿Por qué PostgreSQL + PostGIS?

**Ventajas:**
- ✅ **Geoespacial**: PostGIS es el estándar para datos geográficos
- ✅ **ACID**: Transacciones confiables
- ✅ **JSON Support**: Para datos semi-estructurados
- ✅ **Extensible**: Funciones personalizadas, triggers
- ✅ **Open Source**: Sin costos de licencia

**Funciones PostGIS utilizadas:**
```sql
-- Distancia entre dos puntos (en metros)
SELECT ST_Distance(
    ST_MakePoint(-78.6170, -0.9322)::geography,
    ST_MakePoint(-78.6180, -0.9330)::geography
);

-- Incidencias dentro de un radio
SELECT * FROM incidencias
WHERE ST_DWithin(
    location,
    ST_MakePoint(-78.6170, -0.9322)::geography,
    1000  -- 1km de radio
);
```

### 4. ¿Por qué OSRM para routing?

**Alternativas consideradas:**
- Google Maps API (costo)
- Mapbox Directions API (costo)
- GraphHopper (más pesado)

**Ventajas de OSRM:**
- ✅ **Open Source**: Gratuito
- ✅ **Performance**: Muy rápido para cálculos
- ✅ **Optimización**: Algoritmos TSP (Traveling Salesman)
- ✅ **Self-hosted**: Podemos correr nuestro propio servidor
- ✅ **OpenStreetMap**: Datos actualizados

### 5. ¿Por qué Render.com para deployment?

**Alternativas consideradas:**
- AWS (complejidad)
- Heroku (costo)
- DigitalOcean (requiere más configuración)

**Ventajas de Render:**
- ✅ **Simplicidad**: Deploy desde GitHub
- ✅ **Free Tier**: Para desarrollo/demo
- ✅ **Auto-deploy**: CI/CD integrado
- ✅ **PostgreSQL**: Base de datos incluida
- ✅ **SSL**: HTTPS automático

---

## Escalabilidad y Performance

### Estrategias de Escalabilidad

#### 1. Horizontal Scaling (Scale Out)
```
Load Balancer
     │
     ├──► Backend Instance 1 ──┐
     ├──► Backend Instance 2 ──┼──► PostgreSQL
     └──► Backend Instance 3 ──┘
```

#### 2. Caching Strategy
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_zona_conductores(zona: str):
    """Cache de conductores por zona."""
    return db.query(Conductor).filter(
        Conductor.zona_preferida == zona
    ).all()
```

#### 3. Database Optimization
```sql
-- Índices geoespaciales
CREATE INDEX idx_incidencias_location 
ON incidencias USING GIST(location);

-- Índices compuestos
CREATE INDEX idx_incidencias_zona_estado 
ON incidencias(zona, estado);

-- Particionamiento por zona
CREATE TABLE incidencias_oriental 
PARTITION OF incidencias FOR VALUES IN ('oriental');
```

#### 4. Async Operations
```python
import asyncio

async def procesar_incidencias_batch(incidencias: List[int]):
    """Procesamiento asíncrono de múltiples incidencias."""
    tasks = [
        procesar_incidencia(inc_id) 
        for inc_id in incidencias
    ]
    await asyncio.gather(*tasks)
```

---

## Seguridad

### 1. Autenticación y Autorización

```python
# JWT Token-based Authentication
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    return jose.jwt.encode(
        to_encode, 
        SECRET_KEY, 
        algorithm="HS256"
    )

# Role-based Access Control
def require_admin(current_user: Usuario = Depends(get_current_user)):
    if current_user.tipo_usuario != 'admin':
        raise HTTPException(status_code=403, detail="Admin required")
    return current_user
```

### 2. Validación de Inputs
```python
# Pydantic valida automáticamente
class IncidenciaCreate(BaseModel):
    gravedad: int = Field(ge=1, le=10)  # Entre 1 y 10
    lat: float = Field(ge=-90, le=90)   # Latitud válida
    lon: float = Field(ge=-180, le=180) # Longitud válida
    descripcion: str = Field(min_length=10, max_length=500)
```

### 3. SQL Injection Prevention
```python
# SQLAlchemy ORM previene SQL injection
# MAL (vulnerable):
db.execute(f"SELECT * FROM usuarios WHERE username = '{username}'")

# BIEN (seguro):
db.query(Usuario).filter(Usuario.username == username).first()
```

### 4. CORS Configuration
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://tesis-1-z78t.onrender.com",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Monitoreo y Observabilidad

### 1. Health Checks
```python
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "EPAGAL Backend",
        "version": "2.0.1",
        "timestamp": datetime.utcnow(),
        "environment": "production",
        "python_version": "3.11.14",
        "database": "connected" if check_db() else "disconnected"
    }
```

### 2. Logging
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

logger.info(f"Ruta {ruta_id} generada exitosamente")
logger.error(f"Error en OSRM: {error}", exc_info=True)
```

### 3. Métricas
```python
from prometheus_client import Counter, Histogram

# Contadores
requests_total = Counter('requests_total', 'Total de requests')
routes_generated = Counter('routes_generated', 'Rutas generadas')

# Histogramas (latencias)
request_duration = Histogram(
    'request_duration_seconds',
    'Duración de requests'
)
```

---

**Conclusión:**

La arquitectura del sistema EPAGAL está diseñada para ser:
- **Modular**: Componentes independientes y reusables
- **Escalable**: Preparada para crecer horizontalmente
- **Mantenible**: Código limpio y bien documentado
- **Segura**: Múltiples capas de seguridad
- **Observable**: Monitoreo y logging completo

Esta arquitectura soporta los principios de DevOps y permite iteraciones rápidas con despliegues continuos.
