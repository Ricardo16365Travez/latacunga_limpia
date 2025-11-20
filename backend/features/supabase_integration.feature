# language: es
Característica: Conexión y configuración de Supabase
    Como administrador del sistema
    Quiero verificar que la integración con Supabase funcione correctamente
    Para asegurar la disponibilidad de la base de datos

    Escenario: Verificar conexión con Supabase
        Dado que las credenciales de Supabase están configuradas
        Cuando pruebo la conexión con la base de datos
        Entonces la conexión debería ser exitosa
        Y debería poder ejecutar consultas básicas

    Escenario: Verificar configuración de variables de entorno
        Dado que el sistema está iniciado
        Cuando reviso las variables de configuración de Supabase
        Entonces SUPABASE_URL debería estar definida
        Y SUPABASE_ANON_KEY debería estar definida
        Y SUPABASE_SERVICE_ROLE_KEY debería estar definida

    Escenario: Migración de base de datos
        Dado que las migraciones de Django están preparadas
        Cuando ejecuto las migraciones hacia Supabase
        Entonces todas las tablas deberían crearse correctamente
        Y no debería haber errores de migración

    Escenario: Verificar tablas principales
        Dado que las migraciones se ejecutaron exitosamente
        Cuando consulto las tablas principales
        Entonces la tabla auth_user debería existir
        Y la tabla authentication_user debería existir
        Y todas las relaciones deberían estar correctas