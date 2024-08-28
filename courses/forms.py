# Импорт форм.
from django import forms
# Импорт моделей.
from .models import Course
# Импорт select2.
from django_select2.forms import Select2Widget, Select2MultipleWidget

# Форма создания материала.
class CourseForm(forms.ModelForm):
    class Meta:
        # Модель.
        model = Course
        # Поля.
        fields = [
            'avatar',
            'type',
            'zip_file',
            'creator',
            'categories',
            'name',
            'authors',
            'time_to_complete',
            'bonus',
            'desc',
            'self_appointment',
        ]
        # Классы виджетов.
        widgets = {
            'type': forms.Select(),
            'creator': forms.HiddenInput(),
            'categories': Select2MultipleWidget(),
        }
