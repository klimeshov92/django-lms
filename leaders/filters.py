# Импорт моделей фильтрации.
from django_filters import FilterSet, ModelMultipleChoiceFilter, ChoiceFilter, DateFilter, CharFilter, BooleanFilter
# Импорт виджетов select2.
from django_select2.forms import Select2MultipleWidget, Select2Widget
# Импорт моделей.
from core.models import Employee, EmployeesGroup
from materials.models import Material
from courses.models import Course
from testing.models import Test
from events.models import Event
from .models import Transaction
# Импорт форм.
from django import forms
# Импорт каунта.
from django.db.models import Count, Q, F
# Импорт прав.
from guardian.shortcuts import get_objects_for_user

# Фильтрация результатов.
class LeadersFilter(FilterSet):
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
    # Фильтрация по типу.
    type = ChoiceFilter(
        choices=Transaction.TYPES,
        widget=Select2Widget
    )
    # Фильтрация по материалу.
    material = ModelMultipleChoiceFilter(
        field_name='material',
        queryset=Material.objects.all(),
        widget=Select2MultipleWidget()
    )
    # Фильтрация по курсу.
    course = ModelMultipleChoiceFilter(
        field_name='course',
        queryset=Course.objects.all(),
        widget=Select2MultipleWidget()
    )
    # Фильтрация по тесту.
    test = ModelMultipleChoiceFilter(
        field_name='test',
        queryset=Test.objects.all(),
        widget=Select2MultipleWidget()
    )
    # Фильтрация по мероприятию.
    event = ModelMultipleChoiceFilter(
        field_name='event',
        queryset=Event.objects.all(),
        widget=Select2MultipleWidget()
    )
    # Фильтрация по дате завершения "до".
    created_lte = DateFilter(
        field_name='created',
        lookup_expr="lte",
        label='Начислены до',
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
    # Фильтрация по дате завершения "после".
    created_gte = DateFilter(
        field_name='created',
        lookup_expr="gte",
        label='Начислены после',
        widget=forms.DateInput(attrs={'type': 'date'}),
    )

