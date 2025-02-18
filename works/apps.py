from django.apps import AppConfig


class WorksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'works'
    # Изменение имени приложения.
    verbose_name = 'Работы'    # Подключаем сигналы.
    def ready(self):
        import works.signals
