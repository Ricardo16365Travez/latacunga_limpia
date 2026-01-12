# Backend Técnico - EPAGAL Latacunga

## Estructura del Proyecto Backend

```
backend_prod/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app initialization
│   ├── database.py             # SQLAlchemy setup
│   ├── models.py               # ORM Models
│   │
│   ├── routers/                # API Endpoints
│   │   ├── auth.py            # /api/auth/*
│   │   ├── incidencias.py     # /api/incidencias/*
│   │   ├── rutas.py           # /api/rutas/*
│   │   ├── conductores.py     # /api/conductores/*
│   │   ├── tracking.py        # /api/tracking/*
│   │   ├── notifications.py   # /api/notifications/*
│   │   └── reports.py         # /api/reports/*
│   │
│   ├── services/               # Business Logic
│   │   ├── auth_service.py
│   │   ├── incidencia_service.py
│   │   ├── ruta_service.py
│   │   ├── conductor_service.py
│   │   ├── osrm_service.py
│   │   ├── notification_service.py
│   │   └── report_service.py
│   │
│   ├── schemas/                # Pydantic Models
│   │   └── conductores.py
│   │
│   └── utils/
│       ├── auth.py             # JWT helpers
│       ├── validators.py       # Custom validators
│       └── exceptions.py       # Custom exceptions
│
├── features/                   # BDD Tests (Behave)
│   ├── incidencias.feature
│   ├── rutas.feature
│   └── steps/
│       ├── incidencias_steps.py
│       └── rutas_steps.py
│
├── tests/                      # Unit Tests (Pytest)
│   ├── test_auth.py
│   ├── test_incidencias.py
│   ├── test_rutas.py
│   └── conftest.py
│
├── database/
│   ├── init.sql
│   ├── seed_data.sql
│   └── migrations/             # Alembic
│       ├── versions/
│       ├── env.py
│       └── script.py.mako
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── behave.ini
└── setup.cfg
```

---

## Autenticación JWT

### Flujo de Login

```python
# app/routers/auth.py

from fastapi import APIRouter, HTTPException, status
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

router = APIRouter(prefix="/api/auth", tags=["authentication"])

# Configuración
SECRET_KEY = "tu-clave-secreta-super-larga-y-aleatoria"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hash de contraseñas
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

# JWT Tokens
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Dependency para obtener usuario actual
async def get_current_user(
    token: str = Depends(HTTPBearer())
) -> Usuario:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    db = SessionLocal()
    user = db.query(Usuario).filter(Usuario.username == username).first()
    db.close()
    
    if user is None:
        raise credentials_exception
    return user

# Endpoint login
@router.post("/login")
async def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """
    Login de usuario.
    
    Returns:
        access_token: JWT token para usar en requests
        token_type: "bearer"
        usuario_id: ID del usuario
    """
    user = db.query(Usuario).filter(
        Usuario.username == credentials.username
    ).first()
    
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos"
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "usuario_id": user.id,
        "username": user.username
    }
```

---

## Modelos SQLAlchemy

```python
# app/models.py

from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, Text, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSON
from geoalchemy2 import Geography
from datetime import datetime

class Usuario(Base):
    __tablename__ = 'usuarios'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    tipo_usuario = Column(Enum('admin', 'operador', 'conductor'), default='operador')
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    conductor = relationship("Conductor", back_populates="usuario", uselist=False)
    incidencias = relationship("Incidencia", back_populates="usuario")

class Conductor(Base):
    __tablename__ = 'conductores'
    
    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), unique=True)
    nombre_completo = Column(String(100), nullable=False)
    cedula = Column(String(10), unique=True, nullable=False)
    telefono = Column(String(10))
    licencia_tipo = Column(String(5))  # A, B, E, D, etc.
    estado = Column(Enum('disponible', 'ocupado', 'inactivo'), default='disponible')
    zona_preferida = Column(Enum('oriental', 'occidental', 'ambas'))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    usuario = relationship("Usuario", back_populates="conductor")
    asignaciones = relationship("AsignacionConductor", back_populates="conductor")

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
    estado = Column(Enum('pendiente', 'asignada', 'resuelta'), default='pendiente')
    reportado_en = Column(DateTime, default=datetime.utcnow)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'))
    
    # PostGIS Geography Point
    location = Column(Geography(geometry_type='POINT', srid=4326))
    
    # Relationships
    usuario = relationship("Usuario", back_populates="incidencias")

class RutaGenerada(Base):
    __tablename__ = 'rutas_generadas'
    
    id = Column(Integer, primary_key=True)
    zona = Column(Enum('oriental', 'occidental'))
    fecha_generacion = Column(DateTime, default=datetime.utcnow)
    suma_gravedad = Column(Integer)
    camiones_usados = Column(Integer)
    costo_total = Column(Integer)  # en metros
    duracion_estimada = Column(Interval)
    estado = Column(Enum('planeada', 'en_ejecucion', 'completada'), default='planeada')
    notas = Column(Text)
    
    # Relationships
    detalles = relationship("RutaDetalle", back_populates="ruta")
    asignaciones = relationship("AsignacionConductor", back_populates="ruta")

class RutaDetalle(Base):
    __tablename__ = 'rutas_detalles'
    
    id = Column(Integer, primary_key=True)
    ruta_id = Column(Integer, ForeignKey('rutas_generadas.id'))
    orden = Column(Integer)
    incidencia_id = Column(Integer, ForeignKey('incidencias.id'), nullable=True)
    lat = Column(Float)
    lon = Column(Float)
    tipo_punto = Column(Enum('incidencia', 'punto_fijo', 'inicio', 'fin'))
    camion_tipo = Column(String(20))
    camion_id = Column(String(10))
    
    # Relationships
    ruta = relationship("RutaGenerada", back_populates="detalles")
    incidencia = relationship("Incidencia")

class AsignacionConductor(Base):
    __tablename__ = 'asignaciones_conductores'
    
    id = Column(Integer, primary_key=True)
    conductor_id = Column(Integer, ForeignKey('conductores.id'))
    ruta_id = Column(Integer, ForeignKey('rutas_generadas.id'))
    camion_id = Column(String(10), nullable=False)
    camion_tipo = Column(String(20))
    estado = Column(Enum('asignada', 'iniciada', 'completada'), default='asignada')
    fecha_asignacion = Column(DateTime, default=datetime.utcnow)
    fecha_inicio = Column(DateTime)
    fecha_fin = Column(DateTime)
    
    # Relationships
    conductor = relationship("Conductor", back_populates="asignaciones")
    ruta = relationship("RutaGenerada", back_populates="asignaciones")
```

---

## Pydantic Schemas

```python
# app/schemas.py

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime

class IncidenciaCreate(BaseModel):
    tipo: str
    gravedad: int = Field(ge=1, le=10)
    descripcion: str = Field(min_length=10, max_length=500)
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)
    
    @validator('tipo')
    def tipo_valido(cls, v):
        validos = {'acopio_lleno', 'animal_muerto', 'escombros', 'zona_critica'}
        if v not in validos:
            raise ValueError(f'Tipo debe ser uno de: {validos}')
        return v

class IncidenciaResponse(BaseModel):
    id: int
    tipo: str
    gravedad: int
    descripcion: str
    zona: str
    estado: str
    reportado_en: datetime
    
    class Config:
        from_attributes = True

class RutaGeneradaResponse(BaseModel):
    id: int
    zona: str
    suma_gravedad: int
    camiones_usados: int
    costo_total: int
    duracion_estimada: str
    estado: str
    detalles: List[dict]
    
    class Config:
        from_attributes = True
```

---

## Servicios de Negocio

```python
# app/services/incidencia_service.py

class IncidenciaService:
    
    def calcular_zona(self, lat: float, lon: float) -> str:
        """
        Calcula zona (oriental u occidental) según coordenadas.
        
        Referencia: Latacunga ~0.9322°S, 78.6170°W
        - Oriental: lon < -78.6170 (Este)
        - Occidental: lon >= -78.6170 (Oeste)
        """
        SEPARADOR_LON = -78.6170
        return 'oriental' if lon < SEPARADOR_LON else 'occidental'
    
    def crear_incidencia(self, db: Session, data: IncidenciaCreate, user_id: int) -> Incidencia:
        """Crea incidencia con validación completa."""
        
        # Validar coordenadas
        self.validar_coordenadas(data.lat, data.lon)
        
        # Calcular zona automáticamente
        zona = self.calcular_zona(data.lat, data.lon)
        
        # Crear punto geográfico
        from geoalchemy2.elements import WKTElement
        location = WKTElement(f'POINT({data.lon} {data.lat})', srid=4326)
        
        # Crear incidencia
        incidencia = Incidencia(
            tipo=data.tipo,
            gravedad=data.gravedad,
            descripcion=data.descripcion,
            lat=data.lat,
            lon=data.lon,
            zona=zona,
            location=location,
            usuario_id=user_id,
            estado='pendiente'
        )
        
        db.add(incidencia)
        db.commit()
        db.refresh(incidencia)
        
        return incidencia
    
    def listar_por_zona(self, db: Session, zona: str, estado: Optional[str] = None):
        """Lista incidencias de una zona, opcionalmente filtradas por estado."""
        query = db.query(Incidencia).filter(Incidencia.zona == zona)
        
        if estado:
            query = query.filter(Incidencia.estado == estado)
        
        return query.order_by(Incidencia.gravedad.desc()).all()
    
    def obtener_estadisticas(self, db: Session) -> dict:
        """Retorna estadísticas generales."""
        total = db.query(Incidencia).count()
        pendientes = db.query(Incidencia).filter(
            Incidencia.estado == 'pendiente'
        ).count()
        resueltas = db.query(Incidencia).filter(
            Incidencia.estado == 'resuelta'
        ).count()
        
        return {
            "total_incidencias": total,
            "pendientes": pendientes,
            "resueltas": resueltas,
            "tasa_resolucion": round((resueltas / total * 100), 2) if total > 0 else 0
        }
```

---

## Endpoints Principales

### Incidencias
```
GET    /api/incidencias/          → Listar todas
POST   /api/incidencias/          → Crear nueva
GET    /api/incidencias/{id}      → Obtener por ID
PUT    /api/incidencias/{id}      → Actualizar
DELETE /api/incidencias/{id}      → Eliminar
GET    /api/incidencias/stats     → Estadísticas
GET    /api/incidencias/zona/{zona} → Por zona
```

### Rutas
```
POST   /api/rutas/generar/{zona}     → Generar ruta optimizada
GET    /api/rutas/{id}               → Obtener ruta
GET    /api/rutas/{id}/detalles      → Puntos de la ruta
GET    /api/rutas/historial/estado   → Historial
```

### Conductores
```
GET    /api/conductores/              → Listar
POST   /api/conductores/              → Crear
GET    /api/conductores/{id}          → Obtener
PATCH  /api/conductores/{id}          → Actualizar
GET    /api/conductores/disponibles   → Disponibles por zona
GET    /api/conductores/mis-rutas/todas → Mis rutas asignadas
```

### Tracking
```
POST   /api/tracking/update-location  → Actualizar GPS
GET    /api/tracking/active-routes    → Rutas en ejecución
GET    /api/tracking/route/{id}/status → Estado de ruta
```

---

## Manejo de Errores

```python
# app/utils/exceptions.py

from fastapi import HTTPException, status

class IncidenciaNoEncontrada(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incidencia no encontrada"
        )

class RutaGeneracionFallida(HTTPException):
    def __init__(self, reason: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al generar ruta: {reason}"
        )

class NoHayIncidenciasPendientes(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay incidencias pendientes en la zona"
        )
```

---

## Conclusión

El backend de EPAGAL está arquitectado siguiendo principios SOLID con:
- ✅ Separación clara de responsabilidades
- ✅ Inyección de dependencias
- ✅ Validación automática con Pydantic
- ✅ Transacciones ACID
- ✅ Geoespacialidad con PostGIS
- ✅ Autenticación segura con JWT
