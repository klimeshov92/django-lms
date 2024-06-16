# Импорт форм.
from django import forms
# Импорт моделей.
from .models import Material, File
# Импорт select2.
from django_select2.forms import Select2Widget, Select2MultipleWidget
# CKEditor.
from ckeditor.widgets import CKEditorWidget

# Форма создания материала.
class MaterialForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget(), label='Содержание')
    class Meta:
        # Модель.
        model = Material
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
            'content',
            'self_appointment',
        ]
        # Классы виджетов.
        widgets = {
            'creator': forms.HiddenInput(),
            'categories': Select2MultipleWidget(),
        }

# Форма создания файла.
class FileForm(forms.ModelForm):
    class Meta:
        # Модель.
        model = File
        # Поля.
        fields = ['type',
                  'creator',
                  'categories',
                  'name',
                  'upload_file',
                  'desc',
        ]
        # Классы виджетов.
        widgets = {
            #'type': Select2Widget(),
            'type': forms.Select(),
            'categories': Select2MultipleWidget(),
            'creator': forms.HiddenInput(),
        }
    # Особенность формы для апдейта.
    def __init__(self, *args, **kwargs):
        super(FileForm, self).__init__(*args, **kwargs)

        # Если форма связана с существующим экземпляром модели, скрываем поле 'type'
        if self.instance and self.instance.pk:
            self.fields['upload_file'].widget = forms.HiddenInput(attrs={'disabled': 'disabled'})