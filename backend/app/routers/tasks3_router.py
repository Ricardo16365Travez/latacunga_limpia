from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional, Annotated
from datetime import datetime
from app.database import get_db
from app.models import Task as TaskModel
from pydantic import BaseModel

router = APIRouter()

class TaskOut3(BaseModel):
    task_id: str
    titulo: str
    descripcion: Optional[str] = None
    tipo: str
    prioridad: str
    estado: str
    progreso: int
    fecha_limite: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    conductor_id: Optional[int] = None
    ruta_id: Optional[int] = None

    @classmethod
    def from_orm(cls, obj):
        d = obj.__dict__.copy()
        d['task_id'] = str(d['id']) if d.get('id') is not None else None
        d.pop('id', None)
        return cls(**d)

    class Config:
        from_attributes = True

@router.get("/tasks3", response_model=List[TaskOut3])
async def list_tasks3(db: Annotated[Session, Depends(get_db)]):
    tasks = db.query(TaskModel).all()
    return [TaskOut3.from_orm(t) for t in tasks]
