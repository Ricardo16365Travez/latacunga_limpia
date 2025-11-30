# language: es
Característica: Gestión de Rutas con OSRM
  Como coordinador de rutas
  Quiero gestionar y optimizar rutas de limpieza
  Para maximizar la eficiencia de los recorridos

  Escenario: Crear una zona de limpieza
    Dado que soy un usuario autenticado con permisos de administrador
    Cuando creo una zona de limpieza con los siguientes datos:
      | campo         | valor                  |
      | name          | Zona Centro            |
      | zone_type     | residential            |
      | priority      | 3                      |
      | frequency     | daily                  |
      | is_active     | true                   |
    Entonces la zona debe ser creada exitosamente
    Y la zona debe tener un polígono geográfico válido

  Escenario: Calcular ruta optimizada con OSRM
    Dado que existen los siguientes waypoints:
      | latitud   | longitud  |
      | -0.93517  | -78.61478 |
      | -0.93612  | -78.61556 |
      | -0.93702  | -78.61634 |
    Cuando solicito calcular una ruta optimizada
    Entonces debo recibir una ruta con geometría LineString
    Y la ruta debe tener distancia en kilómetros
    Y la ruta debe tener duración en minutos

  Escenario: Obtener zonas de limpieza activas
    Dado que existen 5 zonas de limpieza
    Y 3 zonas están activas
    Cuando solicito las zonas activas
    Entonces debo recibir una lista con 3 zonas
    Y todas las zonas deben tener is_active = true

  Escenario: Verificar servicio OSRM
    Cuando solicito el estado del servicio OSRM
    Entonces el servicio debe estar disponible
    Y la respuesta debe indicar "healthy"
