# Импорт пути.
from django.urls import  include, path
# Импорт представления.
from .views import EmployeeExcelImportsView, EmployeeExcelImportView, \
   start_employee_excel_import_mdm_view, start_employee_excel_import_name_view, \
   EmployeeExcelImportCreateView, EmployeeExcelImportUpdateView, EmployeeExcelImportDeleteView,\
   CategoriesView, CategoryView, CategoryCreateView, CategoryUpdateView, CategoryDeleteView,\
   GroupsView, GroupView, GroupCreateView, GroupUpdateView, GroupDeleteView, \
   GroupsGeneratorCreateView, GroupsGeneratorUpdateView, \
   EmployeesGroupObjectPermissionCreateView, EmployeesGroupObjectPermissionDeleteView, \
   copy_emails, EmployeesView, EmployeeView, EmployeeCreateView, EmployeeUpdateView, EmployeeDeleteView, \
   PlacementCreateView, PlacementUpdateView, PlacementDeleteView, \
   OrganizationsView, OrganizationView, OrganizationCreateView, OrganizationUpdateView, OrganizationDeleteView, \
   SubdivisionsView, SubdivisionView, SubdivisionCreateView, SubdivisionUpdateView, SubdivisionDeleteView, \
   PositionsView, PositionView,PositionCreateView, PositionUpdateView, PositionDeleteView, update_password, \
   EmployeesObjectPermissionCreateView, EmployeesObjectPermissionDeleteView, PersonalArea, PersonalInfoUpdateView, \
   PrivacyPolicyView, PrivacyPolicyCreateView, PrivacyPolicyUpdateView, \
   DataProcessingView, DataProcessingCreateView, DataProcessingUpdateView, \
   ContactsView, ContactsCreateView, ContactsUpdateView

from rest_framework.routers import DefaultRouter
from .views import EmployeeViewSet, OrganizationViewSet, SubdivisionViewSet, PlacementViewSet, PositionViewSet

# Имя приложения в адресах.
app_name = 'core'

# Роутер вьюсета.
router = DefaultRouter()
router.register(r'employees', EmployeeViewSet)  # Регистрация маршрута для сотрудников
router.register(r'organizations', OrganizationViewSet)  # Регистрация маршрута для организаций
router.register(r'subdivisions', SubdivisionViewSet)  # Регистрация маршрута для подразделений
router.register(r'positions', PositionViewSet)  # Регистрация маршрута для должностей
router.register(r'placements', PlacementViewSet)  # Регистрация маршрута для назначений


'''
Когда вы используете DefaultRouter и регистрируете EmployeeViewSet, роутер автоматически создает стандартные маршруты для CRUD-операций. 
Вот какие маршруты генерируются:
Список (GET /employees/): Позволяет получить список всех объектов.
Детальный просмотр (GET /employees/<pk>/): Позволяет получить детали одного объекта по его первичному ключу (pk).
Создание (POST /employees/): Позволяет создать новый объект.
Полное обновление (PUT /employees/<pk>/): Позволяет полностью обновить объект.
Частичное обновление (PATCH /employees/<pk>/): Позволяет частично обновить объект.
Удаление (DELETE /employees/<pk>/): Позволяет удалить объект по первичному ключу.
'''

'''
Примеры запросов для пользователей: 
curl -X GET http://127.0.0.1:8000/core/api/employees/
    -H "Authorization: Api-Key tU8pcXVO.1RUAQAmmppKz6PAd0tmEhgd78UDhj8Jx"
curl -X GET http://127.0.0.1:8000/core/api/employees/1/
    -H "Authorization: Api-Key tU8pcXVO.1RUAQAmmppKz6PAd0tmEhgd78UDhj8Jx"
curl -X POST http://127.0.0.1:8000/core/api/employees/ \
    -H "Authorization: Api-Key tU8pcXVO.1RUAQAmmppKz6PAd0tmEhgd78UDhj8Jx"
    -H "Content-Type: application/json" \
    -d '{
        "mdm_id": "10",
        "username": "semen@example.com",
        "email": "semen@example.com",
        "first_name": "Семен",
        "last_name": "Семенович",
        "fathers_name": "Семенов",
        "phone": "1234567890",
        "mobile_phone": "0987654321",
        "birthday": "1990-01-01",
        "is_active": true,
        "is_staff": false,
        "is_superuser": false
    }'
curl -X PUT http://127.0.0.1:8000/core/api/employees/1/ \
    -H "Authorization: Api-Key tU8pcXVO.1RUAQAmmppKz6PAd0tmEhgd78UDhj8Jx"
    -H "Content-Type: application/json" \
    -d '{
        "mdm_id": "10",
        "username": "semen@example.com",
        "email": "semen@example.com",
        "first_name": "Семен",
        "last_name": "Семенович",
        "fathers_name": "Семенов",
        "phone": "1234567890",
        "mobile_phone": "0987654321",
        "birthday": "1990-01-01",
        "is_active": false,
        "is_staff": false,
        "is_superuser": false
    }'
curl -X PATCH http://127.0.0.1:8000/core/api/employees/1/ \
    -H "Authorization: Api-Key tU8pcXVO.1RUAQAmmppKz6PAd0tmEhgd78UDhj8Jx"
    -H "Content-Type: application/json" \
    -d '{
        "email": "semenov@example.com"
    }'
curl -X DELETE http://127.0.0.1:8000/core/api/employees/1/
    -H "Authorization: Api-Key tU8pcXVO.1RUAQAmmppKz6PAd0tmEhgd78UDhj8Jx"
'''
'''
Примеры запросов для организаций:
curl -X GET http://127.0.0.1:8000/core/api/organizations/
    -H "Authorization: Api-Key tU8pcXVO.1RUAQAmmppKz6PAd0tmEhgd78UDhj8Jx"
curl -X GET http://127.0.0.1:8000/core/api/organizations/1/
    -H "Authorization: Api-Key tU8pcXVO.1RUAQAmmppKz6PAd0tmEhgd78UDhj8Jx"
curl -X POST http://127.0.0.1:8000/core/api/organizations/ \
    -H "Authorization: Api-Key tU8pcXVO.1RUAQAmmppKz6PAd0tmEhgd78UDhj8Jx"
    -H "Content-Type: application/json" \
    -d '{
        "mdm_id": "20",
        "legal_name": "Компания ABC",
        "tin": "123456789"
    }'
curl -X PUT http://127.0.0.1:8000/core/api/organizations/1/ \
    -H "Authorization: Api-Key tU8pcXVO.1RUAQAmmppKz6PAd0tmEhgd78UDhj8Jx"
    -H "Content-Type: application/json" \
    -d '{
        "mdm_id": "20",
        "legal_name": "Компания ABC",
        "tin": "987654321"
    }'
curl -X PATCH http://127.0.0.1:8000/core/api/organizations/1/ \
    -H "Authorization: Api-Key tU8pcXVO.1RUAQAmmppKz6PAd0tmEhgd78UDhj8Jx"
    -H "Content-Type: application/json" \
    -d '{
        "legal_name": "Новая Компания"
    }'
curl -X DELETE http://127.0.0.1:8000/core/api/organizations/1/
    -H "Authorization: Api-Key tU8pcXVO.1RUAQAmmppKz6PAd0tmEhgd78UDhj8Jx"
'''
'''
Примеры запросов для подразделений:
curl -X GET http://127.0.0.1:8000/core/api/subdivisions/
    -H "Authorization: Api-Key tU8pcXVO.1RUAQAmmppKz6PAd0tmEhgd78UDhj8Jx"
curl -X GET http://127.0.0.1:8000/core/api/subdivisions/1/
    -H "Authorization: Api-Key tU8pcXVO.1RUAQAmmppKz6PAd0tmEhgd78UDhj8Jx"
curl -X POST http://127.0.0.1:8000/core/api/subdivisions/ \
    -H "Authorization: Api-Key tU8pcXVO.1RUAQAmmppKz6PAd0tmEhgd78UDhj8Jx"
    -H "Content-Type: application/json" \
    -d '{
        "mdm_id": "30",
        "name": "Отдел продаж",
        "organization": 1,
        "parent_subdivision": null
    }'
curl -X PUT http://127.0.0.1:8000/core/api/subdivisions/1/ \
    -H "Authorization: Api-Key tU8pcXVO.1RUAQAmmppKz6PAd0tmEhgd78UDhj8Jx"
    -H "Content-Type: application/json" \
    -d '{
        "mdm_id": "30",
        "name": "Отдел маркетинга",
        "organization": 1,
        "parent_subdivision": 3
    }'
curl -X PATCH http://127.0.0.1:8000/core/api/subdivisions/1/ \
    -H "Authorization: Api-Key tU8pcXVO.1RUAQAmmppKz6PAd0tmEhgd78UDhj8Jx"
    -H "Content-Type: application/json" \
    -d '{
        "name": "Отдел исследований"
    }'
curl -X DELETE http://127.0.0.1:8000/core/api/subdivisions/1/
    -H "Authorization: Api-Key tU8pcXVO.1RUAQAmmppKz6PAd0tmEhgd78UDhj8Jx"
'''
'''
Примеры запросов для должностей:
curl -X GET http://127.0.0.1:8000/core/api/positions/
    -H "Authorization: Api-Key tU8pcXVO.1RUAQAmmppKz6PAd0tmEhgd78UDhj8Jx"
curl -X GET http://127.0.0.1:8000/core/api/positions/1/
    -H "Authorization: Api-Key tU8pcXVO.1RUAQAmmppKz6PAd0tmEhgd78UDhj8Jx"
curl -X POST http://127.0.0.1:8000/core/api/positions/ \
    -H "Authorization: Api-Key tU8pcXVO.1RUAQAmmppKz6PAd0tmEhgd78UDhj8Jx"
    -H "Content-Type: application/json" \
    -d '{
        "mdm_id": "50",
        "name": "Менеджер по продажам",
        "subdivision": 1,
    }'
curl -X PUT http://127.0.0.1:8000/core/api/positions/1/ \
    -H "Authorization: Api-Key tU8pcXVO.1RUAQAmmppKz6PAd0tmEhgd78UDhj8Jx"
    -H "Content-Type: application/json" \
    -d '{
        "mdm_id": "50",
        "name": "Старший менеджер по продажам",
        "subdivision": 2,
    }'
curl -X PATCH http://127.0.0.1:8000/core/api/positions/1/ \
    -H "Authorization: Api-Key tU8pcXVO.1RUAQAmmppKz6PAd0tmEhgd78UDhj8Jx"
    -H "Content-Type: application/json" \
    -d '{
        "name": "Старший менеджер"
    }'
curl -X DELETE http://127.0.0.1:8000/core/api/positions/1/
    -H "Authorization: Api-Key tU8pcXVO.1RUAQAmmppKz6PAd0tmEhgd78UDhj8Jx"
'''
'''
Примеры запросов для назначений на должность:
curl -X GET http://127.0.0.1:8000/core/api/placements/
    -H "Authorization: Api-Key tU8pcXVO.1RUAQAmmppKz6PAd0tmEhgd78UDhj8Jx"
curl -X GET http://127.0.0.1:8000/core/api/placements/1/
    -H "Authorization: Api-Key tU8pcXVO.1RUAQAmmppKz6PAd0tmEhgd78UDhj8Jx"
curl -X POST http://127.0.0.1:8000/core/api/placements/ \
    -H "Authorization: Api-Key tU8pcXVO.1RUAQAmmppKz6PAd0tmEhgd78UDhj8Jx"
    -H "Content-Type: application/json" \
    -d '{
        "employee": 1,
        "position": 1,
        "manager": false,
        "start_date": "2024-01-01"
    }'
curl -X PUT http://127.0.0.1:8000/core/api/placements/1/ \
    -H "Authorization: Api-Key tU8pcXVO.1RUAQAmmppKz6PAd0tmEhgd78UDhj8Jx"
    -H "Content-Type: application/json" \
    -d '{
        "employee": 1,
        "position": 1,
        "manager": true,
        "start_date": "2024-01-01"
    }'
curl -X PATCH http://127.0.0.1:8000/core/api/placements/1/ \
    -H "Authorization: Api-Key tU8pcXVO.1RUAQAmmppKz6PAd0tmEhgd78UDhj8Jx"
    -H "Content-Type: application/json" \
    -d '{
        "end_date": "2024-01-01"
    }'
curl -X DELETE http://127.0.0.1:8000/core/api/placements/1/
    -H "Authorization: Api-Key tU8pcXVO.1RUAQAmmppKz6PAd0tmEhgd78UDhj8Jx"
'''

# Список маршрутов приложения.
urlpatterns = [
   # Подключаем все маршруты, которые создал роутер
   path('api/', include(router.urls)),
   # Маршрут вывода списка сотрудников.
   path('employees/', EmployeesView.as_view(), name='employees'),
   # Маршрут вывода сотрудника.
   path('employees/<int:pk>/', EmployeeView.as_view(), name='employee'),
   path('personal_area/', PersonalArea.as_view(), name='personal_area'),
   # Маршрут обновления пароля.
   path('employees/<int:pk>/update_password', update_password, name='update_password'),
   # Маршрут создания сотрудника.
   path('employees/create/', EmployeeCreateView.as_view(), name='employee_create'),
   # Маршрут обновления сотрудника.
   path('employees/<int:pk>/update/', EmployeeUpdateView.as_view(), name='employee_update'),
   path('personal_info/update/', PersonalInfoUpdateView.as_view(), name='personal_info_update'),
   # Маршрут удаления сотрудника.
   path('employees/<int:pk>/delete/', EmployeeDeleteView.as_view(), name='employee_delete'),
   # Маршрут вывода списка организаций.
   path('organizations/', OrganizationsView.as_view(), name='organizations'),
   # Маршрут вывода организации.
   path('organizations/<int:pk>/', OrganizationView.as_view(), name='organization'),
   # Маршрут создания организации.
   path('organizations/create/', OrganizationCreateView.as_view(), name='organization_create'),
   # Маршрут обновления организации.
   path('organizations/<int:pk>/update/', OrganizationUpdateView.as_view(), name='organization_update'),
   # Маршрут удаления организации.
   path('organizations/<int:pk>/delete/', OrganizationDeleteView.as_view(), name='organization_delete'),
   # Маршрут вывода списка подразделений.
   path('subdivisions/', SubdivisionsView.as_view(), name='subdivisions'),
   # Маршрут вывода подразделения.
   path('subdivisions/<int:pk>/', SubdivisionView.as_view(), name='subdivision'),
   # Маршрут создания подразделения.
   path('subdivisions/create/', SubdivisionCreateView.as_view(), name='subdivision_create'),
   # Маршрут обновления подразделения.
   path('subdivisions/<int:pk>/update/', SubdivisionUpdateView.as_view(), name='subdivision_update'),
   # Маршрут удаления подразделения.
   path('subdivisions/<int:pk>/delete/', SubdivisionDeleteView.as_view(), name='subdivision_delete'),
   # Маршрут вывода списка должностей.
   path('positions/', PositionsView.as_view(), name='positions'),
   # Маршрут вывода должности.
   path('positions/<int:pk>/', PositionView.as_view(), name='position'),
   # Маршрут создания должности.
   path('positions/create/', PositionCreateView.as_view(), name='position_create'),
   # Маршрут обновления должности.
   path('positions/<int:pk>/update/', PositionUpdateView.as_view(), name='position_update'),
   # Маршрут удаления должности.
   path('positions/<int:pk>/delete/', PositionDeleteView.as_view(), name='position_delete'),
   # Маршрут создания назначения.
   path('employees/<int:pk>/placements/create/', PlacementCreateView.as_view(), name='placement_create'),
   # Маршрут обновления назначения.
   path('placements/<int:pk>/update/', PlacementUpdateView.as_view(), name='placement_update'),
   # Маршрут удаления назначения.
   path('placements/<int:pk>/delete/', PlacementDeleteView.as_view(), name='placement_delete'),
   # Маршрут вывода списка импортов.
   path('employee_excel_imports/', EmployeeExcelImportsView.as_view(), name='employee_excel_imports'),
   # Маршрут вывода импорта.
   path('employee_excel_imports/<int:pk>/', EmployeeExcelImportView.as_view(), name='employee_excel_import'),
   # Маршрут создания импорта.
   path('employee_excel_imports/create/', EmployeeExcelImportCreateView.as_view(), name='employee_excel_import_create'),
   # Маршрут обновления импорта.
   path('employee_excel_imports/<int:pk>/update/', EmployeeExcelImportUpdateView.as_view(), name='employee_excel_import_update'),
   # Маршрут удаления импорта.
   path('employee_excel_imports/<int:pk>/delete/', EmployeeExcelImportDeleteView.as_view(), name='employee_excel_import_delete'),
   # Маршрут запуска импорта из mdm.
   path('employee_excel_imports/<int:pk>/start_employee_excel_import_mdm/', start_employee_excel_import_mdm_view, name='start_employee_excel_import_mdm'),
   # Маршрут запуска импорта по именам.
   path('employee_excel_imports/<int:pk>/start_employee_excel_import_name/', start_employee_excel_import_name_view, name='start_employee_excel_import_name'),
   # Маршрут вывода списка категорий.
   path('categories/', CategoriesView.as_view(), name='categories'),
   # Маршрут вывода категории.
   path('categories/<int:pk>/', CategoryView.as_view(), name='category'),
   # Маршрут создания категории.
   path('categories/create/', CategoryCreateView.as_view(), name='category_create'),
   # Маршрут обновления категории.
   path('categories/<int:pk>/update/', CategoryUpdateView.as_view(), name='category_update'),
   # Маршрут удаления категории.
   path('categories/<int:pk>/delete/', CategoryDeleteView.as_view(), name='category_delete'),
   # Маршрут вывода списка групп.
   path('groups/', GroupsView.as_view(), name='groups'),
   # Маршрут вывода группы.
   path('groups/<int:pk>/', GroupView.as_view(), name='group'),
   # Маршрут создания группы.
   path('groups/create/', GroupCreateView.as_view(), name='group_create'),
   # Маршрут обновления группы.
   path('groups/<int:pk>/update/', GroupUpdateView.as_view(), name='group_update'),
   # Маршрут удаления группы.
   path('groups/<int:pk>/delete/', GroupDeleteView.as_view(), name='group_delete'),
   # Маршрут создания генератора группы.
   path('groups/<int:pk>/groups_generator/create/', GroupsGeneratorCreateView.as_view(), name='groups_generator_create'),
   # Маршрут обновления генератора группы.
   path('groups_generator/<int:pk>/update/', GroupsGeneratorUpdateView.as_view(), name='groups_generator_update'),
   # Маршрут копирования адресов группы.
   path('groups/<int:pk>/copy_emails/', copy_emails, name='group_copy_emails'),
   # Маршрут создания объектных прав.
   path('employees_group_object_permissions/<str:type>/<int:pk>/create', EmployeesGroupObjectPermissionCreateView.as_view(), name='employees_group_object_permissions_create'),
   # Маршрут удаления объектных прав.
   path('employees_group_object_permissions/<str:type>/<int:pk>/<int:employees_group_object_permission_pk>/delete/', EmployeesGroupObjectPermissionDeleteView.as_view(), name='employees_group_object_permissions_delete'),
   # Маршрут создания объектных прав.
   path('employees_object_permissions/<str:type>/<int:pk>/create', EmployeesObjectPermissionCreateView.as_view(), name='employees_object_permissions_create'),
   # Маршрут удаления объектных прав.
   path('employees_object_permissions/<str:type>/<int:pk>/<int:employees_object_permission_pk>/delete/', EmployeesObjectPermissionDeleteView.as_view(), name='employees_object_permissions_delete'),
   # Маршрут вывода контактов.
   path('contacts/', ContactsView.as_view(), name='contacts'),
   # Маршрут создания контактов.
   path('contacts/create/', ContactsCreateView.as_view(), name='contacts_create'),
   # Маршрут обновления контактов.
   path('contacts/update/', ContactsUpdateView.as_view(), name='contacts_update'),
   # Маршрут вывода политики конфиденциальности.
   path('privacy_policy/', PrivacyPolicyView.as_view(), name='privacy_policy'),
   # Маршрут создания политики конфиденциальности.
   path('privacy_policy/create/', PrivacyPolicyCreateView.as_view(), name='privacy_policy_create'),
   # Маршрут обновления политики конфиденциальности.
   path('privacy_policy/update/', PrivacyPolicyUpdateView.as_view(), name='privacy_policy_update'),
   # Маршрут вывода политики обработки персональных данных.
   path('data_processing/', DataProcessingView.as_view(), name='data_processing'),
   # Маршрут создания политики обработки персональных данных.
   path('data_processing/create/', DataProcessingCreateView.as_view(), name='data_processing_create'),
   # Маршрут обновления политики обработки персональных данных.
   path('data_processing/update/', DataProcessingUpdateView.as_view(), name='data_processing_update'),
]