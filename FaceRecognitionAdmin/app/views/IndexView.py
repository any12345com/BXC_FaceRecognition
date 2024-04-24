from app.views.ViewsBase import *
from app.models import *
from django.shortcuts import render
from app.utils.OSSystem import OSSystem


def index(request):
    context = {
        
    }
    return render(request, 'app/web_index.html', context)


def api_getIndex(request):
    # highcharts 例子 https://www.highcharts.com.cn/demo/highcharts/dynamic-update
    code = 0
    msg = "未知错误"
    osInfo = {}
    try:
        osSystem = OSSystem()
        osInfo = osSystem.getOSInfo()
        code = 1000
        msg = "success"
    except Exception as e:
        msg = str(e)

    res = {
        "code": code,
        "msg": msg,
        "osInfo": osInfo
    }
    return HttpResponseJson(res)
