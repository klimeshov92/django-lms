
# Create your views here.

from django.conf import settings
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Material, File
from .filters import MaterialFilter, FileFilter
from .forms import MaterialForm, FileForm
from django.shortcuts import render, redirect, reverse, get_object_or_404
from guardian.mixins import PermissionListMixin
from guardian.mixins import PermissionRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin as GPermissionRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.contrib.auth.decorators import permission_required
from guardian.shortcuts import get_perms
from guardian.shortcuts import get_objects_for_user
from learning_path.models import Result
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
from core.filters import EmployeesGroupObjectPermissionFilter, EmployeesObjectPermissionFilter

# Импортируем логи
import logging
# Создаем логгер с именем 'project'
logger = logging.getLogger('project')

# Список материалов.
class MaterialsView(PreviousPageSetMixinL1, PermissionListMixin, ListView):
    # Права доступа
    permission_required = 'materials.view_material'
    # Модель.
    model = Material
    # Поле сортировки.
    ordering = 'name'
    # Шаблон.
    template_name = 'materials.html'
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
            material_id=OuterRef('pk'), employee=self.request.user
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
        self.filterset = MaterialFilter(self.request.GET, queryset, request=self.request)

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
class MaterialView(PreviousPageGetMixinL1, PreviousPageSetMixinL0, PermissionRequiredMixin, DetailView):
    # Права доступа/
    permission_required = 'materials.view_material'
    accept_global_perms = True
    # Модель.
    model = Material
    # Шаблон.
    template_name = 'material.html'

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
        if Review.objects.filter(type='material', material__pk=self.kwargs.get('pk')).exists():
            reviews_queryset = Review.objects.filter(type='material', material__pk=self.kwargs.get('pk')).order_by('created')
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
        content_type = ContentType.objects.get_for_model(Material)
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
        group_object_permissions_filter = EmployeesGroupObjectPermissionFilter(self.request.GET, queryset=group_object_permissions_queryset, request=self.request)
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
        object_permissions_filter = EmployeesObjectPermissionFilter(self.request.GET, queryset=object_permissions_queryset, request=self.request)
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

# Объект материала.
class MaterialReadView(PreviousPageGetMixinL0, PermissionRequiredMixin, DetailView):
    # Права доступа
    permission_required = 'materials.view_material'
    accept_global_perms = True
    # Модель.
    model = Material
    # Шаблон.
    template_name = 'material_read.html'

    # Проверяем что материал можно читать.
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        result = self.object.results.filter(employee=self.request.user).latest('id')
        if result.status != 'appointed' and result.status != 'in_progress':
            return HttpResponseForbidden('Вам не назначен этот материал!')
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
                return HttpResponseForbidden('Материал заблокирован!')
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
            # Добавляем в контекст.
            context['result'] = result
        # Возвращаем новый набор переменных.
        return context

# Ознакомление.
def confirm_reading(request, pk):
    # Забираем материал.
    material = Material.objects.get(pk=pk)
    # Забираем результат.
    result = material.results.filter(employee=request.user).latest('id')
    # Отмечаем выполлнение.
    if result.status == 'in_progress':
        result.status = 'completed'
        result.end_date = timezone.now()
        result.save()
    # Уходим.
    return redirect('materials:material', pk=pk)

# Создание материала.
class MaterialCreateView(GPermissionRequiredMixin, CreateView):
    # Права доступа.
    permission_required = 'materials.add_material'
    # Форма.
    form_class = MaterialForm
    # Модель.
    model = Material
    # Шаблон.
    template_name = 'material_edit.html'

    def get_permission_object(self):
        # Возвращаем None, так как при создании объект еще не существует
        return None

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
        return reverse('materials:material', kwargs={'pk': self.object.pk})

# Изменение материала.
class MaterialUpdateView(PermissionRequiredMixin, UpdateView):
    # Права доступа
    permission_required = 'materials.change_material'
    accept_global_perms = True
    # Форма.
    form_class = MaterialForm
    # Модель.
    model = Material
    # Шаблон.
    template_name = 'material_edit.html'

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
        return reverse('materials:material', kwargs={'pk': self.object.pk})

# Удаление материала..
class MaterialDeleteView(PermissionRequiredMixin, DeleteView):
    # Права доступа
    permission_required = 'materials.delete_material'
    accept_global_perms = True
    # Модель.
    model = Material
    # Шаблон.
    template_name = 'material_delete.html'

    # Перенаправление после валидации формы.
    def get_success_url(self):
        # Направляем по адресу объектов.
        return reverse('materials:materials')


# Список файлов.
class FilesView(PreviousPageSetMixinL2, PermissionListMixin, ListView):
    # Права доступа
    permission_required = 'materials.view_file'
    # Модель.
    model = File
    # Поле сортировки.
    ordering = 'name'
    # Шаблон.
    template_name = 'files.html'
    # Количество объектов на странице
    paginate_by = 6

    # Переопределяем выборку вью.
    def get_queryset(self):
        # Забираем изначальную выборку вью.
        queryset = super().get_queryset().prefetch_related(
            'categories',
        )
        # Добавляем модель фильтрации в выборку вью.
        self.filterset = FileFilter(self.request.GET, queryset)
        # Возвращаем вью новую выборку.
        return self.filterset.qs

    # Добавляем во вью переменные.
    def get_context_data(self, **kwargs):
        # Забираем изначальный набор переменных.
        context = super().get_context_data(**kwargs)
        # Добавляем фильтрсет.
        context['filterset'] = self.filterset
        # Добавляем базовый адрес.
        context['BASE_URL'] = settings.BASE_URL
        # Возвращаем новый набор переменных.
        return context

# Объект файла.
class FileView(PreviousPageGetMixinL2, PermissionRequiredMixin, DetailView):
    # Права доступа
    permission_required = 'materials.view_file'
    accept_global_perms = True
    # Модель.
    model = File
    # Шаблон.
    template_name = 'file.html'

    # Добавляем во вью переменные.
    def get_context_data(self, **kwargs):
        # Забираем изначальный набор переменных.
        context = super().get_context_data(**kwargs)
        # Добавляем базовый адрес.
        context['BASE_URL'] = settings.BASE_URL
        # Возвращаем новый набор переменных.
        return context

# Создание файла.
class FileCreateView(GPermissionRequiredMixin, CreateView):
    # Права доступа.
    permission_required = 'materials.add_file'
    # Форма.
    form_class = FileForm
    # Модель.
    model = File
    # Шаблон.
    template_name = 'file_edit.html'

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
        return reverse('materials:file', kwargs={'pk': self.object.pk})

# Изменение файла.
class FileUpdateView(PermissionRequiredMixin, UpdateView):
    # Права доступа
    permission_required = 'materials.change_file'
    accept_global_perms = True
    # Форма.
    form_class = FileForm
    # Модель.
    model = File
    # Шаблон.
    template_name = 'file_edit.html'

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
        return reverse('materials:file', kwargs={'pk': self.object.pk})

# Удаление файла.
class FileDeleteView(PermissionRequiredMixin, DeleteView):
    # Права доступа
    permission_required = 'materials.delete_file'
    accept_global_perms = True
    # Модель.
    model = File
    # Шаблон.
    template_name = 'file_delete.html'

    # Перенаправление после валидации формы.
    def get_success_url(self):
        # Направляем по адресу объектов.
        return reverse('materials:files')
