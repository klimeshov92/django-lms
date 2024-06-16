from django.db import models

# Create your models here.

# Импорт моделей.
from core.models import Employee
from learning_path.models import LearningPath
from materials.models import Material
from testing.models import Test
from courses.models import Course
from events.models import Event

# Импорт валидаторов
from django.core.validators import MinValueValidator, MaxValueValidator

# Класс отзыва.
class Review(models.Model):
    # Тип.
    TYPES = [
        ('', 'Выберите тип отзыва'),
        ('learning_path', 'Траектория обучения'),
        ('material', 'Материал'),
        ('course', 'Курс'),
        ('test', 'Тест'),
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
        related_name='reviews_creators',
        related_query_name='reviews_creators'
    )
    # Текст
    text = models.TextField(verbose_name='Текст', null=True, blank=True)
    # Балл от 0 до 10.
    score = models.IntegerField(
        verbose_name='Балл от 0 до 10',
        default=10,
        validators=[
            # Минимум 0.
            MinValueValidator(0),
            # Максимум 10.
            MaxValueValidator(10)
        ]
    )
    # Дата и время создания и изменения.
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время создания', db_index=True)
    changed = models.DateTimeField(auto_now=True, verbose_name='Дата и время изменения', db_index=True)
    '''
    Объекты.
    '''
    learning_path = models.ForeignKey(
        LearningPath,
        verbose_name='Траектория обучения',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='reviews',
        related_query_name='reviews',
    )
    material = models.ForeignKey(
        Material,
        verbose_name='Материал',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='reviews',
        related_query_name='reviews',
    )
    course = models.ForeignKey(
        Course,
        verbose_name='Курс',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='reviews',
        related_query_name='reviews',
    )
    test = models.ForeignKey(
        Test,
        verbose_name='Тест',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='reviews',
        related_query_name='reviews',
    )
    event = models.ForeignKey(
        Event,
        verbose_name='Мероприятие',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='reviews',
        related_query_name='reviews'
    )

    class Meta:
        # Изменение имени модели.
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        # Добавление прав.
        permissions = (
            ('view_all_review', 'Can view all Отзывы'),
        )

    # Строкове представление.
    def __str__(self):
        TYPES = [
            ('', 'Выберите тип отзыва'),
            ('learning_path', 'Траектория обучения'),
            ('material', 'Материал'),
            ('course', 'Курс'),
            ('test', 'Тест'),
            ('event', 'Мероприятие'),
        ]
        if self.type == 'learning_path':
            object = self.learning_path
            str = 'Траектория обучения'
        elif self.type == 'material':
            object = self.material
            str = 'Материал'
        elif self.type == 'course':
            object = self.course
            str = 'Курс'
        elif self.type == 'test':
            object = self.test
            str = 'Тест'
        elif self.type == 'event':
            object = self.event
            str = 'Мероприятие'
        return f'{str} {object}: {self.creator} - {self.score}'
