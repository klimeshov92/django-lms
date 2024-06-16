# Импортируем настройки.
from django.conf import settings
# Импортируем модуль models.
from django.db import models
# Импортируем post_save из модуля signals. post_save - сигнал, который отправляется после сохранения объекта модели.
from django.db.models.signals import post_save, post_delete
# Импортируем receiver из модуля dispatch. receiver - функция-декоратор для подключения функций обработки сигналов.
from django.dispatch import receiver
# Импортируем ответ с ошибкой сервера.
from django.http import HttpResponseServerError
# Импортируем пользовательские модели из текущего приложения.
# Эти модели используются для создания связанных объектов в базе данных.
from .models import EmployeeExcelImport, Organization, Subdivision, Position, Employee, Placement, EmployeesGroup, GroupsGenerator, EmployeesGroupObjectPermission
# Импортируем функцию make_password из модуля auth.hashers. Используется для хеширования паролей.
from django.contrib.auth.hashers import make_password
# Импортируем функцию get_random_string из модуля utils.crypto.
from django.utils.crypto import get_random_string

# Импортируем логи.
import logging
# Создаем логгер с именем 'project'.
logger = logging.getLogger('project')

# Обработчик сигнала post_save для модели Organization.
@receiver(post_save, sender=Organization)
def organizations_post_save(sender, instance, created, **kwargs):

    try:
        # Устанавливаем имя группы для организации.
        group_name = f"Организация: [{instance.id}] {instance.legal_name}"

        # Если организация только что создана.
        if created:
            group, _ = EmployeesGroup.objects.get_or_create(name=group_name, type='organization')
            instance.group = group  # Связываем созданную группу с организацией.
            instance.save()  # Сохраняем изменения в организации.
            logger.info(f"Для организации {instance.legal_name} создана группа: {instance.group}")
        # Если имя группы изменилось после обновления организации.
        elif instance.group.name != group_name:
            instance.group.name = group_name
            instance.group.save()  # Сохраняем изменения в группе.
            logger.info(f"Для организации {instance.legal_name} обновлена группа: {instance.group}")

    # Логирование исключений, если они возникнут.
    except Exception as e:
        logger.error(f"Ошибка при обработке сигнала post_save для Organization: {e}", exc_info=True)
        # Повторный вызов исключения в режиме отладки.
        if settings.DEBUG:
            raise
        else:
            return HttpResponseServerError("Ошибка сервера, обратитесь к администратору")

# Сигнал удаления группы с сотрудниками организации.
@receiver(post_delete, sender=Organization)
def delete_organizations_groups(sender, instance, **kwargs):

    # Проверка ошибок.
    try:

        # Удаляем связанные группы.
        instance.group.delete()
        logger.info(f"Удаляется связанная с организацией {instance} группа сотрудников {instance.group}.")

    # Логирование исключений, если они возникнут.
    except Exception as e:
        logger.error(f"Ошибка при обработке сигнала delete_organizations_groups для Organization: {e}", exc_info=True)
        # Повторный вызов исключения в режиме отладки.
        if settings.DEBUG:
            raise
        else:
            return HttpResponseServerError("Ошибка сервера, обратитесь к администратору")

# Обработчик сигнала post_save для модели Subdivision.
@receiver(post_save, sender=Subdivision)
def subdivisions_post_save(sender, instance, created, **kwargs):

    try:
        # Устанавливаем имя группы для подразделения.
        group_name = f"Подразделение: [{instance.id}] {instance.name}"

        # Если подразделение только что создано.
        if created:
            group, _ = EmployeesGroup.objects.get_or_create(name=group_name, type='subdivision')
            instance.group = group  # Связываем созданную группу с подразделением.
            instance.save()  # Сохраняем изменения в подразделении.
            logger.info(f"Для подразделения {instance.name} создана группа: {instance.group}")
        # Если имя группы изменилось после обновления подразделения.
        elif instance.group.name != group_name:
            instance.group.name = group_name
            instance.group.save()  # Сохраняем изменения в группе.
            logger.info(f"Для подразделения {instance.name} обновлена группа: {instance.group}")

    # Логирование исключений, если они возникнут.
    except Exception as e:
        logger.error(f"Ошибка при обработке сигнала post_save для Subdivision: {e}", exc_info=True)
        # Повторный вызов исключения в режиме отладки.
        if settings.DEBUG:
            raise
        else:
            return HttpResponseServerError("Ошибка сервера, обратитесь к администратору")

# Сигнал удаления группы с сотрудниками подразделения.
@receiver(post_delete, sender=Subdivision)
def delete_subdivisions_groups(sender, instance, **kwargs):

    # Проверка ошибок.
    try:

        # Удаляем связанные группы.
        instance.group.delete()
        logger.info(f"Удаляется связанная с подразделением {instance} группа сотрудников {instance.group}.")

    # Логирование исключений, если они возникнут.
    except Exception as e:
        logger.error(f"Ошибка при обработке сигнала delete_subdivisions_groups для Subdivision: {e}", exc_info=True)
        # Повторный вызов исключения в режиме отладки.
        if settings.DEBUG:
            raise
        else:
            return HttpResponseServerError("Ошибка сервера, обратитесь к администратору")

# Обработчик сигнала post_save для модели Position.
@receiver(post_save, sender=Position)
def positions_post_save(sender, instance, created, **kwargs):

    try:
        # Устанавливаем имя группы для должности.
        group_name = f"Должность: [{instance.id}] {instance.name}"

        # Если должность только что создана.
        if created:
            group, _ = EmployeesGroup.objects.get_or_create(name=group_name, type='position')
            instance.group = group  # Связываем созданную группу с должностью.
            instance.save()  # Сохраняем изменения в должности.
            logger.info(f"Для должности {instance.name} создана группа: {instance.group}")
        # Если имя группы изменилось после обновления должности.
        elif instance.group.name != group_name:
            instance.group.name = group_name
            instance.group.save()  # Сохраняем изменения в группе.
            logger.info(f"Для должности {instance.name} обновлена группа: {instance.group}")

    # Логирование исключений, если они возникнут.
    except Exception as e:
        logger.error(f"Ошибка при обработке сигнала post_save для Position: {e}", exc_info=True)
        # Повторный вызов исключения в режиме отладки.
        if settings.DEBUG:
            raise
        else:
            return HttpResponseServerError("Ошибка сервера, обратитесь к администратору")

# Сигнал удаления группы с сотрудниками подразделения.
@receiver(post_delete, sender=Position)
def delete_position_groups(sender, instance, **kwargs):

    # Проверка ошибок.
    try:

        # Удаляем связанные группы.
        instance.group.delete()
        logger.info(f"Удаляется связанная с должностью {instance} группа сотрудников {instance.group}.")

    # Логирование исключений, если они возникнут.
    except Exception as e:
        logger.error(f"Ошибка при обработке сигнала delete_position_groups для Position: {e}", exc_info=True)
        # Повторный вызов исключения в режиме отладки.
        if settings.DEBUG:
            raise
        else:
            return HttpResponseServerError("Ошибка сервера, обратитесь к администратору")

# Сигнал post_save для модели Employee
@receiver(post_save, sender=Employee)
def employees_post_save(sender, instance, created, **kwargs):

    try:

        # Пропускаем логику сигнала для суперпользователей.
        if instance.is_superuser:
            return

        # Действия для только что созданных сотрудников.
        if created:
            # Установка случайного пароля для новых сотрудников.
            random_password = get_random_string(length=8)
            instance.set_password(random_password)
            instance.save()

    # Логирование исключений, если они возникнут.
    except Exception as e:
        logger.error(f"Ошибка при обработке сигнала post_save для Employee: {e}", exc_info=True)
        # Повторный вызов исключения в режиме отладки.
        if settings.DEBUG:
            raise
        else:
            return HttpResponseServerError("Ошибка сервера, обратитесь к администратору")

# Сигнал удаления группы с сотрудниками импорта.
@receiver(post_delete, sender=EmployeeExcelImport)
def delete_employee_excel_import_groups(sender, instance, **kwargs):

    # Проверка ошибок.
    try:

        # Удаляем связанные группы.
        instance.group.delete()
        logger.info(f"Удаляется связанная с импортом из Excel-файла {instance} группа сотрудников {instance.group}.")

    # Логирование исключений, если они возникнут.
    except Exception as e:
        logger.error(f"Ошибка при обработке сигнала delete_employee_excel_import_groups для EmployeeExcelImport: {e}", exc_info=True)
        # Повторный вызов исключения в режиме отладки.
        if settings.DEBUG:
            raise
        else:
            return HttpResponseServerError("Ошибка сервера, обратитесь к администратору")

# Сигнал, вызываемый после сохранения объекта Placement.
@receiver(post_save, sender=Placement)
def placements_post_save(sender, instance, created, **kwargs):

    try:
        # Добавление в группы при создании назначения.
        if created:
            instance.position.subdivision.organization.group.user_set.add(instance.employee)
            instance.position.subdivision.group.user_set.add(instance.employee)
            instance.position.group.user_set.add(instance.employee)

            # Создание или получение группы 'manager' и добавление в неё, если пользователь - менеджер.
            if instance.manager:
                manager_group, _ = EmployeesGroup.objects.get_or_create(name='Managers', type='system')
                manager_group.user_set.add(instance.employee)
            else:
                # Создание или получение группы 'employee' и добавление в неё, если пользователь - не менеджер.
                employee_group, _ = EmployeesGroup.objects.get_or_create(name='Employees', type='system')
                employee_group.user_set.add(instance.employee)

        # Обработка изменения или окончания назначения.
        else:
            # Получение всех активных назначений пользователя.
            active_placements = Placement.objects.filter(
                employee=instance.employee,
                end_date__isnull=True
            ).exclude(id=instance.id)

            # Перебор групп связанных с подразделением, должностью и организацией связанных с instance.
            for group in [instance.position.group, instance.position.subdivision.group, instance.position.subdivision.organization.group]:

                # Проверка, существует ли группа и состоит ли в ней пользователь.
                if group and group.user_set.filter(pk=instance.employee.pk).exists():

                    # Далее нужно проверить, есть ли другие активные назначения у сотрудника в этой группе.
                    # Нам нужно убедиться, что пользователь удаляется из группы только если у него нет других активных назначений,
                    # которые должны сохранить его в группе.
                    # Следующие проверки удостоверяются, что нет активных назначений для пользователя в данной группе
                    # по подразделению, должности и организации, соответственно.
                    if not active_placements.filter(position__group=group).exists() \
                            and not active_placements.filter(position__subdivision__group=group).exists() \
                            and not active_placements.filter(position__subdivision__organization__group=group).exists():
                        # Если все три проверки показывают, что нет других активных назначений,
                        # удаляем пользователя из этой группы, т.к. он больше не удовлетворяет критериям включения.
                        group.user_set.remove(instance.employee)

            # Удаление из группы 'manager', если пользователь больше не является менеджером в других активных назначениях.
            if not active_placements.filter(manager=True).exists():
                manager_group, _ = EmployeesGroup.objects.get_or_create(name='Managers', type='system')
                manager_group.user_set.remove(instance.employee)

            # Удаление из группы 'employee', если пользователь стал сотрудником в других активных назначениях.
            if active_placements.filter(manager=True).exists():
                employee_group, _ = EmployeesGroup.objects.get_or_create(name='Employees', type='system')
                employee_group.user_set.remove(instance.employee)

    # Логирование исключений, если они возникнут.
    except Exception as e:
        logger.error(f"Ошибка при обработке сигнала post_save для Placement: {e}", exc_info=True)
        # Повторный вызов исключения в режиме отладки.
        if settings.DEBUG:
            raise
        else:
            return HttpResponseServerError("Ошибка сервера, обратитесь к администратору")

# Сигнал сохранения участников меропрриятия.
@receiver(post_delete, sender=Placement)
def placement_post_delete(sender, instance, **kwargs):

    # Проверка ошибок.
    try:

        # Получение всех активных назначений пользователя.
        active_placements = Placement.objects.filter(
            employee=instance.employee,
            end_date__isnull=True
        ).exclude(id=instance.id)

        # Перебор групп связанных с подразделением, должностью и организацией связанных с instance.
        for group in [instance.position.group, instance.position.subdivision.group, instance.position.subdivision.organization.group]:

            # Проверка, существует ли группа и состоит ли в ней пользователь.
            if group and group.user_set.filter(pk=instance.employee.pk).exists():

                # Далее нужно проверить, есть ли другие активные назначения у сотрудника в этой группе.
                # Нам нужно убедиться, что пользователь удаляется из группы только если у него нет других активных назначений,
                # которые должны сохранить его в группе.
                # Следующие проверки удостоверяются, что нет активных назначений для пользователя в данной группе
                # по подразделению, должности и организации, соответственно.
                if not active_placements.filter(position__group=group).exists() \
                        and not active_placements.filter(position__subdivision__group=group).exists() \
                        and not active_placements.filter(position__subdivision__organization__group=group).exists():
                    # Если все три проверки показывают, что нет других активных назначений,
                    # удаляем пользователя из этой группы, т.к. он больше не удовлетворяет критериям включения.
                    group.user_set.remove(instance.employee)

        # Удаление из группы 'manager', если пользователь больше не является менеджером в других активных назначениях.
        if not active_placements.filter(manager=True).exists():
            manager_group, _ = EmployeesGroup.objects.get_or_create(name='Managers', type='system')
            manager_group.user_set.remove(instance.employee)

        # Удаление из группы 'employee', если пользователь стал сотрудником в других активных назначениях.
        if active_placements.filter(manager=True).exists():
            employee_group, _ = EmployeesGroup.objects.get_or_create(name='Employees', type='system')
            employee_group.user_set.remove(instance.employee)

    # Логирование исключений, если они возникнут.
    except Exception as e:
        logger.error(f"Ошибка при обработке сигнала placement_post_delete для Placement: {e}", exc_info=True)
        # Повторный вызов исключения в режиме отладки.
        if settings.DEBUG:
            raise
        else:
            return HttpResponseServerError("Ошибка сервера, обратитесь к администратору")

# Сигнал генерации состава группы.
@receiver(post_save, sender=GroupsGenerator)
def update_groups_users(sender, instance, **kwargs):

    try:

        # Забирае переменные.
        group = instance.group
        added_groups = instance.added_groups.all()
        added_users = instance.added_users.all()
        excluded_groups = instance.excluded_groups.all()
        excluded_users = instance.excluded_users.all()

        # Выводим информацию о связях многие-ко-многим
        if settings.DEBUG:
            logger.info(f"Добавленные группы: {added_groups}")
            logger.info(f"Добавленные пользователи: {added_users}")
            logger.info(f"Исключенные группы: {excluded_groups}")
            logger.info(f"Исключенные пользователи: {excluded_users}")

        # Получаем добавляемых пользователей.
        all_added_users = Employee.objects.filter(groups__in=added_groups, is_active=True).distinct() | added_users.distinct()
        if settings.DEBUG:
            logger.info(f"Все добавляемые пользователи: {all_added_users}")

        # Получаем добавляемых пользователей.
        all_excluded_users = Employee.objects.filter(groups__in=excluded_groups, is_active=True).distinct() | excluded_users.distinct()
        if settings.DEBUG:
            logger.info(f"Все исключаемые пользователи: {all_excluded_users}")

        # Итог
        final_users = all_added_users.exclude(id__in=all_excluded_users.values_list('id', flat=True))
        if settings.DEBUG:
            logger.info(f"Все пользователи: {final_users}")

        # Фильтруем по датам.
        if instance.start_date_lte:
            final_users = final_users.filter(placements__start_date__lte=instance.start_date_lte)
            logger.info(f"Пользователи с датой приема до {instance.start_date_lte}: {final_users}")
        if instance.start_date_gte:
            final_users = final_users.filter(placements__start_date__gte=instance.start_date_gte)
            logger.info(f"Пользователи с датой приема после {instance.start_date_gte}: {final_users}")

        # Назначаем оставшихся пользователей группе.
        group.user_set.set(final_users)

    # Логирование исключений, если они возникнут.
    except Exception as e:
        logger.error(f"Ошибка при обработке сигнала update_groups_users для GroupsGenerator: {e}", exc_info=True)
        # Повторный вызов исключения в режиме отладки.
        if settings.DEBUG:
            raise
        else:
            return HttpResponseServerError("Ошибка сервера, обратитесь к администратору")

# Удаляем все объектные права, связанные с удаленной группой
@receiver(post_delete, sender=EmployeesGroup)
def delete_group_object_permissions(sender, instance, **kwargs):

    if EmployeesGroupObjectPermission.objects.filter(group=instance).exists():
        perms = EmployeesGroupObjectPermission.objects.filter(group=instance).all()
        perms.delete()
    logger.info('Удалены все объектные права, связанные с удаленной группой')
