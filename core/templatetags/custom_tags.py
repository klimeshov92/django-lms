# Импорт нужных модулей.
from django import template
from guardian.shortcuts import get_objects_for_user
register = template.Library()

# Декоратор для регистрации функции как шаблонного тега.
# "takes_context=True" позволяет тегу принимать текущий контекст шаблона.
@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):

    # Получение копии словаря параметров GET-запроса из текущего запроса.
    # Это делается для того, чтобы изменять параметры, не влияя на оригинальный запрос.
    d = context['request'].GET.copy()

    # Цикл перебирает все ключи и значения, переданные в шаблонный тег.
    # Он обновляет или добавляет параметры в копию словаря.
    for k, v in kwargs.items():
        d[k] = v  # Заменяет или добавляет параметр в словарь.

    # Возвращает URL-кодированную строку параметров, которая может быть использована в URL.
    return d.urlencode()

# Проверка прав.
@register.filter
def perms(user, permission_codename):

    # Проверяем глобальное разрешение для пользователя.
    global_permission = user.has_perm(permission_codename)

    # Проверяем существует ли для пользователя хотя бы один объект с этим разрешением.
    object_permission = get_objects_for_user(user, permission_codename).exists()

    # Возвращаем True, если есть хотя бы одно из разрешений (глобальное или объектное).
    return global_permission or object_permission

# Проверка статуса.
@register.filter(name='status_display')
def status_display(value):

    # Определяем значение.
    status_dict = {
        'appointed': 'Назначено',
        'in_progress': 'В процессe',
        'completed': 'Пройдено',
        'failed': 'Провалено'
    }

    # Возвращаем если оно есть.
    return status_dict.get(value, value)

# Проверка присутствия.
@register.filter(name='presence_mark_display')
def presence_mark_display(value):

    # Определяем значение.
    presence_mark_dict = {
        'registered': 'Зарегистрирован',
        'refused': 'Отказался',
        'present': 'Присутствовал',
        'absent': 'Отсутствовал',
    }

    # Возвращаем если оно есть.
    return presence_mark_dict.get(value, value)

