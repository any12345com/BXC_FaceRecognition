import os
from app.views.ViewsBase import *
from app.models import *
from django.shortcuts import render
from app.utils.Utils import buildPageLabels, gen_random_code_s
import shutil


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
    sql_data = "select * from av_staff order by id desc limit %d,%d " % (
        skip, page_size)
    sql_data_num = "select count(id) as count from av_staff "

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
    context["uploadStaffDir_www"] = g_config.uploadStaffDir_www

    return render(request, 'app/staff/web_staff_index.html', context)


def __remove_upload_file(image_path):
    #image_path：被删除照片文件的相对路径
    try:
        image_path_abs = os.path.join(g_config.uploadStaffDir, image_path)
        image_path_dir = os.path.dirname(os.path.abspath(image_path_abs))
        if os.path.exists(image_path_dir):
            shutil.rmtree(image_path_dir)  # 删除文件夹及其内部所有子文件
    except Exception as e:
        print("StaffView.__remove_upload_file() err: " + str(e))


def __add_upload_file(file):
    __ret = False
    __msg = "未知错误"
    __data = None

    try:
        file_name = file.name  # 上传文件的名称
        file_size = file.size  # 上传文件的字节大小 1M = 1024*1024, 100M = 100*1024*1024 = 104857600
        file_size_m = int(file_size / 1024 / 1024)
        file_content_type = file.content_type  # 上传文件的 content_type [wav->audio/wav , mp3->audio/mpeg]

        if file_size_m <= 5:
            if 'image/png' == file_content_type or 'image/jpeg' == file_content_type or 'image/jpg' == file_content_type:

                up_relative_dir = datetime.now().strftime("%Y%m%d%H%M%S")
                UP_ABSOLUTE_DIR = os.path.join(g_config.uploadStaffDir, up_relative_dir)

                if not os.path.exists(UP_ABSOLUTE_DIR):
                    os.makedirs(UP_ABSOLUTE_DIR)

                image_path_abs = os.path.join(UP_ABSOLUTE_DIR, file_name)  # 上传音频的文件绝对存储路径
                # 将文件写入到本地文件
                up_f = open(image_path_abs, 'wb')
                up_f.write(file.read())
                up_f.close()

                image_path = up_relative_dir + "/" + file_name

                __ret = True
                __msg = "上传照片文件成功"
                __data = {
                    "image_dir": up_relative_dir,
                    "image_path": image_path,
                    "image_path_abs": image_path_abs
                }
            else:
                __msg = "照片文件格式必须是png,jpg,jpeg"
        else:
            __msg = "照片文件不能超过5M:" + str(file_size_m)
    except Exception as e:
        __msg = "上传照片文件失败:" + str(e)

    return __ret, __msg, __data


def add(request):
    if "POST" == request.method:
        __ret = False
        __msg = "未知错误"

        params = parse_post_params(request)
        handle = params.get("handle")

        name = params.get("name", "")

        extend_params = params.get("extend_params", "").strip()
        remark = params.get("remark", "").strip()

        if "add" == handle:
            file = request.FILES.get("file")
            __add_ret, __add_msg, __add_data = __add_upload_file(file)
            if __add_ret:
                image_dir = __add_data["image_dir"]
                image_path = __add_data["image_path"]
                image_path_abs = __add_data["image_path_abs"]

                __face_ret, __face_image_path, __face_feature = g_faceFeatureUtils.calculate_file(
                    image_dir=image_dir,
                    image_path_abs=image_path_abs)

                if __face_ret:
                    try:
                        user_id = getUser(request).get("id")
                    except:
                        user_id = 0

                    obj = Staff()
                    obj.user_id = user_id
                    obj.sort = 0
                    obj.code = params.get("code")
                    obj.name = name.strip()
                    obj.extend_params = extend_params
                    obj.remark = remark
                    obj.image_path = image_path
                    obj.face_image_path = __face_image_path
                    obj.face_feature = __face_feature
                    obj.state = 0
                    obj.is_from_author = 0
                    obj.create_time = datetime.now()
                    obj.last_update_time = datetime.now()
                    obj.save()
                    __msg = "添加成功"
                    __ret = True
                else:
                    __remove_upload_file(image_path=image_path)
                    __msg = "添加失败：提取人脸数据失败"
            else:
                __msg = __add_msg
        else:
            __msg = "请求参数不完整"

        if __ret:
            redirect_url = "/staff/index"
        else:
            redirect_url = "/staff/add"

        return render(request, 'app/message.html',
                      {"msg": __msg, "is_success": __ret, "redirect_url": redirect_url})
    else:

        context = {

        }
        context["handle"] = "add"
        context["obj"] = {
            "code": gen_random_code_s("STAFF")
        }

        return render(request, 'app/staff/web_staff_add.html', context)


def edit(request):
    if "POST" == request.method:
        __ret = False
        __msg = "未知错误"

        params = parse_post_params(request)
        handle = params.get("handle")
        code = params.get("code")
        name = params.get("name")
        extend_params = params.get("extend_params", "").strip()
        remark = params.get("remark", "").strip()

        if "edit" == handle and code and name:

            obj = Staff.objects.get(code=code)
            obj.name = params.get("name").strip()
            obj.extend_params = extend_params

            replace_image_is_success = False
            old_image_path = obj.image_path

            file = request.FILES.get("file")
            __add_ret, __add_msg, __add_data = __add_upload_file(file)
            if __add_ret:
                __face_ret, __face_image_path, __face_feature = g_faceFeatureUtils.calculate_file(
                    image_dir=__add_data["image_dir"],
                    image_path_abs=__add_data["image_path_abs"])
                if __face_ret:
                    replace_image_is_success = True
                    obj.image_path = __add_data.get("image_path")
                    obj.face_image_path = __face_image_path
                    obj.face_feature = ",".join(map(lambda x: str(x), __face_feature))

            if replace_image_is_success:
                __remove_upload_file(image_path=old_image_path)

            obj.remark = remark
            obj.last_update_time = datetime.now()
            obj.save()
            __msg = "编辑成功"
            __ret = True
        else:
            __msg = "请求参数不完整"

        if __ret:
            redirect_url = "/staff/index"
        else:
            redirect_url = "/staff/edit?code=" + code

        return render(request, 'app/message.html',
                      {"msg": __msg, "is_success": __ret, "redirect_url": redirect_url})

    else:
        context = {

        }
        params = parse_get_params(request)
        code = params.get("code")
        try:
            obj = Staff.objects.get(code=code)
            context["handle"] = "edit"
            context["obj"] = obj
            context["uploadStaffDir_www"] = g_config.uploadStaffDir_www
        except Exception as e:
            print("StaffView.edit()", e)

            return render(request, 'app/message.html',
                          {"msg": "请通过员工管理进入", "is_success": False, "redirect_url": "/staff/index"})

        return render(request, 'app/staff/web_staff_add.html', context)


def api_postDel(request):
    code = 0
    msg = "未知错误"
    if request.method == 'POST':
        params = parse_post_params(request)
        staff_code = params.get("code")
        try:
            obj = Staff.objects.filter(code=staff_code)
            if len(obj) > 0:
                obj = obj[0]
                if obj.is_from_author:
                    msg = "系统内置不允许删除！"
                else:
                    image_path = obj.image_path
                    if obj.delete():
                        __remove_upload_file(image_path=image_path)
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
