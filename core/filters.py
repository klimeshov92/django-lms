# Импорт моделей фильтрации.
from django_filters import FilterSet, DateTimeFilter, ChoiceFilter, ModelMultipleChoiceFilter, MultipleChoiceFilter
# Импорт форм.
from django import forms
# Импорт виджетов select2.
from django_select2.forms import Select2MultipleWidget, Select2Widget
# Импорт моделей.
from .models import EmployeeExcelImport, Category, EmployeesGroup, Employee, Organization, Subdivision, Position
from django.db.models import Count

# Фильтрация импортов.
class EmployeeExcelImportFilter(FilterSet):
    # Фильтрация по типу.
    type = ChoiceFilter(
        choices=EmployeeExcelImport.TYPES,
        widget=Select2Widget
    )
    # Фильтрация по категории.
    сategory = ModelMultipleChoiceFilter(
        field_name='categories',
        queryset=Category.objects.annotate(num_employee_excel_imports=Count('employee_excel_imports'))
        .filter(num_employee_excel_imports__gt=0).order_by('name'),
        widget=Select2MultipleWidget()
    )
    # Фильтрация по имени.
    name = ModelMultipleChoiceFilter(
        queryset=EmployeeExcelImport.objects.all(),
        to_field_name='name',
        lookup_expr='icontains',
        widget=Select2MultipleWidget()
    )
    # Фильтрация по дате загрузки "до".
    created_lte = DateTimeFilter(
        field_name='created',
        lookup_expr="lte",
        label='Дата и время создания до',
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})
    )
    # Фильтрация по дате загрузки "после".
    created_gte = DateTimeFilter(
        field_name='created',
        lookup_expr="gte",
        label='Дата и время создания после',
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})
    )

# Фильтрация категорий.
class CategoryFilter(FilterSet):
    # Фильтрация по имени.
    name = ModelMultipleChoiceFilter(
        queryset=Category.objects.all(),
        to_field_name='name',
        lookup_expr='icontains',
        widget=Select2MultipleWidget()
    )

# Фильтрация импортов.
class GroupFilter(FilterSet):
    # Фильтрация по категории.
    сategory = ModelMultipleChoiceFilter(
        field_name='categories',
        queryset=Category.objects.annotate(num_groups=Count('employees_groups'))
        .filter(num_groups__gt=0).order_by('name'),
        widget=Select2MultipleWidget()
    )
    # Фильтрация по имени.
    name = ModelMultipleChoiceFilter(
        queryset=EmployeesGroup.objects.all(),
        to_field_name='name',
        lookup_expr='icontains',
        widget=Select2MultipleWidget()
    )

# Фильтрация сотрудников.
class EmployeeFilter(FilterSet):
    # Фильтрация по группе.
    groups = ModelMultipleChoiceFilter(
        field_name='groups',
        queryset=EmployeesGroup.objects.all(),
        widget=Select2MultipleWidget()
    )
    # Фильтрация по фамилии.
    last_name = ModelMultipleChoiceFilter(
        queryset=Employee.objects.all(),
        to_field_name='last_name',
        lookup_expr='icontains',
        widget=Select2MultipleWidget()
    )

# Фильтрация сотрудников.
class GroupsEmployeeFilter(FilterSet):
    # Фильтрация по группе.
    groups = ModelMultipleChoiceFilter(
        field_name='groups',
        queryset=EmployeesGroup.objects.all(),
        widget=Select2MultipleWidget()
    )
    # Фильтрация по фамилии.
    last_name = ModelMultipleChoiceFilter(
        queryset=Employee.objects.all(),
        to_field_name='last_name',
        lookup_expr='icontains',
        widget=Select2MultipleWidget()
    )

# Фильтрация организаций.
class OrganizationFilter(FilterSet):
    # Фильтрация по названию.
    legal_name = ModelMultipleChoiceFilter(
        queryset=Organization.objects.all(),
        to_field_name='legal_name',
        lookup_expr='icontains',
        widget=Select2MultipleWidget()
    )
    # Фильтрация по ИНН.
    tin = ModelMultipleChoiceFilter(
        queryset=Organization.objects.all(),
        to_field_name='tin',
        lookup_expr='icontains',
        widget=Select2MultipleWidget()
    )

# Фильтрация подразделений.
class SubdivisionFilter(FilterSet):
    # Фильтрация по названию.
    name = ModelMultipleChoiceFilter(
        queryset=Subdivision.objects.all(),
        to_field_name='name',
        lookup_expr='icontains',
        widget=Select2MultipleWidget()
    )
    # Фильтрация по организации.
    organization = ModelMultipleChoiceFilter(
        queryset=Subdivision.objects.all(),
        to_field_name='organization',
        lookup_expr='icontains',
        widget=Select2MultipleWidget()
    )
    # Фильтрация по родительскому подразделению.
    parent_subdivision = ModelMultipleChoiceFilter(
        queryset=Subdivision.objects.all(),
        to_field_name='parent_subdivision',
        lookup_expr='icontains',
        widget=Select2MultipleWidget()
    )

# Фильтрация должностей.
class PositionFilter(FilterSet):
    # Фильтрация по названию.
    name = ModelMultipleChoiceFilter(
        queryset=Position.objects.all(),
        to_field_name='name',
        lookup_expr='icontains',
        widget=Select2MultipleWidget()
    )

# Фильтрация прав.
class EmployeesGroupObjectPermissionFilter(FilterSet):
    # Фильтрация по группе.
    group = ModelMultipleChoiceFilter(
        label='Группа',
        field_name='group',
        queryset=EmployeesGroup.objects.all(),
        widget=Select2MultipleWidget()
    )

# Фильтрация прав.
class EmployeesObjectPermissionFilter(FilterSet):
    # Фильтрация по группе.
    user = ModelMultipleChoiceFilter(
        label='Сотрудник',
        field_name='user',
        queryset=Employee.objects.all(),
        widget=Select2MultipleWidget()
    )