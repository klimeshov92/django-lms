# Импорт форм.
from django import forms
# Импорт моделей.
from .models import Event, ParticipantsGenerator
from learning_path.models import Result
# Импорт select2.
from django_select2.forms import Select2Widget, Select2MultipleWidget

# Форма создания мероприятия.
class EventForm(forms.ModelForm):
    class Meta:
        # Модель.
        model = Event
        # Поля.
        fields = [
            'type',
            'creator',
            'categories',
            'name',
            'webinars_link',
            'location',
            'responsibles',
            'date',
            'start_time',
            'end_time',
            'bonus',
            'desc',
            'materials',
            'files',
            'self_appointment',
        ]
        # Классы виджетов.
        widgets = {
            'type': forms.Select(attrs={'class': 'type-select-1'}),
            'creator': forms.HiddenInput(),
            'categories': Select2MultipleWidget(),
            'webinars_link': forms.Textarea(
                attrs={
                    'maxlength': 255,
                    'class': 'webinar-select toggle-field',
                    'data-show-if-type-1': '["webinar", "in-person_and_webinar"]'
                }
            ),
            'location': forms.Textarea(
                attrs={
                    'maxlength': 255,
                    'class': 'in-person-select toggle-field',
                    'data-show-if-type-1': '["in-person", "in-person_and_webinar"]'
                }
            ),
            'responsibles': Select2MultipleWidget(),
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
            'materials': Select2MultipleWidget(),
            'files': Select2MultipleWidget(),
        }

# Форма создания участников мерпориятия.
class ParticipantsGeneratorForm(forms.ModelForm):
    class Meta:
        # Модель.
        model = ParticipantsGenerator
        # Поля.
        fields = ['creator',
                  'event',
                  'added_groups',
                  'added_users',
                  'excluded_groups',
                  'excluded_users',
                  'days_worked_gte',
                  'days_worked_lte',
                  'autoupdate',
        ]
        # Классы виджетов.
        widgets = {
            'creator': forms.HiddenInput(),
            'event': forms.HiddenInput(),
            'added_groups': Select2MultipleWidget(),
            'added_users': Select2MultipleWidget(),
            'excluded_groups': Select2MultipleWidget(),
            'excluded_users': Select2MultipleWidget(),
        }


