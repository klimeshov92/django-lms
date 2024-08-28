# Импорт всего для сигналов.
import os
import shutil
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.conf import settings
from django.db import models
from django.http import HttpResponseServerError
from .models import Course

# Импортируем логи.
import logging
# Создаем логгер с именем 'project'.
logger = logging.getLogger('project')

# Функция-обработчик сигнала post_delete
@receiver(post_delete, sender=Course)
def delete_scorm_package_directory(sender, instance, **kwargs):
    try:
        # Получаем путь к директории для удаления
        directory_path = os.path.join(settings.MEDIA_ROOT, 'scorm_packages', str(instance.id))

        # Удаляем директорию
        if os.path.exists(directory_path):
            shutil.rmtree(directory_path)

            # Логирование успешного удаления
            logger.info(f"Успешное удаление директории SCORM-пакета {instance.id} по пути {directory_path}")
        else:
            # Логирование, если директория не существует
            logger.warning(f"Директория SCORM-пакета {instance.id} по пути {directory_path} не существует")

    except Exception as e:
        # Логирование ошибки при удалении директории
        logger.error(f"Ошибка при удалении директории SCORM-пакета {instance.id}: {str(e)}")

        # Повторный вызов исключения в режиме отладки.
        if settings.DEBUG:
            raise
        else:
            return HttpResponseServerError("Ошибка сервера, обратитесь к администратору")
