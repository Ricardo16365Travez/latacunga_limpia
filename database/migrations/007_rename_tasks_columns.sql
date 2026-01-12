-- MIGRACIÓN: Renombra columnas de tasks para alinearlas con el modelo backend
ALTER TABLE tasks RENAME COLUMN title TO titulo;
ALTER TABLE tasks RENAME COLUMN description TO descripcion;
