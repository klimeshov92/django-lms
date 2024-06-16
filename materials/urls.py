# Импорт пути.
from django.urls import path

# Импорт представления.
from .views import MaterialsView, MaterialView, MaterialReadView, MaterialCreateView, MaterialUpdateView, MaterialDeleteView, \
   FilesView, FileView, FileCreateView, FileUpdateView, FileDeleteView, confirm_reading

# Имя приложения в адресах.
app_name = 'materials'

# Список маршрутов приложения.
urlpatterns = [
   # Маршрут вывода материалов.
   path('', MaterialsView.as_view(), name='materials'),
   # Маршрут вывода материала.
   path('<int:pk>/', MaterialView.as_view(), name='material'),
   # Маршрут чтения материала.
   path('<int:pk>/read', MaterialReadView.as_view(), name='material_read'),
   # Маршрут подтверждения прочтения.
   path('<int:pk>/confirm_reading', confirm_reading, name='confirm_reading'),
   # Маршрут создания материала.
   path('create/', MaterialCreateView.as_view(), name='material_create'),
   # Маршрут обновления материала.
   path('<int:pk>/update/', MaterialUpdateView.as_view(), name='material_update'),
   # Маршрут удаления материала.
   path('<int:pk>/delete/', MaterialDeleteView.as_view(), name='material_delete'),
   # Маршрут вывода файлов.
   path('files/', FilesView.as_view(), name='files'),
   # Маршрут вывода файла.
   path('files/<int:pk>/', FileView.as_view(), name='file'),
   # Маршрут создания файла.
   path('files/create/', FileCreateView.as_view(), name='file_create'),
   # Маршрут обновления файла.
   path('files/<int:pk>/update/', FileUpdateView.as_view(), name='file_update'),
   # Маршрут удаления файла.
   path('files/<int:pk>/delete/', FileDeleteView.as_view(), name='file_delete'),
]