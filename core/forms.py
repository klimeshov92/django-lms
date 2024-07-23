
from django import forms
from django.utils.safestring import mark_safe
from guardian.forms import GroupObjectPermissionsForm
from django.contrib.auth.models import Permission
from django_select2.forms import Select2Widget, Select2MultipleWidget
from .models import EmployeeExcelImport, Category, EmployeesGroup, Employee, \
    GroupsGenerator, EmployeesGroupObjectPermission, Placement, Organization, Subdivision, Position, EmployeesObjectPermission, \
    PrivacyPolicy, DataProcessing, Contacts
from django.contrib.contenttypes.models import ContentType
from materials.models import Material, File
from courses.models import Course
from testing.models import Test
from events.models import Event
from learning_path.models import LearningPath
from django.contrib.auth.forms import UserCreationForm
from ckeditor.widgets import CKEditorWidget


# Форма сотрудника.
class EmployeeForm(forms.ModelForm):
    class Meta:
        # Модель.
        model = Employee
        # Поля.
        fields = [
            'mdm_id',
            'avatar',
            'username',
            'last_name',
            'first_name',
            'fathers_name',
            'birthday',
            'email',
            'phone',
            'mobile_phone',
            'is_active',
            'user_permissions',
            'is_staff',
            'is_superuser',
            'creator'
            ]
        # Классы виджетов.
        widgets = {
            'creator': forms.HiddenInput(),
            'birthday': forms.DateInput(attrs={'type': 'date'}),
            'user_permissions': Select2MultipleWidget(),
        }

# Форма сотрудника.
class PersonalInfoForm(forms.ModelForm):
    class Meta:
        # Модель.
        model = Employee
        # Поля.
        fields = [
            'avatar',
            'username',
            'last_name',
            'first_name',
            'fathers_name',
            #'birthday',
            'email',
            #'phone',
            #'mobile_phone',
            'creator'
            ]
        # Классы виджетов.
        widgets = {
            'creator': forms.HiddenInput(),
            #'birthday': forms.DateInput(attrs={'type': 'date'})
        }

# Форма организации.
class OrganizationForm(forms.ModelForm):
    class Meta:
        # Модель.
        model = Organization
        # Поля.
        fields = [
            'mdm_id',
            'legal_name',
            'tin',
            'creator'
            ]
        # Классы виджетов.
        widgets = {
            'creator': forms.HiddenInput()
        }

# Форма подразделения.
class SubdivisionForm(forms.ModelForm):
    class Meta:
        # Модель.
        model = Subdivision
        # Поля.
        fields = [
            'mdm_id',
            'name',
            'organization',
            'parent_subdivision',
            'creator'
            ]
        # Классы виджетов.
        widgets = {
            'organization': Select2Widget(),
            'parent_subdivision': Select2Widget(),
            'creator': forms.HiddenInput()
        }

# Форма должности.
class PositionForm(forms.ModelForm):
    class Meta:
        # Модель.
        model = Position
        # Поля.
        fields = [
            'mdm_id',
            'name',
            'subdivision',
            'creator'
            ]
        # Классы виджетов.
        widgets = {
            'subdivision': Select2Widget(),
            'creator': forms.HiddenInput()
        }

# Форма назначения.
class PlacementForm(forms.ModelForm):
    class Meta:
        # Модель.
        model = Placement
        # Поля.
        fields = [
            'employee',
            'position',
            'manager',
            'start_date',
            'end_date',
            'creator'
            ]
        # Классы виджетов.
        widgets = {
            'employee': forms.HiddenInput(),
            'position': Select2Widget(),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'creator': forms.HiddenInput()
        }

# Форма создания импорта.
class EmployeeExcelImportForm(forms.ModelForm):
    class Meta:
        # Модель.
        model = EmployeeExcelImport
        # Поля.
        fields = [
            'type',
            'categories',
            'name',
            'creator',
            'upload_file',
            'desc',
        ]
        # Классы виджетов.
        widgets = {
            'type': forms.Select(),
            'creator': forms.HiddenInput(),
            'categories': Select2MultipleWidget()
        }

    # Особенность формы для апдейта.
    def __init__(self, *args, **kwargs):
        super(EmployeeExcelImportForm, self).__init__(*args, **kwargs)

        # Скрываем поле 'type'
        if self.instance and self.instance.pk:
            self.fields['upload_file'].widget = forms.HiddenInput(attrs={'disabled': 'disabled'})

# Форма создания категории.
class CategoryForm(forms.ModelForm):
    class Meta:
        # Модель.
        model = Category
        # Поля.
        fields = [
            'avatar',
            'creator',
            'name',
            'desc',
            'parent_category',
        ]
        # Классы виджетов.
        widgets = {
            'creator': forms.HiddenInput()
        }

# Форма группы.
class GroupForm(forms.ModelForm):
    class Meta:
        model = EmployeesGroup
        # Поля.
        fields = [
            'type',
            'name',
            #'employee',
            'permissions',
            'categories',
            'desc',
            'creator'
        ]
        # Классы виджетов.
        widgets = {
            'type': forms.HiddenInput(),
            'categories': Select2MultipleWidget(),
            'creator': forms.HiddenInput(),
            'permissions': Select2MultipleWidget()
        }

    # Инициализатор.
    def __init__(self, *args, **kwargs):

        # Вызываем инициализатор базового класса.
        super(GroupForm, self).__init__(*args, **kwargs)

        # Если это не кастомная группа.
        if self.instance.type != 'custom':

            # Не даем менять имя.
            self.fields['name'].widget = forms.HiddenInput()

        # Проверяем объект, связанный с этой формой.
        if self.instance.pk:  # Проверка, что это не новый объект

            # Устанавливаем начальное значение.
            # self.fields['type'].initial = self.instance.type
            #self.fields['employee'].initial = self.instance.user_set.all()
            self.fields['permissions'].initial = self.instance.permissions.all()
            #self.fields['name'].initial = self.instance.name
            #self.fields['categories'].initial = self.instance.categories.all()
            #self.fields['desc'].initial = self.instance.desc

    # Метод сохранения объекта формы.
    def save(self, commit=True):

        # Не проводим сохранение.
        group = super(GroupForm, self).save(commit=False)

        # Добавляем логигу для сохранения связанных объектов, чтобы использовать их в пост сейв сигнале.
        if commit:
            # Сохраняем сам объект.
            group.save()
            # Обновляем связанных сотрудников.
            #group.user_set.set(self.cleaned_data['employee'])
            # Обновляем права доступа.
            group.permissions.set(self.cleaned_data['permissions'])
            # Обновляем связи с категориями.
            group.categories.set(self.cleaned_data['categories'])

        # Возвращаем объект группы после сохранения/обновления.
        return group

# Форма создания генератора группы.
class GroupsGeneratorForm(forms.ModelForm):
    class Meta:
        # Модель.
        model = GroupsGenerator
        # Поля.
        fields = ['creator',
                  'group',
                  'added_groups',
                  'added_users',
                  'excluded_groups',
                  'excluded_users',
                  'days_worked_gte',
                  'days_worked_lte',
                  'autoupdate',
                  'creator'
        ]
        # Классы виджетов.
        widgets = {
            'creator': forms.HiddenInput(),
            'group': forms.HiddenInput(),
            'added_groups': Select2MultipleWidget(),
            'added_users': Select2MultipleWidget(),
            'excluded_groups': Select2MultipleWidget(),
            'excluded_users': Select2MultipleWidget()
        }

# Форма создания импорта.
class EmployeesGroupObjectPermissionForm(forms.ModelForm):
    class Meta:
        # Модель.
        model = EmployeesGroupObjectPermission
        # Поля.
        fields = [
            'permission',
            'content_type',
            'object_pk',
            'group',
            'creator'
        ]
        # Классы виджетов.
        widgets = {
            'permission': Select2Widget(),
            'content_type': forms.HiddenInput(),
            'object_pk': forms.HiddenInput(),
            'group': Select2Widget(),
            'creator': forms.HiddenInput()
        }
        # Названия полей.
        labels = {
            'permission': 'Права',
            'group': 'Группа',
        }

    def __init__(self, *args, **kwargs):

        # Извлекаем тип.
        type = kwargs.pop('type', None)

        # Создаем форму.
        super(EmployeesGroupObjectPermissionForm, self).__init__(*args, **kwargs)

        # Определяем перечень прав для выбора.
        if type == 'learning_path':
            content_type = ContentType.objects.get_for_model(LearningPath)
            self.fields['permission'].queryset = Permission.objects.filter(content_type_id=content_type.id).exclude(codename__startswith='add_')
        if type == 'material':
            content_type = ContentType.objects.get_for_model(Material)
            self.fields['permission'].queryset = Permission.objects.filter(content_type_id=content_type.id).exclude(codename__startswith='add_')
        if type == 'course':
            content_type = ContentType.objects.get_for_model(Course)
            self.fields['permission'].queryset = Permission.objects.filter(content_type_id=content_type.id).exclude(codename__startswith='add_')
        if type == 'test':
            content_type = ContentType.objects.get_for_model(Test)
            self.fields['permission'].queryset = Permission.objects.filter(content_type_id=content_type.id).exclude(codename__startswith='add_')
        if type == 'event':
            content_type = ContentType.objects.get_for_model(Event)
            self.fields['permission'].queryset = Permission.objects.filter(content_type_id=content_type.id).exclude(codename__startswith='add_')

# Форма создания импорта.
class EmployeesObjectPermissionForm(forms.ModelForm):
    class Meta:
        # Модель.
        model = EmployeesObjectPermission
        # Поля.
        fields = [
            'permission',
            'content_type',
            'object_pk',
            'user',
            'creator'
        ]
        # Классы виджетов.
        widgets = {
            'permission': Select2Widget(),
            'content_type': forms.HiddenInput(),
            'object_pk': forms.HiddenInput(),
            'user': Select2Widget(),
            'creator': forms.HiddenInput()
        }
        # Названия полей.
        labels = {
            'permission': 'Права',
            'user': 'Сотрудник',
        }

    def __init__(self, *args, **kwargs):

        # Извлекаем тип.
        type = kwargs.pop('type', None)

        # Создаем форму.
        super(EmployeesObjectPermissionForm, self).__init__(*args, **kwargs)

        # Определяем перечень прав для выбора.
        if type == 'learning_path':
            content_type = ContentType.objects.get_for_model(LearningPath)
            self.fields['permission'].queryset = Permission.objects.filter(content_type_id=content_type.id).exclude(codename__startswith='add_')
        if type == 'material':
            content_type = ContentType.objects.get_for_model(Material)
            self.fields['permission'].queryset = Permission.objects.filter(content_type_id=content_type.id).exclude(codename__startswith='add_')
        if type == 'course':
            content_type = ContentType.objects.get_for_model(Course)
            self.fields['permission'].queryset = Permission.objects.filter(content_type_id=content_type.id).exclude(codename__startswith='add_')
        if type == 'test':
            content_type = ContentType.objects.get_for_model(Test)
            self.fields['permission'].queryset = Permission.objects.filter(content_type_id=content_type.id).exclude(codename__startswith='add_')
        if type == 'event':
            content_type = ContentType.objects.get_for_model(Event)
            self.fields['permission'].queryset = Permission.objects.filter(content_type_id=content_type.id).exclude(codename__startswith='add_')


# Регистрация.
class SignUpForm(UserCreationForm):
    agree_to_privacy_policy = forms.BooleanField(
        required=True,
        label=mark_safe('Я согласен с <a href="/core/privacy_policy/" target="_blank">политикой конфиденциальности</a>')
    )
    agree_to_data_processing = forms.BooleanField(
        required=True,
        label=mark_safe('Я согласен на <a href="/core/data_processing/" target="_blank">обработку персональных данных</a>')
    )

    # Описание формы.
    class Meta:
        model = Employee
        fields = (
            'avatar',
            'username',
            'first_name',
            'last_name',
            'fathers_name',
            'email',
            'password1',
            'password2',
            'agree_to_privacy_policy',
            'agree_to_data_processing',
            'self_registration'
        )
        # Классы виджетов.
        widgets = {
            'self_registration': forms.HiddenInput()
        }

    # Подкрашивание обязательных полей.
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True
        for field_name, field in self.fields.items():
            if field.required:
                self.fields[field_name].label = mark_safe(f'{self.fields[field_name].label}<span class="required-label">*</span>')

# Форма создания контактов.
class ContactsForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget(), label='Содержание')
    class Meta:
        # Модель.
        model = Contacts
        # Поля.
        fields = [
            'creator',
            'name',
            'content'
        ]
        # Классы виджетов.
        widgets = {
            'creator': forms.HiddenInput()
        }

# Форма создания политики.
class PrivacyPolicyForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget(), label='Содержание')
    class Meta:
        # Модель.
        model = PrivacyPolicy
        # Поля.
        fields = [
            'creator',
            'name',
            'content'
        ]
        # Классы виджетов.
        widgets = {
            'creator': forms.HiddenInput()
        }

# Форма создания обработки.
class DataProcessingForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget(), label='Содержание')
    class Meta:
        # Модель.
        model = DataProcessing
        # Поля.
        fields = [
            'creator',
            'name',
            'content'
        ]
        # Классы виджетов.
        widgets = {
            'creator': forms.HiddenInput()
        }