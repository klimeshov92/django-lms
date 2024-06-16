# Импорт моделей фильтрации.
from django_filters import FilterSet, ModelMultipleChoiceFilter, ChoiceFilter, DateTimeFilter
# Импорт виджетов select2.
from django_select2.forms import Select2MultipleWidget, Select2Widget
# Импорт моделей.
from core.models import Category, Employee, EmployeesGroup
from .models import Event
# Импорт форм.
from django import forms
# Импорт каунта.
from django.db.models import Count
# Импорт прав.
from guardian.shortcuts import get_objects_for_user


# Фильтрация материалов.
class EventFilter(FilterSet):

    # Фильтрация по категории.
    сategory = ModelMultipleChoiceFilter(
        field_name='categories',
        queryset=Category.objects.annotate(num_events=Count('events'))
        .filter(num_events__gt=0).order_by('name'),
        widget=Select2MultipleWidget()
    )
    # Фильтрация по имени.
    name = ModelMultipleChoiceFilter(
        queryset=Event.objects.none(),
        to_field_name='name',
        lookup_expr='icontains',
        widget=Select2MultipleWidget()
    )

    # Фильрация выборов.
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters['name'].queryset = get_objects_for_user(
            self.request.user,
            'view_event',
            klass=Event
        ).order_by('name')

    # Фильтрация по статусу
    latest_result_status = ChoiceFilter(
        field_name='latest_result_status',
        choices=[
        ('registered', 'Зарегестрирован'),
        ('refused', 'Отказался'),
        ('present', 'Присутствовал'),
        ('absent', 'Отсутствовал'),
        ],
        widget=Select2Widget,
        label='Присутствие'
    )
    # Фильтрация по дате и времени начала "до".
    date_lte = DateTimeFilter(
        field_name='date',
        lookup_expr="lte",
        label='Дата до',
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
    # Фильтрация по дате и времени начала "после".
    date_gte = DateTimeFilter(
        field_name='date',
        lookup_expr="gte",
        label='Дата после',
        widget=forms.DateInput(attrs={'type': 'date'}),
    )

# Фильтрация участников.
class ParticipantsFilter(FilterSet):
    # Фильтрация по сотруднику.
    employee = ModelMultipleChoiceFilter(
        field_name='employee',
        queryset=Employee.objects.none(),
        widget=Select2MultipleWidget()
    )
    # Фильтрация по группе.
    employee__groups = ModelMultipleChoiceFilter(
        field_name='employee__groups',
        queryset=EmployeesGroup.objects.none(),
        widget=Select2MultipleWidget()
    )
    # Фильрация выборов.
    def __init__(self, *args, **kwargs):
        event = kwargs.pop('event', None)
        super().__init__(*args, **kwargs)
        self.filters['employee'].queryset = event.participants_group.user_set.all()
        self.filters['employee__groups'].queryset = EmployeesGroup.objects.filter(user__in=event.participants_group.user_set.all()).distinct()