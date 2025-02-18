# Импорт моделей фильтрации.
from django_filters import FilterSet, ModelMultipleChoiceFilter, ChoiceFilter, DateTimeFilter, DateFilter
# Импорт виджетов select2.
from django_select2.forms import Select2MultipleWidget, Select2Widget
# Импорт моделей.
from core.models import Category
from .models import Work
# Импорт форм.
from django import forms
# Импорт каунта.
from django.db.models import Count
# Импорт прав.
from guardian.shortcuts import get_objects_for_user
# Импорт моделей.
from core.models import Category, Employee, EmployeesGroup
from learning_path.models import Assignment

# Фильтрация материалов.
class WorkFilter(FilterSet):
    # Фильтрация по категории.
    сategory = ModelMultipleChoiceFilter(
        field_name='categories',
        queryset=Category.objects.annotate(num_materials=Count('works'))
        .filter(num_materials__gt=0).order_by('name'),
        widget=Select2MultipleWidget()
    )
    # Фильтрация по имени.
    name = ModelMultipleChoiceFilter(
        queryset=Work.objects.none(),
        to_field_name='name',
        lookup_expr='icontains',
        widget=Select2MultipleWidget()
    )

    # Фильрация выборов.
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters['name'].queryset = get_objects_for_user(
            self.request.user,
            'view_work',
            klass=Work
        ).order_by('name')

    # Фильтрация по статусу
    latest_result_status = ChoiceFilter(
        field_name='latest_result_status',
        choices=[
            ('appointed', 'Назначено'),
            ('in_progress', 'В процессе'),
            ('completed', 'Пройдено'),
            ('failed', 'Провалено'),
        ],
        widget=Select2Widget,
        label='Статус'
    )

# Фильтрация результатов.
class WorkSupervisingFilter(FilterSet):
    # Фильтрация по сотруднику.
    employee = ModelMultipleChoiceFilter(
        field_name='employee',
        queryset=Employee.objects.all(),
        widget=Select2MultipleWidget()
    )
    # Фильтрация по группе.
    employee__groups = ModelMultipleChoiceFilter(
        field_name='employee__groups',
        queryset=EmployeesGroup.objects.all(),
        widget=Select2MultipleWidget()
    )
    # Фильтрация по назначению.
    assignment = ModelMultipleChoiceFilter(
        field_name='assignment',
        queryset=Assignment.objects.all(),
        widget=Select2MultipleWidget()
    )
    # Фильтрация по статусу
    status = ChoiceFilter(
        field_name='status',
        choices=[
            ('appointed', 'Назначено'),
            ('in_progress', 'В процессе'),
            ('on_review', 'На проверке'),
            ('completed', 'Пройдено'),
            ('failed', 'Провалено'),
        ],
        widget=Select2Widget,
    )
    # Фильтрация по дате завершения "до".
    planned_end_date_lte = DateFilter(
        field_name='planned_end_date',
        lookup_expr="lte",
        label='Планируемая дата завершения до',
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
    # Фильтрация по дате завершения "после".
    planned_end_date_gte = DateFilter(
        field_name='planned_end_date',
        lookup_expr="gte",
        label='Планируемая дата завершения после',
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
