# Импорт форм.
from django import forms
# Импорт моделей.
from .models import Work
from learning_path.models import Result, WorkReview
# Импорт select2.
from django_select2.forms import Select2Widget, Select2MultipleWidget
# CKEditor.
from ckeditor.widgets import CKEditorWidget

# Форма создания работы.
class WorkForm(forms.ModelForm):
    manual = forms.CharField(widget=CKEditorWidget(), label='Инструкция')

    class Meta:
        # Модель.
        model = Work
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
            'manual',
            'require_review',
            'self_appointment',
        ]
        # Классы виджетов.
        widgets = {
            'creator': forms.HiddenInput(),
            'categories': Select2MultipleWidget(),
            'require_review': forms.CheckboxInput(attrs={'class': 'type-select-1'}),
            'reviewer_report': forms.CheckboxInput(
                attrs={'class': 'reviewer-report-select toggle-field', 'data-show-if-type-1': '[true]'}
            ),
        }

# Форма создания комплексной программы.
class ExecutorReportForm(forms.ModelForm):
    executor_report = forms.CharField(widget=CKEditorWidget(), label='Содержание')
    status = forms.ChoiceField(
        choices=[
            ('in_progress', 'Оставить в работе'),
            ('on_review', 'Отправить на проверку'),
        ],
        widget=Select2Widget(),
        label='Статус'
    )
    class Meta:
        # Модель.
        model = Result
        # Поля.
        fields = [
            'status',
            'executor_report',
            'executor_report_date',
        ]
        # Классы виджетов.
        widgets = {
            'executor_report_date': forms.HiddenInput(),
        }

# Форма создания комплексной программы.
class ExecutorReportNoReviewForm(forms.ModelForm):
    executor_report = forms.CharField(widget=CKEditorWidget(), label='Содержание')
    status = forms.ChoiceField(
        choices=[
            ('in_progress', 'Оставить в работе'),
            ('completed', 'Отметить пройденной'),
            ('failed', 'Отметить проваленной'),
        ],
        widget=Select2Widget(),
        label='Статус'
    )
    class Meta:
        # Модель.
        model = Result
        # Поля.
        fields = [
            'status',
            'score_scaled',
            'executor_report',
            'executor_report_date',
        ]
        # Классы виджетов.
        widgets = {
            'executor_report_date': forms.HiddenInput(),
        }

# Форма создания комплексной программы.
class WorkReviewForm(forms.ModelForm):
    reviewer_report = forms.CharField(widget=CKEditorWidget(), label='Содержание')
    status = forms.ChoiceField(
        choices=[
            ('on_review', 'Оставить на проверке'),
            ('in_progress', 'Вернуть в работу'),
            ('completed', 'Отметить пройденной'),
            ('failed', 'Отметить проваленной'),
        ],
        widget=Select2Widget(),
        label='Статус'
    )
    class Meta:
        # Модель.
        model = WorkReview
        # Поля.
        fields = [
            'status',
            'score_scaled',
            'reviewer_report',
            'result',
            'reviewer',
        ]
        # Классы виджетов.
        widgets = {
            'status': forms.Select(),
            'result': forms.HiddenInput(),
            'reviewer': forms.HiddenInput(),
        }
