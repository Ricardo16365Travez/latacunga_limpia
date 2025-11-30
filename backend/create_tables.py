import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection

sql = """
-- Crear tabla incidents si no existe
CREATE TABLE IF NOT EXISTS public.incidents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reporter_kind VARCHAR(20) DEFAULT 'ciudadano',
    reporter_id UUID,
    incident_type VARCHAR(50),
    status VARCHAR(50) DEFAULT 'incidente_no_validado',
    priority VARCHAR(20) DEFAULT 'MEDIA',
    description TEXT,
    address VARCHAR(500),
    location GEOMETRY(Point, 4326),
    photo_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Crear tabla cleaning_zones si no existe
CREATE TABLE IF NOT EXISTS public.cleaning_zones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    zone_name VARCHAR(200) UNIQUE NOT NULL,
    description TEXT,
    zone_polygon GEOMETRY(Polygon, 4326),
    priority INTEGER DEFAULT 1 CHECK (priority BETWEEN 1 AND 5),
    frequency VARCHAR(10) DEFAULT 'daily',
    estimated_duration_minutes INTEGER,
    assigned_team_size INTEGER DEFAULT 2,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índices para incidents
CREATE INDEX IF NOT EXISTS idx_incidents_location ON public.incidents USING GIST(location);
CREATE INDEX IF NOT EXISTS idx_incidents_status ON public.incidents(status);
CREATE INDEX IF NOT EXISTS idx_incidents_type ON public.incidents(incident_type);
CREATE INDEX IF NOT EXISTS idx_incidents_created ON public.incidents(created_at DESC);

-- Índices para cleaning_zones  
CREATE INDEX IF NOT EXISTS idx_zones_polygon ON public.cleaning_zones USING GIST(zone_polygon);
CREATE INDEX IF NOT EXISTS idx_zones_priority ON public.cleaning_zones(priority DESC);
CREATE INDEX IF NOT EXISTS idx_zones_status ON public.cleaning_zones(status);

-- Función de actualización de timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers para updated_at
DROP TRIGGER IF EXISTS trigger_incidents_updated_at ON public.incidents;
CREATE TRIGGER trigger_incidents_updated_at
    BEFORE UPDATE ON public.incidents
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS trigger_zones_updated_at ON public.cleaning_zones;
CREATE TRIGGER trigger_zones_updated_at
    BEFORE UPDATE ON public.cleaning_zones
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
"""

# Ejecutar
with connection.cursor() as cursor:
    cursor.execute(sql)

print("✅ Tablas creadas correctamente en Supabase")
