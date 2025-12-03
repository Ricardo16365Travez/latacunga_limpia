from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from django.contrib.auth import get_user_model
from .models import Task, TaskCheckpoint, TaskAssignmentHistory

User = get_user_model()


class TaskCheckpointSerializer(serializers.ModelSerializer):
    """Serializer para checkpoints de tareas."""
    completed_by_name = serializers.CharField(
        source='completed_by.get_full_name',
        read_only=True
    )
    location_lat = serializers.SerializerMethodField()
    location_lon = serializers.SerializerMethodField()

    class Meta:
        model = TaskCheckpoint
        fields = [
            'id', 'task', 'checkpoint_order', 'name', 'description',
            'location', 'location_lat', 'location_lon', 'address',
            'is_completed', 'completed_at', 'completed_by', 'completed_by_name',
            'requires_photo', 'photo_url', 'notes', 'verification_data',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'completed_at', 'completed_by']

    def get_location_lat(self, obj):
        if obj.location:
            return obj.location.y
        return None

    def get_location_lon(self, obj):
        if obj.location:
            return obj.location.x
        return None


class TaskAssignmentHistorySerializer(serializers.ModelSerializer):
    """Serializer para historial de asignaciones."""
    performed_by_name = serializers.CharField(
        source='performed_by.get_full_name',
        read_only=True
    )
    previous_assignee_name = serializers.CharField(
        source='previous_assignee.get_full_name',
        read_only=True
    )
    new_assignee_name = serializers.CharField(
        source='new_assignee.get_full_name',
        read_only=True
    )
    action_display = serializers.CharField(source='get_action_display', read_only=True)

    class Meta:
        model = TaskAssignmentHistory
        fields = [
            'id', 'task', 'action', 'action_display',
            'performed_by', 'performed_by_name',
            'previous_assignee', 'previous_assignee_name',
            'new_assignee', 'new_assignee_name',
            'previous_status', 'new_status', 'notes', 'metadata', 'timestamp'
        ]
        read_only_fields = ['id', 'timestamp']


class TaskListSerializer(serializers.ModelSerializer):
    """Serializer simple para listas de tareas (NO GeoJSON)."""
    assigned_to_name = serializers.CharField(
        source='assigned_to.get_full_name',
        read_only=True
    )
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    
    # Alias en español para frontend
    titulo = serializers.CharField(source='title', read_only=True)
    descripcion = serializers.CharField(source='description', read_only=True)
    estado = serializers.CharField(source='status', read_only=True)
    prioridad = serializers.IntegerField(source='priority', read_only=True)
    asignado_a = serializers.SerializerMethodField()
    ruta = serializers.SerializerMethodField()
    fecha_limite = serializers.DateField(source='scheduled_date', read_only=True)
    progreso = serializers.IntegerField(source='completion_percentage', read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'task_id', 'titulo', 'descripcion', 'estado', 'prioridad',
            'status_display', 'priority_display', 'assigned_to', 'assigned_to_name',
            'asignado_a', 'ruta', 'fecha_limite', 'progreso', 'title', 'status', 'priority',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'task_id', 'created_at', 'updated_at']

    def get_asignado_a(self, obj):
        if obj.assigned_to:
            return {
                'id': str(obj.assigned_to.id),
                'display_name': obj.assigned_to.get_full_name(),
                'email': obj.assigned_to.email
            }
        return None

    def get_ruta(self, obj):
        if obj.route:
            return {
                'id': obj.route.id,
                'nombre': obj.route.name if hasattr(obj.route, 'name') else obj.route.title
            }
        return None


class TaskSerializer(GeoFeatureModelSerializer):
    """Serializer para tareas con soporte GeoJSON (detalles)."""
    assigned_to_name = serializers.CharField(
        source='assigned_to.get_full_name',
        read_only=True
    )
    created_by_name = serializers.CharField(
        source='created_by.get_full_name',
        read_only=True
    )
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    
    # Campos anidados
    checkpoints = TaskCheckpointSerializer(many=True, read_only=True)
    route_id = serializers.IntegerField(source='route.id', read_only=True)
    incident_id = serializers.IntegerField(source='incident.id', read_only=True, allow_null=True)

    # Campos de ubicación
    location_lat = serializers.SerializerMethodField()
    location_lon = serializers.SerializerMethodField()
    
    # Alias en español para frontend
    titulo = serializers.CharField(source='title', read_only=True)
    descripcion = serializers.CharField(source='description', read_only=True)
    estado = serializers.CharField(source='status', read_only=True)
    prioridad = serializers.CharField(source='priority', read_only=True)
    tipo = serializers.SerializerMethodField()
    asignado_a = serializers.SerializerMethodField()
    ruta = serializers.SerializerMethodField()
    fecha_limite = serializers.DateField(source='scheduled_date', read_only=True)
    progreso = serializers.IntegerField(source='completion_percentage', read_only=True)

    class Meta:
        model = Task
        geo_field = 'location'
        fields = [
            'id', 'task_id', 'titulo', 'descripcion',
            'title', 'description',
            'route', 'route_id', 'incident', 'incident_id', 'ruta',
            'assigned_to', 'assigned_to_name', 'asignado_a', 'created_by', 'created_by_name',
            'status', 'status_display', 'estado',
            'priority', 'priority_display', 'prioridad', 'tipo',
            'location', 'location_lat', 'location_lon', 'address',
            'scheduled_date', 'scheduled_start_time', 'scheduled_end_time', 'fecha_limite',
            'estimated_duration', 'started_at', 'completed_at', 'paused_at',
            'team_size', 'equipment_needed', 'materials_needed',
            'completion_percentage', 'progreso', 'checkpoints_completed', 'checkpoints_total',
            'result_notes', 'result_photos', 'waste_collected_kg',
            'created_at', 'updated_at', 'cancelled_reason',
            'checkpoints'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'started_at', 'completed_at',
            'paused_at', 'completion_percentage', 'checkpoints_completed',
            'checkpoints_total'
        ]

    def get_location_lat(self, obj):
        if obj.location:
            return obj.location.y
        return None

    def get_location_lon(self, obj):
        if obj.location:
            return obj.location.x
        return None
    
    def get_tipo(self, obj):
        """Retorna el tipo de tarea basado en su relación."""
        if obj.route:
            return 'RUTA'
        elif obj.incident:
            return 'INCIDENCIA'
        return 'GENERAL'
    
    def get_asignado_a(self, obj):
        """Retorna datos del usuario asignado."""
        if obj.assigned_to:
            return {
                'id': obj.assigned_to.id,
                'display_name': obj.assigned_to.get_full_name(),
                'email': obj.assigned_to.email
            }
        return None
    
    def get_ruta(self, obj):
        """Retorna datos de la ruta asociada."""
        if obj.route:
            return {
                'id': obj.route.id,
                'nombre': obj.route.name
            }
        return None


class TaskCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear tareas."""
    location_lat = serializers.FloatField(write_only=True, required=False, allow_null=True)
    location_lon = serializers.FloatField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Task
        fields = [
            'task_id', 'title', 'description',
            'route', 'incident', 'assigned_to',
            'status', 'priority',
            'location_lat', 'location_lon', 'address',
            'scheduled_date', 'scheduled_start_time', 'scheduled_end_time',
            'estimated_duration', 'team_size',
            'equipment_needed', 'materials_needed'
        ]

    def create(self, validated_data):
        from django.contrib.gis.geos import Point
        
        # Extraer coordenadas
        location_lat = validated_data.pop('location_lat', None)
        location_lon = validated_data.pop('location_lon', None)

        # Crear punto geográfico si hay coordenadas
        if location_lat and location_lon:
            validated_data['location'] = Point(location_lon, location_lat)

        # Establecer usuario creador
        validated_data['created_by'] = self.context['request'].user

        return super().create(validated_data)


class TaskUpdateSerializer(serializers.ModelSerializer):
    """Serializer para actualizar tareas."""
    location_lat = serializers.FloatField(write_only=True, required=False, allow_null=True)
    location_lon = serializers.FloatField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Task
        fields = [
            'title', 'description', 'assigned_to', 'status', 'priority',
            'location_lat', 'location_lon', 'address',
            'scheduled_date', 'scheduled_start_time', 'scheduled_end_time',
            'estimated_duration', 'team_size',
            'equipment_needed', 'materials_needed',
            'result_notes', 'result_photos', 'waste_collected_kg',
            'cancelled_reason'
        ]

    def update(self, instance, validated_data):
        from django.contrib.gis.geos import Point
        
        # Extraer coordenadas
        location_lat = validated_data.pop('location_lat', None)
        location_lon = validated_data.pop('location_lon', None)

        # Actualizar punto geográfico si hay coordenadas
        if location_lat and location_lon:
            validated_data['location'] = Point(location_lon, location_lat)

        return super().update(instance, validated_data)


class TaskAssignmentSerializer(serializers.Serializer):
    """Serializer para asignar/reasignar tareas."""
    assigned_to = serializers.IntegerField(help_text='ID del usuario a asignar')
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate_assigned_to(self, value):
        try:
            user = User.objects.get(id=value)
            return user
        except User.DoesNotExist:
            raise serializers.ValidationError("Usuario no encontrado")


class TaskStatusUpdateSerializer(serializers.Serializer):
    """Serializer para actualizar el estado de una tarea."""
    status = serializers.ChoiceField(choices=Task.STATUS_CHOICES)
    notes = serializers.CharField(required=False, allow_blank=True)


class CheckpointCompleteSerializer(serializers.Serializer):
    """Serializer para marcar un checkpoint como completado."""
    photo_url = serializers.URLField(required=False, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True)
    verification_data = serializers.JSONField(required=False)


class TaskStatisticsSerializer(serializers.Serializer):
    """Serializer para estadísticas de tareas."""
    total_tasks = serializers.IntegerField()
    pending_tasks = serializers.IntegerField()
    assigned_tasks = serializers.IntegerField()
    in_progress_tasks = serializers.IntegerField()
    completed_tasks = serializers.IntegerField()
    cancelled_tasks = serializers.IntegerField()
    completion_rate = serializers.FloatField()
    avg_completion_time = serializers.DurationField(allow_null=True)
    total_waste_collected = serializers.DecimalField(max_digits=10, decimal_places=2)
