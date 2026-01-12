-- MIGRACIÓN: Renombrar columnas de tasks para alinear con el modelo backend
ALTER TABLE tasks RENAME COLUMN type TO tipo;
ALTER TABLE tasks RENAME COLUMN priority TO prioridad;
ALTER TABLE tasks RENAME COLUMN state TO estado;
ALTER TABLE tasks RENAME COLUMN started_at TO progreso;
ALTER TABLE tasks RENAME COLUMN completed_at TO fecha_limite;
ALTER TABLE tasks RENAME COLUMN actor_id TO conductor_id;
ALTER TABLE tasks RENAME COLUMN route_id TO ruta_id;
