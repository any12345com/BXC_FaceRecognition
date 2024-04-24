from app.views.ViewsBase import *
from app.models import *
from django.shortcuts import render
from app.utils.Common import buildPageLabels
from app.utils.Utils import gen_random_code_s
import shutil
import os
import random
import time
import numpy as np
import cv2
import base64


def __remove_AlarmAllFiles(image_path):
    try:
        image_path_absolute = os.path.join(g_config.uploadAlarmDir, image_path)
        image_path_absolute_dir = os.path.dirname(os.path.abspath(image_path_absolute))
        if os.path.exists(image_path_absolute_dir):
            shutil.rmtree(image_path_absolute_dir)  # 删除文件夹及其内部所有子文件
    except Exception as e:
        print("AlarmView.__remove_AlarmAllFiles() err:" + str(e))


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
    sql_data = "select * from av_alarm order by id desc limit %d,%d " % (
        skip, page_size)
    sql_data_num = "select count(id) as count from av_alarm "

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
    context["uploadAlarmDir_www"] = g_config.uploadAlarmDir_www

    return render(request, 'app/alarm/web_alarm_index.html', context)


def show(request):
    context = {

    }
    params = parse_get_params(request)
    code = params.get("code")
    try:
        obj = Alarm.objects.get(code=code)
        context["obj"] = obj
        context["uploadAlarmDir_www"] = g_config.uploadAlarmDir_www
    except Exception as e:
        print("AlarmView.edit()", e)

        return render(request, 'app/message.html',
                      {"msg": "请通过上班记录管理进入", "is_success": False, "redirect_url": "/alarm/index"})

    return render(request, 'app/alarm/web_alarm_show.html', context)


def api_postDel(request):
    code = 0
    msg = "未知错误"
    if request.method == 'POST':
        params = parse_post_params(request)
        alarm_code = params.get("code")
        try:
            obj = Alarm.objects.filter(code=alarm_code)
            if len(obj) > 0:
                obj = obj[0]
                image_path = obj.image_path
                if obj.delete():
                    __remove_AlarmAllFiles(image_path=image_path)
                    code = 1000
                    msg = "删除成功"
                else:
                    msg = "删除失败！"
            else:
                msg = "删除失败！"
        except Exception as e:
            msg = "删除失败：" + str(e)
    else:
        msg = "请求方法不支持！"

    res = {
        "code": code,
        "msg": msg
    }
    return HttpResponseJson(res)


def api_postAdd(request):
    code = 0
    msg = "未知错误"

    if request.method == 'POST':
        params = parse_post_params(request)
        print("AlarmView.api_postAdd() params=", params)

        controlCode = params.get("controlCode")
        pullApp = params.get("pullApp", "")
        pullName = params.get("pullName", "")
        isPushStream = int(params.get("isPushStream", 0))
        pushApp = params.get("pushApp", "")
        pushName = params.get("pushName", "")

        startTimestamp = int(params.get("startTimestamp", 0))
        checkFps = float(params.get("checkFps", 0))
        videoWidth = int(params.get("videoWidth", 0))
        videoHeight = int(params.get("videoHeight", 0))
        videoChannel = int(params.get("videoChannel", 0))
        videoIndex = int(params.get("videoIndex", 0))
        videoFps = int(params.get("videoFps", 0))
        frameCount = int(params.get("frameCount", 0))

        detects = params.get("detects", None)
        image_base64 = params.get("image_base64", None)

        if controlCode and pullApp and pullName and detects and image_base64:
            control = Control.objects.filter(code=controlCode)
            if len(control) > 0:
                # control = control[0]
                alarm = {
                    "image_base64": image_base64,
                    "controlCode": controlCode,
                    "pullApp": pullApp,
                    "pullName": pullName,
                    "isPushStream": isPushStream,
                    "pushApp": pushApp,
                    "pushName": pushName,
                    "startTimestamp": startTimestamp,
                    "checkFps": checkFps,
                    "videoWidth": videoWidth,
                    "videoHeight": videoHeight,
                    "videoChannel": videoChannel,
                    "videoFps": videoFps,
                    "frameCount": frameCount,
                    "detects": detects,
                    "create_time": datetime.now()
                }
                # g_alarmQueue.put(alarm, block=False)
                g_alarmQueue.put(alarm)

                clear_count = g_alarmQueue.qsize() - 5
                for i in range(clear_count):
                    g_alarmQueue.get()
                    g_alarmQueue.task_done()

                msg = "success"
                code = 1000

            else:
                msg = "incorrect alarm_control parameters"
        else:
            msg = "incorrect request parameters"
    else:
        msg = "request method not supported"
    res = {
        "code": code,
        "msg": msg
    }

    return HttpResponseJson(res)


def __CalculateAlarm():
    # 开启消费打卡记录数据
    loop_count = 0
    updateStaffFaceFeatureDict()

    while True:

        if g_alarmQueue.qsize() > 0:
            alarm_v = g_alarmQueue.get()
            print("开始处理打卡记录数据:", loop_count,g_alarmQueue.qsize())



            image_base64 = alarm_v["image_base64"]
            controlCode = alarm_v["controlCode"]
            detects = alarm_v["detects"]

            encoded_image_byte = base64.b64decode(image_base64)
            image_array = np.frombuffer(encoded_image_byte, np.uint8)
            # image = turboJpeg.decode(image_array)  # turbojpeg 解码
            image = cv2.imdecode(image_array, cv2.COLOR_RGB2BGR)  # opencv 解码

            faces, face_features = g_faceFeatureUtils.calculate_image(image,detects)
            face_count = 0
            face_filename = None
            face_image = None
            staff_code = None
            staff_name = None
            distance = 1000
            if len(faces) > 0:
                try:
                    for i in range(len(faces)):
                        face_feature = face_features[i]
                        __identity = getIdentityByFaceFeature(face_feature=face_feature)
                        faces[i]["distance"] = __identity["distance"]
                        faces[i]["staff_code"] = __identity["staff_code"]
                        faces[i]["staff_name"] = __identity["staff_name"]
                    faces = sorted(faces, key=lambda x: x["distance"], reverse=False)

                    staff_code = faces[0]["staff_code"]
                    staff_name = faces[0]["staff_name"]
                    if staff_code and staff_name:
                        face_count = 1
                        face_filename = faces[0]["face_filename"]
                        face_image = faces[0]["face_image"]
                        distance = faces[0]["distance"]
                        if distance > 0.5:
                            # staff_code = "stranger"
                            staff_name = "相似："+staff_name


                except Exception as e:
                    print("提取打卡图片人脸数据失败：", e)

            if face_count > 0:
                random_name = str(time.time()) + "-" + str(random.randint(1000, 9999))
                image_filename = "photo.jpg"

                image_dir = "{controlCode}/{ymd}/{random_name}".format(
                    dir=g_config.uploadAlarmDir,
                    controlCode=controlCode,
                    ymd=datetime.now().strftime("%Y%m%d"),
                    random_name=random_name
                )
                # 创建文件夹
                image_dir_abs = os.path.join(g_config.uploadAlarmDir, image_dir)
                if not os.path.exists(image_dir_abs):
                    os.makedirs(image_dir_abs)
                # 保存照片
                image_path = image_dir + "/" + image_filename
                image_path_abs = image_dir_abs + "/" + image_filename
                cv2.imwrite(image_path_abs, image)
                # 保存人脸子图
                face_image_path = image_dir + "/" + face_filename
                face_image_path_abs = image_dir_abs + "/" + face_filename
                cv2.imwrite(face_image_path_abs, face_image)


                alarm = Alarm()
                alarm.code = gen_random_code_s(prefix="alarm")
                alarm.user_id = 0
                alarm.sort = 0
                alarm.controlCode = controlCode
                alarm.pullApp = alarm_v.get("pullApp")
                alarm.pullName = alarm_v.get("pullName")
                alarm.isPushStream = alarm_v.get("isPushStream")
                alarm.pushApp = alarm_v.get("pushApp")
                alarm.pushName = alarm_v.get("pushName")
                alarm.startTimestamp = alarm_v.get("startTimestamp")
                alarm.checkFps = alarm_v.get("checkFps")
                alarm.videoWidth = alarm_v.get("videoWidth")
                alarm.videoHeight = alarm_v.get("videoHeight")
                alarm.videoChannel = alarm_v.get("videoChannel")
                alarm.videoFps = alarm_v.get("videoFps")
                alarm.frameCount = alarm_v.get("frameCount")
                alarm.detects = json.dumps(detects)
                alarm.image_dir = image_dir
                alarm.image_path = image_path
                alarm.create_time = alarm_v.get("create_time")
                alarm.state = 0
                alarm.is_calculate = 0
                alarm.face_count = face_count
                alarm.face_image_path = face_image_path
                alarm.staff_code = staff_code
                alarm.staff_name = staff_name
                alarm.distance = distance

                # print("开始保存")
                # 强制解锁数据库
                g_djangoSql.execute("PRAGMA wal_checkpoint(FULL)")
                alarm.save()
                # print("保存结束")

            g_alarmQueue.task_done()
            time.sleep(0.01)
        else:
            time.sleep(1)

        loop_count += 1


__it = threading.Thread(target=__CalculateAlarm)
__it.start()
