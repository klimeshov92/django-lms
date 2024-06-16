from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

# Страницы.
class PreviousPageSetMixinL0:
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        # Сохраняем полный URL предыдущей страницы в сессии при каждом запросе.
        previous_page = request.get_full_path()
        request.session['previous_page_l0'] = previous_page
        print("Previous page l0 set to:", previous_page)
        return super().dispatch(request, *args, **kwargs)
class PreviousPageGetMixinL0:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        previous_page = self.request.session.get('previous_page_l0', '/')
        print("Previous page l0 retrieved from session:", previous_page)
        context['previous_page_l0'] = previous_page
        return context
class PreviousPageSetMixinL1:
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        # Сохраняем полный URL предыдущей страницы в сессии при каждом запросе.
        previous_page = request.get_full_path()
        request.session['previous_page_l1'] = previous_page
        print("Previous page l1 set to:", previous_page)
        return super().dispatch(request, *args, **kwargs)
class PreviousPageGetMixinL1:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        previous_page = self.request.session.get('previous_page_l1', '/')
        print("Previous page l1 retrieved from session:", previous_page)
        context['previous_page_l1'] = previous_page
        return context
class PreviousPageSetMixinL2:
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        # Сохраняем полный URL предыдущей страницы в сессии при каждом запросе.
        previous_page = request.get_full_path()
        request.session['previous_page_l2'] = previous_page
        print("Previous page l2 set to:", previous_page)
        return super().dispatch(request, *args, **kwargs)
class PreviousPageGetMixinL2:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        previous_page = self.request.session.get('previous_page_l2', '/')
        print("Previous page l2 retrieved from session:", previous_page)
        context['previous_page_l2'] = previous_page
        return context
class PreviousPageSetMixinL3:
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        # Сохраняем полный URL предыдущей страницы в сессии при каждом запросе.
        previous_page = request.get_full_path()
        request.session['previous_page_l3'] = previous_page
        print("Previous page l3 set to:", previous_page)
        return super().dispatch(request, *args, **kwargs)
class PreviousPageGetMixinL3:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        previous_page = self.request.session.get('previous_page_l3', '/')
        print("Previous page l3 retrieved from session:", previous_page)
        context['previous_page_l3'] = previous_page
        return context
class PreviousPageSetMixinL4:
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        # Сохраняем полный URL предыдущей страницы в сессии при каждом запросе.
        previous_page = request.get_full_path()
        request.session['previous_page_l4'] = previous_page
        print("Previous page l4 set to:", previous_page)
        return super().dispatch(request, *args, **kwargs)
class PreviousPageGetMixinL4:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        previous_page = self.request.session.get('previous_page_l4', '/')
        print("Previous page l4 retrieved from session:", previous_page)
        context['previous_page_l4'] = previous_page
        return context
class PreviousPageSetMixinL5:
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        # Сохраняем полный URL предыдущей страницы в сессии при каждом запросе.
        previous_page = request.get_full_path()
        request.session['previous_page_l5'] = previous_page
        print("Previous page l5 set to:", previous_page)
        return super().dispatch(request, *args, **kwargs)
class PreviousPageGetMixinL5:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        previous_page = self.request.session.get('previous_page_l5', '/')
        print("Previous page l5 retrieved from session:", previous_page)
        context['previous_page_l5'] = previous_page
        return context

