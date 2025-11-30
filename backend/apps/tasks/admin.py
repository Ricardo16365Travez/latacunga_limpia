from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin
from .models import Task, TaskCheckpoint, TaskAssignmentHistory


@admin.register(Task)
class TaskAdmin(GISModelAdmin):
    """Admin para el modelo Task con soporte para mapas."""
    list_display = [
        'task_id', 'title', 'status', 'priority', 'assigned_to',
        'scheduled_date', 'completion_percentage', 'created_at'
    ]
    list_filter = [
        'status', 'priority', 'scheduled_date', 'created_at'
    ]
    search_fields = [
        'task_id', 'title', 'description', 'address'
    ]
    readonly_fields = [
        'task_id', 'created_by', 'created_at', 'updated_at',
        'started_at', 'completed_at', 'paused_at',
        'completion_percentage', 'checkpoints_completed', 'checkpoints_total'
    ]
    fieldsets = (
        ('Información Básica', {
            'fields': ('task_id', 'title', 'description')
        }),
        ('Relaciones', {
            'fields': ('route', 'incident', 'assigned_to', 'created_by')
        }),
        ('Estado y Prioridad', {
            'fields': ('status', 'priority', 'cancelled_reason')
        }),
        ('Ubicación', {
            'fields': ('location', 'address')
        }),
        ('Programación', {
            'fields': (
                'scheduled_date', 'scheduled_start_time', 'scheduled_end_time',
                'estimated_duration'
            )
        }),
        ('Fechas Reales', {
            'fields': ('started_at', 'completed_at', 'paused_at')
        }),
        ('Recursos', {
            'fields': ('team_size', 'equipment_needed', 'materials_needed')
        }),
        ('Progreso', {
            'fields': (
                'completion_percentage', 'checkpoints_completed', 'checkpoints_total'
            )
        }),
        ('Resultados', {
            'fields': ('result_notes', 'result_photos', 'waste_collected_kg')
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at')
        })
    )
    gis_widget_kwargs = {
        'attrs': {
            'default_lat': -0.93517,
            'default_lon': -78.61478,
            'default_zoom': 13,
        },
    }


@admin.register(TaskCheckpoint)
class TaskCheckpointAdmin(GISModelAdmin):
    """Admin para el modelo TaskCheckpoint."""
    list_display = [
        'task', 'checkpoint_order', 'name', 'is_completed',
        'completed_at', 'completed_by'
    ]
    list_filter = ['is_completed', 'requires_photo', 'completed_at']
    search_fields = ['task__task_id', 'name', 'description']
    readonly_fields = [
        'is_completed', 'completed_at', 'completed_by',
        'created_at', 'updated_at'
    ]
    fieldsets = (
        ('Información', {
            'fields': ('task', 'checkpoint_order', 'name', 'description')
        }),
        ('Ubicación', {
            'fields': ('location', 'address')
        }),
        ('Estado', {
            'fields': ('is_completed', 'completed_at', 'completed_by')
        }),
        ('Verificación', {
            'fields': (
                'requires_photo', 'photo_url', 'notes', 'verification_data'
            )
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at')
        })
    )


@admin.register(TaskAssignmentHistory)
class TaskAssignmentHistoryAdmin(admin.ModelAdmin):
    """Admin para el modelo TaskAssignmentHistory."""
    list_display = [
        'task', 'action', 'performed_by',
        'previous_assignee', 'new_assignee', 'timestamp'
    ]
    list_filter = ['action', 'timestamp']
    search_fields = [
        'task__task_id', 'notes',
        'performed_by__username', 'performed_by__email'
    ]
    readonly_fields = [
        'task', 'action', 'performed_by',
        'previous_assignee', 'new_assignee',
        'previous_status', 'new_status',
        'notes', 'metadata', 'timestamp'
    ]
    fieldsets = (
        ('Tarea', {
            'fields': ('task', 'action')
        }),
        ('Usuarios', {
            'fields': ('performed_by', 'previous_assignee', 'new_assignee')
        }),
        ('Estados', {
            'fields': ('previous_status', 'new_status')
        }),
        ('Detalles', {
            'fields': ('notes', 'metadata', 'timestamp')
        })
    )

    def has_add_permission(self, request):
        """No permitir crear registros manualmente."""
        return False

    def has_change_permission(self, request, obj=None):
        """No permitir editar registros."""
        return False

    def has_delete_permission(self, request, obj=None):
        """No permitir eliminar registros."""
        return False
