from django.db import models

# Create your models here.
from core.models import Employee, Category, EmployeesGroup
# Импорт поля контента с возможностью загрузки файлов.
from ckeditor.fields import RichTextField
from django.core.validators import MinValueValidator

class Work(models.Model):
    # Картинка каталога.
    avatar = models.ImageField(verbose_name='Аватар', null=True, blank=True, upload_to='works_avatar/')
    # Создатель
    creator = models.ForeignKey(
        Employee,
        verbose_name='Создатель',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='works_creators',
        related_query_name='works_creators'
    )
    # Категории
    categories = models.ManyToManyField(
        Category,
        verbose_name='Категории',
        blank=True,
        related_name='works',
        related_query_name='works'
    )
    # Название
    name = models.CharField(verbose_name='Название', max_length=255, db_index=True)
    # Авторы.
    authors = models.CharField(verbose_name='Авторы', null=True, blank=True, max_length=255)
    # Длительность.
    time_to_complete = models.IntegerField(verbose_name='Время на выполнение (минуты)', default=5, validators=[MinValueValidator(1)])
    # Бонус.
    bonus = models.IntegerField(verbose_name='Бонусы', default=10, validators=[MinValueValidator(0)])
    # Описание
    desc = models.TextField(verbose_name='Описание', null=True, blank=True)
    # Инструкция
    manual = RichTextField(verbose_name='Инструкция', null=True, blank=True)
    # Требуется проверка
    require_review = models.BooleanField('Требуется проверка', default=False)
    # Дата и время создания и изменения.
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время создания', db_index=True)
    changed = models.DateTimeField(auto_now=True, verbose_name='Дата и время изменения', db_index=True)
    # Cамоназначение.
    self_appointment = models.BooleanField(verbose_name='Caмоназначение', default=False)

    class Meta:
        verbose_name = 'Работа'
        verbose_name_plural = 'Работа'
        default_permissions = ()
        permissions = (
            ('add_work', 'Может добавить работу'),
            ('change_work', 'Может изменить работу'),
            ('delete_work', 'Может удалить работу'),
            ('view_work', 'Может просматривать работу'),
        )

    # Строкове представление.
    def __str__(self):
        return f'{self.name}'