-- MIGRACIÓN: Agrega columnas 'titulo' y 'descripcion' a tasks para alinear con el modelo backend
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS titulo text;
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS descripcion text;

-- Opcional: Copiar datos desde instructions a descripcion si existe
UPDATE tasks SET descripcion = instructions WHERE instructions IS NOT NULL AND (descripcion IS NULL OR descripcion = '');
