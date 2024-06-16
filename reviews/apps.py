from django.apps import AppConfig


class ReviewsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reviews'
    # Изменение имени приложения.
    verbose_name = 'Отзывы'
    # Подключаем сигналы.
    def ready(self):
        import reviews.signals
