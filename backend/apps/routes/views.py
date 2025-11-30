from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.gis.geos import Point, LineString
from .models import CleaningZone, Route, RouteWaypoint
from .serializers import (
    CleaningZoneSerializer, RouteSerializer, RouteWaypointSerializer,
    CalculateRouteRequestSerializer, CreateRouteRequestSerializer,
    NearestRoadRequestSerializer
)
from .osrm_service import osrm_service
import logging

logger = logging.getLogger(__name__)


class CleaningZoneViewSet(viewsets.ModelViewSet):
    """ViewSet para zonas de limpieza"""
    queryset = CleaningZone.objects.all()
    serializer_class = CleaningZoneSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Listar solo zonas activas"""
        zones = self.queryset.filter(status='active')
        serializer = self.get_serializer(zones, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def routes(self, request, pk=None):
        """Obtener todas las rutas de una zona"""
        zone = self.get_object()
        routes = zone.routes.all()
        serializer = RouteSerializer(routes, many=True)
        return Response(serializer.data)


class RouteViewSet(viewsets.ModelViewSet):
    """ViewSet para rutas optimizadas"""
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def calculate(self, request):
        """
        Calcular una ruta usando OSRM
        POST /api/v1/routes/calculate/
        {
            "waypoints": [{"lat": -0.9367, "lon": -78.6185}, ...],
            "optimize": false,
            "roundtrip": true
        }
        """
        serializer = CalculateRouteRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        waypoints = serializer.validated_data['waypoints']
        optimize = serializer.validated_data['optimize']
        roundtrip = serializer.validated_data['roundtrip']
        
        # Convertir a formato OSRM (lon, lat)
        coordinates = [(wp['lon'], wp['lat']) for wp in waypoints]
        
        if optimize:
            result = osrm_service.optimize_route(coordinates, roundtrip=roundtrip)
        else:
            result = osrm_service.calculate_route(coordinates)
        
        return Response(result)
    
    @action(detail=False, methods=['post'])
    def create_from_waypoints(self, request):
        """
        Crear una ruta desde waypoints y guardarla en BD
        POST /api/v1/routes/create_from_waypoints/
        """
        serializer = CreateRouteRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        waypoints = data['waypoints']
        optimize = data.get('optimize', False)
        
        # Calcular ruta con OSRM
        coordinates = [(wp['lon'], wp['lat']) for wp in waypoints]
        
        if optimize:
            osrm_result = osrm_service.optimize_route(coordinates)
        else:
            osrm_result = osrm_service.calculate_route(coordinates)
        
        if not osrm_result.get('success'):
            return Response(
                {'error': osrm_result.get('error', 'Error al calcular ruta')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Crear ruta en BD
        route = Route.objects.create(
            route_name=data['route_name'],
            zone_id=data.get('zone_id'),
            route_geometry=osrm_result['geometry'],
            waypoints=waypoints,
            total_distance_km=osrm_result['distance_km'],
            estimated_duration_minutes=osrm_result['duration_minutes'],
            optimization_algorithm='osrm' if optimize else 'osrm-direct'
        )
        
        # Crear waypoints
        waypoint_details = data.get('waypoint_details', [])
        for i, wp in enumerate(waypoints):
            details = waypoint_details[i] if i < len(waypoint_details) else {}
            
            RouteWaypoint.objects.create(
                route=route,
                waypoint_order=i,
                location=Point(wp['lon'], wp['lat'], srid=4326),
                address=details.get('address'),
                waypoint_type=details.get('type'),
                notes=details.get('notes')
            )
        
        serializer = RouteSerializer(route)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'])
    def nearest_road(self, request):
        """
        Encontrar punto más cercano en la red vial
        POST /api/v1/routes/nearest_road/
        {
            "lat": -0.9367,
            "lon": -78.6185,
            "number": 1
        }
        """
        serializer = NearestRoadRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        coordinate = (data['lon'], data['lat'])
        number = data.get('number', 1)
        
        result = osrm_service.nearest_road(coordinate, number)
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def health(self, request):
        """Verificar estado del servicio OSRM"""
        is_healthy = osrm_service.health_check()
        return Response({
            'osrm_status': 'available' if is_healthy else 'unavailable',
            'healthy': is_healthy
        })
