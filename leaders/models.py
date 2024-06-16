from django.db import models

# Create your models here.
from django.db import models

# Create your models here.

# Импорт моделей.
from core.models import Employee
from learning_path.models import Result
from materials.models import Material
from testing.models import Test
from courses.models import Course
from events.models import Event

# Класс материала.
class Transaction(models.Model):
    # Тип.
    TYPES = [
        ('', 'Выберите тип отзыва'),
        ('material', 'Материал'),
        ('course', 'Курс'),
        ('test', 'Тест'),
        ('event', 'Мероприятие'),
    ]
    type = models.CharField(max_length=255, choices=TYPES, default='', verbose_name='Тип')
    # Сотрудник.
    employee = models.ForeignKey(
        Employee,
        verbose_name='Сотрудник',
        on_delete=models.CASCADE,
        related_name='transactions',
        related_query_name='transactions',
    )
    # Результат.
    result = models.ForeignKey(
        Result,
        verbose_name='Результат',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='transactions',
        related_query_name='transactions',
    )
    # Бонус.
    bonus = models.IntegerField(verbose_name='Бонус')
    # Дата и время создания и изменения.
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время создания', db_index=True)
    changed = models.DateTimeField(auto_now=True, verbose_name='Дата и время изменения', db_index=True)
    '''
    Объекты.
    '''
    material = models.ForeignKey(
        Material,
        verbose_name='Материал',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='transactions',
        related_query_name='transactions',
    )
    course = models.ForeignKey(
        Course,
        verbose_name='Курс',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='transactions',
        related_query_name='transactions',
    )
    test = models.ForeignKey(
        Test,
        verbose_name='Тест',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='transactions',
        related_query_name='transactions',
    )
    event = models.ForeignKey(
        Event,
        verbose_name='Мероприятие',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='transactions',
        related_query_name='transactions'
    )

    class Meta:
        # Изменение имени модели.
        verbose_name = 'Транзакция'
        verbose_name_plural = 'Транзакции'

    # Строкове представление.
    def __str__(self):
        return f'{self.result}: {self.bonus} бонусов - {self.created.strftime("%d.%m.%Y %H:%M")}'
