# Импорт форм.
from django import forms
from guardian.forms import GroupObjectPermissionsForm
# Импорт моделей.
from .models import LearningPath, LearningTask, Assignment, Result, \
    LearningComplex, LearningComplexPath, AnswersResult, AssignmentRepeat, WorkReview
# Импорт select2.
from django_select2.forms import Select2Widget, Select2MultipleWidget
# Импорт групп и прав
from django.contrib.auth.models import Group, Permission
from django.core.exceptions import ValidationError
# CKEditor.
from ckeditor.widgets import CKEditorWidget

# Форма создания комплексной программы.
class LearningComplexForm(forms.ModelForm):
    class Meta:
        # Модель.
        model = LearningComplex
        # Поля.
        fields = ['avatar',
                  'creator',
                  'categories',
                  'name',
                  'desc',
        ]
        # Классы виджетов.
        widgets = {
            'creator': forms.HiddenInput(),
            'categories': Select2MultipleWidget(),
        }

# Форма создания траектории.
class LearningPathForm(forms.ModelForm):
    class Meta:
        # Модель.
        model = LearningPath
        # Поля.
        fields = ['avatar',
                  'creator',
                  'categories',
                  'name',
                  'duration',
                  'number_control_tasks',
                  'desc',
                  'self_appointment'
        ]
        # Классы виджетов.
        widgets = {
            'creator': forms.HiddenInput(),
            'categories': Select2MultipleWidget(),
        }

# Форма создания комплексной программы.
class LearningComplexPathForm(forms.ModelForm):
    class Meta:
        # Модель.
        model = LearningComplexPath
        # Поля.
        fields = ['learning_complex',
                  'learning_path',
                  'creator',
                  'position',
        ]
        # Классы виджетов.
        widgets = {
            'learning_complex': forms.HiddenInput(),
            'learning_path': Select2Widget(),
            'creator': forms.HiddenInput(),
        }

# Форма создания задачи.
class LearningTaskForm(forms.ModelForm):
    class Meta:
        # Модель.
        model = LearningTask
        # Поля.
        fields = ['learning_path',
                  'creator',
                  'type',
                  'position',
                  'material',
                  'test',
                  'course',
                  'work',
                  'control_task',
                  'blocking_tasks'
        ]
        # Классы виджетов.
        widgets = {
            'learning_path': forms.HiddenInput(),
            'type': forms.Select(attrs={'class': 'type-select-1'}),
            'creator': forms.HiddenInput(),
            'material': Select2Widget(attrs={'class': 'material-select toggle-field', 'data-show-if-type-1': '["material"]'}),
            'test': Select2Widget(attrs={'class': 'test-select toggle-field', 'data-show-if-type-1': '["test"]'}),
            'course': Select2Widget(attrs={'class': 'course-select toggle-field', 'data-show-if-type-1': '["course"]'}),
            'work': Select2Widget(attrs={'class': 'work-select toggle-field', 'data-show-if-type-1': '["work"]'}),
            'blocking_tasks': Select2MultipleWidget(),
        }

# Форма создания назначения.
class AssignmentForm(forms.ModelForm):
    class Meta:
        # Модель.
        model = Assignment
        # Поля.
        fields = ['type',
                  'creator',
                  'learning_complex',
                  'learning_path',
                  'material',
                  'course',
                  'test',
                  'work',
                  'categories',
                  'participants',
                  'employee',
                  'group',
                  'planned_start_date',
                  'duration',
                  'reassignment',
                  'deadlines',
                  'manager_supervising',
                  'supervisors_group',
                  'desc',
        ]
        # Классы виджетов.
        widgets = {
            'creator': forms.HiddenInput(),
            'type': forms.Select(attrs={'class': 'type-select-1'}),
            'learning_complex': Select2Widget(
                attrs={'class': 'learning-complex-select toggle-field', 'data-show-if-type-1': '["learning_complex"]'}
            ),
            'learning_path': Select2Widget(
                attrs={'class': 'learning-path-select toggle-field', 'data-show-if-type-1': '["learning_path"]'}
            ),
            'material': Select2Widget(
                attrs={'class': 'material-select toggle-field', 'data-show-if-type-1': '["material"]'}
            ),
            'course': Select2Widget(
                attrs={'class': 'course-select toggle-field', 'data-show-if-type-1': '["course"]'}
            ),
            'test': Select2Widget(
                attrs={'class': 'test-select toggle-field', 'data-show-if-type-1': '["test"]'}
            ),
            'work': Select2Widget(
                attrs={'class': 'work-select toggle-field', 'data-show-if-type-1': '["work"]'}
            ),
            'categories': Select2MultipleWidget(),
            'participants': forms.Select(attrs={'class': 'type-select-2'}),
            'employee': Select2Widget(
                attrs={'class': 'employee-select toggle-field', 'data-show-if-type-2': '["employee"]'}
            ),
            'group': Select2Widget(
                attrs={'class': 'group-select toggle-field', 'data-show-if-type-2': '["group"]'}
            ),
            'planned_start_date': forms.DateInput(
                attrs={'type': 'date', 'class': 'planned-start-date-select toggle-field', 'data-show-if-type-1': '["learning_complex", "learning_path", "material", "course", "test"]'}
            ),
            'duration': forms.NumberInput(
              attrs={'class': 'duration-select toggle-field', 'data-show-if-type-1': '["material", "course", "test"]'}
            ),
            'supervisors_group': Select2Widget(),
        }

    # Проверки.
    def clean(self):

        cleaned_data = super().clean()

        # Переменные.
        employee = cleaned_data.get('employee')
        group = cleaned_data.get('group')

        # Проверка аудитории.
        if not employee and not group:
            raise ValidationError('Нужно выбрать аудиторию')

        return cleaned_data

    # Особенность формы для апдейта.
    def __init__(self, *args, **kwargs):
        super(AssignmentForm, self).__init__(*args, **kwargs)

        # Скрываем поле 'type'
        if self.instance and self.instance.pk:
            self.fields['type'].widget = forms.HiddenInput()
            self.fields['learning_complex'].widget = forms.HiddenInput()
            self.fields['learning_path'].widget = forms.HiddenInput()
            self.fields['material'].widget = forms.HiddenInput()
            self.fields['course'].widget = forms.HiddenInput()
            self.fields['test'].widget = forms.HiddenInput()
            self.fields['duration'].widget = forms.HiddenInput()
            self.fields['participants'].widget = forms.HiddenInput()
            self.fields['group'].widget = forms.HiddenInput()
            self.fields['employee'].widget = forms.HiddenInput()
            self.fields['planned_start_date'].widget = forms.HiddenInput()
            self.fields['reassignment'].widget = forms.HiddenInput()

# Форма создания назначения.
class AssignmentRepeatForm(forms.ModelForm):
    class Meta:
        # Модель.
        model = AssignmentRepeat
        # Поля.
        fields = ['type',
                  'creator',
                  'assignment',
                  'day_of_week',
                  'month_interval',
                  'desc',
        ]
        # Классы виджетов.
        widgets = {
            'type': forms.Select(attrs={'class': 'type-select-1'}),
            'creator': forms.HiddenInput(),
            'assignment': forms.HiddenInput(),
            'day_of_week': forms.Select(attrs={'class': 'days-of-week-select toggle-field', 'data-show-if-type-1': '["weekly"]'}),
            'month_interval': forms.NumberInput(attrs={'class': 'repeats-date-select toggle-field', 'data-show-if-type-1': '["monthly"]'}),
        }

    # Особенность формы для апдейта.
    #def __init__(self, *args, **kwargs):
        #super(AssignmentForm, self).__init__(*args, **kwargs)

        # Скрываем поле 'type'
        #if self.instance and self.instance.pk:
            #self.fields['type'].widget = forms.HiddenInput()
            #self.fields['learning_path'].widget = forms.HiddenInput()
            #self.fields['learning_complex'].widget = forms.HiddenInput()
            #self.fields['group'].widget = forms.HiddenInput()
            #self.fields['planned_start_date'].widget = forms.HiddenInput()
            #self.fields['reassignment'].widget = forms.HiddenInput()

