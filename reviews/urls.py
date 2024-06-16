# Импорт пути.
from django.urls import path
# Импорт представления.
from .views import ReviewsView, ObjectsReviewsView, ObjectsReviewCreateView, ObjectsReviewUpdateView, ObjectsReviewDeleteView
# Имя приложения в адресах.
app_name = 'reviews'

# Список маршрутов приложения.
urlpatterns = [
   # Маршрут вывода отзывов.
   path('', ReviewsView.as_view(), name='reviews'),
   path('<str:type>/<int:pk>/', ObjectsReviewsView.as_view(), name='objects_reviews'),
   # Маршрут создания отзыва.
   path('<str:type>/<int:pk>/create', ObjectsReviewCreateView.as_view(), name='review_create'),
   # Маршрут изменения отзыва.
   path('<int:pk>/update/', ObjectsReviewUpdateView.as_view(), name='review_update'),
   # Маршрут удаления отзыва.
   path('<int:pk>/delete/', ObjectsReviewDeleteView.as_view(), name='review_delete'),
]