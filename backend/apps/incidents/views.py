"""
Views/ViewSets para la API REST de incidencias.
Compatible con incident-service de Go.
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Incident, IncidentAttachment, IncidentEvent
from .serializers import (
    IncidentSerializer,
    IncidentCreateSerializer,
    IncidentUpdateStatusSerializer,
    IncidentValidationSerializer,
    IncidentAttachmentSerializer
)
from .incident_events_service import get_incident_event_service


class IncidentViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de incidencias.
    
    Endpoints:
    - GET    /api/v1/incidents/          - Listar incidentes
    - POST   /api/v1/incidents/          - Crear incidente (desde app móvil)
    - GET    /api/v1/incidents/{id}/     - Detalle de incidente
    - PATCH  /api/v1/incidents/{id}/     - Actualizar incidente
    - DELETE /api/v1/incidents/{id}/     - Eliminar incidente (solo admin)
    - POST   /api/v1/incidents/{id}/validate/  - Validar/Rechazar (admin)
    - POST   /api/v1/incidents/{id}/attachments/ - Agregar foto/evidencia
    """
    
    queryset = Incident.objects.all()
    serializer_class = IncidentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['incident_type', 'status', 'reporter_kind']
    search_fields = ['description', 'address']
    ordering_fields = ['created_at', 'status']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Retorna el serializer apropiado según la acción"""
        if self.action == 'create':
            return IncidentCreateSerializer
        return IncidentSerializer
    
    def perform_create(self, serializer):
        """
        Crea un incidente y publica evento a RabbitMQ.
        Compatible con offline-first (idempotency_key).
        """
        incident = serializer.save()
        
        # Registrar evento en historial
        IncidentEvent.objects.create(
            incident=incident,
            event_type='incidente_creado',
            payload={'initial_data': serializer.data}
        )
        
        # Publicar evento a RabbitMQ
        event_service = get_incident_event_service()
        event_service.publish_incident_submitted(incident)
    
    def perform_update(self, serializer):
        """Actualiza incidente y publica evento de cambio"""
        old_status = serializer.instance.status
        incident = serializer.save()
        
        # Si cambió el estado, publicar evento
        if old_status != incident.status:
            event_service = get_incident_event_service()
            event_service.publish_status_updated(incident, old_status, incident.status)
            
            # Registrar en historial
            IncidentEvent.objects.create(
                incident=incident,
                event_type='estado_actualizado',
                payload={
                    'old_status': old_status,
                    'new_status': incident.status
                }
            )
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def validate(self, request, pk=None):
        """
        Endpoint para que administradores validen o rechacen incidentes.
        
        POST /api/v1/incidents/{id}/validate/
        Body: {"action": "validate" | "reject", "notes": "..."}
        """
        incident = self.get_object()
        serializer = IncidentValidationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        action_type = serializer.validated_data['action']
        notes = serializer.validated_data.get('notes', '')
        validator_id = str(request.user.id)
        
        old_status = incident.status
        event_service = get_incident_event_service()
        
        if action_type == 'validate':
            # Validar incidente
            incident.status = 'incidente_valido'
            incident.save()
            
            # Publicar evento
            event_service.publish_incident_validated(incident, validator_id, notes)
            
            # Registrar en historial
            IncidentEvent.objects.create(
                incident=incident,
                event_type='incidente_validado',
                payload={
                    'validator_id': validator_id,
                    'notes': notes,
                    'old_status': old_status
                }
            )
            
            return Response({
                'success': True,
                'message': 'Incidente validado correctamente',
                'incident': IncidentSerializer(incident).data
            })
            
        elif action_type == 'reject':
            # Rechazar incidente
            incident.status = 'incidente_rechazado'
            incident.save()
            
            # Publicar evento
            event_service.publish_incident_rejected(incident, validator_id, notes)
            
            # Registrar en historial
            IncidentEvent.objects.create(
                incident=incident,
                event_type='incidente_rechazado',
                payload={
                    'validator_id': validator_id,
                    'reason': notes,
                    'old_status': old_status
                }
            )
            
            return Response({
                'success': True,
                'message': 'Incidente rechazado',
                'incident': IncidentSerializer(incident).data
            })
    
    @action(detail=True, methods=['post'])
    def attachments(self, request, pk=None):
        """
        Agregar foto/evidencia a un incidente.
        
        POST /api/v1/incidents/{id}/attachments/
        Body: {"file_url": "...", "mime_type": "...", "size_bytes": 123}
        """
        incident = self.get_object()
        serializer = IncidentAttachmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        attachment = serializer.save(incident=incident)
        
        # Actualizar contador de fotos
        incident.photos_count = incident.attachments.count()
        incident.save()
        
        # Publicar evento
        event_service = get_incident_event_service()
        event_service.publish_attachment_added(incident, attachment)
        
        # Registrar en historial
        IncidentEvent.objects.create(
            incident=incident,
            event_type='attachment_added',
            payload={
                'attachment_id': str(attachment.id),
                'file_url': attachment.file_url
            }
        )
        
        return Response({
            'success': True,
            'message': 'Evidencia agregada correctamente',
            'attachment': serializer.data,
            'incident': IncidentSerializer(incident).data
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAdminUser])
    def pending(self, request):
        """
        Lista incidentes pendientes de validación (solo para administradores).
        
        GET /api/v1/incidents/pending/
        """
        pending_incidents = Incident.objects.filter(
            status__in=['incidente_pendiente', 'incidente_no_validado']
        ).order_by('-created_at')
        
        serializer = self.get_serializer(pending_incidents, many=True)
        
        return Response({
            'success': True,
            'count': pending_incidents.count(),
            'data': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Estadísticas de incidentes para el dashboard.
        
        GET /api/v1/incidents/stats/
        """
        from django.db.models import Count
        
        stats = {
            'total': Incident.objects.count(),
            'by_status': dict(
                Incident.objects.values('status').annotate(count=Count('id')).values_list('status', 'count')
            ),
            'by_type': dict(
                Incident.objects.values('type').annotate(count=Count('id')).values_list('type', 'count')
            ),
            'pending_validation': Incident.objects.filter(
                status__in=['incidente_pendiente', 'incidente_no_validado']
            ).count(),
            'validated_today': Incident.objects.filter(
                status='incidente_valido',
                updated_at__date=timezone.now().date()
            ).count()
        }
        
        return Response(stats)
