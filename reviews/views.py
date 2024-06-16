from django.shortcuts import render

# Create your views here.

# Импорт настроек.
from django.conf import settings
# Импорт моделей вью.
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
# Импорт моделей ядра.
from .models import Review
# Импорт форм.
from .forms import ObjectsReviewForm
# Проверка прав доступа для классов.
from guardian.mixins import PermissionListMixin
from guardian.mixins import PermissionRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin as GPermissionRequiredMixin
# Импорт декораторов проверки прав.
from django.contrib.auth.decorators import permission_required, login_required
# Импорт моделей
from learning_path.models import LearningPath
from materials.models import Material
from courses.models import Course
from testing.models import Test
from events.models import Event
# Импорт рендера, перенаправления, генерации адреса и других урл функций.
from django.shortcuts import render, redirect, reverse, get_object_or_404
# Импорт выброса ошибок.
from django.http import HttpResponseForbidden
# Импорт модели фильтров.
from .filters import ObjectsReviewFilter, ReviewFilter
# Миксины.
from core.mixins import PreviousPageGetMixinL0, PreviousPageSetMixinL0, PreviousPageGetMixinL1, PreviousPageSetMixinL1, PreviousPageGetMixinL2, PreviousPageSetMixinL2

# Импортируем логи
import logging
# Создаем логгер с именем 'project'
logger = logging.getLogger('project')

# Список отзывов.
class ReviewsView(PermissionListMixin, ListView):
    # Права доступа
    permission_required = 'reviews.view_all_review'
    # Модель.
    model = Review
    # Поле сортировки.
    ordering = 'created'
    # Шаблон.
    template_name = 'reviews.html'
    # Количество объектов на странице
    paginate_by = 6

    # Переопределяем выборку вью.
    def get_queryset(self):
        # Переопределяем изначальную выборку.
        queryset = super().get_queryset()
        # Добавляем модель фильтрации в выборку вью.
        self.filterset = ReviewFilter(self.request.GET, queryset, request=self.request)
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

# Список отзывов на объект.
class ObjectsReviewsView(PreviousPageGetMixinL0, PermissionListMixin, ListView):
    # Права доступа
    permission_required = 'reviews.view_review'
    # Модель.
    model = Review
    # Поле сортировки.
    ordering = 'created'
    # Шаблон.
    template_name = 'objects_reviews.html'
    # Количество объектов на странице
    paginate_by = 6

    # Переопределяем выборку вью.
    def get_queryset(self):
        # Переопределяем изначальную выборку.
        if self.kwargs.get('type') == 'learning_path':
            queryset = super().get_queryset().filter(type='learning_path', learning_path__pk=self.kwargs.get('pk'))
        elif self.kwargs.get('type') == 'material':
            queryset = super().get_queryset().filter(type='material', material__pk=self.kwargs.get('pk'))
        elif self.kwargs.get('type') == 'course':
            queryset = super().get_queryset().filter(type='course', course__pk=self.kwargs.get('pk'))
        elif self.kwargs.get('type') == 'test':
            queryset = super().get_queryset().filter(type='test', test__pk=self.kwargs.get('pk'))
        elif self.kwargs.get('type') == 'event':
            queryset = super().get_queryset().filter(type='event', event__pk=self.kwargs.get('pk'))
        # Добавляем модель фильтрации в выборку вью.
        self.filterset = ObjectsReviewFilter(self.request.GET, queryset, request=self.request)
        # Возвращаем вью новую выборку.
        return self.filterset.qs

    # Добавляем во вью переменные.
    def get_context_data(self, **kwargs):
        # Забираем изначальный набор переменных.
        context = super().get_context_data(**kwargs)
        # Добавляем объект и тип.
        if self.kwargs.get('type') == 'learning_path':
            object = LearningPath.objects.get(pk=self.kwargs.get('pk'))
            type = 'learning_path'
        elif self.kwargs.get('type') == 'material':
            object = Material.objects.get(pk=self.kwargs.get('pk'))
            type = 'material'
        elif self.kwargs.get('type') == 'course':
            object = Course.objects.get(pk=self.kwargs.get('pk'))
            type = 'course'
        elif self.kwargs.get('type') == 'test':
            object = Test.objects.get(pk=self.kwargs.get('pk'))
            type = 'test'
        elif self.kwargs.get('type') == 'event':
            object = Event.objects.get(pk=self.kwargs.get('pk'))
            type = 'event'
        context['object'] = object
        context['type'] = type
        # Забираем отзыв.
        haves_review = False
        print(object.reviews.filter(creator=self.request.user))
        if object.reviews.filter(creator=self.request.user).exists():
            haves_review = True
        if settings.DEBUG:
            logger.info(f"Уже есть отзыв: {haves_review}")
        context['haves_review'] = haves_review
        # Добавляем фильтрсет.
        context['filterset'] = self.filterset
        # Возвращаем новый набор переменных.
        return context

# Создание отзыва на объект.
class ObjectsReviewCreateView(GPermissionRequiredMixin, CreateView):
    # Права доступа
    permission_required = 'reviews.add_review'
    # Форма.
    form_class = ObjectsReviewForm
    # Модель.
    model = Review
    # Шаблон.
    template_name = 'review_edit.html'

    # Добавляем проверку.
    def dispatch(self, request, *args, **kwargs):

        # Забираем переменные.
        object_type = self.kwargs.get('type')
        object_pk = self.kwargs.get('pk')

        # Забираем объект.
        if object_type == 'learning_path':
            object = get_object_or_404(LearningPath, pk=object_pk)
        elif object_type == 'material':
            object = get_object_or_404(Material, pk=object_pk)
        elif object_type == 'course':
            object = get_object_or_404(Course, pk=object_pk)
        elif object_type == 'test':
            object = get_object_or_404(Test, pk=object_pk)
        elif object_type == 'event':
            object = get_object_or_404(Event, pk=object_pk)

        if not object.results.filter(employee=self.request.user).exists():
            return HttpResponseForbidden('Вы не можете оставить отзыв на контент, который не просматривали!')
        elif object.reviews.filter(creator=self.request.user).exists():
            return HttpResponseForbidden('Вы уже оставили отзыв на данный контент!')
        else:
            logger.info(f'Пользователь {self.request.user} может оставить отзыв на {object}')

        # Если все проверки пройдены, продолжаем обработку
        return super().dispatch(request, *args, **kwargs)

    # Заполнение полей данными.
    def get_initial(self):
        # Забираем изначальный набор.
        initial = super().get_initial()
        # Добавляем создателя: юзера отправившего запрос.
        initial["creator"] = self.request.user
        # Добавляем тип и объект.
        initial["type"] = self.kwargs.get('type')
        if self.kwargs.get('type') == 'learning_path':
            initial["learning_path"] = LearningPath.objects.get(pk=self.kwargs.get('pk'))
        elif self.kwargs.get('type') == 'material':
            initial["material"] = Material.objects.get(pk=self.kwargs.get('pk'))
        elif self.kwargs.get('type') == 'course':
            initial["course"] = Course.objects.get(pk=self.kwargs.get('pk'))
        elif self.kwargs.get('type') == 'test':
            initial["test"] = Test.objects.get(pk=self.kwargs.get('pk'))
        elif self.kwargs.get('type') == 'event':
            initial["event"] = Event.objects.get(pk=self.kwargs.get('pk'))
        # Возвращаем значения в форму.
        return initial

    # Перенаправление после валидации формы.
    def get_success_url(self):
        # Направляем по адресу объекта.
        if self.kwargs.get('type') == 'learning_path':
            return reverse('learning_path:learning_path', kwargs={'pk': self.kwargs.get('pk')})
        elif self.kwargs.get('type') == 'material':
            return reverse('materials:material', kwargs={'pk': self.kwargs.get('pk')})
        elif self.kwargs.get('type') == 'course':
            return reverse('courses:course', kwargs={'pk': self.kwargs.get('pk')})
        elif self.kwargs.get('type') == 'test':
            return reverse('testing:test', kwargs={'pk': self.kwargs.get('pk')})
        elif self.kwargs.get('type') == 'event':
            return reverse('events:event', kwargs={'pk': self.kwargs.get('pk')})


# Изменение отзыва на объект.
class ObjectsReviewUpdateView(PermissionRequiredMixin, UpdateView):
    # Права доступа
    permission_required = 'reviews.change_review'
    accept_global_perms = True
    # Форма.
    form_class = ObjectsReviewForm
    # Модель.
    model = Review
    # Шаблон.
    template_name = 'review_edit.html'

    # Заполнение полей данными.
    def get_initial(self):
        # Забираем изначальный набор.
        initial = super().get_initial()
        # Добавляем создателя: юзера отправившего запрос.
        initial["creator"] = self.request.user
        # Добавляем объект.
        if self.kwargs.get('type') == 'learning_path':
            initial["learning_path"] = self.object.learning_path
        elif self.kwargs.get('type') == 'material':
            initial["material"] = self.object.material
        elif self.kwargs.get('type') == 'course':
            initial["course"] = self.object.course
        elif self.kwargs.get('type') == 'test':
            initial["test"] = self.object.test
        elif self.kwargs.get('type') == 'event':
            initial["event"] = self.object.event
        return initial

    # Перенаправление после валидации формы.
    def get_success_url(self):
        # Забираем объект для реверса.
        if self.object.type == 'learning_path':
            return reverse('learning_path:learning_path', kwargs={'pk': self.object.learning_path.pk })
        elif self.object.type == 'material':
            return reverse('materials:material', kwargs={'pk': self.object.material.pk })
        elif self.object.type == 'course':
            return reverse('courses:course', kwargs={'pk': self.object.course.pk})
        elif self.object.type == 'test':
            return reverse('testing:test', kwargs={'pk': self.object.test.pk})
        elif self.object.type == 'event':
            return reverse('events:event', kwargs={'pk': self.object.event.pk})

# Удаление отзыва на объект.
class ObjectsReviewDeleteView(PermissionRequiredMixin, DeleteView):
    # Права доступа.
    permission_required = 'core.delete_review'
    accept_global_perms = True
    # Модель.
    model = Review
    # Шаблон.
    template_name = 'review_delete.html'

    # Перенаправление после валидации формы.
    def get_success_url(self):
        # Забираем объект для реверса.
        if self.object.type == 'learning_path':
            return reverse('learning_path:learning_path', kwargs={'pk': self.object.learning_path.pk })
        elif self.object.type == 'material':
            return reverse('materials:material', kwargs={'pk': self.object.material.pk })
        elif self.object.type == 'course':
            return reverse('courses:course', kwargs={'pk': self.object.course.pk})
        elif self.object.type == 'test':
            return reverse('testing:test', kwargs={'pk': self.object.test.pk})
        elif self.object.type == 'event':
            return reverse('events:event', kwargs={'pk': self.object.event.pk})
