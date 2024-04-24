from django.http import HttpResponseRedirect, HttpResponse

try:
    from django.utils.deprecation import MiddlewareMixin  # Django 1.10.x
except ImportError:
    MiddlewareMixin = object  # Django 1.4.x - Django 1.9.x


class SimpleMiddleware(MiddlewareMixin):
    def process_request(self, request):
        path = request.path_info.lstrip('/')

        # print("process_request:path=%s"%path,request.session.keys(),request.session.get("user"))

        if request.session.has_key("user"):
            request.session["user"] = request.session["user"]
            if path.startswith("login"):
                return HttpResponseRedirect("/")
            else:
                return None
        else:
            if path.startswith("login") \
                    or path.startswith("alarm/postAdd") \
                    or path.startswith("stream/getIndex") \
                    or path.startswith("control/getIndex"):
                # 未登录状态下，需要放开的路由
                return None
            else:
                return HttpResponseRedirect("/login")

    def process_response(self, request, response):
        # print("process_response")
        return response


import time
from django.db import transaction
from django.contrib.sessions.backends.base import UpdateError
from django.contrib.sessions.middleware import SessionMiddleware


class CustomSessionMiddleware(SessionMiddleware):
    # 继承SessionMiddleware 遇到异常重试3次

    def process_response(self, request, response):
        try:
            return super().process_response(request, response)
        except Exception as e:

            max_retries = 3
            retries = 0
            success = False
            while retries < max_retries and not success:
                try:
                    with transaction.atomic():
                        request.session.save()
                    success = True
                except UpdateError:
                    # print('试图获得锁时发现死锁;尝试重新启动事务!')
                    retries += 1
                    time.sleep(1)

            if not success:
                pass
                # 处理超过最大重试次数的情况
                # if request.method == "POST":
                #     print(request.body, '================>')
                # else:
                #     print(request.GET, '================>')
                # print('OperationalError 异常已经重试最大次数')
        return response
