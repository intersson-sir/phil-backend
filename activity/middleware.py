"""
Middleware to set current request in thread-local for activity logging in signals.
"""
from django.utils.deprecation import MiddlewareMixin
from .context import set_current_request, clear_current_request


class ActivityRequestMiddleware(MiddlewareMixin):
    def process_request(self, request):
        set_current_request(request)

    def process_response(self, request, response):
        clear_current_request()
        return response

    def process_exception(self, request, exception):
        clear_current_request()
        return None
