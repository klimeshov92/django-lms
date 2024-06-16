from django.contrib import admin

# Register your models here.

# Импорт моделей.
from .models import Email, EmailsResult

# Регистрация моделей в админке.
admin.site.register(Email)
admin.site.register(EmailsResult)
