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
    # Маршрут вывода пакетов.
    path('scorm_packages', views.ScormPackagesView.as_view(), name='scorm_packages'),
    # Маршрут вывода пакета.
    path('scorm_packages/<int:pk>/', views.ScormPackageView.as_view(), name='scorm_package'),
    # Маршрут создания пакета.
    path('scorm_packages/create/', views.ScormPackageCreateView.as_view(), name='scorm_package_create'),
    # Маршрут обновления пакета.
    path('scorm_packages/<int:pk>/update/', views.ScormPackageUpdateView.as_view(), name='scorm_package_update'),
    # Маршрут удаления пакета.
    path('scorm_packages/<int:pk>/delete/', views.ScormPackageDeleteView.as_view(), name='scorm_package_delete'),
    # SCORM плеер и API.
    path('scorm_display/<int:scorm_package_id>/', views.scorm_display, name='scorm_display'),
    path('api/scorm_initialize/', views.scorm_initialize, name='scorm_initialize'),
    path('api/scorm_finish/', views.scorm_finish, name='scorm_finish'),
    path('api/get_value/', views.scorm_get_value, name='scorm_get_value'),
    path('api/set_value/', views.scorm_set_value, name='scorm_set_value'),
    path('api/scorm_commit/', views.scorm_commit, name='scorm_commit'),
    path('api/get_last_error/', views.scorm_get_last_error, name='scorm_get_last_error'),
    path('api/get_error_string/', views.scorm_get_error_string, name='scorm_get_error_string'),
    path('api/get_diagnostic/', views.scorm_get_diagnostic, name='scorm_get_diagnostic'),
]
