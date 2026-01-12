"""
Router para notificaciones (/api/notifications)
"""
from fastapi import APIRouter, Depends  # type: ignore[import]
from sqlalchemy.orm import Session  # type: ignore[import]
from pydantic import BaseModel  # type: ignore[import]
from typing import Annotated, List
from datetime import datetime
from app.database import get_db

router = APIRouter(prefix="/notifications", tags=["notifications"])


class Notification(BaseModel):
    id: int
    type: str = "info"
    title: str
    message: str
    read: bool = False
    created_at: datetime = datetime.utcnow()


class NotificationList(BaseModel):
    total: int
    unread: int
    notifications: List[Notification]


@router.get("/", response_model=NotificationList)
async def list_notifications(db: Annotated[Session, Depends(get_db)]):
    return {"total": 0, "unread": 0, "notifications": []}


@router.patch("/{notification_id}/read", response_model=Notification)
async def mark_read(notification_id: int, db: Annotated[Session, Depends(get_db)]):
    return Notification(
        id=notification_id,
        type="info",
        title="Notificación",
        message="Marcada como leída",
        read=True,
    )


@router.post("/read-all")
async def mark_all_read(db: Annotated[Session, Depends(get_db)]):
    return {"message": "Todas las notificaciones marcadas como leídas"}
