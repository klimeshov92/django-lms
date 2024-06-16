# Импорт моделей фильтрации.
from django_filters import FilterSet, ModelMultipleChoiceFilter, ChoiceFilter, DateTimeFilter
# Импорт виджетов select2.
from django_select2.forms import Select2MultipleWidget, Select2Widget
# Импорт моделей.
from core.models import Category
from .models import Course, ScormPackage
# Импорт форм.
from django import forms
# Импорт каунта.
from django.db.models import Count
# Импорт прав.
from guardian.shortcuts import get_objects_for_user

# Фильтрация материалов.
class CourseFilter(FilterSet):
    # Фильтрация по категории.
    сategory = ModelMultipleChoiceFilter(
        field_name='categories',
        queryset=Category.objects.annotate(num_courses=Count('courses'))
        .filter(num_courses__gt=0).order_by('name'),
        widget=Select2MultipleWidget()
    )
    # Фильтрация по имени.
    name = ModelMultipleChoiceFilter(
        queryset=Course.objects.none(),
        to_field_name='name',
        lookup_expr='icontains',
        widget=Select2MultipleWidget()
    )

    # Фильрация выборов.
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters['name'].queryset = get_objects_for_user(
            self.request.user,
            'view_course',
            klass=Course
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

# Фильтрация файлов.
class ScormPackageFilter(FilterSet):
    # Фильтрация по категории.
    сategory = ModelMultipleChoiceFilter(
        field_name='categories',
        queryset=Category.objects.annotate(num_scorm_packages=Count('scorm_packages'))
        .filter(num_scorm_packages__gt=0).order_by('name'),
        widget=Select2MultipleWidget()
    )
    # Фильтрация по имени.
    course = ModelMultipleChoiceFilter(
        queryset=ScormPackage.objects.all(),
        to_field_name='course',
        lookup_expr='icontains',
        widget=Select2MultipleWidget()
    )
