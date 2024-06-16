# Импорт сериализатора и моделей.
from rest_framework import serializers
from .models import Employee, Organization, Subdivision, Position, Placement, EmployeesGroup

# Импортируем функцию get_random_string для генерации пароля.
from django.utils.crypto import get_random_string
# Импортируем функцию make_password из модуля auth.hashers. Используется для хеширования паролей.
from django.contrib.auth.hashers import make_password
# Импорт времени.
from datetime import date

# Импортируем логи
import logging
# Создаем логгер с именем 'project'
logger = logging.getLogger('project')


# Сериализатор сотрудника.
class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = [
            'id',  # Идентификатор пользователя.
            'mdm_id',  # MDM ID сотрудника.
            'avatar',  # Фото сотрудника.
            'username',  # Имя пользователя (логин).
            'email',  # Электронная почта.
            'first_name',  # Имя.
            'last_name',  # Фамилия.
            'fathers_name',  # Отчество.
            'phone',  # Телефон.
            'mobile_phone',  # Мобильный телефон.
            'birthday',  # Дата рождения.
            'created',  # Дата и время создания.
            'changed',  # Дата и время изменения.
            'creator',  # Кто создал учетную запись.
            'is_active',  # Активен ли пользователь.
            'is_staff',  # Член персонала.
            'is_superuser',  # Суперпользователь.
            'last_login',  # Последний вход.
            'date_joined',  # Дата регистрации.
        ]
        read_only_fields = [
            'id',
            'created',
            'changed',
            'creator',
            'last_login',
            'date_joined',
        ]

    # Метод создания.
    def create(self, validated_data):

        # Генерация случайного пароля.
        random_password = get_random_string(length=8)

        # Создание сотрудника.
        employee = Employee.objects.create(**validated_data)

        # Установка хешированного пароля.
        employee.set_password(random_password)
        logger.info(f"Добавлен сотрудник: {employee}")

        # Добавление сотрудника в группу, связанную с его импортом API.
        current_date = str(date.today().strftime('%d.%m.%Y'))
        group_name = f"Импорт через API от {current_date}"
        group, _ = EmployeesGroup.objects.get_or_create(name=group_name, type='employee_api_import')
        group.user_set.add(employee)
        logger.info(f"Сотрудник добавлен в группу: {group}")
        # Сохранение сотрудника.
        employee.save()

        return employee

# Сериализатор организации.
class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = '__all__'
        read_only_fields = [
            'id',
            'group',
            'created',
            'changed',
            'creator',
        ]

# Сериализатор подразделения.
class SubdivisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subdivision
        fields = '__all__'
        read_only_fields = [
            'id',
            'created',
            'group',
            'changed',
            'creator',
        ]

# Сериализатор должности.
class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = '__all__'
        read_only_fields = [
            'id',
            'created',
            'group',
            'changed',
            'creator',
        ]

# Сериализатор назначения должности.
class PlacementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Placement
        fields = '__all__'
        read_only_fields = [
            'id',
            'created',
            'changed',
            'creator',
        ]