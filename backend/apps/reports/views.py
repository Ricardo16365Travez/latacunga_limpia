from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Count, Q
from .models import Report, Statistics
from .serializers import ReportSerializer, StatisticsSerializer
from apps.incidents.models import Incident, IncidentType, IncidentStatus
from apps.tasks.models import Task
from apps.routes.models import Route


class ReportViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de reportes."""
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        import uuid
        serializer.save(
            report_id=str(uuid.uuid4()),
            generated_by=self.request.user
        )
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Obtener estadísticas compiladas del sistema."""
        try:
            # Contar incidencias por estado
            incidents = Incident.objects.all()
            incidents_by_status = {}
            for choice in IncidentStatus.choices:
                status_value = choice[0]
                count = incidents.filter(status=status_value).count()
                incidents_by_status[choice[1]] = count
            
            # Contar incidencias por tipo
            incidents_by_type = {}
            for choice in IncidentType.choices:
                type_value = choice[0]
                count = incidents.filter(incident_type=type_value).count()
                incidents_by_type[choice[1]] = count
            
            # Contar tareas: intentar primero usando 'status'; si falla (columna faltante), usar 'state'
            tasks = Task.objects.all()
            try:
                tasks_completed = tasks.filter(status='completed').count()
                tasks_pending = tasks.filter(status='pending').count()
            except Exception:
                try:
                    tasks_completed = tasks.filter(state='completed').count()
                    tasks_pending = tasks.filter(state='pending').count()
                except Exception:
                    tasks_completed = 0
                    tasks_pending = 0
            
            # Contar rutas (proteger si el modelo Route no tiene campo 'status')
            routes = Route.objects.all()
            try:
                # Intentar acceder al campo 'status' y contarlo
                Route._meta.get_field('status')
                routes_active = routes.filter(status='active').count()
            except Exception:
                routes_active = 0
            
            stats = {
                'total_incidencias': incidents.count(),
                'incidencias_por_estado': incidents_by_status,
                'incidencias_por_tipo': incidents_by_type,
                'total_rutas': routes.count(),
                'rutas_activas': routes_active,
                'total_tareas': tasks.count(),
                'tareas_completadas': tasks_completed,
                'tareas_pendientes': tasks_pending,
                'timestamp': timezone.now().isoformat()
            }
            
            return Response(stats)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class StatisticsViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet de solo lectura para estadísticas."""
    queryset = Statistics.objects.all()
    serializer_class = StatisticsSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
