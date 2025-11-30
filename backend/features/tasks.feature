# language: es
Característica: Gestión de Tareas de Limpieza
  Como administrador del sistema
  Quiero gestionar tareas de limpieza
  Para coordinar el trabajo de los equipos de limpieza

  Escenario: Crear una nueva tarea
    Dado que soy un usuario autenticado con rol de administrador
    Cuando creo una nueva tarea con los siguientes datos:
      | campo              | valor                          |
      | task_id            | TASK-001                       |
      | title              | Limpieza Zona Centro           |
      | description        | Recolección de residuos        |
      | priority           | 3                              |
      | scheduled_date     | 2025-12-01                     |
      | estimated_duration | 120                            |
    Entonces la tarea debe ser creada exitosamente
    Y el estado de la tarea debe ser "pending"

  Escenario: Asignar tarea a un trabajador
    Dado que existe una tarea con id "TASK-001"
    Y existe un usuario con rol de trabajador
    Cuando asigno la tarea al trabajador
    Entonces el estado de la tarea debe cambiar a "assigned"
    Y se debe crear un registro en el historial de asignaciones

  Escenario: Completar una tarea
    Dado que existe una tarea asignada con id "TASK-002"
    Y la tarea está en estado "in_progress"
    Cuando marco la tarea como completada con los datos:
      | campo              | valor                    |
      | result_notes       | Trabajo completado OK    |
      | waste_collected_kg | 45.5                     |
    Entonces la tarea debe estar en estado "completed"
    Y el campo completed_at debe tener una fecha

  Escenario: Listar tareas asignadas al usuario
    Dado que soy un usuario autenticado
    Y tengo 3 tareas asignadas
    Cuando solicito mis tareas
    Entonces debo recibir una lista con 3 tareas
    Y todas las tareas deben tener mi user_id como assigned_to
