-- MIGRACIÓN: Cambia la columna progreso de timestamp a integer para alinearla con el modelo backend
ALTER TABLE tasks ALTER COLUMN progreso TYPE integer USING 0;
