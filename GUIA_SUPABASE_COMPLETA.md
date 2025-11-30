# 📋 GUÍA COMPLETA DE INSTALACIÓN - SUPABASE

## 🗄️ TABLAS PARA SUPABASE

### Resumen de Esquemas y Tablas

**Total de Esquemas:** 6
**Total de Tablas:** 21
**Total de Índices:** 40+
**Total de Triggers:** 9
**Total de Vistas:** 3

---

## 📊 LISTA COMPLETA DE TABLAS

### 1️⃣ ESQUEMA: incidentes (6 tablas)
```
✓ incidentes.incidents                    - Incidencias reportadas
✓ incidentes.incident_attachments         - Archivos adjuntos
✓ incidentes.incident_events              - Eventos de incidencias
✓ incidentes.idempotency_keys            - Claves de idempotencia
✓ incidentes.outbox_events               - Eventos para publicación
✓ validacion.incidentes_pendientes (VISTA) - Incidencias pendientes
```

### 2️⃣ ESQUEMA: rutas (3 tablas)
```
✓ rutas.cleaning_zones        - Zonas de limpieza con polígonos
✓ rutas.routes               - Rutas optimizadas
✓ rutas.route_waypoints      - Puntos de parada de rutas
```

### 3️⃣ ESQUEMA: tareas (3 tablas + 1 vista)
```
✓ tareas.tasks                        - Tareas de limpieza
✓ tareas.task_checkpoints            - Checkpoints de tareas
✓ tareas.task_assignments_history    - Historial de asignaciones
✓ tareas.v_active_tasks (VISTA)      - Tareas activas
```

### 4️⃣ ESQUEMA: notificaciones (3 tablas)
```
✓ notificaciones.notifications              - Notificaciones del sistema
✓ notificaciones.device_tokens             - Tokens para push notifications
✓ notificaciones.notification_preferences  - Preferencias de usuario
```

### 5️⃣ ESQUEMA: reportes (2 tablas)
```
✓ reportes.reports      - Reportes generados
✓ reportes.statistics   - Estadísticas precalculadas
```

### 6️⃣ ESQUEMA: auth (Supabase nativo)
```
✓ auth.users            - Usuarios (manejado por Supabase)
```

---

## 🚀 PASOS DE INSTALACIÓN EN SUPABASE

### Paso 1: Acceder a Supabase
1. Ve a https://supabase.com
2. Accede a tu proyecto
3. Ve a **SQL Editor**

### Paso 2: Ejecutar el Script SQL
1. Abre el archivo `database/SUPABASE_COMPLETE_SCHEMA.sql`
2. Copia todo el contenido
3. Pégalo en el SQL Editor de Supabase
4. Haz clic en **Run** (o presiona Ctrl+Enter)

### Paso 3: Verificar la Creación
Ejecuta este comando para verificar:

```sql
-- Verificar esquemas
SELECT schema_name 
FROM information_schema.schemata 
WHERE schema_name IN ('incidentes', 'validacion', 'rutas', 'tareas', 'notificaciones', 'reportes');

-- Contar tablas por esquema
SELECT 
    schemaname,
    COUNT(*) as total_tables
FROM pg_tables
WHERE schemaname IN ('incidentes', 'rutas', 'tareas', 'notificaciones', 'reportes')
GROUP BY schemaname
ORDER BY schemaname;

-- Verificar índices
SELECT 
    schemaname,
    COUNT(*) as total_indexes
FROM pg_indexes
WHERE schemaname IN ('incidentes', 'rutas', 'tareas', 'notificaciones', 'reportes')
GROUP BY schemaname;
```

---

## 🔧 CONFIGURACIÓN DE DJANGO CON SUPABASE

### 1. Variables de Entorno (.env)
```env
# Supabase Database
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=tu_password_supabase
DB_HOST=db.tu-proyecto.supabase.co
DB_PORT=5432

# Supabase API (opcional para integración directa)
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu_supabase_anon_key
SUPABASE_SERVICE_KEY=tu_supabase_service_role_key
```

### 2. Aplicar Migraciones de Django
```bash
# Con Docker
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate

# Sin Docker (en entorno virtual)
python manage.py makemigrations
python manage.py migrate
```

---

## 📝 DATOS DE EJEMPLO (OPCIONAL)

### Insertar usuario de prueba
```sql
-- Nota: En Supabase, los usuarios se crean con la API de Auth
-- Pero puedes referenciarlos en tus tablas usando el UUID
```

### Insertar zona de limpieza
```sql
INSERT INTO rutas.cleaning_zones (name, zone_polygon, zone_type, priority, frequency)
VALUES (
    'Zona Centro',
    ST_GeomFromText('POLYGON((-78.6180 -0.9370, -78.6150 -0.9370, -78.6150 -0.9340, -78.6180 -0.9340, -78.6180 -0.9370))', 4326),
    'residential',
    3,
    'daily'
);
```

### Insertar incidencia
```sql
INSERT INTO incidentes.incidents (
    incident_id, title, description, incident_type, severity, status, 
    location, address
)
VALUES (
    'INC-' || LPAD(nextval('incidentes.incidents_id_seq')::text, 6, '0'),
    'Basura acumulada',
    'Gran cantidad de basura en la esquina',
    'waste_accumulation',
    'medium',
    'pending',
    ST_GeomFromText('POINT(-78.6165 -0.9355)', 4326),
    'Av. Unidad Nacional y Calle Quito'
);
```

### Insertar tarea
```sql
INSERT INTO tareas.tasks (
    task_id, title, description, status, priority, 
    scheduled_date, estimated_duration
)
VALUES (
    'TASK-001',
    'Limpieza Zona Centro',
    'Recolección de residuos en zona centro',
    'pending',
    3,
    CURRENT_DATE + INTERVAL '1 day',
    120
);
```

---

## 🔍 CONSULTAS ÚTILES

### Ver todas las tablas creadas
```sql
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname IN ('incidentes', 'rutas', 'tareas', 'notificaciones', 'reportes')
ORDER BY schemaname, tablename;
```

### Ver triggers activos
```sql
SELECT 
    trigger_schema,
    trigger_name,
    event_object_table,
    action_timing,
    event_manipulation
FROM information_schema.triggers
WHERE trigger_schema IN ('incidentes', 'rutas', 'tareas', 'notificaciones', 'reportes')
ORDER BY trigger_schema, event_object_table;
```

### Ver índices espaciales (PostGIS)
```sql
SELECT 
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE indexdef LIKE '%GIST%'
AND schemaname IN ('incidentes', 'rutas', 'tareas');
```

---

## ⚠️ NOTAS IMPORTANTES

### 1. PostGIS
Asegúrate de que PostGIS esté habilitado en Supabase:
```sql
CREATE EXTENSION IF NOT EXISTS postgis;
```

### 2. UUID
La extensión uuid-ossp debe estar habilitada:
```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

### 3. Row Level Security (RLS)
Por seguridad, considera habilitar RLS en las tablas principales:
```sql
ALTER TABLE tareas.tasks ENABLE ROW LEVEL SECURITY;

-- Política de ejemplo: usuarios solo ven sus propias tareas
CREATE POLICY "users_own_tasks" ON tareas.tasks
    FOR SELECT
    USING (auth.uid() = assigned_to OR auth.uid() = created_by);
```

### 4. Conexión desde Django
Verifica que tu `settings.py` tenga la configuración correcta:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
        'OPTIONS': {
            'sslmode': 'require',  # Importante para Supabase
        }
    }
}
```

---

## 🧪 PROBAR LA INTEGRACIÓN

### 1. Desde Django Shell
```python
# docker-compose exec backend python manage.py shell

from apps.tasks.models import Task
from apps.routes.models import CleaningZone
from apps.notifications.models import Notification

# Verificar que los modelos funcionen
print("Tasks:", Task.objects.count())
print("Zones:", CleaningZone.objects.count())
print("Notifications:", Notification.objects.count())
```

### 2. Desde la API
```bash
# Obtener token de autenticación
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Listar tareas
curl -X GET http://localhost:8000/api/tasks/tasks/ \
  -H "Authorization: Bearer TU_TOKEN"

# Listar zonas de limpieza
curl -X GET http://localhost:8000/api/routes/cleaning-zones/ \
  -H "Authorization: Bearer TU_TOKEN"
```

---

## 📊 ESQUEMA VISUAL DE LAS RELACIONES

```
auth.users
    ├── incidentes.incidents (reported_by, assigned_to, resolved_by)
    ├── tareas.tasks (assigned_to, created_by)
    ├── notificaciones.notifications (user_id)
    └── reportes.reports (generated_by)

rutas.cleaning_zones
    └── rutas.routes (zone_id)
        ├── rutas.route_waypoints (route_id)
        └── tareas.tasks (route_id)

incidentes.incidents
    ├── incidentes.incident_attachments (incident_id)
    ├── incidentes.incident_events (incident_id)
    └── tareas.tasks (incident_id)

tareas.tasks
    ├── tareas.task_checkpoints (task_id)
    └── tareas.task_assignments_history (task_id)
```

---

## ✅ CHECKLIST DE VERIFICACIÓN

- [ ] PostGIS habilitado en Supabase
- [ ] UUID-OSSP habilitado en Supabase
- [ ] Script SQL ejecutado sin errores
- [ ] 21 tablas creadas correctamente
- [ ] 40+ índices creados
- [ ] 9 triggers activos
- [ ] Variables de entorno configuradas
- [ ] Django conectado a Supabase
- [ ] Migraciones aplicadas
- [ ] API endpoints funcionando

---

## 🆘 SOLUCIÓN DE PROBLEMAS

### Error: "extension postgis does not exist"
```sql
CREATE EXTENSION postgis;
```

### Error: "schema already exists"
```sql
-- Eliminar esquema y recrear (CUIDADO: elimina datos)
DROP SCHEMA IF EXISTS incidentes CASCADE;
-- Luego volver a ejecutar el script
```

### Error de conexión desde Django
- Verifica que uses `sslmode: 'require'` en la configuración
- Confirma que el host sea el correcto (db.tu-proyecto.supabase.co)
- Verifica usuario y contraseña en Supabase

---

## 📞 SOPORTE

Si encuentras problemas:
1. Revisa los logs de Supabase en el Dashboard
2. Verifica que todas las extensiones estén habilitadas
3. Confirma que las credenciales sean correctas
4. Revisa los permisos de la base de datos

**¡Sistema listo para producción!** 🚀
