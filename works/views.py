
# Create your views here.

from django.conf import settings
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Work
from .filters import WorkFilter, WorkSupervisingFilter
from .forms import WorkForm, ExecutorReportForm, WorkReviewForm, ExecutorReportNoReviewForm
from django.shortcuts import render, redirect, reverse, get_object_or_404
from guardian.mixins import PermissionListMixin
from guardian.mixins import PermissionRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin as GPermissionRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.contrib.auth.decorators import permission_required
from guardian.shortcuts import get_perms
from guardian.shortcuts import get_objects_for_user
from learning_path.models import Result, WorkReview
from django.http import HttpResponseForbidden
from django.db.models import OuterRef, Subquery
from django.db.models.functions import Coalesce
from django.db.models import F
from django.db.models import Case, When, Value
from django.shortcuts import render
from django.db import models
from django.db.models import Sum
from core.mixins import PreviousPageGetMixinL0, PreviousPageSetMixinL0, \
    PreviousPageGetMixinL1, PreviousPageSetMixinL1, \
    PreviousPageGetMixinL2, PreviousPageSetMixinL2
from django.core.paginator import Paginator
from reviews.models import Review
from core.models import EmployeesGroupObjectPermission, EmployeesObjectPermission
from reviews.filters import ObjectsReviewFilter
from core.filters import EmployeesGroupObjectPermissionGroupsFilter, EmployeesObjectPermissionEmployeesFilter
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

# Импортируем логи
import logging
# Создаем логгер с именем 'project'
logger = logging.getLogger('project')

# Список работ.
class WorksView(LoginRequiredMixin, PreviousPageSetMixinL1, PermissionListMixin, ListView):
    # Права доступа
    permission_required = 'works.view_work'
    # Модель.
    model = Work
    # Поле сортировки.
    ordering = 'name'
    # Шаблон.
    template_name = 'works.html'
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
            work_id=OuterRef('pk'), employee=self.request.user
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
        self.filterset = WorkFilter(self.request.GET, queryset, request=self.request)

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

# Объект работы.
class WorkView(LoginRequiredMixin, PreviousPageGetMixinL1, PreviousPageSetMixinL0, PermissionRequiredMixin, DetailView):
    # Права доступа/
    permission_required = 'works.view_work'
    accept_global_perms = True
    # Модель.
    model = Work
    # Шаблон.
    template_name = 'work.html'

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
                # Добавляем задачи.
                now_blocking_tasks = [
                    blocking_task for blocking_task in blocking_tasks
                    if blocking_task.results.filter(employee=self.request.user).exists() and blocking_task.results.filter(employee=self.request.user).latest('id').status != 'completed'
                ]
                # Блокируем если есть задачи.
                if now_blocking_tasks:
                    blocked = True
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
        if Review.objects.filter(type='work', work__pk=self.kwargs.get('pk')).exists():
            reviews_queryset = Review.objects.filter(type='work', work__pk=self.kwargs.get('pk')).order_by('created')
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
        content_type = ContentType.objects.get_for_model(Work)
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

# Объект работы.
class WorkReadView(LoginRequiredMixin, PreviousPageGetMixinL0, PermissionRequiredMixin, DetailView):
    # Права доступа
    permission_required = 'works.view_work'
    accept_global_perms = True
    # Модель.
    model = Work
    # Шаблон.
    template_name = 'work_read.html'

    # Проверяем что материал можно читать.
    def dispatch(self, request, *args, **kwargs):
        object = self.get_object()
        result = object.results.filter(employee=self.request.user).latest('id')
        # Все для блокировки, если есть результат связанный с задачей.
        if result.learning_task and result.learning_task.blocking_tasks:
            blocking_tasks = result.learning_task.blocking_tasks.all()
            # Добавляем задачи.
            now_blocking_tasks = [
                blocking_task for blocking_task in blocking_tasks
                if blocking_task.results.filter(employee=self.request.user).exists() and blocking_task.results.filter(employee=self.request.user).latest('id').status != 'completed'
            ]
            # Блокируем если есть задачи.
            if now_blocking_tasks:
                return HttpResponseForbidden('Работа заблокирована!')
        # Продолжить обработку запроса
        return super().dispatch(request, *args, **kwargs)

    # Добавляем во вью переменные.
    def get_context_data(self, **kwargs):
        # Забираем изначальный набор переменных.
        context = super().get_context_data(**kwargs)
        # Забираем результат.
        if self.object.results.filter(employee=self.request.user):
            result = self.object.results.filter(employee=self.request.user).latest('id')
            # Меняем статус.
            if result.status == 'appointed':
                result.status = 'in_progress'
                result.start_date = timezone.now()
                result.save()
            # Проверяем, является ли текущий пользователь среди супервизоров.
            supervising = result.supervising.all()
            user_is_supervisor = supervising.filter(supervisor=self.request.user).exists()
            user_is_executor = result.employee == self.request.user
            # Добавляем эту информацию в контекст
            context['result'] = result
            context['user_is_supervisor'] = user_is_supervisor
            context['user_is_executor'] = user_is_executor
        # Возвращаем новый набор переменных.
        return context

# Объект работы.
class WorkResultReadView(LoginRequiredMixin, PreviousPageGetMixinL0, PermissionRequiredMixin, DetailView):
    # Права доступа
    permission_required = 'learning_path.view_result'
    accept_global_perms = True
    # Модель.
    model = Result
    # Шаблон.
    template_name = 'work_result_read.html'

    # Проверяем, что работу можно проверять.
    def dispatch(self, request, *args, **kwargs):
        result = self.get_object()
        if settings.DEBUG:
            logger.info(f"Отчеты проверяющих: {result.reviews}")
        # Для исполнителя.
        if result.employee == self.request.user:
            # Все для блокировки, если есть результат связанный с задачей.
            if result.learning_task and result.learning_task.blocking_tasks:
                blocking_tasks = result.learning_task.blocking_tasks.all()
                # Добавляем задачи.
                now_blocking_tasks = [
                    blocking_task for blocking_task in blocking_tasks
                    if blocking_task.results.filter(employee=self.request.user).exists() and blocking_task.results.filter(employee=self.request.user).latest('id').status != 'completed'
                ]
                # Блокируем если есть задачи.
                if now_blocking_tasks:
                    return HttpResponseForbidden('Работа заблокирована!')
        # Продолжить обработку запроса/
        return super().dispatch(request, *args, **kwargs)

    # Добавляем во вью переменные.
    def get_context_data(self, **kwargs):
        # Забираем изначальный набор переменных.
        context = super().get_context_data(**kwargs)
        # Проверяем, является ли текущий пользователь среди супервизоров.
        supervising = self.object.supervising.all()
        user_is_supervisor = supervising.filter(supervisor=self.request.user).exists()
        user_is_executor = self.object.employee == self.request.user
        # Добавляем эту информацию в контекст
        context['user_is_supervisor'] = user_is_supervisor
        context['user_is_executor'] = user_is_executor
        # Возвращаем новый набор переменных.
        return context

# Создание работы.
class WorkCreateView(LoginRequiredMixin, GPermissionRequiredMixin, CreateView):
    # Права доступа.
    permission_required = 'works.add_work'
    # Форма.
    form_class = WorkForm
    # Модель.
    model = Work
    # Шаблон.
    template_name = 'work_edit.html'

    # Заполнение полей данными.
    def get_initial(self):
        # Забираем изначальный набор.
        initial = super().get_initial()
        # Добавляем создателя: юзера отправившего запрос.
        initial["creator"] = self.request.user
        # Возвращаем значения в форму.
        return initial

    # Перенаправление после валидации формы.
    def get_success_url(self):
        # Направляем по адресу объекта.
        return reverse('works:work', kwargs={'pk': self.object.pk})

# Изменение работы.
class WorkUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    # Права доступа
    permission_required = 'works.change_work'
    accept_global_perms = True
    # Форма.
    form_class = WorkForm
    # Модель.
    model = Work
    # Шаблон.
    template_name = 'work_edit.html'

    # Заполнение полей данными.
    def get_initial(self):
        # Забираем изначальный набор.
        initial = super().get_initial()
        # Добавляем создателя: юзера отправившего запрос.
        initial["creator"] = self.request.user
        # Возвращаем значения в форму.
        return initial

    # Перенаправление после валидации формы.
    def get_success_url(self):
        # Направляем по адресу объекта.
        return reverse('works:work', kwargs={'pk': self.object.pk})

# Удаление работы..
class WorkDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    # Права доступа
    permission_required = 'works.delete_work'
    accept_global_perms = True
    # Модель.
    model = Work
    # Шаблон.
    template_name = 'work_delete.html'

    # Перенаправление после валидации формы.
    def get_success_url(self):
        # Направляем по адресу объектов.
        return reverse('works:works')

# Список работ на контроле.
class WorksSupervising(LoginRequiredMixin, PreviousPageSetMixinL1, PermissionListMixin, ListView):
    # Права доступа
    permission_required = 'learning_path.view_result'
    # Модель.
    model = Result
    # Поле сортировки.
    ordering = '-planned_end_date'
    # Шаблон.
    template_name = 'results_supervising.html'
    # Количество объектов на странице
    paginate_by = 6

    # Переопределяем выборку вью.
    def get_queryset(self):

        # Забираем изначальную выборку вью.
        queryset = super().get_queryset()
        # Забираем только те, что под контролем
        results_supervising_queryset = queryset.filter(
            supervising__supervisor=self.request.user,
            work__isnull=False
        )
        results_supervising_queryset = results_supervising_queryset.select_related('work')
        # Добавляем модель фильтрации в выборку вью.
        self.filterset = WorkSupervisingFilter(self.request.GET, results_supervising_queryset, request=self.request)

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

# Создание отчета исполнителя.
class ExecutorReportUpdateView(LoginRequiredMixin, UpdateView):
    # Форма.
    form_class = ExecutorReportForm
    # Модель.
    model = Result
    # Шаблон.
    template_name = 'executor_report_edit.html'

    def get_form_class(self):
        # Получаем текущий объект.
        object = self.get_object()

        # Динамически выбираем форму в зависимости от необходимости проверки
        if object.work.require_review:
            return ExecutorReportForm
        else:
            return ExecutorReportNoReviewForm

    # Проверяем что работу можно читать.
    def dispatch(self, request, *args, **kwargs):
        result = self.get_object()
        if result.employee == self.request.user:
            if result.work.require_review and result.status != 'appointed' and result.status != 'in_progress':
                return HttpResponseForbidden('Нельзя написать, когда работа в данном статусе!')

            # Все для блокировки, если есть результат связанный с задачей.
            if result.learning_task and result.learning_task.blocking_tasks:
                blocking_tasks = result.learning_task.blocking_tasks.all()
                # Добавляем задачи.
                now_blocking_tasks = [
                    blocking_task for blocking_task in blocking_tasks
                    if blocking_task.results.filter(employee=self.request.user).exists() and blocking_task.results.filter(
                        employee=self.request.user).latest('id').status != 'completed'
                ]
                # Блокируем если есть задачи.
                if now_blocking_tasks:
                    return HttpResponseForbidden('Работа заблокирована!')
        else:
            return HttpResponseForbidden('Вам не назначена эта работа!')
        # Продолжить обработку запроса
        return super().dispatch(request, *args, **kwargs)

    # Заполнение полей данными.
    def get_initial(self):
        # Забираем изначальный набор.
        initial = super().get_initial()
        # Добавляем дату.
        initial["executor_report_date"] = timezone.now()
        # Возвращаем значения в форму.
        return initial

    # Перенаправление после валидации формы.
    def get_success_url(self):
        # Направляем по адресу объекта.
        return reverse('works:work_read', kwargs={'pk': self.object.work.pk})

# Создание отчета контролера.
class WorkReviewCreateView(LoginRequiredMixin, CreateView):
    # Форма.
    form_class = WorkReviewForm
    # Модель.
    model = WorkReview
    # Шаблон.
    template_name = 'work_review_edit.html'

    # Проверяем что работу можно читать.
    def dispatch(self, request, *args, **kwargs):
        # Проверяем, является ли текущий пользователь среди супервизоров.
        result = Result.objects.get(pk=self.kwargs.get('pk'))
        supervising = result.supervising.all()
        user_is_supervisor = supervising.filter(supervisor=self.request.user).exists()
        if not user_is_supervisor:
            return HttpResponseForbidden('Проверять работу может только контролер!')
        # Продолжить обработку запроса
        return super().dispatch(request, *args, **kwargs)

    # Заполнение полей данными.
    def get_initial(self):
        # Забираем изначальный набор.
        initial = super().get_initial()
        # Добавляем создателя: юзера отправившего запрос.
        initial["reviewer"] = self.request.user
        # Добавляем результат.
        result = Result.objects.get(pk=self.kwargs.get('pk'))
        initial["result"] = result
        logger.info(f'result: {initial["result"]}')
        # Возвращаем значения в форму.
        return initial

    # Перенаправление после валидации формы.
    def get_success_url(self):
        # Направляем по адресу объекта.
        return reverse('works:work_result_read', kwargs={'pk': self.object.result.pk})

# Обновление отчета контролера.
class WorkReviewUpdateView(LoginRequiredMixin, UpdateView):
    # Форма.
    form_class = WorkReviewForm
    # Модель.
    model = WorkReview
    # Шаблон.
    template_name = 'work_review_edit.html'

    # Проверяем что работу можно читать.
    def dispatch(self, request, *args, **kwargs):
        # Проверяем, является ли текущий пользователь среди супервизоров.
        object = self.get_object()
        result = object.result
        supervising = result.supervising.all()
        user_is_supervisor = supervising.filter(supervisor=self.request.user).exists()
        if not user_is_supervisor:
            return HttpResponseForbidden('Проверять работу может только контролер!')
        # Продолжить обработку запроса
        return super().dispatch(request, *args, **kwargs)

    # Заполнение полей данными.
    def get_initial(self):
        # Забираем изначальный набор.
        initial = super().get_initial()
        # Добавляем создателя: юзера отправившего запрос.
        initial["reviewer"] = self.request.user
        # Возвращаем значения в форму.
        return initial

    # Перенаправление после валидации формы.
    def get_success_url(self):
        # Направляем по адресу объекта.
        return reverse('works:work_result_read', kwargs={'pk': self.object.result.pk})