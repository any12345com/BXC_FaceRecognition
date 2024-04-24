import os
from app.views.ViewsBase import *
from django.shortcuts import render


def index(request):
    context = {
        
    }
    data = [
        {
            "name": "获取所有摄像头数据",
            "request_method": "GET",
            "url": "{host}/stream/getIndex".format(host=g_config.adminHost),
        },
        {
            "name": "获取所有布控数据",
            "request_method": "GET",
            "url": "{host}/control/getIndex".format(host=g_config.adminHost),
        }
    ]
    context["data"] = data
    return render(request, 'app/web_open_index.html', context)
