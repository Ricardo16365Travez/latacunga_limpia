"""
Servicio de integración con OSRM (Open Source Routing Machine)
para cálculo de rutas optimizadas en el sistema de gestión de residuos.
"""

import requests
import logging
from typing import List, Dict, Tuple, Optional
from django.contrib.gis.geos import LineString, Point
from decimal import Decimal

logger = logging.getLogger(__name__)


class OSRMService:
    """Cliente para interactuar con el servicio OSRM"""
    
    def __init__(self, base_url: str = "http://osrm:5000"):
        """
        Inicializa el servicio OSRM.
        
        Args:
            base_url: URL base del servicio OSRM (default: contenedor Docker)
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = 30  # segundos
    
    def calculate_route(
        self,
        coordinates: List[Tuple[float, float]],
        profile: str = 'driving',
        overview: str = 'full',
        geometries: str = 'geojson'
    ) -> Dict:
        """
        Calcula una ruta entre múltiples puntos.
        
        Args:
            coordinates: Lista de tuplas (lon, lat)
            profile: Perfil de ruta (driving, car, foot, bicycle)
            overview: Nivel de detalle de geometría (full, simplified, false)
            geometries: Formato de geometría (geojson, polyline, polyline6)
        
        Returns:
            Dict con información de la ruta calculada
        """
        # Convertir coordenadas al formato OSRM: lon,lat;lon,lat;...
        coords_string = ';'.join([f"{lon},{lat}" for lon, lat in coordinates])
        
        url = f"{self.base_url}/route/v1/{profile}/{coords_string}"
        
        params = {
            'overview': overview,
            'geometries': geometries,
            'steps': 'true',
            'annotations': 'true'
        }
        
        try:
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('code') == 'Ok':
                logger.info(f"Ruta calculada exitosamente: {len(coordinates)} puntos")
                return self._process_route_response(data)
            else:
                logger.error(f"Error OSRM: {data.get('message', 'Unknown error')}")
                return {
                    'success': False,
                    'error': data.get('message', 'Unknown error')
                }
        
        except requests.exceptions.Timeout:
            logger.error(f"Timeout al conectar con OSRM: {url}")
            return {'success': False, 'error': 'Timeout al calcular ruta'}
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error al conectar con OSRM: {e}")
            return {'success': False, 'error': str(e)}
        
        except Exception as e:
            logger.error(f"Error inesperado en OSRM: {e}")
            return {'success': False, 'error': str(e)}
    
    def optimize_route(
        self,
        coordinates: List[Tuple[float, float]],
        roundtrip: bool = True,
        source: str = 'first',
        destination: str = 'last'
    ) -> Dict:
        """
        Optimiza el orden de visita de múltiples puntos (Travelling Salesman Problem).
        
        Args:
            coordinates: Lista de tuplas (lon, lat)
            roundtrip: Si True, retorna al punto de inicio
            source: Índice del punto de inicio ('first', 'any', o índice)
            destination: Índice del punto final ('last', 'any', o índice)
        
        Returns:
            Dict con ruta optimizada
        """
        coords_string = ';'.join([f"{lon},{lat}" for lon, lat in coordinates])
        
        url = f"{self.base_url}/trip/v1/driving/{coords_string}"
        
        params = {
            'roundtrip': str(roundtrip).lower(),
            'source': source,
            'destination': destination,
            'geometries': 'geojson',
            'overview': 'full',
            'steps': 'true'
        }
        
        try:
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('code') == 'Ok':
                logger.info(f"Ruta optimizada exitosamente: {len(coordinates)} puntos")
                return self._process_trip_response(data)
            else:
                logger.error(f"Error OSRM trip: {data.get('message', 'Unknown error')}")
                return {
                    'success': False,
                    'error': data.get('message', 'Unknown error')
                }
        
        except Exception as e:
            logger.error(f"Error al optimizar ruta: {e}")
            return {'success': False, 'error': str(e)}
    
    def calculate_matrix(
        self,
        sources: List[Tuple[float, float]],
        destinations: Optional[List[Tuple[float, float]]] = None
    ) -> Dict:
        """
        Calcula matriz de distancias/duraciones entre múltiples puntos.
        
        Args:
            sources: Lista de tuplas (lon, lat) de origen
            destinations: Lista de tuplas (lon, lat) de destino (opcional)
        
        Returns:
            Dict con matrices de distancias y duraciones
        """
        if destinations is None:
            destinations = sources
        
        all_coords = sources + destinations
        coords_string = ';'.join([f"{lon},{lat}" for lon, lat in all_coords])
        
        url = f"{self.base_url}/table/v1/driving/{coords_string}"
        
        params = {
            'sources': ';'.join([str(i) for i in range(len(sources))]),
            'destinations': ';'.join([str(i + len(sources)) for i in range(len(destinations))]),
            'annotations': 'duration,distance'
        }
        
        try:
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('code') == 'Ok':
                logger.info(f"Matriz calculada: {len(sources)}x{len(destinations)}")
                return {
                    'success': True,
                    'durations': data.get('durations', []),
                    'distances': data.get('distances', []),
                    'sources': sources,
                    'destinations': destinations
                }
            else:
                return {'success': False, 'error': data.get('message', 'Unknown error')}
        
        except Exception as e:
            logger.error(f"Error al calcular matriz: {e}")
            return {'success': False, 'error': str(e)}
    
    def match_route(
        self,
        coordinates: List[Tuple[float, float]],
        timestamps: Optional[List[int]] = None,
        radiuses: Optional[List[int]] = None
    ) -> Dict:
        """
        Hace map-matching de coordenadas GPS a la red vial.
        Útil para seguimiento de vehículos en tiempo real.
        
        Args:
            coordinates: Lista de tuplas (lon, lat)
            timestamps: Timestamps Unix de cada coordenada (opcional)
            radiuses: Radio de búsqueda en metros para cada punto (opcional)
        
        Returns:
            Dict con ruta ajustada a la red vial
        """
        coords_string = ';'.join([f"{lon},{lat}" for lon, lat in coordinates])
        
        url = f"{self.base_url}/match/v1/driving/{coords_string}"
        
        params = {
            'geometries': 'geojson',
            'overview': 'full',
            'annotations': 'true'
        }
        
        if timestamps:
            params['timestamps'] = ';'.join([str(t) for t in timestamps])
        
        if radiuses:
            params['radiuses'] = ';'.join([str(r) for r in radiuses])
        
        try:
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('code') == 'Ok':
                logger.info(f"Map matching exitoso: {len(coordinates)} puntos")
                return self._process_route_response(data)
            else:
                return {'success': False, 'error': data.get('message', 'Unknown error')}
        
        except Exception as e:
            logger.error(f"Error en map matching: {e}")
            return {'success': False, 'error': str(e)}
    
    def nearest_road(
        self,
        coordinate: Tuple[float, float],
        number: int = 1
    ) -> Dict:
        """
        Encuentra el(los) punto(s) más cercano(s) en la red vial.
        
        Args:
            coordinate: Tupla (lon, lat)
            number: Número de puntos a retornar
        
        Returns:
            Dict con puntos más cercanos en la red vial
        """
        lon, lat = coordinate
        url = f"{self.base_url}/nearest/v1/driving/{lon},{lat}"
        
        params = {'number': number}
        
        try:
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('code') == 'Ok':
                return {
                    'success': True,
                    'waypoints': data.get('waypoints', [])
                }
            else:
                return {'success': False, 'error': data.get('message', 'Unknown error')}
        
        except Exception as e:
            logger.error(f"Error al buscar punto cercano: {e}")
            return {'success': False, 'error': str(e)}
    
    def health_check(self) -> bool:
        """
        Verifica si el servicio OSRM está disponible.
        
        Returns:
            True si está disponible, False en caso contrario
        """
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"OSRM no disponible: {e}")
            return False
    
    # ========== MÉTODOS PRIVADOS ==========
    
    def _process_route_response(self, data: Dict) -> Dict:
        """Procesa la respuesta de /route o /match"""
        routes = data.get('routes', [])
        
        if not routes:
            return {'success': False, 'error': 'No se encontró ninguna ruta'}
        
        route = routes[0]
        geometry = route.get('geometry', {})
        
        # Convertir geometría GeoJSON a LineString de Django
        if geometry.get('type') == 'LineString':
            coordinates = geometry.get('coordinates', [])
            linestring = LineString([Point(lon, lat) for lon, lat in coordinates], srid=4326)
        else:
            linestring = None
        
        return {
            'success': True,
            'geometry': linestring,
            'distance_meters': route.get('distance', 0),
            'distance_km': Decimal(route.get('distance', 0) / 1000).quantize(Decimal('0.001')),
            'duration_seconds': route.get('duration', 0),
            'duration_minutes': int(route.get('duration', 0) / 60),
            'legs': route.get('legs', []),
            'waypoints': data.get('waypoints', []),
            'raw_geometry': geometry
        }
    
    def _process_trip_response(self, data: Dict) -> Dict:
        """Procesa la respuesta de /trip (optimización)"""
        trips = data.get('trips', [])
        
        if not trips:
            return {'success': False, 'error': 'No se pudo optimizar la ruta'}
        
        trip = trips[0]
        geometry = trip.get('geometry', {})
        
        # Convertir geometría
        if geometry.get('type') == 'LineString':
            coordinates = geometry.get('coordinates', [])
            linestring = LineString([Point(lon, lat) for lon, lat in coordinates], srid=4326)
        else:
            linestring = None
        
        # Obtener orden optimizado de waypoints
        waypoints = data.get('waypoints', [])
        optimized_order = [wp.get('waypoint_index') for wp in waypoints]
        
        return {
            'success': True,
            'geometry': linestring,
            'distance_meters': trip.get('distance', 0),
            'distance_km': Decimal(trip.get('distance', 0) / 1000).quantize(Decimal('0.001')),
            'duration_seconds': trip.get('duration', 0),
            'duration_minutes': int(trip.get('duration', 0) / 60),
            'legs': trip.get('legs', []),
            'waypoints': waypoints,
            'optimized_order': optimized_order,
            'raw_geometry': geometry
        }


# Instancia global del servicio
osrm_service = OSRMService()
