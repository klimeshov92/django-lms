# Импорт моделей фильтрации.
from django_filters import FilterSet, ModelMultipleChoiceFilter, ChoiceFilter, DateTimeFilter
# Импорт виджетов select2.
from django_select2.forms import Select2MultipleWidget, Select2Widget
# Импорт моделей.
from core.models import Category
# Импорт выборки по правам.
from guardian.shortcuts import get_objects_for_user
from .models import Test, Question
# Импорт форм.
from django import forms
# Импорт каунта.
from django.db.models import Count

# Фильтрация тестов.
class TestFilter(FilterSet):
    # Фильтрация по категории.
    сategory = ModelMultipleChoiceFilter(
        field_name='categories',
        queryset=Category.objects.annotate(num_materials=Count('tests'))
        .filter(num_materials__gt=0).order_by('name'),
        widget=Select2MultipleWidget()
    )
    # Фильтрация по имени.
    name = ModelMultipleChoiceFilter(
        queryset=Test.objects.none(),
        to_field_name='name',
        lookup_expr='icontains',
        widget=Select2MultipleWidget()
    )
    # Фильрация выборов.
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters['name'].queryset = get_objects_for_user(
            self.request.user,
            'view_test',
            klass=Test
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

# Фильтрация вопросов.
class QuestionFilter(FilterSet):
    # Фильтрация по категории.
    сategory = ModelMultipleChoiceFilter(
        field_name='categories',
        queryset=Category.objects.annotate(num_questions=Count('questions'))
        .filter(num_questions__gt=0).order_by('name'),
        widget=Select2MultipleWidget()
    )
    # Фильтрация по имени.
    text = ModelMultipleChoiceFilter(
        queryset=Question.objects.none(),
        to_field_name='text',
        lookup_expr='icontains',
        widget=Select2MultipleWidget()
    )
    # Фильрация выборов.
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters['text'].queryset = get_objects_for_user(
            self.request.user,
            'view_question',
            klass=Question
        ).order_by('text')
