import pika
import json
import logging
from datetime import datetime
from django.conf import settings
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class RabbitMQService:
    """Servicio para manejar mensajería con RabbitMQ."""
    
    def __init__(self):
        self.connection = None
        self.channel = None
        self._connect()
    
    def _connect(self):
        """Establecer conexión con RabbitMQ."""
        try:
            # Crear credenciales
            credentials = pika.PlainCredentials('tesis', 'tesis')
            
            # Parámetros de conexión
            parameters = pika.ConnectionParameters(
                host='rabbitmq',
                credentials=credentials
            )
            
            # Establecer conexión
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            logger.info("Conexión establecida con RabbitMQ")
            
        except Exception as e:
            logger.error(f"Error conectando a RabbitMQ: {e}")
            self.connection = None
            self.channel = None
    
    def _ensure_connection(self):
        """Asegurar que la conexión esté activa."""
        if not self.connection or self.connection.is_closed:
            self._connect()
    
    def publish_message(self, exchange: str, routing_key: str, message: Dict[Any, Any], exchange_type: str = 'direct'):
        """Publicar un mensaje en RabbitMQ."""
        try:
            self._ensure_connection()
            
            if not self.channel:
                logger.error("No hay canal disponible para publicar mensaje")
                return False
            
            # Declarar exchange si no existe
            self.channel.exchange_declare(
                exchange=exchange,
                exchange_type=exchange_type,
                durable=True
            )
            
            # Preparar mensaje
            message_body = json.dumps(message, default=str)
            
            # Publicar mensaje
            self.channel.basic_publish(
                exchange=exchange,
                routing_key=routing_key,
                body=message_body,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Hacer el mensaje persistente
                    content_type='application/json',
                    timestamp=int(datetime.now().timestamp())
                )
            )
            
            logger.info(f"Mensaje publicado: {exchange}/{routing_key}")
            return True
            
        except Exception as e:
            logger.error(f"Error publicando mensaje: {e}")
            return False
    
    def publish_user_login_event(self, user):
        """Publicar evento de login de usuario."""
        message = {
            'event_type': 'user.login',
            'event_id': str(user.id),
            'timestamp': datetime.now().isoformat(),
            'data': {
                'user_id': str(user.id),
                'email': user.email,
                'phone': user.phone,
                'role': user.role,
                'display_name': user.get_full_name(),
                'login_time': datetime.now().isoformat()
            }
        }
        
        return self.publish_message(
            exchange='incidente.cmd',
            routing_key='auditoria.login',
            message=message
        )
    
    def publish_user_registration_event(self, user):
        """Publicar evento de registro de usuario."""
        message = {
            'event_type': 'user.registered',
            'event_id': str(user.id),
            'timestamp': datetime.now().isoformat(),
            'data': {
                'user_id': str(user.id),
                'email': user.email,
                'phone': user.phone,
                'role': user.role,
                'display_name': user.get_full_name(),
                'registration_time': datetime.now().isoformat()
            }
        }
        
        return self.publish_message(
            exchange='incidente.cmd',
            routing_key='auditoria.registration',
            message=message
        )
    
    def publish_otp_sent_event(self, phone: str, purpose: str):
        """Publicar evento de envío de OTP."""
        message = {
            'event_type': 'otp.sent',
            'event_id': phone,
            'timestamp': datetime.now().isoformat(),
            'data': {
                'phone': phone,
                'purpose': purpose,
                'sent_time': datetime.now().isoformat()
            }
        }
        
        return self.publish_message(
            exchange='incidente.cmd',
            routing_key='auditoria.otp',
            message=message
        )
    
    def publish_report_created_event(self, report_data):
        """Publicar evento de reporte creado."""
        message = {
            'event_type': 'report.created',
            'event_id': report_data.get('id'),
            'timestamp': datetime.now().isoformat(),
            'data': report_data
        }
        
        return self.publish_message(
            exchange='incidente.cmd',
            routing_key='validacion',
            message=message
        )
    
    def publish_task_assigned_event(self, task_data):
        """Publicar evento de tarea asignada."""
        message = {
            'event_type': 'task.assigned',
            'event_id': task_data.get('id'),
            'timestamp': datetime.now().isoformat(),
            'data': task_data
        }
        
        return self.publish_message(
            exchange='incidente.validado.fanout',
            routing_key='',
            message=message,
            exchange_type='fanout'
        )
    
    def publish_location_update_event(self, location_data):
        """Publicar evento de actualización de ubicación."""
        message = {
            'event_type': 'location.updated',
            'event_id': location_data.get('actor_id'),
            'timestamp': datetime.now().isoformat(),
            'data': location_data
        }
        
        return self.publish_message(
            exchange='incidente.cmd',
            routing_key='ubicacion',
            message=message
        )
    
    def close(self):
        """Cerrar conexión con RabbitMQ."""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            logger.info("Conexión con RabbitMQ cerrada")
    
    def __del__(self):
        """Destructor para cerrar conexión."""
        self.close()