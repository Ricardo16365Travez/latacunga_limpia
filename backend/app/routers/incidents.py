"""
Router alias en inglés para incidencias (/api/incidents)
"""
from fastapi import APIRouter, Depends  # type: ignore[import]
from sqlalchemy.orm import Session  # type: ignore[import]
from pydantic import BaseModel  # type: ignore[import]
from typing import Annotated, List
from datetime import datetime
from app.database import get_db

router = APIRouter(prefix="/incidents", tags=["incidents"])


class Incident(BaseModel):
    id: int
    title: str
    description: str
    status: str = "open"
    priority: str = "medium"
    created_at: datetime = datetime.utcnow()


class IncidentList(BaseModel):
    total: int
    incidents: List[Incident]


@router.get("/", response_model=IncidentList)
async def list_incidents(db: Annotated[Session, Depends(get_db)]):
    """Lista de incidencias (alias)"""
    return {
        "total": 0,
        "incidents": [],
    }


@router.post("/", response_model=Incident)
async def create_incident(payload: dict, db: Annotated[Session, Depends(get_db)]):
    """Crear incidencia (alias)"""
    return Incident(
        id=1,
        title=payload.get("title", "Nueva incidencia"),
        description=payload.get("description", ""),
        status=payload.get("status", "open"),
        priority=payload.get("priority", "medium"),
    )


@router.get("/{incident_id}", response_model=Incident)
async def get_incident(incident_id: int, db: Annotated[Session, Depends(get_db)]):
    """Obtener incidencia (alias)"""
    return Incident(
        id=incident_id,
        title="Incidencia demo",
        description="Detalle no disponible",
        status="open",
        priority="medium",
    )


@router.patch("/{incident_id}", response_model=Incident)
async def update_incident(incident_id: int, payload: dict, db: Annotated[Session, Depends(get_db)]):
    """Actualizar incidencia (alias)"""
    return Incident(
        id=incident_id,
        title=payload.get("title", "Incidencia demo"),
        description=payload.get("description", "Detalle no disponible"),
        status=payload.get("status", "open"),
        priority=payload.get("priority", "medium"),
    )


@router.delete("/{incident_id}")
async def delete_incident(incident_id: int, db: Annotated[Session, Depends(get_db)]):
    """Eliminar incidencia (alias)"""
    return {"message": "Incidencia eliminada", "id": incident_id}
