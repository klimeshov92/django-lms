from django.shortcuts import render

# Create your views here.

# Импорт настроек.
from django.conf import settings
# Импорт моделей вью.
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
# Импорт моделей ядра.
from .models import Transaction
from core.models import Employee
# Импорт модели фильтров.
from .filters import LeadersFilter
# Импорт рендера, перенаправления, генерации адреса и других урл функций.
from django.shortcuts import render, redirect, reverse, get_object_or_404
# Импорт простого ответа.
from django.http import HttpResponse, HttpResponseServerError
# Проверка прав доступа для классов.
from guardian.mixins import PermissionListMixin
from guardian.mixins import PermissionRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin as GPermissionRequiredMixin
# Импорт декораторов проверки прав.
from django.contrib.auth.decorators import permission_required, login_required
# Импорт времени с учетом таймзоны.
from django.utils import timezone
from django.db.models import OuterRef, Subquery, Prefetch
from django.db.models import F
from django.db.models import Case, When, Value
# Импорт суммирования значений.
from django.db.models import FilteredRelation, Q, Sum
from django.db.models.functions import Cast, Coalesce
# Импорт пагинатора
from django.core.paginator import Paginator
# Миксины.
from core.mixins import PreviousPageGetMixinL0, PreviousPageSetMixinL0, PreviousPageGetMixinL1, PreviousPageSetMixinL1, PreviousPageGetMixinL2, PreviousPageSetMixinL2

# Импортируем логи
import logging
# Создаем логгер с именем 'project'
logger = logging.getLogger('project')

# Список сотрудников.
class LeadersView(PermissionListMixin, ListView):
    # Права доступа
    permission_required = 'leaders.view_transaction'
    # Модель.
    model = Transaction
    # Поле сортировки.
    ordering = 'created'
    # Шаблон.
    template_name = 'leaders.html'

    # Переопределяем выборку вью.
    def get_queryset(self):
        # Забираем изначальную выборку вью.
        queryset = super().get_queryset()
        # Добавляем модель фильтрации в выборку вью.
        self.filterset = LeadersFilter(self.request.GET, queryset, request=self.request)
        # Возвращаем вью новую выборку.
        return self.filterset.qs

    # Добавляем во вью переменные.
    def get_context_data(self, **kwargs):
        # Забираем изначальный набор переменных.
        context = super().get_context_data(**kwargs)
        # Добавляем фильтрсет.
        context['filterset'] = self.filterset
        # Заменяем кверисет на лидеров.
        # Забираем связанный список сотрудников и айди.
        employees_list = self.filterset.qs.values_list('employee', flat=True).distinct()
        employees = Employee.objects.filter(id__in=employees_list)
        # Аннотируем суммой бонусов.
        leaders = employees.annotate(
            total_bonus=Coalesce(Sum('transactions__bonus', filter=Q(transactions__in=self.filterset.qs)), 0)
        ).order_by('-total_bonus')
        context['leaders_list'] = leaders
        # Если участники есть.
        if leaders:
            # Добавляем пагинатор
            paginator = Paginator(leaders, 10)
            page_number = self.request.GET.get('page')
            page_obj = paginator.get_page(page_number)
        # Если нет...
        else:
            # Задаем пустую переменную для проверки в шаблоне.
            page_obj = None
        # Добавляем во вью.
        context['page_obj'] = page_obj
        # Возвращаем переменные.
        return context