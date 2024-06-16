# Все для сигналов.
from datetime import timedelta
from django.http import HttpResponseServerError
from guardian.core import ObjectPermissionChecker
from guardian.shortcuts import assign_perm
from django.db import transaction
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Assignment, Result, LearningTask, LearningPath
from core.models import Employee, EmployeesGroup, EmployeesGroupObjectPermission
from leaders.models import Transaction
from django.conf import settings
from django.utils import timezone


# Импортируем логи.
import logging
# Создаем логгер с именем 'project'.
logger = logging.getLogger('project')


@transaction.atomic
@receiver(post_save, sender=Assignment)
def create_learning_results(sender, instance, created, **kwargs):

    # Создание результатов комплексной программы.
    def create_learning_complex_results(assignment, employee, learning_complex, learning_paths, planned_start_date, reassignment):
        logger.info(f"Назначение комплексной программы {learning_complex} для {employee}.")

        # Проверка на переназначение.
        if reassignment == 'not_passed' and Result.objects.filter(
            employee=employee,
            learning_complex=learning_complex,
            type='learning_complex',
            status='completed'
        ).exists():
            logger.info(f"Пропускаем для {employee}: уже сдан")
            return

        # Создание объекта результата для учебного пути.
        learning_complex_result = Result.objects.create(
            learning_complex=learning_complex,
            employee=employee,
            assignment=assignment,
            type='learning_complex',
        )
        logger.info(f"Создан {learning_complex_result}")

        # Переменная для определения даты конца.
        _planned_start_date = planned_start_date
        logger.info(f"Дата начала назначений {_planned_start_date}")

        # Создание результатов учебных траекторий.
        for learning_path in learning_paths:

            # Переменные.
            duration = learning_path.duration
            planned_end_date = _planned_start_date + timedelta(days=duration)
            _planned_start_date = _planned_start_date + timedelta(days=duration)
            logger.info(f"Назначение учебной траектории {learning_path} для {employee}.")

            # Проверка на переназначение.
            if reassignment == 'not_passed' and Result.objects.filter(
                employee=employee,
                learning_path=learning_path,
                type='learning_path',
                status='completed'
            ).exists():
                logger.info(f"Пропускаем для {employee}: уже сдан")
                continue

            # Создание объекта результата для учебной траектории.
            learning_path_result = Result.objects.create(
                learning_complex=learning_complex,
                learning_complex_result=learning_complex_result,
                learning_path=learning_path,
                employee=employee,
                assignment=assignment,
                type='learning_path',
                planned_end_date=planned_end_date,
            )
            logger.info(f"Создан: {learning_path_result}")

            # Перебор задач учебного пути.
            for learning_task in learning_path.learning_tasks.all():
                logger.info(f"Назначение учебной задачи {learning_task} для {employee}.")

                if learning_task.type == 'material':

                    # Забираем материал.
                    material = learning_task.material

                    # Проверка на переназначение.
                    if reassignment == 'not_passed' and Result.objects.filter(
                            employee=employee,
                            material=material,
                            status='completed'
                    ).exists():
                        logger.info(f"Пропускаем для {employee}: уже сдан")
                        if learning_task.control_task == True:
                            learning_path_result.completed_control_tasks +=1
                            learning_path_result.save()
                            logger.info(f"Перезачтено задач: {learning_path_result.completed_control_tasks}")
                        continue

                    # Создание объекта результата для задачи.
                    learning_task_result = Result.objects.create(
                        learning_path=learning_path,
                        learning_path_result=learning_path_result,
                        employee=employee,
                        material=material,
                        learning_task=learning_task,
                        assignment=assignment,
                        type='material'
                    )
                    logger.info(f"Создан {learning_task_result}")

                if learning_task.type == 'test':

                    # Забираем тест.
                    test = learning_task.test

                    # Проверка на переназначение.
                    if reassignment == 'not_passed' and Result.objects.filter(
                            employee=employee,
                            test=test,
                            status='completed'
                    ).exists():
                        logger.info(f"Пропускаем для {employee}: уже сдан.")
                        if learning_task.control_task == True:
                            learning_path_result.completed_control_tasks +=1
                            learning_path_result.save()
                            logger.info(f"Перезачтено задач: {learning_path_result.completed_control_tasks}")
                        continue

                    # Создание объекта результата для задачи.
                    learning_task_result = Result.objects.create(
                        learning_path=learning_path,
                        learning_path_result=learning_path_result,
                        employee=employee,
                        test=test,
                        learning_task=learning_task,
                        assignment=assignment,
                        type='test'
                    )
                    logger.info(f"Создан {learning_task_result}")

                if learning_task.type == 'course':

                    # Забираем курс.
                    course = learning_task.course

                    # Проверка на переназначение.
                    if reassignment == 'not_passed' and Result.objects.filter(
                            employee=employee,
                            course=course,
                            status='completed'
                    ).exists():
                        logger.info(f"Пропускаем для {employee}: уже сдан")
                        if learning_task.control_task == True:
                            learning_path_result.completed_control_tasks +=1
                            learning_path_result.save()
                            logger.info(f"Перезачтено задач: {learning_path_result.completed_control_tasks}")
                        continue

                    # Создание объекта результата для задачи.
                    learning_task_result = Result.objects.create(
                        learning_path=learning_path,
                        learning_path_result=learning_path_result,
                        employee=employee,
                        course=course,
                        scorm_package=course.scorm_package,
                        learning_task=learning_task,
                        assignment=assignment,
                        type='course'
                    )
                    logger.info(f"Создан {learning_task_result}")

    # Создание результатов учебной траектории.
    def create_learning_path_results(assignment, employee, learning_path, planned_start_date, reassignment):

        # Переменные.
        duration = learning_path.duration
        planned_end_date = planned_start_date + timedelta(days=duration)
        logger.info(f"Назначение учебной траектории {learning_path} для {employee}.")

        # Проверка на переназначение.
        if reassignment == 'not_passed' and Result.objects.filter(
            employee=employee,
            learning_path=learning_path,
            type='learning_path',
            status='completed'
        ).exists():
            logger.info(f"Пропускаем для {employee}: уже сдан")
            return

        # Создание объекта результата для учебной траектории.
        learning_path_result = Result.objects.create(
            learning_path=learning_path,
            employee=employee,
            assignment=assignment,
            type='learning_path',
            planned_end_date=planned_end_date,
        )
        logger.info(f"Создан {learning_path_result}")

        # Перебор задач учебного пути.
        for learning_task in learning_path.learning_tasks.all():
            logger.info(f"Назначение учебной задачи {learning_task} для {employee}.")

            if learning_task.type == 'material':

                # Забираем материал.
                material = learning_task.material

                # Проверка на переназначение.
                if reassignment == 'not_passed' and Result.objects.filter(
                        employee=employee,
                        material=material,
                        status='completed'
                ).exists():
                    logger.info(f"Пропускаем для {employee}: уже сдан")
                    if learning_task.control_task == True:
                        learning_path_result.completed_control_tasks += 1
                        learning_path_result.save()
                        logger.info(f"Перезачтено задач: {learning_path_result.completed_control_tasks}")
                    continue

                # Создание объекта результата для задачи.
                learning_task_result = Result.objects.create(
                    learning_path=learning_path,
                    learning_path_result=learning_path_result,
                    employee=employee,
                    material=material,
                    learning_task=learning_task,
                    assignment=assignment,
                    type='material'
                )
                logger.info(f"Создан {learning_task_result}")

            if learning_task.type == 'test':

                # Забираем тест.
                test = learning_task.test

                # Проверка на переназначение.
                if reassignment == 'not_passed' and Result.objects.filter(
                        employee=employee,
                        test=test,
                        status='completed'
                ).exists():
                    logger.info(f"Пропускаем для {employee}: уже сдан.")
                    if learning_task.control_task == True:
                        learning_path_result.completed_control_tasks += 1
                        learning_path_result.save()
                        logger.info(f"Перезачтено задач: {learning_path_result.completed_control_tasks}")
                    continue

                # Создание объекта результата для задачи.
                learning_task_result = Result.objects.create(
                    learning_path=learning_path,
                    learning_path_result=learning_path_result,
                    employee=employee,
                    test=test,
                    learning_task=learning_task,
                    assignment=assignment,
                    type='test'
                )
                logger.info(f"Создан {learning_task_result}")

            if learning_task.type == 'course':

                # Забираем курс.
                course = learning_task.course

                # Проверка на переназначение.
                if reassignment == 'not_passed' and Result.objects.filter(
                        employee=employee,
                        course=course,
                        status='completed'
                ).exists():
                    logger.info(f"Пропускаем для {employee}: уже сдан")
                    if learning_task.control_task == True:
                        learning_path_result.completed_control_tasks += 1
                        learning_path_result.save()
                        logger.info(f"Перезачтено задач: {learning_path_result.completed_control_tasks}")
                    continue

                # Создание объекта результата для задачи.
                learning_task_result = Result.objects.create(
                    learning_path=learning_path,
                    learning_path_result=learning_path_result,
                    employee=employee,
                    course=course,
                    scorm_package=course.scorm_package,
                    learning_task=learning_task,
                    assignment=assignment,
                    type='course'
                )
                logger.info(f"Создан {learning_task_result}")

    # Создание прав доступа.
    def create_perms(learning_paths, participants_group):

        # Создание результатов учебных задач.
        for learning_path in learning_paths:

            # Присвоение прав доступа к LearningPath для группы.
            assign_perm('view_learningpath', participants_group, learning_path)
            logger.info(f"Право на просмотр учебной траектории {learning_path} назначено группе {participants_group}.")

            # Перебор задач учебного пути.
            for learning_task in learning_path.learning_tasks.all():

                # Пррисвоение прав доступа.
                assign_perm('view_learningtask', participants_group, learning_task)
                logger.info(f"Право на просмотр учебной задачи {learning_task} назначено группе {participants_group}.")

                if learning_task.type == 'material':

                    # Забираем материал.
                    material=learning_task.material

                    # Присвоение прав доступа к тесту для группы.
                    assign_perm('view_material', participants_group, material)
                    logger.info(f"Право на просмотр материала {material} назначено группе {participants_group}.")

                if learning_task.type == 'test':

                    # Забираем тест.
                    test = learning_task.test

                    # Присвоение прав доступа к Material для группы.
                    assign_perm('view_test', participants_group, test)
                    logger.info(f"Право на просмотр теста {test} назначено группе {participants_group}.")

                if learning_task.type == 'course':

                    # Забираем курс.
                    course = learning_task.course

                    # Присвоение прав доступа к тесту для группы.
                    assign_perm('view_course', participants_group, course)
                    logger.info(f"Право на просмотр курса {course} назначено группе {participants_group}.")

                # Добавьте обработку других объектов.

        logger.info("Массовое создание прав завершено.")


    # Перехват ошибок.
    try:

        # Если объект создается.
        if created:
            logger.info(f"Обработка создания Assignment: {instance}")

            # Получение переменных.
            assignment = instance
            group = instance.group
            reassignment = instance.reassignment
            employees = Employee.objects.filter(groups=group, is_active=True).prefetch_related(
                'results',
            )
            planned_start_date = instance.planned_start_date

            # Общие переменные.
            if instance.type == 'learning_complex':
                learning_complex = instance.learning_complex
                learning_paths = [
                    learning_complex_path.learning_path for learning_complex_path in
                    learning_complex.learning_complex_paths.all().order_by('learning_complex', 'position')
                ]
                participants_group_name = f"Назначение комплексной программы [{instance.pk}]: {instance.learning_complex.name} для {group} с {planned_start_date.strftime('%d.%m.%Y')}"
            if instance.type == 'learning_path':
                learning_path = instance.learning_path
                learning_paths=[learning_path]
                participants_group_name = f"Назначение траектории обучения [{instance.pk}]: {instance.learning_path.name} для {group} с {planned_start_date.strftime('%d.%m.%Y')}"

            # Забираем группу для отвественных и участников мероприятия.
            participants_group, _ = EmployeesGroup.objects.get_or_create(name=participants_group_name, type='assignment')
            instance.participants_group = participants_group
            instance.save()
            participants_group.user_set.set(employees)
            logger.info(f"Была создана группа для назначения: {participants_group}.")

            # Создание результатов.
            if instance.type == 'learning_complex':

                # Нарезка.
                chunk_size = 50
                employees_chunks = [employees[i:i + chunk_size] for i in range(0, len(employees), chunk_size)]

                # Перебор сотрудников и создание результатов.
                for employees_chunk in employees_chunks:
                    for employee in employees_chunk:

                        # Действия.
                        learning_path_results = create_learning_complex_results(
                            assignment=assignment,
                            employee=employee,
                            learning_complex=learning_complex,
                            learning_paths=learning_paths,
                            planned_start_date=planned_start_date,
                            reassignment=reassignment
                        )
                    logger.info("Массовое создание результатов завершено.")

            # Создание результатов.
            if instance.type == 'learning_path':

                # Нарезка.
                chunk_size = 50
                employees_chunks = [employees[i:i + chunk_size] for i in range(0, len(employees), chunk_size)]

                # Перебор сотрудников и создание результатов.
                for employees_chunk in employees_chunks:
                    for employee in employees_chunk:

                        # Действия.
                        learning_path_result = create_learning_path_results(
                            assignment=assignment,
                            employee=employee,
                            learning_path=learning_path,
                            planned_start_date=planned_start_date,
                            reassignment=reassignment
                        )
                    logger.info("Массовое создание результатов завершено.")

            # Создание прав.
            create_perms(learning_paths, participants_group)

    # Логирование исключений, если они возникнут.
    except Exception as e:
        logger.error(f"Ошибка при обработке сигнала create_learning_results для Assignment: {e}", exc_info=True)
        # Повторный вызов исключения в режиме отладки.
        if settings.DEBUG:
            raise
        else:
            return HttpResponseServerError("Ошибка сервера, обратитесь к администратору")

# Сигнал сохранения участников меропрриятия.
@receiver(post_delete, sender=Assignment)
def delete_assignment_groups(sender, instance, **kwargs):

    # Проверка ошибок.
    try:

        # Удаляем связанные группы.
        instance.participants_group.delete()
        logger.info(f"Удаляется связанная с обучением {instance} группа {instance.participants_group}.")

    # Логирование исключений, если они возникнут.
    except Exception as e:
        logger.error(f"Ошибка при обработке сигнала delete_assignment_groups для Assignment: {e}", exc_info=True)
        # Повторный вызов исключения в режиме отладки.
        if settings.DEBUG:
            raise
        else:
            return HttpResponseServerError("Ошибка сервера, обратитесь к администратору")

# Выполнение траектории и программы.
@receiver(post_save, sender=Result)
def update_learning_path_result_status(sender, instance, **kwargs):

    # Проверка ошибок.
    try:

        # Если это задача.
        if instance.learning_task:

            # Если траектория в процессе - проставляем в программе.
            if instance.status != 'appointed':

                # Получаем переменные.
                learning_path_result = instance.learning_path_result

                # Если задача в процессе - проставляем в траектории.
                if instance.status == 'in_progress' and learning_path_result.status == 'appointed':
                    # Обновляем статус результата для LearningPath на 'выполнено'.
                    learning_path_result.status = 'in_progress'
                    learning_path_result.start_date = timezone.now()
                    learning_path_result.save()

                # Получаем переменные.
                learning_task = instance.learning_task

                # Если задача контрольная.
                if learning_task.control_task == True:

                    # Получаем переменные.
                    learning_path = instance.learning_path
                    if settings.DEBUG:
                        logger.info(f'Взяли траекторию: {learning_path}')

                    # Если выполнена и балов нет - проставляем.
                    if instance.status == 'completed' and instance.control_score == 0:
                        instance.control_score +=1
                        learning_path_result.completed_control_tasks +=1
                        if settings.DEBUG:
                            logger.info(f'Пройдено задач: {learning_path_result.completed_control_tasks} из {learning_path.number_control_tasks}')

                        # Если достаточно - выполняем.
                        if learning_path_result.completed_control_tasks == learning_path.number_control_tasks:
                            if settings.DEBUG:
                                logger.info(f'Обучение пройдено: {learning_path_result}')
                            learning_path_result.status = 'completed'
                            learning_path_result.end_date = timezone.now()

                        # Сохраняем изменения.
                        learning_path_result.save()
                        instance.save()

                    # Если выполнена - проставляем.
                    if instance.status == 'failed':

                        # Если был балл - забираем.
                        if instance.control_score != 0:
                            instance.control_score = 0
                            instance.save()

                        # Вычисляем число для провала и проваленные задачи.
                        control_tasks_all = LearningTask.objects.filter(learning_path=learning_path, control_task=True).count()
                        failure_number = (control_tasks_all - learning_path.number_control_tasks) + 1
                        failed_tasks_results = instance.learning_path_result.path_results.filter(status='failed').count()
                        if settings.DEBUG:
                            logger.info(f'Провалено задач: {failed_tasks_results} из {failure_number}')

                        # Если достаточно - проваливаем.
                        if failed_tasks_results >= failure_number:
                            if settings.DEBUG:
                                logger.info(f'Обучение провалено: {learning_path_result}')
                            learning_path_result.status = 'failed'
                            learning_path_result.end_date = timezone.now()

                        # Сохраняем изменения.
                        learning_path_result.save()

                    if settings.DEBUG:
                        logger.info(f'Холостой проход сигнала')

        # Если это траектория программы.
        if instance.type == 'learning_path' and instance.learning_complex_result:

            # Если траектория в процессе - проставляем в программе.
            if instance.status != 'appointed':

                # Получаем результат траектории.
                learning_complex_result = instance.learning_complex_result

                # Если траектория в процессе - проставляем в программе.
                if instance.status == 'in_progress' and learning_complex_result.status == 'appointed':
                    learning_complex_result.status = 'in_progress'
                    learning_complex_result.start_date = timezone.now()
                    learning_complex_result.save()

                # Получаем все связанные траектории.
                path_results = Result.objects.filter(learning_complex_result=learning_complex_result)

                # Если все выполнены - проставлем в программе.
                if all(path_result.status == 'completed' for path_result in path_results if path_result):
                    learning_complex_result.status = 'completed'
                    learning_complex_result.end_date = timezone.now()
                    learning_complex_result.save()

                # Если все провалены - проставлем в программе.
                if any(path_result.status == 'failed' for path_result in path_results if path_result):
                    learning_complex_result.status = 'failed'
                    learning_complex_result.end_date = timezone.now()
                    learning_complex_result.save()

    # Логирование исключений, если они возникнут.
    except Exception as e:
        logger.error(f"Ошибка при обработке сигнала update_learning_path_result_status для Result: {e}", exc_info=True)
        # Повторный вызов исключения в режиме отладки.
        if settings.DEBUG:
            raise
        else:
            return HttpResponseServerError("Ошибка сервера, обратитесь к администратору")

# Создание и обновление транзакций.
@receiver(post_save, sender=Result)
def create_results_transaction(sender, instance, created, **kwargs):

    # Проверка ошибок.
    try:

        # Если результат обновляется.
        if not created:

            # Если обучение пройдено.
            if instance.status == 'completed':

                # Если это материал.
                if instance.type == 'material':

                    # Создаем или обновляем транзакцию.
                    transaction, created = Transaction.objects.get_or_create(
                        type = 'material',
                        employee = instance.employee,
                        material = instance.material,
                        bonus = instance.material.bonus,
                    )
                    transaction.result=instance
                    transaction.save()

                    # Логи.
                    if created:
                        logger.info(f"Создана транзакция {transaction}")
                    else:
                        logger.info(f"Транзакция существует {transaction}")

                # Если это курс.
                if instance.type == 'course':

                    # Вычисляем бонус.
                    courses_bonus = instance.course.bonus
                    score_scaled = instance.score_scaled
                    bonus = (courses_bonus * score_scaled) / 100

                    # Создаем транзакцию.
                    transaction, created = Transaction.objects.get_or_create(
                        type='course',
                        employee=instance.employee,
                        course=instance.course,
                        bonus=bonus,
                    )
                    transaction.result=instance
                    transaction.save()

                    # Логи.
                    if created:
                        logger.info(f"Создана транзакция {transaction}")
                    else:
                        logger.info(f"Обновлена транзакция {transaction}")

                # Если это тест.
                if instance.type == 'test':

                    # Вычисляем бонус.
                    tests_bonus = instance.test.bonus
                    score_scaled = instance.score_scaled
                    bonus = (tests_bonus * score_scaled) / 100

                    # Создаем транзакцию.
                    transaction, created = Transaction.objects.get_or_create(
                        type='test',
                        employee=instance.employee,
                        test=instance.test,
                        bonus=bonus,
                    )
                    transaction.result=instance
                    transaction.save()

                    # Логи.
                    if created:
                        logger.info(f"Создана транзакция {transaction}")
                    else:
                        logger.info(f"Обновлена транзакция {transaction}")

            # Если мероприятие пройдено.
            if instance.presence_mark == 'present':

                # Создаем или обновляем транзакцию.
                transaction, created = Transaction.objects.get_or_create(
                    type='event',
                    employee=instance.employee,
                    event=instance.event,
                    bonus=instance.event.bonus,
                )
                transaction.result = instance
                transaction.save()

                # Логи.
                if created:
                    logger.info(f"Создана транзакция {transaction}")
                else:
                    logger.info(f"Транзакция существует {transaction}")

    # Логирование исключений, если они возникнут.
    except Exception as e:
        logger.error(f"Ошибка при обработке сигнала create_results_transaction для Result: {e}", exc_info=True)
        # Повторный вызов исключения в режиме отладки.
        if settings.DEBUG:
            raise
        else:
            return HttpResponseServerError("Ошибка сервера, обратитесь к администратору")
