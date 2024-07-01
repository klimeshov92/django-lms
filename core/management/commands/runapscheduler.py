
# Асинхронных планировщик.
from apscheduler.schedulers.background import BackgroundScheduler
# Синхронный планировщик.
from apscheduler.schedulers.blocking import BlockingScheduler
# Установка времени выполнения задач по расписанию.
from apscheduler.triggers.cron import CronTrigger
# Импортируем настройки.
from django.conf import settings
# Создание пользовательских команд в Django.
from django.core.management.base import BaseCommand
# Импортируем утилиты django_apscheduler для управления соединениями с базой данных.
from django_apscheduler import util
# Импортируем класс DjangoJobStore для хранения задач в базе данных Django.
from django_apscheduler.jobstores import DjangoJobStore
# Импортируем модель DjangoJobExecution для выполнения задач.
from django_apscheduler.models import DjangoJobExecution
# Импортируем модели.
from learning_path.models import Result, Assignment, AssignmentRepeat
from materials.models import Material
from testing.models import Test
from testing.views import completion_of_test
from courses.models import Course
from core.models import GroupsGenerator
from events.models import ParticipantsGenerator
# Импортируем Q-фильтрацию.
from django.db.models import Q
# Импортируем дату и время, промежуток.
from datetime import datetime, timedelta
# Импорт времени с учетом таймзоны.
from django.utils import timezone
from dateutil.relativedelta import relativedelta

# Импортируем логи.
import logging
# Создаем логгер с именем 'project'.
logger = logging.getLogger('project')

# Тест планировщика.
def test():
    logger.info(f'Тест планировщика: {datetime.now()}')

# Провал обучения по срокам.
def autolearning():

    '''
    Провал обучения по срокам.
    '''

    # Забираем истекшие результаты обучения.
    learning_results = Result.objects.filter(
        # Это курс, тест или материал.
        (Q(course__isnull=False) | Q(test__isnull=False) | Q(material__isnull=False))
        &
        # Планируемая дата завершения которых, была вчера.
        (
            Q(learning_path_result__planned_end_date__lte=datetime.now().date() - timedelta(days=1))
            |
            Q(planned_end_date__lte=datetime.now().date() - timedelta(days=1))
        )
        &
        # И в которых установлен дедлайн.
        Q(assignment__deadlines=True)
    )
    logger.info(f'Результаты обучения с дедлайном: {learning_results}')

    # Проставляем провалено не выполненным.
    for learning_result in learning_results:

        logger.info(f'Результат обучения с дедлайном: {learning_result}')

        # Если обучение не пройдено.
        if learning_result.status != 'completed':

            # Для теста.
            if learning_result.type == 'test':

                # Забираем результат теста и тест.
                tests_result = learning_result
                test = tests_result.test

                # Вызываем завершение теста.
                completion_of_test(tests_result=tests_result, test=test)

            # Для других видов.
            else:

                # Проставляем провалено.
                learning_result.status = 'failed'
                learning_result.end_date = timezone.now()
                logger.info(f'Обучение не пройдено: {learning_results}')
                learning_result.save()
        else:
            logger.info(f'Обучение пройдено: {learning_results}')

    '''
    Обновление групп.
    '''

    # Забираем группы с генератором и автообновлением.
    generators = GroupsGenerator.objects.filter(autoupdate=True)
    logger.info(f'Генераторы групп на обновление: {generators}')

    # Запускаем сигнал пост-сейв, который обновит состав.
    for generator in generators:
        logger.info(f'Обновлен генератор группы: {generator}')
        generator.save()

    '''
    Повтор назначений.
    '''

    # Забираем назначения с включенным повтором.
    assignments_repeats = AssignmentRepeat.objects.all()
    logger.info(f'Повторяемые назначения: {assignments_repeats}')

    # Обрабатываем каждое назначение.
    for assignments_repeat in assignments_repeats:

        assignment = assignments_repeat.assignment

        # Пропускаем первый день старта назначения.
        if datetime.now().date() >= assignment.planned_start_date + timedelta(days=1):

            # Если повторяется ежедневно.
            if assignments_repeat.type == 'daily':
                logger.info(f'Обработка и запуск ежедневного назначения: {assignments_repeat}')

                # Создание назначения.
                repeat_assignments = Assignment.objects.create(
                    type=assignment.type,
                    learning_complex=assignment.learning_complex,
                    learning_path=assignment.learning_path,
                    material=assignment.material,
                    test=assignment.test,
                    course=assignment.course,
                    scorm_package=assignment.course.scorm_package,
                    participants=assignment.participants,
                    group=assignment.group,
                    employee=assignment.employee,
                    planned_start_date=datetime.now().date(),
                    duration=assignment.duration,
                    reassignment=assignment.reassignment,
                    deadlines=assignment.deadlines,
                    desc=assignment.desc,
                    is_repeat=True,
                )
                repeat_assignments.categories.set(assignment.categories.all())

                # Отметка о выполении.
                assignments_repeat.last_repeats_date = datetime.now().date()
                assignments_repeat.save()

            # Если повторяется еженедельно.
            if assignments_repeat.type == 'weekly':
                logger.info(f'Обработка еженедельного назначения: {assignments_repeat}')
                # Получаем день недели из назначения.
                repeat_day_of_week = assignments_repeat.day_of_week
                logger.info(f'День недели повтора: {repeat_day_of_week}')
                # Получаем текущий день недели
                current_day_of_week = datetime.now().strftime('%A').lower()
                logger.info(f'Текущий день недели: {current_day_of_week}')
                if current_day_of_week == repeat_day_of_week:
                    logger.info(f'Запуск: {assignments_repeat}')

                    # Создание назначения.
                    repeat_assignments = Assignment.objects.create(
                        type=assignment.type,
                        learning_complex=assignment.learning_complex,
                        learning_path=assignment.learning_path,
                        material=assignment.material,
                        test=assignment.test,
                        course=assignment.course,
                        scorm_package=assignment.course.scorm_package,
                        participants=assignment.participants,
                        group=assignment.group,
                        employee=assignment.employee,
                        planned_start_date=datetime.now().date(),
                        duration=assignment.duration,
                        reassignment=assignment.reassignment,
                        deadlines=assignment.deadlines,
                        desc=assignment.desc,
                        is_repeat=True,
                    )
                    repeat_assignments.categories.set(assignment.categories.all())

                    # Отметка о выполении.
                    assignments_repeat.last_repeats_date = datetime.now().date()
                    assignments_repeat.save()

            # Если повторяется ежемесячно.
            if assignments_repeat.type == 'monthly':
                logger.info(f'Обработка ежемесячного назначения: {assignments_repeat}')
                # Получаем день месяца из назначения.
                if assignments_repeat.last_repeats_date:
                    repeats_date = assignments_repeat.last_repeats_date + relativedelta(
                        months=assignments_repeat.month_interval)
                    logger.info(f'День месяца повтора (повтор уже был): {repeats_date}')
                else:
                    repeats_date = assignment.planned_start_date + relativedelta(
                        months=assignments_repeat.month_interval)
                    logger.info(f'День месяца повтора (повтора еще не было): {repeats_date}')
                # Получаем текущий день недели.
                current_date = datetime.now().date()
                logger.info(f'Текущий день месяца: {current_date}')
                if current_date >= repeats_date:
                    logger.info(f'Запуск: {assignments_repeat}')

                    # Создание назначения.
                    repeat_assignments = Assignment.objects.create(
                        type=assignment.type,
                        learning_complex=assignment.learning_complex,
                        learning_path=assignment.learning_path,
                        material=assignment.material,
                        test=assignment.test,
                        course=assignment.course,
                        scorm_package=assignment.course.scorm_package,
                        participants=assignment.participants,
                        group=assignment.group,
                        employee=assignment.employee,
                        planned_start_date=datetime.now().date(),
                        duration=assignment.duration,
                        reassignment=assignment.reassignment,
                        deadlines=assignment.deadlines,
                        desc=assignment.desc,
                        is_repeat=True,
                    )
                    repeat_assignments.categories.set(assignment.categories.all())

                    # Отметка о выполении.
                    assignments_repeat.last_repeats_date = datetime.now().date()
                    assignments_repeat.save()

# Обновление участников мероприятий.
def partisipiants_update():

    # Забираем группы с генератором.
    generators = ParticipantsGenerator.objects.filter(autoupdate=True)
    logger.info(f'Генераторы участников мероприятия на обновление: {generators}')

    # Запускаем сигнал пост-сейв, который обновит состав.
    for generator in generators:
        logger.info(f'Обновлен генератор участников мероприятия: {generator}')
        generator.save()

# Декорируем функцию для закрытия устаревших соединений с базой данных.
@util.close_old_connections
# Определяем функцию для удаления устаревших записей о выполнении задач.
def delete_old_job_executions(max_age=604_800):

    # Удаляем устаревшие записи из базы данных.
    DjangoJobExecution.objects.delete_old_job_executions(max_age)

# Запуск через команду: python manage.py runapscheduler.
# Определяем пользовательскую команду Django.
class Command(BaseCommand):

    # Определяем описание команды.
    help = "Запускает APScheduler."

    # Определяем метод для обработки команды.
    def handle(self, *args, **options):
        # Создаем планировщик задач с учетом часового пояса из настроек Django.
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        # Добавляем хранилище задач в планировщик.
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # Тест расписания.
        scheduler.add_job(
            test,  # Указываем функцию для выполнения.
            trigger=CronTrigger(hour="1"),  # Указываем расписание выполнения задачи.
            # trigger=CronTrigger(second="*/10"), # Указываем расписание выполнения задачи (каждые 10 секунд).
            id="test",  # Указываем уникальный идентификатор задачи.
            max_instances=1,  # Указываем максимальное количество одновременных экземпляров задачи.
            replace_existing=True,  # Если задача с таким идентификатором уже существует, её нужно заменить.
        )
        logger.info("Добавлена ежечасная задача 'test'.")  # Выводим информационное сообщение о добавлении задачи

        # Автообучение.
        scheduler.add_job(
            autolearning,  # Указываем функцию для выполнения.
            trigger = CronTrigger(hour="00", minute="00"),  # Указываем расписание выполнения задачи (каждый день).
            #trigger=CronTrigger(second="*/30"), # Указываем расписание выполнения задачи (каждые 30 секунд)
            id="autolearning",  # Указываем уникальный идентификатор задачи.
            max_instances=1,  # Указываем максимальное количество одновременных экземпляров задачи.
            replace_existing=True,  # Если задача с таким идентификатором уже существует, её нужно заменить.
        )
        logger.info("Добавлена ежедневная задача 'autolearning'.")  # Выводим информационное сообщение о добавлении задачи

        # Обновление генераторов участников мероприятий.
        scheduler.add_job(
            partisipiants_update,  # Указываем функцию для выполнения.
            trigger = CronTrigger(hour="00", minute="00"),  # Указываем расписание выполнения задачи (каждый день).
            # trigger=CronTrigger(second="*/30"), # Указываем расписание выполнения задачи (каждые 30 секунд)
            id="partisipiants_update",  # Указываем уникальный идентификатор задачи.
            max_instances=1,  # Указываем максимальное количество одновременных экземпляров задачи.
            replace_existing=True,  # Указываем, что если задача с таким идентификатором уже существует, её нужно заменить.
        )
        logger.info("Добавлена ежедневная задача 'partisipiants_update'.")  # Выводим информационное сообщение о добавлении задачи

        # Удаление лишних задач.
        scheduler.add_job(
            delete_old_job_executions,  # Указываем функцию для выполнения.
            trigger=CronTrigger(day_of_week="mon", hour="00", minute="00"),  # Указываем расписание выполнения задачи (каждый понедельник в полночь).
            id="delete_old_job_executions",  # Указываем уникальный идентификатор задачи.
            max_instances=1,  # Указываем максимальное количество одновременных экземпляров задачи.
            replace_existing=True,  # Указываем, что если задача с таким идентификатором уже существует, её нужно заменить.
        )
        logger.info("Добавлена еженедельная задача: 'delete_old_job_executions'.")  # Выводим информационное сообщение о добавлении задачи.

        # Обрабатываем возможное исключение KeyboardInterrupt (Ctrl+C).
        try:
            # Выводим информационное сообщение о запуске планировщика.
            logger.info("Запуск планировщика...")
            # Запускаем планировщик.
            scheduler.start()
        except KeyboardInterrupt:
            # Выводим информационное сообщение остановке планировщика.
            logger.info("Остановка планировщика...")
            # Останавливаем планировщик.
            scheduler.shutdown()
            # Выводим информационное сообщение об успешной остановке планировщика.
            logger.info("Планировщик успешно остановлен!")
