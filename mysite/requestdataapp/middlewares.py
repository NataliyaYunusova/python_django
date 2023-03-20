from datetime import datetime

from django.http import HttpRequest
from django.shortcuts import render


def setup_useragent_on_request_middleware(get_response):
    print('initial call')

    def middleware(request: HttpRequest):
        print('before get response')
        request.user_agent = request.META['HTTP_USER_AGENT']
        response = get_response(request)
        print('after get response')

        return response

    return middleware


class CountRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.requests_count = 0
        self.responses_count = 0
        self.exceptions_count = 0

    def __call__(self, request: HttpRequest):
        self.requests_count += 1
        print('requests count', self.requests_count)
        response = self.get_response(request)
        self.responses_count += 1
        print('responses count', self.responses_count)
        return response

    def process_exception(self, request: HttpRequest, exception: Exception):
        self.exceptions_count += 1
        print('got', self.exceptions_count, 'exceptions so far')


class ThrottlingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.request_time = dict()

    def __call__(self, request: HttpRequest):
        user_ip = request.META.get('REMOTE_ADDR')
        if not self.request_time:
            print('Словарь запросов ещё пуст')

        else:
            if self.request_time['user_ip'] == user_ip and \
                    (datetime.now() - self.request_time['time']).seconds < 5:

                return render(request, 'requestdataapp/request-error.html')

        self.request_time = {'time': datetime.now(), 'user_ip': user_ip}

        response = self.get_response(request)
        return response
