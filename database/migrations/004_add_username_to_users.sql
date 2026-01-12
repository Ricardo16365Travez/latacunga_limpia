-- MIGRACIÓN: Agrega columna username a la tabla users si no existe
ALTER TABLE users ADD COLUMN IF NOT EXISTS username text;

-- Opcional: Rellenar username con email si está vacío
UPDATE users SET username = email WHERE username IS NULL OR username = '';
