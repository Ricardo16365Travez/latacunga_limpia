"""
Router para tracking GPS en tiempo real de camiones recolectores
Usa WebSocket para streaming de posiciones
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Annotated, List, Dict, Optional
from datetime import datetime
from pydantic import BaseModel
import json

from app.database import get_db

router = APIRouter(prefix="/tracking", tags=["tracking"])


# ============================================
# MODELOS PYDANTIC
# ============================================

class TrackingUpdate(BaseModel):
    """Update de posición GPS del camión"""
    ejecucion_id: int
    lat: float
    lon: float
    velocidad: Optional[float] = None
    timestamp: Optional[datetime] = None


class TrackingResponse(BaseModel):
    """Respuesta de tracking activo"""
    ejecucion_id: int
    conductor_nombre: str
    camion_placa: str
    sector: str
    lat: float
    lon: float
    velocidad: Optional[float]
    timestamp: datetime
    estado: str


# ============================================
# GESTOR DE CONEXIONES WEBSOCKET
# ============================================

class ConnectionManager:
    """Administra conexiones WebSocket activas"""
    
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, ejecucion_id: int):
        """Conectar cliente a una ejecución específica"""
        await websocket.accept()
        if ejecucion_id not in self.active_connections:
            self.active_connections[ejecucion_id] = []
        self.active_connections[ejecucion_id].append(websocket)
    
    def disconnect(self, websocket: WebSocket, ejecucion_id: int):
        """Desconectar cliente"""
        if ejecucion_id in self.active_connections:
            self.active_connections[ejecucion_id].remove(websocket)
            if not self.active_connections[ejecucion_id]:
                del self.active_connections[ejecucion_id]
    
    async def broadcast(self, ejecucion_id: int, message: dict):
        """Enviar mensaje a todos los clientes conectados a una ejecución"""
        if ejecucion_id in self.active_connections:
            for connection in self.active_connections[ejecucion_id]:
                try:
                    await connection.send_json(message)
                except:
                    pass

manager = ConnectionManager()


# ============================================
# ENDPOINTS REST
# ============================================

@router.get("/activos", response_model=List[TrackingResponse])
async def obtener_trackings_activos(db: Annotated[Session, Depends(get_db)]):
    """
    Obtener todas las ejecuciones actualmente en curso con última posición GPS
    Mock endpoint - en producción conecta con la BD de horarios
    """
    # Por ahora retornar lista vacía
    # En producción, esto consultaría la tabla de ejecuciones_horario
    return []


@router.post("/actualizar")
async def actualizar_posicion(
    update: TrackingUpdate,
    db: Annotated[Session, Depends(get_db)]
):
    """
    Endpoint REST para actualizar posición GPS (alternativa a WebSocket)
    Usado por app móvil del conductor
    """
    # Broadcast a clientes conectados vía WebSocket
    await manager.broadcast(update.ejecucion_id, {
        "type": "position_update",
        "ejecucion_id": update.ejecucion_id,
        "lat": update.lat,
        "lon": update.lon,
        "velocidad": update.velocidad,
        "timestamp": (update.timestamp or datetime.utcnow()).isoformat()
    })
    
    return {"status": "ok", "message": "Posición actualizada"}


@router.get("/ruta/{ejecucion_id}")
async def obtener_ruta_recorrida(
    ejecucion_id: int,
    db: Annotated[Session, Depends(get_db)]
):
    """
    Obtener todos los puntos GPS de una ejecución (ruta completa recorrida)
    """
    # Mock - retornar lista vacía
    # En producción consultaría puntos_tracking_horario
    return {"ejecucion_id": ejecucion_id, "puntos": []}


# ============================================
# WEBSOCKET ENDPOINTS
# ============================================

@router.websocket("/ws/{ejecucion_id}")
async def websocket_tracking(
    websocket: WebSocket,
    ejecucion_id: int
):
    """
    WebSocket para streaming en tiempo real de posiciones GPS
    
    Conectarse: ws://localhost:8000/api/tracking/ws/{ejecucion_id}
    
    Mensajes enviados por el servidor:
    {
        "type": "position_update",
        "ejecucion_id": 123,
        "lat": -0.933,
        "lon": -78.617,
        "velocidad": 25.5,
        "timestamp": "2026-01-04T10:30:00"
    }
    """
    await manager.connect(websocket, ejecucion_id)
    
    try:
        # Mantener conexión abierta y escuchar
        while True:
            data = await websocket.receive_text()
            # Cliente puede enviar "ping" para mantener viva la conexión
            if data == "ping":
                await websocket.send_text("pong")
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, ejecucion_id)
    except Exception as e:
        manager.disconnect(websocket, ejecucion_id)
        print(f"Error WebSocket: {e}")
