from django.apps import AppConfig


class TestingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'testing'
    # Изменение имени приложения.
    verbose_name = 'Тестирование'
    # Подключаем сигналы.
    def ready(self):
        import testing.signals
