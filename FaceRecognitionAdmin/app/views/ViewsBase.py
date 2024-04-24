import json
import time
import threading
import os
import numpy as np
import cv2
import dlib
from datetime import datetime
import queue
from app.utils.ZLMediaKit import ZLMediaKit
from app.utils.AnalyzerApi import AnalyzerApi
from app.utils.DjangoSql import DjangoSql
from app.utils.Config import Config
from django.http import HttpResponse
from app.models import Stream, Staff, Alarm

g_alarmQueue = queue.Queue(100)
g_staffs = []  # 员工信息
g_config = Config()
g_media = ZLMediaKit(config=g_config)
g_analyzer = AnalyzerApi(host=g_config.analyzerHost)
g_djangoSql = DjangoSql()
g_session_key_user = "user"


class FaceFeatureUtils():
    def __init__(self, uploadAlgorithmWeightDir):
        # 加载正脸检测器
        self.detector = dlib.get_frontal_face_detector()

        # 加载人脸关键点检测器
        shape_model_path = os.path.join(uploadAlgorithmWeightDir, "shape_predictor_68_face_landmarks.dat")
        self.shape_pred = dlib.shape_predictor(shape_model_path)

        # 3. 加载人脸识别模型
        recognition_model_path = os.path.join(uploadAlgorithmWeightDir, "dlib_face_recognition_resnet_model_v1.dat")
        self.facerec = dlib.face_recognition_model_v1(recognition_model_path)

    def calculate_file(self, image_dir, image_path_abs):
        __face_ret = False
        __face_image_path = None
        __face_feature = None

        image = cv2.imread(image_path_abs)
        # image = resize(image, width=300)
        # image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # 1.人脸检测
        detects = self.detector(image, 1)

        if len(detects) > 0:
            # 2.关键点检测
            detect = detects[0]
            shape = self.shape_pred(image, detect)
            # 3.描述子提取，128D向量
            face_descriptor = self.facerec.compute_face_descriptor(image, shape)
            # __face_feature = np.array(face_descriptor)# 转换为numpy array
            __face_feature = list(face_descriptor)

            # rectangle [(x1,y1),(x2,y2)]
            x1 = detect.left()
            y1 = detect.top()
            x2 = detect.right()
            y2 = detect.bottom()
            face = image[y1:y2, x1:x2]  # 人脸照片
            filename = "face.jpg"

            face_image_path_abs_dir = os.path.dirname(image_path_abs)
            if not os.path.exists(face_image_path_abs_dir):
                os.makedirs(face_image_path_abs_dir)
            print("face_image_path_abs_dir=",face_image_path_abs_dir,face.shape)
            face_image_path_abs = face_image_path_abs_dir + "/" + filename
            print("face_image_path_abs=",face_image_path_abs,face.shape)

            cv2.imwrite(face_image_path_abs, face)

            __face_image_path = image_dir + "/" + filename
            __face_ret = True

        __face_feature_str = None
        if __face_ret:
            __face_feature_str = ",".join(map(lambda x: str(x), __face_feature))

        return __face_ret, __face_image_path, __face_feature_str

    def calculate_image(self, image, detects):

        # image = resize(image, width=300)
        # image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        # h,w,c = image.shape

        faces = []
        face_features = []

        for i in range(len(detects)):
            detect_dict = detects[i]
            x1 = int(detect_dict["x1"])
            y1 = int(detect_dict["y1"])
            x2 = int(detect_dict["x2"])
            y2 = int(detect_dict["y2"])
            score = float(detect_dict["score"])
            class_name = detect_dict["class_name"]

            # 计算特征值start
            detect = dlib.rectangle(x1, y1, x2, y2)
            shape = self.shape_pred(image, detect)
            # 3.描述子提取，128D向量
            face_descriptor = self.facerec.compute_face_descriptor(image, shape)
            face_feature = np.array(face_descriptor)  # 转换为numpy array
            # 计算特征值end
            face_filename = "face%d.jpg" % i
            face_image = image[y1:y2, x1:x2]

            face_features.append(face_feature)
            faces.append({
                "face_filename": face_filename,
                "face_image": face_image
            })

        return faces, face_features


g_faceFeatureUtils = FaceFeatureUtils(uploadAlgorithmWeightDir=g_config.uploadAlgorithmWeightDir)


def updateStaffFaceFeatureDict():
    print("更新员工人脸特征库缓存")
    staffs = Staff.objects.all()
    g_staffs.clear()
    for staff in staffs:

        feature_str_array = staff.face_feature.split(",")
        print(staff.code, staff.name, len(feature_str_array), feature_str_array)
        if 128 == len(feature_str_array):
            face_feature = np.array(list(map(lambda x: float(x), feature_str_array)))
            g_staffs.append({
                "code": staff.code,
                "name": staff.name,
                "remark": staff.remark,
                "feature": face_feature
            })


def getIdentityByFaceFeature(face_feature):
    __identity = {
        "staff_code": None,
        "staff_name": None,
        "distance": 0
    }

    result = []
    for staff in g_staffs:
        staff_code = staff["code"]
        staff_name = staff["name"]
        staff_feature = staff["feature"]
        distance = np.linalg.norm(face_feature - staff_feature)

        distance = float("%.5f"%distance)
        result.append({
            "staff_code": staff_code,
            "staff_name": staff_name,
            "distance": distance,
        })

    if len(result) > 0:
        result = sorted(result, key=lambda x: x["distance"], reverse=False)
        first = result[0]
        # distance = first["distance"]
        __identity["staff_code"] = first["staff_code"]
        __identity["staff_name"] = first["staff_name"]
        __identity["distance"] = first["distance"]

    return __identity


def getUser(request):
    user = request.session.get(g_session_key_user)
    # request.session.get("user") = {'id': 1, 'username': 'admin', 'email': '786251107@qq.com', 'last_login': '2022-06-03 22:33:21'}

    return user


def parse_get_params(request):
    params = {}
    try:
        for k in request.GET:
            params.__setitem__(k, request.GET.get(k))
    except Exception as e:
        print("parse_get_params", e)

    return params


def parse_post_params(request):
    params = {}
    try:

        for k in request.POST:
            params.__setitem__(k, request.POST.get(k))

        # 接收json方式上传的参数
        if not params:
            try:
                params = request.body.decode('utf-8')
                params = json.loads(params)
            except Exception as e:
                print("ViewBase.parse_post_params() error:", e)
                params = {}
    except Exception as e:
        print("ViewBase.parse_post_params() error:", e)

    return params


def HttpResponseJson(res):
    def json_dumps_default(obj):
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        else:
            raise TypeError

    return HttpResponse(json.dumps(res, default=json_dumps_default), content_type="application/json")


def readAllStreamData():
    data = g_djangoSql.select("select * from av_stream order by id desc")
    return data


def readAllControlData():
    data = g_djangoSql.select("select * from av_control order by id desc")
    return data


def AllStreamStartForward():
    __ret = False
    __msg = "未知错误"

    try:
        online_data = g_media.getMediaList()
        online_dict = {}
        mediaServerState = g_media.mediaServerState
        if not mediaServerState:
            # 流媒体服务不在线，全部更新下线状态
            g_djangoSql.execute("update av_stream set forward_state=0")
            __msg = "流媒体服务不在线，无法开启转发！"
        else:
            for d in online_data:
                app_name = "{app}_{name}".format(app=d["app"], name=d["name"])
                online_dict[app_name] = d
            streams = Stream.objects.all()

            successCount = 0
            errorCount = 0
            for stream in streams:
                stream_app_name = "{app}_{name}".format(app=stream.app, name=stream.name)
                if online_dict.get(stream_app_name):  # 当前流已经在线，不用再次请求转发
                    successCount += 1
                else:
                    __media_ret = g_media.addStreamProxy(app=stream.app,
                                                         name=stream.name,
                                                         origin_url=stream.pull_stream_url)
                    if __media_ret:
                        stream.forward_state = 1
                        stream.save()
                        successCount += 1
                    else:
                        errorCount += 1

            if successCount > 0:
                __ret = True
            __msg = "转发成功%d条,转发失败%d条" % (successCount, errorCount)

    except Exception as e:
        __msg = "开启转发失败：" + str(e)

    return __ret, __msg


def __InitThread():
    i = 0
    while True:
        g_media.getMediaList()
        mediaServerState = g_media.mediaServerState
        if mediaServerState:
            __ret, __msg = AllStreamStartForward()
            print("AllStreamStartForward()", i, __ret, __msg)
            break
        time.sleep(1)
        i += 1

    # 版本检测
    # j = 0
    # while True:
    #     print("j", j)
    #     time.sleep(1)
    #     j += 1


__it = threading.Thread(target=__InitThread)
__it.start()
# __it.join()
