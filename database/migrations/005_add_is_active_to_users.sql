-- MIGRACIÓN: Agrega columna is_active a la tabla users si no existe
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_active boolean DEFAULT true;

-- Opcional: Rellenar is_active como true para todos los usuarios existentes
UPDATE users SET is_active = true WHERE is_active IS NULL;
