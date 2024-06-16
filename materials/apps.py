from django.apps import AppConfig


class MaterialsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'materials'
    # Изменение имени приложения.
    verbose_name = 'Материалы'    # Подключаем сигналы.
    def ready(self):
        import materials.signals

