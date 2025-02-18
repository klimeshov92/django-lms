# Импорт модуля регулярных выражений для работы с текстом.
import re
# Импорт функции receiver для указания, что функция является обработчиком сигнала.
from django.dispatch import receiver
# Импорт сигнала pre_save, который отправляется перед сохранением объекта в базу данных.
from django.db.models.signals import pre_save, post_save
# Импорт модели, для которой будет установлен обработчик сигнала.
from django.http import HttpResponseServerError
from learning_path.models import WorkReview, Result
# Импорт парсера шаблона.
from bs4 import BeautifulSoup
# Импорт настроек
from django.conf import settings


# Импортируем логи.
import logging
# Создаем логгер с именем 'project'.
logger = logging.getLogger('project')

# Оборачивание таблиц в див с классом 'material-content-table-responsive'.
@receiver(pre_save, sender=Result)
def wrap_tables_result(sender, instance, **kwargs):
    try:
        # Проверяем, что содержимое не пустое.
        if instance.executor_report:
            # Парсинг содержимого экземпляра.
            soup = BeautifulSoup(instance.executor_report, "html.parser")
            # Поиск всех таблиц.
            tables = soup.find_all('table')
            if tables:
                for table in tables:
                    # Оборачивание таблицы в див, если она не обёрнута.
                    if 'material-content-table-responsive' not in table.parent.get('class', []):
                        new_div = soup.new_tag("div", **{'class': 'material-content-table-responsive'})
                        table.wrap(new_div)
                # Обновление содержимого экземпляра.
                instance.executor_report = str(soup)
    except Exception as e:
        # Логирование ошибки.
        logger.error(f"Ошибка при оборачивании таблиц: {e}", exc_info=True)
        # Повторное возбуждение исключения, если включен режим отладки.
        if settings.DEBUG:
            raise
        else:
            return HttpResponseServerError("Ошибка сервера, обратитесь к администратору")

# Оборачивание таблиц в див с классом 'material-content-table-responsive'.
@receiver(pre_save, sender=WorkReview)
def wrap_tables_work_review(sender, instance, **kwargs):
    try:
        # Парсинг содержимого экземпляра.
        soup = BeautifulSoup(instance.reviewer_report, "html.parser")
        # Поиск всех таблиц.
        tables = soup.find_all('table')
        if tables:
            for table in tables:
                # Оборачивание таблицы в див, если она не обёрнута.
                if 'material-content-table-responsive' not in table.parent.get('class', []):
                    new_div = soup.new_tag("div", **{'class': 'material-content-table-responsive'})
                    table.wrap(new_div)
            # Обновление содержимого экземпляра.
            instance.reviewer_report = str(soup)
    except Exception as e:
        # Логирование ошибки.
        logger.error(f"Ошибка при оборачивании таблиц: {e}", exc_info=True)
        # Повторное возбуждение исключения, если включен режим отладки.
        if settings.DEBUG:
            raise
        else:
            return HttpResponseServerError("Ошибка сервера, обратитесь к администратору")

# Создание контроля результутов.
@receiver(post_save, sender=WorkReview)
def update_work_result(sender, instance, created, **kwargs):

    # Проверка ошибок.
    try:
        # Извлекаем связанные объекты.
        result = instance.result
        # Проставляем статус и баллы.
        result.status = instance.status
        result.score_scaled = instance.score_scaled
        result.save()
        if settings.DEBUG:
            logger.info(f"Новый статус результата: {result.status}")
            logger.info(f"Новый % результата: {result.score_scaled}")
    # Логирование исключений, если они возникнут.
    except Exception as e:
        logger.error(f"Ошибка при обработке сигнала update_work_result для WorkReview: {e}", exc_info=True)
        # Повторный вызов исключения в режиме отладки.
        if settings.DEBUG:
            raise
        else:
            return HttpResponseServerError("Ошибка сервера, обратитесь к администратору")
