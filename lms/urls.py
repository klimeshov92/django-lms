"""
URL configuration for lms project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
# Импорт путей и их наследования.
from django.urls import path, include
# Импорт настроек и модели
# для упрощения обслуживания статических и медиа- файлов
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordChangeDoneView, LogoutView, \
    PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from core.views import HomeView, signup_view, activate, HomeCreateView, HomeUpdateView

urlpatterns = [
    path('admin/', admin.site.urls),
    # Для select2.
    path('select2/', include('django_select2.urls')),
    # Маршруты регистрации.
    path('signup/', signup_view, name='signup'),
    path('activate/<uidb64>/<token>/', activate, name='activate'),
    # Маршруты авторизации.
    path('login/', LoginView.as_view(), name='login'),
    path('', HomeView.as_view(), name='home'),
    path('home_create/', HomeCreateView.as_view(), name='home_create'),
    path('home_update/', HomeUpdateView.as_view(), name='home_update'),
    path('logout/', LogoutView.as_view(), name='logout'),
    # Маршруты изменения пароля
    path('password_change/', PasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', PasswordChangeDoneView.as_view(), name='password_change_done'),
    # Маршруты сброса пароля
    path('password_reset/', PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    # Для ядра.
    path('core/', include('core.urls')),
    # Для CKEditor.
    path('ckeditor/', include('ckeditor_uploader.urls')),
    # Для траекторий обучения.
    path('learning_paths/', include('learning_path.urls')),
    # Для материалов.
    path('materials/', include('materials.urls')),
    # Для тестов.
    path('tests/', include('testing.urls')),
    # Для курсов.
    path('courses/', include('courses.urls')),
    # Для мероприятий.
    path('events/', include('events.urls')),
    # Для рассылок.
    path('emails/', include('emails.urls')),
    # Для отзывов.
    path('reviews/', include('reviews.urls')),
    # Для лидеров.
    path('leaders/', include('leaders.urls')),
    # Путь статических фалов.
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
# Путь медиафалов.
# Доступен только при разработке (if settings.DEBUG).
# Потом надо сервером обрабатывать.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Для тулбарчика.
    #import debug_toolbar
    #urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]
