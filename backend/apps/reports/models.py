from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Report(models.Model):
    """Modelo para reportes generados del sistema."""
    REPORT_TYPE_CHOICES = [
        ('daily', 'Reporte Diario'),
        ('weekly', 'Reporte Semanal'),
        ('monthly', 'Reporte Mensual'),
        ('custom', 'Reporte Personalizado'),
        ('tasks', 'Reporte de Tareas'),
        ('incidents', 'Reporte de Incidencias'),
        ('routes', 'Reporte de Rutas'),
        ('performance', 'Reporte de Rendimiento'),
    ]

    FORMAT_CHOICES = [
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('csv', 'CSV'),
        ('json', 'JSON'),
    ]

    report_id = models.CharField(max_length=100, unique=True, db_index=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    report_type = models.CharField(max_length=50, choices=REPORT_TYPE_CHOICES)
    format = models.CharField(max_length=20, choices=FORMAT_CHOICES, default='pdf')
    
    # Usuario que generó el reporte
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    # Parámetros del reporte
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    filters = models.JSONField(default=dict, blank=True)
    
    # Archivo generado
    file_path = models.FileField(upload_to='reports/%Y/%m/', blank=True)
    file_url = models.URLField(blank=True)
    file_size = models.IntegerField(null=True, blank=True)
    
    # Estado
    is_generated = models.BooleanField(default=False)
    generated_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'reports'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['report_type', '-created_at']),
            models.Index(fields=['generated_by', '-created_at']),
        ]

    def __str__(self):
        return f"{self.report_id} - {self.title}"


class Statistics(models.Model):
    """Modelo para estadísticas precalculadas."""
    stat_type = models.CharField(max_length=50, db_index=True)
    date = models.DateField(db_index=True)
    value = models.DecimalField(max_digits=15, decimal_places=2)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'reportes.statistics'
        unique_together = ['stat_type', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"{self.stat_type} - {self.date}: {self.value}"
