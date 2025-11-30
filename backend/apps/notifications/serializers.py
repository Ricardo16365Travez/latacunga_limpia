from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Notification, DeviceToken, NotificationPreference

User = get_user_model()


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer para notificaciones."""
    notification_type_display = serializers.CharField(
        source='get_notification_type_display',
        read_only=True
    )
    priority_display = serializers.CharField(
        source='get_priority_display',
        read_only=True
    )
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    created_by_name = serializers.CharField(
        source='created_by.get_full_name',
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = Notification
        fields = [
            'id', 'notification_id', 'user', 'user_name',
            'notification_type', 'notification_type_display',
            'title', 'message', 'priority', 'priority_display',
            'delivery_channels', 'related_task_id', 'related_incident_id',
            'related_route_id', 'action_url', 'metadata', 'icon', 'image_url',
            'is_read', 'read_at', 'is_sent', 'sent_at', 'is_delivered', 'delivered_at',
            'scheduled_for', 'expires_at', 'created_at', 'updated_at',
            'created_by', 'created_by_name', 'delivery_errors', 'retry_count'
        ]
        read_only_fields = [
            'id', 'notification_id', 'is_read', 'read_at', 'is_sent', 'sent_at',
            'is_delivered', 'delivered_at', 'created_at', 'updated_at',
            'delivery_errors', 'retry_count'
        ]


class DeviceTokenSerializer(serializers.ModelSerializer):
    """Serializer para tokens de dispositivos."""
    platform_display = serializers.CharField(source='get_platform_display', read_only=True)

    class Meta:
        model = DeviceToken
        fields = [
            'id', 'user', 'token', 'platform', 'platform_display',
            'device_id', 'device_name', 'device_model', 'os_version',
            'app_version', 'is_active', 'last_used_at', 'metadata',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'last_used_at', 'created_at', 'updated_at']


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    """Serializer para preferencias de notificaciones."""
    
    class Meta:
        model = NotificationPreference
        fields = [
            'id', 'user', 'push_enabled', 'email_enabled', 'in_app_enabled',
            'websocket_enabled', 'task_notifications', 'incident_notifications',
            'route_notifications', 'system_notifications', 'message_notifications',
            'do_not_disturb', 'dnd_start_time', 'dnd_end_time',
            'sound_enabled', 'vibration_enabled', 'badge_enabled',
            'group_notifications', 'max_notifications_per_day',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class NotificationCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear notificaciones."""
    
    class Meta:
        model = Notification
        fields = [
            'user', 'notification_type', 'title', 'message', 'priority',
            'delivery_channels', 'related_task_id', 'related_incident_id',
            'related_route_id', 'action_url', 'metadata', 'icon', 'image_url',
            'scheduled_for', 'expires_at'
        ]

    def create(self, validated_data):
        import uuid
        validated_data['notification_id'] = str(uuid.uuid4())
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class BulkNotificationSerializer(serializers.Serializer):
    """Serializer para envío masivo de notificaciones."""
    user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text='Lista de IDs de usuarios'
    )
    notification_type = serializers.ChoiceField(
        choices=Notification.NOTIFICATION_TYPE_CHOICES
    )
    title = serializers.CharField(max_length=200)
    message = serializers.CharField()
    priority = serializers.IntegerField(default=2)
    delivery_channels = serializers.ListField(
        child=serializers.CharField(),
        default=['in_app', 'push']
    )
    action_url = serializers.URLField(required=False, allow_blank=True)
    metadata = serializers.JSONField(required=False, default=dict)
