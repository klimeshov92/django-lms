# Импорт моделей фильтрации.
from django_filters import FilterSet, ModelMultipleChoiceFilter, ChoiceFilter, DateFilter, CharFilter, BooleanFilter
# Импорт виджетов select2.
from django_select2.forms import Select2MultipleWidget, Select2Widget
# Импорт моделей.
from core.models import Category, Employee, EmployeesGroup
from materials.models import Material
from courses.models import Course
from testing.models import Test
from events.models import Event
from .models import LearningTask, LearningPath, Result, Assignment, LearningComplex
# Импорт форм.
from django import forms
# Импорт каунта.
from django.db.models import Count, Q, F
# Импорт прав.
from guardian.shortcuts import get_objects_for_user
# Сабквери.
from django.db.models import OuterRef, Subquery


# Фильтрация комплексных программ.
class LearningComplexFilter(FilterSet):
    # Фильтрация по категории.
    сategory = ModelMultipleChoiceFilter(
        field_name='categories',
        queryset=Category.objects.annotate(num_learning_complexs=Count('learning_complexs'))
        .filter(num_learning_complexs__gt=0).order_by('name'),
        widget=Select2MultipleWidget()
    )
    # Фильтрация по имени.
    name = ModelMultipleChoiceFilter(
        queryset=LearningComplex.objects.none(),
        to_field_name='name',
        lookup_expr='icontains',
        widget=Select2MultipleWidget()
    )
    # Фильрация выборов.
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters['name'].queryset = get_objects_for_user(
            self.request.user,
            'view_learningcomplex',
            klass=LearningComplex
        )

# Фильтрация траекторий.
class LearningPathFilter(FilterSet):
    # Фильтрация по категории.
    сategory = ModelMultipleChoiceFilter(
        field_name='categories',
        queryset=Category.objects.annotate(num_learning_paths=Count('learning_paths'))
        .filter(num_learning_paths__gt=0).order_by('name'),
        widget=Select2MultipleWidget()
    )
    # Фильтрация по имени.
    name = ModelMultipleChoiceFilter(
        queryset=LearningPath.objects.none(),
        to_field_name='name',
        lookup_expr='icontains',
        widget=Select2MultipleWidget()
    )

    # Фильрация выборов.
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters['name'].queryset = get_objects_for_user(
            self.request.user,
            'view_learningpath',
            klass=LearningPath
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

# Фильтрация назначений
class AssignmentFilter(FilterSet):
    # Фильтрация по категории.
    сategory = ModelMultipleChoiceFilter(
        field_name='categories',
        queryset=Category.objects.annotate(num_groups=Count('assignments'))
        .filter(num_groups__gt=0).order_by('name'),
        widget=Select2MultipleWidget()
    )

    # Фильтрация по группе.
    group = ModelMultipleChoiceFilter(
        field_name='group',
        queryset=EmployeesGroup.objects.all(),
        widget=Select2MultipleWidget()
    )

    # Фильтрация по комплексу.
    learning_complex = ModelMultipleChoiceFilter(
        field_name='learning_complex',
        queryset=LearningComplex.objects.all(),
        widget=Select2MultipleWidget()
    )
    # Фильтрация по пути.
    learning_path = ModelMultipleChoiceFilter(
        field_name='learning_path',
        queryset=LearningPath.objects.all(),
        widget=Select2MultipleWidget()
    )
    # Фильтрация по дате начала "до".
    planned_start_date_lte = DateFilter(
        field_name='planned_start_date',
        lookup_expr="lte",
        label='Планируемая дата начала до',
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
    # Фильтрация по дате начала "после".
    planned_start_date_gte = DateFilter(
        field_name='planned_start_date',
        lookup_expr="gte",
        label='Планируемая дата начала после',
        widget=forms.DateInput(attrs={'type': 'date'}),
    )

# Фильтрация результатов.
class ResultFilter(FilterSet):
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
    # Фильтрация по типу.
    type = ChoiceFilter(
        choices=Result.TYPES,
        widget=Select2Widget
    )
    # Фильтрация по комплексу.
    learning_complex = ModelMultipleChoiceFilter(
        field_name='learning_complex',
        queryset=LearningComplex.objects.all(),
        widget=Select2MultipleWidget()
    )
    # Фильтрация по пути.
    learning_path = ModelMultipleChoiceFilter(
        field_name='learning_path',
        queryset=LearningPath.objects.all(),
        widget=Select2MultipleWidget()
    )
    # Фильтрация по задаче.
    learning_task = ModelMultipleChoiceFilter(
        field_name='learning_task',
        queryset=LearningTask.objects.all().order_by('learning_path'),
        widget=Select2MultipleWidget()
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
    # Фильтрация по статусу
    status = ChoiceFilter(
        field_name='status',
        choices=[
            ('appointed', 'Назначено'),
            ('in_progress', 'В процессе'),
            ('completed', 'Пройдено'),
            ('failed', 'Провалено'),
            ('registered', 'Зарегистрирован'),
            ('refused', 'Отказался'),
            ('present', 'Присутствовал'),
            ('absent', 'Отсутствовал'),
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
    # Самоназначение.
    self_appointment = ChoiceFilter(
        field_name='self_appointment',
        label='Самоназначение',
        choices=[
            (True, 'Да'),
            (False, 'Нет')
        ],
        widget=forms.Select,  # Использует выпадающий список для выбора.
    )


