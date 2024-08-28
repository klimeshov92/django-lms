from django.contrib import admin

# Register your models here.

# Импорт моделей.
from .models import Course

# Регистрация моделей в админке.
admin.site.register(Course)