"""
Modelos para el sistema de incidencias reportadas por ciudadanos.
Compatible con el sistema de eventos RabbitMQ del latacunga_clean_app.
"""

import uuid
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from django.utils import timezone
from django.conf import settings


class IncidentType(models.TextChoices):
    """Tipos de incidentes que se pueden reportar"""
    PUNTO_ACOPIO = 'punto_acopio', 'Punto de Acopio'
    ZONA_CRITICA = 'zona_critica', 'Zona Crítica'
    ANIMAL_MUERTO = 'animal_muerto', 'Animal Fallecido'
    ZONA_RECICLAJE = 'zona_reciclaje', 'Zona de Reciclaje'


class IncidentStatus(models.TextChoices):
    """Estados del flujo de vida de un incidente"""
    NO_VALIDADO = 'incidente_no_validado', 'No Validado'
    PENDIENTE = 'incidente_pendiente', 'Pendiente Validación'
    VALIDO = 'incidente_valido', 'Válido'
    RECHAZADO = 'incidente_rechazado', 'Rechazado'
    CONVERTIDO_TAREA = 'convertido_en_tarea', 'Convertido en Tarea'
    CERRADO = 'cerrado', 'Cerrado'


class Incident(models.Model):
    """
    Modelo principal para incidentes reportados.
    Compatible con incident-service de Go.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Información del reportante
    reporter_kind = models.CharField(
        max_length=20,
        default='ciudadano',
        help_text='Tipo de reportante: ciudadano, operador, sistema'
    )
    reporter_id = models.UUIDField(
        null=True,
        blank=True,
        help_text='ID del usuario que reportó'
    )
    
    # Datos del incidente
    incident_type = models.CharField(
        max_length=30,
        choices=IncidentType.choices,
        db_column='incident_type',
        help_text='Tipo de incidente reportado'
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text='Descripción detallada del incidente'
    )
    
    # Ubicación geográfica (PostGIS)
    location = models.PointField(
        help_text='Ubicación geográfica del incidente (lat, lon)',
        srid=4326  # WGS84
    )
    address = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text='Dirección aproximada'
    )
    
    # Estado y seguimiento
    status = models.CharField(
        max_length=30,
        choices=IncidentStatus.choices,
        default=IncidentStatus.NO_VALIDADO,
        help_text='Estado actual del incidente'
    )
    
    # Foto URL simple
    photo_url = models.TextField(
        blank=True,
        null=True,
        help_text='URL de foto del incidente'
    )
    
    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'incidents'
        verbose_name = 'Incidente'
        verbose_name_plural = 'Incidentes'
        ordering = ['-created_at']
    
    def __str__(self):
        # Mostrar tipo y un fragmento de la descripción o la dirección
        tipo = getattr(self, 'incident_type', '')
        tipo_display = self.get_incident_type_display() if tipo else ''
        preview = (self.description or self.address or '')[:50]
        return f"{tipo_display} - {preview}"
    
    @property
    def latitude(self):
        """Retorna la latitud del punto"""
        return self.location.y if self.location else None
    
    @property
    def longitude(self):
        """Retorna la longitud del punto"""
        return self.location.x if self.location else None
    
    def to_event_payload(self):
        """
        Convierte el incidente a payload para eventos RabbitMQ.
        Incluye los campos disponibles del modelo actual.
        """
        return {
            'incident_id': str(self.id),
            'reporter_kind': self.reporter_kind,
            'reporter_id': str(self.reporter_id) if self.reporter_id else None,
            'incident_type': self.incident_type,
            'description': self.description,
            'location': {
                'latitude': self.latitude,
                'longitude': self.longitude,
            },
            'address': self.address,
            'status': self.status,
            'photo_url': self.photo_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class IncidentAttachment(models.Model):
    """Archivos/fotos adjuntas a un incidente"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    incident = models.ForeignKey(
        Incident,
        on_delete=models.CASCADE,
        related_name='attachments'
    )
    file_url = models.URLField(
        max_length=500,
        help_text='URL del archivo en storage (S3, Cloudinary, etc.)'
    )
    mime_type = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='Tipo MIME del archivo'
    )
    size_bytes = models.BigIntegerField(
        blank=True,
        null=True,
        help_text='Tamaño del archivo en bytes'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'incident_attachments'
        verbose_name = 'Adjunto de Incidente'
        verbose_name_plural = 'Adjuntos de Incidentes'
        ordering = ['-created_at']
    
    def __str__(self):
        preview = (self.incident.description or self.incident.address or '')[:30]
        return f"Adjunto {self.id} - {preview}"


class IncidentEvent(models.Model):
    """Registro de eventos/auditoría de cambios en incidentes"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    incident = models.ForeignKey(
        Incident,
        on_delete=models.CASCADE,
        related_name='events'
    )
    event_type = models.CharField(
        max_length=50,
        help_text='Tipo de evento: incidente_creado, estado_actualizado, etc.'
    )
    payload = models.JSONField(
        blank=True,
        null=True,
        help_text='Datos adicionales del evento'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'incident_events'
        verbose_name = 'Evento de Incidente'
        verbose_name_plural = 'Eventos de Incidentes'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['incident', '-created_at']),
            models.Index(fields=['event_type']),
        ]
    
    def __str__(self):
        preview = (self.incident.description or self.incident.address or '')[:30]
        return f"{self.event_type} - {preview}"


class OutboxEvent(models.Model):
    """
    Patrón Transactional Outbox para garantizar entrega de eventos.
    Los eventos se guardan primero en DB y luego se publican a RabbitMQ.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    aggregate_type = models.CharField(
        max_length=50,
        help_text='Tipo de agregado: incident, task, etc.'
    )
    aggregate_id = models.UUIDField(
        help_text='ID del agregado relacionado'
    )
    event_type = models.CharField(
        max_length=50,
        help_text='Tipo de evento a publicar'
    )
    payload = models.JSONField(
        help_text='Payload completo del evento'
    )
    routing_key = models.CharField(
        max_length=100,
        help_text='Routing key para RabbitMQ'
    )
    status = models.CharField(
        max_length=20,
        default='pending',
        choices=[
            ('pending', 'Pendiente'),
            ('published', 'Publicado'),
            ('failed', 'Fallido'),
        ]
    )
    attempts = models.IntegerField(
        default=0,
        help_text='Número de intentos de publicación'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    published_at = models.DateTimeField(blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'outbox_events'
        verbose_name = 'Evento Outbox'
        verbose_name_plural = 'Eventos Outbox'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['aggregate_type', 'aggregate_id']),
        ]
    
    def __str__(self):
        return f"{self.event_type} - {self.status}"
