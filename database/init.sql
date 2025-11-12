-- PostgreSQL schema for "Gestión de Residuos Latacunga" (MVP)
-- Requirements addressed: auth (JWT/refresh/OTP), reports (geolocation + attachments + history),
-- tasks/assignment, offline sync (outbox + sync ops), notifications, audit/processed events.
-- Assumes extensions: "uuid-ossp" or "pgcrypto" for UUID generation and "postgis" for geospatial.
-- Run as a privileged DB user.

-- Extensions
CREATE EXTENSION IF NOT EXISTS "pgcrypto";   -- gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS postgis;       -- geometry, geospatial indices

-- -----------------------------
-- Types / Enums
-- -----------------------------
-- Roles for RBAC
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'user_role') THEN
    CREATE TYPE user_role AS ENUM ('user','admin','operador','trabajador','super_admin');
  END IF;
END$$;

-- Report types and states
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'report_type') THEN
    CREATE TYPE report_type AS ENUM ('ZONA_CRITICA','PUNTO_ACOPIO_LLENO');
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'report_state') THEN
    CREATE TYPE report_state AS ENUM ('ENVIADO','PENDIENTE','VERIFICADO','EMITIDO','RECHAZADO','COMPLETADO');
  END IF;
END$$;

-- Task types and states
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'task_type') THEN
    CREATE TYPE task_type AS ENUM ('RECOLECCION','LIMPIEZA');
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'task_state') THEN
    CREATE TYPE task_state AS ENUM ('PENDIENTE_ASIGNAR','ASIGNADA','EN_CURSO','COMPLETADA','FALLIDA','CANCELADA');
  END IF;
END$$;

-- Sync/op/enums
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'sync_status') THEN
    CREATE TYPE sync_status AS ENUM ('LOCAL_PENDING','SENDING','SENT','FAILED_RETRY','FAILED_PERMANENT');
  END IF;
END$$;

-- -----------------------------
-- USERS / AUTH
-- -----------------------------
CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT UNIQUE,
  phone TEXT UNIQUE,
  password_hash TEXT,                     -- nullable if registered only by OTP
  role user_role NOT NULL DEFAULT 'user',
  display_name TEXT,
  avatar_url TEXT,
  status TEXT NOT NULL DEFAULT 'ACTIVE',  -- ACTIVE, DISABLED, LOCKED (freeform)
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Indexes for quick lookup
CREATE INDEX IF NOT EXISTS idx_users_email ON users (lower(email));
CREATE INDEX IF NOT EXISTS idx_users_phone ON users (phone);

-- Refresh tokens (one row per issued refresh token)
CREATE TABLE IF NOT EXISTS refresh_tokens (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  token TEXT NOT NULL,
  issued_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  expires_at TIMESTAMPTZ NOT NULL,
  revoked BOOLEAN NOT NULL DEFAULT FALSE,
  metadata JSONB,    -- device info, ip, userAgent
  CONSTRAINT uniq_user_token UNIQUE (user_id, token)
);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user ON refresh_tokens (user_id);

-- OTP codes (one-time codes for phone login/registration). Store hashed code for security.
CREATE TABLE IF NOT EXISTS otp_codes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  phone TEXT NOT NULL,
  code_hash TEXT NOT NULL,                  -- HMAC/HASH of code
  attempts INT NOT NULL DEFAULT 0,
  max_attempts INT NOT NULL DEFAULT 5,
  issued_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  expires_at TIMESTAMPTZ NOT NULL,
  consumed BOOLEAN NOT NULL DEFAULT FALSE,
  purpose TEXT,                             -- e.g., 'LOGIN', 'REGISTER'
  created_by_ip TEXT,
  created_by_device TEXT
);
CREATE INDEX IF NOT EXISTS idx_otp_phone ON otp_codes (phone);

-- -----------------------------
-- REPORTS
-- -----------------------------
CREATE TABLE IF NOT EXISTS reports (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  client_report_id TEXT,                     -- temp id from client (for sync mapping)
  reporter_id UUID REFERENCES users(id) ON DELETE SET NULL,
  type report_type NOT NULL,
  description TEXT NOT NULL,
  priority_score REAL DEFAULT 0.0,
  -- geolocation: use PostGIS geometry(Point, 4326)
  location GEOGRAPHY(POINT, 4326) NOT NULL,
  location_accuracy INT,                     -- optional meters precision
  address TEXT,                              -- reverse geocoded or user input
  state report_state NOT NULL DEFAULT 'ENVIADO',
  channel TEXT DEFAULT 'MOBILE',             -- origination: MOBILE | WEB | SYNC
  sync_status sync_status NOT NULL DEFAULT 'SENT',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  emitted_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  version INT NOT NULL DEFAULT 1             -- optimistic locking
);

-- Indexes for searching / geo
CREATE INDEX IF NOT EXISTS idx_reports_state ON reports (state);
CREATE INDEX IF NOT EXISTS idx_reports_reporter ON reports (reporter_id);
CREATE INDEX IF NOT EXISTS idx_reports_created_at ON reports (created_at);
CREATE INDEX IF NOT EXISTS idx_reports_type ON reports (type);
CREATE INDEX IF NOT EXISTS idx_reports_location ON reports USING GIST (location);

-- -----------------------------
-- REPORT ATTACHMENTS / MEDIA
-- -----------------------------
CREATE TABLE IF NOT EXISTS report_attachments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  report_id UUID REFERENCES reports(id) ON DELETE CASCADE,
  attachment_id UUID,                 -- id from media-service / object storage metadata
  filename TEXT,
  mime_type TEXT,
  size_bytes INT,
  remote_url TEXT,                    -- URL in S3/MinIO
  hash TEXT,                          -- optional checksum
  type TEXT DEFAULT 'EVIDENCE',       -- BEFORE | AFTER | EVIDENCE
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_report_attachments_report ON report_attachments (report_id);

-- -----------------------------
-- REPORT HISTORY (audit of state transitions)
-- -----------------------------
CREATE TABLE IF NOT EXISTS report_history (
  id BIGSERIAL PRIMARY KEY,
  report_id UUID REFERENCES reports(id) ON DELETE CASCADE,
  from_state report_state,
  to_state report_state,
  changed_by UUID REFERENCES users(id),
  comment TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_report_history_report ON report_history (report_id);

-- -----------------------------
-- ACTORS / OPERATORS / WORKERS (basic registry)
-- -----------------------------
-- Actors table can represent operators and workers
CREATE TABLE IF NOT EXISTS actors (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  actor_type TEXT NOT NULL,            -- OPERATOR | WORKER | other
  vehicle_info JSONB,                  -- capacity, plate, type
  capacity INT DEFAULT 1,              -- how many tasks can be assigned concurrently
  status TEXT DEFAULT 'ACTIVE',        -- ACTIVE | INACTIVE | OFFLINE
  last_seen_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_actors_type_status ON actors (actor_type, status);

-- Actor location heartbeat (timeseries-lite)
CREATE TABLE IF NOT EXISTS actor_locations (
  id BIGSERIAL PRIMARY KEY,
  actor_id UUID REFERENCES actors(id) ON DELETE CASCADE,
  location GEOGRAPHY(POINT,4326) NOT NULL,
  heading REAL,
  speed REAL,
  reported_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_actor_locations_actor ON actor_locations (actor_id);
CREATE INDEX IF NOT EXISTS idx_actor_locations_location ON actor_locations USING GIST (location);

-- -----------------------------
-- TASKS (operational tasks created from reports)
-- -----------------------------
CREATE TABLE IF NOT EXISTS tasks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  report_id UUID REFERENCES reports(id) ON DELETE SET NULL,
  actor_id UUID REFERENCES actors(id) ON DELETE SET NULL,
  type task_type NOT NULL,
  state task_state NOT NULL DEFAULT 'PENDIENTE_ASIGNAR',
  priority INT DEFAULT 0,
  instructions TEXT,
  route_id UUID,                          -- optional reference to route-service table
  started_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  version INT NOT NULL DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_tasks_report ON tasks (report_id);
CREATE INDEX IF NOT EXISTS idx_tasks_actor ON tasks (actor_id);
CREATE INDEX IF NOT EXISTS idx_tasks_state ON tasks (state);

-- Task attachments / evidence (e.g., after cleaning)
CREATE TABLE IF NOT EXISTS task_attachments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  task_id UUID REFERENCES tasks(id) ON DELETE CASCADE,
  attachment_id UUID,
  filename TEXT,
  mime_type TEXT,
  remote_url TEXT,
  type TEXT DEFAULT 'AFTER',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_task_attachments_task ON task_attachments (task_id);

-- -----------------------------
-- ROUTES (route optimization results, optional)
-- -----------------------------
CREATE TABLE IF NOT EXISTS routes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  operator_id UUID REFERENCES actors(id) ON DELETE SET NULL,
  task_ids UUID[],                         -- ordered array of task ids (simple representation)
  geometry GEOMETRY(LineString,4326),
  total_distance_m INT,
  total_duration_s INT,
  optimized_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  fallback BOOLEAN DEFAULT FALSE
);
CREATE INDEX IF NOT EXISTS idx_routes_operator ON routes (operator_id);

-- -----------------------------
-- OUTBOX (for reliable event publication)
-- -----------------------------
CREATE TABLE IF NOT EXISTS outbox_events (
  id BIGSERIAL PRIMARY KEY,
  event_id UUID DEFAULT gen_random_uuid() UNIQUE,
  aggregate_type TEXT,
  aggregate_id UUID,
  event_type TEXT NOT NULL,
  payload JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  published BOOLEAN NOT NULL DEFAULT FALSE,
  published_at TIMESTAMPTZ,
  retry_count INT NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_outbox_published ON outbox_events (published);
CREATE INDEX IF NOT EXISTS idx_outbox_aggregate ON outbox_events (aggregate_type, aggregate_id);

-- -----------------------------
-- SYNC OPERATIONS (client-side batches)
-- -----------------------------
CREATE TABLE IF NOT EXISTS sync_operations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id TEXT NOT NULL,
  batch_id TEXT NOT NULL,
  operations JSONB NOT NULL,    -- array of operations with clientOpId, action, data
  result JSONB,                 -- result mapping, conflicts, errors
  status sync_status NOT NULL DEFAULT 'LOCAL_PENDING',
  received_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  processed_at TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_sync_operations_client ON sync_operations (client_id);

-- -----------------------------
-- PROCESSED EVENTS (for consumer idempotency)
-- -----------------------------
CREATE TABLE IF NOT EXISTS processed_events (
  event_id UUID PRIMARY KEY,
  consumer TEXT NOT NULL,
  processed_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_processed_events_consumer ON processed_events (consumer);

-- -----------------------------
-- NOTIFICATIONS (audit of outgoing notifications)
-- -----------------------------
CREATE TABLE IF NOT EXISTS notifications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  event_id UUID,                           -- domain event that triggered notification
  recipient_user_id UUID REFERENCES users(id),
  channel TEXT NOT NULL,                   -- PUSH | EMAIL | SMS | IN_APP
  payload JSONB,
  status TEXT NOT NULL DEFAULT 'PENDING',  -- PENDING | SENT | FAILED
  attempts INT NOT NULL DEFAULT 0,
  last_error TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  sent_at TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications (recipient_user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_status ON notifications (status);

-- -----------------------------
-- AUDIT LOG (append only, simplified)
-- -----------------------------
CREATE TABLE IF NOT EXISTS audit_logs (
  id BIGSERIAL PRIMARY KEY,
  entity_type TEXT,
  entity_id UUID,
  action TEXT,
  performed_by UUID,
  before_snapshot JSONB,
  after_snapshot JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_audit_entity ON audit_logs (entity_type, entity_id);

-- -----------------------------
-- Triggers / Helper functions (examples)
-- -----------------------------
-- Update updated_at automatically
CREATE OR REPLACE FUNCTION trigger_set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Attach triggers for tables that have updated_at
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'reports_set_updated_at') THEN
    CREATE TRIGGER reports_set_updated_at
    BEFORE UPDATE ON reports
    FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'tasks_set_updated_at') THEN
    CREATE TRIGGER tasks_set_updated_at
    BEFORE UPDATE ON tasks
    FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'actors_set_updated_at') THEN
    CREATE TRIGGER actors_set_updated_at
    BEFORE UPDATE ON actors
    FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();
  END IF;
END$$;

-- -----------------------------
-- Sample constraints / validations
-- -----------------------------
-- Phone format check (E.164 basic) - optional but helpful
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.table_constraints 
    WHERE constraint_name = 'chk_users_phone_e164' 
    AND table_name = 'users'
  ) THEN
    ALTER TABLE users ADD CONSTRAINT chk_users_phone_e164
    CHECK (phone IS NULL OR phone ~ '^\\+[1-9][0-9]{7,14}$');
  END IF;
END$$;

-- -----------------------------
-- Final notes
-- -----------------------------
-- 1) Consider partitioning high-volume tables (actor_locations, audit_logs, outbox_events) by time for scale.
-- 2) Use materialized views for dashboards (counts by state, SLA monitoring).
-- 3) Keep schema changes backward compatible where possible; when changing event payloads, version events (e.g., report.created.v2).
-- 4) Implement outbox writer in application logic: write domain change + outbox row in same DB transaction.