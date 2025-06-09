from typing import Callable
from django.http import HttpRequest, HttpResponse
import time


class RequestTimingMiddleware:
    def __init__(self, get_response: Callable):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        start_time = time.time()
        response = self.get_response(request)
        duration = time.time() - start_time
        response['X-Request-Duration'] = str(duration)
        return response


class RequestTrackingMiddleware:
    def __init__(self, get_response: Callable):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        if request.user.is_authenticated:
            request.user.last_activity = time.time()
            request.user.save(update_fields=['last_activity'])
        return self.get_response(request)
