from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    # Изменение имени приложения.
    verbose_name = 'Ядро'
    # Подключаем сигналы.
    def ready(self):
        import core.signals
