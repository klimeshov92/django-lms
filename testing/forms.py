# Импорт форм.
from django import forms
# Импорт моделей.
from .models import Test, Question, Answer, RelevantPoint, TestsQuestion, TestsQuestionsGenerator
from learning_path.models import AnswersResult
# Импорт select2.
from django_select2.forms import Select2Widget, Select2MultipleWidget

# Форма создания теста.
class TestForm(forms.ModelForm):
    class Meta:
        # Модель.
        model = Test
        # Поля.
        fields = (
            'avatar',
            'creator',
            'categories',
            'name',
            'authors',
            'bonus',
            'desc',
            'amount_of_try',
            'sample_of_questions',
            'number_of_questions',
            'passing_score',
            'random_questions',
            'random_answers',
            'time_to_complete',
            'show_questions_results',
            'show_answers_results',
            'self_appointment',
        )
        # Классы виджетов.
        widgets = {
            'creator': forms.HiddenInput(),
            'categories': Select2MultipleWidget(),
            'questions': Select2MultipleWidget(),
            'sample_of_questions': forms.Select(attrs={'class': 'type-select-1'}),
            'number_of_questions': forms.NumberInput(
                attrs={'class': 'number-of-questions-select toggle-field', 'data-show-if-type-1': '["random"]'}
            ),
        }

# Форма создания вопроса.
class QuestionForm(forms.ModelForm):
    class Meta:
        # Модель.
        model = Question
        # Поля.
        fields = (
            'type',
            'creator',
            'categories',
            'text',
            'picture',
            'instruction',
            'score',
            'feedback_for_correct',
            'feedback_for_incorrect',
        )
        # Классы виджетов.
        widgets = {
            'type': forms.Select(attrs={'class': 'type-select-1'}),
            'instruction': forms.Textarea(attrs={'class': 'instruction'}),
            'creator': forms.HiddenInput(),
            'categories': Select2MultipleWidget(),
        }

    # Особенность формы для апдейта.
    def __init__(self, *args, **kwargs):
        super(QuestionForm, self).__init__(*args, **kwargs)

        # Если форма связана с существующим экземпляром модели, скрываем поле 'type'
        if self.instance and self.instance.pk:
            self.fields['type'].widget = forms.HiddenInput()

# форма изменения ответа
class AnswerForm(forms.ModelForm):
    class Meta:
        # модель
        model = Answer
        # поля
        fields = (
            'question',
            'creator',
            'position',
            'picture',
            'text',
            'correct_answer',
            'correct_position',
            'correct_text_input',
            'correct_numeric_input',
            'score',
            'feedback_for_correct',
            'feedback_for_incorrect',
                  )
        widgets = {
            'creator': forms.HiddenInput(),
            'question': forms.HiddenInput(),
        }

    # Привязка к типу вопроса.
    def __init__(self, *args, **kwargs):

        # Извлекаем question_pk.
        question_pk = kwargs.pop('question_pk', None)
        super(AnswerForm, self).__init__(*args, **kwargs)

        # Если question_pk предоставлен, получаем тип вопроса.
        if question_pk:
            question = Question.objects.get(pk=question_pk)
            # Теперь используем question_type для управления видимостью полей.
            if question.type != 'single_selection' and question.type != 'multiple_choice':
                self.fields['correct_answer'].widget = forms.HiddenInput()
            if question.type != 'sorting':
                self.fields['correct_position'].widget = forms.HiddenInput()
            if question.type == 'text_input' or question.type == 'numeric_input':
                self.fields['text'].widget = forms.HiddenInput()
                self.fields['picture'].widget = forms.HiddenInput()
            if question.type != 'text_input':
                self.fields['correct_text_input'].widget = forms.HiddenInput()
            if question.type != 'numeric_input':
                self.fields['correct_numeric_input'].widget = forms.HiddenInput()

# Форма соотвествующего ответа.
class RelevantPointForm(forms.ModelForm):
    class Meta:
        # Модель.
        model = RelevantPoint
        # Поля.
        fields = ('creator',
                  'answer',
                  'text')
        widgets = {
            'creator': forms.HiddenInput(),
        }

# Форма создания категории.
class TestsQuestionsGeneratorForm(forms.ModelForm):
    class Meta:
        # Модель.
        model = TestsQuestionsGenerator
        # Поля.
        fields = (
            'creator',
            'test',
            'added_categories',
            'added_questions',
            'excluded_categories',
            'excluded_questions',
        )
        # Классы виджетов.
        widgets = {
            'creator': forms.HiddenInput(),
            'group': forms.HiddenInput(),
            'test': forms.HiddenInput(),
            'added_categories': Select2MultipleWidget(),
            'added_questions': Select2MultipleWidget(),
            'excluded_categories': Select2MultipleWidget(),
            'excluded_questions': Select2MultipleWidget(),
        }


# Форма ответа на вопрос.
class AnswersToQuestionForm(forms.ModelForm):
    class Meta:
        # модель
        model = AnswersResult
        # поля
        fields = (
            'answer',
            'selected_answer',
            'selected_position',
            'selected_text_input',
            'selected_numeric_input',
            'selected_relevant_point',
            'score',
            'status'
        )
        widgets = {
            'answer': forms.HiddenInput(),
            'score': forms.HiddenInput(),
            'status': forms.HiddenInput(),
        }

    # Переопределяем поля формы.
    def __init__(self, *args, **kwargs):
        # Забираем форму.
        super(AnswersToQuestionForm, self).__init__(*args, **kwargs)
        # Определяем queryset для поля выбора соответствующего пункта.
        if self.instance.answer.question.type == 'compliance':
            # Фильтруем соответствующие пункты по вопросу.
            question = self.instance.answer.question
            relevant_points_queryset = RelevantPoint.objects.filter(answer__question=question)
            # Устанавливаем новый queryset для поля.
            self.fields['selected_relevant_point'].queryset = relevant_points_queryset
        # Обрабатываем одиночный выбор.
        if self.instance.answer.question.type == 'single_selection':
            self.fields['selected_answer'].widget.attrs['class'] = 'single_selection'
        # Прячем лишние поля.
        if self.instance.answer.question.type != 'single_selection' and self.instance.answer.question.type != 'multiple_choice':
            self.fields['selected_answer'].widget = forms.HiddenInput()
        if self.instance.answer.question.type != 'sorting':
            self.fields['selected_position'].widget = forms.HiddenInput()
        if self.instance.answer.question.type != 'compliance':
            self.fields['selected_relevant_point'].widget = forms.HiddenInput()
        if self.instance.answer.question.type != 'text_input':
            self.fields['selected_text_input'].widget = forms.HiddenInput()
        if self.instance.answer.question.type != 'numeric_input':
            self.fields['selected_numeric_input'].widget = forms.HiddenInput()