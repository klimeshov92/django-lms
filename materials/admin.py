from django.contrib import admin

# Register your models here.

# Импорт моделей.
from .models import Material, File

# Регистрация моделей в админке.
admin.site.register(Material)
admin.site.register(File)