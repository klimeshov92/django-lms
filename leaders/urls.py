# Импорт пути.
from django.urls import path
# Импорт представления.
from .views import (
   LeadersView
)


# Имя приложения в адресах.
app_name = 'leaders'

# Список маршрутов приложения.
urlpatterns = [
   # Маршрут вывода списка.
   path('leaders/', LeadersView.as_view(), name='leaders'),
]