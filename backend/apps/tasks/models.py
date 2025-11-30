from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.gis.db import models as gis_models
from apps.routes.models import Route
from apps.incidents.models import Incident

User = get_user_model()


class Task(models.Model):
    """
    Modelo para tareas de limpieza asignadas a trabajadores.
    Una tarea puede estar asociada a una ruta optimizada y/o incidencias reportadas.
    """
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('assigned', 'Asignada'),
        ('in_progress', 'En Progreso'),
        ('paused', 'Pausada'),
        ('completed', 'Completada'),
        ('cancelled', 'Cancelada'),
    ]

    PRIORITY_CHOICES = [
        (1, 'Muy Baja'),
        (2, 'Baja'),
        (3, 'Normal'),
        (4, 'Alta'),
        (5, 'Urgente'),
    ]

    # Identificación
    task_id = models.CharField(max_length=50, unique=True, db_index=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Relaciones
    route = models.ForeignKey(
        Route,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks',
        help_text='Ruta asociada a esta tarea'
    )
    incident = models.ForeignKey(
        Incident,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks',
        help_text='Incidencia que generó esta tarea'
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_tasks'
    )

    # Estado y prioridad
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True
    )
    priority = models.IntegerField(
        choices=PRIORITY_CHOICES,
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    # Localización
    location = gis_models.PointField(
        null=True,
        blank=True,
        help_text='Ubicación específica de la tarea'
    )
    address = models.CharField(max_length=500, blank=True)

    # Fechas y tiempos
    scheduled_date = models.DateField(
        null=True,
        blank=True,
        help_text='Fecha programada para realizar la tarea'
    )
    scheduled_start_time = models.TimeField(
        null=True,
        blank=True,
        help_text='Hora de inicio programada'
    )
    scheduled_end_time = models.TimeField(
        null=True,
        blank=True,
        help_text='Hora de finalización programada'
    )
    estimated_duration = models.IntegerField(
        default=30,
        help_text='Duración estimada en minutos'
    )

    # Fechas reales
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    paused_at = models.DateTimeField(null=True, blank=True)

    # Recursos
    team_size = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text='Número de trabajadores necesarios'
    )
    equipment_needed = models.JSONField(
        default=list,
        blank=True,
        help_text='Lista de equipamiento necesario'
    )
    materials_needed = models.JSONField(
        default=list,
        blank=True,
        help_text='Lista de materiales necesarios'
    )

    # Progreso
    completion_percentage = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    checkpoints_completed = models.IntegerField(default=0)
    checkpoints_total = models.IntegerField(default=0)

    # Resultados
    result_notes = models.TextField(blank=True)
    result_photos = models.JSONField(
        default=list,
        blank=True,
        help_text='URLs de fotos del resultado'
    )
    waste_collected_kg = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Cantidad de residuos recolectados en kg'
    )

    # Auditoría
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cancelled_reason = models.TextField(blank=True)

    class Meta:
        db_table = 'tasks'
        ordering = ['-priority', 'scheduled_date', 'scheduled_start_time']
        indexes = [
            models.Index(fields=['status', 'scheduled_date']),
            models.Index(fields=['assigned_to', 'status']),
            models.Index(fields=['priority', 'status']),
            models.Index(fields=['created_at']),
        ]
        verbose_name = 'Tarea'
        verbose_name_plural = 'Tareas'

    def __str__(self):
        return f"{self.task_id} - {self.title} ({self.get_status_display()})"

    def update_completion_percentage(self):
        """Actualiza el porcentaje de completitud basado en checkpoints."""
        if self.checkpoints_total > 0:
            self.completion_percentage = int(
                (self.checkpoints_completed / self.checkpoints_total) * 100
            )
            self.save(update_fields=['completion_percentage'])


class TaskCheckpoint(models.Model):
    """
    Puntos de control dentro de una tarea para seguimiento detallado del progreso.
    """
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='checkpoints'
    )
    checkpoint_order = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text='Orden del checkpoint en la secuencia'
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Localización del checkpoint
    location = gis_models.PointField(
        null=True,
        blank=True,
        help_text='Ubicación del punto de control'
    )
    address = models.CharField(max_length=500, blank=True)

    # Estado
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    completed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='completed_checkpoints'
    )

    # Verificación
    requires_photo = models.BooleanField(default=False)
    photo_url = models.URLField(blank=True)
    notes = models.TextField(blank=True)
    verification_data = models.JSONField(
        default=dict,
        blank=True,
        help_text='Datos adicionales de verificación'
    )

    # Auditoría
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'task_checkpoints'
        ordering = ['task', 'checkpoint_order']
        unique_together = ['task', 'checkpoint_order']
        indexes = [
            models.Index(fields=['task', 'is_completed']),
            models.Index(fields=['completed_at']),
        ]
        verbose_name = 'Checkpoint de Tarea'
        verbose_name_plural = 'Checkpoints de Tareas'

    def __str__(self):
        status = "✓" if self.is_completed else "○"
        return f"{status} {self.task.task_id} - CP{self.checkpoint_order}: {self.name}"

    def mark_completed(self, user):
        """Marca el checkpoint como completado."""
        from django.utils import timezone
        
        self.is_completed = True
        self.completed_at = timezone.now()
        self.completed_by = user
        self.save()

        # Actualizar contador de checkpoints de la tarea
        task = self.task
        task.checkpoints_completed = task.checkpoints.filter(
            is_completed=True
        ).count()
        task.checkpoints_total = task.checkpoints.count()
        task.update_completion_percentage()


class TaskAssignmentHistory(models.Model):
    """
    Historial de asignaciones de tareas para auditoría y seguimiento.
    """
    ACTION_CHOICES = [
        ('created', 'Creada'),
        ('assigned', 'Asignada'),
        ('reassigned', 'Reasignada'),
        ('unassigned', 'Desasignada'),
        ('started', 'Iniciada'),
        ('paused', 'Pausada'),
        ('resumed', 'Reanudada'),
        ('completed', 'Completada'),
        ('cancelled', 'Cancelada'),
    ]

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='history'
    )
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        db_index=True
    )
    performed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='task_actions'
    )
    previous_assignee = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='previous_assignments'
    )
    new_assignee = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='new_assignments'
    )
    previous_status = models.CharField(max_length=20, blank=True)
    new_status = models.CharField(max_length=20, blank=True)
    notes = models.TextField(blank=True)
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text='Datos adicionales de la acción'
    )
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'task_assignments_history'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['task', '-timestamp']),
            models.Index(fields=['performed_by', '-timestamp']),
            models.Index(fields=['action', '-timestamp']),
        ]
        verbose_name = 'Historial de Asignación'
        verbose_name_plural = 'Historial de Asignaciones'

    def __str__(self):
        return f"{self.task.task_id} - {self.get_action_display()} @ {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
