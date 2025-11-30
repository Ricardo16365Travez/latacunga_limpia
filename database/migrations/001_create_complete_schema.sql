-- ============================================================
-- MIGRACIÓN COMPLETA PARA SISTEMA DE GESTIÓN DE RESIDUOS
-- Compatible con incident-service de latacunga_clean_app
-- ============================================================

-- Extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";
CREATE EXTENSION IF NOT EXISTS "pg_trgm"; -- Para búsquedas de texto

-- ============================================================
-- ESQUEMA: incidentes
-- ============================================================
CREATE SCHEMA IF NOT EXISTS incidentes;

-- Tabla: incidents (incidentes reportados)
CREATE TABLE IF NOT EXISTS incidentes.incidents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    reporter_kind TEXT NOT NULL CHECK (reporter_kind IN ('ciudadano', 'operador', 'sistema')),
    reporter_id UUID,
    type TEXT NOT NULL CHECK (type IN ('punto_acopio', 'zona_critica', 'animal_muerto', 'zona_reciclaje')),
    title TEXT NOT NULL,
    description TEXT,
    location GEOGRAPHY(Point, 4326) NOT NULL,
    address TEXT,
    status TEXT NOT NULL DEFAULT 'incidente_no_validado' 
        CHECK (status IN ('incidente_no_validado', 'incidente_pendiente', 'incidente_valido', 
                         'incidente_rechazado', 'convertido_en_tarea', 'cerrado')),
    incident_day DATE NOT NULL DEFAULT ((now() AT TIME ZONE 'UTC')::date),
    photos_count INTEGER DEFAULT 0,
    idempotency_key TEXT UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Tabla: incident_attachments (fotos/archivos adjuntos)
CREATE TABLE IF NOT EXISTS incidentes.incident_attachments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    incident_id UUID NOT NULL REFERENCES incidentes.incidents(id) ON DELETE CASCADE,
    file_url TEXT NOT NULL,
    mime_type TEXT,
    size_bytes BIGINT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Tabla: incident_events (historial de eventos)
CREATE TABLE IF NOT EXISTS incidentes.incident_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    incident_id UUID NOT NULL REFERENCES incidentes.incidents(id) ON DELETE CASCADE,
    event_type TEXT NOT NULL,
    payload JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Tabla: idempotency_keys (control de duplicados offline-first)
CREATE TABLE IF NOT EXISTS incidentes.idempotency_keys (
    key TEXT PRIMARY KEY,
    resource_id UUID,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Tabla: outbox_events (patrón transactional outbox para RabbitMQ)
CREATE TABLE IF NOT EXISTS incidentes.outbox_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    aggregate_type TEXT NOT NULL,
    aggregate_id UUID NOT NULL,
    type TEXT NOT NULL,
    payload JSONB NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'published', 'failed')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    published_at TIMESTAMPTZ
);

-- Índices para incidentes
CREATE INDEX IF NOT EXISTS idx_incidents_status ON incidentes.incidents(status);
CREATE INDEX IF NOT EXISTS idx_incidents_type ON incidentes.incidents(type);
CREATE INDEX IF NOT EXISTS idx_incidents_reporter_id ON incidentes.incidents(reporter_id);
CREATE INDEX IF NOT EXISTS idx_incidents_incident_day ON incidentes.incidents(incident_day DESC);
CREATE INDEX IF NOT EXISTS idx_incidents_location ON incidentes.incidents USING GIST(location);
CREATE INDEX IF NOT EXISTS idx_incidents_created_at ON incidentes.incidents(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_incident_attachments_incident_id ON incidentes.incident_attachments(incident_id);
CREATE INDEX IF NOT EXISTS idx_incident_events_incident_id ON incidentes.incident_events(incident_id);
CREATE INDEX IF NOT EXISTS idx_incident_events_created_at ON incidentes.incident_events(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_outbox_events_status ON incidentes.outbox_events(status, created_at);

-- ============================================================
-- ESQUEMA: validacion
-- ============================================================
CREATE SCHEMA IF NOT EXISTS validacion;

-- Tabla: incidentes_pendientes (para servicio de validación)
CREATE TABLE IF NOT EXISTS validacion.incidentes_pendientes (
    incidente_id UUID PRIMARY KEY,
    tipo VARCHAR(50) NOT NULL,
    descripcion TEXT NOT NULL,
    ciudadano_id UUID NOT NULL,
    estado VARCHAR(50) NOT NULL DEFAULT 'pendiente_validacion',
    fecha_evento TIMESTAMPTZ NOT NULL,
    dia_incidente DATE NOT NULL,
    num_fotos INTEGER DEFAULT 0,
    direccion TEXT,
    latitud DECIMAL(10, 8) NOT NULL,
    longitud DECIMAL(11, 8) NOT NULL,
    geometria GEOMETRY(Point, 4326),
    validado_por VARCHAR(100),
    fecha_validacion TIMESTAMPTZ,
    notas_validacion TEXT,
    recibido_en TIMESTAMPTZ DEFAULT NOW(),
    actualizado_en TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_incidentes_pendientes_estado ON validacion.incidentes_pendientes(estado);
CREATE INDEX IF NOT EXISTS idx_incidentes_pendientes_fecha ON validacion.incidentes_pendientes(fecha_evento DESC);
CREATE INDEX IF NOT EXISTS idx_incidentes_pendientes_tipo ON validacion.incidentes_pendientes(tipo);
CREATE INDEX IF NOT EXISTS idx_incidentes_pendientes_geometria ON validacion.incidentes_pendientes USING GIST(geometria);

-- ============================================================
-- ESQUEMA: rutas
-- ============================================================
CREATE SCHEMA IF NOT EXISTS rutas;

-- Tabla: cleaning_zones (zonas de limpieza)
CREATE TABLE IF NOT EXISTS rutas.cleaning_zones (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    zone_name TEXT NOT NULL UNIQUE,
    description TEXT,
    zone_polygon GEOGRAPHY(Polygon, 4326) NOT NULL,
    priority INTEGER DEFAULT 1 CHECK (priority BETWEEN 1 AND 5),
    frequency TEXT DEFAULT 'daily' CHECK (frequency IN ('daily', 'weekly', 'biweekly', 'monthly')),
    estimated_duration_minutes INTEGER,
    assigned_team_size INTEGER DEFAULT 2,
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'maintenance')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Tabla: routes (rutas optimizadas)
CREATE TABLE IF NOT EXISTS rutas.routes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    route_name TEXT NOT NULL,
    zone_id UUID REFERENCES rutas.cleaning_zones(id) ON DELETE CASCADE,
    route_geometry GEOGRAPHY(LineString, 4326) NOT NULL,
    waypoints JSONB NOT NULL, -- Array de puntos con lat/lon
    total_distance_km DECIMAL(10, 3),
    estimated_duration_minutes INTEGER,
    optimization_algorithm TEXT DEFAULT 'osrm',
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'archived')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Tabla: route_waypoints (puntos de parada en la ruta)
CREATE TABLE IF NOT EXISTS rutas.route_waypoints (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    route_id UUID NOT NULL REFERENCES rutas.routes(id) ON DELETE CASCADE,
    waypoint_order INTEGER NOT NULL,
    location GEOGRAPHY(Point, 4326) NOT NULL,
    address TEXT,
    waypoint_type TEXT CHECK (waypoint_type IN ('start', 'collection', 'disposal', 'end')),
    estimated_service_minutes INTEGER DEFAULT 5,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Índices para rutas
CREATE INDEX IF NOT EXISTS idx_cleaning_zones_status ON rutas.cleaning_zones(status);
CREATE INDEX IF NOT EXISTS idx_cleaning_zones_polygon ON rutas.cleaning_zones USING GIST(zone_polygon);
CREATE INDEX IF NOT EXISTS idx_routes_zone_id ON rutas.routes(zone_id);
CREATE INDEX IF NOT EXISTS idx_routes_status ON rutas.routes(status);
CREATE INDEX IF NOT EXISTS idx_routes_geometry ON rutas.routes USING GIST(route_geometry);
CREATE INDEX IF NOT EXISTS idx_route_waypoints_route_id ON rutas.route_waypoints(route_id, waypoint_order);
CREATE INDEX IF NOT EXISTS idx_route_waypoints_location ON rutas.route_waypoints USING GIST(location);

-- ============================================================
-- ESQUEMA: tareas
-- ============================================================
CREATE SCHEMA IF NOT EXISTS tareas;

-- Tabla: tasks (tareas asignadas a operadores)
CREATE TABLE IF NOT EXISTS tareas.tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_type TEXT NOT NULL CHECK (task_type IN ('route_cleaning', 'incident_response', 'maintenance', 'special')),
    title TEXT NOT NULL,
    description TEXT,
    route_id UUID REFERENCES rutas.routes(id) ON DELETE SET NULL,
    zone_id UUID REFERENCES rutas.cleaning_zones(id) ON DELETE SET NULL,
    incident_id UUID REFERENCES incidentes.incidents(id) ON DELETE SET NULL,
    assigned_to UUID, -- user_id del operador
    assigned_team JSONB, -- Array de user_ids si es equipo
    status TEXT NOT NULL DEFAULT 'pending' 
        CHECK (status IN ('pending', 'assigned', 'in_progress', 'paused', 'completed', 'cancelled')),
    priority INTEGER DEFAULT 3 CHECK (priority BETWEEN 1 AND 5),
    scheduled_start_time TIMESTAMPTZ,
    scheduled_end_time TIMESTAMPTZ,
    actual_start_time TIMESTAMPTZ,
    actual_end_time TIMESTAMPTZ,
    estimated_duration_minutes INTEGER,
    actual_duration_minutes INTEGER,
    completion_percentage INTEGER DEFAULT 0 CHECK (completion_percentage BETWEEN 0 AND 100),
    completion_notes TEXT,
    completion_photos JSONB, -- Array de URLs de fotos
    created_by UUID,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Tabla: task_checkpoints (puntos de verificación en tareas)
CREATE TABLE IF NOT EXISTS tareas.task_checkpoints (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id UUID NOT NULL REFERENCES tareas.tasks(id) ON DELETE CASCADE,
    checkpoint_order INTEGER NOT NULL,
    location GEOGRAPHY(Point, 4326) NOT NULL,
    checkpoint_type TEXT CHECK (checkpoint_type IN ('start', 'waypoint', 'collection', 'disposal', 'end')),
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'completed', 'skipped')),
    completed_at TIMESTAMPTZ,
    notes TEXT,
    photo_url TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Tabla: task_assignments_history (historial de asignaciones)
CREATE TABLE IF NOT EXISTS tareas.task_assignments_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id UUID NOT NULL REFERENCES tareas.tasks(id) ON DELETE CASCADE,
    assigned_from UUID,
    assigned_to UUID NOT NULL,
    assignment_reason TEXT,
    assigned_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    assigned_by UUID
);

-- Índices para tareas
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tareas.tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_assigned_to ON tareas.tasks(assigned_to);
CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tareas.tasks(priority DESC);
CREATE INDEX IF NOT EXISTS idx_tasks_scheduled_start ON tareas.tasks(scheduled_start_time);
CREATE INDEX IF NOT EXISTS idx_tasks_zone_id ON tareas.tasks(zone_id);
CREATE INDEX IF NOT EXISTS idx_tasks_route_id ON tareas.tasks(route_id);
CREATE INDEX IF NOT EXISTS idx_tasks_incident_id ON tareas.tasks(incident_id);
CREATE INDEX IF NOT EXISTS idx_task_checkpoints_task_id ON tareas.task_checkpoints(task_id, checkpoint_order);
CREATE INDEX IF NOT EXISTS idx_task_checkpoints_location ON tareas.task_checkpoints USING GIST(location);
CREATE INDEX IF NOT EXISTS idx_task_assignments_task_id ON tareas.task_assignments_history(task_id);
CREATE INDEX IF NOT EXISTS idx_task_assignments_assigned_to ON tareas.task_assignments_history(assigned_to);

-- ============================================================
-- ESQUEMA: notificaciones
-- ============================================================
CREATE SCHEMA IF NOT EXISTS notificaciones;

-- Tabla: notifications (notificaciones push)
CREATE TABLE IF NOT EXISTS notificaciones.notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    notification_type TEXT NOT NULL 
        CHECK (notification_type IN ('task_assigned', 'incident_created', 'incident_validated', 
                                     'route_updated', 'alert', 'message', 'system')),
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    data JSONB, -- Datos adicionales específicos del tipo
    priority TEXT DEFAULT 'normal' CHECK (priority IN ('low', 'normal', 'high', 'urgent')),
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMPTZ,
    sent_via JSONB, -- Canales por los que se envió: {"push": true, "email": false, "sms": false}
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Tabla: device_tokens (tokens de dispositivos móviles para push notifications)
CREATE TABLE IF NOT EXISTS notificaciones.device_tokens (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    device_token TEXT NOT NULL UNIQUE,
    device_type TEXT NOT NULL CHECK (device_type IN ('ios', 'android', 'web')),
    device_name TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    last_used_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Índices para notificaciones
CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notificaciones.notifications(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_notifications_is_read ON notificaciones.notifications(is_read, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_notifications_type ON notificaciones.notifications(notification_type);
CREATE INDEX IF NOT EXISTS idx_device_tokens_user_id ON notificaciones.device_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_device_tokens_active ON notificaciones.device_tokens(is_active);

-- ============================================================
-- ESQUEMA: reportes
-- ============================================================
CREATE SCHEMA IF NOT EXISTS reportes;

-- Tabla: reports (reportes generados)
CREATE TABLE IF NOT EXISTS reportes.reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    report_type TEXT NOT NULL 
        CHECK (report_type IN ('daily_summary', 'weekly_summary', 'monthly_summary', 
                              'incident_analysis', 'route_performance', 'operator_performance', 'custom')),
    report_name TEXT NOT NULL,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    generated_by UUID,
    parameters JSONB, -- Filtros y parámetros usados
    data JSONB NOT NULL, -- Datos del reporte
    file_url TEXT, -- URL del PDF/Excel generado
    file_format TEXT CHECK (file_format IN ('pdf', 'excel', 'csv', 'json')),
    status TEXT DEFAULT 'generating' CHECK (status IN ('generating', 'completed', 'failed')),
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Tabla: statistics (estadísticas agregadas diarias)
CREATE TABLE IF NOT EXISTS reportes.statistics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    stat_date DATE NOT NULL,
    stat_type TEXT NOT NULL,
    zone_id UUID REFERENCES rutas.cleaning_zones(id) ON DELETE CASCADE,
    metrics JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(stat_date, stat_type, zone_id)
);

-- Índices para reportes
CREATE INDEX IF NOT EXISTS idx_reports_type ON reportes.reports(report_type);
CREATE INDEX IF NOT EXISTS idx_reports_period ON reportes.reports(period_start, period_end);
CREATE INDEX IF NOT EXISTS idx_reports_generated_by ON reportes.reports(generated_by);
CREATE INDEX IF NOT EXISTS idx_statistics_date ON reportes.statistics(stat_date DESC);
CREATE INDEX IF NOT EXISTS idx_statistics_type ON reportes.statistics(stat_type);
CREATE INDEX IF NOT EXISTS idx_statistics_zone ON reportes.statistics(zone_id);

-- ============================================================
-- FUNCIONES Y TRIGGERS
-- ============================================================

-- Función para actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers para updated_at
CREATE TRIGGER update_incidents_updated_at BEFORE UPDATE ON incidentes.incidents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_cleaning_zones_updated_at BEFORE UPDATE ON rutas.cleaning_zones
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_routes_updated_at BEFORE UPDATE ON rutas.routes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tasks_updated_at BEFORE UPDATE ON tareas.tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_incidentes_pendientes_actualizado_en BEFORE UPDATE ON validacion.incidentes_pendientes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Función para calcular duración real de tarea
CREATE OR REPLACE FUNCTION calculate_task_duration()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.actual_end_time IS NOT NULL AND NEW.actual_start_time IS NOT NULL THEN
        NEW.actual_duration_minutes = EXTRACT(EPOCH FROM (NEW.actual_end_time - NEW.actual_start_time)) / 60;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER calculate_task_duration_trigger BEFORE UPDATE ON tareas.tasks
    FOR EACH ROW EXECUTE FUNCTION calculate_task_duration();

-- ============================================================
-- VISTAS ÚTILES
-- ============================================================

-- Vista: incidentes pendientes con información geográfica
CREATE OR REPLACE VIEW incidentes.v_incidents_pending AS
SELECT 
    i.id,
    i.type,
    i.title,
    i.description,
    i.status,
    i.incident_day,
    i.photos_count,
    ST_Y(i.location::geometry) AS latitude,
    ST_X(i.location::geometry) AS longitude,
    i.address,
    i.created_at,
    COUNT(ia.id) AS attachments_count
FROM incidentes.incidents i
LEFT JOIN incidentes.incident_attachments ia ON i.id = ia.incident_id
WHERE i.status IN ('incidente_pendiente', 'incidente_valido')
GROUP BY i.id;

-- Vista: tareas activas con información completa
CREATE OR REPLACE VIEW tareas.v_active_tasks AS
SELECT 
    t.id,
    t.task_type,
    t.title,
    t.status,
    t.priority,
    t.assigned_to,
    t.scheduled_start_time,
    t.scheduled_end_time,
    t.completion_percentage,
    z.zone_name,
    r.route_name,
    i.title AS incident_title
FROM tareas.tasks t
LEFT JOIN rutas.cleaning_zones z ON t.zone_id = z.id
LEFT JOIN rutas.routes r ON t.route_id = r.id
LEFT JOIN incidentes.incidents i ON t.incident_id = i.id
WHERE t.status IN ('pending', 'assigned', 'in_progress');

-- Vista: estadísticas diarias de incidentes
CREATE OR REPLACE VIEW reportes.v_daily_incident_stats AS
SELECT 
    incident_day,
    type,
    status,
    COUNT(*) AS total_count,
    AVG(photos_count) AS avg_photos
FROM incidentes.incidents
GROUP BY incident_day, type, status
ORDER BY incident_day DESC;

-- ============================================================
-- COMENTARIOS EN TABLAS
-- ============================================================

COMMENT ON SCHEMA incidentes IS 'Gestión de incidentes reportados por ciudadanos y operadores';
COMMENT ON SCHEMA validacion IS 'Servicio de validación manual de incidentes por administradores';
COMMENT ON SCHEMA rutas IS 'Gestión de zonas de limpieza y rutas optimizadas';
COMMENT ON SCHEMA tareas IS 'Gestión de tareas asignadas a operadores';
COMMENT ON SCHEMA notificaciones IS 'Sistema de notificaciones push y alertas';
COMMENT ON SCHEMA reportes IS 'Generación de reportes y estadísticas';

COMMENT ON TABLE incidentes.incidents IS 'Incidentes reportados con soporte offline-first y geolocalización';
COMMENT ON TABLE incidentes.outbox_events IS 'Patrón transactional outbox para publicación confiable de eventos a RabbitMQ';
COMMENT ON TABLE rutas.cleaning_zones IS 'Zonas de limpieza definidas con polígonos geográficos';
COMMENT ON TABLE rutas.routes IS 'Rutas optimizadas calculadas con OSRM';
COMMENT ON TABLE tareas.tasks IS 'Tareas de limpieza asignadas a operadores';
COMMENT ON TABLE notificaciones.notifications IS 'Notificaciones push para usuarios móviles';
COMMENT ON TABLE reportes.reports IS 'Reportes generados en PDF/Excel';

-- ============================================================
-- DATOS DE EJEMPLO (OPCIONAL - COMENTAR EN PRODUCCIÓN)
-- ============================================================

-- Zona de ejemplo
-- INSERT INTO rutas.cleaning_zones (zone_name, description, zone_polygon, priority, frequency)
-- VALUES (
--     'Centro Histórico',
--     'Zona central de la ciudad con alta concentración comercial',
--     ST_GeogFromText('POLYGON((-78.6200 -0.9350, -78.6150 -0.9350, -78.6150 -0.9400, -78.6200 -0.9400, -78.6200 -0.9350))'),
--     5,
--     'daily'
-- );

-- ============================================================
-- FIN DE MIGRACIÓN
-- ============================================================
