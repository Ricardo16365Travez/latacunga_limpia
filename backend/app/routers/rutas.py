"""
Router de rutas para FastAPI
"""
from fastapi import APIRouter, Depends, HTTPException, status  # type: ignore[import]
from sqlalchemy.orm import Session  # type: ignore[import]
from pydantic import BaseModel  # type: ignore[import]
from typing import Annotated, List, Optional
from datetime import datetime
from app.database import get_db
from app.models import Ruta

router = APIRouter(prefix="/rutas", tags=["rutas"])


class RutaResponse(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str] = None
    distancia_km: float
    tiempo_estimado_minutos: int
    estado: str
    created_at: datetime

    class Config:
        from_attributes = True


class RutaCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    distancia_km: float
    tiempo_estimado_minutos: int


@router.get("/", response_model=List[RutaResponse])
async def listar_rutas(db: Annotated[Session, Depends(get_db)]):
    """Listar todas las rutas"""
    return db.query(Ruta).all()


@router.post("/", response_model=RutaResponse, status_code=status.HTTP_201_CREATED)
async def crear_ruta(ruta: RutaCreate, db: Annotated[Session, Depends(get_db)]):
    """Crear nueva ruta"""
    new_ruta = Ruta(
        nombre=ruta.nombre,
        descripcion=ruta.descripcion,
        distancia_km=ruta.distancia_km,
        tiempo_estimado_minutos=ruta.tiempo_estimado_minutos,
        estado="activa"
    )
    db.add(new_ruta)
    db.commit()
    db.refresh(new_ruta)
    return new_ruta


@router.get("/{ruta_id}", response_model=RutaResponse)
async def obtener_ruta(ruta_id: int, db: Annotated[Session, Depends(get_db)]):
    """Obtener una ruta específica"""
    ruta = db.query(Ruta).filter(Ruta.id == ruta_id).first()
    if not ruta:
        raise HTTPException(status_code=404, detail="Ruta no encontrada")
    return ruta


@router.patch("/{ruta_id}", response_model=RutaResponse)
async def actualizar_ruta(
    ruta_id: int,
    payload: dict,
    db: Annotated[Session, Depends(get_db)]
):
    """Actualizar una ruta"""
    ruta = db.query(Ruta).filter(Ruta.id == ruta_id).first()
    if not ruta:
        raise HTTPException(status_code=404, detail="Ruta no encontrada")

    for key, value in payload.items():
        if hasattr(ruta, key) and key != "id":
            setattr(ruta, key, value)

    db.commit()
    db.refresh(ruta)
    return ruta


@router.delete("/{ruta_id}")
async def eliminar_ruta(ruta_id: int, db: Annotated[Session, Depends(get_db)]):
    """Eliminar una ruta"""
    ruta = db.query(Ruta).filter(Ruta.id == ruta_id).first()
    if not ruta:
        raise HTTPException(status_code=404, detail="Ruta no encontrada")

    db.delete(ruta)
    db.commit()
    return {"mensaje": "Ruta eliminada"}


@router.get("/zona/{zona}", response_model=List[RutaResponse])
async def obtener_rutas_por_zona(zona: str, db: Annotated[Session, Depends(get_db)]):
    """Obtener rutas por zona"""
    # TODO: Cuando Ruta tenga campo 'zona'
    return db.query(Ruta).all()
