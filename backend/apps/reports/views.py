from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Report, Statistics
from .serializers import ReportSerializer, StatisticsSerializer


class ReportViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de reportes."""
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        import uuid
        serializer.save(
            report_id=str(uuid.uuid4()),
            generated_by=self.request.user
        )


class StatisticsViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet de solo lectura para estadísticas."""
    queryset = Statistics.objects.all()
    serializer_class = StatisticsSerializer
    permission_classes = [IsAuthenticated]
