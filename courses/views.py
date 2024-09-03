from django.shortcuts import render

# Create your views here.

from django.conf import settings
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Course
from .filters import CourseFilter
from .forms import CourseForm
from django.shortcuts import render, redirect, reverse, get_object_or_404
from guardian.mixins import PermissionListMixin
from guardian.mixins import PermissionRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin as GPermissionRequiredMixin
from django.utils import timezone
from django.contrib.auth.decorators import permission_required
from guardian.shortcuts import get_perms
from guardian.shortcuts import get_objects_for_user
from learning_path.models import Result
from core.models import Employee
from django.db import models
from django.http import HttpResponseForbidden, HttpResponseServerError, HttpResponse, JsonResponse
from django.db.models import OuterRef, Subquery
from django.db.models.functions import Coalesce
from django.db.models import F
from django.db.models import Case, When, Value
import zipfile
import os
from django.views.decorators.csrf import csrf_exempt
import json
from django.db.models import Sum
from core.mixins import PreviousPageGetMixinL0, PreviousPageSetMixinL0, PreviousPageGetMixinL1, PreviousPageSetMixinL1, PreviousPageGetMixinL2, PreviousPageSetMixinL2
from reviews.models import Review
from core.models import EmployeesGroupObjectPermission, EmployeesObjectPermission
from reviews.filters import ObjectsReviewFilter
from django.core.paginator import Paginator
from django.contrib.contenttypes.models import ContentType
from core.filters import EmployeesGroupObjectPermissionGroupsFilter, EmployeesObjectPermissionEmployeesFilter
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
import shutil


# Импортируем логи
import logging
# Создаем логгер с именем 'project'
logger = logging.getLogger('project')

# Список курсов.
class CoursesView(LoginRequiredMixin, PreviousPageSetMixinL1, PermissionListMixin, ListView):
    # Права доступа
    permission_required = 'courses.view_course'
    # Модель.
    model = Course
    # Поле сортировки.
    ordering = 'name'
    # Шаблон.
    template_name = 'courses.html'
    # Количество объектов на странице
    paginate_by = 6

    # Переопределяем выборку вью.
    def get_queryset(self):
        # Забираем изначальную выборку вью.
        queryset = super().get_queryset().prefetch_related(
            'categories',
        )
        # Аннотируем queryset данными из последнего Result
        latest_result = Result.objects.filter(
            course_id=OuterRef('pk'), employee=self.request.user
        ).order_by('-id').values('status', 'learning_path_result__planned_end_date', 'end_date')[:1]
        queryset = queryset.annotate(
            latest_result_status=Subquery(latest_result.values('status')),
            latest_result_planned_end_date=Subquery(latest_result.values('learning_path_result__planned_end_date')),
            latest_result_end_date=Subquery(latest_result.values('end_date'))
        )
        queryset = queryset.annotate(
            has_date=Case(
                When(latest_result_planned_end_date__isnull=False, then=Value(1)),
                default=Value(0),
                output_field=models.IntegerField()
            )
        ).order_by('-has_date', 'latest_result_planned_end_date', 'name')

        # Добавляем модель фильтрации в выборку вью.
        self.filterset = CourseFilter(self.request.GET, queryset, request=self.request)

        # Все для блокировки.
        for obj in self.filterset.qs:
            # Забираем результат.
            if obj.results.filter(employee=self.request.user):
                result = obj.results.filter(employee=self.request.user).latest('id')
                # Все для блокировки, если есть результат связанный с задачей.
                if result.learning_task and result.learning_task.blocking_tasks:
                    blocking_tasks = result.learning_task.blocking_tasks.all()
                    # Добавляем задачи.
                    obj.now_blocking_tasks = [
                        blocking_task for blocking_task in blocking_tasks
                        if blocking_task.results.filter(employee=self.request.user).exists() and blocking_task.results.filter(employee=self.request.user).latest('id').status != 'completed'
                    ]

        # Возвращаем вью новую выборку.
        return self.filterset.qs

    # Добавляем во вью переменные.
    def get_context_data(self, **kwargs):
        # Забираем изначальный набор переменных.
        context = super().get_context_data(**kwargs)
        # Добавляем фильтрсет.
        context['filterset'] = self.filterset
        # Возвращаем новый набор переменных.
        return context

# Объект материала.
class CourseView(LoginRequiredMixin, PreviousPageGetMixinL1, PreviousPageSetMixinL0, PermissionRequiredMixin, DetailView):
    # Права доступа
    permission_required = 'courses.view_course'
    accept_global_perms = True
    # Модель.
    model = Course
    # Шаблон.
    template_name = 'course.html'

    # Добавляем во вью переменные.
    def get_context_data(self, **kwargs):
        # Забираем изначальный набор переменных.
        context = super().get_context_data(**kwargs)

        # Забираем результат.
        if self.object.results.filter(employee=self.request.user):
            result = self.object.results.filter(employee=self.request.user).latest('id')
            blocked = False
            # Все для блокировки, если есть результат связанный с задачей.
            if result.learning_task and result.learning_task.blocking_tasks:
                blocking_tasks = result.learning_task.blocking_tasks.all()
                # Забираем результаты.
                blocking_tasks_results = [
                    blocking_task.results.filter(employee=self.request.user).latest('id')
                    for blocking_task in blocking_tasks
                ]
                if settings.DEBUG:
                    logger.info(f"Результаты блокирующих задач: {blocking_tasks_results}")
                # Проверяем.
                if any(blocking_task_results.status != 'completed' for blocking_task_results in blocking_tasks_results):
                    # Блокируем.
                    blocked = True
                    # Добавляем задачи в контекст.
                    now_blocking_tasks = [
                        blocking_task for blocking_task in blocking_tasks
                        if blocking_task.results.filter(employee=self.request.user).exists() and blocking_task.results.filter(employee=self.request.user).latest('id').status != 'completed'
                    ]
                    if settings.DEBUG:
                        logger.info(f"Текущие блокирующие задачи: {blocking_tasks}")
                    context['now_blocking_tasks'] = now_blocking_tasks
                if settings.DEBUG:
                    logger.info(f"Блокировка: {blocked}")
            # Добавляем контекст.
            context['result'] = result
            context['blocked'] = blocked

        # Добавляем средний балл.
        # Сначала получаем сумму оценок и количество отзывов.
        reviews_sum = self.object.reviews.aggregate(Sum('score'))['score__sum']
        reviews_count = self.object.reviews.count()
        # Вычисляем среднюю оценку.
        if reviews_count > 0:
            reviews_average_mark = round((reviews_sum / reviews_count), 1)
        else:
            reviews_average_mark = 0
        # Добавляем вью.
        context['reviews_average_mark'] = reviews_average_mark

        # Добавляем отзывы.
        if Review.objects.filter(type='course', course__pk=self.kwargs.get('pk')).exists():
            reviews_queryset = Review.objects.filter(type='course', course__pk=self.kwargs.get('pk')).order_by('created')
        else:
            reviews_queryset = Review.objects.none()
        context['reviews_qs_count'] = len(reviews_queryset)
        reviews_filter = ObjectsReviewFilter(self.request.GET, queryset=reviews_queryset, request=self.request)
        reviews = reviews_filter.qs
        # Добавляем пагинатор.
        reviews_paginator = Paginator(reviews, 6)
        reviews_page_number = self.request.GET.get('reviews_page')
        reviews_page_obj = reviews_paginator.get_page(reviews_page_number)
        # Добавляем во вью.
        context['reviews_filter'] = reviews_filter
        context['reviews_page_obj'] = reviews_page_obj

        # Забираем отзыв.
        haves_review = False
        if self.object.reviews.filter(creator=self.request.user).exists():
            haves_review = True
        if settings.DEBUG:
            logger.info(f"Уже есть отзыв: {haves_review}")
        context['haves_review'] = haves_review

        # Добавляем объектные права.
        content_type = ContentType.objects.get_for_model(Course)
        if EmployeesGroupObjectPermission.objects.filter(
            content_type=content_type,
            object_pk=self.kwargs.get('pk')
        ).prefetch_related('content_object').exists():
            group_object_permissions_queryset = EmployeesGroupObjectPermission.objects.filter(
                content_type=content_type,
                object_pk=self.kwargs.get('pk')
            ).prefetch_related('content_object').order_by('group')

        else:
            group_object_permissions_queryset = EmployeesGroupObjectPermission.objects.none()
        context['group_object_permissions_qs_count'] = len(group_object_permissions_queryset)
        group_object_permissions_filter = EmployeesGroupObjectPermissionGroupsFilter(self.request.GET, queryset=group_object_permissions_queryset, request=self.request)
        group_object_permissions = group_object_permissions_filter.qs
        # Добавляем пагинатор.
        group_object_permissions_paginator = Paginator(group_object_permissions, 6)
        group_object_permissions_page_number = self.request.GET.get('group_object_permissions_page')
        group_object_permissions_page_obj = group_object_permissions_paginator.get_page(group_object_permissions_page_number)
        # Добавляем во вью.
        context['group_object_permissions_filter'] = group_object_permissions_filter
        context['group_object_permissions_page_obj'] = group_object_permissions_page_obj

        # Добавляем объектные права.
        if EmployeesObjectPermission.objects.filter(object_pk=self.kwargs.get('pk'), content_type=content_type).prefetch_related('content_object').exists():
            object_permissions_queryset = EmployeesObjectPermission.objects.filter(
                object_pk=self.kwargs.get('pk'),
                content_type=content_type
            ).prefetch_related('content_object').order_by('-id')
        else:
            object_permissions_queryset = EmployeesObjectPermission.objects.none()
        context['object_permissions_qs_count'] = len(object_permissions_queryset)
        object_permissions_filter = EmployeesObjectPermissionEmployeesFilter(self.request.GET, queryset=object_permissions_queryset, request=self.request)
        object_permissions = object_permissions_filter.qs
        # Добавляем пагинатор.
        object_permissions_paginator = Paginator(object_permissions, 6)
        object_permissions_page_number = self.request.GET.get('object_permissions_page')
        object_permissions_page_obj = object_permissions_paginator.get_page(object_permissions_page_number)
        # Добавляем во вью.
        context['object_permissions_filter'] = object_permissions_filter
        context['object_permissions_page_obj'] = object_permissions_page_obj

        # Возвращаем новый набор переменных.
        return context

# Создание материала.
class CourseCreateView(LoginRequiredMixin, GPermissionRequiredMixin, CreateView):
    # Права доступа.
    permission_required = 'courses.add_course'
    # Форма.
    form_class = CourseForm
    # Модель.
    model = Course
    # Шаблон.
    template_name = 'course_edit.html'

    # Заполнение полей данными.
    def get_initial(self):
        # Забираем изначальный набор.
        initial = super().get_initial()
        # Добавляем создателя: юзера отправившего запрос.
        initial["creator"] = self.request.user
        # Возвращаем значения в форму.
        return initial

    # Валидация формы.
    def form_valid(self, form):
        try:
            course = form.save()

            # Путь распаковки.
            extract_path = os.path.join(settings.MEDIA_ROOT, 'scorm_packages', str(course.id))

            # Создаем директорию.
            os.makedirs(extract_path, exist_ok=True)

            # Логирование: начало распаковки.
            logger.info(f"Начало распаковки SCORM-пакета {course.id}")

            # Распаковываем SCORM-пакет.
            with zipfile.ZipFile(course.zip_file.path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)

            # Логирование: успешная распаковка.
            logger.info(f"Успешная распаковка SCORM-пакета {course.id} в {extract_path}")

            return super().form_valid(form)

        except Exception as e:
            logger.error(f"Ошибка при распаковке SCORM-пакета {course.id}: {str(e)}")

            if settings.DEBUG:
                raise e
            else:
                return HttpResponseServerError("Ошибка сервера, обратитесь к администратору")

    # Перенаправление после валидации формы.
    def get_success_url(self):
        # Направляем по адресу объекта.
        return reverse('courses:course', kwargs={'pk': self.object.pk})

# Изменение материала.
class CourseUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    # Права доступа
    permission_required = 'courses.change_course'
    accept_global_perms = True
    # Форма.
    form_class = CourseForm
    # Модель.
    model = Course
    # Шаблон.
    template_name = 'course_edit.html'

    # Заполнение полей данными.
    def get_initial(self):
        # Забираем изначальный набор.
        initial = super().get_initial()
        # Добавляем создателя: юзера отправившего запрос.
        initial["creator"] = self.request.user
        # Возвращаем значения в форму.
        return initial

    # Валидация формы.
    def form_valid(self, form):

        try:

            # Сохраняем форму (обновляем курс).
            course = form.save()

            # Проверяем, был ли загружен новый файл.
            if 'zip_file' in form.changed_data:

                # Путь распаковки.
                extract_path = os.path.join(settings.MEDIA_ROOT, 'scorm_packages', str(course.id))

                # Удаляем старое содержимое, если оно существует.
                if os.path.exists(extract_path):
                    shutil.rmtree(extract_path)

                # Создаем директорию.
                os.makedirs(extract_path, exist_ok=True)

                # Логирование: начало распаковки.
                logger.info(f"Начало распаковки SCORM-пакета {course.id}")

                # Распаковываем SCORM-пакет.
                with zipfile.ZipFile(course.zip_file.path, 'r') as zip_ref:
                    zip_ref.extractall(extract_path)

                # Логирование: успешная распаковка.
                logger.info(f"Успешная распаковка SCORM-пакета {course.id} в {extract_path}")

            return super().form_valid(form)

        except Exception as e:
            logger.error(f"Ошибка при распаковке SCORM-пакета {course.id}: {str(e)}")

            if settings.DEBUG:
                raise e
            else:
                return HttpResponseServerError("Ошибка сервера, обратитесь к администратору")

    # Перенаправление после валидации формы.
    def get_success_url(self):
        # Направляем по адресу объекта.
        return reverse('courses:course', kwargs={'pk': self.object.pk})

# Удаление материала..
class CourseDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    # Права доступа
    permission_required = 'courses.delete_course'
    accept_global_perms = True
    # Модель.
    model = Course
    # Шаблон.
    template_name = 'course_delete.html'

    # Перенаправление после валидации формы.
    def get_success_url(self):
        # Направляем по адресу объектов.
        return reverse('courses:courses')

# Плеер.
@login_required
def scorm_display(request, course_id):
    logger.info(f"Запрос на отображение SCORM-пакета: {course_id}")
    # Забираем пакет.
    course = get_object_or_404(Course, pk=course_id)
    # Проверки.
    result = course.results.filter(employee=request.user).latest('id')
    if result.status != 'appointed' and result.status != 'in_progress':
        return HttpResponseForbidden('Вам не назначен этот курс!')
    if result.learning_task and result.learning_task.blocking_tasks:
        blocking_tasks = result.learning_task.blocking_tasks.all()
        blocking_tasks_results = [
            blocking_task.results.filter(employee=request.user).latest('id')
            for blocking_task in blocking_tasks
        ]
        if any(blocking_task_results.status != 'completed' for blocking_task_results in blocking_tasks_results):
            return HttpResponseForbidden('Курс заблокирован!')
    if course.type == 'ispring':
        type = 'ispring'
    if course.type == 'articulate':
        type = 'articulate'
    if course.type == 'scroll':
        type = 'scroll'
    # Получаем идентификатор текущего пользователя.
    user_id = request.user.id
    # Получаем контекст.
    context = {
        'user_id': user_id,
        'course_id': course_id,
        'course': course,
        'type': type,
    }
    # Отдаем.
    return render(request, 'scorm_display.html', context)


# Запуск SCORM.
@csrf_exempt
def scorm_initialize(request):
    # Выводим отладочную информацию о запросе.
    logger.info(f'scorm_initialize: {request}, {request.body}')

    # Проверка корректности метода.
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

    # Ловим ошибки.
    try:
        # Парсим JSON из тела запроса.
        data = json.loads(request.body)

        # Получаем user_id и course_id из данных запроса.
        user_id = data.get('user_id')
        course_id = data.get('course_id')

        # Проверяем.
        user = get_object_or_404(Employee, id=user_id)
        course = get_object_or_404(Course, id=course_id)

        # Сохраняем user_id и course_id в сессии.
        request.session['user_id'] = user_id
        request.session['course_id'] = course_id

        # Получаем объект Result для отслеживания прогресса пользователя.
        result = Result.objects.filter(employee_id=user_id, course_id=course_id).latest('id')

        # Если курс назначен - ставим отметку начала.
        if result.status == 'appointed':
            result.start_date = timezone.now()
            result.status = 'in_progress'
            result.save()

        # Возвращаем успешный JSON-ответ с информацией о процессе инициализации.
        logger.info(f'Результат курса: {result}')
        return JsonResponse({'status': 'initialize_success'})

    # Ловим ошибки декодирования JSON.
    except json.JSONDecodeError as e:
        logger.info(f'JSON Decode Error in scorm_initialize: {e}')
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)

    # Обрабатываем другие исключения, выводим ошибку.
    except Exception as e:
        logger.info(f'Error in scorm_initialize: {e}')
        return JsonResponse({'status': 'error', 'message': 'Internal server error'}, status=500)


# Получение значения из базы.
@csrf_exempt
def scorm_get_value(request):

    # Проверка корректности метода.
    if request.method != 'GET':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

    # Ловим ошибки.
    try:

        # Получаем значения из сессии.
        user_id = request.session.get('user_id')
        course_id = request.session.get('course_id')
        element = request.GET.get('element')

        # Выводим информацию о полученном элементе.
        if settings.DEBUG:
            logger.info(f'Запрашиваемый элемент: {element}')

        # Проверяем, что элемент был передан.
        if not element:
            return JsonResponse({'status': 'error', 'message': 'Element not specified'}, status=400)

        # Если запрашивается режим работы.
        if element == 'cmi.mode':
            # Установка режима работы для передачи пакету.
            scorm_mode = 'normal'
            return JsonResponse({'cmi.mode': scorm_mode})

        # Если запрашивается ID пользователя Django.
        if element == 'cmi.learner_id':
            # Возврат ID пользователя Django.
            return JsonResponse({'cmi.learner_id': request.user.id})

        # Если запрашивается имя пользователя Django.
        if element == 'cmi.learner_name':
            # Возврат имени пользователя Django.
            return JsonResponse({'cmi.learner_name': request.user.username})

        # Получаем последний объект Result из базы данных.
        result = Result.objects.filter(employee_id=user_id, course_id=course_id).latest('id')

        # Преобразование строки JSON в словарь Python.
        progress_data = json.loads(result.progress)

        # Если запрашивается номер взаимодействия.
        if element == 'cmi.interactions._count':
            # Возврат количества взаимодействий
            interaction_count = str(len(progress_data.get('cmi.interactions', [])))
            if settings.DEBUG:
                logger.info(f'Номер взаимодействия: {interaction_count}')
            return JsonResponse({'cmi.interactions._count': interaction_count})

        # Если запрашивается конкретное взаимодействие.
        elif element.startswith('cmi.interactions[') and element.endswith(']'):
            # Извлекаем индекс из строки элемента.
            index = int(element.split('[')[1].split(']')[0])
            # Извлекаем данные об интеракциях из прогресса.
            interaction_data = progress_data.get('cmi.interactions', [])
            # Проверяем, существует ли интеракция с запрошенным индексом.
            if index < len(interaction_data):
                # Возвращаем данные по конкретной интеракции.
                return JsonResponse(interaction_data[index])
            else:
                # Если индекс выходит за пределы существующих интеракций, возвращаем ошибку.
                return JsonResponse({'status': 'error', 'message': 'Invalid interaction index'}, status=404)

        # Возврат других элементов.
        elif element in progress_data:
            return JsonResponse({element: progress_data[element]})

        # Если нужного элемента нет - выдаем ошибку.
        else:
            return JsonResponse({'status': 'error', 'message': 'Element not found'}, status=404)

    # Если результата нет - выдаем ошибку.
    except Result.DoesNotExist:
        return JsonResponse({'status': 'progress_not_found'}, status=404)

    # Отрабатываем другие ошибки.
    except Exception as e:
        # Выводим информацию об ошибке в консоль.
        logger.info(f'Error in scorm_get_value: {e}')
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


# Установка значения в базе.
@csrf_exempt
def scorm_set_value(request):

    # Проверка корректности метода.
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

    # Ловим ошибки.
    try:

        # Разбор тела запроса.
        data = json.loads(request.body)
        if settings.DEBUG:
            logger.info(f'Данные запроса на запись данных: {data}')

        # Извлечение идентификатора пользователя и пакета SCORM из сессии.
        user_id = request.session.get('user_id')
        course_id = request.session.get('course_id')

        # Получение данных о прогрессе пользователя.
        result = Result.objects.filter(employee_id=user_id, course_id=course_id).latest('id')
        progress_data = json.loads(result.progress)

        # Инициализация, если отсутствует.
        progress_data.setdefault('cmi.interactions', [])

        check_status = False

        # Разбираем словарь.
        for key, value in data.items():

            # Если нужно записать результат взаимодействия.
            if 'cmi.interactions' in key:

                # Делим результат взаимодействия на уже выделенные точками части.
                parts = key.split('.')
                # Получение индекса взаимодействия.
                interaction_index = int(parts[2])
                # Получение свойства взаимодействия.
                interaction_property = parts[3]

                # Убедитесь, что у вас достаточно элементов в массиве.
                while len(progress_data['cmi.interactions']) <= interaction_index:
                    progress_data['cmi.interactions'].append({})

                # Обновление или добавление данных взаимодействия.
                progress_data['cmi.interactions'][interaction_index][interaction_property] = value

                # Печать результата
                if settings.DEBUG:
                    logger.info(f"Итог запроса на запись данных: cmi.interactions[{interaction_index}].{interaction_property} = {value}")

            # Если нужно записать что-то иное.
            else:

                # Обновление обычных ключей.
                progress_data[key] = value
                if settings.DEBUG:
                    logger.info(f"Итог запроса на запись данных: {key} = {value}")

                # Если нужно записать результат курса.
                if key == 'cmi.completion_status' or key == 'cmi.success_status':
                    check_status = True

        # Сохранение обновленных данных
        result.progress = json.dumps(progress_data)
        result.save()

        # Если нужно проверить статус:
        if check_status:

            # Если курс еще не пройден или не провален.
            if result.status != 'completed':

                # Преобразуем текущий прогресс в словарь.
                progress_data = json.loads(result.progress)

                # Забираем данные.
                success_status = progress_data.get('cmi.success_status', 'Статус выполнения не определен')
                if settings.DEBUG:
                    logger.info(f'Статус выполнения: {success_status}')
                completion_status = progress_data.get('cmi.completion_status', 'Статус прохождения не определен')
                if settings.DEBUG:
                    logger.info(f'Статус прохождения: {completion_status}')

                # Устанавливаем статус.
                if success_status in ['completed', 'passed']:
                    result.status = 'completed'
                    result.end_date = timezone.now()
                elif completion_status == 'completed' and success_status == 'unknown':
                    result.status = 'completed'
                    result.score_scaled = 100
                    result.end_date = timezone.now()
                elif success_status == 'failed':
                    result.status = 'failed'
                    result.end_date = timezone.now()
                if settings.DEBUG:
                    logger.info(f'Статус курса: {result.status}')

                # Забираем %.
                score_scaled = progress_data.get('cmi.score.scaled', False)
                if score_scaled:
                    result.score_scaled = round(float(score_scaled) * 100)
                    if settings.DEBUG:
                        logger.info(f'Полученный балл в %: {result.score_scaled}')

                # Сохранение обновленных данных.
                result.save()

        # Возвращаем ответ об успехе.
        return JsonResponse({'status': 'set_value_success'})

    # Отрабатываем отсутствие результата.
    except Result.DoesNotExist:
        return JsonResponse({'status': 'progress_not_found'}, status=404)

    # Ловим ошибки декодирования JSON.
    except json.JSONDecodeError as e:
        logger.info(f'JSON Decode Error in scorm_set_value: {e}')
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)

    # Обработка ошибок.
    except Exception as e:
        logger.info(f'Error in scorm_set_value: {e}')
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

# Сохранение данных.
@csrf_exempt
def scorm_commit(request):

    # Проверка корректности метода.
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

    # Ловим ошибки.
    try:

        # Разбираем тело запроса.
        data = json.loads(request.body)
        if settings.DEBUG:
            logger.info(f'Данные для сохранения: {data}')

        # Забираем пользователя и пакет.
        user_id = request.session.get('user_id')
        course_id = request.session.get('course_id')

        # Получение данных о прогрессе пользователя.
        result = Result.objects.filter(employee_id=user_id, course_id=course_id).latest('id')

        # Преобразуем текущий прогресс в словарь.
        progress_data = json.loads(result.progress)

        # Объединяем новые данные с текущими данными о прогрессе.
        for key, value in data.items():
            progress_data[key] = value
        if settings.DEBUG:
            logger.info(f'Итоговые данные для сохранения: {progress_data}')

        # Сохранение обновленных данных.
        result.progress = json.dumps(progress_data)
        result.save()

        # Выдаем сообщение что сохранение выполнено.
        return JsonResponse({'status': 'commit_success'})

    # Отрабатываем отсутствие результата.
    except Result.DoesNotExist:
        return JsonResponse({'status': 'progress_not_found'}, status=404)

    # Отрабатываем ошибки декодирования.
    except json.JSONDecodeError as e:
        logger.info(f'JSON Decode Error in scorm_commit: {e}')
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)

    # Отрабатываем другие ошибки.
    except Exception as e:
        logger.info(f'Error in scorm_commit: {e}')
        return JsonResponse({'status': 'error', 'message': 'Internal server error'}, status=500)


# Завершение курса.
@csrf_exempt
def scorm_finish(request):

    # Проверка корректности метода.
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

    # Ловим ошибки.
    try:

        # Загружаем запрос.
        data = json.loads(request.body)
        user_id = request.session.get('user_id')
        course_id = request.session.get('course_id')

        # Получение данных о прогрессе пользователя.
        result = Result.objects.filter(employee_id=user_id, course_id=course_id).latest('id')

        # Устанавливаем время завершения.
        result.end_date = timezone.now()

        # Cохраняем данные.
        result.save()

        # Отдаем ответ об успешном завершении.
        return JsonResponse({'status': 'finish_success'})

    # Отрабатываем отсутствие результата.
    except Result.DoesNotExist:
        return JsonResponse({'status': 'progress_not_found'}, status=404)

    # Отрабатываем ошибки декодирования.
    except json.JSONDecodeError as e:
        logger.info(f'JSON Decode Error in scorm_finish: {e}')
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)

    # Отрабатываем другие ошибки.
    except Exception as e:
        logger.info(f'Error in scorm_finish: {e}')
        return JsonResponse({'status': 'error', 'message': 'Internal server error'}, status=500)


# Отработчики ошибок.

def scorm_get_last_error(request):
    user_id = request.session.get('user_id')
    course_id = request.session.get('course_id')
    try:
        # Получение данных о прогрессе пользователя.
        result = Result.objects.filter(employee_id=user_id, course_id=course_id).latest('id')

        # Преобразование строки JSON в словарь Python.
        progress_data = json.loads(result.progress)
        error_code = progress_data.get('cmi.error_code', "0")

        return JsonResponse({'error_code': error_code})
    except Exception as e:
        logger.info(f'Error in scorm_get_last_error: {e}')
        return JsonResponse({'status': 'error', 'message': 'Internal server error'}, status=500)

def scorm_get_error_string(request):
    error_code = request.GET.get('error_code', "0")

    error_strings = {
        "0": "No error",
        "101": "General exception",
        "102": "General initialization failure",
        "103": "Already initialized",
        "104": "Content instance terminated",
        "201": "Invalid argument error",
        "202": "Element cannot have children",
        "203": "Element not an array – cannot have count",
        "301": "Not initialized",
        "401": "Not implemented error",
        "402": "Invalid set value, element is a keyword",
        "403": "Element is read only",
        "404": "Element is write only",
        "405": "Incorrect data type",
        # Дополнительные коды ошибок по стандарту SCORM
    }

    error_string = error_strings.get(error_code, "Unknown error")
    return JsonResponse({'error_string': error_string})

def scorm_get_diagnostic(request):
    error_code = request.GET.get('error_code', "0")

    # Расширенное сопоставление кодов ошибок с диагностической информацией
    diagnostic_info = {
        "0": "No diagnostic information",
        "101": "General exception, no specific diagnostic information.",
        "102": "Initialization failed for an unknown reason.",
        "103": "Attempted to re-initialize.",
        "104": "Content terminated without proper initialization.",
        "201": "Invalid argument error, details provided in diagnostic information.",
        "202": "Element cannot have children, violating SCORM data model.",
        "203": "Element not an array, count function is invalid.",
        "301": "SCORM API not initialized.",
        "401": "SCORM API function not implemented.",
        "402": "Invalid set value, element is a keyword and is read-only.",
        "403": "Element is read-only and cannot be modified.",
        "404": "Element is write-only and cannot be read.",
        "405": "Incorrect data type used for value.",
        # Дополнительные коды ошибок и диагностика
    }

    diagnostic = diagnostic_info.get(error_code, "No specific diagnostic information available.")
    return JsonResponse({'diagnostic_info': diagnostic})