# language: es
Característica: Sistema de Notificaciones
  Como usuario del sistema
  Quiero recibir notificaciones
  Para estar informado sobre cambios y eventos importantes

  Escenario: Enviar notificación de tarea asignada
    Dado que existe un usuario con id 1
    Y existe una tarea con id "TASK-001"
    Cuando se asigna la tarea al usuario
    Entonces el usuario debe recibir una notificación tipo "task_assigned"
    Y la notificación debe tener título "Nueva tarea asignada"
    Y la notificación debe estar sin leer

  Escenario: Marcar notificación como leída
    Dado que tengo una notificación sin leer con id "NOTIF-001"
    Cuando marco la notificación como leída
    Entonces el campo is_read debe ser true
    Y el campo read_at debe tener una fecha

  Escenario: Obtener contador de notificaciones no leídas
    Dado que tengo 5 notificaciones
    Y 3 notificaciones están sin leer
    Cuando solicito el contador de no leídas
    Entonces debo recibir el número 3

  Escenario: Registrar token de dispositivo para push notifications
    Dado que soy un usuario autenticado
    Cuando registro un token de dispositivo con los datos:
      | campo       | valor                          |
      | token       | fcm-token-12345                |
      | platform    | android                        |
      | device_name | Samsung Galaxy S21             |
    Entonces el token debe ser registrado exitosamente
    Y el token debe estar activo
