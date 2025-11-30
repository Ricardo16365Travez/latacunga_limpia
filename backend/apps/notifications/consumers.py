import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

User = get_user_model()
logger = logging.getLogger(__name__)


class NotificationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer para notificaciones en tiempo real.
    
    Maneja conexiones WebSocket para enviar notificaciones push
    a clientes conectados.
    """

    async def connect(self):
        """Maneja la conexión del WebSocket."""
        # Obtener usuario de la sesión
        self.user = self.scope['user']
        
        if self.user.is_anonymous:
            await self.close()
            return

        # Grupo único por usuario
        self.user_group_name = f'notifications_user_{self.user.id}'

        # Unirse al grupo de notificaciones del usuario
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )

        await self.accept()
        logger.info(f"WebSocket conectado para usuario: {self.user.username}")

        # Enviar mensaje de bienvenida
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Conexión establecida con servidor de notificaciones',
            'user_id': self.user.id
        }))

    async def disconnect(self, close_code):
        """Maneja la desconexión del WebSocket."""
        if hasattr(self, 'user_group_name'):
            # Salir del grupo de notificaciones
            await self.channel_layer.group_discard(
                self.user_group_name,
                self.channel_name
            )
            logger.info(f"WebSocket desconectado para usuario: {self.user.username}")

    async def receive(self, text_data):
        """
        Maneja mensajes recibidos del cliente.
        Puede usarse para marcar notificaciones como leídas.
        """
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            if message_type == 'mark_as_read':
                notification_id = data.get('notification_id')
                await self.mark_notification_as_read(notification_id)
                
                await self.send(text_data=json.dumps({
                    'type': 'notification_read',
                    'notification_id': notification_id,
                    'status': 'success'
                }))

            elif message_type == 'ping':
                # Responder a ping para mantener conexión viva
                await self.send(text_data=json.dumps({
                    'type': 'pong'
                }))

        except json.JSONDecodeError:
            logger.error("Error al decodificar mensaje JSON")
        except Exception as e:
            logger.error(f"Error en receive: {str(e)}")

    async def notification_message(self, event):
        """
        Maneja mensajes de notificación enviados al grupo.
        Este método se llama cuando se envía un mensaje al grupo del usuario.
        """
        # Enviar mensaje al WebSocket
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'notification': event['notification']
        }))

    async def task_update(self, event):
        """Maneja actualizaciones de tareas."""
        await self.send(text_data=json.dumps({
            'type': 'task_update',
            'data': event['data']
        }))

    async def incident_update(self, event):
        """Maneja actualizaciones de incidencias."""
        await self.send(text_data=json.dumps({
            'type': 'incident_update',
            'data': event['data']
        }))

    async def route_update(self, event):
        """Maneja actualizaciones de rutas."""
        await self.send(text_data=json.dumps({
            'type': 'route_update',
            'data': event['data']
        }))

    async def system_alert(self, event):
        """Maneja alertas del sistema."""
        await self.send(text_data=json.dumps({
            'type': 'system_alert',
            'alert': event['alert']
        }))

    @database_sync_to_async
    def mark_notification_as_read(self, notification_id):
        """Marca una notificación como leída."""
        from .models import Notification
        try:
            notification = Notification.objects.get(
                notification_id=notification_id,
                user=self.user
            )
            notification.mark_as_read()
            return True
        except Notification.DoesNotExist:
            logger.warning(f"Notificación {notification_id} no encontrada")
            return False


class TeamNotificationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer para notificaciones de equipo/grupo.
    
    Permite enviar notificaciones a todos los miembros de un equipo
    o grupo de trabajo.
    """

    async def connect(self):
        """Maneja la conexión del WebSocket."""
        self.user = self.scope['user']
        
        if self.user.is_anonymous:
            await self.close()
            return

        # Obtener ID del equipo de los parámetros de URL
        self.team_id = self.scope['url_route']['kwargs'].get('team_id')
        
        if not self.team_id:
            await self.close()
            return

        # Verificar que el usuario pertenece al equipo
        is_member = await self.check_team_membership()
        if not is_member:
            await self.close()
            return

        # Grupo del equipo
        self.team_group_name = f'team_notifications_{self.team_id}'

        # Unirse al grupo del equipo
        await self.channel_layer.group_add(
            self.team_group_name,
            self.channel_name
        )

        await self.accept()
        logger.info(f"Usuario {self.user.username} conectado al equipo {self.team_id}")

    async def disconnect(self, close_code):
        """Maneja la desconexión del WebSocket."""
        if hasattr(self, 'team_group_name'):
            await self.channel_layer.group_discard(
                self.team_group_name,
                self.channel_name
            )
            logger.info(f"Usuario {self.user.username} desconectado del equipo")

    async def receive(self, text_data):
        """Maneja mensajes recibidos del cliente."""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            if message_type == 'team_message':
                # Broadcast mensaje a todo el equipo
                await self.channel_layer.group_send(
                    self.team_group_name,
                    {
                        'type': 'team_message',
                        'message': data.get('message'),
                        'sender': self.user.username
                    }
                )

        except json.JSONDecodeError:
            logger.error("Error al decodificar mensaje JSON")
        except Exception as e:
            logger.error(f"Error en receive: {str(e)}")

    async def team_message(self, event):
        """Maneja mensajes del equipo."""
        await self.send(text_data=json.dumps({
            'type': 'team_message',
            'message': event['message'],
            'sender': event['sender']
        }))

    async def team_notification(self, event):
        """Maneja notificaciones del equipo."""
        await self.send(text_data=json.dumps({
            'type': 'team_notification',
            'notification': event['notification']
        }))

    @database_sync_to_async
    def check_team_membership(self):
        """Verifica si el usuario pertenece al equipo."""
        # TODO: Implementar lógica de verificación de membresía
        # Por ahora, retornar True para permitir conexiones
        return True
