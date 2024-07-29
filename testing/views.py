
from django.shortcuts import render

# Create your views here.

from django.conf import settings
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Test, Question, Answer, RelevantPoint, TestsQuestion, TestsQuestionsGenerator
from .filters import TestFilter, QuestionFilter
from .forms import TestForm, QuestionForm, AnswerForm, RelevantPointForm, TestsQuestionsGeneratorForm, AnswersToQuestionForm
from django.shortcuts import render, redirect, reverse, get_object_or_404
from guardian.mixins import PermissionListMixin
from guardian.mixins import PermissionRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin as GPermissionRequiredMixin
from django.utils import timezone
from django.contrib.auth.decorators import permission_required
from guardian.shortcuts import get_perms
from guardian.shortcuts import get_objects_for_user
from guardian.core import ObjectPermissionChecker
from learning_path.models import Result, QuestionsResult, AnswersResult
from django.http import HttpResponseForbidden
from django.db.models import OuterRef, Subquery
from django.db.models.functions import Coalesce
from django.db.models import Case, When, Value
from django.template.response import TemplateResponse
from django.forms import modelformset_factory
from django.forms.formsets import ORDERING_FIELD_NAME
from django.db.models import Q
from django.http import HttpResponseNotFound, HttpResponseForbidden, JsonResponse
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Sum
from django.db import models
import json
from django.core.paginator import Paginator
from django import forms
from django.contrib.auth.decorators import permission_required, login_required
from core.mixins import PreviousPageGetMixinL0, PreviousPageSetMixinL0, PreviousPageGetMixinL1, PreviousPageSetMixinL1, PreviousPageGetMixinL2, PreviousPageSetMixinL2
from reviews.models import Review
from core.models import EmployeesGroupObjectPermission, EmployeesObjectPermission
from reviews.filters import ObjectsReviewFilter
from django.core.paginator import Paginator
from django.contrib.contenttypes.models import ContentType
from core.filters import EmployeesGroupObjectPermissionGroupsFilter, EmployeesObjectPermissionEmployeesFilter
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required



# Импортируем логи
import logging
# Создаем логгер с именем 'project'
logger = logging.getLogger('project')

# Список тестов.
class TestsView(LoginRequiredMixin, PreviousPageSetMixinL1, PermissionListMixin, ListView):
    # Права доступа
    permission_required = 'testing.view_test'
    # Модель.
    model = Test
    # Поле сортировки.
    ordering = 'name'
    # Шаблон.
    template_name = 'tests.html'
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
            test_id=OuterRef('pk'), employee=self.request.user
        ).order_by('-id').values('id', 'attempts_used','status', 'learning_path_result__planned_end_date', 'end_date')[:1]
        queryset = queryset.annotate(
            latest_result_id=Subquery(latest_result.values('id')),
            latest_result_attempts_used=Subquery(latest_result.values('attempts_used')),
            latest_result_status=Subquery(latest_result.values('status')),
            latest_result_planned_end_date=Subquery(latest_result.values('learning_path_result__planned_end_date')),
            latest_result_end_date=Subquery(latest_result.values('end_date'))
        )
        queryset = queryset.annotate(
            has_date=Case(
                When(latest_result_planned_end_date__isnull=False, then=Value(1)),
                default=Value(0),
                output_field=models.IntegerField()
            )
        ).order_by('-has_date', 'latest_result_planned_end_date', 'name')

        # Добавляем модель фильтрации в выборку вью.
        self.filterset = TestFilter(self.request.GET, queryset, request=self.request)

        # Все для блокировки.
        for obj in self.filterset.qs:
            # Забираем результат.
            if obj.results.filter(employee=self.request.user):
                result = obj.results.filter(employee=self.request.user).latest('id')
                # Все для блокировки, если есть результат связанный с задачей.
                if result.learning_task and result.learning_task.blocking_tasks:
                    blocking_tasks = result.learning_task.blocking_tasks.all()
                    # Добавляем задачи.
                    obj.now_blocking_tasks = [
                        blocking_task for blocking_task in blocking_tasks
                        if blocking_task.results.filter(employee=self.request.user).exists() and blocking_task.results.filter(employee=self.request.user).latest('id').status != 'completed'
                    ]

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

# Вывод теста.
class TestView(LoginRequiredMixin, PreviousPageGetMixinL1, PreviousPageSetMixinL0, PermissionRequiredMixin, ListView):
    # Права доступа
    permission_required = 'testing.view_test'
    accept_global_perms = True
    # Модель.
    model = TestsQuestion
    # Поле сортировки.
    ordering = 'position'
    # Шаблон.
    template_name = 'test.html'
    # Количество объектов на странице
    paginate_by = 6

    # Определяем объект проверки.
    def get_permission_object(self):
        test = Test.objects.get(pk=self.kwargs.get('pk'))
        return test

    # Переопределяем выборку вью.
    def get_queryset(self):
        # Переопределяем изначальную выборку.
        test = self.get_permission_object()
        queryset = super().get_queryset().filter(test=test).order_by('position')
        self.qs_count = len(queryset)
        # Возвращаем вью новую выборку.
        return queryset

    # Переопределеяем переменные вью.
    def get_context_data(self, **kwargs):
        # забираем изначальный набор переменных
        context = super().get_context_data(**kwargs)

        # Добавляем во вью.
        test = self.get_permission_object()
        context['object'] = test
        context['qs_count'] = self.qs_count

        # Забираем результат.
        if test.results.filter(employee=self.request.user):
            result = test.results.filter(employee=self.request.user).latest('id')
            blocked = False
            # Все для блокировки, если есть результат связанный с задачей.
            if result.learning_task and result.learning_task.blocking_tasks:
                blocking_tasks = result.learning_task.blocking_tasks.all()
                # Добавляем задачи.
                now_blocking_tasks = [
                    blocking_task for blocking_task in blocking_tasks
                    if blocking_task.results.filter(employee=self.request.user).exists() and blocking_task.results.filter(employee=self.request.user).latest('id').status != 'completed'
                ]
                # Блокируем если есть задачи.
                if now_blocking_tasks:
                    blocked = True
                    context['now_blocking_tasks'] = now_blocking_tasks
                if settings.DEBUG:
                    logger.info(f"Блокировка: {blocked}")
            # Добавляем фильтрсет.
            context['result'] = result
            context['blocked'] = blocked
            # Добавляем все для просрочки.
            if not result.learning_path_result or result.assignment.deadlines == False or (result.learning_path_result.planned_end_date >= datetime.now().date() and result.assignment.deadlines == True):
                context['overdue'] = False
                if result.learning_path_result is None:
                    if settings.DEBUG:
                        logger.info(f'Тест активен')
                else:
                    if settings.DEBUG:
                        logger.info(f'Тест активен до: {result.learning_path_result.planned_end_date}')
            else:
                if settings.DEBUG:
                    logger.info(f'Тест просрочен с: {result.learning_path_result.planned_end_date}')
                context['overdue'] = True

        # Получаем доп. информацию.
        if test.tests_questions.exists():

            # Создаем переменную.
            tests_questions_exists = True
            context['tests_questions_exists']=tests_questions_exists

            # Создаем переменную.
            maximum_test_score = 0

            # Забираем сумму баллов за вопросы.
            questions = Question.objects. \
                filter(tests_questions__test=test).order_by('tests_questions__position')
            questions_scores_sum = questions.aggregate(sum=Sum('score'))['sum']
            context['questions_scores_sum'] = questions_scores_sum
            maximum_test_score += questions_scores_sum
            logger.info(f'Сумма баллов в вопросах теста: {questions_scores_sum}')

            # Забираем сумму баллов за ответы.
            if Answer.objects.filter(question__in=questions).exists():
                answers = Answer.objects.filter(question__in=questions)
                answers_scores_sum = answers.aggregate(sum=Sum('score'))['sum']
                context['answers_scores_sum'] = answers_scores_sum
                maximum_test_score += answers_scores_sum
                logger.info(f'Сумма баллов в ответах на вопросы теста: {answers_scores_sum}')

            # Забираем максимальный балл.
            context['maximum_test_score'] = maximum_test_score
            logger.info(f'Максимальный балл: {maximum_test_score}')

        # Добавляем средний балл.
        # Сначала получаем сумму оценок и количество отзывов.
        reviews_sum = test.reviews.aggregate(Sum('score'))['score__sum']
        reviews_count = test.reviews.count()
        # Вычисляем среднюю оценку.
        if reviews_count > 0:
            reviews_average_mark = round((reviews_sum / reviews_count), 1)
        else:
            reviews_average_mark = 0
        # Добавляем вью.
        context['reviews_average_mark'] = reviews_average_mark

        # Добавляем отзывы.
        if Review.objects.filter(type='test', test__pk=self.kwargs.get('pk')).exists():
            reviews_queryset = Review.objects.filter(type='test', test__pk=self.kwargs.get('pk')).order_by('created')
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
        if test.reviews.filter(creator=self.request.user).exists():
            haves_review = True
        if settings.DEBUG:
            logger.info(f"Уже есть отзыв: {haves_review}")
        context['haves_review'] = haves_review

        # Добавляем объектные права.
        content_type = ContentType.objects.get_for_model(Test)
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
        group_object_permissions_filter = EmployeesGroupObjectPermissionGroupsFilter(self.request.GET, queryset=group_object_permissions_queryset, request=self.request)
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
        object_permissions_filter = EmployeesObjectPermissionEmployeesFilter(self.request.GET, queryset=object_permissions_queryset, request=self.request)
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

# Сортировка вопросов теста.
@login_required
@permission_required('testing.change_test')
def tests_questions_ordering(request, pk):

    #Кверисет.
    queryset = TestsQuestion.objects.filter(test__pk=pk).order_by('position')

    # Формсет.
    TestsQuestionFormSet = modelformset_factory(
        TestsQuestion,
        fields=('question',),
        can_order=True,
        can_delete=False,
        extra=0,
        widgets={
            'question': forms.HiddenInput(),
        },
    )

    # Если форма отправлена.
    if request.method == 'POST':
        formset = TestsQuestionFormSet(request.POST, queryset=queryset)
        if formset.is_valid():
            for form in formset:
                if form.cleaned_data:
                    tests_questions = form.save(commit=False)
                    tests_questions.position = form.cleaned_data[ORDERING_FIELD_NAME]
                    tests_questions.save()
            return redirect('testing:test', pk=pk)

    # Если форма открыта.
    else:
        formset = TestsQuestionFormSet(queryset=queryset)

    # Контекст.
    contex = {'formset': formset}

    # Форма.
    return render(request, 'tests_questions_ordering.html', contex)


# Создание теста.
class TestCreateView(LoginRequiredMixin, GPermissionRequiredMixin, CreateView):
    # Права доступа.
    permission_required = 'testing.add_test'
    # Форма.
    form_class = TestForm
    # Модель.
    model = Test
    # Шаблон.
    template_name = 'test_edit.html'

    # Заполнение полей данными.
    def get_initial(self):
        # Забираем изначальный набор.
        initial = super().get_initial()
        # Добавляем создателя: юзера отправившего запрос.
        initial["creator"] = self.request.user
        # Возвращаем значения в форму.
        return initial

    # Перенаправление после валидации формы.
    def get_success_url(self):
        # Направляем по адресу объекта.
        return reverse('testing:test', kwargs={'pk': self.object.pk})

# Изменение теста.
class TestUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    # Права доступа
    permission_required = 'testing.change_test'
    accept_global_perms = True
    # Форма.
    form_class = TestForm
    # Модель.
    model = Test
    # Шаблон.
    template_name = 'test_edit.html'

    # Заполнение полей данными.
    def get_initial(self):
        # Забираем изначальный набор.
        initial = super().get_initial()
        # Добавляем создателя: юзера отправившего запрос.
        initial["creator"] = self.request.user
        # Возвращаем значения в форму.
        return initial

    # Перенаправление после валидации формы.
    def get_success_url(self):
        # Направляем по адресу объекта.
        return reverse('testing:test', kwargs={'pk': self.object.pk})

# Удаление теста.
class TestDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    # Права доступа
    permission_required = 'testing.delete_test'
    accept_global_perms = True
    # Модель.
    model = Test
    # Шаблон.
    template_name = 'test_delete.html'

    # Перенаправление после валидации формы.
    def get_success_url(self):
        # Направляем по адресу объектов.
        return reverse('testing:tests')

# Список вопросов.
class QuestionsView(LoginRequiredMixin, PreviousPageSetMixinL1, PermissionListMixin, ListView):
    # Права доступа
    permission_required = 'testing.view_question'
    # Модель.
    model = Question
    # Поле сортировки.
    ordering = 'text'
    # Шаблон.
    template_name = 'questions.html'
    # Количество объектов на странице
    paginate_by = 6

    # Переопределяем выборку вью.
    def get_queryset(self):
        # Забираем изначальную выборку вью.
        queryset = super().get_queryset().prefetch_related(
            'categories',
        )
        # Добавляем модель фильтрации в выборку вью.
        self.filterset = QuestionFilter(self.request.GET, queryset, request=self.request)
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

# Вывод вопроса.
class QuestionView(LoginRequiredMixin, PreviousPageGetMixinL1, PermissionRequiredMixin, ListView):
    # Права доступа
    permission_required = 'testing.view_question'
    accept_global_perms = True
    # Модель.
    model = Answer
    # Поле сортировки.
    ordering = 'position'
    # Шаблон.
    template_name = 'question.html'
    # Количество объектов на странице
    paginate_by = 6

    # Определяем объект проверки.
    def get_permission_object(self):
        question = Question.objects.get(pk=self.kwargs.get('pk'))
        return question

    # Переопределяем выборку вью.
    def get_queryset(self):
        # Переопределяем изначальную выборку.
        question = self.get_permission_object()
        queryset = super().get_queryset().filter(question=question).order_by('position')
        self.qs_count = len(queryset)
        # Возвращаем вью новую выборку.
        return queryset

    # Переопределеяем переменные вью.
    def get_context_data(self, **kwargs):
        # забираем изначальный набор переменных
        context = super().get_context_data(**kwargs)
        # Добавляем во вью.
        question = self.get_permission_object()
        context['object'] = question
        context['qs_count'] = self.qs_count
        # Получаем доп. информацию.
        if question.answers.exists():
            # Создаем переменную.
            answers_exists = True
            context['answers_exists']=answers_exists
        # Возвращаем новый набор переменных в контролер.
        return context

# Создание вопроса.
class QuestionCreateView(LoginRequiredMixin, GPermissionRequiredMixin, CreateView):
    # Права доступа.
    permission_required = 'testing.add_question'
    # Форма.
    form_class = QuestionForm
    # Модель.
    model = Question
    # Шаблон.
    template_name = 'question_edit.html'

    # Заполнение полей данными.
    def get_initial(self):
        # Забираем изначальный набор.
        initial = super().get_initial()
        # Добавляем создателя: юзера отправившего запрос.
        initial["creator"] = self.request.user
        # Возвращаем значения в форму.
        return initial

    # Перенаправление после валидации формы.
    def get_success_url(self):
        # Направляем по адресу объекта.
        return reverse('testing:question', kwargs={'pk': self.object.pk})

# Изменение вопроса.
class QuestionUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    # Права доступа
    permission_required = 'testing.change_question'
    accept_global_perms = True
    # Форма.
    form_class = QuestionForm
    # Модель.
    model = Question
    # Шаблон.
    template_name = 'question_edit.html'

    # Заполнение полей данными.
    def get_initial(self):
        # Забираем изначальный набор.
        initial = super().get_initial()
        # Добавляем создателя: юзера отправившего запрос.
        initial["creator"] = self.request.user
        # Добавляем тип, т.к. поле скрыто.
        initial["type"] = self.object.type
        # Возвращаем значения в форму.
        return initial

    # Перенаправление после валидации формы.
    def get_success_url(self):
        # Направляем по адресу объекта.
        return reverse('testing:question', kwargs={'pk': self.object.pk})

# Удаление вопроса.
class QuestionDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    # Права доступа
    permission_required = 'testing.delete_question'
    accept_global_perms = True
    # Модель.
    model = Question
    # Шаблон.
    template_name = 'question_delete.html'

    # Перенаправление после валидации формы.
    def get_success_url(self):
        # Направляем по адресу объектов.
        return reverse('testing:questions')

# Создание категории.
class TestsQuestionsGeneratorCreateView(LoginRequiredMixin, GPermissionRequiredMixin, CreateView):
    # Права доступа.
    permission_required = 'testing.add_test'
    # Форма.
    form_class = TestsQuestionsGeneratorForm
    # Модель.
    model = TestsQuestionsGenerator
    # Шаблон.
    template_name = 'tests_questions_generator_edit.html'

    # Определяем объект проверки.
    def get_permission_object(self):
        self.test = Test.objects.get(pk=self.kwargs.get('pk'))
        return self.test

    # Заполнение полей данными.
    def get_initial(self):
        # Забираем изначальный набор.
        initial = super().get_initial()
        # Добавляем создателя: юзера отправившего запрос.
        initial["creator"] = self.request.user
        # Добавляем группу из которой создан генератор.
        initial["test"] = Test.objects.get(pk=self.kwargs.get('pk'))
        # Возвращаем значения в форму.
        return initial

    # Валидация формы.
    def form_valid(self, form):
        # Сохраняем объект без коммита.
        self.object = form.save(commit=False)
        # Сохраняем объект в базу данных.
        self.object.save()

        # Логируем информацию об объекте после сохранения.
        if settings.DEBUG:
            logger.info(f"Объект после сохранения: {self.object}")
            logger.info(f"Поля объекта после сохранения: {vars(self.object)}")

        # Сохраняем связи.
        form.save_m2m()

        # Логируем информацию о связанных объектах.
        if settings.DEBUG:
            for related_object in form.cleaned_data:
                logger.info(f"Связанный объект: {related_object}")
                logger.info(f"Значение: {form.cleaned_data[related_object]}")

        # Вызываем базовую реализацию для дальнейшей обработки.
        return super(TestsQuestionsGeneratorCreateView, self).form_valid(form)

    # Перенаправление после валидации формы.
    def get_success_url(self):
        # Направляем по адресу объекта.
        return reverse('testing:test', kwargs={'pk': self.object.test.pk})

# Изменение категории.
class TestsQuestionsGeneratorUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    # Права доступа.
    permission_required = 'testing.change_test'
    accept_global_perms = True
    # Форма.
    form_class = TestsQuestionsGeneratorForm
    # Модель.
    model = TestsQuestionsGenerator
    # Шаблон.
    template_name = 'tests_questions_generator_edit.html'

    # Определяем объект проверки.
    def get_permission_object(self):
        test = self.get_object().test
        return test

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
        if settings.DEBUG:
            logger.info(f"Объект после сохранения: {self.object}")
            logger.info(f"Поля объекта после сохранения: {vars(self.object)}")

        # Сохраняем связи.
        form.save_m2m()

        # Логируем информацию о связанных объектах.
        if settings.DEBUG:
            for related_object in form.cleaned_data:
                logger.info(f"Связанный объект: {related_object}")
                logger.info(f"Значение: {form.cleaned_data[related_object]}")

        # Вызываем базовую реализацию для дальнейшей обработки.
        return super(TestsQuestionsGeneratorUpdateView, self).form_valid(form)

    # Перенаправление после валидации формы.
    def get_success_url(self):
        # Направляем по адресу объекта.
        return reverse('testing:test', kwargs={'pk': self.object.test.pk})

# Создание вопроса.
class AnswerCreateView(LoginRequiredMixin, GPermissionRequiredMixin, CreateView):
    # Права доступа.
    permission_required = 'testing.add_question'
    # Форма.
    form_class = AnswerForm
    # Модель.
    model = Answer
    # Шаблон.
    template_name = 'answer_edit.html'

    # Определяем объект проверки.
    def get_permission_object(self):
        question = Question.objects.get(pk=self.kwargs.get('pk'))
        return question

    # Добавляем в форму аргументы.
    def get_form_kwargs(self):
        kwargs = super(AnswerCreateView, self).get_form_kwargs()
        question = self.get_permission_object()
        kwargs['question_pk'] = question.pk
        return kwargs

    # Заполнение полей данными.
    def get_initial(self):
        # Забираем изначальный набор.
        initial = super().get_initial()
        # Добавляем позицию.
        question = self.get_permission_object()
        last_position = question.answers.order_by('position').values_list('position', flat=True).last()
        if last_position:
            position = last_position + 1
        else:
            position = 1
        initial["position"] = position
        # Добавляем создателя: юзера отправившего запрос.
        initial["creator"] = self.request.user
        # Добавляем создателя: юзера отправившего запрос.
        initial["question"] = question
        # Возвращаем значения в форму.
        return initial

    # Перенаправление после валидации формы.
    def get_success_url(self):
        # Направляем по адресу объекта.
        return reverse('testing:question', kwargs={'pk': self.object.question.pk})

# Сортировка ответов на вопрос.
@login_required
@permission_required('testing.change_question')
def answers_ordering(request, pk):

    #Кверисет.
    queryset = Answer.objects.filter(question__pk=pk).order_by('position')

    # Формсет.
    AnswerFormSet = modelformset_factory(
        Answer,
        fields=('text',),
        can_order=True,
        can_delete=False,
        extra=0,
        widgets={
            'text': forms.HiddenInput(),
        },
    )

    # Если форма отправлена.
    if request.method == 'POST':
        formset = AnswerFormSet(request.POST, queryset=queryset)
        if formset.is_valid():
            for form in formset:
                if form.cleaned_data:
                    answers = form.save(commit=False)
                    answers.position = form.cleaned_data[ORDERING_FIELD_NAME]
                    answers.save()
            return redirect('testing:question', pk=pk)

    # Если форма открыта.
    else:
        formset = AnswerFormSet(queryset=queryset)

    # Контекст.
    contex = {'formset': formset}

    # Форма.
    return render(request, 'answers_ordering.html', contex)

# Изменение вопроса.
class AnswerUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    # Права доступа
    permission_required = 'testing.change_question'
    accept_global_perms = True
    # Форма.
    form_class = AnswerForm
    # Модель.
    model = Answer
    # Шаблон.
    template_name = 'answer_edit.html'

    # Определяем объект проверки.
    def get_permission_object(self):
        question = self.get_object().question
        return question

    # Добавляем в форму аргументы.
    def get_form_kwargs(self):
        kwargs = super(AnswerUpdateView, self).get_form_kwargs()
        kwargs['question_pk'] = self.object.question.pk
        return kwargs

    # Заполнение полей данными.
    def get_initial(self):
        # Забираем изначальный набор.
        initial = super().get_initial()
        # Добавляем создателя: юзера отправившего запрос.
        initial["creator"] = self.request.user
        # Возвращаем значения в форму.
        return initial

    # Перенаправление после валидации формы.
    def get_success_url(self):
        # Направляем по адресу объекта.
        return reverse('testing:question', kwargs={'pk': self.object.question.pk})

# Удаление вопроса.
class AnswerDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    # Права доступа
    permission_required = 'testing.change_question'
    accept_global_perms = True
    # Модель.
    model = Answer
    # Шаблон.
    template_name = 'answer_delete.html'

    # Определяем объект проверки.
    def get_permission_object(self):
        question = self.get_object().question
        return question

    # Перенаправление после валидации формы.
    def get_success_url(self):
        # Направляем по адресу объектов.
        return reverse('testing:question', kwargs={'pk': self.object.question.pk})

# Создание соотвествующего пункта.
class RelevantPointCreateView(LoginRequiredMixin, GPermissionRequiredMixin, CreateView):
    # Права доступа.
    permission_required = 'testing.add_question'
    # Форма.
    form_class = RelevantPointForm
    # Модель.
    model = RelevantPoint
    # Шаблон.
    template_name = 'relevant_point_edit.html'

    # Определяем объект проверки.
    def get_permission_object(self):
        answer = Answer.objects.get(pk=self.kwargs.get('pk'))
        question = answer.question
        return question

    # Заполнение полей данными.
    def get_initial(self):
        # Забираем изначальный набор.
        initial = super().get_initial()
        # Добавляем создателя: юзера отправившего запрос.
        initial["creator"] = self.request.user
        # Добавляем создателя: юзера отправившего запрос.
        initial["answer"] = Answer.objects.get(pk=self.kwargs.get('pk'))
        # Возвращаем значения в форму.
        return initial

    # Перенаправление после валидации формы.
    def get_success_url(self):
        # Направляем по адресу объекта.
        return reverse('testing:question', kwargs={'pk': self.object.answer.question.pk})

# Изменение соотвествующего пункта.
class RelevantPointUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    # Права доступа
    permission_required = 'testing.change_question'
    accept_global_perms = True
    # Форма.
    form_class = RelevantPointForm
    # Модель.
    model = RelevantPoint
    # Шаблон.
    template_name = 'relevant_point_edit.html'

    # Определяем объект проверки.
    def get_permission_object(self):
        question = self.get_object().answer.question
        return question

    # Заполнение полей данными.
    def get_initial(self):
        # Забираем изначальный набор.
        initial = super().get_initial()
        # Добавляем создателя: юзера отправившего запрос.
        initial["creator"] = self.request.user
        # Возвращаем значения в форму.
        return initial

    # Перенаправление после валидации формы.
    def get_success_url(self):
        # Направляем по адресу объекта.
        return reverse('testing:question', kwargs={'pk': self.object.answer.question.pk})

# Функция завершения теста.
@login_required
def completion_of_test(request, tests_result, test):

    # Забираем результаты
    if settings.DEBUG:
        logger.info(f'Набранные балы за тест: {tests_result.score}\n')
        logger.info(f'Проходной бал по тесту: {test.passing_score}\n')
        logger.info(f'Тест пройден?: {bool(tests_result.score >= test.passing_score)}\n')

    # Если результат теста больше проходного балла - проставляем "Выполнено".
    if tests_result.score >= test.passing_score:
        tests_result.status = 'completed'

    # Иначе - "Провалено".
    else:
        tests_result.status = 'failed'

    # Объявляем %.
    maximum_test_score = 0

    # Забираем сумму баллов за вопросы.
    questions = Question.objects.filter(tests_questions__test=test).order_by('tests_questions__position')
    questions_scores_sum = questions.aggregate(sum=Sum('score'))['sum']
    maximum_test_score += questions_scores_sum
    if settings.DEBUG:
        logger.info(f'Сумма баллов в вопросах теста: {questions_scores_sum}')

    # Забираем сумму баллов за ответы.
    if Answer.objects.filter(question__in=questions).exists():
        answers = Answer.objects.filter(question__in=questions)
        answers_scores_sum = answers.aggregate(sum=Sum('score'))['sum']
        maximum_test_score += answers_scores_sum
        if settings.DEBUG:
            logger.info(f'Сумма баллов в ответах на вопросы теста: {answers_scores_sum}')

    # Забираем %.
    if maximum_test_score != 0:
        score_scaled = round((tests_result.score / maximum_test_score) * 100)
    else:
        score_scaled = 0
    if settings.DEBUG:
        logger.info(f'Максимальный балл: {maximum_test_score}')

    # Устанавливаем %.
    tests_result.score_scaled = score_scaled
    if settings.DEBUG:
        logger.info(f'Полученный балл в %: {tests_result.score_scaled}')

    # Проставляем дату завершения.
    tests_result.end_date = timezone.now()
    if settings.DEBUG:
        logger.info(f'Время завершения теста: {tests_result.end_date}\n')

    # Проставляем использование попытки.
    tests_result.attempts_used += 1
    if settings.DEBUG:
        logger.info(f'Использовано попыток: {tests_result.attempts_used}\n')
    tests_result.save()
    if settings.DEBUG:
        logger.info(f'Результат теста: {tests_result.get_status_display()}\n')

# Функция прохождения теста.
@login_required
def take_assigned_test(request, pk):

    # Забираем результат теста и тест.
    tests_result = Result.objects.get(pk=pk)
    test = tests_result.test
    if settings.DEBUG:
        logger.info(f'Результат теста: {tests_result}\n')
        logger.info(f'Тест: {test}\n')

    # Если страницу открыл не тот, кому назначено, запрещаем доступ.
    if tests_result.employee != request.user:
        return HttpResponseForbidden('Этот тест назначен не Вам!')

    # Если тест заблокирован.
    if tests_result.learning_task and tests_result.learning_task.blocking_tasks:
        blocking_tasks = tests_result.learning_task.blocking_tasks.all()
        blocking_tasks_results = [
            blocking_task.results.filter(employee=request.user).latest('id')
            for blocking_task in blocking_tasks
        ]
        if any(blocking_task_results.status != 'completed' for blocking_task_results in blocking_tasks_results):
            return HttpResponseForbidden('Тест заблокирован!')

    # Если дата уже наступила.
    if tests_result.learning_path_result and tests_result.learning_path_result.planned_end_date <= datetime.now().date():
        return HttpResponseForbidden('Тест просрочен!')

    # Если нет вопросов.
    if not test.tests_questions.exists():
        return HttpResponseForbidden('В тесте нет вопросов!')

    # Если нет результатов вопросов и результатов ответов - создаем их.
    if not tests_result.questions_results.exists():

        # Забираем вопросы теста.
        questions = Question.objects.\
            filter(tests_questions__test=test).order_by('tests_questions__position')
        if settings.DEBUG:
            logger.info(f'Вопросы теста: {questions}\n')

        # Создаем результаты вопросов теста.
        for question in questions:
            questions_result = QuestionsResult.objects.\
                create(question=question, tests_result=tests_result)
            if settings.DEBUG:
                logger.info(f'Создан результат вопроса теста: {questions_result}\n')

            # Забираем ответы на вопросы теста.
            answers = question.answers.all()
            if settings.DEBUG:
                logger.info(f'Ответы на вопрос теста: {answers}\n')

            # Создаем результаты ответов на вопросы теста.
            for answer in answers:
                answers_result = AnswersResult.objects.create(answer=answer, questions_result=questions_result)
                if settings.DEBUG:
                    logger.info(f'Создан результат ответа на вопрос теста: {answers_result}\n')

    # Если статус теста "Назначен" - запускаем процесс.
    if tests_result.status == 'appointed':
        # Забираем результаты вопросов.
        questions_results = tests_result.questions_results.all()
        if settings.DEBUG:
            logger.info(f'Результаты вопросов теста: {questions_results}\n')

        # Если в тесте указан случайный порядок вопросов - генерируем его.
        if test.random_questions == True:
            sorting_questions_results_id = [questions_result.id for questions_result in questions_results.order_by('?')]
            if settings.DEBUG:
                logger.info(f'Создан список в случайном порядке: {sorting_questions_results_id}\n')
            sorting_questions_results_json = json.dumps(sorting_questions_results_id)
            if settings.DEBUG:
                logger.info(f'Создан джисон в случайном порядке: {sorting_questions_results_json}\n')

        # Если указан строгий порядок ответов - его.
        else:
            sorting_questions_results_id = [questions_result.id for questions_result in questions_results.order_by('question__tests_questions__position')]
            if settings.DEBUG:
                logger.info(f'Создан список в строгом порядке: {sorting_questions_results_id}\n')
            sorting_questions_results_json = json.dumps(sorting_questions_results_id)
            if settings.DEBUG:
                logger.info(f'Создан джисон в строгом порядке: {sorting_questions_results_json}\n')

        # Записываем порядок вопросов в поле.
        tests_result.sorting_questions_results = sorting_questions_results_json

        # Получаем интервал до окончания теста.
        interval = tests_result.test.time_to_complete * 60
        if settings.DEBUG:
            logger.info(f'До окончания теста (сек): {interval}\n')

        # Получаем время до окончания теста.
        attempt_end_time = timezone.now() + timedelta(seconds=interval)
        if settings.DEBUG:
            logger.info(f'Время окончания теста: {attempt_end_time}\n')

        # Сохраняем время окончания теста в специальное поле.
        tests_result.attempt_end_time = attempt_end_time

        # Меняем статус теста на "В процессе".
        tests_result.status = 'in_progress'

        # Проставляем дату начала.
        tests_result.start_date = timezone.now()

        # Сохраняем результат теста.
        if settings.DEBUG:
            logger.info(f'Новый статус результат теста: {tests_result.get_status_display()}\n')
        tests_result.save()

    # Если тест еще не пройден и не провален - забираем все результаты вопросов.
    if tests_result.status == 'in_progress':

        # Если в тест еще остались неотвеченные вопросы - забираем.
        if tests_result.questions_results. \
                filter(Q(status='appointed') | Q(status='in_progress')).exists():
            questions_results = tests_result.questions_results. \
                filter(Q(status='appointed') | Q(status='in_progress'))
            if settings.DEBUG:
                logger.info(f'Результаты вопросов: {questions_results}\n')

            # Применяем сортировку.
            sorting_questions_results_id = json.loads(tests_result.sorting_questions_results)
            if settings.DEBUG:
                logger.info(f'Разджисоненный список вопросов: {sorting_questions_results_id}\n')
            questions_results_list = sorted(questions_results, key=lambda qr: sorting_questions_results_id.index(qr.id))
            if settings.DEBUG:
                logger.info(f'Отсортированные результаты вопросов: {questions_results_list}\n')
            questions_result = questions_results_list[0]
            if settings.DEBUG:
                logger.info(f'Вопрос теста: {questions_result}\n')

            # Переходим
            return redirect('testing:answer_to_question', pk=questions_result.id)

        # Если все вопросы уже пройдены.
        else:

            # Вызываем завершение теста.
            completion_of_test(request=request, test=test, tests_result=tests_result)

            # Переходим.
            return redirect('testing:test', pk=test.id)

    # Если тест пройден.
    else:

        return HttpResponseForbidden('Этот тест уже пройден!')


# Функция прохождения теста.
@login_required
def view_test_results(request, pk):

    # Забираем результат теста и тест.
    tests_result = Result.objects.get(pk=pk)
    test = tests_result.test
    if settings.DEBUG:
        logger.info(f'Результат теста: {tests_result}\n')
        logger.info(f'Тест: {test}\n')

    # Если страницу открыл не тот, кому назначено, запрещаем доступ.
    if tests_result.employee != request.user:
        return HttpResponseForbidden('Этот тест назначен не Вам!')

    # Забираем вопросы.
    questions_results = tests_result.questions_results.all()
    if settings.DEBUG:
        logger.info(f'Результаты вопросов: {questions_results}\n')

    # Применяем сортировку.
    sorting_questions_results_id = json.loads(tests_result.sorting_questions_results)
    if settings.DEBUG:
        logger.info(f'Разджисоненный список вопросов: {sorting_questions_results_id}\n')
    questions_results_list = sorted(questions_results, key=lambda qr: sorting_questions_results_id.index(qr.id))
    if settings.DEBUG:
        logger.info(f'Отсортированные результаты вопросов: {questions_results_list}\n')
    questions_result = questions_results_list[0]
    if settings.DEBUG:
        logger.info(f'Вопрос теста: {questions_result}\n')

    # Переходим
    return redirect('testing:answer_to_question', pk=questions_result.id)

# Функция ответа на вопрос теста.
@login_required
def answer_to_question(request, pk):

    # Забираем резульат вопроса.
    questions_result = QuestionsResult.objects.get(pk=pk)
    if settings.DEBUG:
        logger.info(f'Результат вопроса: {questions_result}\n')

    # Забираем вопрос.
    question = questions_result.question
    if settings.DEBUG:
        logger.info(f'Вопрос: {question}\n')

    # Забираем результат теста.
    tests_result = questions_result.tests_result
    if settings.DEBUG:
        logger.info(f'Результат теста: {tests_result}\n')

    # Забираем результаты вопросов.
    questions_results = tests_result.questions_results.all()
    if settings.DEBUG:
        logger.info(f'Результаты вопросов теста: {questions_results}\n')

    # Забираем тест.
    test = tests_result.test
    if settings.DEBUG:
        logger.info(f'Тест: {test}\n')

    # Если запрос отправил не тот, кому он назначен - закрываем доступ.
    if questions_result.tests_result.employee != request.user:
        return HttpResponseForbidden('Тест назначен не вам!')

    # Если дата уже наступила.
    if tests_result.learning_path_result and tests_result.learning_path_result.planned_end_date <= datetime.now().date():
        return HttpResponseForbidden('Тест просрочен!')

    # Если тест заблокирован.
    if tests_result.learning_task and tests_result.learning_task.blocking_tasks:
        blocking_tasks = tests_result.learning_task.blocking_tasks.all()
        blocking_tasks_results = [
            blocking_task.results.filter(employee=request.user).latest('id')
            for blocking_task in blocking_tasks
        ]
        if any(blocking_task_results.status != 'completed' for blocking_task_results in blocking_tasks_results):
            return HttpResponseForbidden('Тест заблокирован!')

    # Если статус вопроса "Назначен", меняем на "В процессе" и проставляем дату начала.
    if settings.DEBUG:
        logger.info(f'Старый статус результат вопроса: {questions_result.get_status_display()}\n')
    if questions_result.status == 'appointed':
        questions_result.status = 'in_progress'
        questions_result.start_date = timezone.now()
        questions_result.save()
    if settings.DEBUG:
        logger.info(f'Новый статус результат вопроса: {questions_result.get_status_display()}\n')
    # Забираем результаты ответа на вопрос c учетом сортировки.
    if test.random_questions == True:
        queryset = AnswersResult.objects.filter(questions_result=questions_result).order_by('?')
    else:
        queryset = AnswersResult.objects.filter(questions_result=questions_result).order_by('position')
    if settings.DEBUG:
        logger.info(f'Выборка ответов на вопрос: {queryset}\n')
    # Создаем модель формсета.
    AnswerToQuestionFormSet = modelformset_factory(AnswersResult, form=AnswersToQuestionForm, extra=0)
    # Если форма отправлена.
    if request.method == 'POST':
        # Создаем формсет.
        formset = AnswerToQuestionFormSet(request.POST, queryset=queryset)
        # Если данные валидны.
        if formset.is_valid():
            # Предварительно сохраняем данные для дальнейших операций.
            formset.save(commit=False)
            # Проходим циклом по формам.
            for form in formset:
                # Забираем правильный и введенный ответ в зависимости от типа вопроса.
                if question.type == 'single_selection' or question.type == 'multiple_choice':
                    correct_answer = form.instance.answer.correct_answer
                    selected_answer = form.cleaned_data["selected_answer"]
                elif question.type == 'sorting':
                    correct_answer = form.instance.answer.correct_position
                    selected_answer = form.cleaned_data["selected_position"]
                elif question.type == 'compliance':
                    correct_answer = form.instance.answer.relevant_point
                    selected_answer = form.cleaned_data["selected_relevant_point"]
                elif question.type == 'text_input':
                    correct_answer = form.instance.answer.correct_text_input
                    selected_answer = form.cleaned_data["selected_text_input"]
                elif question.type == 'numeric_input':
                    correct_answer = form.instance.answer.correct_numeric_input
                    selected_answer = form.cleaned_data["selected_numeric_input"]
                if settings.DEBUG:
                    logger.info(f'Введенные данные: {form.cleaned_data}\n')
                    logger.info(f'Правильный ответ: {correct_answer}\n')
                    logger.info(f'Выбранный ответ: {selected_answer}\n')
                    logger.info(f'Возможный балл за ответ: {form.instance.answer.score}\n')
                # Если ответ верный, записываем в результат баллы и отметку.
                if selected_answer == correct_answer:
                    form.instance.score = form.instance.answer.score
                    form.instance.status = 'completed'
                # Если ответ НЕ верный, обнуляем баллы и проставляем отметку.
                else:
                    form.instance.score = 0
                    form.instance.status = 'failed'
                if settings.DEBUG:
                    logger.info(f'Статус ответа: {form.instance.get_status_display()}\n')
                    logger.info(f'Полученный балл за ответ: {form.instance.score}\n')
                # Сохраняем форму.
                form.save()
            # Печатаем сохраненные объекты.
            for saved_object in queryset:
                if settings.DEBUG:
                    logger.info(f'Сохраненный объект: {saved_object.__dict__}')
            # Если все ответы верные, начисляем баллы и проставляем выполнение вопроса.
            if settings.DEBUG:
                logger.info(f'Все ответы верные: {bool(not queryset.exclude(status="completed").exists())}\n')
                logger.info(f'Возможный балл за вопрос: {question.score}\n')
            answers_scores_sum = queryset.aggregate(sum=Sum('score'))['sum']
            if not queryset.exclude(status="completed").exists():
                questions_result.score = question.score
                tests_result.score += questions_result.score
                tests_result.score += answers_scores_sum
                questions_result.status = 'completed'
            # Если есть неверные ответы, проставляем провал и обнуляем баллы
            else:
                questions_result.score = 0
                questions_result.status = 'failed'
            questions_result.end_date = timezone.now()
            if settings.DEBUG:
                logger.info(f'Статус вопроса: {questions_result.get_status_display()}\n')
                logger.info(f'Полученные баллы за ответы: {answers_scores_sum}\n')
                logger.info(f'Полученный балл за вопрос: {questions_result.score}\n')
                logger.info(f'Полученный балл за тест: {tests_result.score}\n')
                logger.info(f'Время завершения вопроса: {questions_result.end_date}\n')
            # Cохраняем изменения.
            questions_result.save()
            tests_result.save()
            if settings.DEBUG:
                logger.info(f'Результат вопроса: {questions_result}\n')
                logger.info(f'Результат теста: {tests_result}\n')
            # Переходим.
            return redirect('testing:answer_to_question', pk=questions_result.id)

    # Если форма открыта.
    else:
        # Создаем формсет.
        formset = AnswerToQuestionFormSet(queryset=queryset)

    # Получаем время до окончания теста.
    attempt_end_time = round((tests_result.attempt_end_time - timezone.now()).total_seconds())
    logger.info(f'Время окончания теста: {attempt_end_time}\n')

    # Получаем предыдущий и следующий элемент.
    sorting_questions_results_id = json.loads(tests_result.sorting_questions_results)
    questions_results_list = sorted(questions_results, key=lambda qr: sorting_questions_results_id.index(qr.id))
    questions_results_list_count = questions_results.count()
    current_index = next((index for index, qr in enumerate(questions_results_list) if qr.id == questions_result.id), None)
    current_index_normal = current_index + 1
    next_question_result = questions_results_list[current_index+1] if current_index < len(questions_results_list) - 1 else None
    previous_question_result = questions_results_list[current_index-1] if current_index > 0 else None
    if settings.DEBUG:
        logger.info(f'Разджисоненный список вопросов: {sorting_questions_results_id}\n')
        logger.info(f'Отсортированные результаты вопросов: {questions_results_list}\n')
        logger.info(f'Длинна списка: {questions_results_list_count}\n')
        logger.info(f'Индекс текущего результата вопроса: {current_index}\n')
        logger.info(f'Следующий результат вопроса: {next_question_result}\n')
        logger.info(f'Предыдущий результат вопроса: {previous_question_result}\n')

    # Пагинация.
    paginator = Paginator(questions_results_list, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Деактивация полей, если вопрос завершен
    if questions_result.status == 'completed' or questions_result.status == 'failed':
        for form in formset:
            for field in form.fields.values():
                field.disabled = True

    # Проверяем пора ли заканчивать тест.
    if not questions_results.filter(status='appointed').exists() and not questions_results.filter(status='in_progress').exists() and not tests_result.end_date:
        end_of_test = True
    else:
        end_of_test = False

    # Если тест закончен - деактивируем поля.
    if tests_result.status == 'completed' or tests_result.status == 'failed' and tests_result.end_date:
        # Деактивация полей, если тест завершен.
        if questions_result.status == 'appointed' or questions_result.status == 'in_progress':
            for form in formset:
                for field in form.fields.values():
                    field.disabled = True

    # Отдаем контекст.
    context = {'formset': formset,
               'tests_result': tests_result,
               'questions_result': questions_result,
               'questions_results_list': questions_results_list,
               'questions_results_list_count': questions_results_list_count,
               'page_obj': page_obj,
               'time': attempt_end_time,
               'current_index': current_index,
               'current_index_normal': current_index_normal,
               'next_question_result': next_question_result,
               'previous_question_result': previous_question_result,
               'end_of_test': end_of_test
               }

    # Возвращаем шаблон с формой.
    return render(request, 'answer_to_question.html', context)

# Функция завершения не пройденного теста.
@login_required
def attempt_end_timeout(request, pk):

    # Забираем результат теста и тест.
    tests_result = Result.objects.get(pk=pk)
    test=tests_result.test

    # Вызываем завершение теста.
    completion_of_test(request=request, test=test, tests_result=tests_result)

    # Переходим.
    return redirect('testing:test', pk=test.id)

# Функция переназначения теста.
@login_required
def retake_the_test(request, pk):
    # забираем результат теста.
    tests_result = Result.objects.get(pk=pk)
    if settings.DEBUG:
        logger.info(f'Результат теста: {tests_result}\n')
    # Если страницу открыл не тот, кому назначено, запрещаем доступ.
    if tests_result.employee != request.user:
        return HttpResponseForbidden('Этот тест назначен не Вам!')
    # Если уже использованы все попытки - запрещаем доступ.
    if tests_result.attempts_used >= tests_result.test.amount_of_try:
        return HttpResponseForbidden('Уже использованы все попытки!')
    # Если дата уже наступила.
    if tests_result.learning_path_result and tests_result.learning_path_result.planned_end_date <= datetime.now().date():
        return HttpResponseForbidden('Тест просрочен!')
    if settings.DEBUG:
        logger.info(f'Результат теста: {tests_result.get_status_display()}\n')
    # Удаляем результаты вопросов и ответов.
    questions_results = tests_result.questions_results.all()
    for questions_result in questions_results:
        answers_results = questions_result.answers_results.all()
        for answers_result in answers_results:
            if answers_result.selected_relevant_point:
                answers_result.selected_relevant_point = None
        answers_results.delete()
    questions_results.delete()
    # Обнуляем результаты теста и прибавляем использованных попыток.
    tests_result.status = 'appointed'
    tests_result.score = 0
    tests_result.score_scaled = 0
    tests_result.end_date = None
    tests_result.attempts_used += 1
    # сохраняем результат теста
    tests_result.save()
    # переходим
    return redirect('testing:take_assigned_test', pk = tests_result.id)



