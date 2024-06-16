from django.contrib import admin

# Register your models here.

# Импорт моделей.
from .models import Transaction

# Регистрация моделей в админке.
admin.site.register(Transaction)