# Импортируем настройки.
from django.conf import settings
# Импортируем модуль models из Django, используется для определения моделей в Django.
from django.db import models
# Импортируем post_save из модуля signals. post_save - сигнал, который отправляется после сохранения объекта модели.
from django.db.models.signals import post_save, post_delete, pre_save
# Импортируем receiver из модуля dispatch. receiver - функция-декоратор для подключения функций обработки сигналов.
from django.dispatch import receiver
# Импортируем модели.
from .models import ParticipantsGenerator, Event
from learning_path.models import Result
from core.models import Employee, EmployeesGroup, EmployeesGroupObjectPermission
# Права.
from django.http import HttpResponseServerError
from guardian.shortcuts import assign_perm
from django.db import transaction
from datetime import datetime, timedelta


# Импортируем логи.
import logging

# Создаем логгер с именем 'project'.
logger = logging.getLogger('project')

# Сигнал сохранения участников меропрриятия.
@transaction.atomic
@receiver(post_save, sender=Event)
def events_participants_and_responsibles_save(sender, instance, created, **kwargs):

    # Проверка ошибок.
    try:

        # Устанавливаем имя группы для участников и отвественных обучения.
        participants_group_name = f"Участники мероприятия: [{instance.pk}] {instance.name} - {instance.date.strftime('%d.%m.%Y')}"
        responsibles_group_name = f"Ответственные мероприятия: [{instance.pk}] {instance.name} - {instance.date.strftime('%d.%m.%Y')}"

        # Если группа ответственных создана.
        if created:

            # Забираем группу для отвественных и участников мероприятия.
            responsibles_group = EmployeesGroup.objects.create(name=responsibles_group_name, type='event_responsibles')

            # Привязываем к мероприятию.
            instance.responsibles_group = responsibles_group
            logger.info(f"Была создана группа для отвественных мероприятия: {responsibles_group}.")

            # Даем права смотреть мероприятие.
            assign_perm('view_event', responsibles_group, instance)
            logger.info(f"Право на просмотр мероприятия {instance} назначено группе {responsibles_group}.")

            # Даем права менять мероприятие.
            assign_perm('change_event', responsibles_group, instance)
            logger.info(f"Право на изменение мероприятия {instance} назначено группе {responsibles_group}.")

            # Забираем группу для участников.
            participants_group = EmployeesGroup.objects.create(name=participants_group_name, type='event_participants')

            # Привязываем к мероприятию.
            instance.participants_group = participants_group
            logger.info(f"Была создана группа для участников мероприятия: {participants_group}.")

            # Даем права смотреть мероприятие.
            assign_perm('view_event', participants_group, instance)
            logger.info(f"Право на просмотр мероприятия {instance} назначено группе {participants_group}.")

            # Сохраняем.
            instance.save()

        # Если мероприятие обновилось.
        else:

            if instance.responsibles_group.name != responsibles_group_name:
                instance.responsibles_group.name = responsibles_group_name
                instance.responsibles_group.save()
                logger.info(f"Была изменена группа для отвественных мероприятия: {instance.responsibles_group}.")

            # Если имя группы изменилось после обновления мероприятия.
            if instance.participants_group.name != participants_group_name:
                instance.participants_group.name = participants_group_name
                instance.participants_group.save()
                logger.info(f"Была изменена группа для участников мероприятия: {instance.responsibles_group}.")

        # Назначаем отвественных.
        if instance.responsibles.exists():
            instance.responsibles_group.user_set.set(instance.responsibles.all())
            logger.info(f'Отвественные мероприятия: {instance.responsibles_group.user_set.all()}')

    # Логирование исключений, если они возникнут.
    except Exception as e:
        logger.error(f"Ошибка при обработке сигнала events_participants_and_responsibles_save для Event: {e}", exc_info=True)
        # Повторный вызов исключения в режиме отладки.
        if settings.DEBUG:
            raise
        else:
            return HttpResponseServerError("Ошибка сервера, обратитесь к администратору")


# Сигнал определения состава участников.
@receiver(post_save, sender=ParticipantsGenerator)
def update_events_participants(sender, instance, **kwargs):

    # Проверка ошибок.
    try:

        # Забирае переменные.
        event = instance.event
        participants_group = instance.event.participants_group
        added_groups = instance.added_groups.all()
        added_users = instance.added_users.all()
        excluded_groups = instance.excluded_groups.all()
        excluded_users = instance.excluded_users.all()

        # Выводим информацию о связях многие-ко-многим
        logger.info(f"Добавленные группы: {added_groups}")
        logger.info(f"Добавленные пользователи: {added_users}")
        logger.info(f"Исключенные группы: {excluded_groups}")
        logger.info(f"Исключенные пользователи: {excluded_users}")

        # Получаем добавляемых пользователей.
        all_added_users = Employee.objects.filter(groups__in=added_groups, is_active=True).distinct() | added_users.distinct()
        logger.info(f"Все добавляемые пользователи: {all_added_users}")

        # Получаем исключаемых пользователей.
        all_excluded_users = Employee.objects.filter(groups__in=excluded_groups, is_active=True).distinct() | excluded_users.distinct()
        logger.info(f"Все исключаемые пользователи: {all_excluded_users}")

        # Итог
        final_users = all_added_users.exclude(id__in=all_excluded_users.values_list('id', flat=True))
        logger.info(f"Все пользователи: {final_users}")

        # Фильтруем по датам.
        if instance.days_worked_lte is not None:
            start_date_lte = datetime.now().date() - timedelta(days=instance.days_worked_lte)
            final_users = final_users.filter(placements__start_date__gte=start_date_lte)
            logger.info(f"Пользователи с датой приема после {start_date_lte}: {final_users}")
        if instance.days_worked_gte is not None:
            start_date_gte = datetime.now().date() - timedelta(days=instance.days_worked_gte)
            final_users = final_users.filter(placements__start_date__lte=start_date_gte)
            logger.info(f"Пользователи с датой приема до {start_date_gte}: {final_users}")

        # Удаление результатов.
        if Result.objects.filter(event=event).exists():

            # Забираем результаты мероприятия.
            event_results = Result.objects.filter(event=event).all()
            logger.info(f'Все результаты мероприятия: {event_results}')

            # Забираем ID участников мероприятия.
            event_employees_id = [event_result.employee.id for event_result in event_results]
            logger.info(f'ID участников мерпориятия: {event_employees_id}')

            # Забираем участников мероприятия через ID.
            event_employees = Employee.objects.filter(id__in=event_employees_id)
            logger.info(f'Все участники мероприятия: {event_employees}')

            # Забираем удаляемых участников (имеющиеся минус обновленные).
            deleted_event_employees = event_employees.exclude(id__in=final_users.values_list('id', flat=True))
            logger.info(f'Участники на удаление: {deleted_event_employees}')

            # Забираем удаляемые результаты.
            deleted_event_results = event_results.filter(employee__in=deleted_event_employees)
            logger.info(f'Результаты на удаление: {deleted_event_results}')

            # Выпоняем удаление.
            deleted_event_results.delete()

        # Обработка списка.
        for employee in final_users:
            # Подготавливаем словарь для заполнения.
            result_defaults = {
                'planned_end_date': event.date,
            }
            # Проверяем результат участника.
            result, created = Result.objects.get_or_create(
                type='event',
                status='registered',
                employee=employee,
                event=event,
                defaults=result_defaults,
            )
            if not created:
                logger.info(f'Сотрудник уже является участником мероприятия: {result}')

        # Назначаем оставшихся пользователей группе.
        participants_group.user_set.set(final_users)
        logger.info(f'Группа участников мероприятия: {participants_group.user_set.all()}')

    # Логирование исключений, если они возникнут.
    except Exception as e:
        logger.error(f"Ошибка при обработке сигнала update_events_participants для ParticipantsGenerator: {e}",
                     exc_info=True)
        # Повторный вызов исключения в режиме отладки.
        if settings.DEBUG:
            raise
        else:
            return HttpResponseServerError("Ошибка сервера, обратитесь к администратору")

# Добавление участника в группу при саморегистрации.
@receiver(post_save, sender=Result)
def add_selfregistered_to_group(sender, instance, created, **kwargs):

    # Проверяем ошибки.
    try:

        # Если результат создан и это саморегистрация.
        if created and instance.self_appointment == True and instance.type == 'event':

            # Забираем участника и добавляем в группу.
            participant = instance.employee
            participants_group = instance.event.participants_group
            participants_group.user_set.add(participant)
            participants_group.save()
            logger.info(f'Сотроудник {participant} добавлен в группу {participants_group}')

    # Логирование исключений, если они возникнут.
    except Exception as e:
        logger.error(f"Ошибка при обработке сигнала add_selfregistered_to_group для Result: {e}", exc_info=True)
        # Повторный вызов исключения в режиме отладки.
        if settings.DEBUG:
            raise
        else:
            return HttpResponseServerError("Ошибка сервера, обратитесь к администратору")

# Сигнал удаления группы с участниками мероприятия.
@receiver(post_delete, sender=Event)
def delete_events_groups(sender, instance, **kwargs):

    # Проверка ошибок.
    try:

        # Удаляем связанные группы.
        instance.responsibles_group.delete()
        logger.info(f"Удаляется связанная с мероприятием {instance} группа участников {instance.responsibles_group}.")
        instance.participants_group.delete()
        logger.info(f"Удаляется связанная с мероприятием {instance} группа отвественных {instance.participants_group}.")

    # Логирование исключений, если они возникнут.
    except Exception as e:
        logger.error(f"Ошибка при обработке сигнала delete_events_groups для Event: {e}", exc_info=True)
        # Повторный вызов исключения в режиме отладки.
        if settings.DEBUG:
            raise
        else:
            return HttpResponseServerError("Ошибка сервера, обратитесь к администратору")
