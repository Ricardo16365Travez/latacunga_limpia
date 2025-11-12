# Documentación del Sistema de Gestión de Residuos Latacunga

## Diagrama de Arquitectura

```mermaid
flowchart TD
    Citizen[👤 Ciudadano] -->|Reporte con ubicación y foto| Reports[📝 API / reports]
    Reports -->|Genera tarea| Tasks[⚙️ Tareas y Asignación]
    Tasks -->|Asignar a operador| Actors[👷 Operadores / Trabajadores]
    Actors -->|Actualiza ubicación| Locations[📍 Ubicaciones PostGIS]
    Tasks --> Routes[🗺️ Optimización de Rutas]
    Routes --> Dashboard[📊 Panel Administrativo Django-React]
    Dashboard --> Notifications[📱 Notificaciones a usuarios]
    Reports --> Audit[📋 Auditoría y Registro]
    Reports --> Outbox[🔄 Sincronización Outbox / Sync Ops]
    Outbox --> Citizen

    style Citizen fill:#E6F7FF,stroke:#1E90FF,stroke-width:2px
    style Reports fill:#E0FFE0,stroke:#32CD32,stroke-width:2px
    style Tasks fill:#FFFFE0,stroke:#DAA520,stroke-width:2px
    style Routes fill:#FFDAB9,stroke:#CD853F,stroke-width:2px
    style Dashboard fill:#E6E6FA,stroke:#6A5ACD,stroke-width:2px
    style Audit fill:#FFF0F5,stroke:#DC143C,stroke-width:2px
```

## Flujo de Datos Principal

### 1. Proceso de Reporte Ciudadano

1. **Creación del Reporte**
   - Ciudadano envía reporte desde app móvil/web
   - Incluye: descripción, tipo, ubicación GPS, foto
   - Estado inicial: `ENVIADO`

2. **Verificación Administrativa**
   - Admin revisa el reporte
   - Puede cambiar estado a `VERIFICADO` o `RECHAZADO`
   - Si es verificado, puede convertirse en tarea

3. **Generación de Tarea**
   - Reporte verificado genera tarea automáticamente
   - Tipo de tarea: `RECOLECCION` o `LIMPIEZA`
   - Estado inicial: `PENDIENTE_ASIGNAR`

4. **Asignación y Ejecución**
   - Sistema asigna tarea a operador disponible
   - Operador recibe notificación
   - Puede actualizar estado: `EN_CURSO` → `COMPLETADA`

### 2. Sincronización Offline

El sistema implementa el patrón **Outbox** para garantizar consistencia:

```sql
-- Ejemplo de inserción con patrón Outbox
BEGIN;
  INSERT INTO reports (...) VALUES (...);
  INSERT INTO outbox_events (event_type, payload, aggregate_id) 
  VALUES ('report.created', '{"report_id": "..."}', '...');
COMMIT;
```

### 3. Optimización de Rutas

Algoritmo implementado para optimización:

1. **Agrupación Geográfica**: Agrupa tareas por proximidad
2. **Cálculo de Distancias**: Usa PostGIS para calcular distancias reales
3. **Optimización**: Implementa algoritmo de vecino más cercano
4. **Asignación**: Asigna ruta completa a operador

## Base de Datos

### Entidades Principales

#### Users (Autenticación)
```sql
CREATE TYPE user_role AS ENUM ('user','admin','operador','trabajador','super_admin');

CREATE TABLE users (
  id UUID PRIMARY KEY,
  email TEXT UNIQUE,
  phone TEXT UNIQUE,
  role user_role DEFAULT 'user',
  status TEXT DEFAULT 'ACTIVE'
);
```

#### Reports (Reportes Ciudadanos)
```sql
CREATE TYPE report_type AS ENUM ('ZONA_CRITICA','PUNTO_ACOPIO_LLENO');
CREATE TYPE report_state AS ENUM ('ENVIADO','PENDIENTE','VERIFICADO','EMITIDO','RECHAZADO','COMPLETADO');

CREATE TABLE reports (
  id UUID PRIMARY KEY,
  reporter_id UUID REFERENCES users(id),
  type report_type NOT NULL,
  description TEXT NOT NULL,
  location GEOGRAPHY(POINT, 4326) NOT NULL,
  state report_state DEFAULT 'ENVIADO'
);
```

#### Tasks (Tareas Operativas)
```sql
CREATE TYPE task_type AS ENUM ('RECOLECCION','LIMPIEZA');
CREATE TYPE task_state AS ENUM ('PENDIENTE_ASIGNAR','ASIGNADA','EN_CURSO','COMPLETADA','FALLIDA','CANCELADA');

CREATE TABLE tasks (
  id UUID PRIMARY KEY,
  report_id UUID REFERENCES reports(id),
  actor_id UUID REFERENCES actors(id),
  type task_type NOT NULL,
  state task_state DEFAULT 'PENDIENTE_ASIGNAR'
);
```

### Índices Importantes

```sql
-- Índices geoespaciales
CREATE INDEX idx_reports_location ON reports USING GIST (location);
CREATE INDEX idx_actor_locations_location ON actor_locations USING GIST (location);

-- Índices para consultas frecuentes
CREATE INDEX idx_reports_state ON reports (state);
CREATE INDEX idx_tasks_state ON tasks (state);
CREATE INDEX idx_reports_created_at ON reports (created_at);
```

## API REST

### Endpoints de Reportes

#### Listar Reportes
```http
GET /api/reports/
Authorization: Bearer {token}

Query Parameters:
- state: ENVIADO|PENDIENTE|VERIFICADO|EMITIDO|RECHAZADO|COMPLETADO
- type: ZONA_CRITICA|PUNTO_ACOPIO_LLENO
- bounds: bbox para filtro geográfico
- page: número de página
```

#### Crear Reporte
```http
POST /api/reports/
Content-Type: multipart/form-data

{
  "type": "ZONA_CRITICA",
  "description": "Basura acumulada en la esquina",
  "latitude": -0.9363,
  "longitude": -78.6166,
  "photo": [archivo]
}
```

### Endpoints de Tareas

#### Asignar Tarea
```http
PATCH /api/tasks/{id}/assign/
{
  "actor_id": "uuid-del-operador"
}
```

#### Actualizar Estado
```http
PATCH /api/tasks/{id}/
{
  "state": "EN_CURSO"
}
```

## Frontend React

### Estructura de Componentes

```
src/
├── components/          # Componentes reutilizables
│   ├── Map/            # Componentes de mapa
│   ├── Forms/          # Formularios
│   └── UI/             # Elementos de interfaz
├── pages/              # Páginas principales
│   ├── Dashboard/      # Panel principal
│   ├── Reports/        # Gestión de reportes
│   ├── Tasks/          # Gestión de tareas
│   └── Auth/           # Autenticación
├── hooks/              # Custom hooks
├── services/           # Servicios API
├── types/              # Tipos TypeScript
├── utils/              # Utilidades
└── App.tsx            # Componente principal
```

### Gestión de Estado

- **React Query**: Para estado de servidor (cache, refetch, etc.)
- **React Hook Form**: Para formularios
- **Context API**: Para estado global de autenticación

### Componente de Mapa

```typescript
import { MapContainer, TileLayer, Marker } from 'react-leaflet';

const ReportsMap: React.FC = () => {
  const { data: reports } = useReports();

  return (
    <MapContainer center={[-0.9363, -78.6166]} zoom={13}>
      <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      {reports?.map(report => (
        <Marker 
          key={report.id} 
          position={[report.latitude, report.longitude]}
        />
      ))}
    </MapContainer>
  );
};
```

## Deployment

### Desarrollo Local
```bash
git clone https://github.com/AndreaDu2001/Tesis-.git
cd Tesis-
docker-compose up --build
```

### Producción

1. **Variables de Entorno**
   ```bash
   DEBUG=False
   SECRET_KEY=clave-super-secreta
   DATABASE_URL=postgresql://user:pass@host:port/db
   REDIS_URL=redis://host:port/0
   ```

2. **Configuración SSL**
   - Configurar certificados en Nginx
   - Actualizar `ALLOWED_HOSTS` en Django

3. **Monitoring**
   - Logs centralizados
   - Métricas de performance
   - Alertas automáticas

## Testing

### Backend Tests
```bash
docker-compose exec backend python manage.py test
```

### Frontend Tests
```bash
docker-compose exec frontend npm test
```

### Integration Tests
- Tests de API completos
- Tests de flujo de usuario
- Tests de carga con datos reales

## Performance

### Optimizaciones Implementadas

1. **Base de Datos**
   - Índices geoespaciales optimizados
   - Consultas con LIMIT y paginación
   - Conexiones pooling

2. **API**
   - Caché con Redis
   - Compresión gzip
   - Lazy loading de relaciones

3. **Frontend**
   - Code splitting
   - Caché de componentes
   - Optimización de imágenes

### Métricas de Performance

- **Tiempo de respuesta API**: < 200ms
- **Carga inicial frontend**: < 3s
- **Búsquedas geoespaciales**: < 500ms
- **Concurrent users**: 100+ usuarios simultáneos