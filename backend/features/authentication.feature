# language: es
Característica: Autenticación de usuarios con Supabase
    Como usuario del sistema de gestión de residuos
    Quiero poder autenticarme usando Supabase
    Para acceder a las funcionalidades del sistema

    Antecedentes:
        Dado que el sistema está configurado con Supabase
        Y la base de datos está disponible

    Escenario: Registro exitoso de usuario
        Dado que soy un usuario nuevo
        Cuando registro mi cuenta con:
            | campo     | valor                    |
            | email     | test@latacunga.gob.ec   |
            | password  | TestPassword123!        |
            | nombre    | Juan                     |
            | apellido  | Pérez                    |
            | rol       | citizen                  |
        Entonces debería recibir una confirmación de registro
        Y el usuario debería existir en Supabase
        Y debería recibir un token JWT válido

    Escenario: Inicio de sesión exitoso
        Dado que existe un usuario registrado con:
            | email    | test@latacunga.gob.ec |
            | password | TestPassword123!      |
        Cuando intento iniciar sesión con esas credenciales
        Entonces debería recibir un token JWT válido
        Y debería poder acceder a endpoints protegidos

    Escenario: Inicio de sesión con credenciales incorrectas
        Dado que existe un usuario registrado
        Cuando intento iniciar sesión con credenciales incorrectas
        Entonces debería recibir un mensaje de error
        Y no debería recibir ningún token

    Escenario: Acceso a endpoints protegidos sin token
        Dado que no estoy autenticado
        Cuando intento acceder a un endpoint protegido
        Entonces debería recibir un error 401 Unauthorized

    Escenario: Sincronización de datos entre Django y Supabase
        Dado que registro un nuevo usuario en Django
        Cuando el usuario se crea exitosamente
        Entonces los datos deberían sincronizarse automáticamente con Supabase
        Y debería poder autenticarme usando las credenciales de Supabase