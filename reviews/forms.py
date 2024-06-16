# Импорт форм.
from django import forms
# Импорт моделей.
from .models import Review
# Импорт select2.
from django_select2.forms import Select2Widget

# Форма создания отзыва.
class ObjectsReviewForm(forms.ModelForm):
    class Meta:
        # Модель.
        model = Review
        # Поля.
        fields = [
            'type',
            'creator',
            'score',
            'text',
            'learning_path',
            'material',
            'test',
            'course',
            'event',
        ]
        # Классы виджетов.
        widgets = {
            'type': forms.HiddenInput(),
            'creator': forms.HiddenInput(),
            'learning_path': forms.HiddenInput(),
            'material': forms.HiddenInput(),
            'course': forms.HiddenInput(),
            'test': forms.HiddenInput(),
            'event': forms.HiddenInput(),
        }
