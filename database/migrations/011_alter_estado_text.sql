-- MIGRACIÓN: Cambia la columna estado de task_state (enum) a text para máxima compatibilidad
ALTER TABLE tasks ALTER COLUMN estado TYPE text USING estado::text;
