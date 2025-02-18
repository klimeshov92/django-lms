# Импорт пути.
from django.urls import path

# Импорт представления.
from .views import *

# Имя приложения в адресах.
app_name = 'works'

# Список маршрутов приложения.
urlpatterns = [
   # Маршрут вывода материалов.
   path('', WorksView.as_view(), name='works'),
   # Маршрут вывода материала.
   path('<int:pk>/', WorkView.as_view(), name='work'),
   # Маршрут чтения материала.
   path('<int:pk>/read/', WorkReadView.as_view(), name='work_read'),
   # Маршрут создания материала.
   path('create/', WorkCreateView.as_view(), name='work_create'),
   # Маршрут обновления материала.
   path('<int:pk>/update/', WorkUpdateView.as_view(), name='work_update'),
   # Маршрут удаления материала.
   path('<int:pk>/delete/', WorkDeleteView.as_view(), name='work_delete'),
   # Маршрут вывода списка для контроля.
   path('results/supervising/', WorksSupervising.as_view(), name='results_supervising'),
   path('results/<int:pk>/read/', WorkResultReadView.as_view(), name='work_result_read'),
   # Маршруты написания отчета и оценки.
   path('results/<int:pk>/executor_report_update/', ExecutorReportUpdateView.as_view(), name='executor_report_update'),
   path('results/<int:pk>/work_review_create/', WorkReviewCreateView.as_view(), name='work_review_create'),
   path('work_review_update/<int:pk>', WorkReviewUpdateView.as_view(), name='work_review_update'),
]