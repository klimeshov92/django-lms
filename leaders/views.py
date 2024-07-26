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
from django.db.models import OuterRef, Subquery, Prefetch, Count
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

        # Получаем всех сотрудников, участвующих в транзакциях.
        all_employees_list = queryset.values_list('employee', flat=True).distinct()
        all_employees = Employee.objects.filter(id__in=all_employees_list)

        # Аннотируем суммой бонусов для всех сотрудников.
        self.absolute_leaders = all_employees.annotate(
            total_bonus=Coalesce(Sum('transactions__bonus', filter=Q(transactions__in=queryset)), 0)
        ).order_by('-total_bonus')

        # Добавляем ранг.
        rank = 1
        for leader in self.absolute_leaders:
            leader.total_rank = rank
            rank += 1

        # Добавляем модель фильтрации в выборку вью.
        self.filterset = LeadersFilter(self.request.GET, queryset, request=self.request)

        # Возвращаем вью новую выборку и абсолютных лидеров.
        return self.filterset.qs

    # Добавляем во вью переменные.
    def get_context_data(self, **kwargs):
        # Забираем изначальный набор переменных.
        context = super().get_context_data(**kwargs)
        # Добавляем фильтрсет.
        context['filterset'] = self.filterset

        # Аннотируем суммой транзакций для фильтрованных лидеров.
        leaders = self.absolute_leaders.filter(
            id__in=self.filterset.qs.values_list('employee', flat=True).distinct()
        ).annotate(
            filter_bonus=Coalesce(Sum('transactions__bonus', filter=Q(transactions__in=self.filterset.qs)), 0)
        ).order_by('-total_bonus')

        # Присваиваем ранг каждому лидеру для filter_bonus.
        rank = 1
        previous_filter_bonus = None
        for leader in leaders:
            if previous_filter_bonus is not None and leader.filter_bonus == previous_filter_bonus:
                leader.filter_rank = previous_filter_rank
            else:
                leader.filter_rank = rank
                rank += 1

            previous_filter_bonus = leader.filter_bonus
            previous_filter_rank = leader.filter_rank

        # Присваиваем ранг каждому лидеру для total_bonus.
        rank = 1
        previous_total_bonus = None
        for leader in leaders:
            if previous_total_bonus is not None and leader.total_bonus == previous_total_bonus:
                leader.total_rank = previous_total_rank
            else:
                leader.total_rank = rank
                rank += 1

            previous_total_bonus = leader.total_bonus
            previous_total_rank = leader.total_rank

        context['leaders'] = leaders

        # Добавляем пагинатор
        paginator = Paginator(leaders, 10)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj

        return context