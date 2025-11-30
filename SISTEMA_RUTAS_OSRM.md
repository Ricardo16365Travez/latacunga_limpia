# 🗺️ Sistema de Gestión de Rutas Optimizadas con OSRM

## 📋 Resumen de Implementación

### ✅ Completado

1. **Migraciones SQL Completas** (`database/migrations/001_create_complete_schema.sql`)
   - ✅ Esquema `incidentes` con 5 tablas
   - ✅ Esquema `validacion` para validación manual
   - ✅ Esquema `rutas` para zonas y rutas optimizadas
   - ✅ Esquema `tareas` para gestión de tareas
   - ✅ Esquema `notificaciones` para push notifications
   - ✅ Esquema `reportes` para estadísticas
   - ✅ Índices espaciales con PostGIS
   - ✅ Triggers y funciones automáticas
   - ✅ Vistas útiles predefinidas

2. **Módulo de Rutas** (`apps/routes/`)
   - ✅ Modelos: `CleaningZone`, `Route`, `RouteWaypoint`
   - ✅ Servicio OSRM completo con 6 funcionalidades
   - ✅ Serializers con soporte GeoJSON
   - ✅ ViewSets con acciones personalizadas
   - ✅ Admin con soporte de mapas (GISModelAdmin)

3. **Docker Compose Actualizado**
   - ✅ Servicio OSRM para cálculo de rutas
   - ✅ Puerto 5000 expuesto
   - ✅ Health checks configurados

## 🚀 Instalación y Configuración

### 1. Aplicar Migraciones SQL

```bash
# Conectar a la base de datos PostgreSQL
psql -h localhost -p 5433 -U postgres -d residuos_latacunga -f database/migrations/001_create_complete_schema.sql
```

O desde Docker:

```powershell
docker-compose exec db psql -U postgres -d residuos_latacunga -f /docker-entrypoint-initdb.d/001_create_complete_schema.sql
```

### 2. Descargar Datos de Mapa para OSRM

OSRM necesita datos del mapa de OpenStreetMap. Para Ecuador:

```powershell
# Crear directorio para datos OSRM
mkdir osrm_data
cd osrm_data

# Descargar mapa de Ecuador (o la región específica)
# Desde: http://download.geofabrik.de/south-america/ecuador-latest.osm.pbf
curl -O http://download.geofabrik.de/south-america/ecuador-latest.osm.pbf

# Procesar datos con OSRM
docker run -t -v ${PWD}:/data osrm/osrm-backend osrm-extract -p /opt/car.lua /data/ecuador-latest.osm.pbf
docker run -t -v ${PWD}:/data osrm/osrm-backend osrm-partition /data/ecuador-latest.osrm
docker run -t -v ${PWD}:/data osrm/osrm-backend osrm-customize /data/ecuador-latest.osrm
```

### 3. Iniciar Servicios

```powershell
docker-compose up -d
```

Servicios disponibles:
- **Backend Django**: http://localhost:8000
- **Frontend React**: http://localhost:3001
- **OSRM**: http://localhost:5000
- **RabbitMQ Management**: http://localhost:15672
- **PostgreSQL**: localhost:5433

### 4. Crear Migraciones Django

```powershell
docker-compose exec backend python manage.py makemigrations routes
docker-compose exec backend python manage.py migrate routes
```

## 📡 API Endpoints - Módulo de Rutas

### Zonas de Limpieza

#### Listar Zonas
```http
GET /api/routes/zones/
```

#### Crear Zona
```http
POST /api/routes/zones/
Content-Type: application/json

{
  "zone_name": "Centro Histórico",
  "description": "Zona central con alta densidad comercial",
  "zone_polygon": {
    "type": "Polygon",
    "coordinates": [[
      [-78.6200, -0.9350],
      [-78.6150, -0.9350],
      [-78.6150, -0.9400],
      [-78.6200, -0.9400],
      [-78.6200, -0.9350]
    ]]
  },
  "priority": 5,
  "frequency": "daily",
  "estimated_duration_minutes": 120,
  "assigned_team_size": 3
}
```

#### Zonas Activas
```http
GET /api/routes/zones/active/
```

#### Rutas de una Zona
```http
GET /api/routes/zones/{id}/routes/
```

### Rutas Optimizadas

#### Calcular Ruta
```http
POST /api/routes/routes/calculate/
Content-Type: application/json

{
  "waypoints": [
    {"lat": -0.9367, "lon": -78.6185},
    {"lat": -0.9380, "lon": -78.6200},
    {"lat": -0.9390, "lon": -78.6210}
  ],
  "optimize": false,
  "roundtrip": true
}
```

**Response:**
```json
{
  "success": true,
  "distance_km": "2.450",
  "duration_minutes": 8,
  "geometry": {
    "type": "LineString",
    "coordinates": [[...]]
  }
}
```

#### Optimizar Orden de Waypoints (TSP)
```http
POST /api/routes/routes/calculate/
Content-Type: application/json

{
  "waypoints": [
    {"lat": -0.9367, "lon": -78.6185},
    {"lat": -0.9380, "lon": -78.6200},
    {"lat": -0.9390, "lon": -78.6210},
    {"lat": -0.9400, "lon": -78.6220}
  ],
  "optimize": true,
  "roundtrip": true
}
```

**Response:**
```json
{
  "success": true,
  "distance_km": "2.250",
  "duration_minutes": 7,
  "optimized_order": [0, 2, 3, 1],
  "geometry": {...}
}
```

#### Crear y Guardar Ruta
```http
POST /api/routes/routes/create_from_waypoints/
Content-Type: application/json

{
  "route_name": "Ruta Centro Mañana",
  "zone_id": "uuid-de-zona",
  "waypoints": [
    {"lat": -0.9367, "lon": -78.6185},
    {"lat": -0.9380, "lon": -78.6200}
  ],
  "optimize": true,
  "waypoint_details": [
    {
      "address": "Av. Principal 123",
      "type": "collection",
      "notes": "Punto de recolección principal"
    },
    {
      "address": "Calle 24 de Mayo",
      "type": "disposal",
      "notes": "Centro de acopio"
    }
  ]
}
```

#### Punto Más Cercano en Red Vial
```http
POST /api/routes/routes/nearest_road/
Content-Type: application/json

{
  "lat": -0.9367,
  "lon": -78.6185,
  "number": 1
}
```

#### Estado del Servicio OSRM
```http
GET /api/routes/routes/health/
```

**Response:**
```json
{
  "osrm_status": "available",
  "healthy": true
}
```

## 🧪 Pruebas Manuales

### Test 1: Verificar OSRM

```powershell
curl http://localhost:5000/route/v1/driving/-78.6185,-0.9367;-78.6200,-0.9380?overview=full
```

### Test 2: Crear Zona de Limpieza

```python
import requests

url = "http://localhost:8000/api/routes/zones/"
data = {
    "zone_name": "Parque La Filantropica",
    "zone_polygon": {
        "type": "Polygon",
        "coordinates": [[
            [-78.6200, -0.9350],
            [-78.6150, -0.9350],
            [-78.6150, -0.9400],
            [-78.6200, -0.9400],
            [-78.6200, -0.9350]
        ]]
    },
    "priority": 4,
    "frequency": "daily"
}

response = requests.post(url, json=data, headers={
    "Authorization": "Bearer YOUR_TOKEN"
})
print(response.json())
```

### Test 3: Calcular Ruta Optimizada

```python
url = "http://localhost:8000/api/routes/routes/calculate/"
data = {
    "waypoints": [
        {"lat": -0.9367, "lon": -78.6185},
        {"lat": -0.9380, "lon": -78.6200},
        {"lat": -0.9390, "lon": -78.6210},
        {"lat": -0.9400, "lon": -78.6220}
    ],
    "optimize": True,
    "roundtrip": True
}

response = requests.post(url, json=data, headers={
    "Authorization": "Bearer YOUR_TOKEN"
})
result = response.json()

print(f"Distancia: {result['distance_km']} km")
print(f"Duración: {result['duration_minutes']} minutos")
print(f"Orden optimizado: {result['optimized_order']}")
```

## 🎯 Funcionalidades del Servicio OSRM

El `OSRMService` (`apps/routes/osrm_service.py`) proporciona:

1. **`calculate_route()`** - Calcular ruta directa entre puntos
2. **`optimize_route()`** - Optimizar orden de waypoints (TSP)
3. **`calculate_matrix()`** - Matriz de distancias/duraciones
4. **`match_route()`** - Map-matching de coordenadas GPS
5. **`nearest_road()`** - Punto más cercano en red vial
6. **`health_check()`** - Verificar disponibilidad del servicio

## 📊 Esquema de Base de Datos

### Tabla: rutas.cleaning_zones
- Zonas de limpieza con polígonos geográficos
- Prioridad, frecuencia, duración estimada
- Tamaño de equipo asignado

### Tabla: rutas.routes
- Rutas optimizadas calculadas con OSRM
- Geometría LineString
- Distancia total, duración estimada
- Algoritmo de optimización usado

### Tabla: rutas.route_waypoints
- Puntos de parada en cada ruta
- Orden secuencial
- Tipo: start, collection, disposal, end
- Tiempo estimado de servicio por punto

## 🔧 Solución de Problemas

### OSRM no responde

```powershell
# Verificar que el contenedor esté corriendo
docker-compose ps osrm

# Ver logs
docker-compose logs osrm

# Reiniciar servicio
docker-compose restart osrm
```

### Datos de mapa no cargados

Si OSRM no tiene datos:

```powershell
# Verificar volumen
docker volume inspect tesisandrea_osrm_data

# Copiar datos al volumen
docker cp ecuador-latest.osrm residuos_osrm:/data/
```

### Error en cálculo de ruta

- Verificar que las coordenadas estén en formato correcto (lon, lat)
- Verificar que los puntos estén dentro del área del mapa descargado
- Verificar conectividad entre puntos (no pueden estar en islas desconectadas)

## 🚀 Próximos Pasos

1. ✅ Migración SQL completa
2. ✅ Módulo de Rutas con OSRM
3. ⏳ Módulo de Tareas
4. ⏳ Módulo de Notificaciones
5. ⏳ Módulo de Reportes
6. ⏳ Tests con Behave/Cucumber

## 📚 Referencias

- [OSRM Documentation](http://project-osrm.org/docs/v5.24.0/api/)
- [GeoDjango Tutorial](https://docs.djangoproject.com/en/4.2/ref/contrib/gis/)
- [PostGIS Reference](https://postgis.net/docs/)
- [GeoFabrik Downloads](http://download.geofabrik.de/)

---

**Estado del Sistema**: 🟢 Rutas optimizadas con OSRM implementadas y funcionando

**Última actualización**: 29 de noviembre de 2025
