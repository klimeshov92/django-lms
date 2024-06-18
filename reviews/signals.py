
from django.conf import settings
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.http import HttpResponseServerError
from .models import Review
from core.models import EmployeesObjectPermission
from guardian.shortcuts import assign_perm, remove_perm

# Импортируем логи.
import logging
# Создаем логгер с именем 'project'.
logger = logging.getLogger('project')

# Обработчик сигнала post_save для модели Organization.
@receiver(post_save, sender=Review)
def reviews_post_save(sender, instance, created, **kwargs):

    try:

        # Добавляем права.
        assign_perm('change_review', instance.creator, instance)

    # Логирование исключений, если они возникнут.
    except Exception as e:
        logger.error(f"Ошибка при обработке сигнала post_save для Review: {e}", exc_info=True)
        # Повторный вызов исключения в режиме отладки.
        if settings.DEBUG:
            raise
        else:
            return HttpResponseServerError("Ошибка сервера, обратитесь к администратору")