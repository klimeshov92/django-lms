from django.contrib import admin

# Register your models here.

# Импорт моделей.
from .models import LearningPath, LearningTask, Assignment, \
    Result, QuestionsResult, AnswersResult, LearningComplex, LearningComplexPath, AssignmentRepeat, ResultSupervising, WorkReview


# Регистрация моделей в админке.
admin.site.register(LearningComplex)
admin.site.register(LearningPath)
admin.site.register(LearningComplexPath)
admin.site.register(LearningTask)
admin.site.register(Assignment)
admin.site.register(Result)
admin.site.register(ResultSupervising)
admin.site.register(WorkReview)
admin.site.register(QuestionsResult)
admin.site.register(AnswersResult)
admin.site.register(AssignmentRepeat)