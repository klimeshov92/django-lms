
from django.db import models

# Create your models here.

# Импорт моделей
from core.models import Employee, Category, EmployeesGroup
from materials.models import Material, File
import datetime
from django.core.validators import MinValueValidator

# Мероприятие.
class Event(models.Model):
    # Тип.
    TYPES = [
        ('', 'Выберите тип мероприятия'),
        ('in-person', 'Очное мероприятие'),
        ('webinar', 'Вебинар'),
        ('in-person_and_webinar', 'Очное меропритяие + вебинар'),
    ]
    type = models.CharField(max_length=255, choices=TYPES, default='', verbose_name='Тип')
    # Создатель.
    creator = models.ForeignKey(
        Employee,
        verbose_name='Создатель',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='events_creators',
        related_query_name='events_creators'
    )
    # Категории.
    categories = models.ManyToManyField(
        Category,
        verbose_name='Категории',
        blank=True,
        related_name='events',
        related_query_name='events',
        db_index=True
    )
    # Название.
    name = models.CharField(verbose_name='Название', max_length=255, db_index=True)
    # Ссылка на вебинар.
    webinars_link = models.TextField(verbose_name='Ссылка на вебинар',  null=True, blank=True)
    # Место проведения.
    location = models.TextField(verbose_name='Место проведения', null=True, blank=True)
    # Участие обязательно.
    mandatory = models.BooleanField(verbose_name='Участие обязательно', default=False)
    # Отвественные.
    responsibles = models.ManyToManyField(
        Employee,
        verbose_name='Отвественные',
        related_name='events_responsibles',
        related_query_name='events_responsibles',
        db_index=True
    )
    # Время.
    date = models.DateField(auto_now=False, verbose_name='Дата', db_index=True)
    start_time = models.TimeField(auto_now=False, verbose_name='Время начала', db_index=True)
    end_time = models.TimeField(auto_now=False, verbose_name='Время завершения', db_index=True)
    # Бонус.
    bonus = models.IntegerField(verbose_name='Бонусы', default=10, validators=[MinValueValidator(0)])
    # Описание.
    desc = models.TextField(verbose_name='Описание', null=True, blank=True)
    # Материалы.
    materials = models.ManyToManyField(
        Material,
        verbose_name='Материалы',
        blank=True,
        related_name='events',
        related_query_name='events',
        db_index=True
    )
    # Материалы.
    files = models.ManyToManyField(
        File,
        verbose_name='Файлы',
        blank=True,
        related_name='events',
        related_query_name='events',
        db_index=True
    )
    # Группа отвественных.
    responsibles_group = models.OneToOneField(
        EmployeesGroup,
        verbose_name='Группа ведущих',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='events_responsibles',
        related_query_name='events_responsibles'
    )
    # Группа участников.
    participants_group = models.OneToOneField(
        EmployeesGroup,
        verbose_name='Группа участников',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='events_participants',
        related_query_name='events_participants'
    )
    # Статус.
    STATUSES = [
        ('planned', 'Планируется'),
        ('canceled', 'Отменено'),
        ('in_progress', 'В процессe'),
        ('completed', 'Завершено'),
    ]
    status = models.CharField(max_length=64, choices=STATUSES, default='planned', verbose_name='Статус')
    # Дата и время создания и изменения.
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время создания', db_index=True)
    changed = models.DateTimeField(auto_now=True, verbose_name='Дата и время изменения', db_index=True)
    # Cаморегистрация.
    self_appointment = models.BooleanField(verbose_name='Саморегистрация',default=False)

    class Meta:
        # Изменение имени модели.
        verbose_name = 'Мероприятие'
        verbose_name_plural = 'Мероприятия'

    # Строкове представление.
    def __str__(self):
        category_list = []
        if self.categories.exists():
            for category in self.categories.all():
                category_list.append(f'{category.name}')
            category_str = ' | '.join(category_list)
            return f'{self.name} - {self.date.strftime("%d.%m.%Y")} {self.start_time.strftime("%H:%M")}-{self.end_time.strftime("%H:%M")} ({category_str})'
        else:
            return f'{self.name} - {self.date.strftime("%d.%m.%Y")} {self.start_time.strftime("%H:%M")}-{self.end_time.strftime("%H:%M")}'

# Генератор участников.
class ParticipantsGenerator(models.Model):
    # Создатель.
    creator = models.ForeignKey(
        Employee,
        verbose_name='Создатель',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='participants_generator_creators',
        related_query_name='participants_generator_creators'
    )
    # Дата и время создания и изменения.
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время создания', db_index=True)
    changed = models.DateTimeField(auto_now=True, verbose_name='Дата и время изменения', db_index=True)
    # Группа
    event = models.OneToOneField(
        Event,
        verbose_name='Мероприятие',
        on_delete=models.CASCADE,
        related_name='participants_generator',
        related_query_name='participants_generator'
    )
    # Добавляемые и исключаемые сотрудники.
    added_groups = models.ManyToManyField(
        EmployeesGroup,
        verbose_name='Добавляемые группы',
        blank=True,
        related_name='added_participants_generators',
        related_query_name='added_participants_generators'
    )
    added_users = models.ManyToManyField(
        Employee,
        verbose_name='Добавляемые сотрудники',
        blank=True,
        related_name='added_participants_generators',
        related_query_name='added_participants_generators'
    )
    excluded_groups = models.ManyToManyField(
        EmployeesGroup,
        verbose_name='Исключаемые группы',
        blank=True,
        related_name='excluded_participants_generators',
        related_query_name='excluded_participants_generators'
    )
    excluded_users = models.ManyToManyField(
        Employee,
        verbose_name='Исключаемые сотрудники',
        blank=True,
        related_name='excluded_participants_generators',
        related_query_name='excluded_participants_generators'
    )
    # Дата начала работы.
    start_date_lte = models.DateField(verbose_name='Дата начала работы до или равна', null=True, blank=True)
    start_date_gte = models.DateField(verbose_name='Дата начала работы после или равна', null=True, blank=True)
    # Обновлять автоматически.
    autoupdate = models.BooleanField(verbose_name='Автообновление', default=False)
    class Meta:
        # Изменение имени модели.
        verbose_name = 'Генератор участников'
        verbose_name_plural = 'Генераторы участников'

    def __str__(self):
        # Возвращаем пользовательское строковое представление, например, имя группы.
        return f'{self.event.name}'

