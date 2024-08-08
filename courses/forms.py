# Импорт форм.
from django import forms
# Импорт моделей.
from .models import ScormPackage, Course
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
            'creator': forms.HiddenInput(),
            'categories': Select2MultipleWidget(),
        }

# Форма пакета.
class ScormPackageForm(forms.ModelForm):
    class Meta:
        model = ScormPackage
        fields = [
            'type',
            'creator',
            'categories',
            'desc',
            'course',
            'zip_file'
        ]
        # Классы виджетов.
        widgets = {
            'type': forms.Select(),
            'course': Select2Widget(),
            'creator': forms.HiddenInput(),
            'categories': Select2MultipleWidget(),
        }
