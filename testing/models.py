from django.db import models

# Create your models here.

# Импорт пользователя и каталога.
from core.models import Employee, Category
from django.core.validators import MinValueValidator

# Класс теста.
class Test(models.Model):
    # Картинка теста.
    avatar = models.ImageField(verbose_name='Аватар', null=True, blank=True, upload_to='tests_avatar/')
    # Создатель.
    creator = models.ForeignKey(
        Employee,
        verbose_name='Создатель',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='tests_creators',
        related_query_name='tests_creators'
    )
    # Дата и время создания и изменения.
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время создания', db_index=True)
    changed = models.DateTimeField(auto_now=True, verbose_name='Дата и время изменения', db_index=True)
    # Категории.
    categories = models.ManyToManyField(
        Category, verbose_name='Категории',
        blank=True,
        related_name='tests',
        related_query_name='tests',
        db_index=True
    )
    # Название.
    name = models.CharField(verbose_name='Название', max_length=255, db_index=True)
    # Авторы.
    authors = models.CharField(verbose_name='Авторы', null=True, blank=True, max_length=255)
    # Бонус.
    bonus = models.IntegerField(verbose_name='Бонусы', default=100, validators=[MinValueValidator(0)])
    # Описание.
    desc = models.TextField(verbose_name='Описание', null=True, blank=True)
    # Количество попыток.
    amount_of_try = models.IntegerField(verbose_name='Количество попыток', default=1, validators=[MinValueValidator(1)])
    # Выборка вопросов.
    SAMPLE_OF_QUESTIONS = [
        ('all', 'Все'),
        ('random', 'Несколько случайных'),
    ]
    sample_of_questions = models.CharField(max_length=255, choices=SAMPLE_OF_QUESTIONS, default='all', verbose_name='Выборка вопросов')
    # Количество вопросов.
    number_of_questions = models.IntegerField(verbose_name='Количество вопросов в выборке', default=1, validators=[MinValueValidator(1)])
    # Проходной балл.
    passing_score = models.IntegerField(verbose_name='Проходной балл', default=20, validators=[MinValueValidator(1)])
    # Случайный порядок вопросов.
    random_questions = models.BooleanField(verbose_name='Случайный порядок вопросов', default=True)
    # Случайный порядок ответов.
    random_answers = models.BooleanField(verbose_name='Случайный порядок ответов', default=True)
    # Длительность.
    time_to_complete = models.IntegerField(verbose_name='Время на выполнение (минуты)', default=20, validators=[MinValueValidator(1)])
    # Cамоназначение.
    self_appointment = models.BooleanField(verbose_name='Caмоназначение', default=False)
    # Отражение результатов.
    show_questions_results = models.BooleanField(verbose_name='Показывать результаты вопросов', default=True)
    # Отражение правильных ответов.
    show_answers_results = models.BooleanField(verbose_name='Показывать результаты ответов', default=True)
    class Meta:
        # Изменение имени модели.
        verbose_name = 'Тест'
        verbose_name_plural = 'Тесты'

    # Строкове представление.
    def __str__(self):
        category_list = []
        if self.categories.exists():
            for category in self.categories.all():
                category_list.append(f'{category.name}')
            category_str = ' | '.join(category_list)
            return f'{self.name} ({category_str})'
        else:
            return f'{self.name}'

# Класс вопроса.
class Question(models.Model):
    # Тип.
    TYPES = [
        ('', 'Выберите тип вопроса'),
        ('single_selection', 'Одиночный выбор'),
        ('multiple_choice', 'Множественный выбор'),
        ('sorting', 'Сортировка'),
        ('compliance', 'Соотвествие'),
        ('text_input', 'Текстовый ввод'),
        ('numeric_input', 'Числовой ввод'),
    ]
    type = models.CharField(max_length=255, choices=TYPES, default='', verbose_name='Тип')
    # Создатель.
    creator = models.ForeignKey(
        Employee,
        verbose_name='Создатель',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='questions_creators',
        related_query_name='questions_creators'
    )
    # Категории.
    categories = models.ManyToManyField(
        Category,
        verbose_name='Категории',
        blank=True,
        related_name='questions',
        related_query_name='questions',
        db_index=True
    )
    # Текст.
    text = models.TextField(verbose_name='Текст вопроса', db_index=True)
    # Картинка.
    picture = models.ImageField(verbose_name='Картинка', null=True, blank=True, upload_to='questions_picture/')
    # Инструкция.
    instruction = models.TextField(verbose_name='Инструкция')
    # Балл.
    score = models.IntegerField(verbose_name='Балл', default=1, validators=[MinValueValidator(0)])
    # Обратная связь при привильном ответе.
    feedback_for_correct = models.TextField(verbose_name='Обратная связь при правильном ответе', default='Верно!')
    # Обратная связь при непривильном ответе.
    feedback_for_incorrect = models.TextField(verbose_name='Обратная связь при неправильном ответе', default='Неверно!')
    class Meta:
        # Изменение имени модели.
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'

    # Строкове представление.
    def __str__(self):
        category_list = []
        if self.categories.exists():
            for category in self.categories.all():
                category_list.append(f'{category.name}')
            category_str = ' | '.join(category_list)
            return f'{self.text} ({category_str})'
        else:
            return f'{self.text}'


# Класс вопросов теста.
class TestsQuestion(models.Model):
    # Тест.
    test = models.ForeignKey(
        Test,
        verbose_name='Тест',
        null=True,
        on_delete=models.CASCADE,
        related_name='tests_questions',
        related_query_name='tests_questions',
        db_index=True
    )
    # Вопрос.
    question = models.ForeignKey(
        Question,
        verbose_name='Вопрос',
        null=True,
        on_delete=models.CASCADE,
        related_name='tests_questions',
        related_query_name='tests_questions',
        db_index=True
    )
    # Позиция.
    position = models.IntegerField(verbose_name='Позиция', db_index=True, validators=[MinValueValidator(1)])
    class Meta:
        # Изменение имени модели.
        verbose_name = 'Вопросы теста'
        verbose_name_plural = 'Вопросы теста'
        # Сортировка.
        ordering = ['position']

    # Строкове представление.
    def __str__(self):
        return f'{self.test} - {self.position} - {self.question}'

# Генератор вопросов.
class TestsQuestionsGenerator(models.Model):
    # Создатель.
    creator = models.ForeignKey(
        Employee,
        verbose_name='Создатель',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='tests_questions_generator_creators',
        related_query_name='tests_questions_generator_creators'
    )
    # Дата и время создания и изменения.
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время создания', db_index=True)
    changed = models.DateTimeField(auto_now=True, verbose_name='Дата и время изменения', db_index=True)
    # Группа
    test = models.OneToOneField(
        Test,
        verbose_name='Тест',
        on_delete=models.CASCADE,
        related_name='tests_questions_generator',
        related_query_name='tests_questions_generator'
    )
    # Добавляемые и исключаемые сотрудники.
    added_categories = models.ManyToManyField(
        Category,
        verbose_name='Добавляемые категоии',
        blank=True,
        related_name='added_tests_questions_generators',
        related_query_name='added_tests_questions_generators'
    )
    added_questions = models.ManyToManyField(
        Question,
        verbose_name='Добавляемые вопросы',
        blank=True,
        related_name='added_tests_questions_generators',
        related_query_name='added_tests_questions_generators'
    )
    excluded_categories = models.ManyToManyField(
        Category,
        verbose_name='Исключаемые категоии',
        blank=True,
        related_name='excluded_tests_questions_generators',
        related_query_name='excluded_tests_questions_generators'
    )
    excluded_questions = models.ManyToManyField(
        Question,
        verbose_name='Исключаемые вопросы',
        blank=True,
        related_name='excluded_tests_questions_generators',
        related_query_name='excluded_tests_questions_generators'
    )
    class Meta:
        # Изменение имени модели.
        verbose_name = 'Генератор вопросов'
        verbose_name_plural = 'Генератор вопросов'

    def __str__(self):
        # Возвращаем пользовательское строковое представление, например, имя группы.
        return f'{self.test.name}'

# Класс ответа.
class Answer(models.Model):
    # Создатель.
    creator = models.ForeignKey(
        Employee,
        verbose_name='Создатель',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='answers_creators',
        related_query_name='answers_creators'
    )
    # Вопрос.
    question = models.ForeignKey(Question, verbose_name='Вопрос', null=True, on_delete=models.CASCADE,
                                related_name='answers', related_query_name='answers', db_index=True)
    # Текст.
    text = models.TextField(verbose_name='Текст ответа', null=True, blank=True)
    # Картинка.
    picture = models.ImageField(verbose_name='Картинка', null=True, blank=True, upload_to='answers_picture/')
    # Балл.
    score = models.IntegerField(verbose_name='Балл', default=0, validators=[MinValueValidator(0)])
    # Обратная связь при привильном ответе.
    feedback_for_correct = models.TextField(verbose_name='Обратная связь при привильном ответе', default='Верно!')
    # Обратная связь при непривильном ответе.
    feedback_for_incorrect = models.TextField(verbose_name='Обратная связь при непривильном ответе', default='Неверно!')
    # Правильный или нет.
    correct_answer = models.BooleanField(verbose_name='Правильный ответ', default=False)
    # Правильая позиция.
    correct_position = models.IntegerField(verbose_name='Правильная позиция', null=True, blank=True, validators=[MinValueValidator(1)])
    # Правильный текст.
    correct_text_input = models.CharField(verbose_name='Правильный ответ', max_length=255, null=True, blank=True)
    # Правильное число.
    correct_numeric_input = models.IntegerField(verbose_name='Правильный ответ', null=True, blank=True)
    # Позиция в списке.
    position = models.IntegerField(verbose_name='Позиция в списке', db_index=True, validators=[MinValueValidator(1)])

    class Meta:
        # Изменение имени модели.
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'
        # Сортировка.
        ordering = ['position']

    # Строкове представление.
    def __str__(self):
        return f'{self.text} из вопроса {self.question.text}'

# Класс соотвествующего ответу пункта.
class RelevantPoint(models.Model):
    # Соотвествующий ответ.
    answer = models.OneToOneField(
        Answer,
        verbose_name='Соотвествующий ответ',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='relevant_point',
        related_query_name='relevant_point'
    )
    # Создатель.
    creator = models.ForeignKey(
        Employee,
        verbose_name='Создатель',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='relevant_points_creators',
        related_query_name='relevant_points_creators'
    )
    # Текст.
    text = models.TextField(verbose_name='Текст пункта')
    class Meta:
        # Изменение имени модели.
        verbose_name = 'Соотвествующий пункт'
        verbose_name_plural = 'Соотвествующий пункт'

    # Строкове представление.
    def __str__(self):
        return f'{self.text}'
