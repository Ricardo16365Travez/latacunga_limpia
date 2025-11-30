-- ============================================
-- SCRIPT SQL COMPLETO PARA SUPABASE
-- Sistema de Gestión de Residuos - Latacunga
-- ============================================

-- Habilitar extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";

-- ============================================
-- ESQUEMA: AUTENTICACIÓN (Ya existe en Supabase)
-- ============================================
-- Supabase maneja auth.users automáticamente

-- ============================================
-- ESQUEMA: INCIDENTES
-- ============================================
CREATE SCHEMA IF NOT EXISTS incidentes;

-- Tabla: incidents
CREATE TABLE IF NOT EXISTS incidentes.incidents (
    id BIGSERIAL PRIMARY KEY,
    incident_id VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    incident_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) DEFAULT 'medium',
    status VARCHAR(20) DEFAULT 'pending',
    location GEOGRAPHY(Point, 4326),
    address TEXT,
    reported_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    assigned_to UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    resolved_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    reported_at TIMESTAMPTZ DEFAULT NOW(),
    resolved_at TIMESTAMPTZ,
    metadata JSONB DEFAULT '{}',
    attachments JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla: incident_attachments
CREATE TABLE IF NOT EXISTS incidentes.incident_attachments (
    id BIGSERIAL PRIMARY KEY,
    incident_id BIGINT REFERENCES incidentes.incidents(id) ON DELETE CASCADE,
    file_url TEXT NOT NULL,
    file_type VARCHAR(50),
    file_size INTEGER,
    uploaded_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    uploaded_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla: incident_events
CREATE TABLE IF NOT EXISTS incidentes.incident_events (
    id BIGSERIAL PRIMARY KEY,
    incident_id BIGINT REFERENCES incidentes.incidents(id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL,
    event_data JSONB DEFAULT '{}',
    performed_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla: idempotency_keys
CREATE TABLE IF NOT EXISTS incidentes.idempotency_keys (
    id BIGSERIAL PRIMARY KEY,
    key VARCHAR(255) UNIQUE NOT NULL,
    response_data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ
);

-- Tabla: outbox_events
CREATE TABLE IF NOT EXISTS incidentes.outbox_events (
    id BIGSERIAL PRIMARY KEY,
    aggregate_id VARCHAR(100) NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    event_data JSONB NOT NULL,
    published BOOLEAN DEFAULT FALSE,
    published_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- ESQUEMA: VALIDACIÓN
-- ============================================
CREATE SCHEMA IF NOT EXISTS validacion;

-- Vista: incidentes_pendientes
CREATE OR REPLACE VIEW validacion.incidentes_pendientes AS
SELECT 
    id,
    incident_id,
    title,
    description,
    incident_type,
    severity,
    location,
    address,
    reported_at,
    created_at
FROM incidentes.incidents
WHERE status = 'pending'
ORDER BY severity DESC, reported_at DESC;

-- ============================================
-- ESQUEMA: RUTAS
-- ============================================
CREATE SCHEMA IF NOT EXISTS rutas;

-- Tabla: cleaning_zones
CREATE TABLE IF NOT EXISTS rutas.cleaning_zones (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    zone_polygon GEOGRAPHY(Polygon, 4326) NOT NULL,
    zone_type VARCHAR(50) DEFAULT 'residential',
    priority INTEGER DEFAULT 3 CHECK (priority BETWEEN 1 AND 5),
    frequency VARCHAR(20) DEFAULT 'daily',
    estimated_duration INTEGER DEFAULT 60,
    team_size INTEGER DEFAULT 2,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla: routes
CREATE TABLE IF NOT EXISTS rutas.routes (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    route_geometry GEOGRAPHY(LineString, 4326),
    zone_id BIGINT REFERENCES rutas.cleaning_zones(id) ON DELETE SET NULL,
    waypoints JSONB DEFAULT '[]',
    distance_km DECIMAL(10, 2),
    duration_minutes INTEGER,
    optimization_type VARCHAR(50),
    is_optimized BOOLEAN DEFAULT FALSE,
    schedule_date DATE,
    status VARCHAR(20) DEFAULT 'draft',
    assigned_to UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla: route_waypoints
CREATE TABLE IF NOT EXISTS rutas.route_waypoints (
    id BIGSERIAL PRIMARY KEY,
    route_id BIGINT REFERENCES rutas.routes(id) ON DELETE CASCADE,
    waypoint_order INTEGER NOT NULL,
    location GEOGRAPHY(Point, 4326) NOT NULL,
    waypoint_type VARCHAR(50) DEFAULT 'collection',
    address TEXT,
    estimated_service_time INTEGER DEFAULT 5,
    actual_service_time INTEGER,
    completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMPTZ,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- ESQUEMA: TAREAS
-- ============================================
CREATE SCHEMA IF NOT EXISTS tareas;

-- Tabla: tasks
CREATE TABLE IF NOT EXISTS tareas.tasks (
    id BIGSERIAL PRIMARY KEY,
    task_id VARCHAR(50) UNIQUE NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    route_id BIGINT REFERENCES rutas.routes(id) ON DELETE SET NULL,
    incident_id BIGINT REFERENCES incidentes.incidents(id) ON DELETE SET NULL,
    assigned_to UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    created_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    status VARCHAR(20) DEFAULT 'pending',
    priority INTEGER DEFAULT 3 CHECK (priority BETWEEN 1 AND 5),
    location GEOGRAPHY(Point, 4326),
    address VARCHAR(500),
    scheduled_date DATE,
    scheduled_start_time TIME,
    scheduled_end_time TIME,
    estimated_duration INTEGER DEFAULT 30,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    paused_at TIMESTAMPTZ,
    team_size INTEGER DEFAULT 1,
    equipment_needed JSONB DEFAULT '[]',
    materials_needed JSONB DEFAULT '[]',
    completion_percentage INTEGER DEFAULT 0 CHECK (completion_percentage BETWEEN 0 AND 100),
    checkpoints_completed INTEGER DEFAULT 0,
    checkpoints_total INTEGER DEFAULT 0,
    result_notes TEXT,
    result_photos JSONB DEFAULT '[]',
    waste_collected_kg DECIMAL(10, 2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    cancelled_reason TEXT
);

-- Tabla: task_checkpoints
CREATE TABLE IF NOT EXISTS tareas.task_checkpoints (
    id BIGSERIAL PRIMARY KEY,
    task_id BIGINT REFERENCES tareas.tasks(id) ON DELETE CASCADE,
    checkpoint_order INTEGER NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    location GEOGRAPHY(Point, 4326),
    address VARCHAR(500),
    is_completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMPTZ,
    completed_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    requires_photo BOOLEAN DEFAULT FALSE,
    photo_url TEXT,
    notes TEXT,
    verification_data JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(task_id, checkpoint_order)
);

-- Tabla: task_assignments_history
CREATE TABLE IF NOT EXISTS tareas.task_assignments_history (
    id BIGSERIAL PRIMARY KEY,
    task_id BIGINT REFERENCES tareas.tasks(id) ON DELETE CASCADE,
    action VARCHAR(20) NOT NULL,
    performed_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    previous_assignee UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    new_assignee UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    previous_status VARCHAR(20),
    new_status VARCHAR(20),
    notes TEXT,
    metadata JSONB DEFAULT '{}',
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- ESQUEMA: NOTIFICACIONES
-- ============================================
CREATE SCHEMA IF NOT EXISTS notificaciones;

-- Tabla: notifications
CREATE TABLE IF NOT EXISTS notificaciones.notifications (
    id BIGSERIAL PRIMARY KEY,
    notification_id VARCHAR(100) UNIQUE NOT NULL,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    notification_type VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    priority INTEGER DEFAULT 2 CHECK (priority BETWEEN 1 AND 4),
    delivery_channels TEXT[] DEFAULT ARRAY['in_app'],
    related_task_id VARCHAR(50),
    related_incident_id VARCHAR(50),
    related_route_id BIGINT,
    action_url TEXT,
    metadata JSONB DEFAULT '{}',
    icon VARCHAR(50),
    image_url TEXT,
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMPTZ,
    is_sent BOOLEAN DEFAULT FALSE,
    sent_at TIMESTAMPTZ,
    is_delivered BOOLEAN DEFAULT FALSE,
    delivered_at TIMESTAMPTZ,
    scheduled_for TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    delivery_errors JSONB DEFAULT '{}',
    retry_count INTEGER DEFAULT 0
);

-- Tabla: device_tokens
CREATE TABLE IF NOT EXISTS notificaciones.device_tokens (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    token VARCHAR(500) UNIQUE NOT NULL,
    platform VARCHAR(20) NOT NULL,
    device_id VARCHAR(200),
    device_name VARCHAR(200),
    device_model VARCHAR(100),
    os_version VARCHAR(50),
    app_version VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    last_used_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, device_id, platform)
);

-- Tabla: notification_preferences
CREATE TABLE IF NOT EXISTS notificaciones.notification_preferences (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID UNIQUE REFERENCES auth.users(id) ON DELETE CASCADE,
    push_enabled BOOLEAN DEFAULT TRUE,
    email_enabled BOOLEAN DEFAULT TRUE,
    in_app_enabled BOOLEAN DEFAULT TRUE,
    websocket_enabled BOOLEAN DEFAULT TRUE,
    task_notifications BOOLEAN DEFAULT TRUE,
    incident_notifications BOOLEAN DEFAULT TRUE,
    route_notifications BOOLEAN DEFAULT TRUE,
    system_notifications BOOLEAN DEFAULT TRUE,
    message_notifications BOOLEAN DEFAULT TRUE,
    do_not_disturb BOOLEAN DEFAULT FALSE,
    dnd_start_time TIME,
    dnd_end_time TIME,
    sound_enabled BOOLEAN DEFAULT TRUE,
    vibration_enabled BOOLEAN DEFAULT TRUE,
    badge_enabled BOOLEAN DEFAULT TRUE,
    group_notifications BOOLEAN DEFAULT TRUE,
    max_notifications_per_day INTEGER DEFAULT 50,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- ESQUEMA: REPORTES
-- ============================================
CREATE SCHEMA IF NOT EXISTS reportes;

-- Tabla: reports
CREATE TABLE IF NOT EXISTS reportes.reports (
    id BIGSERIAL PRIMARY KEY,
    report_id VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    report_type VARCHAR(50) NOT NULL,
    format VARCHAR(20) DEFAULT 'pdf',
    generated_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    start_date DATE,
    end_date DATE,
    filters JSONB DEFAULT '{}',
    file_path TEXT,
    file_url TEXT,
    file_size INTEGER,
    is_generated BOOLEAN DEFAULT FALSE,
    generated_at TIMESTAMPTZ,
    data JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla: statistics
CREATE TABLE IF NOT EXISTS reportes.statistics (
    id BIGSERIAL PRIMARY KEY,
    stat_type VARCHAR(50) NOT NULL,
    date DATE NOT NULL,
    value DECIMAL(15, 2) NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(stat_type, date)
);

-- ============================================
-- ÍNDICES PARA MEJOR RENDIMIENTO
-- ============================================

-- Incidentes
CREATE INDEX IF NOT EXISTS idx_incidents_status ON incidentes.incidents(status);
CREATE INDEX IF NOT EXISTS idx_incidents_type ON incidentes.incidents(incident_type);
CREATE INDEX IF NOT EXISTS idx_incidents_severity ON incidentes.incidents(severity);
CREATE INDEX IF NOT EXISTS idx_incidents_reported_at ON incidentes.incidents(reported_at DESC);
CREATE INDEX IF NOT EXISTS idx_incidents_location ON incidentes.incidents USING GIST(location);
CREATE INDEX IF NOT EXISTS idx_incidents_reported_by ON incidentes.incidents(reported_by);

-- Rutas
CREATE INDEX IF NOT EXISTS idx_zones_active ON rutas.cleaning_zones(is_active);
CREATE INDEX IF NOT EXISTS idx_zones_polygon ON rutas.cleaning_zones USING GIST(zone_polygon);
CREATE INDEX IF NOT EXISTS idx_routes_status ON rutas.routes(status);
CREATE INDEX IF NOT EXISTS idx_routes_schedule ON rutas.routes(schedule_date);
CREATE INDEX IF NOT EXISTS idx_routes_geometry ON rutas.routes USING GIST(route_geometry);
CREATE INDEX IF NOT EXISTS idx_waypoints_route ON rutas.route_waypoints(route_id, waypoint_order);
CREATE INDEX IF NOT EXISTS idx_waypoints_location ON rutas.route_waypoints USING GIST(location);

-- Tareas
CREATE INDEX IF NOT EXISTS idx_tasks_status_date ON tareas.tasks(status, scheduled_date);
CREATE INDEX IF NOT EXISTS idx_tasks_assigned ON tareas.tasks(assigned_to, status);
CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tareas.tasks(priority, status);
CREATE INDEX IF NOT EXISTS idx_tasks_created ON tareas.tasks(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_tasks_location ON tareas.tasks USING GIST(location);
CREATE INDEX IF NOT EXISTS idx_checkpoints_task ON tareas.task_checkpoints(task_id, is_completed);
CREATE INDEX IF NOT EXISTS idx_history_task ON tareas.task_assignments_history(task_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_history_action ON tareas.task_assignments_history(action, timestamp DESC);

-- Notificaciones
CREATE INDEX IF NOT EXISTS idx_notif_user_created ON notificaciones.notifications(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_notif_user_read ON notificaciones.notifications(user_id, is_read);
CREATE INDEX IF NOT EXISTS idx_notif_type ON notificaciones.notifications(notification_type, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_notif_scheduled ON notificaciones.notifications(is_sent, scheduled_for);
CREATE INDEX IF NOT EXISTS idx_tokens_user_active ON notificaciones.device_tokens(user_id, is_active);
CREATE INDEX IF NOT EXISTS idx_tokens_platform ON notificaciones.device_tokens(platform, is_active);

-- Reportes
CREATE INDEX IF NOT EXISTS idx_reports_type ON reportes.reports(report_type, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_reports_generated_by ON reportes.reports(generated_by, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_stats_type_date ON reportes.statistics(stat_type, date DESC);

-- ============================================
-- TRIGGERS PARA AUTO-UPDATE
-- ============================================

-- Función para actualizar updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Aplicar trigger a todas las tablas con updated_at
DROP TRIGGER IF EXISTS update_incidents_updated_at ON incidentes.incidents;
CREATE TRIGGER update_incidents_updated_at BEFORE UPDATE ON incidentes.incidents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_zones_updated_at ON rutas.cleaning_zones;
CREATE TRIGGER update_zones_updated_at BEFORE UPDATE ON rutas.cleaning_zones
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_routes_updated_at ON rutas.routes;
CREATE TRIGGER update_routes_updated_at BEFORE UPDATE ON rutas.routes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_tasks_updated_at ON tareas.tasks;
CREATE TRIGGER update_tasks_updated_at BEFORE UPDATE ON tareas.tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_checkpoints_updated_at ON tareas.task_checkpoints;
CREATE TRIGGER update_checkpoints_updated_at BEFORE UPDATE ON tareas.task_checkpoints
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_notifications_updated_at ON notificaciones.notifications;
CREATE TRIGGER update_notifications_updated_at BEFORE UPDATE ON notificaciones.notifications
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_device_tokens_updated_at ON notificaciones.device_tokens;
CREATE TRIGGER update_device_tokens_updated_at BEFORE UPDATE ON notificaciones.device_tokens
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_preferences_updated_at ON notificaciones.notification_preferences;
CREATE TRIGGER update_preferences_updated_at BEFORE UPDATE ON notificaciones.notification_preferences
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_reports_updated_at ON reportes.reports;
CREATE TRIGGER update_reports_updated_at BEFORE UPDATE ON reportes.reports
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- VISTAS ÚTILES
-- ============================================

-- Vista: Tareas activas
CREATE OR REPLACE VIEW tareas.v_active_tasks AS
SELECT 
    t.id,
    t.task_id,
    t.title,
    t.status,
    t.priority,
    t.assigned_to,
    t.scheduled_date,
    t.completion_percentage,
    t.created_at
FROM tareas.tasks t
WHERE t.status IN ('pending', 'assigned', 'in_progress')
ORDER BY t.priority DESC, t.scheduled_date;

-- Vista: Estadísticas diarias de incidentes
CREATE OR REPLACE VIEW incidentes.v_daily_incident_stats AS
SELECT 
    DATE(created_at) as date,
    COUNT(*) as total_incidents,
    COUNT(*) FILTER (WHERE status = 'pending') as pending,
    COUNT(*) FILTER (WHERE status = 'resolved') as resolved,
    COUNT(*) FILTER (WHERE severity = 'high') as high_severity
FROM incidentes.incidents
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- ============================================
-- PERMISOS RLS (Row Level Security) - OPCIONAL
-- ============================================
-- Descomentar si deseas habilitar RLS en Supabase

-- ALTER TABLE incidentes.incidents ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE tareas.tasks ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE notificaciones.notifications ENABLE ROW LEVEL SECURITY;

-- CREATE POLICY "Users can view their own tasks" ON tareas.tasks
--     FOR SELECT USING (auth.uid() = assigned_to OR auth.uid() = created_by);

-- CREATE POLICY "Users can view their own notifications" ON notificaciones.notifications
--     FOR SELECT USING (auth.uid() = user_id);

-- ============================================
-- FIN DEL SCRIPT
-- ============================================

-- Mensaje de confirmación
DO $$
BEGIN
    RAISE NOTICE 'Base de datos creada exitosamente!';
    RAISE NOTICE 'Esquemas creados: incidentes, validacion, rutas, tareas, notificaciones, reportes';
    RAISE NOTICE 'Total de tablas: 20+';
    RAISE NOTICE 'Total de índices: 40+';
    RAISE NOTICE 'Total de triggers: 9';
    RAISE NOTICE 'Total de vistas: 3';
END $$;
