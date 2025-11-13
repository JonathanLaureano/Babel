from django.apps import AppConfig


class TranslatorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'translator'
    
    def ready(self):
        """Import checks when app is ready."""
        from . import checks  # noqa: F401
