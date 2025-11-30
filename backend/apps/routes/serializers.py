from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import CleaningZone, Route, RouteWaypoint


class CleaningZoneSerializer(GeoFeatureModelSerializer):
    """Serializer para zonas de limpieza con geometría"""
    
    class Meta:
        model = CleaningZone
        geo_field = 'zone_polygon'
        fields = [
            'id', 'zone_name', 'description', 'zone_polygon', 'priority',
            'frequency', 'estimated_duration_minutes', 'assigned_team_size',
            'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class RouteWaypointSerializer(serializers.ModelSerializer):
    """Serializer para puntos de ruta"""
    
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()
    
    class Meta:
        model = RouteWaypoint
        fields = [
            'id', 'waypoint_order', 'latitude', 'longitude', 'location',
            'address', 'waypoint_type', 'estimated_service_minutes', 'notes'
        ]
    
    def get_latitude(self, obj):
        return obj.location.y if obj.location else None
    
    def get_longitude(self, obj):
        return obj.location.x if obj.location else None


class RouteSerializer(GeoFeatureModelSerializer):
    """Serializer para rutas con geometría"""
    
    zone_name = serializers.CharField(source='zone.zone_name', read_only=True)
    route_waypoints = RouteWaypointSerializer(many=True, read_only=True)
    
    class Meta:
        model = Route
        geo_field = 'route_geometry'
        fields = [
            'id', 'route_name', 'zone', 'zone_name', 'route_geometry',
            'waypoints', 'total_distance_km', 'estimated_duration_minutes',
            'optimization_algorithm', 'status', 'route_waypoints',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CalculateRouteRequestSerializer(serializers.Serializer):
    """Serializer para solicitud de cálculo de ruta"""
    
    waypoints = serializers.ListField(
        child=serializers.DictField(),
        min_length=2,
        help_text="Lista de puntos con {lat, lon}"
    )
    optimize = serializers.BooleanField(
        default=False,
        help_text="Si True, optimiza el orden de los waypoints"
    )
    roundtrip = serializers.BooleanField(
        default=True,
        help_text="Si True, retorna al punto de inicio"
    )
    
    def validate_waypoints(self, value):
        """Validar que cada waypoint tenga lat y lon"""
        for i, wp in enumerate(value):
            if 'lat' not in wp or 'lon' not in wp:
                raise serializers.ValidationError(
                    f"Waypoint {i} debe tener 'lat' y 'lon'"
                )
            
            # Validar rangos
            lat = float(wp['lat'])
            lon = float(wp['lon'])
            
            if not (-90 <= lat <= 90):
                raise serializers.ValidationError(
                    f"Latitud inválida en waypoint {i}: {lat}"
                )
            
            if not (-180 <= lon <= 180):
                raise serializers.ValidationError(
                    f"Longitud inválida en waypoint {i}: {lon}"
                )
        
        return value


class CreateRouteRequestSerializer(serializers.Serializer):
    """Serializer para crear una ruta desde waypoints"""
    
    route_name = serializers.CharField(max_length=200)
    zone_id = serializers.UUIDField(required=False, allow_null=True)
    waypoints = serializers.ListField(
        child=serializers.DictField(),
        min_length=2
    )
    optimize = serializers.BooleanField(default=False)
    waypoint_details = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        help_text="Detalles adicionales de cada waypoint (address, type, notes)"
    )


class RouteOptimizationResultSerializer(serializers.Serializer):
    """Serializer para resultado de optimización de ruta"""
    
    success = serializers.BooleanField()
    distance_km = serializers.DecimalField(max_digits=10, decimal_places=3)
    duration_minutes = serializers.IntegerField()
    optimized_order = serializers.ListField(child=serializers.IntegerField())
    waypoints = serializers.ListField(child=serializers.DictField())
    geometry = serializers.JSONField()
    error = serializers.CharField(required=False)


class NearestRoadRequestSerializer(serializers.Serializer):
    """Serializer para buscar punto más cercano en la red vial"""
    
    lat = serializers.FloatField(min_value=-90, max_value=90)
    lon = serializers.FloatField(min_value=-180, max_value=180)
    number = serializers.IntegerField(default=1, min_value=1, max_value=10)
