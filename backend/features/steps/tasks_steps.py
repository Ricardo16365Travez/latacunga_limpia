from behave import given, when, then
from django.contrib.auth import get_user_model
from apps.tasks.models import Task, TaskCheckpoint

User = get_user_model()


@given('que soy un usuario autenticado con rol de administrador')
def step_user_authenticated_admin(context):
    """Crear usuario administrador y autenticar."""
    context.user = User.objects.create_user(
        username='admin_test',
        email='admin@test.com',
        password='test123',
        is_staff=True
    )
    context.client.force_authenticate(user=context.user)


@given('que soy un usuario autenticado')
def step_user_authenticated(context):
    """Crear usuario normal y autenticar."""
    context.user = User.objects.create_user(
        username='user_test',
        email='user@test.com',
        password='test123'
    )
    context.client.force_authenticate(user=context.user)


@given('que existe una tarea con id "{task_id}"')
def step_task_exists(context, task_id):
    """Crear tarea de prueba."""
    if not hasattr(context, 'user') or context.user is None:
        context.user = User.objects.create_user(
            username='test_user',
            email='test@test.com',
            password='test123'
        )
    
    context.task = Task.objects.create(
        task_id=task_id,
        title='Tarea de prueba',
        description='Descripción de prueba',
        status='pending',
        priority=3,
        created_by=context.user
    )


@given('que existe una tarea asignada con id "{task_id}"')
def step_assigned_task_exists(context, task_id):
    """Crear tarea asignada."""
    if not hasattr(context, 'user') or context.user is None:
        context.user = User.objects.create_user(
            username='test_user',
            email='test@test.com',
            password='test123'
        )
    
    context.task = Task.objects.create(
        task_id=task_id,
        title='Tarea asignada',
        status='assigned',
        assigned_to=context.user,
        created_by=context.user
    )


@given('la tarea está en estado "{status}"')
def step_task_status(context, status):
    """Establecer estado de la tarea."""
    context.task.status = status
    context.task.save()


@given('tengo {count:d} tareas asignadas')
def step_multiple_tasks_assigned(context, count):
    """Crear múltiples tareas asignadas."""
    if not hasattr(context, 'user'):
        step_user_authenticated(context)
    
    for i in range(count):
        Task.objects.create(
            task_id=f'TASK-{i+1:03d}',
            title=f'Tarea {i+1}',
            status='assigned',
            assigned_to=context.user,
            created_by=context.user
        )


@when('creo una nueva tarea con los siguientes datos')
def step_create_task(context):
    """Crear tarea con datos de la tabla."""
    data = {}
    for row in context.table:
        field = row['campo']
        value = row['valor']
        # Convertir valores numéricos
        if field == 'priority' or field == 'estimated_duration':
            value = int(value)
        data[field] = value
    
    data['created_by'] = context.user.id
    context.response = context.client.post('/api/tasks/tasks/', data, format='json')


@when('asigno la tarea al trabajador')
def step_assign_task(context):
    """Asignar tarea a un trabajador."""
    worker = User.objects.create_user(
        username='worker_test',
        email='worker@test.com',
        password='test123'
    )
    
    data = {'assigned_to': worker.id}
    context.response = context.client.post(
        f'/api/tasks/tasks/{context.task.id}/assign/',
        data,
        format='json'
    )


@when('marco la tarea como completada con los datos')
def step_complete_task(context):
    """Completar tarea."""
    data = {}
    for row in context.table:
        field = row['campo']
        value = row['valor']
        if field == 'waste_collected_kg':
            value = float(value)
        data[field] = value
    
    context.response = context.client.post(
        f'/api/tasks/tasks/{context.task.id}/complete/',
        data,
        format='json'
    )


@when('solicito mis tareas')
def step_get_my_tasks(context):
    """Obtener tareas del usuario actual."""
    context.response = context.client.get('/api/tasks/tasks/my_tasks/')


@then('la tarea debe ser creada exitosamente')
def step_task_created(context):
    """Verificar que la tarea fue creada."""
    assert context.response.status_code == 201, \
        f"Expected 201, got {context.response.status_code}"


@then('el estado de la tarea debe ser "{expected_status}"')
def step_verify_task_status(context, expected_status):
    """Verificar estado de la tarea."""
    if context.response:
        data = context.response.json()
        if 'task' in data:
            actual_status = data['task']['status']
        else:
            actual_status = data.get('status')
    else:
        context.task.refresh_from_db()
        actual_status = context.task.status
    
    assert actual_status == expected_status, \
        f"Expected status '{expected_status}', got '{actual_status}'"


@then('el estado de la tarea debe cambiar a "{expected_status}"')
def step_verify_task_status_changed(context, expected_status):
    """Verificar cambio de estado."""
    step_verify_task_status(context, expected_status)


@then('se debe crear un registro en el historial de asignaciones')
def step_verify_history_created(context):
    """Verificar que se creó registro en historial."""
    from apps.tasks.models import TaskAssignmentHistory
    count = TaskAssignmentHistory.objects.filter(task=context.task).count()
    assert count > 0, "No se creó registro en historial"


@then('la tarea debe estar en estado "{expected_status}"')
def step_task_in_status(context, expected_status):
    """Verificar estado de la tarea."""
    step_verify_task_status(context, expected_status)


@then('el campo completed_at debe tener una fecha')
def step_verify_completed_at(context):
    """Verificar que completed_at tiene fecha."""
    context.task.refresh_from_db()
    assert context.task.completed_at is not None, \
        "completed_at no tiene fecha"


@then('debo recibir una lista con {count:d} tareas')
def step_verify_task_count(context, count):
    """Verificar cantidad de tareas en respuesta."""
    assert context.response.status_code == 200
    data = context.response.json()
    actual_count = len(data)
    assert actual_count == count, \
        f"Expected {count} tasks, got {actual_count}"


@then('todas las tareas deben tener mi user_id como assigned_to')
def step_verify_assigned_to_me(context):
    """Verificar que todas las tareas están asignadas al usuario."""
    data = context.response.json()
    for task in data:
        assert task['assigned_to'] == context.user.id, \
            f"Task {task['task_id']} is not assigned to current user"
