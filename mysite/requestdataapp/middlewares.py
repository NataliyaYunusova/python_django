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
            self.request_time[user_ip] = datetime.now()

        else:
            if user_ip in self.request_time.keys():
                time_delta = (datetime.now() - self.request_time[user_ip]).seconds

                if time_delta < 5:
                    return render(request, 'requestdataapp/request-error.html')

            self.request_time[user_ip] = datetime.now()
            #  вместо ключа 'user_ip' надо использовать переменную user_ip, иначе получается что хранится адрес
            #  только последнего пользователя и если будет 1000 запросов в минуту от двух пользователей которые делают
            #  запросы почереди, то данный алгоритм не ограничит их. В словаре надо хранить время последнего посещения
            #  конкртеного пользователя

        response = self.get_response(request)
        return response
#
#  Попробуйте сделать так:
#  - храним данные по посещениях в словаре
#  - при запросе смотрим в словарь по ключу с ip, если его нет, создаём запись вида "ip: время доступа", и всё, а если
#  ключ есть, то получаем время прошлого доступа
#  - сравниваем текущее время и время последнего запроса, если разница меньше допустимого - возвращаем страницу
#  с ошибкой. Если разница допустима - обновляем время доступа для этого ip.
