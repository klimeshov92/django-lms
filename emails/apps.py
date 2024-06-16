from django.apps import AppConfig


class EmailsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'emails'
    # Изменение имени приложения.
    verbose_name = 'Рассылки'
    # Подключаем сигналы.
    def ready(self):
        import emails.signals


