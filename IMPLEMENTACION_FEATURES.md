# Implementación de Features - EPAGAL Latacunga

## Feature 1: Generación de Rutas Optimizadas

### Algoritmo

```
INPUT: Zona (oriental/occidental)

1. OBTENER INCIDENCIAS PENDIENTES
   ├─ Query: SELECT * FROM incidencias 
   │         WHERE zona = ? AND estado = 'pendiente'
   ├─ Ordenar por gravedad DESC (críticas primero)
   └─ Output: Lista de incidencias

2. CALCULAR RUTA ÓPTIMA (TSP - Traveling Salesman Problem)
   ├─ Entrada: Coordenadas [lat, lon] de cada incidencia
   ├─ Llamar OSRM: /route/v1/driving/lon,lat;lon,lat
   ├─ OSRM retorna: matriz de distancias y duración
   └─ Output: Orden optimizado de visita

3. CALCULAR CAMIONES NECESARIOS
   ├─ Calcular suma_gravedad de incidencias
   ├─ Dividir entre capacidad camión (15 puntos)
   └─ Output: Cantidad de camiones requeridos

4. PERSISTIR RUTA
   ├─ INSERT INTO rutas_generadas (zona, suma_gravedad, camiones_usados, ...)
   ├─ Para cada incidencia en orden:
   │  └─ INSERT INTO rutas_detalles (ruta_id, orden, incidencia_id, ...)
   ├─ UPDATE incidencias SET estado = 'asignada'
   └─ Output: RutaGenerada con ID

RETURN: RutaGenerada JSON
```

### Ejemplo de Ejecución

```
Entrada:
  zona = 'oriental'

Incidencias disponibles:
  - ID 5: Acopio lleno, gravedad 8, (-0.9322, -78.6170)
  - ID 7: Escombros, gravedad 6, (-0.9350, -78.6150)
  - ID 12: Zona crítica, gravedad 9, (-0.9300, -78.6180)

Llamada OSRM:
  GET /route/v1/driving/-78.6170,-0.9322;-78.6150,-0.9350;-78.6180,-0.9300

Respuesta OSRM:
  {
    "waypoint_order": [2, 0, 1],  # Orden óptimo: ID12 → ID5 → ID7
    "distance": 15000,             # 15 km
    "duration": 9000               # 9 minutos
  }

Cálculo de camiones:
  suma_gravedad = 8 + 6 + 9 = 23
  camiones = ceil(23 / 15) = 2

Salida:
  {
    "id": 42,
    "zona": "oriental",
    "suma_gravedad": 23,
    "camiones_usados": 2,
    "costo_total": 15000,
    "duracion_estimada": "00:09:00",
    "estado": "planeada",
    "detalles": [
      {
        "orden": 1,
        "incidencia_id": 12,
        "lat": -0.9300,
        "lon": -78.6180,
        "tipo_punto": "incidencia",
        "camion_tipo": "compactador"
      },
      {
        "orden": 2,
        "incidencia_id": 5,
        "lat": -0.9322,
        "lon": -78.6170,
        ...
      },
      ...
    ]
  }
```

---

## Feature 2: Sistema de Incidencias

### Ciclo de Vida

```
       REPORTAR
         │
         ▼
    ┌─────────┐
    │PENDIENTE│  ← Usuario reporta incidencia
    └────┬────┘     (foto, ubicación, descripción)
         │
         │ Sistema calcula zona automáticamente
         │ Notificación a operadores
         │
         ▼
    ┌─────────┐
    │ASIGNADA │  ← Incluida en ruta generada
    └────┬────┘     Asignado a conductor
         │
         │ Conductor inicia recolección
         │
         ▼
    ┌─────────┐
    │RESUELTA │  ← Conductor marca como completado
    └─────────┘    Sistema registra hora de resolución

Campos validados:
  - tipo: ['acopio_lleno', 'animal_muerto', 'escombros', 'zona_critica']
  - gravedad: 1-10 (escala de urgencia)
  - lat/lon: Coordenadas válidas en Latacunga
  - descripción: 10-500 caracteres

Lógica de Zonas:
  IF lon < -78.6170 THEN zona = 'oriental'
  ELSE zona = 'occidental'
```

### Cálculo de Gravedad Ajustada

```
Base: Usuario proporciona gravedad (1-10)

Ajustes (bonificadores):
  IF descripción contiene 'urgente' → +2
  IF descripción contiene 'crítico' → +3
  IF tipo = 'zona_critica' → +2
  IF hora = 'noche' AND gravedad >= 5 → +1

Ejemplo:
  Base: 5
  Descripción: "Situación urgente en zona crítica"
  → +2 (urgente) +3 (crítico) = 10 final

Capped: min 1, max 10
```

---

## Feature 3: Asignación de Conductores

### Algoritmo de Matching

```
INPUT: Ruta generada

1. OBTENER CONDUCTORES DISPONIBLES
   ├─ SELECT * FROM conductores
   │  WHERE estado = 'disponible'
   │  AND zona_preferida IN (ruta.zona, 'ambas')
   └─ Ordenar por rating de desempeño DESC

2. ASIGNAR CONDUCTORES
   ├─ Cantidad necesaria: ruta.camiones_usados
   ├─ Para cada conductor:
   │  ├─ Determinar tipo de vehículo según incidencias
   │  ├─ INSERT INTO asignaciones_conductores
   │  ├─ UPDATE conductores SET estado = 'ocupado'
   │  └─ Enviar notificación push (FCM)
   └─ Output: Asignaciones creadas

3. TRANSACCIONES
   ├─ ATOMIC: Si falla alguna asignación, rollback de todas
   ├─ Consistencia de estado
   └─ Logging de auditoría

RETURN: AsignacionConductor[] con IDs de asignación
```

### Tipos de Camiones por Incidencia

```
acopio_lleno  → compactador (capacidad 15 pts)
escombros     → volqueta (capacidad 20 pts)
animal_muerto → recolector (capacidad 10 pts)
zona_critica  → compactador (capacidad 15 pts)

Capacidades:
  recolector  = 10 puntos gravedad
  compactador = 15 puntos gravedad
  volqueta    = 20 puntos gravedad
```

---

## Feature 4: Tracking en Tiempo Real

### Arquitectura

```
┌─────────────┐
│  GPS Device │  (Conductor en vehículo)
└──────┬──────┘
       │ POST /api/tracking/update-location
       │ {lat, lon, speed, accuracy, timestamp}
       │
       ▼
┌─────────────────────────┐
│   Backend (FastAPI)     │
│  ├─ Validar ubicación   │
│  ├─ Guardar en BD       │
│  ├─ Broadcast a otros   │
│  └─ Calcular ETA        │
└────────────┬────────────┘
             │
    ┌────────┴────────┐
    │                 │
    ▼                 ▼
┌──────────┐     ┌──────────────┐
│  Database│     │  WebSocket   │
│  (Buffer)│     │  (Live Push) │
└──────────┘     └──────────────┘
                      │
                      ▼
              ┌────────────────┐
              │  Admin Panel   │
              │  (Mapa en vivo)│
              └────────────────┘
```

### Formato de Actualización

```json
{
  "conductor_id": 5,
  "ruta_id": 42,
  "lat": -0.9322,
  "lon": -78.6170,
  "speed": 45,           // km/h
  "accuracy": 5,         // metros
  "timestamp": "2026-01-11T14:30:00Z",
  "status": "en_ruta"    // 'en_ruta' | 'en_punto' | 'completado'
}

Respuesta:
{
  "success": true,
  "message": "Ubicación actualizada",
  "eta_siguiente": "2026-01-11T14:35:00Z"  // ETA próximo punto
}
```

### Cálculo de ETA

```
Ubicación actual: punto A
Próximo punto de recolección: punto B

Distancia A→B: d (de OSRM)
Velocidad promedio: v (últimas mediciones)

ETA = now + (d / v)

Ejemplo:
  Distancia: 2.5 km
  Velocidad: 40 km/h
  ETA = 2.5 / 40 = 0.0625 horas = 3.75 minutos ≈ 4 minutos
```

---

## Feature 5: Reportes y Estadísticas

### Métricas Calculadas

```sql
-- Total de incidencias por mes
SELECT DATE_TRUNC('month', reportado_en) AS mes,
       COUNT(*) AS total,
       AVG(gravedad) AS gravedad_promedio
FROM incidencias
GROUP BY DATE_TRUNC('month', reportado_en)
ORDER BY mes DESC;

-- Incidencias por tipo
SELECT tipo, COUNT(*) AS cantidad, AVG(gravedad) AS gravedad
FROM incidencias
GROUP BY tipo;

-- Eficiencia de resolución
SELECT 
  COUNT(*) AS total,
  COUNT(CASE WHEN estado = 'resuelta' THEN 1 END) AS resueltas,
  ROUND(COUNT(CASE WHEN estado = 'resuelta' THEN 1 END)::numeric / 
        COUNT(*) * 100, 2) AS tasa_resolucion
FROM incidencias;

-- Tiempo promedio de resolución
SELECT AVG(EXTRACT(EPOCH FROM (fecha_resolucion - reportado_en)) / 3600) 
       AS horas_promedio
FROM incidencias
WHERE estado = 'resuelta';

-- Desempeño por zona
SELECT zona, COUNT(*) AS incidencias, AVG(gravedad) AS gravedad_promedio
FROM incidencias
GROUP BY zona;
```

### Dashboard Visualizations

```
1. Pie Chart: Distribución por tipo de incidencia
2. Line Chart: Tendencia mensual de incidencias
3. Bar Chart: Incidencias por zona
4. KPI Cards: Total, Pendientes, Resueltas, Tasa resolución
5. Table: Últimas 10 incidencias con filtros
6. Map: Mapa de calor de puntos críticos
```

---

## Feature 6: Notificaciones Push

### FCM Integration

```python
# Backend: Firebase Cloud Messaging

from firebase_admin import messaging

def enviar_notificacion_asignacion(conductor_id: int, ruta_id: int):
    """Envía notificación push al conductor de nueva asignación."""
    
    conductor = db.query(Conductor).get(conductor_id)
    fcm_token = conductor.fcm_token
    
    message = messaging.Message(
        notification=messaging.Notification(
            title="Nueva Ruta Asignada",
            body=f"Ruta #{ruta_id} - Ver detalles"
        ),
        data={
            "ruta_id": str(ruta_id),
            "action": "open_ruta"
        },
        token=fcm_token
    )
    
    response = messaging.send(message)
    logger.info(f"Push enviado: {response}")
```

### Tipos de Notificaciones

```
1. ASIGNACION_RUTA
   - Título: "Nueva ruta asignada"
   - Data: ruta_id, zona, incidencias_count

2. INCIDENCIA_CRITICA
   - Título: "Incidencia crítica reportada"
   - Data: incidencia_id, ubicación
   - Destinatarios: Todos los conductores

3. ESTIMADO_ACTUALIZADO
   - Título: "ETA actualizado"
   - Data: nuevo_eta
   - Destinatarios: Admin, Conductor

4. RUTA_COMPLETADA
   - Título: "Ruta completada exitosamente"
   - Data: resumen_ruta
```

---

## Conclusión

Las features implementadas demuestran:
- ✅ Algoritmos complejos (TSP, matching)
- ✅ Integración con APIs externas (OSRM, FCM)
- ✅ Real-time processing
- ✅ Validación exhaustiva
- ✅ Transaccionalidad ACID
- ✅ Auditoría y logging
