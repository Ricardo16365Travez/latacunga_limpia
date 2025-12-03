# 🎬 GUÍA DE INICIO RÁPIDO - Sistema Completado

## ⚡ Inicio en 3 Pasos

### Paso 1: Verificar y Cargar Datos
```powershell
# En PowerShell (Windows)
.\verify_system.ps1

# O en CMD (Windows)
verify_system.bat

# O manualmente:
docker-compose exec backend python load_sample_data.py
```

### Paso 2: Reiniciar Servicios
```bash
docker-compose down
docker-compose up -d
```

### Paso 3: Acceder a la Aplicación
- **Frontend:** http://localhost:3001
- **Backend:** http://localhost:8000/api
- **Docs:** http://localhost:8000/api/docs/

---

## 📱 Interfaz - Qué Esperar

### Página de Incidencias ✅
- **URL:** http://localhost:3001/incidencias
- **Datos esperados:** 16+ incidencias
- **Campos mostrados:** tipo, descripción, estado, dirección, ubicación
- **Funcionalidades:** Crear, editar, eliminar, buscar por estado

### Página de Tareas ✅
- **URL:** http://localhost:3001/tareas
- **Datos esperados:** 5+ tareas
- **Campos mostrados:** título, descripción, estado, prioridad, tipo, asignado a, ruta, fecha límite, progreso
- **Funcionalidades:** Crear, asignar, iniciar, completar, cambiar estado

### Página de Rutas ✅
- **URL:** http://localhost:3001/rutas
- **Datos esperados:** 4+ rutas
- **Campos mostrados:** nombre, estado, tipo de ruta, distancia, duración, puntos en mapa
- **Funcionalidades:** Crear, visualizar en mapa, optimizar

### Página de Notificaciones ✅
- **URL:** http://localhost:3001/notificaciones
- **Datos esperados:** 5+ notificaciones
- **Campos mostrados:** tipo, título, mensaje, leída, prioridad
- **Funcionalidades:** Marcar como leída, eliminar, filtrar

### Página de Reportes ✅
- **URL:** http://localhost:3001/reportes
- **Datos esperados:** Estadísticas compiladas (gráficas)
- **Campos mostrados:** total incidencias, por estado, por tipo, tareas, rutas
- **Funcionalidades:** Exportar PDF, Excel, ver estadísticas en tiempo real

---

## 🔍 Verificación de Endpoints

### Verificar que los endpoints retornan datos:

```powershell
# En PowerShell:
$headers = @{'Authorization' = 'Bearer dummy'}

# Incidencias (debe retornar 16+)
Invoke-WebRequest -Uri 'http://localhost:8000/api/incidents/?limit=5' -Headers $headers | Select-Object -ExpandProperty Content

# Tareas (debe retornar 5+)
Invoke-WebRequest -Uri 'http://localhost:8000/api/tasks/?limit=5' -Headers $headers | Select-Object -ExpandProperty Content

# Rutas (debe retornar 4+)
Invoke-WebRequest -Uri 'http://localhost:8000/api/routes/?limit=5' -Headers $headers | Select-Object -ExpandProperty Content

# Notificaciones (debe retornar 5+)
Invoke-WebRequest -Uri 'http://localhost:8000/api/notifications/?limit=5' -Headers $headers | Select-Object -ExpandProperty Content

# Reportes - Estadísticas compiladas
Invoke-WebRequest -Uri 'http://localhost:8000/api/reports/statistics/' -Headers $headers | Select-Object -ExpandProperty Content
```

---

## 🛠️ Solución de Problemas

### Error: "Error al cargar datos"
**Causa:** Backend no está corriendo o endpoint retorna 500  
**Solución:**
```bash
# Ver logs del backend
docker-compose logs backend

# Reiniciar backend
docker-compose restart backend

# O verificar que el puerto 8000 esté disponible
netstat -ano | findstr :8000
```

### Error: "No hay tareas registradas" (UI vacía)
**Causa:** Datos de prueba no se cargaron  
**Solución:**
```bash
docker-compose exec backend python load_sample_data.py
docker-compose restart backend frontend
```

### Error: "Cannot find module 'react-leaflet'"
**Causa:** Frontend necesita dependencias instaladas  
**Solución:**
```bash
docker-compose exec frontend npm install
docker-compose restart frontend
```

### Docker no responde
**Causa:** Daemon de Docker no está corriendo  
**Solución:**
```powershell
# Reiniciar Docker Desktop en Windows
# O ejecutar:
docker ps  # Verificar que funciona

# Si no, reiniciar Docker:
Restart-Service -Name "Docker for Windows" -Force
```

---

## 📊 Campos de Datos Mapeados

### Incidencias
| Nombre de Campo (Frontend) | Campo Backend | Tipo |
|---------------------------|--------------|------|
| tipo | incident_type | String |
| descripcion | description | String |
| estado | status | String |
| direccion | address | String |
| ubicacion | location (GeoJSON) | Object |

### Tareas
| Nombre de Campo (Frontend) | Campo Backend | Tipo |
|---------------------------|--------------|------|
| titulo | title | String |
| descripcion | description | String |
| estado | status | String |
| prioridad | priority | Integer |
| asignado_a | assigned_to | Object |
| ruta | route | Object |
| fecha_limite | scheduled_date | Date |
| progreso | completion_percentage | Integer |

### Rutas
| Nombre de Campo (Frontend) | Campo Backend | Tipo |
|---------------------------|--------------|------|
| nombre | route_name | String |
| estado | status | String |
| tipo_ruta | (inferido) | String |
| puntos_ruta | route_geometry | GeoJSON |
| distancia_km | total_distance_km | Decimal |
| duracion_estimada | estimated_duration_minutes | Integer |

### Notificaciones
| Nombre de Campo (Frontend) | Campo Backend | Tipo |
|---------------------------|--------------|------|
| tipo | notification_type | String |
| titulo | title | String |
| mensaje | message | String |
| leida | is_read | Boolean |
| prioridad | priority | String |

---

## 🚀 Endpoints Disponibles

### Incidencias
```
GET    /api/incidents/                 → Listar incidencias
POST   /api/incidents/                 → Crear incidencia
GET    /api/incidents/{id}/            → Obtener detalle
PATCH  /api/incidents/{id}/            → Actualizar
DELETE /api/incidents/{id}/            → Eliminar
```

### Tareas
```
GET    /api/tasks/                     → Listar tareas
POST   /api/tasks/                     → Crear tarea
GET    /api/tasks/{id}/                → Obtener detalle
PATCH  /api/tasks/{id}/                → Actualizar
DELETE /api/tasks/{id}/                → Eliminar
POST   /api/tasks/{id}/start/          → Iniciar tarea
POST   /api/tasks/{id}/complete/       → Completar tarea
```

### Rutas
```
GET    /api/routes/                    → Listar rutas
POST   /api/routes/                    → Crear ruta
GET    /api/routes/{id}/               → Obtener detalle
PATCH  /api/routes/{id}/               → Actualizar
DELETE /api/routes/{id}/               → Eliminar
GET    /api/zones/                     → Listar zonas de limpieza
```

### Notificaciones
```
GET    /api/notifications/             → Listar notificaciones del usuario
POST   /api/notifications/{id}/mark_as_read/  → Marcar como leída
POST   /api/notifications/mark_all_as_read/   → Marcar todas como leídas
GET    /api/notifications/unread_count/       → Contar no leídas
```

### Reportes
```
GET    /api/reports/                   → Listar reportes
POST   /api/reports/                   → Crear reporte
GET    /api/reports/statistics/        → Estadísticas compiladas (🆕)
```

---

## 📚 Documentación

- **Swagger UI:** http://localhost:8000/api/docs/
- **ReDoc:** http://localhost:8000/api/redoc/
- **Schema OpenAPI:** http://localhost:8000/api/schema/

---

## 💡 Tips

1. **Para ver logs en tiempo real:**
   ```bash
   docker-compose logs -f backend
   docker-compose logs -f frontend
   ```

2. **Para acceder a Django shell:**
   ```bash
   docker-compose exec backend python manage.py shell
   ```

3. **Para crear más datos de prueba:**
   ```bash
   docker-compose exec backend python manage.py shell
   # Dentro del shell:
   from backend.load_sample_data import create_sample_data
   create_sample_data()
   ```

4. **Para ver estado de base de datos:**
   ```bash
   docker-compose exec backend python manage.py check
   ```

---

## ✅ Checklist Final

- [ ] Docker-compose está corriendo (`docker-compose ps` muestra 5+ containers)
- [ ] Backend responde en http://localhost:8000/api
- [ ] Frontend carga en http://localhost:3001
- [ ] Página de incidencias muestra 16+ incidencias
- [ ] Página de tareas muestra 5+ tareas
- [ ] Página de rutas muestra 4+ rutas
- [ ] Página de notificaciones muestra 5+ notificaciones
- [ ] Página de reportes muestra estadísticas compiladas
- [ ] Puedes crear una nueva incidencia
- [ ] Puedes crear una nueva tarea
- [ ] Puedes marcar notificaciones como leídas

---

## 🎓 Ejemplo de Respuesta API

### GET /api/incidents/?limit=1
```json
{
  "count": 16,
  "next": "http://localhost:8000/api/incidents/?limit=1&offset=1",
  "previous": null,
  "results": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "tipo": "punto_acopio",
      "descripcion": "Punto de acopio reportado",
      "estado": "incidente_valido",
      "direccion": "Calle Principal 123, Latacunga",
      "ubicacion": {
        "type": "Point",
        "coordinates": [-0.9315, -0.9369]
      },
      "lat": -0.9369,
      "lon": -0.9315,
      "photo_url": null,
      "created_at": "2025-12-02T00:00:00Z",
      "updated_at": "2025-12-02T00:00:00Z"
    }
  ]
}
```

---

**¡Sistema listo para usar! 🚀**
