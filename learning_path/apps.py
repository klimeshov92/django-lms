from django.apps import AppConfig


class LearningPathConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'learning_path'
    # Изменение имени приложения.
    verbose_name = 'Траектории обучения'
    # Подключаем сигналы.
    def ready(self):
        import learning_path.signals