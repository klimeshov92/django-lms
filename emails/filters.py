# Импорт моделей фильтрации.
from django_filters import FilterSet, ModelMultipleChoiceFilter, ChoiceFilter, DateTimeFilter
# Импорт виджетов select2.
from django_select2.forms import Select2MultipleWidget, Select2Widget
# Импорт моделей.
from core.models import Category, EmployeesGroup
from .models import Email
# Импорт форм.
from django import forms
# Импорт каунта.
from django.db.models import Count
# Импорт прав.
from guardian.shortcuts import get_objects_for_user


# Фильтрация материалов.
class EmailFilter(FilterSet):

    # Фильтрация по типу.
    presence_mark = ChoiceFilter(
        field_name='presence_mark',
        choices=[
        ('password', 'Пароль'),
        ('assignment', 'Назначение'),
        ('event', 'Мероприятие'),
        ],
        widget=Select2Widget,
        label='Тип'
    )

    # Фильтрация по категории.
    сategory = ModelMultipleChoiceFilter(
        field_name='categories',
        queryset=Category.objects.annotate(num_courses=Count('emails'))
        .filter(num_courses__gt=0).order_by('name'),
        widget=Select2MultipleWidget()
    )

    # Фильтрация по группе.
    group = ModelMultipleChoiceFilter(
        field_name='group',
        queryset=EmployeesGroup.objects.all(),
        widget=Select2MultipleWidget()
    )

