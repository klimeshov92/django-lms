# Все для сигналов.
from datetime import timedelta
from django.http import HttpResponseServerError
from guardian.core import ObjectPermissionChecker
from guardian.shortcuts import assign_perm, remove_perm
from django.db import transaction
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Assignment, Result, LearningTask, LearningPath, ResultSupervising
from core.models import Employee, EmployeesGroup, EmployeesGroupObjectPermission, Placement
from leaders.models import Transaction
from django.conf import settings
from django.utils import timezone


# Импортируем логи.
import logging
# Создаем логгер с именем 'project'.
logger = logging.getLogger('project')

# Результаты обучения
@transaction.atomic
@receiver(post_save, sender=Assignment)
def create_learning_results(sender, instance, created, **kwargs):

    # Функция для получения супервизоров
    def get_supervisors(assignment, employee):
        # Проверка на наличие группы супервизоров.
        if assignment.supervisors_group:
            supervisors_group_users = assignment.supervisors_group.user_set.all()
        else:
            supervisors_group_users = Employee.objects.none()
        logger.info(f"Сотрудники контролирующей группы: {supervisors_group_users}")

        # Если менеджеры являются наблюдателями, добавляем их к супервизорам.
        if assignment.manager_supervising:
            # Находим все подразделения сотрудника.
            employee_placements = employee.placements.all()

            # Ищем менеджеров в этих подразделениях.
            managers = Placement.objects.filter(
                position__subdivision__in=employee_placements.values_list('position__subdivision__id', flat=True),
                manager=True
            ).values_list('employee', flat=True)

            # Добавляем найденных менеджеров к супервизорам.
            supervisors = supervisors_group_users.union(Employee.objects.filter(id__in=managers))
        else:
            supervisors = supervisors_group_users

        logger.info(f"Итоговый список супервизоров: {supervisors}")
        return supervisors

    # Создание результатов комплексной программы.
    def create_learning_complex_results(assignment, employee, learning_complex, learning_paths, planned_start_date, reassignment):
        logger.info(f"Назначение комплексной программы {learning_complex} для {employee}.")

        # Забираем супервизоров
        supervisors = get_supervisors(assignment, employee)

        # Проверка на переназначение.
        if reassignment == 'not_completed' and Result.objects.filter(
            employee=employee,
            learning_complex=learning_complex,
            type='learning_complex',
            status='completed'
        ).exists():
            logger.info(f"Пропускаем для {employee}: уже сдан")
            return
        if reassignment == 'not_appoint' and Result.objects.filter(
            employee=employee,
            learning_complex=learning_complex,
            type='learning_complex'
        ).exists():
            logger.info(f"Пропускаем для {employee}: уже назначен")
            return

        # Создание объекта результата для учебного пути.
        learning_complex_result = Result.objects.create(
            learning_complex=learning_complex,
            employee=employee,
            assignment=assignment,
            type='learning_complex',
        )
        logger.info(f"Создан {learning_complex_result}")

        # Добавление контролеров
        for supervisor in supervisors:
            result_supervising, _ = ResultSupervising.objects.get_or_create(supervisor=supervisor, result=learning_complex_result)
            logger.info(f"Создан контроль результата {result_supervising}")

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
            if reassignment == 'not_completed' and Result.objects.filter(
                employee=employee,
                learning_path=learning_path,
                type='learning_path',
                status='completed'
            ).exists():
                logger.info(f"Пропускаем для {employee}: уже сдан")
                continue
            if reassignment == 'not_appoint' and Result.objects.filter(
                employee=employee,
                learning_path=learning_path,
                type='learning_path'
            ).exists():
                logger.info(f"Пропускаем для {employee}: уже назначен")
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

            # Добавление контролеров
            for supervisor in supervisors:
                result_supervising, _ = ResultSupervising.objects.get_or_create(supervisor=supervisor, result=learning_path_result)
                logger.info(f"Создан контроль результата {result_supervising}")

            # Перебор задач учебного пути.
            for learning_task in learning_path.learning_tasks.all():
                logger.info(f"Назначение учебной задачи {learning_task} для {employee}.")

                if learning_task.type == 'material':

                    # Забираем материал.
                    material = learning_task.material

                    # Проверка на переназначение.
                    if reassignment == 'not_completed' and Result.objects.filter(
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
                    if reassignment == 'not_appoint' and Result.objects.filter(
                            employee=employee,
                            material=material
                    ).exists():
                        logger.info(f"Пропускаем для {employee}: уже назначен")
                        continue

                    # Создание объекта результата для задачи.
                    learning_task_result = Result.objects.create(
                        learning_path=learning_path,
                        learning_path_result=learning_path_result,
                        employee=employee,
                        material=material,
                        learning_task=learning_task,
                        assignment=assignment,
                        type='material',
                        planned_end_date=planned_end_date,
                    )
                    logger.info(f"Создан {learning_task_result}")

                if learning_task.type == 'test':

                    # Забираем тест.
                    test = learning_task.test

                    # Проверка на переназначение.
                    if reassignment == 'not_completed' and Result.objects.filter(
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
                    if reassignment == 'not_appoint' and Result.objects.filter(
                            employee=employee,
                            test=test
                    ).exists():
                        logger.info(f"Пропускаем для {employee}: уже назначен.")
                        continue

                    # Создание объекта результата для задачи.
                    learning_task_result = Result.objects.create(
                        learning_path=learning_path,
                        learning_path_result=learning_path_result,
                        employee=employee,
                        test=test,
                        learning_task=learning_task,
                        assignment=assignment,
                        type='test',
                        planned_end_date=planned_end_date,
                    )
                    logger.info(f"Создан {learning_task_result}")

                if learning_task.type == 'work':

                    # Забираем тест.
                    work = learning_task.work

                    # Проверка на переназначение.
                    if reassignment == 'not_completed' and Result.objects.filter(
                            employee=employee,
                            work=work,
                            status='completed'
                    ).exists():
                        logger.info(f"Пропускаем для {employee}: уже сдан.")
                        if learning_task.control_task == True:
                            learning_path_result.completed_control_tasks +=1
                            learning_path_result.save()
                            logger.info(f"Перезачтено задач: {learning_path_result.completed_control_tasks}")
                        continue
                    if reassignment == 'not_appoint' and Result.objects.filter(
                            employee=employee,
                            work=work
                    ).exists():
                        logger.info(f"Пропускаем для {employee}: уже назначен.")
                        continue

                    # Создание объекта результата для задачи.
                    learning_task_result = Result.objects.create(
                        learning_path=learning_path,
                        learning_path_result=learning_path_result,
                        employee=employee,
                        work=work,
                        learning_task=learning_task,
                        assignment=assignment,
                        type='work',
                        planned_end_date=planned_end_date,
                    )
                    logger.info(f"Создан {learning_task_result}")

                if learning_task.type == 'course':

                    # Забираем курс.
                    course = learning_task.course

                    # Проверка на переназначение.
                    if reassignment == 'not_completed' and Result.objects.filter(
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
                    if reassignment == 'not_appoint' and Result.objects.filter(
                            employee=employee,
                            course=course
                    ).exists():
                        logger.info(f"Пропускаем для {employee}: уже назначен")
                        continue

                    # Создание объекта результата для задачи.
                    learning_task_result = Result.objects.create(
                        learning_path=learning_path,
                        learning_path_result=learning_path_result,
                        employee=employee,
                        course=course,
                        learning_task=learning_task,
                        assignment=assignment,
                        type='course',
                        planned_end_date=planned_end_date,
                    )
                    logger.info(f"Создан {learning_task_result}")

                # Добавление контролеров
                for supervisor in supervisors:
                    result_supervising, _ = ResultSupervising.objects.get_or_create(
                        supervisor=supervisor,
                        result=learning_task_result
                    )
                    logger.info(f"Создан контроль результата {result_supervising}")

    # Создание результатов учебной траектории.
    def create_learning_path_results(assignment, employee, learning_path, planned_start_date, reassignment):

        logger.info(f"!!!Дата начала назначения траектории: {planned_start_date}")
        # Забираем супервизоров
        supervisors = get_supervisors(assignment, employee)

        # Переменные.
        duration = learning_path.duration
        planned_end_date = planned_start_date + timedelta(days=duration)
        logger.info(f"Назначение учебной траектории {learning_path} для {employee}.")

        # Проверка на переназначение.
        if reassignment == 'not_completed' and Result.objects.filter(
            employee=employee,
            learning_path=learning_path,
            type='learning_path',
            status='completed'
        ).exists():
            logger.info(f"Пропускаем для {employee}: уже сдан")
            return
        if reassignment == 'not_appoint' and Result.objects.filter(
            employee=employee,
            learning_path=learning_path,
            type='learning_path'
        ).exists():
            logger.info(f"Пропускаем для {employee}: уже назначен")
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

        # Добавление контролеров
        for supervisor in supervisors:
            result_supervising, _ = ResultSupervising.objects.get_or_create(
                supervisor=supervisor,
                result=learning_path_result
            )
            logger.info(f"Создан контроль результата {result_supervising}")

        # Перебор задач учебного пути.
        for learning_task in learning_path.learning_tasks.all():
            logger.info(f"Назначение учебной задачи {learning_task} для {employee}.")

            if learning_task.type == 'material':

                # Забираем материал.
                material = learning_task.material

                # Проверка на переназначение.
                if reassignment == 'not_completed' and Result.objects.filter(
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
                if reassignment == 'not_appoint' and Result.objects.filter(
                        employee=employee,
                        material=material
                ).exists():
                    logger.info(f"Пропускаем для {employee}: уже назначен")
                    continue

                # Создание объекта результата для задачи.
                learning_task_result = Result.objects.create(
                    learning_path=learning_path,
                    learning_path_result=learning_path_result,
                    employee=employee,
                    material=material,
                    learning_task=learning_task,
                    assignment=assignment,
                    type='material',
                    planned_end_date=planned_end_date,
                )
                logger.info(f"Создан {learning_task_result}")

            if learning_task.type == 'test':

                # Забираем тест.
                test = learning_task.test

                # Проверка на переназначение.
                if reassignment == 'not_completed' and Result.objects.filter(
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
                if reassignment == 'not_appoint' and Result.objects.filter(
                        employee=employee,
                        test=test
                ).exists():
                    logger.info(f"Пропускаем для {employee}: уже назначен.")
                    continue

                # Создание объекта результата для задачи.
                learning_task_result = Result.objects.create(
                    learning_path=learning_path,
                    learning_path_result=learning_path_result,
                    employee=employee,
                    test=test,
                    learning_task=learning_task,
                    assignment=assignment,
                    type='test',
                    planned_end_date=planned_end_date,
                )
                logger.info(f"Создан {learning_task_result}")

            if learning_task.type == 'work':

                # Забираем тест.
                work = learning_task.work

                # Проверка на переназначение.
                if reassignment == 'not_completed' and Result.objects.filter(
                        employee=employee,
                        work=work,
                        status='completed'
                ).exists():
                    logger.info(f"Пропускаем для {employee}: уже сдан.")
                    if learning_task.control_task == True:
                        learning_path_result.completed_control_tasks += 1
                        learning_path_result.save()
                        logger.info(f"Перезачтено задач: {learning_path_result.completed_control_tasks}")
                    continue
                if reassignment == 'not_appoint' and Result.objects.filter(
                        employee=employee,
                        work=work
                ).exists():
                    logger.info(f"Пропускаем для {employee}: уже назначен.")
                    continue

                # Создание объекта результата для задачи.
                learning_task_result = Result.objects.create(
                    learning_path=learning_path,
                    learning_path_result=learning_path_result,
                    employee=employee,
                    work=work,
                    learning_task=learning_task,
                    assignment=assignment,
                    type='work',
                    planned_end_date=planned_end_date,
                )
                logger.info(f"Создан {learning_task_result}")

            if learning_task.type == 'course':

                # Забираем курс.
                course = learning_task.course

                # Проверка на переназначение.
                if reassignment == 'not_completed' and Result.objects.filter(
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
                if reassignment == 'not_appoint' and Result.objects.filter(
                        employee=employee,
                        course=course
                ).exists():
                    logger.info(f"Пропускаем для {employee}: уже назначен")
                    continue

                # Создание объекта результата для задачи.
                learning_task_result = Result.objects.create(
                    learning_path=learning_path,
                    learning_path_result=learning_path_result,
                    employee=employee,
                    course=course,
                    learning_task=learning_task,
                    assignment=assignment,
                    type='course',
                    planned_end_date=planned_end_date,
                )
                logger.info(f"Создан {learning_task_result}")

            # Добавление контролеров
            for supervisor in supervisors:
                result_supervising, _ = ResultSupervising.objects.get_or_create(
                    supervisor=supervisor,
                    result=learning_task_result
                )
                logger.info(f"Создан контроль результата {result_supervising}")

    # Создание прав доступа.
    def create_groups_perms(type, object, participants_group):

        # Создание прав.
        if type == 'learning_complex':

            # Переменная.
            learning_paths = object

            # Для траекторий.
            for learning_path in learning_paths:

                # Присвоение прав доступа.
                assign_perm('view_learningpath', participants_group, learning_path)
                logger.info(f"Право на просмотр учебной траектории {learning_path} назначено группе {participants_group}.")

                # Перебор задач учебного пути.
                for learning_task in learning_path.learning_tasks.all():

                    # Пррисвоение прав доступа.
                    # assign_perm('view_learningtask', participants_group, learning_task)
                    # logger.info(f"Право на просмотр учебной задачи {learning_task} назначено группе {participants_group}.")

                    if learning_task.type == 'material':

                        # Забираем материал.
                        material=learning_task.material

                        # Присвоение прав доступа.
                        assign_perm('view_material', participants_group, material)
                        logger.info(f"Право на просмотр материала {material} назначено группе {participants_group}.")

                    if learning_task.type == 'test':

                        # Забираем тест.
                        test = learning_task.test

                        # Присвоение прав доступа.
                        assign_perm('view_test', participants_group, test)
                        logger.info(f"Право на просмотр теста {test} назначено группе {participants_group}.")

                    if learning_task.type == 'work':

                        # Забираем тест.
                        work = learning_task.work

                        # Присвоение прав доступа.
                        assign_perm('view_work', participants_group, work)
                        logger.info(f"Право на просмотр теста {work} назначено группе {participants_group}.")

                    if learning_task.type == 'course':

                        # Забираем курс.
                        course = learning_task.course

                        # Присвоение прав доступа.
                        assign_perm('view_course', participants_group, course)
                        logger.info(f"Право на просмотр курса {course} назначено группе {participants_group}.")

                    # Добавьте обработку других объектов.

        # Создание прав.
        if type == 'learning_path':

            # Переменная.
            learning_path = object

            # Присвоение прав доступа для группы.
            assign_perm('view_learningpath', participants_group, learning_path)
            logger.info(
                f"Право на просмотр учебной траектории {learning_path} назначено группе {participants_group}.")

            # Перебор задач учебного пути.
            for learning_task in learning_path.learning_tasks.all():

                # Пррисвоение прав доступа.
                # assign_perm('view_learningtask', participants_group, learning_task)
                # logger.info(f"Право на просмотр учебной задачи {learning_task} назначено группе {participants_group}.")

                if learning_task.type == 'material':
                    # Забираем материал.
                    material = learning_task.material

                    # Присвоение прав доступа.
                    assign_perm('view_material', participants_group, material)
                    logger.info(
                        f"Право на просмотр материала {material} назначено группе {participants_group}.")

                if learning_task.type == 'test':
                    # Забираем тест.
                    test = learning_task.test

                    # Присвоение прав доступа.
                    assign_perm('view_test', participants_group, test)
                    logger.info(f"Право на просмотр теста {test} назначено группе {participants_group}.")

                if learning_task.type == 'work':
                    # Забираем тест.
                    work = learning_task.work

                    # Присвоение прав доступа.
                    assign_perm('view_work', participants_group, work)
                    logger.info(f"Право на просмотр теста {work} назначено группе {participants_group}.")

                if learning_task.type == 'course':
                    # Забираем курс.
                    course = learning_task.course

                    # Присвоение прав доступа.
                    assign_perm('view_course', participants_group, course)
                    logger.info(f"Право на просмотр курса {course} назначено группе {participants_group}.")

        # Создание прав.
        if type == 'material':

            # Переменная.
            material = object

            # Присвоение прав доступа для группы.
            assign_perm('view_material', participants_group, material)
            logger.info(f"Право на просмотр материала {material} назначено группе {participants_group}.")

        # Создание прав.
        if type == 'test':
            # Переменная.
            test = object

            # Присвоение прав доступа для группы.
            assign_perm('view_test', participants_group, test)
            logger.info(f"Право на просмотр теста {test} назначено группе {participants_group}.")

        # Создание прав.
        if type == 'work':
            # Переменная.
            work = object

            # Присвоение прав доступа для группы.
            assign_perm('view_work', participants_group, work)
            logger.info(f"Право на просмотр теста {work} назначено группе {participants_group}.")

        # Создание прав.
        if type == 'course':
            # Переменная.
            course = object

            # Присвоение прав доступа для группы.
            assign_perm('view_course', participants_group, course)
            logger.info(f"Право на просмотр курс {course} назначено группе {participants_group}.")

    # Создание прав доступа.
    def create_employees_perms(type, object, employee):

        # Создание .
        if type == 'learning_complex':

            # Переменная прав.
            learning_paths = object

            # Создание прав учебных задач.
            for learning_path in learning_paths:

                # Присвоение прав доступа.
                assign_perm('view_learningpath', employee, learning_path)
                logger.info(f"Право на просмотр учебной траектории {learning_path} назначено {employee}.")

                # Перебор задач учебного пути.
                for learning_task in learning_path.learning_tasks.all():

                    # Пррисвоение прав доступа.
                    # assign_perm('view_learningtask', employee, learning_task)
                    # logger.info(f"Право на просмотр учебной задачи {learning_task} назначено {employee}.")

                    if learning_task.type == 'material':

                        # Забираем материал.
                        material=learning_task.material

                        # Присвоение прав доступа.
                        assign_perm('view_material', employee, material)
                        logger.info(f"Право на просмотр материала {material} назначено {employee}.")

                    if learning_task.type == 'test':

                        # Забираем тест.
                        test = learning_task.test

                        # Присвоение прав доступа.
                        assign_perm('view_test', employee, test)
                        logger.info(f"Право на просмотр теста {test} назначено {employee}.")

                    if learning_task.type == 'work':

                        # Забираем тест.
                        work = learning_task.work

                        # Присвоение прав доступа.
                        assign_perm('view_work', employee, work)
                        logger.info(f"Право на просмотр теста {work} назначено {employee}.")

                    if learning_task.type == 'course':

                        # Забираем курс.
                        course = learning_task.course

                        # Присвоение прав доступа.
                        assign_perm('view_course', employee, course)
                        logger.info(f"Право на просмотр курса {course} назначено {employee}.")

        # Создание прав.
        if type == 'learning_path':

            # Переменная.
            learning_path = object

            # Присвоение прав доступа для группы.
            assign_perm('view_learningpath', employee, learning_path)
            logger.info(f"Право на просмотр учебной траектории {learning_path} назначено {employee}.")

            # Перебор задач учебного пути.
            for learning_task in learning_path.learning_tasks.all():

                # Пррисвоение прав доступа.
                # assign_perm('view_learningtask', employee, learning_task)
                # logger.info(f"Право на просмотр учебной задачи {learning_task} назначено {employee}.")

                if learning_task.type == 'material':

                    # Забираем материал.
                    material = learning_task.material

                    # Присвоение прав доступа к тесту для группы.
                    assign_perm('view_material', employee, material)
                    logger.info(f"Право на просмотр материала {material} назначено {employee}.")

                if learning_task.type == 'test':

                    # Забираем тест.
                    test = learning_task.test

                    # Присвоение прав доступа к Material для группы.
                    assign_perm('view_test', employee, test)
                    logger.info(f"Право на просмотр теста {test} назначено {employee}.")

                if learning_task.type == 'work':

                    # Забираем тест.
                    work = learning_task.work

                    # Присвоение прав доступа к Material для группы.
                    assign_perm('view_work', employee, work)
                    logger.info(f"Право на просмотр теста {work} назначено {employee}.")

                if learning_task.type == 'course':

                    # Забираем курс.
                    course = learning_task.course

                    # Присвоение прав доступа к тесту для группы.
                    assign_perm('view_course', employee, course)
                    logger.info(f"Право на просмотр курса {course} назначено {employee}.")

        # Создание прав.
        if type == 'material':

            # Переменная.
            material = object

            # Присвоение прав доступа для группы.
            assign_perm('view_material', employee, material)
            logger.info(f"Право на просмотр материала {material} назначено {employee}.")

        # Создание прав.
        if type == 'test':

            # Переменная.
            test = object

            # Присвоение прав доступа для группы.
            assign_perm('view_test', employee, test)
            logger.info(f"Право на просмотр теста {test} назначено {employee}.")

        # Создание прав.
        if type == 'work':

            # Переменная.
            work = object

            # Присвоение прав доступа для группы.
            assign_perm('view_work', employee, work)
            logger.info(f"Право на просмотр теста {work} назначено {employee}.")

        # Создание прав.
        if type == 'course':

            # Переменная.
            course = object

            # Присвоение прав доступа для группы.
            assign_perm('view_course', employee, course)
            logger.info(f"Право на просмотр курс {course} назначено {employee}.")

    # Перехват ошибок.
    try:

        # Если объект создается.
        if created:
            logger.info(f"Обработка создания назначения: {instance}")

            # Получение переменных.
            assignment = instance
            reassignment = instance.reassignment
            if instance.participants == 'employee':
                employee = instance.employee
            if instance.participants == 'group':
                group = instance.group
                employees = Employee.objects.filter(groups=group, is_active=True).prefetch_related(
                    'results',
                )
            planned_start_date = instance.planned_start_date
            logger.info(f"!!!Дата начала назначения: {instance}")
            if instance.type == 'material' or instance.type == 'test' or instance.type == 'work' or instance.type == 'course':
                duration = instance.duration
                planned_end_date = planned_start_date + timedelta(days=duration)

            # Общие переменные.
            if instance.type == 'learning_complex':
                learning_complex = instance.learning_complex
                learning_paths = [
                    learning_complex_path.learning_path for learning_complex_path in
                    learning_complex.learning_complex_paths.all().order_by('learning_complex', 'position')
                ]
                if instance.participants == 'group':
                    participants_group_name = f"Назначение комплексной программы [{instance.pk}]: {instance.learning_complex.name} для {group} с {planned_start_date.strftime('%d.%m.%Y')}"
            if instance.type == 'learning_path':
                learning_path = instance.learning_path
                if instance.participants == 'group':
                    participants_group_name = f"Назначение траектории обучения [{instance.pk}]: {instance.learning_path.name} для {group} с {planned_start_date.strftime('%d.%m.%Y')}"
            if instance.type == 'material':
                material = instance.material
                if instance.participants == 'group':
                    participants_group_name = f"Назначение материала [{instance.pk}]: {instance.material.name} для {group} с {planned_start_date.strftime('%d.%m.%Y')}"
            if instance.type == 'test':
                test = instance.test
                if instance.participants == 'group':
                    participants_group_name = f"Назначение теста [{instance.pk}]: {instance.test.name} для {group} с {planned_start_date.strftime('%d.%m.%Y')}"
            if instance.type == 'work':
                work = instance.work
                if instance.participants == 'group':
                    participants_group_name = f"Назначение теста [{instance.pk}]: {instance.work.name} для {group} с {planned_start_date.strftime('%d.%m.%Y')}"
            if instance.type == 'course':
                course = instance.course
                if instance.participants == 'group':
                    participants_group_name = f"Назначение курса [{instance.pk}]: {instance.course.name} для {group} с {planned_start_date.strftime('%d.%m.%Y')}"

            # Забираем группу для участников.
            if instance.participants == 'group':
                participants_group, _ = EmployeesGroup.objects.get_or_create(name=participants_group_name, type='assignment')
                instance.participants_group = participants_group
                instance.save()
                # Теперь добавляем по одному.
                # participants_group.user_set.set(employees)
                logger.info(f"Была создана группа для назначения: {participants_group}.")

            # Создание результатов.
            if instance.type == 'learning_complex':

                # Создание результатов группы.
                if instance.participants == 'group':

                    # Нарезка.
                    chunk_size = 50
                    employees_chunks = [employees[i:i + chunk_size] for i in range(0, len(employees), chunk_size)]

                    # Перебор сотрудников и создание результатов.
                    for employees_chunk in employees_chunks:
                        for employee in employees_chunk:

                            # Действия.
                            learning_complex_results = create_learning_complex_results(
                                assignment=assignment,
                                employee=employee,
                                learning_complex=learning_complex,
                                learning_paths=learning_paths,
                                planned_start_date=planned_start_date,
                                reassignment=reassignment
                            )
                            participants_group.user_set.add(employee)
                            logger.info(f"Сотрудник {employee} добавлен в группу участников назначения")
                        logger.info("Массовое создание результатов завершено.")

                    # Создание прав.
                    create_groups_perms(instance.type, learning_paths, participants_group)

                # Создание результатов сотрудника.
                if instance.participants == 'employee':

                    # Действия.
                    learning_complex_results = create_learning_complex_results(
                        assignment=assignment,
                        employee=employee,
                        learning_complex=learning_complex,
                        learning_paths=learning_paths,
                        planned_start_date=planned_start_date,
                        reassignment=reassignment
                    )
                    logger.info("Cоздание результатов завершено.")

                    # Создание прав.
                    create_employees_perms(instance.type, learning_paths, employee)

            # Создание результатов.
            if instance.type == 'learning_path':

                # Создание результатов группы.
                if instance.participants == 'group':

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
                            participants_group.user_set.add(employee)
                            logger.info(f"Сотрудник {employee} добавлен в группу участников назначения")
                        logger.info("Массовое создание результатов завершено.")

                    # Создание прав.
                    create_groups_perms(instance.type, learning_path, participants_group)

                # Создание результатов сотрудника.
                if instance.participants == 'employee':

                    # Действия.
                    learning_path_result = create_learning_path_results(
                        assignment=assignment,
                        employee=employee,
                        learning_path=learning_path,
                        planned_start_date=planned_start_date,
                        reassignment=reassignment
                    )
                    logger.info("Создание результатов завершено.")

                    # Создание прав.
                    create_employees_perms(instance.type, learning_path, employee)

            # Создание результатов.
            if instance.type == 'material':

                # Создание результатов группы.
                if instance.participants == 'group':

                    # Нарезка.
                    chunk_size = 50
                    employees_chunks = [employees[i:i + chunk_size] for i in range(0, len(employees), chunk_size)]

                    # Перебор сотрудников и создание результатов.
                    for employees_chunk in employees_chunks:
                        for employee in employees_chunk:

                            # Проверка на переназначение.
                            if reassignment == 'not_completed' and Result.objects.filter(
                                    employee=employee,
                                    material=material,
                                    status='completed'
                            ).exists():
                                logger.info(f"Пропускаем для {employee}: уже сдан")
                                continue
                            if reassignment == 'not_appoint' and Result.objects.filter(
                                    employee=employee,
                                    material=material
                            ).exists():
                                logger.info(f"Пропускаем для {employee}: уже назначен")
                                continue

                            # Создание объекта результата для задачи.
                            material_result = Result.objects.create(
                                employee=employee,
                                material=material,
                                assignment=assignment,
                                planned_end_date=planned_end_date,
                                type='material',
                            )
                            logger.info(f"Создан {material_result}")

                            # Забираем супервизоров
                            supervisors = get_supervisors(assignment, employee)
                            # Добавление контролеров
                            for supervisor in supervisors:
                                result_supervising, _ = ResultSupervising.objects.get_or_create(
                                    supervisor=supervisor,
                                    result=material_result
                                )
                                logger.info(f"Создан контроль результата {result_supervising}")

                            participants_group.user_set.add(employee)
                            logger.info(f"Сотрудник {employee} добавлен в группу участников назначения")

                    # Присвоение прав доступа.
                    assign_perm('view_material', participants_group, material)
                    logger.info(f"Право на просмотр материала {material} назначено группе {participants_group}.")

                # Создание результатов сотрудника.
                if instance.participants == 'employee':

                    # Проверка на переназначение.
                    if reassignment == 'not_completed' and Result.objects.filter(
                            employee=employee,
                            material=material,
                            status='completed'
                    ).exists():
                        logger.info(f"Пропускаем для {employee}: уже сдан")
                    if reassignment == 'not_appoint' and Result.objects.filter(
                            employee=employee,
                            material=material
                    ).exists():
                        logger.info(f"Пропускаем для {employee}: уже назначен")

                    # Создание объекта результата для задачи.
                    material_result = Result.objects.create(
                        employee=employee,
                        material=material,
                        assignment=assignment,
                        planned_end_date=planned_end_date,
                        type='material'
                    )
                    logger.info(f"Создан {material_result}")

                    # Забираем супервизоров
                    supervisors = get_supervisors(assignment, employee)
                    # Добавление контролеров
                    for supervisor in supervisors:
                        result_supervising, _ = ResultSupervising.objects.get_or_create(
                            supervisor=supervisor,
                            result=material_result
                        )
                        logger.info(f"Создан контроль результата {result_supervising}")

                    # Присвоение прав доступа.
                    assign_perm('view_material', employee, material)
                    logger.info(f"Право на просмотр материала {material} назначено {employee}.")

            # Создание результатов.
            if instance.type == 'test':

                # Создание результатов группы.
                if instance.participants == 'group':

                    # Нарезка.
                    chunk_size = 50
                    employees_chunks = [employees[i:i + chunk_size] for i in range(0, len(employees), chunk_size)]

                    # Перебор сотрудников и создание результатов.
                    for employees_chunk in employees_chunks:
                        for employee in employees_chunk:

                            # Проверка на переназначение.
                            if reassignment == 'not_completed' and Result.objects.filter(
                                    employee=employee,
                                    test=test,
                                    status='completed'
                            ).exists():
                                logger.info(f"Пропускаем для {employee}: уже сдан")
                                continue
                            if reassignment == 'not_appoint' and Result.objects.filter(
                                    employee=employee,
                                    test=test
                            ).exists():
                                logger.info(f"Пропускаем для {employee}: уже назначен")
                                continue

                            # Создание объекта результата для задачи.
                            test_result = Result.objects.create(
                                employee=employee,
                                test=test,
                                assignment=assignment,
                                planned_end_date=planned_end_date,
                                type='test'
                            )
                            logger.info(f"Создан {test_result}")

                            # Забираем супервизоров
                            supervisors = get_supervisors(assignment, employee)
                            # Добавление контролеров
                            for supervisor in supervisors:
                                result_supervising, _ = ResultSupervising.objects.get_or_create(
                                    supervisor=supervisor,
                                    result=test_result
                                )
                                logger.info(f"Создан контроль результата {result_supervising}")

                            participants_group.user_set.add(employee)
                            logger.info(f"Сотрудник {employee} добавлен в группу участников назначения")

                    # Присвоение прав доступа.
                    assign_perm('view_test', participants_group, test)
                    logger.info(f"Право на просмотр теста {test} назначено группе {participants_group}.")


                # Создание результатов сотрудника.
                if instance.participants == 'employee':

                    # Проверка на переназначение.
                    if reassignment == 'not_completed' and Result.objects.filter(
                            employee=employee,
                            test=test,
                            status='completed'
                    ).exists():
                        logger.info(f"Пропускаем для {employee}: уже сдан")
                    if reassignment == 'not_appoint' and Result.objects.filter(
                            employee=employee,
                            test=test
                    ).exists():
                        logger.info(f"Пропускаем для {employee}: уже назначен")

                    # Создание объекта результата для задачи.
                    test_result = Result.objects.create(
                        employee=employee,
                        test=test,
                        assignment=assignment,
                        planned_end_date=planned_end_date,
                        type='test'
                    )
                    logger.info(f"Создан {test_result}")

                    # Забираем супервизоров
                    supervisors = get_supervisors(assignment, employee)
                    # Добавление контролеров
                    for supervisor in supervisors:
                        result_supervising, _ = ResultSupervising.objects.get_or_create(
                            supervisor=supervisor,
                            result=test_result
                        )
                        logger.info(f"Создан контроль результата {result_supervising}")

                    # Присвоение прав доступа.
                    assign_perm('view_test', employee, test)
                    logger.info(f"Право на просмотр теста {test} назначено {employee}.")

            # Создание результатов.
            if instance.type == 'work':

                # Создание результатов группы.
                if instance.participants == 'group':

                    # Нарезка.
                    chunk_size = 50
                    employees_chunks = [employees[i:i + chunk_size] for i in range(0, len(employees), chunk_size)]

                    # Перебор сотрудников и создание результатов.
                    for employees_chunk in employees_chunks:
                        for employee in employees_chunk:

                            # Проверка на переназначение.
                            if reassignment == 'not_completed' and Result.objects.filter(
                                    employee=employee,
                                    work=work,
                                    status='completed'
                            ).exists():
                                logger.info(f"Пропускаем для {employee}: уже сдан")
                                continue
                            if reassignment == 'not_appoint' and Result.objects.filter(
                                    employee=employee,
                                    work=work
                            ).exists():
                                logger.info(f"Пропускаем для {employee}: уже назначен")
                                continue

                            # Создание объекта результата для задачи.
                            work_result = Result.objects.create(
                                employee=employee,
                                work=work,
                                assignment=assignment,
                                planned_end_date=planned_end_date,
                                type='work'
                            )
                            logger.info(f"Создан {work_result}")

                            # Забираем супервизоров
                            supervisors = get_supervisors(assignment, employee)
                            # Добавление контролеров
                            for supervisor in supervisors:
                                result_supervising, _ = ResultSupervising.objects.get_or_create(
                                    supervisor=supervisor,
                                    result=work_result
                                )
                                logger.info(f"Создан контроль результата {result_supervising}")

                            participants_group.user_set.add(employee)
                            logger.info(f"Сотрудник {employee} добавлен в группу участников назначения")

                    # Присвоение прав доступа.
                    assign_perm('view_work', participants_group, work)
                    logger.info(f"Право на просмотр теста {work} назначено группе {participants_group}.")


                # Создание результатов сотрудника.
                if instance.participants == 'employee':

                    # Проверка на переназначение.
                    if reassignment == 'not_completed' and Result.objects.filter(
                            employee=employee,
                            work=work,
                            status='completed'
                    ).exists():
                        logger.info(f"Пропускаем для {employee}: уже сдан")
                    if reassignment == 'not_appoint' and Result.objects.filter(
                            employee=employee,
                            work=work
                    ).exists():
                        logger.info(f"Пропускаем для {employee}: уже назначен")

                    # Создание объекта результата для задачи.
                    work_result = Result.objects.create(
                        employee=employee,
                        work=work,
                        assignment=assignment,
                        planned_end_date=planned_end_date,
                        type='work'
                    )
                    logger.info(f"Создан {work_result}")

                    # Забираем супервизоров
                    supervisors = get_supervisors(assignment, employee)
                    # Добавление контролеров
                    for supervisor in supervisors:
                        result_supervising, _ = ResultSupervising.objects.get_or_create(
                            supervisor=supervisor,
                            result=work_result
                        )
                        logger.info(f"Создан контроль результата {result_supervising}")

                    # Присвоение прав доступа.
                    assign_perm('view_work', employee, work)
                    logger.info(f"Право на просмотр теста {work} назначено {employee}.")


            # Создание результатов.
            if instance.type == 'course':

                # Создание результатов группы.
                if instance.participants == 'group':

                    # Нарезка.
                    chunk_size = 50
                    employees_chunks = [employees[i:i + chunk_size] for i in range(0, len(employees), chunk_size)]

                    # Перебор сотрудников и создание результатов.
                    for employees_chunk in employees_chunks:
                        for employee in employees_chunk:

                            # Проверка на переназначение.
                            if reassignment == 'not_completed' and Result.objects.filter(
                                    employee=employee,
                                    course=course,
                                    status='completed'
                            ).exists():
                                logger.info(f"Пропускаем для {employee}: уже сдан")
                                continue
                            if reassignment == 'not_appoint' and Result.objects.filter(
                                    employee=employee,
                                    course=course
                            ).exists():
                                logger.info(f"Пропускаем для {employee}: уже назначен")
                                continue

                            # Создание объекта результата для задачи.
                            course_result = Result.objects.create(
                                employee=employee,
                                course=course,
                                assignment=assignment,
                                planned_end_date=planned_end_date,
                                type='course'
                            )
                            logger.info(f"Создан {course_result}")

                            # Забираем супервизоров
                            supervisors = get_supervisors(assignment, employee)
                            # Добавление контролеров
                            for supervisor in supervisors:
                                result_supervising, _ = ResultSupervising.objects.get_or_create(
                                    supervisor=supervisor,
                                    result=course_result
                                )
                                logger.info(f"Создан контроль результата {result_supervising}")

                            participants_group.user_set.add(employee)
                            logger.info(f"Сотрудник {employee} добавлен в группу участников назначения")

                    # Присвоение прав доступа.
                    assign_perm('view_course', participants_group, course)
                    logger.info(f"Право на просмотр курса {course} назначено группе {participants_group}.")

                # Создание результатов сотрудника.
                if instance.participants == 'employee':

                    # Проверка на переназначение.
                    if reassignment == 'not_completed' and Result.objects.filter(
                            employee=employee,
                            course=course,
                            status='completed'
                    ).exists():
                        logger.info(f"Пропускаем для {employee}: уже сдан")
                    if reassignment == 'not_appoint' and Result.objects.filter(
                            employee=employee,
                            course=course
                    ).exists():
                        logger.info(f"Пропускаем для {employee}: уже назначен")

                    # Создание объекта результата для задачи.
                    course_result = Result.objects.create(
                        employee=employee,
                        course=course,
                        assignment=assignment,
                        planned_end_date=planned_end_date,
                        type='course'
                    )
                    logger.info(f"Создан {course_result}")

                    # Забираем супервизоров
                    supervisors = get_supervisors(assignment, employee)
                    # Добавление контролеров
                    for supervisor in supervisors:
                        result_supervising, _ = ResultSupervising.objects.get_or_create(
                            supervisor=supervisor,
                            result=course_result
                        )
                        logger.info(f"Создан контроль результата {result_supervising}")

                    # Присвоение прав доступа.
                    assign_perm('view_course', employee, course)
                    logger.info(f"Право на просмотр курса {course} назначено {employee}.")

    # Логирование исключений, если они возникнут.
    except Exception as e:
        logger.error(f"Ошибка при обработке сигнала create_learning_results для Assignment: {e}", exc_info=True)
        # Повторный вызов исключения в режиме отладки.
        if settings.DEBUG:
            raise
        else:
            return HttpResponseServerError("Ошибка сервера, обратитесь к администратору")

# Сигнал удаления назначения.
@receiver(post_delete, sender=Assignment)
def delete_assignment(sender, instance, **kwargs):

    # Проверка ошибок.
    try:

        if instance.participants == 'group':

            # Удаляем связанные группы.
            instance.participants_group.delete()
            logger.info(f"Удаляется связанная с обучением {instance} группа {instance.participants_group}.")

        if instance.participants == 'employee':

            # Получение переменных.
            assignment = instance
            employee = instance.employee

            # Если это комплексная программа.
            if instance.type == 'learning_complex':

                # Забираем объект.
                learning_complex=instance.learning_complex

                # Убираем рпава доступа.
                for learning_path in learning_complex.learning_complex_paths.all():

                    result = Result.objects.get(
                        employee=employee,
                        assignment=assignment,
                        learning_path=learning_path,
                        type='learning_path'
                    )

                    if Result.objects.filter(
                            employee=employee,
                            learning_path=learning_path,
                            type='learning_path'
                    ).exclude(id=result.id).exists():
                        logger.info(f"Пропускаем для {learning_path}: есть другое назначение")
                        continue

                    # Исключение прав.
                    remove_perm('view_learningpath', employee, learning_path)
                    logger.info(f"Право на просмотр траектории обучения {learning_path} удалено {employee}.")

                    for learning_task in learning_path.learning_tasks.all():

                        result = Result.objects.get(
                            employee=employee,
                            assignment=assignment,
                            learning_task=learning_task,
                        )

                        if Result.objects.filter(
                                employee=employee,
                                learning_task=learning_task,
                        ).exclude(id=result.id).exists():
                            logger.info(f"Пропускаем для {learning_task}: есть другое назначение")
                            continue

                        # Исключение прав.
                        remove_perm('view_learningtask', employee, learning_task)
                        logger.info(f"Право на просмотр материал {learning_task} удалено {employee}.")

                        # Создание результатов.
                        if learning_task.type == 'material':

                            # Забираем материал.
                            material = learning_task.material

                            # Исключение прав.
                            remove_perm('view_material', employee, material)
                            logger.info(f"Право на просмотр материал {material} удалено {employee}.")

                        # Создание результатов.
                        if learning_task.type == 'test':

                            # Забираем материал.
                            test = learning_task.test

                            # Исключение прав.
                            remove_perm('view_test', employee, test)
                            logger.info(f"Право на просмотр тест {test} удалено {employee}.")

                        # Создание результатов.
                        if learning_task.type == 'work':

                            # Забираем материал.
                            work = learning_task.work

                            # Исключение прав.
                            remove_perm('view_work', employee, work)
                            logger.info(f"Право на просмотр тест {work} удалено {employee}.")

                        # Создание результатов.
                        if learning_task.type == 'course':

                            # Забираем материал.
                            course = learning_task.course

                            # Исключение прав.
                            remove_perm('view_course', employee, course)
                            logger.info(f"Право на просмотр курс {course} удалено {employee}.")

            if instance.type == 'learning_path':

                # Забираем объект.
                learning_path=instance.learning_path

                result = Result.objects.get(
                    employee=employee,
                    assignment=assignment,
                    learning_path=learning_path,
                    type='learning_path'
                )

                if Result.objects.filter(
                        employee=employee,
                        learning_path=learning_path,
                        type='learning_path'
                ).exclude(id=result.id).exists():
                    logger.info(f"Пропускаем для {learning_path}: есть другое назначение")
                    return

                # Исключение прав.
                remove_perm('view_learningpath', employee, learning_path)
                logger.info(f"Право на просмотр траектории обучения {learning_path} удалено {employee}.")

                for learning_task in learning_path.learning_tasks.all():

                    result = Result.objects.get(
                        employee=employee,
                        assignment=assignment,
                        learning_task=learning_task,
                    )

                    if Result.objects.filter(
                            employee=employee,
                            learning_task=learning_task,
                    ).exclude(id=result.id).exists():
                        logger.info(f"Пропускаем для {learning_task}: есть другое назначение")
                        continue

                    # Исключение прав.
                    remove_perm('view_learningtask', employee, learning_task)
                    logger.info(f"Право на просмотр материал {learning_task} удалено {employee}.")

                    # Создание результатов.
                    if learning_task.type == 'material':
                        # Забираем материал.
                        material = learning_task.material

                        # Исключение прав.
                        remove_perm('view_material', employee, material)
                        logger.info(f"Право на просмотр материал {material} удалено {employee}.")

                    # Создание результатов.
                    if learning_task.type == 'test':
                        # Забираем материал.
                        test = learning_task.test

                        # Исключение прав.
                        remove_perm('view_test', employee, test)
                        logger.info(f"Право на просмотр тест {test} удалено {employee}.")

                    # Создание результатов.
                    if learning_task.type == 'work':
                        # Забираем материал.
                        work = learning_task.work

                        # Исключение прав.
                        remove_perm('view_work', employee, work)
                        logger.info(f"Право на просмотр тест {work} удалено {employee}.")

                    # Создание результатов.
                    if learning_task.type == 'course':
                        # Забираем материал.
                        course = learning_task.course

                        # Исключение прав.
                        remove_perm('view_course', employee, course)
                        logger.info(f"Право на просмотр курс {course} удалено {employee}.")

            if instance.type == 'material':

                # Забираем объект.
                material = instance.material

                result = Result.objects.get(
                    employee=employee,
                    assignment=assignment,
                    material=material,
                    type='material'
                )

                if Result.objects.filter(
                        employee=employee,
                        material=material,
                        type='material'
                ).exclude(id=result.id).exists():
                    logger.info(f"Пропускаем для {material}: есть другое назначение")
                    return

                # Исключение прав.
                remove_perm('view_material', employee, material)
                logger.info(f"Право на просмотр материала {material} удалено {employee}.")

            if instance.type == 'work':

                # Забираем объект.
                work = instance.work

                result = Result.objects.get(
                    employee=employee,
                    assignment=assignment,
                    work=work,
                    type='work'
                )

                if Result.objects.filter(
                        employee=employee,
                        work=work,
                        type='work'
                ).exclude(id=result.id).exists():
                    logger.info(f"Пропускаем для {work}: есть другое назначение")
                    return

                # Исключение прав.
                remove_perm('view_work', employee, work)
                logger.info(f"Право на просмотр материала {work} удалено {employee}.")

            if instance.type == 'test':

                # Забираем объект.
                test = instance.test

                result = Result.objects.get(
                    employee=employee,
                    assignment=assignment,
                    test=test,
                    type='test'
                )

                if Result.objects.filter(
                        employee=employee,
                        test=test,
                        type='test'
                ).exclude(id=result.id).exists():
                    logger.info(f"Пропускаем для {test}: есть другое назначение")
                    return

                # Исключение прав.
                remove_perm('view_test', employee, test)
                logger.info(f"Право на просмотр материала {test} удалено {employee}.")

            if instance.type == 'course':

                # Забираем объект.
                course = instance.course

                result = Result.objects.get(
                    employee=employee,
                    assignment=assignment,
                    course=course,
                    type='course'
                )

                if Result.objects.filter(
                        employee=employee,
                        course=course,
                        type='course'
                ).exclude(id=result.id).exists():
                    logger.info(f"Пропускаем для {course}: есть другое назначение")
                    return

                # Исключение прав.
                remove_perm('view_course', employee, course)
                logger.info(f"Право на просмотр материала {course} удалено {employee}.")

    # Логирование исключений, если они возникнут.
    except Exception as e:
        logger.error(f"Ошибка при обработке сигнала delete_assignment для Assignment: {e}", exc_info=True)
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

                # Если это тест.
                if instance.type == 'work':

                    # Вычисляем бонус.
                    works_bonus = instance.work.bonus
                    score_scaled = instance.score_scaled
                    bonus = (works_bonus * score_scaled) / 100

                    # Создаем транзакцию.
                    transaction, created = Transaction.objects.get_or_create(
                        type='work',
                        employee=instance.employee,
                        work=instance.work,
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
            if instance.status == 'present':

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

# Создание контроля результутов.
@receiver(post_save, sender=ResultSupervising)
def create_result_supervising(sender, instance, created, **kwargs):

    # Проверка ошибок.
    try:

        if created:
            # Извлекаем связанные объекты.
            result = instance.result
            supervisor = instance.supervisor

            # Присвоение прав доступа.
            assign_perm('view_result', supervisor, result)
            logger.info(f"Право на просмотр резульата {result} назначено {supervisor}.")

    # Логирование исключений, если они возникнут.
    except Exception as e:
        logger.error(f"Ошибка при обработке сигнала create_result_supervising для ResultSupervising: {e}", exc_info=True)
        # Повторный вызов исключения в режиме отладки.
        if settings.DEBUG:
            raise
        else:
            return HttpResponseServerError("Ошибка сервера, обратитесь к администратору")

# Удаление контроля результутов.
@receiver(post_delete, sender=ResultSupervising)
def delete_result_supervising(sender, instance, **kwargs):
    # Проверка ошибок.
    try:
        # Извлекаем связанные объекты.
        result = instance.result
        supervisor = instance.supervisor

        # Удаление прав доступа.
        remove_perm('view_result', supervisor, result)
        logger.info(f"Право на просмотр результата {result} удалено у {supervisor}.")

    # Логирование исключений, если они возникнут.
    except Exception as e:
        logger.error(f"Ошибка при обработке сигнала delete_result_supervising для ResultSupervising: {e}", exc_info=True)
        # Повторный вызов исключения в режиме отладки.
        if settings.DEBUG:
            raise
        else:
            return HttpResponseServerError("Ошибка сервера, обратитесь к администратору")