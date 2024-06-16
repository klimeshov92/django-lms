# Импорт модуля регулярных выражений для работы с текстом.
import re
# Импорт функции receiver для указания, что функция является обработчиком сигнала.
from django.dispatch import receiver
# Импорт сигнала pre_save, который отправляется перед сохранением объекта в базу данных.
from django.db.models.signals import pre_save
# Импорт модели, для которой будет установлен обработчик сигнала.
from django.http import HttpResponseServerError
from .models import Material
# Импорт парсера шаблона.
from bs4 import BeautifulSoup
# Импорт настроек
from django.conf import settings


# Импортируем логи.
import logging
# Создаем логгер с именем 'project'.
logger = logging.getLogger('project')

# Добавление атрибута 'nodownload' ко всем элементам 'video'.
@receiver(pre_save, sender=Material)
def add_nodownload_to_all_videos(sender, instance, **kwargs):
    try:
        # Проверка наличия содержимого экземпляра.
        if instance.content:
            soup = BeautifulSoup(instance.content, 'html.parser')
            # Поиск всех элементов 'video'.
            videos = soup.find_all('video')
            for video in videos:
                # Добавление 'nodownload' к 'controlsList', если его нет.
                if 'controlsList' not in video.attrs or 'nodownload' not in video.attrs['controlsList']:
                    video['controlsList'] = 'nodownload'
            # Обновление содержимого экземпляра.
            instance.content = str(soup)
    except Exception as e:
        # Логирование ошибки.
        logger.error(f"Ошибка при добавлении запрета на скачивание для видео: {e}", exc_info=True)
        # Повторное возбуждение исключения, если включен режим отладки.
        if settings.DEBUG:
            raise
        else:
            return HttpResponseServerError("Ошибка сервера, обратитесь к администратору")

# Оборачивание таблиц в див с классом 'material-content-table-responsive'.
@receiver(pre_save, sender=Material)
def wrap_tables(sender, instance, **kwargs):
    try:
        # Парсинг содержимого экземпляра.
        soup = BeautifulSoup(instance.content, "html.parser")
        # Поиск всех таблиц.
        tables = soup.find_all('table')
        for table in tables:
            # Оборачивание таблицы в див, если она не обёрнута.
            if 'material-content-table-responsive' not in table.parent.get('class', []):
                new_div = soup.new_tag("div", **{'class': 'material-content-table-responsive'})
                table.wrap(new_div)
        # Обновление содержимого экземпляра.
        instance.content = str(soup)
    except Exception as e:
        # Логирование ошибки.
        logger.error(f"Ошибка при оборачивании таблиц: {e}", exc_info=True)
        # Повторное возбуждение исключения, если включен режим отладки.
        if settings.DEBUG:
            raise
        else:
            return HttpResponseServerError("Ошибка сервера, обратитесь к администратору")



