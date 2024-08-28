from django.urls import path

# Импорт всех представлений.
from . import views

# Имя приложения в адресах.
app_name = 'courses'

# Список маршрутов приложения.
urlpatterns = [
    # Маршрут вывода курсов.
    path('', views.CoursesView.as_view(), name='courses'),
    # Маршрут вывода курса.
    path('<int:pk>/', views.CourseView.as_view(), name='course'),
    # Маршрут создания курса.
    path('create/', views.CourseCreateView.as_view(), name='course_create'),
    # Маршрут обновления курса.
    path('<int:pk>/update/', views.CourseUpdateView.as_view(), name='course_update'),
    # Маршрут удаления курса.
    path('<int:pk>/delete/', views.CourseDeleteView.as_view(), name='course_delete'),
    # SCORM плеер и API.
    path('scorm_display/<int:course_id>/', views.scorm_display, name='scorm_display'),
    path('api/scorm_initialize/', views.scorm_initialize, name='scorm_initialize'),
    path('api/scorm_finish/', views.scorm_finish, name='scorm_finish'),
    path('api/get_value/', views.scorm_get_value, name='scorm_get_value'),
    path('api/set_value/', views.scorm_set_value, name='scorm_set_value'),
    path('api/scorm_commit/', views.scorm_commit, name='scorm_commit'),
    path('api/get_last_error/', views.scorm_get_last_error, name='scorm_get_last_error'),
    path('api/get_error_string/', views.scorm_get_error_string, name='scorm_get_error_string'),
    path('api/get_diagnostic/', views.scorm_get_diagnostic, name='scorm_get_diagnostic'),
]
