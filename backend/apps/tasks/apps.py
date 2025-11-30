from django.apps import AppConfig


class TasksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.tasks'
    verbose_name = 'Gestión de Tareas'

    def ready(self):
        """Importar señales cuando la app esté lista."""
        pass