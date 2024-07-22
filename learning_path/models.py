from django.db import models

# Create your models here.

# Импорт таймзоны.
from django.utils import timezone
# Импорт моделей.
from core.models import Employee, EmployeesGroup, Category
from materials.models import Material
from testing.models import Test, Question, Answer, RelevantPoint
from courses.models import ScormPackage, Course
from events.models import Event
from asgiref.sync import sync_to_async
from django.core.validators import MinValueValidator

# Класс комплекса.
class LearningComplex(models.Model):
    # Картинка каталога.
    avatar = models.ImageField(verbose_name='Аватар', null=True, blank=True, upload_to='learning_path_avatar/')
    # Создатель.
    creator = models.ForeignKey(
        Employee,
        verbose_name='Создатель',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='learning_complex_creators',
        related_query_name='learning_complex_creators'
    )
    # Дата и время создания и изменения.
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время создания', db_index=True)
    changed = models.DateTimeField(auto_now=True, verbose_name='Дата и время изменения', db_index=True)
    # Категории.
    categories = models.ManyToManyField(
        Category,
        verbose_name='Категории',
        blank=True,
        related_name='learning_complexs',
        related_query_name='learning_complexs',
        db_index=True
    )
    # Название.
    name = models.CharField(verbose_name='Название', max_length=255, db_index=True)
    # Описание.
    desc = models.TextField(verbose_name='Описание', null=True, blank=True)

    class Meta:
        # Изменение имени модели.
        verbose_name = 'Комплексная программа'
        verbose_name_plural = 'Комплексные программы'

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

# Класс траектории.
class LearningPath(models.Model):
    # Картинка каталога.
    avatar = models.ImageField(verbose_name='Аватар', null=True, blank=True, upload_to='learning_path_avatar/')
    # Создатель.
    creator = models.ForeignKey(
        Employee,
        verbose_name='Создатель',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='learning_path_creators',
        related_query_name='learning_path_creators'
    )
    # Дата и время создания и изменения.
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время создания', db_index=True)
    changed = models.DateTimeField(auto_now=True, verbose_name='Дата и время изменения', db_index=True)
    # Категории.
    categories = models.ManyToManyField(
        Category,
        verbose_name='Категории',
        blank=True,
        related_name='learning_paths',
        related_query_name='learning_paths',
        db_index=True
    )
    # Название.
    name = models.CharField(verbose_name='Название', max_length=255, db_index=True)
    # Описание.
    desc = models.TextField(verbose_name='Описание', null=True, blank=True)
    # Количество дней.
    duration = models.IntegerField(verbose_name='Длительность (дней)', default=14, validators=[MinValueValidator(1)])
    # Необходимо пройти.
    number_control_tasks = models.IntegerField(
        verbose_name='Необходимо пройти (контрольных задач)',
        default=1,
        validators=[MinValueValidator(1)]
    )
    # Cамоназначение.
    self_appointment = models.BooleanField(verbose_name='Caмоназначение', default=False)

    class Meta:
        # Изменение имени модели.
        verbose_name = 'Тракектория обучения'
        verbose_name_plural = 'Тракектория обучения'

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

# Класс траектории.
class LearningComplexPath(models.Model):
    # Комплекс.
    learning_complex = models.ForeignKey(
        LearningComplex,
        verbose_name='Комплексная программа',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='learning_complex_paths',
        related_query_name='learning_complex_paths',
        db_index=True
    )
    # Путь.
    learning_path = models.ForeignKey(
        LearningPath,
        verbose_name='Траектория обучения',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='learning_complex_paths',
        related_query_name='learning_complex_paths',
        db_index=True
    )
    # Создатель.
    creator = models.ForeignKey(
        Employee,
        verbose_name='Создатель',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='learning_complex_path_creators',
        related_query_name='learning_complex_path_creators'
    )
    # Позиция.
    position = models.IntegerField(verbose_name='Позиция', default=0, db_index=True, validators=[MinValueValidator(1)])
    class Meta:
        # Изменение имени модели.
        verbose_name = 'Тракектория обучения комлексной программы'
        verbose_name_plural = 'Тракектории обучения комлексных программ'
        # Сортировка.
        ordering = ['position']

    # Строкове представление.
    def __str__(self):
        return f'{self.learning_path.name} из {self.learning_complex.name}'

# Класс задач.
class LearningTask(models.Model):
    # Путь.
    learning_path = models.ForeignKey(
        LearningPath,
        verbose_name='Траектория обучения',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='learning_tasks',
        related_query_name='learning_tasks',
        db_index=True
    )
    # Создатель.
    creator = models.ForeignKey(
        Employee,
        verbose_name='Создатель',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='learning_task_creators',
        related_query_name='learning_task_creators'
    )
    # Дата и время создания и изменения.
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время создания', db_index=True)
    changed = models.DateTimeField(auto_now=True, verbose_name='Дата и время изменения', db_index=True)
    # Тип
    TYPES = [
        ('', 'Выберите тип здачачи'),
        ('material', 'Материал'),
        ('test', 'Тест'),
        ('course', 'Курс'),
    ]
    type = models.CharField(max_length=255, choices=TYPES, default='', verbose_name='Тип')
    # Позиция.
    position = models.IntegerField(verbose_name='Позиция', default=0, db_index=True, validators=[MinValueValidator(1)])
    # Материал.
    material = models.ForeignKey(
        Material, verbose_name='Материал',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='learning_tasks',
        related_query_name='learning_tasks'
    )
    # Тест.
    test = models.ForeignKey(
        Test, verbose_name='Тест',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='learning_tasks',
        related_query_name='learning_tasks'
    )
    # Курс.
    course = models.ForeignKey(
        Course,
        verbose_name='Курс',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='learning_tasks',
        related_query_name='learning_tasks',
        db_index=True
    )
    # Контрольная задача.
    control_task = models.BooleanField(verbose_name='Контрольная задача', default=False)
    # Блокирующие задачи.
    blocking_tasks = models.ManyToManyField(
        'self',
        symmetrical=False,
        verbose_name='Блокирующие задачи',
        blank=True,
        related_name='learning_tasks',
        related_query_name='learning_tasks',
        db_index=True
    )

    class Meta:
        # Изменение имени модели.
        verbose_name = 'Учебная задача'
        verbose_name_plural = 'Учебные задачи'
        # Сортировка.
        ordering = ['position']

    # Строкове представление.
    def __str__(self):
        if self.type == 'material':
            object = self.material
        if self.type == 'test':
            object = self.test
        if self.type == 'course':
            object = self.course
        if object:
            return f'{self.get_type_display()} - {object.name} | {self.learning_path}'


# Назначение
class Assignment(models.Model):
    # Тип.
    TYPES = [
        ('', 'Выберите тип назначения'),
        ('learning_complex', 'Назначение комплексной программы'),
        ('learning_path', 'Назначение траектории обучения'),
        ('material', 'Материал'),
        ('course', 'Курс'),
        ('test', 'Тест'),
    ]
    type = models.CharField(max_length=255, choices=TYPES, default='', verbose_name='Тип')
    PARTICIPANTS = [
        ('', 'Выберите участников'),
        ('employee', 'Сотрудник'),
        ('group', 'Группа'),
    ]
    participants = models.CharField(max_length=255, choices=PARTICIPANTS, default='', verbose_name='Аудитория')
    # Категории.
    categories = models.ManyToManyField(
        Category,
        verbose_name='Категории',
        blank=True,
        related_name='assignments',
        related_query_name='assignments',
        db_index=True
    )
    # Контент.
    learning_complex = models.ForeignKey(
        LearningComplex,
        verbose_name='Комплексная программа',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='assignments',
        related_query_name='assignments',
        db_index=True
    )
    learning_path = models.ForeignKey(
        LearningPath,
        verbose_name='Траектория обучения',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='assignments',
        related_query_name='assignments',
        db_index=True
    )
    material = models.ForeignKey(
        Material,
        verbose_name='Материал',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='assignments',
        related_query_name='assignments',
        db_index=True
    )
    course = models.ForeignKey(
        Course,
        verbose_name='Курс',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='assignments',
        related_query_name='assignments',
        db_index=True
    )
    test = models.ForeignKey(
        Test,
        verbose_name='Тест',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='assignments',
        related_query_name='assignments',
        db_index=True
    )
    # Дата и время создания и изменения.
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время создания', db_index=True)
    changed = models.DateTimeField(auto_now=True, verbose_name='Дата и время изменения', db_index=True)
    # Создатель.
    creator = models.ForeignKey(
        Employee,
        verbose_name='Создатель',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='assignment_creators',
        related_query_name='assignment_creators'
    )
    # Аудитория.
    employee = models.ForeignKey(
        Employee,
        verbose_name='Сотрудник',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='assignments',
        related_query_name='assignments'
    )
    group = models.ForeignKey(
        EmployeesGroup,
        verbose_name='Группа',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='assignments',
        related_query_name='assignments'
    )
    # Планируемая дата начала.
    planned_start_date = models.DateField(auto_now=False, verbose_name='Планируемая дата начала', db_index=True)
    # Количество дней.
    duration = models.IntegerField(verbose_name='Длительность (дней)', null=True, blank=True, validators=[MinValueValidator(1)])
    # Сроки обязательны или нет.
    deadlines = models.BooleanField(verbose_name='Соблюдение сроков обязательно', default=False)
    # Описание.
    desc = models.TextField(verbose_name='Описание', null=True, blank=True)
    # Группа прав участников.
    participants_group = models.OneToOneField(
        EmployeesGroup,
        verbose_name='Группа прав участников',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='assignment_participants',
        related_query_name='assignment_participants'
    )
    # Переназначение.
    REASSIGNMENT = [
        ('', 'Выберите тип переназначения'),
        ('anyway', 'В любом случае'),
        ('not_completed', 'Если не прошел'),
        ('not_appoint', 'Если не проходил'),
    ]
    reassignment = models.CharField(max_length=255, choices=REASSIGNMENT, default='', verbose_name='Переназначение')
    # Это повтор.
    is_repeat = models.BooleanField(verbose_name='Это повтор', default=False)
    class Meta:
        # Изменение имени модели.
        verbose_name = 'Назначение'
        verbose_name_plural = 'Назначения'

    def __str__(self):
        try:
            if self.type == 'learning_complex':
                object = self.learning_complex
            if self.type == 'learning_path':
                object = self.learning_path
            if self.type == 'material':
                object = self.material
            if self.type == 'test':
                object = self.test
            if self.type == 'course':
                object = self.course
            if self.participants == 'group':
                participants = self.group
            if self.participants == 'employee':
                participants = self.employee

            return f'[{self.id}] {object} для {participants} с {self.planned_start_date.strftime("%d.%m.%Y")}'
        except (LearningComplex.DoesNotExist, LearningPath.DoesNotExist, Material.DoesNotExist, Test.DoesNotExist, Course.DoesNotExist):
            return f"[{self.id}] [не найдено] для {participants} с {self.planned_start_date.strftime('%d.%m.%Y')}"

# Назначение
class AssignmentRepeat(models.Model):
    # Дата и время создания и изменения.
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время создания', db_index=True)
    changed = models.DateTimeField(auto_now=True, verbose_name='Дата и время изменения', db_index=True)
    # Тип.
    TYPES = [
        ('', 'Выберите тип повтора'),
        ('daily', 'Ежедневно'),
        ('weekly', 'Еженедельно'),
        ('monthly', 'Ежемесячно'),
    ]
    type = models.CharField(max_length=255, choices=TYPES, default='no_repeat', verbose_name='Повтор')
    # Назначение.
    assignment = models.ForeignKey(
        Assignment,
        verbose_name='Назначение',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='repeats',
        related_query_name='repeats',
        db_index=True
    )
    # Создатель.
    creator = models.ForeignKey(
        Employee,
        verbose_name='Создатель',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='assignment_repeat_creators',
        related_query_name='assignment_repeat_creators'
    )
    # День повтора.
    DAYS_OF_WEEK = (
        ('', 'Выберите день повтора'),
        ('monday', 'Понедельник'),
        ('tuesday', 'Вторник'),
        ('wednesday', 'Среда'),
        ('thursday', 'Четверг'),
        ('friday', 'Пятница'),
        ('saturday', 'Суббота'),
        ('sunday', 'Воскресенье'),
    )
    day_of_week = models.CharField(
        max_length=255,
        choices=DAYS_OF_WEEK,
        default='',
        null=True,
        blank=True,
        verbose_name='День повтора'
    )
    # Интервал (месяцев).
    month_interval = models.IntegerField(verbose_name='Интервал (месяцев)', null=True, blank=True, default=1, validators=[MinValueValidator(1)])
    # Описание.
    desc = models.TextField(verbose_name='Описание', null=True, blank=True)
    # Дата последнего повтора.
    last_repeats_date = models.DateField(auto_now=False, verbose_name='Дата последнего выполнения', null=True, blank=True, db_index=True)
    class Meta:
        # Изменение имени модели.
        verbose_name = 'Повтор назначения'
        verbose_name_plural = 'Повтор назначения'

    def __str__(self):
        if self.type == 'daily':
            return f"[{self.id}] Ежедневно"
        if self.type == 'weekly':
            return f"[{self.id}] Еженедельно в {self.get_day_of_week_display()}"
        if self.type == 'monthly':
            return f"[{self.id}] Ежемесячно каждый {self.month_interval} месяц"

# Результат.
class Result(models.Model):
    # Тип.
    TYPES = [
        ('', 'Выберите тип результата'),
        ('learning_complex', 'Комплексная программа'),
        ('learning_path', 'Траектория обучения'),
        ('material', 'Материал'),
        ('test', 'Тест'),
        ('course', 'Курс'),
        ('event', 'Мероприятие'),
    ]
    type = models.CharField(max_length=255, choices=TYPES, default='', verbose_name='Тип')
    # Группа.
    assignment = models.ForeignKey(
        Assignment,
        verbose_name='Назначение',
        null=True,
        on_delete=models.CASCADE,
        related_name='results',
        related_query_name='results',
        db_index=True
    )
    # Сотрудник.
    employee = models.ForeignKey(
        Employee,
        verbose_name='Сотрудник',
        null=True,
        on_delete=models.CASCADE,
        related_name='results',
        related_query_name='results',
        db_index=True
    )
    # Планируемая дата конца.
    planned_end_date = models.DateField(auto_now=False, verbose_name='Планируемая дата завершения', null=True, blank=True, db_index=True)
    # Фактическая дата и время начала.
    start_date = models.DateTimeField(auto_now=False, null=True, blank=True, verbose_name='Дата начала', db_index=True)
    # Фактическая дата и время завершения.
    end_date = models.DateTimeField(auto_now=False, null=True, blank=True, verbose_name='Дата завершения', db_index=True)
    # Статус.
    STATUSES = [
        ('appointed', 'Назначено'),
        ('in_progress', 'В процессe'),
        ('completed', 'Пройдено'),
        ('failed', 'Провалено'),
        ('registered', 'Зарегистрирован'),
        ('refused', 'Отказался'),
        ('present', 'Присутствовал'),
        ('absent', 'Отсутствовал'),
    ]
    status = models.CharField(max_length=255, choices=STATUSES, default='appointed', verbose_name='Статус')
    # Cамоназначение.
    self_appointment = models.BooleanField(verbose_name='Caмоназначение', default=False)
    '''
    Для программ.
    '''
    # Траектория.
    learning_complex = models.ForeignKey(
        LearningComplex,
        verbose_name='Комплексная программа',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='results',
        related_query_name='results',
        db_index=True
    )
    '''
    Для траекторий.
    '''
    # Траектория.
    learning_path = models.ForeignKey(
        LearningPath,
        verbose_name='Траектория обучения',
        null=True, blank=True,
        on_delete=models.CASCADE,
        related_name='results',
        related_query_name='results',
        db_index=True
    )
    # Результат комплекса.
    learning_complex_result = models.ForeignKey(
        'self',
        verbose_name='Результат комплексной программы',
        null=True, blank=True,
        on_delete=models.CASCADE,
        related_name='complex_results',
        related_query_name='complex_results',
        db_index=True
    )
    completed_control_tasks = models.IntegerField(verbose_name='Выполнено контрольных задач', default=0)
    '''
    Для задач траекторий.
    '''
    # Задача.
    learning_task = models.ForeignKey(
        LearningTask,
        verbose_name='Учебная задача',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='results',
        related_query_name='results',
        db_index=True
    )
    # Результат траектории.
    learning_path_result = models.ForeignKey(
        'self',
        verbose_name='Результат траектории обучения',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='path_results',
        related_query_name='path_results',
        db_index=True
    )
    control_score = models.IntegerField(verbose_name='Выполнение контрольной задачи', default=0)
    '''
    Для материалов.
    '''
    # Результат материала.
    material = models.ForeignKey(
        Material,
        verbose_name='Материал',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='results',
        related_query_name='results',
        db_index=True
    )
    '''
    Для тестов.
    '''
    # Результат теста.
    test = models.ForeignKey(
        Test,
        verbose_name='Тест',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='results',
        related_query_name='results',
        db_index=True
    )
    # Балл.
    score = models.IntegerField(verbose_name='Балл', default=0)
    # Порядок вопросов.
    sorting_questions_results = models.TextField(verbose_name='Сортировка вопросов', null=True, blank=True)
    # Использовано попыток.
    attempts_used = models.IntegerField(verbose_name='Использовано попыток', default=0)
    # Время завершения попытки.
    attempt_end_time = models.DateTimeField(auto_now=False, null=True, blank=True, verbose_name='Время окончания попытки')
    '''
    Для курсов.
    '''
    # Результат курса.
    course = models.ForeignKey(
        Course,
        verbose_name='Курс',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='results',
        related_query_name='results',
        db_index=True
    )
    # Пакет.
    scorm_package = models.ForeignKey(
        ScormPackage,
        verbose_name='SCORM-пакет',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='results',
        related_query_name='results',
        db_index=True
    )
    # Прогресс.
    progress = models.TextField(verbose_name='Прогресс', default="{}")
    '''
    Для тестов и курсов.
    '''
    score_scaled = models.IntegerField(verbose_name='Полученный бал в %', default=0)
    '''
    Для мероприятий.
    '''
    # Вопрос статьи.
    event = models.ForeignKey(
        Event,
        verbose_name='Мероприятие',
        null=True,
        on_delete=models.CASCADE,
        related_name='results',
        related_query_name='results'
    )

    class Meta:
        # Изменение имени модели.
        verbose_name = 'Результат'
        verbose_name_plural = 'Результаты'
        # Добавление прав.
        permissions = (
            ('view_managed_result', 'Can view managed Результат'),
        )

    # Строкове представление.
    def __str__(self):
        if self.type == 'learning_complex':
            object = self.learning_complex
        if self.type == 'learning_path':
            object = self.learning_path
        if self.type == 'material':
            object = self.material
        if self.type == 'test':
            object = self.test
        if self.type == 'course':
            object = self.course
        if self.type == 'event':
            object = self.event
        if object:
            return f'{self.get_type_display()}: {object.name} | {self.employee} | {self.get_status_display()}'

# Результат вопроса.
class QuestionsResult(models.Model):
    # Результаты теста.
    tests_result = models.ForeignKey(
        Result,
        verbose_name='Результат теста',
        null=True,
        on_delete=models.CASCADE,
        related_name='questions_results',
        related_query_name='questions_results'
    )
    # Вопрос статьи.
    question = models.ForeignKey(
        Question,
        verbose_name='Вопрос',
        null=True,
        on_delete=models.PROTECT,
        related_name='results',
        related_query_name='results'
    )
    # Балл.
    score = models.IntegerField(verbose_name='Балл', default=0)
    # Статус.
    STATUSES = [
        ('appointed', 'Назначено'),
        ('in_progress', 'В процессe'),
        ('completed', 'Пройдено'),
        ('failed', 'Провалено'),
    ]
    status = models.CharField(max_length=255, choices=STATUSES, default='appointed', verbose_name='Статус')

    class Meta:
        # Изменение имени модели.
        verbose_name = 'Результат вопроса теста'
        verbose_name_plural = 'Результаты вопросов теста'

    # Строкове представление.
    def __str__(self):
        return f'[{self.id}] по вопросу {self.question.text} для {self.tests_result.employee} | {self.get_status_display()}'

# Результат ответа.
class AnswersResult(models.Model):
    # Результат вопроса.
    questions_result = models.ForeignKey(
        QuestionsResult,
        verbose_name='Результат вопроса',
        null=True,
        on_delete=models.CASCADE,
        related_name='answers_results',
        related_query_name='answers_results'
    )
    # Ответ.
    answer = models.ForeignKey(
        Answer,
        verbose_name='Ответ на вопрос',
        null=True,
        on_delete=models.PROTECT,
        related_name='results',
        related_query_name='results'
    )
    # Балл.
    score = models.IntegerField(verbose_name='Балл', default=0)
    # Ответ выбран.
    selected_answer = models.BooleanField(verbose_name='Правильный ответ', default=False)
    # Выбранная позиция.
    selected_position = models.IntegerField(verbose_name='Правильная позиция', null=True, blank=True, validators=[MinValueValidator(1)])
    # Введенный текст.
    selected_text_input = models.CharField(verbose_name='Правильный ответ', max_length=255, null=True, blank=True)
    # Введенное число.
    selected_numeric_input = models.IntegerField(verbose_name='Правильный ответ', null=True, blank=True)
    # Выбранный пункт.
    selected_relevant_point = models.ForeignKey(
        RelevantPoint,
        verbose_name='Соответствующий пункт',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='answers_results',
        related_query_name='answers_results'
    )
    # Статус.
    STATUSES = [
        ('appointed', 'Назначено'),
        ('in_progress', 'В процессe'),
        ('completed', 'Пройдено'),
        ('failed', 'Провалено'),
    ]
    status = models.CharField(max_length=255, choices=STATUSES, default='appointed', verbose_name='Статус')
    class Meta:
        # Изменение имени модели.
        verbose_name = 'Результат ответа на вопрос теста'
        verbose_name_plural = 'Результаты ответов на вопрос теста'

    # Строкове представление.
    def __str__(self):
        return f'По вопросу {self.questions_result.question.text} для {self.questions_result.tests_result.employee} | {self.get_status_display()}'



