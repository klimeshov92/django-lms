
from django.db import models

# Create your models here.

# Импорт моделей
from core.models import Employee, Category
from django.core.validators import MinValueValidator


# Курс.
class Course(models.Model):
    # Картинка курса.
    avatar = models.ImageField(verbose_name='Аватар', null=True, blank=True, upload_to='courses_avatar/')
    # Тип.
    TYPES = [
        ('', 'Выберите тип файла'),
        ('ispring', 'Ispring'),
        ('articulate', 'Articulate'),
        ('scroll', 'Scroll'),
    ]
    type = models.CharField(max_length=255, choices=TYPES, default='', verbose_name='Тип')
    # Файл.
    zip_file = models.FileField(verbose_name='Zip-файл', upload_to='scorm_packages/')
    # Создатель.
    creator = models.ForeignKey(
        Employee,
        verbose_name='Создатель',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='courses_creators',
        related_query_name='courses_creators'
    )
    # Категории.
    categories = models.ManyToManyField(
        Category,
        verbose_name='Категории',
        blank=True,
        related_name='courses',
        related_query_name='courses',
        db_index=True
    )
    # Название.
    name = models.CharField(verbose_name='Название', max_length=255, db_index=True)
    # Авторы.
    authors = models.CharField(verbose_name='Авторы', null=True, blank=True, max_length=255)
    # Длительность.
    time_to_complete = models.IntegerField(verbose_name='Время на прохождение (минуты)', default=20, validators=[MinValueValidator(1)])
    # Бонус.
    bonus = models.IntegerField(verbose_name='Бонусы', default=100,  validators=[MinValueValidator(0)])
    # Описание.
    desc = models.TextField(verbose_name='Описание', null=True, blank=True)
    # Дата и время создания и изменения.
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время создания', db_index=True)
    changed = models.DateTimeField(auto_now=True, verbose_name='Дата и время изменения', db_index=True)
    # Cамоназначение.
    self_appointment = models.BooleanField(verbose_name='Caмоназначение', default=False)

    class Meta:
        # Изменение имени модели.
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'

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
