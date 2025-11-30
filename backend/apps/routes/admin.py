from django.contrib.gis import admin
from .models import CleaningZone, Route, RouteWaypoint


@admin.register(CleaningZone)
class CleaningZoneAdmin(admin.GISModelAdmin):
    list_display = ['zone_name', 'priority', 'frequency', 'status', 'created_at']
    list_filter = ['status', 'priority', 'frequency']
    search_fields = ['zone_name', 'description']
    ordering = ['-priority', 'zone_name']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('zone_name', 'description', 'zone_polygon')
        }),
        ('Configuración', {
            'fields': ('priority', 'frequency', 'estimated_duration_minutes', 'assigned_team_size', 'status')
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Route)
class RouteAdmin(admin.GISModelAdmin):
    list_display = ['route_name', 'zone', 'total_distance_km', 'estimated_duration_minutes', 'status', 'created_at']
    list_filter = ['status', 'optimization_algorithm']
    search_fields = ['route_name', 'zone__zone_name']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('route_name', 'zone', 'route_geometry')
        }),
        ('Detalles de Ruta', {
            'fields': ('waypoints', 'total_distance_km', 'estimated_duration_minutes', 'optimization_algorithm', 'status')
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']


@admin.register(RouteWaypoint)
class RouteWaypointAdmin(admin.GISModelAdmin):
    list_display = ['route', 'waypoint_order', 'waypoint_type', 'address']
    list_filter = ['waypoint_type']
    search_fields = ['route__route_name', 'address']
    ordering = ['route', 'waypoint_order']
