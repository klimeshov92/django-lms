from django.apps import AppConfig


class LeadersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'leaders'
    # Изменение имени приложения.
    verbose_name = 'Лидеры'
    # Подключаем сигналы.
    def ready(self):
        import leaders.signals

