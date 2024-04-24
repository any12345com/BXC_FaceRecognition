from app.views.ViewsBase import *
from app.models import *
from django.shortcuts import render, redirect
from app.utils.Utils import buildPageLabels, gen_random_code_s
import xlrd
import shutil


def online(request):
    context = {
        
    }
    # data = Camera.objects.all().order_by("-sort")
    return render(request, 'app/web_stream_online.html', context)


def index(request):
    context = {
        
    }
    data = []

    params = parse_get_params(request)

    page = params.get('p', 1)
    page_size = params.get('ps', 10)
    try:
        page = int(page)
    except:
        page = 1

    try:
        page_size = int(page_size)
        if page_size > 20 or page_size < 10:
            page_size = 10
    except:
        page_size = 10

    skip = (page - 1) * page_size
    sql_data = "select * from av_stream order by id desc limit %d,%d " % (
        skip, page_size)
    sql_data_num = "select count(id) as count from av_stream "

    count = g_djangoSql.select(sql_data_num)

    if len(count) > 0:
        count = int(count[0]["count"])
        data = g_djangoSql.select(sql_data)
    else:
        count = 0

    page_num = int(count / page_size)  # 总页数
    if count % page_size > 0:
        page_num += 1
    pageLabels = buildPageLabels(page=page, page_num=page_num)
    pageData = {
        "page": page,
        "page_size": page_size,
        "page_num": page_num,
        "count": count,
        "pageLabels": pageLabels
    }

    context["data"] = data
    context["pageData"] = pageData
    return render(request, 'app/web_stream_index.html', context)


def api_getIndex(request):
    code = 0
    msg = "未知错误"

    sql_data = "select * from av_stream order by id desc"
    data = g_djangoSql.select(sql_data)

    code = 1000
    msg = "success"
    res = {
        "code": code,
        "msg": msg,
        "data": data
    }
    return HttpResponseJson(res)


def add(request):
    if "POST" == request.method:
        __ret = False
        __msg = "未知错误"

        params = parse_post_params(request)
        handle = params.get("handle")
        code = params.get("code")
        pull_stream_url = params.get("pull_stream_url", "").strip()
        nickname = params.get("nickname").strip()
        remark = params.get("remark", "").strip()

        if "add" == handle and code and pull_stream_url.lower().startswith("rtsp") and nickname:
            try:
                user_id = getUser(request).get("id")
            except:
                user_id = 0

            obj = Stream()
            obj.user_id = user_id
            obj.sort = 0
            obj.code = params.get("code").strip()
            obj.app = params.get("app").strip()
            obj.name = params.get("name").strip()
            obj.pull_stream_url = pull_stream_url
            obj.pull_stream_type = 0
            obj.nickname = nickname
            obj.remark = remark
            obj.forward_state = 0  # 默认未开启转发
            obj.create_time = datetime.now()
            obj.last_update_time = datetime.now()
            obj.state = 0
            obj.save()
            __msg = "添加成功"
            __ret = True

        else:
            __msg = "请求参数格式错误"
        if __ret:
            redirect_url = "/stream/index"
        else:
            redirect_url = "/stream/add"
        return render(request, 'app/message.html',
                      {"msg": __msg, "is_success": __ret, "redirect_url": redirect_url})
    else:
        context = {
            
        }

        code = gen_random_code_s(prefix="cam")
        app = "live"
        name = code
        context["handle"] = "add"
        context["obj"] = {
            "code": code,
            "app": app,
            "name": name,
            "rtspUrl": g_media.get_rtspUrl(app, name),
            "hlsUrl": g_media.get_hlsUrl(app, name),
            "httpMp4Url": g_media.get_httpMp4Url(app, name),
            "wsMp4Url": g_media.get_wsMp4Url(app, name),

        }
        context["data"] = g_djangoSql.select("select * from av_stream order by id desc")

        return render(request, 'app/web_stream_add.html', context)


def edit(request):
    if "POST" == request.method:
        __ret = False
        __msg = "未知错误"

        params = parse_post_params(request)
        handle = params.get("handle")
        code = params.get("code")
        pull_stream_url = params.get("pull_stream_url", "").strip()
        nickname = params.get("nickname", None)
        remark = params.get("remark", "").strip()

        if "edit" == handle and code and pull_stream_url.lower().startswith("rtsp") and nickname:
            obj = Stream.objects.get(code=code)
            if obj.pull_stream_url != pull_stream_url:
                # 如果 拉流地址更换了，需要停止转发代理
                g_media.delStreamProxy(app=obj.app, name=obj.name)
                obj.forward_state = 0
            obj.pull_stream_url = pull_stream_url
            obj.nickname = nickname.strip()
            obj.remark = remark
            obj.last_update_time = datetime.now()
            obj.save()
            # 编辑完成后，需要取消转发代理，避免视频源被更换

            __msg = "编辑成功"
            __ret = True

        else:
            __msg = "请求参数格式错误"
        if __ret:
            redirect_url = "/stream/index"
        else:
            redirect_url = "/stream/edit?code=" + code

        return render(request, 'app/message.html',
                      {"msg": __msg, "is_success": __ret, "redirect_url": redirect_url})
    else:
        context = {
            
        }
        params = parse_get_params(request)
        code = params.get("code")

        __is_edit_page = False
        if code:
            data = g_djangoSql.select("select * from av_stream order by id desc")
            obj = None
            for d in data:
                if code == d["code"]:
                    obj = d
                    break
            if obj:
                obj["rtspUrl"] = g_media.get_rtspUrl(obj["app"], obj["name"])
                obj["hlsUrl"] = g_media.get_hlsUrl(obj["app"], obj["name"])
                obj["wsMp4Url"] = g_media.get_wsMp4Url(obj["app"], obj["name"])
                obj["httpMp4Url"] = g_media.get_httpMp4Url(obj["app"], obj["name"])

                context["handle"] = "edit"
                context["obj"] = obj
                context["data"] = data
                __is_edit_page = True

        if __is_edit_page:
            return render(request, 'app/web_stream_add.html', context)
        else:
            return redirect("/stream/index")
            # return render(request, 'app/message.html',{"msg": "请通过摄像头管理进入", "is_success": False, "redirect_url": "/stream/index"})

def player(request):
    context = {
    }
    params = parse_get_params(request)
    app = params.get("app",None)
    name = params.get("name",None)

    if app and name:
        context["url"] = g_media.get_httpFlvUrl(app, name)
        context["hasAddress"] = True
    else:
        context["hasAddress"] = False

    return render(request, 'app/web_player.html', context)

    """
    context = {
        
    }
    params = parse_get_params(request)
    app = params.get("app", None)
    name = params.get("name", None)

    if app and name:
        stream = GetStream(app=app, name=name)
        context["stream"] = stream
        context["is_exist_params"] = 1
    else:
        context["is_exist_params"] = 0

    return render(request, 'app/web_stream_player.html', context)

    """

def api_getOnline(request):
    # 获取在线流
    code = 0
    msg = "未知错误"
    mediaServerState = False
    data = []

    try:
        mediaServerState, data = __getAllOnlineStream(is_filter_analyzer=True)

        code = 1000
        msg = "success"
    except Exception as e:
        log = "流媒体服务异常：" + str(e)
        msg = log

    top_msg = ""
    if not mediaServerState:
        top_msg = "流媒体服务未运行"

    res = {
        "code": code,
        "msg": msg,
        "top_msg": top_msg,
        "data": data
    }
    return HttpResponseJson(res)


def __postImportFile(file):
    __ret = False
    __msg = "未知错误"
    __data = []

    try:
        file_name = file.name  # 上传文件的名称
        file_size = file.size  # 上传文件的字节大小 1M = 1024*1024, 100M = 100*1024*1024 = 104857600
        file_size_m = int(file_size / 1024 / 1024)
        file_content_type = file.content_type  # 上传文件的 content_type

        if file_size_m <= 10:
            # print("file_content_type=",file_content_type)
            if 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' == file_content_type and file_name.endswith(
                    ".xlsx"):

                file_name_dir = datetime.now().strftime("%Y%m%d%H%M%S") + "_" + file_name
                FILE_ABSOLUTE_DIR = os.path.join(g_config.uploadTempDir, file_name_dir)

                if not os.path.exists(FILE_ABSOLUTE_DIR):
                    os.makedirs(FILE_ABSOLUTE_DIR)

                file_absolute_path = os.path.join(FILE_ABSOLUTE_DIR, file_name)  # 上传的压缩包的文件绝对存储路径
                # 将上传文件写入到本地
                f = open(file_absolute_path, 'wb')
                f.write(file.read())
                f.close()

                # 读取excel start
                wb = xlrd.open_workbook(file_absolute_path)
                sheet = wb.sheet_by_index(0)

                if sheet.ncols == 3:
                    for row in range(sheet.nrows):
                        if row > 0:
                            value = sheet.row_values(row)  # 类型是list， 一行数据
                            pull_stream_url = value[1]
                            d = {
                                'nickname': value[0],
                                'pull_stream_url': pull_stream_url,
                                'remark': value[2]
                            }
                            __data.append(d)

                # 读取excel end

                try:
                    if os.path.exists(FILE_ABSOLUTE_DIR):
                        shutil.rmtree(FILE_ABSOLUTE_DIR)  # 删除文件夹及其内部所有子文件
                except Exception as e:
                    print("StreamView.__postImportFile() err: " + str(e))

                __ret = True
                __msg = "success"

            else:
                __msg = "文件格式必须是xlsx"
        else:
            __msg = "文件不能超过10M:" + str(file_size_m)
    except Exception as e:
        __msg = "上传文件失败:" + str(e)

    return __ret, __msg, __data
def __getAllOnlineStream(is_filter_analyzer=False):
    data = []
    online_data = g_media.getMediaList()
    mediaServerState = g_media.mediaServerState
    if mediaServerState:

        db_streams = readAllStreamData()
        db_stream_dict = {}  # 数据库
        for db_stream in db_streams:
            app_name = "{app}_{name}".format(app=db_stream["app"], name=db_stream["name"])
            db_stream_dict[app_name] = db_stream

        for online_stream in online_data:
            app = online_stream["app"]
            name = online_stream["name"]

            if app == "live":
                app_name = "{app}_{name}".format(app=app, name=name)
                db_stream = db_stream_dict.get(app_name, None)  # 数据库查到的数据
                if db_stream:
                    online_stream["source_type"] = 1  # 来自数据库
                    online_stream["source"] = db_stream
                    online_stream["source_nickname"] = db_stream["nickname"]
                else:
                    online_stream["source_type"] = 0  # 来自推流
                    online_stream["source_nickname"] = "{app}/{name}".format(app=app, name=name)
                data.append(online_stream)
            else:
                # print(is_filter_analyzer,app,g_media.default_push_stream_app)

                if is_filter_analyzer and app == g_media.default_push_stream_app:
                    # 筛选算法流的同时，app也必须是算法流分类
                    app_name = "{app}_{name}".format(app=app, name=name)
                    db_stream = db_stream_dict.get(app_name, None)  # 数据库查到的数据
                    if db_stream:
                        online_stream["source_type"] = 1  # 来自数据库
                        online_stream["source"] = db_stream
                        online_stream["source_nickname"] = db_stream["nickname"]
                    else:
                        online_stream["source_type"] = 0  # 来自推流
                        online_stream["source_nickname"] = "{app}/{name}".format(app=app, name=name)
                    data.append(online_stream)

    return mediaServerState, data



def api_postImportFile(request):
    code = 0
    msg = "未知错误"
    if request.method == 'POST':
        params = parse_post_params(request)
        file = request.FILES.get("file")

        importRemark = params.get("importRemark")

        __upload_ret, __upload_msg, __upload_data = __postImportFile(file)
        if __upload_ret:
            try:
                user_id = getUser(request).get("id")
            except:
                user_id = 0

            importSuccessCount = 0
            for d in __upload_data:
                nickname = d["nickname"]
                pull_stream_url = d["pull_stream_url"]
                remark = ",".join([d["remark"], importRemark])

                stream_code = gen_random_code_s(prefix="S")

                obj = Stream()
                obj.user_id = user_id
                obj.sort = 0
                obj.code = stream_code
                obj.app = "live"
                obj.name = stream_code
                obj.pull_stream_url = pull_stream_url
                obj.pull_stream_type = 0
                obj.nickname = nickname
                obj.remark = remark
                obj.forward_state = 0  # 默认未开启转发
                obj.create_time = datetime.now()
                obj.last_update_time = datetime.now()
                obj.state = 0
                obj.save()
                importSuccessCount += 1

            if importSuccessCount > 0:
                pass

                msg = "success"
                code = 1000
            else:
                msg = "导入数据失败!"
        else:
            msg = __upload_msg
    else:
        msg = "请求方法不支持"
    res = {
        "code": code,
        "msg": msg
    }
    return HttpResponseJson(res)


def api_getAllStartForward(request):
    code = 0
    msg = "未知错误"
    if request.method == 'GET':
        __ret, __msg = AllStreamStartForward()
        msg = __msg
        if __ret:
            code = 1000
    else:
        msg = "请求方法不支持"

    res = {
        "code": code,
        "msg": msg
    }
    return HttpResponseJson(res)


def api_getAllUpdateForwardState(request):
    code = 0
    msg = "未知错误"
    # 全部更新转发状态
    try:
        online_data = g_media.getMediaList()
        online_dict = {}
        mediaServerState = g_media.mediaServerState
        if not mediaServerState:
            # 流媒体服务不在线，全部更新下线状态
            g_djangoSql.execute("update av_stream set forward_state=0")
        else:
            for d in online_data:
                app_name = "{app}_{name}".format(app=d["app"], name=d["name"])
                online_dict[app_name] = d

            stream_data = g_djangoSql.select("select * from av_stream order by id desc")
            stream_data_set = set()
            for stream_d in stream_data:
                app_name = "{app}_{name}".format(app=stream_d["app"], name=stream_d["name"])
                stream_data_set.add(app_name)
                if online_dict.get(app_name):
                    g_djangoSql.execute("update av_stream set forward_state=1 where id=%d" % int(stream_d["id"]))
                else:
                    g_djangoSql.execute("update av_stream set forward_state=0 where id=%d" % int(stream_d["id"]))

            online_not_in_db_data = set(online_dict.keys()).difference(stream_data_set)
            # online_not_in_db_data = list(online_not_in_db_data)  # 在线但不来自于数据库的视频流

        code = 1000
        msg = "刷新状态成功"
    except Exception as e:
        msg = "刷新状态失败：" + str(e)

    res = {
        "code": code,
        "msg": msg
    }
    return HttpResponseJson(res)


def api_postDel(request):
    code = 0
    msg = "未知错误"
    if request.method == 'POST':
        params = parse_post_params(request)
        stream_code = params.get("code")
        try:
            obj = Stream.objects.filter(code=stream_code)
            if len(obj) > 0:
                obj = obj[0]
                g_media.delStreamProxy(app=obj.app, name=obj.name)
                if obj.delete():
                    code = 1000
                    msg = "删除成功"
                else:
                    msg = "删除失败！"
            else:
                msg = "删除失败！"
        except Exception as e:
            msg = "删除失败：" + str(e)
    else:
        msg = "请求方法不支持"

    res = {
        "code": code,
        "msg": msg
    }
    return HttpResponseJson(res)


def api_postHandleForward(request):
    code = 0
    msg = "未知错误"
    if request.method == 'POST':
        params = parse_post_params(request)
        stream_code = params.get("code")
        handle = params.get("handle")  # add,del (add 代理流，del 取消代理)
        if handle in ["add", "del"]:
            try:
                stream = Stream.objects.get(code=stream_code)
                if "add" == handle:
                    if stream.forward_state == 1:
                        code = 1000
                        msg = "开启转发已经成功"
                    else:
                        __media_ret = g_media.addStreamProxy(app=stream.app, name=stream.name,
                                                             origin_url=stream.pull_stream_url)
                        if __media_ret:
                            stream.forward_state = 1
                            stream.save()
                            code = 1000
                            msg = "开启转发成功"
                        else:
                            msg = "开启转发失败！"
                else:
                    __media_ret = g_media.delStreamProxy(app=stream.app, name=stream.name)
                    stream.forward_state = 0
                    stream.save()
                    code = 1000
                    msg = "停止转发成功"

            except Exception as e:
                msg = "处理失败：" + str(e)
        else:
            msg = "请求处理类型错误！"
    else:
        msg = "请求方法不支持"

    res = {
        "code": code,
        "msg": msg
    }
    return HttpResponseJson(res)
