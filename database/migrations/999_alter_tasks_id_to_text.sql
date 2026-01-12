-- MIGRACIÓN: Cambia el tipo de columna id en tasks de UUID a TEXT
ALTER TABLE tasks ALTER COLUMN id TYPE TEXT USING id::text;