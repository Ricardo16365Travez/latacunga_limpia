from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField

User = get_user_model()


class Notification(models.Model):
    """
    Modelo para notificaciones del sistema.
    Soporta notificaciones push, en app y por email.
    """
    NOTIFICATION_TYPE_CHOICES = [
        ('task_assigned', 'Tarea Asignada'),
        ('task_updated', 'Tarea Actualizada'),
        ('task_completed', 'Tarea Completada'),
        ('task_cancelled', 'Tarea Cancelada'),
        ('incident_created', 'Incidencia Creada'),
        ('incident_updated', 'Incidencia Actualizada'),
        ('incident_resolved', 'Incidencia Resuelta'),
        ('route_assigned', 'Ruta Asignada'),
        ('route_updated', 'Ruta Actualizada'),
        ('checkpoint_completed', 'Checkpoint Completado'),
        ('system_alert', 'Alerta del Sistema'),
        ('message', 'Mensaje'),
        ('reminder', 'Recordatorio'),
    ]

    PRIORITY_CHOICES = [
        (1, 'Baja'),
        (2, 'Normal'),
        (3, 'Alta'),
        (4, 'Urgente'),
    ]

    DELIVERY_CHANNEL_CHOICES = [
        ('push', 'Push Notification'),
        ('in_app', 'In-App'),
        ('email', 'Email'),
        ('websocket', 'WebSocket'),
    ]

    # Identificación
    notification_id = models.CharField(max_length=100, unique=True, db_index=True)
    
    # Destinatario
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        help_text='Usuario destinatario de la notificación'
    )

    # Contenido
    notification_type = models.CharField(
        max_length=50,
        choices=NOTIFICATION_TYPE_CHOICES,
        db_index=True
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    priority = models.IntegerField(
        choices=PRIORITY_CHOICES,
        default=2,
        db_index=True
    )

    # Canales de entrega
    delivery_channels = ArrayField(
        models.CharField(max_length=20),
        default=list,
        help_text='Canales por los que se enviará la notificación'
    )

    # Referencias a objetos relacionados
    related_task_id = models.CharField(max_length=50, blank=True, db_index=True)
    related_incident_id = models.CharField(max_length=50, blank=True, db_index=True)
    related_route_id = models.IntegerField(null=True, blank=True, db_index=True)

    # Datos adicionales
    action_url = models.URLField(blank=True, help_text='URL de acción al hacer clic')
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text='Datos adicionales de la notificación'
    )
    icon = models.CharField(max_length=50, blank=True)
    image_url = models.URLField(blank=True)

    # Estado
    is_read = models.BooleanField(default=False, db_index=True)
    read_at = models.DateTimeField(null=True, blank=True)
    is_sent = models.BooleanField(default=False, db_index=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    is_delivered = models.BooleanField(default=False)
    delivered_at = models.DateTimeField(null=True, blank=True)

    # Programación
    scheduled_for = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Fecha y hora programada para envío'
    )

    # Expiración
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Fecha de expiración de la notificación'
    )

    # Auditoría
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_notifications'
    )

    # Errores de entrega
    delivery_errors = models.JSONField(
        default=dict,
        blank=True,
        help_text='Errores durante la entrega por canal'
    )
    retry_count = models.IntegerField(default=0)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['notification_type', '-created_at']),
            models.Index(fields=['is_sent', 'scheduled_for']),
            models.Index(fields=['priority', '-created_at']),
        ]
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'

    def __str__(self):
        return f"{self.notification_id} - {self.title} ({self.user.username})"

    def mark_as_read(self):
        """Marca la notificación como leída."""
        from django.utils import timezone
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])

    def mark_as_sent(self):
        """Marca la notificación como enviada."""
        from django.utils import timezone
        if not self.is_sent:
            self.is_sent = True
            self.sent_at = timezone.now()
            self.save(update_fields=['is_sent', 'sent_at'])

    def mark_as_delivered(self):
        """Marca la notificación como entregada."""
        from django.utils import timezone
        if not self.is_delivered:
            self.is_delivered = True
            self.delivered_at = timezone.now()
            self.save(update_fields=['is_delivered', 'delivered_at'])

    def is_expired(self):
        """Verifica si la notificación ha expirado."""
        from django.utils import timezone
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False


class DeviceToken(models.Model):
    """
    Modelo para tokens de dispositivos para push notifications.
    Soporta FCM (Firebase Cloud Messaging) y APNs (Apple Push Notification service).
    """
    PLATFORM_CHOICES = [
        ('android', 'Android'),
        ('ios', 'iOS'),
        ('web', 'Web'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='device_tokens'
    )
    
    # Token del dispositivo
    token = models.CharField(
        max_length=500,
        unique=True,
        db_index=True,
        help_text='Token único del dispositivo para push notifications'
    )
    platform = models.CharField(
        max_length=20,
        choices=PLATFORM_CHOICES,
        db_index=True
    )

    # Información del dispositivo
    device_id = models.CharField(
        max_length=200,
        blank=True,
        help_text='Identificador único del dispositivo'
    )
    device_name = models.CharField(max_length=200, blank=True)
    device_model = models.CharField(max_length=100, blank=True)
    os_version = models.CharField(max_length=50, blank=True)
    app_version = models.CharField(max_length=50, blank=True)

    # Estado
    is_active = models.BooleanField(default=True, db_index=True)
    last_used_at = models.DateTimeField(auto_now=True)
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)

    # Auditoría
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'device_tokens'
        ordering = ['-last_used_at']
        unique_together = ['user', 'device_id', 'platform']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['platform', 'is_active']),
            models.Index(fields=['token']),
        ]
        verbose_name = 'Token de Dispositivo'
        verbose_name_plural = 'Tokens de Dispositivos'

    def __str__(self):
        return f"{self.user.username} - {self.platform} ({self.device_name})"

    def deactivate(self):
        """Desactiva el token del dispositivo."""
        self.is_active = False
        self.save(update_fields=['is_active'])


class NotificationPreference(models.Model):
    """
    Preferencias de notificaciones por usuario.
    Permite controlar qué tipos de notificaciones recibe y por qué canales.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='notification_preferences'
    )

    # Canales habilitados globalmente
    push_enabled = models.BooleanField(default=True)
    email_enabled = models.BooleanField(default=True)
    in_app_enabled = models.BooleanField(default=True)
    websocket_enabled = models.BooleanField(default=True)

    # Preferencias por tipo de notificación
    task_notifications = models.BooleanField(default=True)
    incident_notifications = models.BooleanField(default=True)
    route_notifications = models.BooleanField(default=True)
    system_notifications = models.BooleanField(default=True)
    message_notifications = models.BooleanField(default=True)

    # Horario de no molestar
    do_not_disturb = models.BooleanField(default=False)
    dnd_start_time = models.TimeField(null=True, blank=True)
    dnd_end_time = models.TimeField(null=True, blank=True)

    # Configuración adicional
    sound_enabled = models.BooleanField(default=True)
    vibration_enabled = models.BooleanField(default=True)
    badge_enabled = models.BooleanField(default=True)

    # Agrupación
    group_notifications = models.BooleanField(default=True)
    max_notifications_per_day = models.IntegerField(default=50)

    # Auditoría
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'notification_preferences'
        verbose_name = 'Preferencia de Notificación'
        verbose_name_plural = 'Preferencias de Notificaciones'

    def __str__(self):
        return f"Preferencias de {self.user.username}"

    def is_channel_enabled(self, channel):
        """Verifica si un canal está habilitado."""
        channel_map = {
            'push': self.push_enabled,
            'email': self.email_enabled,
            'in_app': self.in_app_enabled,
            'websocket': self.websocket_enabled,
        }
        return channel_map.get(channel, False)

    def is_notification_type_enabled(self, notification_type):
        """Verifica si un tipo de notificación está habilitado."""
        if notification_type.startswith('task_'):
            return self.task_notifications
        elif notification_type.startswith('incident_'):
            return self.incident_notifications
        elif notification_type.startswith('route_'):
            return self.route_notifications
        elif notification_type == 'system_alert':
            return self.system_notifications
        elif notification_type == 'message':
            return self.message_notifications
        return True

    def is_in_dnd_period(self):
        """Verifica si está en horario de no molestar."""
        if not self.do_not_disturb or not self.dnd_start_time or not self.dnd_end_time:
            return False
        
        from django.utils import timezone
        now_time = timezone.now().time()
        
        if self.dnd_start_time < self.dnd_end_time:
            return self.dnd_start_time <= now_time <= self.dnd_end_time
        else:  # Cruza la medianoche
            return now_time >= self.dnd_start_time or now_time <= self.dnd_end_time
