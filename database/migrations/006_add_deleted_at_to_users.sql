-- MIGRACIÓN: Agrega columna deleted_at a la tabla users si no existe
ALTER TABLE users ADD COLUMN IF NOT EXISTS deleted_at timestamp with time zone;
