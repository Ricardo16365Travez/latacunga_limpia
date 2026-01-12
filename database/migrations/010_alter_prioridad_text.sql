-- MIGRACIÓN: Cambia la columna prioridad de integer a text para alinearla con el modelo backend
ALTER TABLE tasks ALTER COLUMN prioridad TYPE text USING prioridad::text;
