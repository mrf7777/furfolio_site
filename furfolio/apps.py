from django.apps import AppConfig


class FurfolioConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'furfolio'

    def ready(self) -> None:
        from . import handlers
        return super().ready()
