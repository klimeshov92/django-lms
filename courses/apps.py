from django.apps import AppConfig

class CoursesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'courses'
    # Изменение имени приложения.
    verbose_name = 'Курсы'
    # Подключаем сигналы.
    def ready(self):
        import courses.signals