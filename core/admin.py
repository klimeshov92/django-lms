from django.contrib import admin

# Register your models here.

# Импорт моделей.
from .models import Employee, EmployeesGroup, GroupsGenerator, EmployeesGroupObjectPermission, EmployeesObjectPermission, \
    Organization, Subdivision, Position, Placement, \
    EmployeeExcelImport, Category, PrivacyPolicy, DataProcessing, Home
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from guardian.models import GroupObjectPermission

# Регистрация моделей в админке.
admin.site.register(Employee)
admin.site.register(Organization)
admin.site.register(Subdivision)
admin.site.register(Position)
admin.site.register(Placement)
admin.site.register(EmployeeExcelImport)
admin.site.register(Category)
admin.site.unregister(Group)
admin.site.register(EmployeesGroup)
admin.site.register(GroupsGenerator)
admin.site.register(EmployeesGroupObjectPermission)
admin.site.register(EmployeesObjectPermission)
admin.site.register(PrivacyPolicy)
admin.site.register(DataProcessing)
admin.site.register(Home)

# Класс отображения модели в админке.
class PermissionAdmin(admin.ModelAdmin):
    list_display = ['codename', 'name', 'content_type']
    list_filter = ['content_type']
    search_fields = ['codename', 'name', 'content_type__app_label']

# Регистрация с классом отображения.
admin.site.register(Permission, PermissionAdmin)