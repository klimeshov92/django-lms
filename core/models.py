# Create your models here.
from django.core.validators import MinValueValidator
from django.db import models
# Импорт расширенных прав.
from guardian.models import GroupObjectPermissionAbstract, UserObjectPermissionAbstract

# Импортируем класс пользователя для создания нестандартного пользователя.
from django.contrib.auth.models import AbstractUser
# Импортируем группы для создания нестандартной группы.
from django.contrib.auth.models import Group
# Импорт таймзоны.
from django.utils import timezone
# Импорт поля контента с возможностью загрузки файлов.
from ckeditor.fields import RichTextField

# Класс сотрудника на основе пользователя.
class Employee(AbstractUser):
    # Поля модели AbstractUser:
    # username;
    # password;
    # email;
    # first_name;
    # last_name;
    # is_active;
    # 'user_permissions';
    # is_staff;
    # is_superuser;
    # last_login;
    # date_joined.
    # Код элемента.
    mdm_id = models.CharField(verbose_name='MDM ID сотрудника', unique=True, null=True, blank=True, max_length=32)
    # Фото сотрудника.
    avatar = models.ImageField(verbose_name='Аватар', null=True, blank=True, upload_to='employees_avatar/')
    # Политики.
    agree_to_privacy_policy = models.BooleanField(default=False, verbose_name="Согласие с политикой конфиденциальности")
    agree_to_data_processing = models.BooleanField(default=False, verbose_name="Согласие на обработку персональных данных")
    # Подтверждение почты.
    email_confirmed = models.BooleanField(default=False, verbose_name="Подтверждение электронной почты")
    # Фамилия.
    fathers_name = models.CharField(verbose_name='Отчество', null=True, blank=True, max_length=255, db_index=True)
    # Телефон.
    phone = models.CharField(verbose_name='Телефон', null=True, blank=True, max_length=32)
    # Телефон мобильный.
    mobile_phone = models.CharField(verbose_name='Мобильный телефон', null=True, blank=True, max_length=32)
    # Дата рождения.
    birthday = models.DateField(verbose_name='Дата рождения', null=True, blank=True)
    # Дата и время создания и изменения.
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время создания', db_index=True)
    changed = models.DateTimeField(auto_now=True, verbose_name='Дата и время изменения', db_index=True)
    # Создатель.
    creator = models.ForeignKey(
        'self',
        verbose_name='Создатель',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='employees_creators',
        related_query_name='employees_creators'
    )
    # Cамоназначение.
    self_registration = models.BooleanField(verbose_name='Саморегистрация', default=False)

    class Meta:
        # Изменение имени модели.
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'
        # Добавление прав.
        permissions = (
            ('change_self_employee', 'Can change self Сотрудник'),
        )

    # Строковое представление.
    def __str__(self):
        positions_subdivisions_organizations_list = []
        for placement in self.placements.filter(end_date=None):
            positions_subdivisions_organizations_list.\
                append(f'{placement.position.name} - {placement.position.subdivision.name} - {placement.position.subdivision.organization.legal_name}')
        positions_subdivisions_organizations_str = ' | '.join(positions_subdivisions_organizations_list)
        if self.placements.exists():
            return f'{self.last_name} {self.first_name} ({positions_subdivisions_organizations_str})'
        elif self.last_name and self.first_name:
            return f'{self.last_name} {self.first_name}'
        else:
            return f'{self.username}'


# Класс каталога.
class Category(models.Model):
    # Картинка каталога.
    avatar = models.ImageField(verbose_name='Аватар', null=True, blank=True, upload_to='categories_avatar/')
    # Создатель.
    creator = models.ForeignKey(
        Employee,
        verbose_name='Создатель',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='categories_creators',
        related_query_name='categories_creators'
    )
    # Название.
    name = models.CharField(verbose_name='Название', max_length=255, db_index=True)
    # Описание.
    desc = models.TextField(verbose_name='Описание', null=True, blank=True)
    # Дата и время создания и изменения.
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время создания', db_index=True)
    changed = models.DateTimeField(auto_now=True, verbose_name='Дата и время изменения', db_index=True)
    # Родительский каталог.
    parent_category = models.ForeignKey(
        'self',
        verbose_name='Родительский каталог',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='categories',
        related_query_name='categories'
    )

    class Meta:
        # Изменение имени модели.
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    # Получение родительских категорий по цепочке.
    def get_parents_chain(self):
        # Возвращает строку с цепочкой всех родительских категорий.
        if self.parent_category:
            return f'{self.parent_category.get_parents_chain()} - {self.name}'
        else:
            return self.name

    # Строкове представление.
    def __str__(self):
        return f'{self.get_parents_chain()}'


# Переопределенная модель групп.
class EmployeesGroup(Group):
    # Тип.
    TYPES = [
        ('custom', 'Пользовательская'),
        ('system', 'Системная'),
        ('organization', 'Организация'),
        ('subdivision', 'Подразделение'),
        ('position', 'Должность'),
        ('employee_excel_import', 'Импорт сотрудников из Excel'),
        ('employee_api_import', 'Импорт сотрудников по API'),
        ('event_participants', 'Участники мероприятия'),
        ('event_responsibles', 'Ответственные мероприятия'),
        ('assignment', 'Назначение'),
    ]
    type = models.CharField(max_length=255, choices=TYPES, default='custom', verbose_name='Тип')
    # Категории.
    categories = models.ManyToManyField(
        Category,
        verbose_name='Категории',
        blank=True,
        related_name='employees_groups',
        related_query_name='employees_groups'
    )
    # Создатель.
    creator = models.ForeignKey(
        Employee,
        verbose_name='Создатель',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='employees_groups_creators',
        related_query_name='employees_groups_creators'
    )
    # Описание.
    desc = models.TextField(verbose_name='Описание', null=True, blank=True)

    class Meta:
        # Изменение имени модели.
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    # Строковое представление.
    def __str__(self):
        # Если это группа организации.
        if hasattr(self, 'organization'):
            return f'{self.name}'
        # Если это группа отдела.
        elif hasattr(self, 'subdivision'):
            return f'{self.name} - {self.subdivision.organization.legal_name}'
        # Если это группа должности.
        elif hasattr(self, 'position'):
            return f'{self.name} - {self.position.subdivision.name} | {self.position.subdivision.organization.legal_name}'
        # Иначе просто имя.
        else:
            return f' {self.name}'


# Генератор групп.
class GroupsGenerator(models.Model):
    # Создатель.
    creator = models.ForeignKey(
        Employee,
        verbose_name='Создатель',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='groups_generators_creators',
        related_query_name='groups_generators_creators'
    )
    # Дата и время создания и изменения.
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время создания', db_index=True)
    changed = models.DateTimeField(auto_now=True, verbose_name='Дата и время изменения', db_index=True)
    # Группа.
    group = models.OneToOneField(
        EmployeesGroup,
        verbose_name='Группа прав',
        on_delete=models.CASCADE,
        related_name='groups_generator',
        related_query_name='groups_generator')
    # Добавляемые и исключаемые сотрудники.
    added_groups = models.ManyToManyField(
        EmployeesGroup,
        verbose_name='Добавляемые группы',
        blank=True,
        related_name='added_groups_generators',
        related_query_name='added_groups_generators'
    )
    added_users = models.ManyToManyField(
        Employee,
        verbose_name='Добавляемые сотрудники',
        blank=True,
        related_name='added_users_generators',
        related_query_name='added_users_generators'
    )
    excluded_groups = models.ManyToManyField(
        EmployeesGroup,
        verbose_name='Исключаемые группы',
        blank=True,
        related_name='excluded_groups_generators',
        related_query_name='excluded_groups_generators'
    )
    excluded_users = models.ManyToManyField(
        Employee,
        verbose_name='Исключаемые сотрудники',
        blank=True,
        related_name='excluded_users_generators',
        related_query_name='excluded_users_generators'
    )
    # Дата начала работы.
    days_worked_gte = models.IntegerField(
        verbose_name='Отработано от (дней)',
        null=True,
        blank=True,
        default=0,
        validators=[MinValueValidator(0)]
    )
    days_worked_lte = models.IntegerField(
        verbose_name='Отработано до (дней)',
        null=True,
        blank=True,
        default=90,
        validators=[MinValueValidator(0)]
    )
    # Обновлять автоматически.
    autoupdate = models.BooleanField(verbose_name='Автообновление', default=False)

    class Meta:
        # Изменение имени модели.
        verbose_name = 'Генератор групп'
        verbose_name_plural = 'Генераторы групп'

    def __str__(self):
        # Возвращаем пользовательское строковое представление, например, имя группы.
        return f'{self.group.name}'


# Модель расширенных прав.
class EmployeesGroupObjectPermission(GroupObjectPermissionAbstract):
    # Создатель.
    creator = models.ForeignKey(
        Employee,
        verbose_name='Создатель',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='employees_group_object_permissions_creators',
        related_query_name='employees_group_object_permissions_creators'
    )
    class Meta:
        # Изменение имени модели.
        verbose_name = 'Права группы на объект'
        verbose_name_plural = 'Права группы на объекты'

    # Строковое представление.
    def __str__(self):
        return f'{self.group} - {self.permission}'

# Модель расширенных прав.
class EmployeesObjectPermission(UserObjectPermissionAbstract):
    # Создатель.
    creator = models.ForeignKey(
        Employee,
        verbose_name='Создатель',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='employees_object_permissions_creators',
        related_query_name='employees_object_permissions_creators'
    )
    class Meta:
        # Изменение имени модели.
        verbose_name = 'Права сотрудника на объект'
        verbose_name_plural = 'Права сотрудника на объекты'

    # Строковое представление.
    def __str__(self):
        return f'{self.user} - {self.permission}'

# Класс организации.
class Organization(models.Model):
    # Код элемента.
    mdm_id = models.CharField(verbose_name='MDM ID организации', unique=True, null=True, blank=True, max_length=32)
    # Название.
    legal_name = models.CharField(verbose_name='Юридическое название', max_length=255, db_index=True)
    # ИНН
    tin = models.CharField(verbose_name='ИНН организации', max_length=32)
    # Группа прав.
    group = models.OneToOneField(
        EmployeesGroup,
        verbose_name='Группа прав',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='organization',
        related_query_name='organization'
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
        related_name='organizations_creators',
        related_query_name='organizations_creators'
    )

    class Meta:
        # Изменение имени модели.
        verbose_name = 'Организация'
        verbose_name_plural = 'Организации'

    # Строковое представление.
    def __str__(self):
        return f'{self.legal_name}'


# Класс подразделения.
class Subdivision(models.Model):
    # Код элемента.
    mdm_id = models.CharField(verbose_name='MDM ID подразделения', unique=True, null=True, blank=True, max_length=32)
    # Название.
    name = models.CharField(verbose_name='Название', max_length=255, db_index=True)
    # Организация.
    organization = models.ForeignKey(
        Organization,
        verbose_name='Органиазция',
        on_delete=models.CASCADE,
        related_name='subdivisions',
        related_query_name='subdivisions'
    )
    # Главное подразделение.
    parent_subdivision = models.ForeignKey(
        'self',
        verbose_name='Главное подразделение',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='subdivisions',
        related_query_name='subdivisions'
    )
    # Группа прав.
    group = models.OneToOneField(
        EmployeesGroup,
        verbose_name='Группа прав',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='subdivision',
        related_query_name='subdivision'
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
        related_name='subdivisions_creators',
        related_query_name='subdivisions_creators'
    )

    class Meta:
        # Изменение имени модели.
        verbose_name = 'Подразделение'
        verbose_name_plural = 'Подразделения'

    # Строковое представление.
    def __str__(self):
        return f'{self.name} - {self.organization.legal_name}'


# Класс должности.
class Position(models.Model):
    # Код элемента.
    mdm_id = models.CharField(verbose_name='MDM ID должности', unique=True, null=True, blank=True, max_length=32)
    # Название.
    name = models.CharField(verbose_name='Название', max_length=255, db_index=True)
    # Подразделение.
    subdivision = models.ForeignKey(
        Subdivision,
        verbose_name='Подразделение',
        on_delete=models.CASCADE,
        related_name='positions',
        related_query_name='positions'
    )
    # Группа прав.
    group = models.OneToOneField(
        EmployeesGroup,
        verbose_name='Группа прав',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='position',
        related_query_name='position'
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
        related_name='positions_creators',
        related_query_name='positions_creators'
    )

    class Meta:
        # Изменение имени модели.
        verbose_name = 'Должность'
        verbose_name_plural = 'Должности'

    # Строковое представление.
    def __str__(self):
        return f'{self.name} - {self.subdivision.name} - {self.subdivision.organization.legal_name}'

# Назначение.
class Placement(models.Model):
    # Сотрудник.
    employee = models.ForeignKey(
        Employee,
        verbose_name='Сотрудник',
        on_delete=models.PROTECT,
        related_name='placements',
        related_query_name='placements'
    )
    # Должность.
    position = models.ForeignKey(
        Position,
        verbose_name='Должность',
        on_delete=models.PROTECT,
        related_name='placements',
        related_query_name='placements'
    )
    # Руководитель в подразделении.
    manager = models.BooleanField(verbose_name='Руководитель', default=False)
    # Дата начала работы.
    start_date = models.DateField(verbose_name='Дата начала работы', null=True, blank=True)
    # Дата окончания работы.
    end_date = models.DateField(
        verbose_name='Дата окончания работы',
        null=True,
        blank=True
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
        related_name='placements_creators',
        related_query_name='placements_creators'
    )

    class Meta:
        # Изменение имени модели.
        verbose_name = 'Должность сотрудника'
        verbose_name_plural = 'Должности сотрудников'

    # Строковое представление.
    def __str__(self):
        return f'{self.employee.last_name} {self.employee.first_name} | ' \
               f'{self.position.name} - {self.position.subdivision.name} - {self.position.subdivision.organization.legal_name}'

# Модель для импорта сотрудников.
class EmployeeExcelImport(models.Model):
    # Типы.
    TYPES = [
        ('', 'Выберите тип импорта'),
        ('mdm', 'C MDM ID'),
        ('name', 'Только и именами'),
    ]
    type = models.CharField(max_length=255, choices=TYPES, default='', verbose_name='Тип')
    # Категории.
    categories = models.ManyToManyField(
        Category,
        verbose_name='Категории',
        blank=True,
        related_name='employee_excel_imports',
        related_query_name='employee_excel_imports'
    )
    # Название.
    name = models.CharField(verbose_name='Название', max_length=255)
    # Создатель.
    creator = models.ForeignKey(
        Employee,
        verbose_name='Создатель',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='employee_excel_import_creators',
        related_query_name='employee_excel_import_creators'
    )
    # Загруженный файл.
    upload_file = models.FileField(verbose_name='Excel-файл', upload_to='employee_excel_import/')
    # Описание.
    desc = models.TextField(verbose_name='Описание', null=True, blank=True)
    # Дата и время создания и изменения.
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время создания', db_index=True)
    changed = models.DateTimeField(auto_now=True, verbose_name='Дата и время изменения', db_index=True)
    # Обработан.
    processed = models.BooleanField(verbose_name='Обработан', default=False)
    # Загруженные сотрудники.
    group = models.OneToOneField(
        EmployeesGroup,
        verbose_name='Загруженные сотрудники',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='employee_excel_import',
        related_query_name='employee_excel_import')

    class Meta:
        # Изменение имени модели.
        verbose_name = 'Импорт из Excel'
        verbose_name_plural = 'Импорты из Excel'

    # Строковое представление.
    def __str__(self):
        return f'{self.name} | {self.created.astimezone(timezone.get_current_timezone())}'

# Класс контактов.
class Contacts(models.Model):
    # Создатель.
    creator = models.ForeignKey(
        Employee,
        verbose_name='Создатель',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='сontacts_creator',
        related_query_name='сontacts_creator'
    )
    # Название.
    name = models.CharField(verbose_name='Название', max_length=255, db_index=True)
    # Контент
    content = RichTextField(verbose_name='Содержание', null=True, blank=True)
    # Дата и время создания и изменения.
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время создания', db_index=True)
    changed = models.DateTimeField(auto_now=True, verbose_name='Дата и время изменения', db_index=True)

    class Meta:
        # Изменение имени модели.
        verbose_name = 'Контакты'
        verbose_name_plural = 'Контакты'

    # Ограничение одной записью.
    def save(self, *args, **kwargs):
        if not self.pk and Contacts.objects.exists():
            raise ValueError("Может быть только одна запись в модели Contacts")
        return super().save(*args, **kwargs)

# Класс политики.
class PrivacyPolicy(models.Model):
    # Создатель.
    creator = models.ForeignKey(
        Employee,
        verbose_name='Создатель',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='privacy_policy_creator',
        related_query_name='privacy_policy_creator'
    )
    # Название.
    name = models.CharField(verbose_name='Название', max_length=255, db_index=True)
    # Контент
    content = RichTextField(verbose_name='Содержание', null=True, blank=True)
    # Дата и время создания и изменения.
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время создания', db_index=True)
    changed = models.DateTimeField(auto_now=True, verbose_name='Дата и время изменения', db_index=True)

    class Meta:
        # Изменение имени модели.
        verbose_name = 'Политика конфиденциальности'
        verbose_name_plural = 'Политики конфиденциальности'

    # Ограничение одной записью.
    def save(self, *args, **kwargs):
        if not self.pk and PrivacyPolicy.objects.exists():
            raise ValueError("Может быть только одна запись в модели PrivacyPolicy")
        return super().save(*args, **kwargs)


# Класс обработки.
class DataProcessing(models.Model):
    # Создатель.
    creator = models.ForeignKey(
        Employee,
        verbose_name='Создатель',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='data_processing_creator',
        related_query_name='data_processing_creator'
    )
    # Название.
    name = models.CharField(verbose_name='Название', max_length=255, db_index=True)
    # Контент
    content = RichTextField(verbose_name='Содержание', null=True, blank=True)
    # Дата и время создания и изменения.
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время создания', db_index=True)
    changed = models.DateTimeField(auto_now=True, verbose_name='Дата и время изменения', db_index=True)

    class Meta:
        # Изменение имени модели.
        verbose_name = 'Политика в области обработки персональных данных'
        verbose_name_plural = 'Политика в области обработки персональных данных'

    # Ограничение одной записью.
    def save(self, *args, **kwargs):
        if not self.pk and DataProcessing.objects.exists():
            raise ValueError("Может быть только одна запись в модели DataProcessing")
        return super().save(*args, **kwargs)