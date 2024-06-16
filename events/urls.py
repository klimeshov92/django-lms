# Импорт пути.
from django.urls import path
# Импорт представления.
from .views import EventsView, EventView, EventCreateView, EventUpdateView, EventDeleteView, \
   ParticipantsGeneratorCreateView, ParticipantsGeneratorUpdateView, \
   responsibles_mark, participants_mark, change_status

# Имя приложения в адресах.
app_name = 'events'

# Список маршрутов приложения.
urlpatterns = [
   # Маршрут вывода мероприятий.
   path('', EventsView.as_view(), name='events'),
   # Маршрут вывода мероприятия.
   path('<int:pk>/', EventView.as_view(), name='event'),
   # Маршрут создания мероприятия.
   path('create/', EventCreateView.as_view(), name='event_create'),
   # Маршрут обновления мероприятия.
   path('<int:pk>/update/', EventUpdateView.as_view(), name='event_update'),
   # Маршрут удаления мероприятия.
   path('<int:pk>/delete/', EventDeleteView.as_view(), name='event_delete'),
   # Маршрут создания генератора группы.
   path('<int:pk>/participants_generator/create/', ParticipantsGeneratorCreateView.as_view(), name='participants_generator_create'),
   # Маршрут обновления генератора группы.
   path('participants_generator/<int:pk>/update/', ParticipantsGeneratorUpdateView.as_view(), name='participants_generator_update'),
   # Маршрут отметки ответственного.
   path('<int:pk>/responsibles_mark/<str:status>/', responsibles_mark, name='responsibles_mark'),
   # Маршрут отметок участника.
   path('<int:pk>/participants_mark/<str:presence_mark>/', participants_mark, name='participants_mark'),
   # Маршрут смены статуса.
   path('<int:pk>/change_status/<str:status>/', change_status, name='change_status'),
]