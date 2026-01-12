-- Migración para crear la tabla de tareas
CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    titulo VARCHAR(255) NOT NULL,
    descripcion TEXT,
    tipo VARCHAR(50) NOT NULL DEFAULT 'RECOLECCION',
    prioridad VARCHAR(20) NOT NULL DEFAULT 'MEDIA',
    estado VARCHAR(20) NOT NULL DEFAULT 'PENDIENTE',
    progreso INTEGER DEFAULT 0,
    fecha_limite TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    conductor_id INTEGER REFERENCES conductores(id) ON DELETE SET NULL,
    ruta_id INTEGER REFERENCES rutas(id) ON DELETE SET NULL
);