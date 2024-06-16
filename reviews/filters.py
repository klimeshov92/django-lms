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
from learning_path.models import LearningTask, LearningPath, Result, Assignment, LearningComplex
from .models import Review

# Фильтрация результатов.
class ReviewFilter(FilterSet):
    # Фильтрация по сотруднику.
    creator = ModelMultipleChoiceFilter(
        field_name='creator',
        queryset=Employee.objects.all(),
        widget=Select2MultipleWidget()
    )
    # Фильтрация по группе.
    creator__groups = ModelMultipleChoiceFilter(
        label='Группа создателей',
        field_name='creator__groups',
        queryset=EmployeesGroup.objects.all(),
        widget=Select2MultipleWidget()
    )
    # Фильтрация по типу.
    type = ChoiceFilter(
        choices=Review.TYPES,
        widget=Select2Widget
    )
    # Фильтрация по пути.
    learning_path = ModelMultipleChoiceFilter(
        field_name='learning_path',
        queryset=LearningPath.objects.all(),
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

# Фильтрация результатов.
class ObjectsReviewFilter(FilterSet):
    # Фильтрация по сотруднику.
    creator = ModelMultipleChoiceFilter(
        field_name='creator',
        queryset=Employee.objects.all(),
        widget=Select2MultipleWidget()
    )
    # Фильтрация по группе.
    creator__groups = ModelMultipleChoiceFilter(
        label='Группа создателей',
        field_name='creator__groups',
        queryset=EmployeesGroup.objects.all(),
        widget=Select2MultipleWidget()
    )

