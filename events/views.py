from django.shortcuts import render

# Create your views here.

# Импорт настроек.
from django.conf import settings
# Импорт моделей вью.
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
# Импорт моделей ядра.
from .models import Event, ParticipantsGenerator
from learning_path.models import Result
# Импорт модели фильтров.
from .filters import EventFilter, ParticipantsFilter
# Импорт форм.
from .forms import EventForm, ParticipantsGeneratorForm
# Импорт рендера, перенаправления, генерации адреса и других урл функций.
from django.shortcuts import redirect, reverse, get_object_or_404
# Проверка прав доступа для классов.
from guardian.mixins import PermissionListMixin
from guardian.mixins import PermissionRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin as GPermissionRequiredMixin
# Импорт декораторов проверки прав.
from guardian.decorators import permission_required
# Сабквери.
from django.db.models import OuterRef, Subquery
from django.db.models.functions import Coalesce
from django.db.models import Case, When, Value
# Импорт Q.
from django.db.models import Q
# Импорт выброса ошибок и джисон ответа.
from django.http import HttpResponseNotFound, HttpResponseForbidden, JsonResponse
# Импорт времени с учетом таймзоны.
from django.utils import timezone
# Импорт пагинатора
from django.core.paginator import Paginator
# Импорт суммирования значений.
from django.db.models import Sum
# Миксины.
from core.mixins import PreviousPageGetMixinL0, PreviousPageSetMixinL0, PreviousPageGetMixinL1, PreviousPageSetMixinL1, PreviousPageGetMixinL2, PreviousPageSetMixinL2
from reviews.models import Review
from core.models import EmployeesGroupObjectPermission, EmployeesObjectPermission
from reviews.filters import ObjectsReviewFilter
from django.core.paginator import Paginator
from django.contrib.contenttypes.models import ContentType
from core.filters import EmployeesGroupObjectPermissionFilter, EmployeesObjectPermissionFilter

# Импортируем логи
import logging
# Создаем логгер с именем 'project'
logger = logging.getLogger('project')

# Список вопросов.
class EventsView(PreviousPageSetMixinL1, PermissionListMixin, ListView):
    # Права доступа
    permission_required = 'events.view_event'
    # Модель.
    model = Event
    # Поле сортировки.
    ordering = '-date', '-start_time'
    # Шаблон.
    template_name = 'events.html'
    # Количество объектов на странице
    paginate_by = 6

    # Переопределяем выборку вью.
    def get_queryset(self):
        # Забираем изначальную выборку вью.
        queryset = super().get_queryset().prefetch_related(
            'categories',
        )
        # Аннотируем queryset данными из последнего Result
        latest_result = Result.objects.filter(
            event_id=OuterRef('pk'), employee=self.request.user
        ).order_by('-id').values('status')[:1]
        queryset = queryset.annotate(
            latest_result_status=Coalesce(Subquery(latest_result.values('status')), Value('None'))
        ).order_by('-date', '-start_time')
        # Добавляем модель фильтрации в выборку вью.
        self.filterset = EventFilter(self.request.GET, queryset, request=self.request)
        # Возвращаем вью новую выборку.
        return self.filterset.qs

    # Добавляем во вью переменные.
    def get_context_data(self, **kwargs):
        # Забираем изначальный набор переменных.
        context = super().get_context_data(**kwargs)
        # Добавляем фильтрсет.
        context['filterset'] = self.filterset
        # Возвращаем новый набор переменных.
        return context

# Вывод мероприятия.
class EventView(PreviousPageGetMixinL1, PreviousPageSetMixinL0, PermissionRequiredMixin, ListView):
    # Права доступа
    permission_required = 'events.view_event'
    accept_global_perms = True
    # Модель.
    model = Result
    # Шаблон.
    template_name = 'event.html'
    # Количество объектов на странице
    paginate_by = 6

    # Определяем объект проверки.
    def get_permission_object(self):
        event = Event.objects.get(pk=self.kwargs.get('pk'))
        return event

    # Переопределяем выборку вью.
    def get_queryset(self):
        # Переопределяем изначальную выборку.
        event = self.get_permission_object()
        queryset = super().get_queryset().filter(event=event).order_by('employee')
        self.qs_count = queryset.count
        # Добавляем модель фильтрации в выборку вью.
        self.filterset = ParticipantsFilter(self.request.GET, queryset, request=self.request, event=event)
        # Возвращаем вью новую выборку.
        return self.filterset.qs

    # Переопределеяем переменные вью.
    def get_context_data(self, **kwargs):
        # забираем изначальный набор переменных
        context = super().get_context_data(**kwargs)

        # Добавляем фильтрсет.
        context['filterset'] = self.filterset
        context['qs_count'] = self.qs_count
        # Добавляем во вью.
        event = self.get_permission_object()
        context['object'] = event

        # Забираем результат объекта.
        if event.results.filter(employee=self.request.user):
            result = event.results.filter(employee=self.request.user).latest('id')
            # Добавляем в контекст.
            context['result'] = result

        # Добавляем базовый адрес.
        context['BASE_URL'] = settings.BASE_URL

        # Пересечения
        intersecting_events=Event.objects.filter(
            # Те, что начнутся во время, а закончатся позже.
            Q(start_time__lte=event.end_time) & Q(end_time__gte=event.end_time) & Q(date=event.date) |
            # Те, что начнутся раньше, а закончатся во время.
            Q(start_time__lte=event.start_time) & Q(end_time__gte=event.start_time) & Q(date=event.date) |
            # Те, что начнутся и закончатся во время.
            Q(start_time__gte=event.start_time) & Q(end_time__lte=event.end_time) & Q(date=event.date)
        ).exclude(id=event.id).order_by('-date', '-start_time')
        # Забираем участников текущего мероприятия.
        current_event_participants = event.participants_group.user_set.all()
        # Создаем словарь для пересекающихся участников.
        intersecting_events_dict = {}
        # Проходимся по каждому мероприятию в списке intersecting_events.
        for event in intersecting_events:
            # Получаем список участников забираемого мероприятия.
            event_participants = event.participants_group.user_set.all()
            # Получаем пересекающихся участников.
            common_participants = event_participants.intersection(current_event_participants)
            # Сохраняем общих участников в словаре.
            intersecting_events_dict[event] = common_participants
        # Меняем формат на список кортежей.
        intersecting_events_items = list(intersecting_events_dict.items())
        context['intersecting_events_count'] = len(intersecting_events_items)
        # Если участники есть.
        if intersecting_events_items:
            # Добавляем пагинатор
            intersecting_events_paginator = Paginator(intersecting_events_items, 6)
            intersecting_events_page_number = self.request.GET.get('intersecting_events_page')
            intersecting_events_page_obj = intersecting_events_paginator.get_page(intersecting_events_page_number)
        # Если нет...
        else:
            # Задаем пустую переменную для проверки в шаблоне.
            intersecting_events_page_obj = None
        # Добавляем во вью.
        context['intersecting_events_page_obj'] = intersecting_events_page_obj

        # Добавляем средний балл.
        # Сначала получаем сумму оценок и количество отзывов.
        reviews_sum = event.reviews.aggregate(Sum('score'))['score__sum']
        reviews_count = event.reviews.count()
        # Вычисляем среднюю оценку.
        if reviews_count > 0:
            reviews_average_mark = round((reviews_sum / reviews_count), 1)
        else:
            reviews_average_mark = 0
        # Добавляем вью.
        context['reviews_average_mark'] = reviews_average_mark

        # Добавляем отзывы.
        if Review.objects.filter(type='event', event__pk=self.kwargs.get('pk')).exists():
            reviews_queryset = Review.objects.filter(type='event', event__pk=self.kwargs.get('pk')).order_by('created')
        else:
            reviews_queryset = Review.objects.none()
        context['reviews_qs_count'] = len(reviews_queryset)
        reviews_filter = ObjectsReviewFilter(self.request.GET, queryset=reviews_queryset, request=self.request)
        reviews = reviews_filter.qs
        # Добавляем пагинатор.
        reviews_paginator = Paginator(reviews, 6)
        reviews_page_number = self.request.GET.get('reviews_page')
        reviews_page_obj = reviews_paginator.get_page(reviews_page_number)
        # Добавляем во вью.
        context['reviews_filter'] = reviews_filter
        context['reviews_page_obj'] = reviews_page_obj

        # Забираем отзыв.
        haves_review = False
        if event.reviews.filter(creator=self.request.user).exists():
            haves_review = True
        if settings.DEBUG:
            logger.info(f"Уже есть отзыв: {haves_review}")
        context['haves_review'] = haves_review

        # Добавляем объектные права.
        content_type = ContentType.objects.get_for_model(Event)
        if EmployeesGroupObjectPermission.objects.filter(
            content_type=content_type,
            object_pk=self.kwargs.get('pk')
        ).prefetch_related('content_object').exists():
            group_object_permissions_queryset = EmployeesGroupObjectPermission.objects.filter(
                content_type=content_type,
                object_pk=self.kwargs.get('pk')
            ).prefetch_related('content_object').order_by('group')

        else:
            group_object_permissions_queryset = EmployeesGroupObjectPermission.objects.none()
        context['group_object_permissions_qs_count'] = len(group_object_permissions_queryset)
        group_object_permissions_filter = EmployeesGroupObjectPermissionFilter(self.request.GET, queryset=group_object_permissions_queryset, request=self.request)
        group_object_permissions = group_object_permissions_filter.qs
        # Добавляем пагинатор.
        group_object_permissions_paginator = Paginator(group_object_permissions, 6)
        group_object_permissions_page_number = self.request.GET.get('group_object_permissions_page')
        group_object_permissions_page_obj = group_object_permissions_paginator.get_page(group_object_permissions_page_number)
        # Добавляем во вью.
        context['group_object_permissions_filter'] = group_object_permissions_filter
        context['group_object_permissions_page_obj'] = group_object_permissions_page_obj

        # Добавляем объектные права.
        if EmployeesObjectPermission.objects.filter(object_pk=self.kwargs.get('pk'), content_type=content_type).prefetch_related('content_object').exists():
            object_permissions_queryset = EmployeesObjectPermission.objects.filter(
                object_pk=self.kwargs.get('pk'),
                content_type=content_type
            ).prefetch_related('content_object').order_by('-id')
        else:
            object_permissions_queryset = EmployeesObjectPermission.objects.none()
        context['object_permissions_qs_count'] = len(object_permissions_queryset)
        object_permissions_filter = EmployeesObjectPermissionFilter(self.request.GET, queryset=object_permissions_queryset, request=self.request)
        object_permissions = object_permissions_filter.qs
        # Добавляем пагинатор.
        object_permissions_paginator = Paginator(object_permissions, 6)
        object_permissions_page_number = self.request.GET.get('object_permissions_page')
        object_permissions_page_obj = object_permissions_paginator.get_page(object_permissions_page_number)
        # Добавляем во вью.
        context['object_permissions_filter'] = object_permissions_filter
        context['object_permissions_page_obj'] = object_permissions_page_obj

        # Возвращаем новый набор переменных в контролер.
        return context

# Создание мероприятия.
class EventCreateView(GPermissionRequiredMixin, CreateView):
    # Права доступа.
    permission_required = 'events.add_event'
    # Форма.
    form_class = EventForm
    # Модель.
    model = Event
    # Шаблон.
    template_name = 'event_edit.html'

    def get_permission_object(self):
        # Возвращаем None, так как при создании объект еще не существует
        return None

    # Заполнение полей данными.
    def get_initial(self):
        # Забираем изначальный набор.
        initial = super().get_initial()
        # Добавляем создателя: юзера отправившего запрос.
        initial["creator"] = self.request.user
        # Возвращаем значения в форму.
        return initial

    # Валидация формы.
    def form_valid(self, form):

        # Сохраняем объект без коммита.
        self.object = form.save(commit=False)

        # Сохраняем объект в базу данных.
        self.object.save()

        # Сохраняем связи.
        form.save_m2m()

        # Вызываем базовую реализацию для дальнейшей обработки.
        return super(EventCreateView, self).form_valid(form)

    # Перенаправление после валидации формы.
    def get_success_url(self):
        # Направляем по адресу объекта.
        return reverse('events:event', kwargs={'pk': self.object.pk})

# Изменение мероприятия.
class EventUpdateView(PermissionRequiredMixin, UpdateView):
    # Права доступа
    permission_required = 'events.change_event'
    accept_global_perms = True
    # Форма.
    form_class = EventForm
    # Модель.
    model = Event
    # Шаблон.
    template_name = 'event_edit.html'

    # Заполнение полей данными.
    def get_initial(self):
        # Забираем изначальный набор.
        initial = super().get_initial()
        # Добавляем создателя: юзера отправившего запрос.
        initial["creator"] = self.request.user
        # Добавляем время начала и время конца.
        initial["date"] = self.object.date.strftime('%Y-%m-%d')
        initial["start_time"] = self.object.start_time
        initial["end_time"] = self.object.end_time
        # Возвращаем значения в форму.
        return initial

    # Валидация формы.
    def form_valid(self, form):

        # Сохраняем объект без коммита.
        self.object = form.save(commit=False)

        # Сохраняем объект в базу данных.
        self.object.save()

        # Сохраняем связи.
        form.save_m2m()

        # Вызываем базовую реализацию для дальнейшей обработки.
        return super(EventUpdateView, self).form_valid(form)

    # Перенаправление после валидации формы.
    def get_success_url(self):
        # Направляем по адресу объекта.
        return reverse('events:event', kwargs={'pk': self.object.pk})

# Удаление мероприятия.
class EventDeleteView(PermissionRequiredMixin, DeleteView):
    # Права доступа
    permission_required = 'events.delete_event'
    accept_global_perms = True
    # Модель.
    model = Event
    # Шаблон.
    template_name = 'event_delete.html'

    # Перенаправление после валидации формы.
    def get_success_url(self):
        # Направляем по адресу объектов.
        return reverse('events:events')


# Создание категории.
class ParticipantsGeneratorCreateView(GPermissionRequiredMixin, CreateView):
    # Права доступа.
    permission_required = 'events.add_event'
    # Форма.
    form_class = ParticipantsGeneratorForm
    # Модель.
    model = ParticipantsGenerator
    # Шаблон.
    template_name = 'participants_generator_edit.html'

    # Определяем объект проверки.
    def get_permission_object(self):
        event = Event.objects.get(pk=self.kwargs.get('pk'))
        return event

    # Заполнение полей данными.
    def get_initial(self):
        # Забираем изначальный набор.
        initial = super().get_initial()
        # Добавляем создателя: юзера отправившего запрос.
        initial["creator"] = self.request.user
        # Добавляем группу из которой создан генератор.
        event = self.get_permission_object()
        initial["event"] = event
        # Возвращаем значения в форму.
        return initial

    # Валидация формы.
    def form_valid(self, form):
        # Сохраняем объект без коммита.
        self.object = form.save(commit=False)
        # Сохраняем объект в базу данных.
        self.object.save()

        # Логируем информацию об объекте после сохранения.
        logger.info(f"Объект после сохранения: {self.object}")
        logger.info(f"Поля объекта после сохранения: {vars(self.object)}")

        # Сохраняем связи.
        form.save_m2m()

        # Логируем информацию о связанных объектах.
        for related_object in form.cleaned_data:
            logger.info(f"Связанный объект: {related_object}")
            logger.info(f"Значение: {form.cleaned_data[related_object]}")

        # Вызываем базовую реализацию для дальнейшей обработки.
        return super(ParticipantsGeneratorCreateView, self).form_valid(form)

    # Перенаправление после валидации формы.
    def get_success_url(self):
        # Направляем по адресу объекта.
        return reverse('events:event', kwargs={'pk': self.object.event.pk})

# Изменение категории.
class ParticipantsGeneratorUpdateView(PermissionRequiredMixin, UpdateView):
    # Права доступа.
    permission_required = 'events.change_event'
    accept_global_perms = True
    # Форма.
    form_class = ParticipantsGeneratorForm
    # Модель.
    model = ParticipantsGenerator
    # Шаблон.
    template_name = 'participants_generator_edit.html'

    # Определяем объект проверки.
    def get_permission_object(self):
        event = self.get_object().event
        return event

    # Заполнение полей данными.
    def get_initial(self):
        # Забираем изначальный набор.
        initial = super().get_initial()
        # Добавляем создателя: юзера отправившего запрос.
        initial["creator"] = self.request.user
        # Возвращаем значения в форму.
        return initial

    # Валидация формы.
    def form_valid(self, form):
        # Сохраняем объект без коммита.
        self.object = form.save(commit=False)
        # Сохраняем объект в базу данных.
        self.object.save()

        # Логируем информацию об объекте после сохранения.
        logger.info(f"Объект после сохранения: {self.object}")
        logger.info(f"Поля объекта после сохранения: {vars(self.object)}")

        # Сохраняем связи.
        form.save_m2m()

        # Логируем информацию о связанных объектах.
        for related_object in form.cleaned_data:
            logger.info(f"Связанный объект: {related_object}")
            logger.info(f"Значение: {form.cleaned_data[related_object]}")

        # Вызываем базовую реализацию для дальнейшей обработки.
        return super(ParticipantsGeneratorUpdateView, self).form_valid(form)

    # Перенаправление после валидации формы.
    def get_success_url(self):
        # Направляем по адресу объекта.
        return reverse('events:event', kwargs={'pk': self.object.event.pk})

# Отметка отказа.
def participants_mark(request, pk, status):

    # Забираем резульат.
    result = Result.objects.get(pk=pk)
    logger.info(f"Результат участия в мероприятии: {result}")

    # Если страницу открыл не тот, кому назначено, запрещаем доступ.
    if result.employee != request.user:
        return HttpResponseForbidden('Этот не Ваш результат мероприятия!')

    # Отмечаем выполнение.
    if status == 'refused':
        result.status = 'refused'
        result.end_date = timezone.now()
        result.save()
    if status == 'registered':
        result.status = 'registered'
        result.end_date = None
        result.save()

    # Уходим.
    return redirect('events:event', pk=result.event.pk)

# Отметка пристуствия.
@permission_required('events.change_event', return_403=True)
def responsibles_mark(request, pk, status):

    # Забираем резульат.
    result = Result.objects.get(pk=pk)
    logger.info(f"Результат участия в мероприятии: {result}")

    # Отмечаем выполнение.
    if status == 'present':
        result.status = 'present'
        result.end_date = timezone.now()
        result.save()
    if status == 'absent':
        result.status = 'absent'
        result.end_date = timezone.now()
        result.save()

    # Уходим.
    return redirect('events:event', pk=result.event.pk)

# Отметка статуса.
@permission_required('events.change_event', return_403=True)
def change_status(request, pk, status):

    # Забираем резульат.
    event = Event.objects.get(pk=pk)
    logger.info(f"Мепроприятие: {event}")

    # Отмечаем выполнение.
    if status == 'in_progress':
        event.status = 'in_progress'
        event.save()
    if status == 'canceled':
        event.status = 'canceled'
        event.save()
    if status == 'planned':
        event.status = 'planned'
        event.save()
    if status == 'completed':
        event.status = 'completed'
        event.save()

        # Забираем результаты.
        results = Result.objects.filter(event=event)

        # Отмечаем участие.
        for result in results:
            if result.status == 'registered':
                result.status = 'present'
                result.end_date = timezone.now()
                result.save()

    # Уходим.
    return redirect('events:event', pk=pk)


