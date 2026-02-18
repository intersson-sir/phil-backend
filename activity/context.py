"""
Thread-local storage for current request (used by signals to get user and IP).
"""
import threading

_request = threading.local()


def get_current_request():
    return getattr(_request, "request", None)


def set_current_request(request):
    _request.request = request


def clear_current_request():
    if hasattr(_request, "request"):
        del _request.request
