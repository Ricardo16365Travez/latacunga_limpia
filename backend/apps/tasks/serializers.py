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


class TaskSerializer(GeoFeatureModelSerializer):
    """Serializer para tareas con soporte GeoJSON."""
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

    class Meta:
        model = Task
        geo_field = 'location'
        fields = [
            'id', 'task_id', 'title', 'description',
            'route', 'route_id', 'incident', 'incident_id',
            'assigned_to', 'assigned_to_name', 'created_by', 'created_by_name',
            'status', 'status_display', 'priority', 'priority_display',
            'location', 'location_lat', 'location_lon', 'address',
            'scheduled_date', 'scheduled_start_time', 'scheduled_end_time',
            'estimated_duration', 'started_at', 'completed_at', 'paused_at',
            'team_size', 'equipment_needed', 'materials_needed',
            'completion_percentage', 'checkpoints_completed', 'checkpoints_total',
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
