# 📋 Guía de Endpoints - Backend Externo Go (latacunga_clean_app)

## ℹ️ Información Importante

El backend utilizado es un sistema de **microservicios en Go** con arquitectura de eventos (RabbitMQ).

**Repositorio**: https://github.com/Andres09xZ/latacunga_clean_app.git  
**URL de Producción**: https://epagal-backend-routing-latest.onrender.com  
**Versión API**: `/api/v1`

---

## 🏗️ Arquitectura de Microservicios

```
┌─────────────────────────────────────────────┐
│        Load Balancer / Proxy (Render)       │
│ https://epagal-backend-routing-latest...   │
└──────────────────┬──────────────────────────┘
                   │
    ┌──────────────┼──────────────┬──────────────┬──────────────┐
    │              │              │              │              │
    ▼              ▼              ▼              ▼              ▼
┌────────────┐ ┌────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│Auth Service│ │Fleet Service│ │ Incident Svc │ │Scheduler Svc │ │Operations Svc│
│  :8080     │ │  :8081     │ │   :8082     │ │  :8083      │ │  :8085      │
└────────────┘ └────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
```

---

## 🔐 AUTENTICACIÓN (Auth Service)

### Registro de Operador (Admin)
```http
POST /api/v1/auth/operators
Content-Type: application/json

{
  "full_name": "Juan Pérez",
  "username": "juan_perez",
  "password": "secure_password",
  "email": "juan@example.com",
  "license_id": "ABC123456",
  "preferred_zone_id": 1,
  "can_drive_lateral": true,
  "can_drive_compactor": false,
  "role": "operator"
}

Response 201:
{
  "id": "uuid",
  "full_name": "Juan Pérez",
  "username": "juan_perez",
  "email": "juan@example.com",
  "role": "operator",
  "active": true
}
```

### Registro de Ciudadano (OTP)
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "phone": "+593991234567",
  "email": "citizen@example.com"
}

Response 201:
{
  "id": "uuid",
  "phone": "+593991234567",
  "email": "citizen@example.com"
}
```

### Login (Operador + Ciudadano)
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "juan@example.com",
  "password": "secure_password"
}

Response 200:
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "user": {
    "id": "uuid",
    "role": "operator"
  }
}
```

---

## 🚚 FLOTA (Fleet Service: 8081)

### Camiones (Trucks)

#### Listar camiones
```http
GET /api/v1/trucks
GET /api/v1/trucks?status=DISPONIBLE
GET /api/v1/trucks?type=CARGA_LATERAL

Response 200:
{
  "trucks": [
    {
      "id": 1,
      "plate": "GYE-1234",
      "type": "CARGA_LATERAL",
      "status": "DISPONIBLE",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "count": 1
}
```

#### Crear camión
```http
POST /api/v1/trucks
Content-Type: application/json
Authorization: Bearer <JWT_TOKEN>

{
  "plate": "GYE-1234",
  "type": "CARGA_LATERAL",
  "status": "DISPONIBLE"
}

Response 201:
{
  "id": 1,
  "plate": "GYE-1234",
  "type": "CARGA_LATERAL",
  "status": "DISPONIBLE"
}
```

### Conductores (Drivers)

#### Listar conductores
```http
GET /api/v1/drivers

Response 200:
{
  "drivers": [
    {
      "id": "uuid",
      "full_name": "Juan Pérez",
      "license_id": "ABC123456",
      "status": "ACTIVE"
    }
  ],
  "count": 1
}
```

### Turnos (Shifts)

#### Clock-in (Iniciar turno)
```http
POST /api/v1/shifts/clock-in
Content-Type: application/json
Authorization: Bearer <JWT_TOKEN>

{
  "driver_id": "uuid",
  "truck_plate": "GYE-1234"
}

Response 200:
{
  "shift_id": "uuid",
  "message": "Turno iniciado exitosamente"
}
```

#### Clock-out (Finalizar turno)
```http
POST /api/v1/shifts/clock-out
Content-Type: application/json
Authorization: Bearer <JWT_TOKEN>

{
  "shift_id": "uuid"
}

Response 200:
{
  "message": "Turno finalizado exitosamente"
}
```

---

## 📍 INCIDENTES (Incident Service: 8082)

### Crear incidente (Offline-first)
```http
POST /api/v1/incidents
Content-Type: application/json
Authorization: Bearer <JWT_TOKEN>
Idempotency-Key: unique-key-for-this-incident

{
  "type": "punto_acopio",
  "title": "Basurero sin recoger",
  "description": "Basurero lleno en zona residencial",
  "latitude": -0.9276,
  "longitude": -78.6245,
  "address": "Calle Principal y 5 de Junio"
}

Response 201:
{
  "id": "uuid",
  "type": "punto_acopio",
  "title": "Basurero sin recoger",
  "status": "emitido",
  "latitude": -0.9276,
  "longitude": -78.6245,
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Tipos válidos**:
- `punto_acopio` - Punto de acopio de residuos
- `zona_critica` - Zona crítica de contaminación
- `animal_muerto` - Animal muerto encontrado
- `zona_reciclaje` - Área de reciclaje

### Listar incidentes
```http
GET /api/v1/incidents
GET /api/v1/incidents?skip=0&limit=10

Response 200:
{
  "incidents": [...],
  "count": 50,
  "total": 500
}
```

---

## 📋 ÓRDENES DE TRABAJO (Operations Service: 8085)

### Obtener órdenes activas
```http
GET /api/v1/driver/orders/active?driver_id=uuid
Authorization: Bearer <JWT_TOKEN>

Response 200:
{
  "orders": [
    {
      "id": "uuid",
      "status": "planned",
      "total_stops": 5,
      "completed_stops": 0,
      "route_polyline": "...",
      "stops": [
        {
          "id": "uuid",
          "latitude": -0.9276,
          "longitude": -78.6245,
          "address": "Calle Principal",
          "status": "pending",
          "sequence_order": 1
        }
      ]
    }
  ]
}
```

### Iniciar orden de trabajo
```http
POST /api/v1/driver/orders/{order_id}/start
Authorization: Bearer <JWT_TOKEN>

Response 200:
{
  "status": "started",
  "message": "Orden de trabajo iniciada"
}
```

### Completar parada
```http
POST /api/v1/driver/stops/{stop_id}/complete
Content-Type: application/json
Authorization: Bearer <JWT_TOKEN>

{
  "notes": "Residuo recogido exitosamente"
}

Response 200:
{
  "status": "completed",
  "stop_id": "uuid",
  "message": "Parada completada"
}
```

### Finalizar orden de trabajo
```http
POST /api/v1/driver/orders/{order_id}/finish
Authorization: Bearer <JWT_TOKEN>

Response 200:
{
  "status": "completed",
  "message": "Orden de trabajo finalizada"
}
```

---

## 📊 ESTADÍSTICAS (Fleet Service)

### Métricas de zona
```http
GET /api/v1/zones/{zone_id}/metrics
Authorization: Bearer <JWT_TOKEN>

Response 200:
{
  "zone_id": 1,
  "status": "ACUMULANDO",
  "score": 75.5,
  "threshold": 80.0,
  "last_trigger": "2024-01-15T08:00:00Z"
}
```

---

## ✅ Códigos de Estado HTTP

| Código | Significado |
|--------|------------|
| 200 | OK - Solicitud exitosa |
| 201 | Created - Recurso creado exitosamente |
| 400 | Bad Request - Datos inválidos |
| 401 | Unauthorized - Token inválido o expirado |
| 403 | Forbidden - Acceso denegado |
| 404 | Not Found - Recurso no encontrado |
| 409 | Conflict - Conflicto (ej: ID duplicado) |
| 422 | Unprocessable Entity - Validación de datos fallida |
| 500 | Internal Server Error - Error del servidor |

---

## 🔄 Headers Requeridos

Todas las solicitudes **autenticadas** requieren:
```
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
```

Para **offline-first** (incidentes):
```
Idempotency-Key: <unique-key>
```

---

## 🧪 Pruebas E2E

El repositorio incluye prueba automatizada completa:
```bash
# En desarrollo local
go run e2e.go

# Script PowerShell
.\run_e2e_test.ps1

# Script Bash
./run_e2e_test.sh
```

---

## 📚 Referencias

- [Repositorio Backend](https://github.com/Andres09xZ/latacunga_clean_app)
- [E2E README](https://github.com/Andres09xZ/latacunga_clean_app/blob/main/E2E_README.md)
- [Fleet API Reference](https://github.com/Andres09xZ/latacunga_clean_app/blob/main/FLEET_API_REFERENCE.md)

