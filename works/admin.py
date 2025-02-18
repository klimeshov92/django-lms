from django.contrib import admin

# Register your models here.

# Импорт моделей.
from .models import Work

# Регистрация моделей в админке.
admin.site.register(Work)