# Импорт пути.
from django.urls import path
# Импорт представления.
from .views import (
   LearningComplexsView, LearningComplexView, LearningComplexCreateView, LearningComplexUpdateView, LearningComplexDeleteView,
   LearningComplexPathsView, LearningComplexPathCreateView, LearningComplexPathUpdateView, LearningComplexPathDeleteView,
   LearningPathsView, LearningPathView, LearningPathCreateView, LearningPathUpdateView, LearningPathDeleteView,
   LearningPathTasksView, LearningTaskCreateView, LearningTaskUpdateView, LearningTaskDeleteView,
   AssignmentsView, AssignmentView, AssignmentCreateView,  AssignmentUpdateView, AssignmentDeleteView,
   self_appointment, ResultsView, learning_tasks_ordering, learning_paths_ordering,
   AssignmentRepeatCreateView, AssignmentRepeatUpdateView, AssignmentRepeatDeleteView
)


# Имя приложения в адресах.
app_name = 'learning_path'

# Список маршрутов приложения.
urlpatterns = [
   # Маршрут вывода списка.
   path('learning_complexs/', LearningComplexsView.as_view(), name='learning_complexs'),
   # Маршрут вывода.
   path('learning_complexs/<int:pk>/', LearningComplexView.as_view(), name='learning_complex'),
   # Маршрут создания.
   path('learning_complexs/create/', LearningComplexCreateView.as_view(), name='learning_complex_create'),
   # Маршрут обновления.
   path('learning_complexs/<int:pk>/update/', LearningComplexUpdateView.as_view(), name='learning_complex_update'),
   # Маршрут удаления.
   path('learning_complexs/<int:pk>/delete/', LearningComplexDeleteView.as_view(), name='learning_complex_delete'),
   # Маршрут вывода списка.
   path('learning_complexs/<int:pk>/learning_complex_paths/', LearningComplexPathsView.as_view(), name='learning_complex_paths'),
   # Маршрут создания.
   path('learning_complexs/<int:pk>/learning_complex_path/create', LearningComplexPathCreateView.as_view(), name='learning_complex_path_create'),
   # Маршрут сортировки.
   path('learning_complex_path/<int:pk>/learning_paths_ordering/', learning_paths_ordering, name='learning_paths_ordering'),
   # Маршрут обновления.
   path('learning_complex_path/<int:pk>/update/', LearningComplexPathUpdateView.as_view(), name='learning_complex_path_update'),
   # Маршрут удаления.
   path('learning_complex_path/<int:pk>/delete/', LearningComplexPathDeleteView.as_view(), name='learning_complex_path_delete'),
   # Маршрут вывода списка.
   path('', LearningPathsView.as_view(), name='learning_paths'),
   # Маршрут вывода.
   path('<int:pk>/', LearningPathView.as_view(), name='learning_path'),
   # Маршрут создания.
   path('create/', LearningPathCreateView.as_view(), name='learning_path_create'),
   # Маршрут обновления.
   path('<int:pk>/update/', LearningPathUpdateView.as_view(), name='learning_path_update'),
   # Маршрут удаления.
   path('<int:pk>/delete/', LearningPathDeleteView.as_view(), name='learning_path_delete'),
   # Маршрут вывода списка.
   path('<int:pk>/learning_tasks/', LearningPathTasksView.as_view(), name='learning_path_tasks'),
   # Маршрут создания.
   path('<int:pk>/learning_task/create/', LearningTaskCreateView.as_view(), name='learning_task_create'),
   # Маршрут сортировки.
   path('<int:pk>/learning_tasks/learning_tasks_ordering/', learning_tasks_ordering, name='learning_tasks_ordering'),
   # Маршрут обновления.
   path('learning_task/<int:pk>/update/', LearningTaskUpdateView.as_view(), name='learning_task_update'),
   # Маршрут удаления.
   path('learning_task/<int:pk>/delete/', LearningTaskDeleteView.as_view(), name='learning_task_delete'),
   # Маршрут вывода списка.
   path('assignments/', AssignmentsView.as_view(), name='assignments'),
   # Маршрут вывода.
   path('assignments/<int:pk>/', AssignmentView.as_view(), name='assignment'),
   # Маршрут создания.
   path('assignments/create/', AssignmentCreateView.as_view(), name='assignment_create'),
   # Маршрут обновления.
   path('assignments/<int:pk>/update/', AssignmentUpdateView.as_view(), name='assignment_update'),
   # Маршрут удаления.
   path('assignments/<int:pk>/delete/', AssignmentDeleteView.as_view(), name='assignment_delete'),
   # Маршрут создания.
   path('assignments/<int:pk>/repeat_create/', AssignmentRepeatCreateView.as_view(), name='assignment_repeat_create'),
   # Маршрут обновления.
   path('assignment_repeat/<int:pk>/update/', AssignmentRepeatUpdateView.as_view(), name='assignment_repeat_update'),
   # Маршрут удаления.
   path('assignment_repeat/<int:pk>/delete/', AssignmentRepeatDeleteView.as_view(), name='assignment_repeat_delete'),
   # Маршрут самоназначения.
   path('<str:type>/<int:pk>/self_appointment/', self_appointment, name='self_appointment'),
   # Маршрут вывода списка.
   path('results/', ResultsView.as_view(), name='results'),

]