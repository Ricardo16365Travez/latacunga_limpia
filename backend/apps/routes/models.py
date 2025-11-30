from django.contrib.gis.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


class CleaningZone(models.Model):
    """Zona de limpieza con polígono geográfico"""
    
    FREQUENCY_CHOICES = [
        ('daily', 'Diario'),
        ('weekly', 'Semanal'),
        ('biweekly', 'Quincenal'),
        ('monthly', 'Mensual'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Activa'),
        ('inactive', 'Inactiva'),
        ('maintenance', 'En mantenimiento'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    zone_name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True, null=True)
    zone_polygon = models.PolygonField(srid=4326)  # Polígono geográfico
    priority = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="1=Baja, 5=Muy alta"
    )
    frequency = models.CharField(
        max_length=10,
        choices=FREQUENCY_CHOICES,
        default='daily'
    )
    estimated_duration_minutes = models.IntegerField(null=True, blank=True)
    assigned_team_size = models.IntegerField(default=2)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cleaning_zones'
        verbose_name = 'Zona de Limpieza'
        verbose_name_plural = 'Zonas de Limpieza'
        ordering = ['-priority', 'zone_name']
    
    def __str__(self):
        return f"{self.zone_name} (Prioridad: {self.priority})"


class Route(models.Model):
    """Ruta optimizada para limpieza"""
    
    STATUS_CHOICES = [
        ('active', 'Activa'),
        ('inactive', 'Inactiva'),
        ('archived', 'Archivada'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    route_name = models.CharField(max_length=200)
    zone = models.ForeignKey(
        CleaningZone,
        on_delete=models.CASCADE,
        related_name='routes',
        null=True,
        blank=True
    )
    route_geometry = models.LineStringField(srid=4326)  # LineString geográfica
    waypoints = models.JSONField(help_text="Array de puntos con lat/lon")
    total_distance_km = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        null=True,
        blank=True
    )
    estimated_duration_minutes = models.IntegerField(null=True, blank=True)
    optimization_algorithm = models.CharField(
        max_length=50,
        default='osrm',
        help_text="Algoritmo usado para optimización"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'routes'
        verbose_name = 'Ruta'
        verbose_name_plural = 'Rutas'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.route_name} ({self.total_distance_km}km)"


class RouteWaypoint(models.Model):
    """Punto de parada en una ruta"""
    
    WAYPOINT_TYPES = [
        ('start', 'Inicio'),
        ('collection', 'Recolección'),
        ('disposal', 'Disposición'),
        ('end', 'Fin'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        related_name='route_waypoints'
    )
    waypoint_order = models.IntegerField()
    location = models.PointField(srid=4326)
    address = models.CharField(max_length=300, blank=True, null=True)
    waypoint_type = models.CharField(
        max_length=20,
        choices=WAYPOINT_TYPES,
        null=True,
        blank=True
    )
    estimated_service_minutes = models.IntegerField(default=5)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'route_waypoints'
        verbose_name = 'Punto de Ruta'
        verbose_name_plural = 'Puntos de Ruta'
        ordering = ['route', 'waypoint_order']
        unique_together = ['route', 'waypoint_order']
    
    def __str__(self):
        return f"{self.route.route_name} - Waypoint {self.waypoint_order}"
