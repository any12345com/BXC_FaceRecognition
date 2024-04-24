from django.urls import path
from .views import UserView
from .views import IndexView
from .views import StaffView
from .views import StreamView
from .views import ControlView
from .views import AlarmView
from .views import OpenView
app_name = 'app'

urlpatterns = [
    # 主页功能
    path('', IndexView.index),
    path('index/getIndex', IndexView.api_getIndex),
    # 用户登陆，退出，用户中心
    path('login', UserView.web_login),
    path('logout', UserView.web_logout),
    path('user/index', UserView.index),

    # 视频流功能
    path('stream/online', StreamView.online),
    path('stream/getIndex', StreamView.api_getIndex),
    path('stream/index', StreamView.index),
    path('stream/add', StreamView.add),
    path('stream/edit', StreamView.edit),
    path('stream/postDel', StreamView.api_postDel),
    path('stream/postHandleForward', StreamView.api_postHandleForward),
    path('stream/player', StreamView.player),
    path('stream/getOnline', StreamView.api_getOnline),
    path('stream/getAllStartForward', StreamView.api_getAllStartForward),
    path('stream/getAllUpdateForwardState', StreamView.api_getAllUpdateForwardState),
    path('stream/postImportFile', StreamView.api_postImportFile),

    # 布控功能
    path('controls', ControlView.web_controls),
    path('control/add', ControlView.web_add_control),
    path('control/edit', ControlView.web_edit_control),
    path('api/postAddControl', ControlView.api_postAddControl),
    path('api/postEditControl', ControlView.api_postEditControl),
    path('api/postDelControl', ControlView.api_postDelControl),

    path('api/getControls', ControlView.api_getControls),
    path('api/postAddAnalyzer', ControlView.api_postAddAnalyzer),
    path('api/postCancelAnalyzer', ControlView.api_postCancelAnalyzer),

    # 员工管理
    path('staff/index', StaffView.index),
    path('staff/add', StaffView.add),
    path('staff/edit', StaffView.edit),
    path('staff/postDel', StaffView.api_postDel),

    # 上班记录管理
    path('alarm/index', AlarmView.index),
    path('alarm/show', AlarmView.show),
    path('alarm/postDel', AlarmView.api_postDel),
    path('alarm/postAdd', AlarmView.api_postAdd),

    # 开放接口
    path('open/index', OpenView.index),


]