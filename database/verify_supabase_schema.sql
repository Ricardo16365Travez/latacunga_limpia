-- ============================================
-- SCRIPT DE VERIFICACIÓN DE ESQUEMA SUPABASE
-- ============================================

-- 1. Verificar que los esquemas existen
SELECT 
    'ESQUEMAS CREADOS' as verificacion,
    schema_name 
FROM information_schema.schemata 
WHERE schema_name IN ('incidentes', 'validacion', 'rutas', 'tareas', 'notificaciones', 'reportes')
ORDER BY schema_name;

-- 2. Contar tablas por esquema
SELECT 
    'TABLAS POR ESQUEMA' as verificacion,
    table_schema,
    COUNT(*) as total_tablas
FROM information_schema.tables 
WHERE table_schema IN ('incidentes', 'rutas', 'tareas', 'notificaciones', 'reportes')
    AND table_type = 'BASE TABLE'
GROUP BY table_schema
ORDER BY table_schema;

-- 3. Listar todas las tablas creadas
SELECT 
    'LISTA DE TABLAS' as verificacion,
    table_schema || '.' || table_name as tabla_completa
FROM information_schema.tables 
WHERE table_schema IN ('incidentes', 'rutas', 'tareas', 'notificaciones', 'reportes')
    AND table_type = 'BASE TABLE'
ORDER BY table_schema, table_name;

-- 4. Verificar índices creados
SELECT 
    'ÍNDICES CREADOS' as verificacion,
    schemaname,
    COUNT(*) as total_indices
FROM pg_indexes 
WHERE schemaname IN ('incidentes', 'rutas', 'tareas', 'notificaciones', 'reportes')
GROUP BY schemaname
ORDER BY schemaname;

-- 5. Verificar triggers creados
SELECT 
    'TRIGGERS CREADOS' as verificacion,
    trigger_schema,
    trigger_name,
    event_object_table as tabla
FROM information_schema.triggers
WHERE trigger_schema IN ('incidentes', 'rutas', 'tareas', 'notificaciones', 'reportes')
ORDER BY trigger_schema, event_object_table;

-- 6. Verificar vistas creadas
SELECT 
    'VISTAS CREADAS' as verificacion,
    table_schema || '.' || table_name as vista_completa
FROM information_schema.views 
WHERE table_schema IN ('validacion', 'tareas', 'incidentes')
ORDER BY table_schema, table_name;

-- 7. Verificar extensiones habilitadas
SELECT 
    'EXTENSIONES' as verificacion,
    extname as extension_name,
    extversion as version
FROM pg_extension 
WHERE extname IN ('uuid-ossp', 'postgis')
ORDER BY extname;

-- 8. Verificar foreign keys
SELECT 
    'FOREIGN KEYS' as verificacion,
    tc.table_schema,
    tc.table_name,
    COUNT(*) as total_fk
FROM information_schema.table_constraints tc
WHERE tc.constraint_type = 'FOREIGN KEY'
    AND tc.table_schema IN ('incidentes', 'rutas', 'tareas', 'notificaciones', 'reportes')
GROUP BY tc.table_schema, tc.table_name
ORDER BY tc.table_schema, tc.table_name;

-- 9. Resumen completo
SELECT 
    'RESUMEN COMPLETO' as verificacion,
    (SELECT COUNT(*) FROM information_schema.schemata 
     WHERE schema_name IN ('incidentes', 'validacion', 'rutas', 'tareas', 'notificaciones', 'reportes')) as esquemas,
    (SELECT COUNT(*) FROM information_schema.tables 
     WHERE table_schema IN ('incidentes', 'rutas', 'tareas', 'notificaciones', 'reportes')
     AND table_type = 'BASE TABLE') as tablas,
    (SELECT COUNT(*) FROM information_schema.views 
     WHERE table_schema IN ('validacion', 'tareas', 'incidentes')) as vistas,
    (SELECT COUNT(*) FROM pg_indexes 
     WHERE schemaname IN ('incidentes', 'rutas', 'tareas', 'notificaciones', 'reportes')) as indices,
    (SELECT COUNT(*) FROM information_schema.triggers
     WHERE trigger_schema IN ('incidentes', 'rutas', 'tareas', 'notificaciones', 'reportes')) as triggers;

-- 10. Verificar que las tablas estén vacías (recién creadas)
SELECT 
    'TABLAS VACÍAS' as verificacion,
    schemaname || '.' || tablename as tabla,
    n_live_tup as registros
FROM pg_stat_user_tables
WHERE schemaname IN ('incidentes', 'rutas', 'tareas', 'notificaciones', 'reportes')
ORDER BY schemaname, tablename;
