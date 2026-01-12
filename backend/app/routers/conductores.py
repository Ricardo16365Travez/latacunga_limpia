"""
Router de conductores para FastAPI
"""
from fastapi import APIRouter, Depends, HTTPException, status  # type: ignore[import]
from sqlalchemy.orm import Session  # type: ignore[import]
from pydantic import BaseModel  # type: ignore[import]
from typing import Annotated, List, Optional
from datetime import datetime
from app.database import get_db
from app.models import Conductor

router = APIRouter(prefix="/conductores", tags=["conductores"])


class ConductorResponse(BaseModel):
    id: int
    cedula: str
    nombre_completo: str
    email: str
    telefono: str
    username: str
    licencia_tipo: str
    zona_preferida: Optional[str] = None
    estado: str
    usuario_id: Optional[int] = None
    fecha_contratacion: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class ConductorCreate(BaseModel):
    cedula: str
    nombre_completo: str
    email: str
    telefono: str
    username: str
    licencia_tipo: str
    zona_preferida: Optional[str] = None


@router.get("/", response_model=List[ConductorResponse])
async def listar_conductores(db: Annotated[Session, Depends(get_db)]):
    """Listar todos los conductores"""
    return db.query(Conductor).all()


@router.post("/", response_model=ConductorResponse, status_code=status.HTTP_201_CREATED)
async def crear_conductor(
    conductor: ConductorCreate,
    db: Annotated[Session, Depends(get_db)]
):
    """Crear nuevo conductor"""
    # Verificar si ya existe
    existing = db.query(Conductor).filter(
        (Conductor.cedula == conductor.cedula) |
        (Conductor.email == conductor.email) |
        (Conductor.username == conductor.username)
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Conductor ya existe"
        )

    new_conductor = Conductor(
        cedula=conductor.cedula,
        nombre_completo=conductor.nombre_completo,
        email=conductor.email,
        telefono=conductor.telefono,
        username=conductor.username,
        licencia_tipo=conductor.licencia_tipo,
        zona_preferida=conductor.zona_preferida,
        estado="disponible"
    )
    db.add(new_conductor)
    db.commit()
    db.refresh(new_conductor)
    return new_conductor


@router.get("/{conductor_id}", response_model=ConductorResponse)
async def obtener_conductor(conductor_id: int, db: Annotated[Session, Depends(get_db)]):
    """Obtener un conductor específico"""
    conductor = db.query(Conductor).filter(Conductor.id == conductor_id).first()
    if not conductor:
        raise HTTPException(status_code=404, detail="Conductor no encontrado")
    return conductor


@router.patch("/{conductor_id}", response_model=ConductorResponse)
async def actualizar_conductor(
    conductor_id: int,
    payload: dict,
    db: Annotated[Session, Depends(get_db)]
):
    """Actualizar un conductor"""
    conductor = db.query(Conductor).filter(Conductor.id == conductor_id).first()
    if not conductor:
        raise HTTPException(status_code=404, detail="Conductor no encontrado")

    for key, value in payload.items():
        if hasattr(conductor, key) and key != "id":
            setattr(conductor, key, value)

    db.commit()
    db.refresh(conductor)
    return conductor


@router.delete("/{conductor_id}")
async def eliminar_conductor(conductor_id: int, db: Annotated[Session, Depends(get_db)]):
    """Eliminar un conductor"""
    conductor = db.query(Conductor).filter(Conductor.id == conductor_id).first()
    if not conductor:
        raise HTTPException(status_code=404, detail="Conductor no encontrado")

    db.delete(conductor)
    db.commit()
    return {"mensaje": "Conductor eliminado"}


@router.get("/mis-rutas/todas", response_model=List[dict])
async def mis_rutas_todas(db: Annotated[Session, Depends(get_db)], conductor_id: int = 1):
    """Obtener todas las rutas asignadas al conductor"""
    # TODO: Implementar lógica real cuando exista tabla de asignaciones
    return []


@router.get("/mis-rutas/actual", response_model=Optional[dict])
async def mis_rutas_actual(db: Annotated[Session, Depends(get_db)], conductor_id: int = 1):
    """Obtener la ruta actual del conductor"""
    # TODO: Implementar lógica real
    return
