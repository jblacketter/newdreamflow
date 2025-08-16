from django.apps import AppConfig


class ThingsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.things'
    
    def ready(self):
        import apps.things.signals
