# Импорт форм.
from django import forms
# Импорт прав.
from guardian.forms import GroupObjectPermissionsForm
from django.contrib.auth.models import Permission
# Импорт select2.
from django_select2.forms import Select2Widget, Select2MultipleWidget
# Импорт моделей.
from .models import EmployeeExcelImport, Category, EmployeesGroup, Employee, \
    GroupsGenerator, EmployeesGroupObjectPermission, Placement, Organization, Subdivision, Position
from django.contrib.contenttypes.models import ContentType
from materials.models import Material, File
from courses.models import Course
from testing.models import Test
from events.models import Event


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
            'is_staff',
            'is_superuser',
            'creator'
            ]
        # Классы виджетов.
        widgets = {
            'creator': forms.HiddenInput(),
            'birthday': forms.DateInput(attrs={'type': 'date'}),
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
            'creator': forms.HiddenInput(),
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
            'creator': forms.HiddenInput(),
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
            'creator': forms.HiddenInput(),
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
            'creator': forms.HiddenInput(),
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
            'categories': Select2MultipleWidget(),
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
            'creator': forms.HiddenInput(),
        }

# Форма группы.
class GroupForm(forms.ModelForm):
    # Сотрудники. Убрано: не удобно при большом количестве людей. Есть генератор.
    #employee = forms.ModelMultipleChoiceField(
        #queryset=Employee.objects.all(),
        #widget=forms.HiddenInput(),
        #required=False,
        #label="Сотрудники"
    #)
    # Права доступа.
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        widget=Select2MultipleWidget(),
        required=False,
        label="Права доступа"
    )
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
        }

    # Инициализатор.
    def __init__(self, *args, **kwargs):

        # Вызываем инициализатор базового класса.
        super(GroupForm, self).__init__(*args, **kwargs)

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
                  'start_date_lte',
                  'start_date_gte',
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
            'excluded_users': Select2MultipleWidget(),
            'start_date_lte': forms.DateInput(attrs={'type': 'date'}),
            'start_date_gte': forms.DateInput(attrs={'type': 'date'}),
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
            'creator': forms.HiddenInput(),
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
        if type == 'material':
            content_type = ContentType.objects.get_for_model(Material)
            self.fields['permission'].queryset = Permission.objects.filter(content_type_id=content_type.id)
        if type == 'course':
            content_type = ContentType.objects.get_for_model(Course)
            self.fields['permission'].queryset = Permission.objects.filter(content_type_id=content_type.id)
        if type == 'test':
            content_type = ContentType.objects.get_for_model(Test)
            self.fields['permission'].queryset = Permission.objects.filter(content_type_id=content_type.id)
        if type == 'event':
            content_type = ContentType.objects.get_for_model(Event)
            self.fields['permission'].queryset = Permission.objects.filter(content_type_id=content_type.id)



