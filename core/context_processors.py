

# Добавляем глобальный контекст.
from django.db.models import OuterRef, Subquery


def context_processor(request):

    # Подзапрос активных задач.

    if not request.user.is_authenticated:
        return {}

    latest_paths_results = request.user.results.filter(
        learning_path=OuterRef('learning_path'),
        type='learning_path',
        employee=request.user
    ).order_by('-id').values('id')[:1]

    latest_materials_results = request.user.results.filter(
        material=OuterRef('material'),
        type='material',
        employee=request.user
    ).order_by('-id').values('id')[:1]

    latest_tests_results = request.user.results.filter(
        test=OuterRef('test'),
        type='test',
        employee=request.user
    ).order_by('-id').values('id')[:1]

    latest_courses_results = request.user.results.filter(
        course=OuterRef('course'),
        type='course',
        employee=request.user
    ).order_by('-id').values('id')[:1]

    latest_events_results = request.user.results.filter(
        event=OuterRef('event'),
        type='event',
        employee=request.user
    ).order_by('-id').values('id')[:1]

    # Основной запрос активных задач.

    employees_paths_results = request.user.results.filter(
        id__in=Subquery(latest_paths_results)
    ).prefetch_related('learning_path')

    employees_materials_results = request.user.results.filter(
        id__in=Subquery(latest_materials_results)
    ).prefetch_related('material')

    employees_tests_results = request.user.results.filter(
        id__in=Subquery(latest_tests_results)
    ).prefetch_related('test')

    employees_courses_results = request.user.results.filter(
        id__in=Subquery(latest_courses_results)
    ).prefetch_related('course')

    employees_events_results = request.user.results.filter(
        id__in=Subquery(latest_events_results)
    ).prefetch_related('event')

    # Забираем.

    appointed_paths_count = employees_paths_results.filter(
        status='appointed',
    ).count()
    paths_in_progress_count = employees_paths_results.filter(
        status='in_progress',
    ).count()
    active_paths_count = appointed_paths_count + paths_in_progress_count

    appointed_materials_count = employees_materials_results.filter(
        status='appointed',
    ).count()
    materials_in_progress_count = employees_materials_results.filter(
        status='in_progress',
    ).count()
    active_materials_count = appointed_materials_count + materials_in_progress_count

    appointed_tests_count = employees_tests_results.filter(
        status='appointed',
    ).count()
    tests_in_progress_count = employees_tests_results.filter(
        status='in_progress',
    ).count()
    active_tests_count = appointed_tests_count + tests_in_progress_count

    appointed_courses_count = employees_courses_results.filter(
        status='appointed',
    ).count()
    courses_in_progress_count = employees_courses_results.filter(
        status='in_progress',
    ).count()
    active_courses_count = appointed_courses_count + courses_in_progress_count

    appointed_events_count = employees_events_results.filter(
        status='appointed',
    ).count()
    events_in_progress_count = employees_events_results.filter(
        status='in_progress',
    ).count()
    active_events_count = appointed_events_count + events_in_progress_count

    # Здесь можно выполнять любые необходимые вычисления.
    return {
        'active_paths_count': active_paths_count,
        'active_materials_count': active_materials_count,
        'active_tests_count': active_tests_count,
        'active_courses_count': active_courses_count,
        'active_events_count': active_events_count,
        # Другие переменные.
    }