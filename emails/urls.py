# Импорт пути.
from django.urls import path

# Импорт представления.
from .views import EmailsView, EmailView, EmailCreateView, EmailUpdateView, EmailDeleteView, sending

# Имя приложения в адресах.
app_name = 'emails'

# Список маршрутов приложения.
urlpatterns = [
   # Маршрут вывода рассылок.
   path('', EmailsView.as_view(), name='emails'),
   # Маршрут вывода рассылки.
   path('<int:pk>/', EmailView.as_view(), name='email'),
   # Маршрут создания рассылки.
   path('create/', EmailCreateView.as_view(), name='email_create'),
   # Маршрут обновления рассылки.
   path('<int:pk>/update/', EmailUpdateView.as_view(), name='email_update'),
   # Маршрут удаления рассылки.
   path('<int:pk>/delete/', EmailDeleteView.as_view(), name='email_delete'),
   # Отправки письма.
   path('<int:pk>/sending/', sending, name='sending'),
]