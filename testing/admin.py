from django.contrib import admin

# Register your models here.

# Импорт моделей.
from .models import Test, Question, Answer, RelevantPoint

# Регистрация моделей в админке.
admin.site.register(Test)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(RelevantPoint)