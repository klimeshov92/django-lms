# Импорт форм.
from django import forms
# Импорт моделей.
from .models import Email
# Импорт select2.
from django_select2.forms import Select2Widget, Select2MultipleWidget

# Форма создания рассылки.
class EmailForm(forms.ModelForm):
    class Meta:
        # Модель.
        model = Email
        # Поля.
        fields = [
            'type',
            'creator',
            'categories',
            'group',
            'assignment',
            'event',
            'desc',
        ]
        # Классы виджетов.
        widgets = {
            'type': forms.Select(attrs={'class': 'type-select-1'}),
            'creator': forms.HiddenInput(),
            'categories': Select2MultipleWidget(),
            'group': Select2Widget(),
            'assignment': Select2Widget(
                attrs={
                    'class': 'assignment-select toggle-field',
                    'data-show-if-type-1': '["assignment"]'
                }
            ),
            'event': Select2Widget(
                attrs={
                    'class': 'in-person-select toggle-field',
                    'data-show-if-type-1': '["event"]'
                }
            ),
        }

    # Особенность формы для апдейта.
    def __init__(self, *args, **kwargs):
        super(EmailForm, self).__init__(*args, **kwargs)

        # Если форма связана с существующим экземпляром модели, скрываем поле 'type'.
        if self.instance and self.instance.pk:
            self.fields['group'].widget = forms.HiddenInput()
            self.fields['assignment'].widget = forms.HiddenInput()
            self.fields['event'].widget = forms.HiddenInput()
            self.fields['type'].widget = forms.HiddenInput()


# Выбор типа рассылки.
class EmailSendingForm(forms.Form):
    SENDING_TYPES = [('new', 'Новым адресатам'), ('all', 'Всем адресатам')]
    sending_type = forms.ChoiceField(choices=SENDING_TYPES, label='Тип рассылки')
