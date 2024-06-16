
from django.db import models
from django.core.validators import MinValueValidator

# Create your models here.

# Импорт пользователя и каталога.
from core.models import Employee, Category
# Импорт поля контента с возможностью загрузки файлов.
from ckeditor.fields import RichTextField

# Класс материала.
class Material(models.Model):
    # Картинка каталога.
    avatar = models.ImageField(verbose_name='Аватар', null=True, blank=True, upload_to='materials_avatar/')
    # Создатель.
    creator = models.ForeignKey(
        Employee,
        verbose_name='Создатель',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='materials_creators',
        related_query_name='materials_creators'
    )
    # Категории.
    categories = models.ManyToManyField(
        Category,
        verbose_name='Категории',
        blank=True,
        related_name='materials',
        related_query_name='materials',
        db_index=True
    )
    # Название.
    name = models.CharField(verbose_name='Название', max_length=255, db_index=True)
    # Авторы.
    authors = models.CharField(verbose_name='Авторы', null=True, blank=True, max_length=255)
    # Длительность.
    time_to_complete = models.IntegerField(verbose_name='Время на просмотр (минуты)', default=5, validators=[MinValueValidator(1)])
    # Бонус.
    bonus = models.IntegerField(verbose_name='Бонусы', default=10, validators=[MinValueValidator(0)])
    # Описание.
    desc = models.TextField(verbose_name='Описание', null=True, blank=True)
    # Контент
    content = RichTextField(verbose_name='Содержание', null=True, blank=True)
    # Дата и время создания и изменения.
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время создания', db_index=True)
    changed = models.DateTimeField(auto_now=True, verbose_name='Дата и время изменения', db_index=True)
    # Cамоназначение.
    self_appointment = models.BooleanField(verbose_name='Caмоназначение', default=False)

    class Meta:
        # Изменение имени модели.
        verbose_name = 'Материал'
        verbose_name_plural = 'Материалы'

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

class File(models.Model):
    # Тип.
    TYPES = [
        ('', 'Выберите тип файла'),
        ('image', 'Картинка'),
        ('video', 'Видео'),
        ('audio', 'Аудио'),
        ('document', 'Документ'),
    ]
    type = models.CharField(max_length=255, choices=TYPES, default='', verbose_name='Тип')
    # Создатель.
    creator = models.ForeignKey(
        Employee,
        verbose_name='Создатель',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='files_creators',
        related_query_name='files_creators'
    )
    # Категории.
    categories = models.ManyToManyField(
        Category,
        verbose_name='Категории',
        blank=True,
        related_name='files',
        related_query_name='files',
        db_index=True
    )
    # Название.
    name = models.CharField(verbose_name='Название', max_length=255, db_index=True)
    # Описание.
    desc = models.TextField(verbose_name='Описание', null=True, blank=True)
    # Файл.
    upload_file = models.FileField(verbose_name='Файл', upload_to='materials_files/')
    # Дата и время создания и изменения.
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время создания', db_index=True)
    changed = models.DateTimeField(auto_now=True, verbose_name='Дата и время изменения', db_index=True)

    class Meta:
        # Изменение имени модели.
        verbose_name = 'Файл'
        verbose_name_plural = 'Файлы'

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