from django.contrib import admin

# Register your models here.

# Импорт моделей.
from .models import Course, ScormPackage

# Регистрация моделей в админке.
admin.site.register(Course)
admin.site.register(ScormPackage)