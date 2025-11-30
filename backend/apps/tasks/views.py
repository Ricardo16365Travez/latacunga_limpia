from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count, Avg, Sum
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Task, TaskCheckpoint, TaskAssignmentHistory
from .serializers import (
    TaskSerializer, TaskCreateSerializer, TaskUpdateSerializer,
    TaskCheckpointSerializer, TaskAssignmentHistorySerializer,
    TaskAssignmentSerializer, TaskStatusUpdateSerializer,
    CheckpointCompleteSerializer, TaskStatisticsSerializer
)


class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de tareas de limpieza.
    
    Endpoints:
    - GET /api/tasks/ - Listar todas las tareas
    - POST /api/tasks/ - Crear nueva tarea
    - GET /api/tasks/{id}/ - Obtener detalle de tarea
    - PUT /api/tasks/{id}/ - Actualizar tarea completa
    - PATCH /api/tasks/{id}/ - Actualizar parcialmente tarea
    - DELETE /api/tasks/{id}/ - Eliminar tarea
    - GET /api/tasks/my_tasks/ - Tareas asignadas al usuario actual
    - POST /api/tasks/{id}/assign/ - Asignar tarea a usuario
    - POST /api/tasks/{id}/start/ - Iniciar tarea
    - POST /api/tasks/{id}/pause/ - Pausar tarea
    - POST /api/tasks/{id}/resume/ - Reanudar tarea
    - POST /api/tasks/{id}/complete/ - Completar tarea
    - POST /api/tasks/{id}/cancel/ - Cancelar tarea
    - GET /api/tasks/statistics/ - Obtener estadísticas de tareas
    """
    queryset = Task.objects.select_related(
        'route', 'incident', 'assigned_to', 'created_by'
    ).prefetch_related('checkpoints', 'history')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'priority', 'assigned_to', 'scheduled_date']
    search_fields = ['task_id', 'title', 'description', 'address']
    ordering_fields = ['created_at', 'scheduled_date', 'priority', 'status']
    ordering = ['-priority', 'scheduled_date']

    def get_serializer_class(self):
        if self.action == 'create':
            return TaskCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return TaskUpdateSerializer
        return TaskSerializer

    def perform_create(self, serializer):
        """Crear tarea y registrar en historial."""
        task = serializer.save()
        TaskAssignmentHistory.objects.create(
            task=task,
            action='created',
            performed_by=self.request.user,
            new_status=task.status,
            metadata={'created_via': 'api'}
        )

    @action(detail=False, methods=['get'])
    def my_tasks(self, request):
        """Obtener tareas asignadas al usuario actual."""
        tasks = self.queryset.filter(assigned_to=request.user)
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """Asignar tarea a un usuario."""
        task = self.get_object()
        serializer = TaskAssignmentSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        previous_assignee = task.assigned_to
        new_assignee = serializer.validated_data['assigned_to']
        notes = serializer.validated_data.get('notes', '')

        # Actualizar asignación
        task.assigned_to = new_assignee
        if task.status == 'pending':
            task.status = 'assigned'
        task.save()

        # Registrar en historial
        TaskAssignmentHistory.objects.create(
            task=task,
            action='assigned' if previous_assignee is None else 'reassigned',
            performed_by=request.user,
            previous_assignee=previous_assignee,
            new_assignee=new_assignee,
            new_status=task.status,
            notes=notes
        )

        return Response({
            'message': 'Tarea asignada exitosamente',
            'task': TaskSerializer(task).data
        })

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """Iniciar una tarea."""
        task = self.get_object()

        if task.status not in ['assigned', 'paused']:
            return Response(
                {'error': 'Solo se pueden iniciar tareas asignadas o pausadas'},
                status=status.HTTP_400_BAD_REQUEST
            )

        previous_status = task.status
        task.status = 'in_progress'
        if not task.started_at:
            task.started_at = timezone.now()
        task.save()

        # Registrar en historial
        TaskAssignmentHistory.objects.create(
            task=task,
            action='resumed' if previous_status == 'paused' else 'started',
            performed_by=request.user,
            previous_status=previous_status,
            new_status='in_progress'
        )

        return Response({
            'message': 'Tarea iniciada',
            'task': TaskSerializer(task).data
        })

    @action(detail=True, methods=['post'])
    def pause(self, request, pk=None):
        """Pausar una tarea en progreso."""
        task = self.get_object()

        if task.status != 'in_progress':
            return Response(
                {'error': 'Solo se pueden pausar tareas en progreso'},
                status=status.HTTP_400_BAD_REQUEST
            )

        task.status = 'paused'
        task.paused_at = timezone.now()
        task.save()

        # Registrar en historial
        serializer = TaskStatusUpdateSerializer(data=request.data)
        notes = ''
        if serializer.is_valid():
            notes = serializer.validated_data.get('notes', '')

        TaskAssignmentHistory.objects.create(
            task=task,
            action='paused',
            performed_by=request.user,
            previous_status='in_progress',
            new_status='paused',
            notes=notes
        )

        return Response({
            'message': 'Tarea pausada',
            'task': TaskSerializer(task).data
        })

    @action(detail=True, methods=['post'])
    def resume(self, request, pk=None):
        """Reanudar una tarea pausada."""
        return self.start(request, pk)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Completar una tarea."""
        task = self.get_object()

        if task.status not in ['in_progress', 'assigned']:
            return Response(
                {'error': 'Solo se pueden completar tareas en progreso o asignadas'},
                status=status.HTTP_400_BAD_REQUEST
            )

        task.status = 'completed'
        task.completed_at = timezone.now()
        task.completion_percentage = 100
        
        # Actualizar datos de resultado si se proveen
        if 'result_notes' in request.data:
            task.result_notes = request.data['result_notes']
        if 'result_photos' in request.data:
            task.result_photos = request.data['result_photos']
        if 'waste_collected_kg' in request.data:
            task.waste_collected_kg = request.data['waste_collected_kg']
        
        task.save()

        # Registrar en historial
        TaskAssignmentHistory.objects.create(
            task=task,
            action='completed',
            performed_by=request.user,
            previous_status='in_progress',
            new_status='completed',
            notes=request.data.get('notes', '')
        )

        return Response({
            'message': 'Tarea completada',
            'task': TaskSerializer(task).data
        })

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancelar una tarea."""
        task = self.get_object()

        if task.status in ['completed', 'cancelled']:
            return Response(
                {'error': 'No se puede cancelar una tarea ya completada o cancelada'},
                status=status.HTTP_400_BAD_REQUEST
            )

        previous_status = task.status
        task.status = 'cancelled'
        task.cancelled_reason = request.data.get('cancelled_reason', '')
        task.save()

        # Registrar en historial
        TaskAssignmentHistory.objects.create(
            task=task,
            action='cancelled',
            performed_by=request.user,
            previous_status=previous_status,
            new_status='cancelled',
            notes=task.cancelled_reason
        )

        return Response({
            'message': 'Tarea cancelada',
            'task': TaskSerializer(task).data
        })

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Obtener estadísticas generales de tareas."""
        # Contadores por estado
        stats = Task.objects.aggregate(
            total=Count('id'),
            pending=Count('id', filter=Q(status='pending')),
            assigned=Count('id', filter=Q(status='assigned')),
            in_progress=Count('id', filter=Q(status='in_progress')),
            completed=Count('id', filter=Q(status='completed')),
            cancelled=Count('id', filter=Q(status='cancelled')),
            total_waste=Sum('waste_collected_kg')
        )

        # Calcular tasa de completitud
        total = stats['total'] or 1
        stats['completion_rate'] = (stats['completed'] / total) * 100

        # Tiempo promedio de completitud
        completed_tasks = Task.objects.filter(
            status='completed',
            started_at__isnull=False,
            completed_at__isnull=False
        )
        
        avg_time = None
        if completed_tasks.exists():
            durations = [
                (task.completed_at - task.started_at).total_seconds()
                for task in completed_tasks
            ]
            avg_seconds = sum(durations) / len(durations)
            from datetime import timedelta
            avg_time = timedelta(seconds=avg_seconds)

        serializer = TaskStatisticsSerializer({
            'total_tasks': stats['total'],
            'pending_tasks': stats['pending'],
            'assigned_tasks': stats['assigned'],
            'in_progress_tasks': stats['in_progress'],
            'completed_tasks': stats['completed'],
            'cancelled_tasks': stats['cancelled'],
            'completion_rate': stats['completion_rate'],
            'avg_completion_time': avg_time,
            'total_waste_collected': stats['total_waste'] or 0
        })

        return Response(serializer.data)


class TaskCheckpointViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de checkpoints de tareas.
    
    Endpoints:
    - GET /api/task-checkpoints/ - Listar checkpoints
    - POST /api/task-checkpoints/ - Crear checkpoint
    - GET /api/task-checkpoints/{id}/ - Obtener detalle
    - PUT /api/task-checkpoints/{id}/ - Actualizar checkpoint
    - DELETE /api/task-checkpoints/{id}/ - Eliminar checkpoint
    - POST /api/task-checkpoints/{id}/complete/ - Marcar como completado
    """
    queryset = TaskCheckpoint.objects.select_related('task', 'completed_by')
    serializer_class = TaskCheckpointSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['task', 'is_completed']
    ordering = ['task', 'checkpoint_order']

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Marcar checkpoint como completado."""
        checkpoint = self.get_object()

        if checkpoint.is_completed:
            return Response(
                {'error': 'El checkpoint ya está completado'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = CheckpointCompleteSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Actualizar checkpoint
        checkpoint.photo_url = serializer.validated_data.get('photo_url', '')
        checkpoint.notes = serializer.validated_data.get('notes', '')
        checkpoint.verification_data = serializer.validated_data.get('verification_data', {})
        checkpoint.mark_completed(request.user)

        return Response({
            'message': 'Checkpoint completado',
            'checkpoint': TaskCheckpointSerializer(checkpoint).data
        })


class TaskAssignmentHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet de solo lectura para historial de asignaciones.
    
    Endpoints:
    - GET /api/task-history/ - Listar historial
    - GET /api/task-history/{id}/ - Obtener detalle de registro
    """
    queryset = TaskAssignmentHistory.objects.select_related(
        'task', 'performed_by', 'previous_assignee', 'new_assignee'
    )
    serializer_class = TaskAssignmentHistorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['task', 'action', 'performed_by']
    ordering = ['-timestamp']
