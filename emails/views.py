from django.shortcuts import render

# Create your views here.

# Импорт настроек.
from django.conf import settings
# Импорт моделей вью.
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
# Импорт моделей ядра.
from .models import Email, EmailsResult
# Импорт модели фильтров.
from .filters import EmailFilter
# Импорт форм.
from .forms import EmailForm, EmailSendingForm
# Импорт рендера, перенаправления, генерации адреса и других урл функций.
from django.shortcuts import render, redirect, reverse, get_object_or_404
# Проверка прав доступа для классов.
from guardian.mixins import PermissionListMixin
from guardian.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin as GPermissionRequiredMixin
# Импорт забора.
from django.shortcuts import get_object_or_404
# Импорт ответов.
from django.http import HttpResponse
# Импорт отправки.
from django.core.mail import send_mail
from lms.settings import EMAIL_HOST_USER
# Для пароля.
from django.contrib.auth.hashers import make_password
from django.utils.crypto import get_random_string
# Событие в календарь.
import vobject
# Для отображения нужной таймзоны
from django.utils import timezone
tz = timezone.get_default_timezone()
# Импорт моделей.
from core.models import Employee
# Миксины.
from core.mixins import PreviousPageGetMixinL0, PreviousPageSetMixinL0, PreviousPageGetMixinL1, PreviousPageSetMixinL1, PreviousPageGetMixinL2, PreviousPageSetMixinL2
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

# Импортируем логи
import logging
# Создаем логгер с именем 'project'
logger = logging.getLogger('project')

# Список вопросов.
class EmailsView(LoginRequiredMixin, PreviousPageSetMixinL1, PermissionListMixin, ListView):
    # Права доступа
    permission_required = 'emails.view_email'
    # Модель.
    model = Email
    # Поле сортировки.
    ordering = 'created'
    # Шаблон.
    template_name = 'emails.html'
    # Количество объектов на странице
    paginate_by = 6

    # Переопределяем выборку вью.
    def get_queryset(self):
        # Забираем изначальную выборку вью.
        queryset = super().get_queryset()
        # Добавляем модель фильтрации в выборку вью.
        self.filterset = EmailFilter(self.request.GET, queryset, request=self.request)
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

# Вывод рассылки.
class EmailView(LoginRequiredMixin, PreviousPageGetMixinL1, PermissionRequiredMixin, ListView):
    # Права доступа
    permission_required = 'emails.view_email'
    accept_global_perms = True
    # Модель.
    model = EmailsResult
    # Поле сортировки.
    ordering = 'created'
    # Шаблон.
    template_name = 'email.html'
    # Количество объектов на странице
    paginate_by = 6

    # Определяем объект проверки.
    def get_permission_object(self):
        email = Email.objects.get(pk=self.kwargs.get('pk'))
        return email

    # Переопределяем выборку вью.
    def get_queryset(self):
        # Переопределяем изначальную выборку.
        queryset = super().get_queryset().filter(email__pk=self.kwargs.get('pk')).order_by('employee')
        self.qs_count = queryset.count
        # Возвращаем вью новую выборку.
        return queryset

    # Переопределеяем переменные вью.
    def get_context_data(self, **kwargs):
        # забираем изначальный набор переменных
        context = super().get_context_data(**kwargs)
        # Добавляем во вью.
        email = self.get_permission_object()
        context['object'] = email
        context['qs_count'] = self.qs_count
        # Возвращаем новый набор переменных в контролер.
        return context

# Создание рассылки.
class EmailCreateView(LoginRequiredMixin, GPermissionRequiredMixin, CreateView):
    # Права доступа.
    permission_required = 'emails.add_email'
    # Форма.
    form_class = EmailForm
    # Модель.
    model = Email
    # Шаблон.
    template_name = 'email_edit.html'

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
        return reverse('emails:email', kwargs={'pk': self.object.pk})

# Изменение файла.
class EmailUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    # Права доступа
    permission_required = 'courses.change_email'
    accept_global_perms = True
    # Форма.
    form_class = EmailForm
    # Модель.
    model = Email
    # Шаблон.
    template_name = 'email_edit.html'

    # Заполнение полей данными.
    def get_initial(self):
        # Забираем изначальный набор.
        initial = super().get_initial()
        # Добавляем создателя: юзера отправившего запрос.
        initial["creator"] = self.request.user
        initial["type"] = self.object.type
        initial["group"] = self.object.group
        initial["assignment"] = self.object.assignment
        initial["event"] = self.object.event
        # Возвращаем значения в форму.
        return initial

    # Перенаправление после валидации формы.
    def get_success_url(self):
        # Направляем по адресу объекта.
        return reverse('emails:email', kwargs={'pk': self.object.pk})

# Удаление рассылки.
class EmailDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    # Права доступа
    permission_required = 'emails.delete_email'
    accept_global_perms = True
    # Модель.
    model = Email
    # Шаблон.
    template_name = 'email_delete.html'

    # Перенаправление после валидации формы.
    def get_success_url(self):
        # Направляем по адресу объектов.
        return reverse('emails:emails')

# Функция рассылки сообщений.
def sending_start(email, sending_type):

    # Получаем переменные.
    group = email.group
    assignment = email.assignment
    event = email.event
    base_href = settings.BASE_URL

    # Получение пользователей.
    if email.type == 'password':
        employees = group.user_set.filter(email__isnull=False)
    elif email.type == 'assignment':
        if assignment.participants == 'group':
            employees = assignment.participants_group.user_set.filter(email__isnull=False)
        if assignment.participants == 'employee':
            employees = [assignment.employee]
    elif email.type == 'event':
        employees = event.participants_group.user_set.filter(email__isnull=False)

    # Если рассылка только для новых адресатов.
    if sending_type == 'new':

        # Если уже есть отправленные письма.
        if EmailsResult.objects.filter(email=email, status='sent').exists():
            # Создаем список старых получателей.
            old_employees_list = Employee.objects.filter(
                emails_employee__email=email, emails_employee__status='sent'
            ).distinct()
            # Получаем ключи.
            old_employees_pks = list(old_employees_list.values_list('pk', flat=True))

            # Фильтруем набор.
            employees = employees.exclude(pk__in=old_employees_pks)

    # Если получатели есть:
    if employees.exists():

        # Проходим по сотрудникам.
        for employee in employees:

            # Подготовка письма с паролем.
            if email.type == 'password':
                # Генерируем новый случайный пароль.
                new_password = get_random_string(length=8)
                employee.set_password(new_password)
                employee.save()

                # Письмо.
                subject = 'Пароль для входа'
                message = (
                    f'Добрый день, {employee.username}!\n\n'
                    f'Ваш пароль для входа: {new_password}\n\n'
                    f'Ссылка на портал: {base_href}\n\n'
                )

            # Подготовка письма с назначением.
            elif email.type == 'assignment':

                # Получаем ссылку для письма.
                sub_href = reverse('core:personal_area') + '#tab2'
                href = f'{base_href}{sub_href}'

                # Письмо.

                subject = 'Назначение обучения'

                if assignment.type == 'learning_complex':

                    learning_paths = [
                        learning_complex_path.learning_path for learning_complex_path in
                        assignment.learning_complex.learning_complex_paths.all().order_by(
                            'learning_complex', 'position')
                    ]

                    message = (
                        f'Добрый день, коллеги!\n\n'
                        f'Вам назначены траектории обучения:\n'
                    )
                    for learning_path in learning_paths:
                        message += f'- {learning_path}\n'
                    message += f'Просмотрите назначенное обучение: {href}\n\n'

                elif assignment.type == 'learning_path':
                    message = (
                        f'Добрый день, {employee.username}!\n\n'
                        f'Вам назначена траектория обучения: {assignment.learning_path}\n\n'
                        f'Просмотрите назначенное обучение: {href}\n\n'
                    )

                elif assignment.type == 'material':
                    message = (
                        f'Добрый день, {employee.username}!\n\n'
                        f'Вам назначен материал: {assignment.material}\n\n'
                        f'Просмотрите назначенное обучение: {href}\n\n'
                    )

                elif assignment.type == 'course':
                    message = (
                        f'Добрый день, {employee.username}!\n\n'
                        f'Вам назначен курс: {assignment.course}\n\n'
                        f'Просмотрите назначенное обучение: {href}\n\n'
                    )

                elif assignment.type == 'test':
                    message = (
                        f'Добрый день, {employee.username}!\n\n'
                        f'Вам назначен тест: {assignment.test}\n\n'
                        f'Просмотрите назначенное обучение: {href}\n\n'
                    )

            # Подготовка письма с мероприятием.
            elif email.type == 'event':

                # Проверка объекта.
                if email.event:
                    event = email.event
                    base_href = settings.BASE_URL
                    event_href = reverse('events:event', kwargs={'pk': event.pk})
                    href = f'{base_href}{event_href}'
                else:
                    return HttpResponse(f"Мероприятие не найдено.")

                # Письмо.

                subject = 'Приглашение на мероприятие'

                # Создаем HTML-сообщение с вложенным iCalendar-файлом
                icalendar = vobject.iCalendar()
                vevent = icalendar.add('vevent')
                vevent.add('summary').value = subject
                vevent.add('dtstart').value = event.planned_start_date.astimezone(tz)
                vevent.add('dtend').value = event.planned_start_date.astimezone(tz)
                vevent.add('description').value = event.desc
                icalendar_content = icalendar.serialize()

                message = (
                    f'Добрый день, {employee.username}!\n\n'
                    f'{event.planned_start_date.strftime("%d.%m.%Y %H:%M")} состоится мероприятие: {event}\n'
                    f'Ссылка: {href}\n'
                    f'<pre>{icalendar_content}</pre>'
                )

            # Отправка письма.
            try:
                send_mail(
                    subject,
                    message,
                    EMAIL_HOST_USER,
                    [employee.email],
                    fail_silently=False,
                    html_message=message
                )
                status = 'sent'
            except Exception as e:
                status = 'not_sent'
                logger.info(f'Ошибка отправки сообщения: {e}')

            # Сохраняем результат в базе данных.
            EmailsResult.objects.create(
                email=email,
                employee=employee,
                sending_type=sending_type,
                status=status
            )

# Отправка писем.
@login_required
@permission_required('emails.add_email')
def sending(request, pk):

    # Получаем объект.
    email = get_object_or_404(Email, id=pk)

    # Если форма отправлена.
    if request.method == 'POST':

        # Форма с данными.
        form = EmailSendingForm(request.POST)

        # Если данные валидны.
        if form.is_valid():

            # Выбранный тип рассылки.
            sending_type = form.cleaned_data['sending_type']

            # Выполнение рассылки.
            sending_start(email=email, sending_type=sending_type)

        # Переходим.
        return redirect('emails:email', pk=pk)

    # Если это форма для заполнения.
    else:

        # Пустая форма.
        form = EmailSendingForm()

    # Страница с формой.
    return render(request, 'email_sending_edit.html', {'form': form})
