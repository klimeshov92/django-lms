

from django.http import HttpResponse
from django.db.models.deletion import ProtectedError
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import get_user_model
from guardian.utils import get_anonymous_user

# Отработка защиты от удаления.
class ProtectedErrorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        if isinstance(exception, ProtectedError):
            # Получаем защищенные объекты.
            protected_objects = list(exception.protected_objects)
            # Составляем строку с именами защищенных объектов.
            protected_names = ', '.join([str(obj) for obj in protected_objects])
            # Формируем сообщение об ошибке.
            back_button = f"<a href='javascript:window.history.go(-2)'>Назад</a>"
            error_message = f"Не удалось удалить из-за связанных объектов: {protected_names} {back_button}"
            return HttpResponse(error_message)

        # Если это не исключение ProtectedError, передаем его дальше
        return None

class CustomAnonymousUserMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_anonymous:
            request.user = get_anonymous_user()