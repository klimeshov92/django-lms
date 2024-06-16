# Импортируем настройки.
from django.conf import settings
# Импортируем модуль models из Django, используется для определения моделей в Django.
from django.db import models
# Импортируем post_save из модуля signals. post_save - сигнал, который отправляется после сохранения объекта модели.
from django.db.models.signals import post_save
# Импортируем receiver из модуля dispatch. receiver - функция-декоратор для подключения функций обработки сигналов.
from django.dispatch import receiver
# Импортируем пользовательские модели.
from .models import TestsQuestionsGenerator, Question, TestsQuestion
# Ответы.
from django.http import HttpResponseServerError


# Импортируем логи.
import logging
# Создаем логгер с именем 'project'.
logger = logging.getLogger('project')

# Сигнал генерации вопросов теста.
@receiver(post_save, sender=TestsQuestionsGenerator)
def update_tests_questions(sender, instance, **kwargs):

    # Проверка ошибок.
    try:

        # Забирае переменные.
        test = instance.test
        added_categories = instance.added_categories.all()
        added_questions = instance.added_questions.all()
        excluded_categories = instance.excluded_categories.all()
        excluded_questions = instance.excluded_questions.all()

        # Выводим информацию о связях многие-ко-многим
        if settings.DEBUG:
            logger.info(f"Добавленные категории: {added_categories}")
            logger.info(f"Добавленные вопросы: {added_questions}")
            logger.info(f"Исключенные категории: {excluded_categories}")
            logger.info(f"Исключенные вопросы: {excluded_questions}")

        # Получаем добавляемые вопросы.
        all_added_questions = Question.objects.filter(categories__in=added_categories).distinct() | added_questions.distinct()
        if settings.DEBUG:
            logger.info(f"Все добавляемые пользователи: {all_added_questions}")

        # Получаем добавляемые вопросы.
        all_excluded_questions = Question.objects.filter(categories__in=excluded_categories).distinct() | excluded_questions.distinct()
        if settings.DEBUG:
            logger.info(f"Все исключаемые пользователи: {all_excluded_questions}")

        # Итог
        final_questions = all_added_questions.exclude(id__in=all_excluded_questions.values_list('id', flat=True))
        if settings.DEBUG:
            logger.info(f"Все вопросы: {final_questions}")

        # Удаляем прежние вопросы.
        old_tests_questions = TestsQuestion.objects.filter(test__pk=test.id)
        if settings.DEBUG:
            logger.info(f"Старые вопросы теста: {old_tests_questions}")
        old_tests_questions.delete()

        # Создаем переменную позиции.
        position = 1
        # Назначаем вопросы тесту.
        for question in final_questions:
            # Создаем вопросы теста.
            new_tests_question = TestsQuestion.objects.create(test=test, question=question, position=position)
            if settings.DEBUG:
                logger.info(f"Новый вопрос теста: {new_tests_question}")
            position += 1

    # Логирование исключений, если они возникнут.
    except Exception as e:
        logger.error(f"Ошибка при обработке сигнала update_group_users для GroupsGenerator: {e}", exc_info=True)
        # Повторный вызов исключения в режиме отладки.
        if settings.DEBUG:
            raise
        else:
            return HttpResponseServerError("Ошибка сервера, обратитесь к администратору")
