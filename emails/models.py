from django.db import models

# Create your models here.

# Импорт моделей
from core.models import Employee, Category, EmployeesGroup
from learning_path.models import Assignment
from events.models import Event

# Рассылка.
class Email(models.Model):
    # Тип.
    TYPES = [
        ('', 'Выберите тип письма'),
        ('password', 'Пароль'),
        ('assignment', 'Назначение'),
        ('event', 'Мероприятие'),
    ]
    type = models.CharField(max_length=255, choices=TYPES, default='', verbose_name='Тип')
    # Создатель.
    creator = models.ForeignKey(
        Employee,
        verbose_name='Создатель',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='emails_creators',
        related_query_name='emails_creators'
    )
    # Категории.
    categories = models.ManyToManyField(
        Category,
        verbose_name='Категории',
        blank=True,
        related_name='emails',
        related_query_name='emails',
        db_index=True,
        help_text='Выберите категории'
    )
    # Группа.
    group = models.ForeignKey(
        EmployeesGroup,
        verbose_name='Группа',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='emails',
        related_query_name='emails',
        help_text='Выберите группу'
    )
    # Назначение.
    assignment = models.OneToOneField(
        Assignment,
        verbose_name='Назначение',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='emails',
        related_query_name='emails',
        help_text='Выберите назначение'
    )
    # Мероприятие.
    event = models.OneToOneField(
        Event,
        verbose_name='Мероприятие',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='emails',
        related_query_name='emails',
        help_text='Выберите мероприятие'
    )
    # Описание.
    desc = models.TextField(verbose_name='Описание', null=True, blank=True)
    # Дата и время создания и изменения.
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время создания', db_index=True)
    changed = models.DateTimeField(auto_now=True, verbose_name='Дата и время изменения', db_index=True)

    class Meta:
        # Изменение имени модели.
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'

    # Строкове представление.
    def __str__(self):
        category_list = []
        if self.categories.exists():
            for category in self.categories.all():
                category_list.append(f'{category.name}')
            category_str = ' | '.join(category_list)
            if self.type == 'password':
                return f'{self.get_type_display()} - {self.group} ({category_str})'
            if self.type == 'event':
                return f'{self.get_type_display()} - {self.event} ({category_str})'
            if self.type == 'assignment':
                return f'{self.get_type_display()} - {self.assignment} ({category_str})'
        else:
            if self.type == 'password':
                return f'{self.get_type_display()} - {self.group}'
            if self.type == 'event':
                return f'{self.get_type_display()} - {self.event}'
            if self.type == 'assignment':
                return f'{self.get_type_display()} - {self.assignment}'

# Результат.
class EmailsResult(models.Model):
    # Тип отправки.
    SENDING_TYPES = [
        ('', 'Выберите тип письма'),
        ('new', 'Новым адресатам'),
        ('all', 'Всем адресатам'),
    ]
    sending_type = models.CharField(max_length=64, choices=SENDING_TYPES, default='', verbose_name='Тип отправки')
    # Рассылка.
    email = models.ForeignKey(
        Email,
        verbose_name='Рассылка',
        on_delete=models.CASCADE,
        related_name='emails_results',
        related_query_name='emails_results'
    )
    # Адресат.
    employee = models.ForeignKey(
        Employee,
        verbose_name='Адресат',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='emails_employee',
        related_query_name='emails_employee'
    )
    # Дата и время создания и изменения.
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время создания', db_index=True)
    changed = models.DateTimeField(auto_now=True, verbose_name='Дата и время изменения', db_index=True)
    # Статус.
    STATUSES = [
        ('sending', 'Отправка'),
        ('sent', 'Отправлено'),
        ('not_sent', 'Не отправлено'),
    ]
    status = models.CharField(max_length=64, choices=STATUSES, default='sending', verbose_name='Статус')

    class Meta:
        # Изменение имени модели.
        verbose_name = 'Письмо'
        verbose_name_plural = 'Письмо'

    # Строкове представление.
    def __str__(self):
        return f'{self.employee} | {self.get_status_display()}'
