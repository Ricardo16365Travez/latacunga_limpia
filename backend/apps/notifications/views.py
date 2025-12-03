from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from .models import Notification, DeviceToken, NotificationPreference
from .serializers import (
    NotificationSerializer, DeviceTokenSerializer,
    NotificationPreferenceSerializer, NotificationCreateSerializer,
    BulkNotificationSerializer
)


class NotificationViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de notificaciones."""
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['notification_type', 'is_read', 'priority']
    ordering = ['-created_at']

    def get_queryset(self):
        user = getattr(self.request, 'user', None)
        # Si el usuario no está autenticado, devolver queryset vacío (no mostrar notificaciones privadas)
        if user is None or getattr(user, 'is_anonymous', True):
            return Notification.objects.none()
        return Notification.objects.filter(user=user)

    def get_serializer_class(self):
        if self.action == 'create':
            return NotificationCreateSerializer
        return NotificationSerializer

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """Marcar notificación como leída."""
        notification = self.get_object()
        notification.mark_as_read()
        return Response({'status': 'notification marked as read'})

    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        """Marcar todas las notificaciones como leídas."""
        count = Notification.objects.filter(
            user=request.user, is_read=False
        ).update(is_read=True)
        return Response({'marked_as_read': count})

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Obtener contador de notificaciones no leídas."""
        count = Notification.objects.filter(
            user=request.user, is_read=False
        ).count()
        return Response({'unread_count': count})

    @action(detail=False, methods=['post'])
    def send_bulk(self, request):
        """Enviar notificaciones masivas."""
        serializer = BulkNotificationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Implementar lógica de envío masivo
        # TODO: Implementar servicio de notificaciones
        return Response({'status': 'bulk notifications queued'})


class DeviceTokenViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de tokens de dispositivos."""
    serializer_class = DeviceTokenSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return DeviceToken.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class NotificationPreferenceViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de preferencias de notificaciones."""
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return NotificationPreference.objects.filter(user=self.request.user)
