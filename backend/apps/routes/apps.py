from django.apps import AppConfig


class RoutesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.routes'
    verbose_name = 'Gestión de Rutas'
    
    def ready(self):
        # Importar signals si los hay
        pass