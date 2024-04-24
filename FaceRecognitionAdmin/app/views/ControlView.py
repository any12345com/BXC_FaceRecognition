from app.views.ViewsBase import *
from app.models import *
from django.shortcuts import render, redirect
from app.utils.Utils import gen_random_code_s

def api_getControls(request):

    code = 0
    msg = "error"
    mediaServerState = False
    ananyServerState = False

    atDBControls = [] #数据库中存储的布控数据

    try:
        __online_streams_dict = {}  #在线的视频流
        __online_controls_dict = {} #在线的布控数据

        __streams = g_media.getMediaList()
        mediaServerState = g_media.mediaServerState
        for d in __streams:
            if d.get("is_online"):
                __online_streams_dict[d.get("code")] = d

        if mediaServerState:
            __state, __msg, __controls = g_analyzer.controls()
            ananyServerState = g_analyzer.analyzerServerState
            for d in __controls:
                __online_controls_dict[d.get("code")] = d


        sql = "select * from av_control order by av_control.id desc"
        atDBControls = g_djangoSql.select(sql) #数据库中存储的布控数据
        atDBControlCodeSet = set() # 数据库中所有布控code的set

        for atDBControl in atDBControls:
            atDBControlCodeSet.add(atDBControl.get("code"))

            atDBControl_stream_code = "%s_%s"%(atDBControl["stream_app"],atDBControl["stream_name"])
            atDBControl["create_time"] = atDBControl["create_time"].strftime("%Y-%m-%d %H:%M")
            if __online_streams_dict.get(atDBControl_stream_code):
                atDBControl["stream_active"] = True # 当前视频流在线
            else:
                atDBControl["stream_active"] = False # 当前视频流不在线

            __online_control = __online_controls_dict.get(atDBControl["code"])
            atDBControl["checkFps"] = "0"

            if __online_control:
                atDBControl["cur_state"] = 1 # 布控中
                atDBControl["checkFps"] = "%.2f"%float(__online_control.get("checkFps"))
            else:
                if 0 == int(atDBControl.get("state")):
                    atDBControl["cur_state"] = 0 # 未布控
                else:
                    atDBControl["cur_state"] = 5 # 布控中断

            if atDBControl.get("state") != atDBControl.get("cur_state"):
                # 数据表中的布控状态和最新布控状态不一致，需要更新至最新状态
                update_state_sql = "update av_control set state=%d where id=%d " % (atDBControl.get("cur_state"), atDBControl.get("id"))
                g_djangoSql.execute(update_state_sql)

        for code,control in __online_controls_dict.items():
            if code not in atDBControlCodeSet:
                # 布控数据在运行中，但却不存在本地数据表中，该数据为失控数据，需要关闭其运行状态
                print("api_getControls() 当前布控数据还在运行在，但却不存在本地数据表中，已启动停止布控",code,control)
                g_analyzer.control_cancel(code=code)

        code = 1000
        msg = "success"
    except Exception as e:
        msg = str(e)

    if mediaServerState and ananyServerState:
        serverState = "<span style='color:green;font-size:14px;'>流媒体运行中，视频分析器运行中</span>"
    elif mediaServerState and not ananyServerState:
        serverState = "<span style='color:green;font-size:14px;'>流媒体运行中</span> <span style='color:red;font-size:14px;'>视频分析器未运行<span>"
    else:
        serverState = "<span style='color:red;font-size:14px;'>流媒体未运行，视频分析器未运行<span>"

    res = {
        "code":code,
        "msg":msg,
        "ananyServerState":ananyServerState,
        "mediaServerState":mediaServerState,
        "serverState":serverState,
        "data":atDBControls
    }
    return HttpResponseJson(res)

def web_controls(request):
    context = {
    }

    return render(request, 'app/web_controls.html', context)

def web_add_control(request):
    context = {
    }

    context["streams"] = g_media.getMediaList()
    context["handle"] = "add"

    context["control"] = {
        "code": gen_random_code_s("Control"),
        "push_stream": True
    }

    return render(request, 'app/web_add_control.html', context)

def web_edit_control(request):
    context = {
    }
    params = parse_get_params(request)

    code = params.get("code")
    try:
        control = Control.objects.get(code=code)
        # context["streams"] = media.getStreams()
        context["handle"] = "edit"
        context["control"] = control
        context["control_stream_flvUrl"] = g_media.get_httpFlvUrl(control.stream_app, control.stream_name)

    except Exception as e:
        print("web_control_edit error",e)

        return render(request, 'app/message.html', {"msg": "请通过布控管理进入", "is_success": False, "redirect_url": "/controls"})

    return render(request, 'app/web_add_control.html', context)
def api_postAddAnalyzer(request):
    code = 0
    msg = "error"

    if request.method == 'POST':
        params = parse_post_params(request)

        controlCode = params.get("controlCode")

        if controlCode:

            try:
                control = Control.objects.get(code=controlCode)
            except:
                control = None

            if control:
                __state, __msg = g_analyzer.control_add(
                    code=control.code,
                    pullApp=control.stream_app,
                    pullName=control.stream_name,
                    isPushStream=control.push_stream,
                    pushApp=control.push_stream_app,
                    pushName=control.push_stream_name
                )
                msg = __msg
                if __state:
                    control = Control.objects.get(code=controlCode)
                    control.state = 1
                    control.save()
                    code = 1000
            else:
                msg = "布控数据不能存在，请先添加布控！"

        else:
            msg = "请求参数不合法"
    else:
        msg = "请求方法不支持"
    res = {
        "code":code,
        "msg":msg
    }
    return HttpResponseJson(res)
def api_postCancelAnalyzer(request):
    code = 0
    msg = "error"

    if request.method == 'POST':
        params = parse_post_params(request)

        controlCode = params.get("controlCode")
        if controlCode:
            control = None
            try:
                control = Control.objects.get(code=controlCode)
            except:
                pass

            if control:
                __state, __msg = g_analyzer.control_cancel(
                    code=controlCode
                )

                if __state:
                    control = Control.objects.get(code=controlCode)
                    control.state = 0
                    control.save()
                    msg = "取消布控成功"
                    code = 1000
                else:
                    msg = "取消布控失败："+str(__msg)
            else:
                msg = "布控数据不能存在！"

        else:
            msg = "请求参数不合法"
    else:
        msg = "请求方法不支持"

    res = {
        "code":code,
        "msg":msg
    }
    return HttpResponseJson(res)


def api_postAddControl(request):
    code = 0
    msg = "error"

    if request.method == 'POST':
        params = parse_post_params(request)
        try:
            print(params)

            controlCode = params.get("controlCode")
            pushStream = True if '1' == params.get("pushStream") else False
            remark = params.get("remark")

            streamApp = params.get("streamApp")
            streamName = params.get("streamName")
            streamVideo = params.get("streamVideo")
            streamAudio = params.get("streamAudio")

            if controlCode and streamApp and streamName and streamVideo:

                __save_state = False
                __save_msg = "error"


                control = None
                try:
                    control = Control.objects.get(code=controlCode)
                except:
                    pass

                if control:
                    # 编辑更新
                    control.stream_app = streamApp
                    control.stream_name = streamName
                    control.stream_video = streamVideo
                    control.stream_audio = streamAudio
                    control.remark = remark
                    control.push_stream = pushStream
                    control.last_update_time = datetime.now()
                    control.save()

                    if control.id:
                        __save_state = True
                        __save_msg = "更新布控数据成功(a)"
                    else:
                        __save_msg = "更新布控数据失败(a)"

                else:
                    # 新增
                    control = Control()
                    control.user_id = getUser(request).get("id")
                    control.sort = 0
                    control.code = controlCode

                    control.stream_app = streamApp
                    control.stream_name = streamName
                    control.stream_video = streamVideo
                    control.stream_audio = streamAudio
                    control.remark = remark
                    control.push_stream = pushStream
                    control.push_stream_app = g_media.default_push_stream_app
                    control.push_stream_name = controlCode

                    control.create_time = datetime.now()
                    control.last_update_time = datetime.now()

                    control.save()

                    if control.id:
                        __save_state = True
                        __save_msg = "添加布控数据成功"
                    else:
                        __save_msg = "添加布控数据失败"

                if __save_state:
                    code = 1000
                msg = __save_msg
            else:
                msg = "布控请求参数不完整！"
        except Exception as e:
            msg = "布控请求参数存在错误: %s"%str(e)
            print(msg)

    else:
        msg = "请求方法不合法！"


    res = {
        "code":code,
        "msg":msg
    }
    return HttpResponseJson(res)
def api_postEditControl(request):
    code = 0
    msg = "error"

    if request.method == 'POST':
        params = parse_post_params(request)
        try:
            controlCode = params.get("controlCode")
            pushStream = True if '1' == params.get("pushStream") else False
            remark = params.get("remark")

            if controlCode:
                try:
                    control = Control.objects.get(code=controlCode)
                    control.remark = remark
                    control.push_stream = pushStream

                    control.last_update_time = datetime.now()
                    control.save()

                    if control.id:
                        code = 1000
                        msg = "更新布控数据成功"
                    else:
                        msg = "更新布控数据失败"

                except Exception as e:
                    msg = "更新布控数据失败：" + str(e)
            else:
                msg = "更新布控请求参数不完整！"
        except Exception as e:
            msg = "布控请求参数存在错误: %s"%str(e)
    else:
        msg = "请求方法不合法！"


    res = {
        "code":code,
        "msg":msg
    }
    return HttpResponseJson(res)
def api_postDelControl(request):
    code = 0
    msg = "error"

    if request.method == 'POST':
        params = parse_post_params(request)
        try:
            controlCode = params.get("controlCode")

            if controlCode:
                try:
                    control = Control.objects.get(code=controlCode)
                    g_analyzer.control_cancel(code=controlCode) # 取消布控

                    if control.delete():
                        code = 1000
                        msg = "删除布控数据成功"
                    else:
                        msg = "删除布控数据失败"

                except Exception as e:
                    msg = "更新布控数据失败：" + str(e)
            else:
                msg = "删除布控请求参数不完整！"
        except Exception as e:
            msg = "删除布控请求参数存在错误: %s"%str(e)
    else:
        msg = "请求方法不合法！"


    res = {
        "code":code,
        "msg":msg
    }
    return HttpResponseJson(res)
