# Импорт пути.
from django.urls import path
# Импорт представления.
from .views import TestsView, TestView, TestCreateView, TestUpdateView, TestDeleteView,\
   QuestionsView, QuestionView, QuestionCreateView, QuestionUpdateView, QuestionDeleteView, \
   AnswerCreateView, AnswerUpdateView, AnswerDeleteView, \
   RelevantPointCreateView, RelevantPointUpdateView, \
   TestsQuestionsGeneratorCreateView, TestsQuestionsGeneratorUpdateView, \
   take_assigned_test, answer_to_question, attempt_end_timeout, retake_the_test, \
   tests_questions_ordering, answers_ordering
# Имя приложения в адресах.
app_name = 'testing'
# Список маршрутов приложения.
urlpatterns = [
   # Маршрут вывода тестов.
   path('', TestsView.as_view(), name='tests'),
   # Маршрут вывода теста.
   path('<int:pk>/', TestView.as_view(), name='test'),
   # Маршрут сортировки вопросов теста.
   path('<int:pk>/tests_questions_ordering/', tests_questions_ordering, name='tests_questions_ordering'),
   # Маршрут создания теста.
   path('create/', TestCreateView.as_view(), name='test_create'),
   # Маршрут обновления теста.
   path('<int:pk>/update/', TestUpdateView.as_view(), name='test_update'),
   # Маршрут удаления теста.
   path('<int:pk>/delete/', TestDeleteView.as_view(), name='test_delete'),
   # Маршрут вывода вопросов.
   path('questions/', QuestionsView.as_view(), name='questions'),
   # Маршрут вывода вопроса.
   path('questions/<int:pk>/', QuestionView.as_view(), name='question'),
   # Маршрут создания вопроса.
   path('questions/create/', QuestionCreateView.as_view(), name='question_create'),
   # Маршрут обновления вопроса.
   path('questions/<int:pk>/update/', QuestionUpdateView.as_view(), name='question_update'),
   # Маршрут удаления вопроса.
   path('questions/<int:pk>/delete/', QuestionDeleteView.as_view(), name='question_delete'),
   # Маршрут создания вопросов теста.
   path('<int:pk>/tests_questions_generator/create/', TestsQuestionsGeneratorCreateView.as_view(), name='tests_questions_generator_create'),
   # Маршрут обновления вопрсоов теста.
   path('tests_questions_generator/<int:pk>/update/', TestsQuestionsGeneratorUpdateView.as_view(), name='tests_questions_generator_update'),
   # Маршрут создания вопроса.
   path('questions/<int:pk>/answer/create/', AnswerCreateView.as_view(), name='answer_create'),
   # Маршрут сортировки ответов на вопрос.
   path('questions/<int:pk>/answers_ordering/', answers_ordering, name='answers_ordering'),
   # Маршрут обновления вопроса.
   path('answer/<int:pk>/update/', AnswerUpdateView.as_view(), name='answer_update'),
   # Маршрут удаления вопроса.
   path('answer/<int:pk>/delete/', AnswerDeleteView.as_view(), name='answer_delete'),
   # Маршрут создания соотвествующего пункта.
   path('answer/<int:pk>/relevant_point/create/', RelevantPointCreateView.as_view(), name='relevant_point_create'),
   # Маршрут обновления соотвествующего пункта.
   path('relevant_point/<int:pk>/update/', RelevantPointUpdateView.as_view(), name='relevant_point_update'),
   # маршрут прохождения теста
   path('take_assigned_test/<int:pk>/', take_assigned_test, name='take_assigned_test'),
   # маршрут ответа на вопрос теста
   path('answer_to_question/<int:pk>/', answer_to_question, name='answer_to_question'),
   # маршрут перезапуска теста
   path('retake_the_test/<int:pk>/', retake_the_test, name='retake_the_test'),
   # маршрут окончаниея времени
   path('attempt_end_timeout/<int:pk>/', attempt_end_timeout, name='attempt_end_timeout'),
]