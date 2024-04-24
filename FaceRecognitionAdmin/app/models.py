from django.db import models
from django.utils import timezone


class Alarm(models.Model):
    code = models.CharField(max_length=50, verbose_name='编号')
    user_id = models.IntegerField(verbose_name='用户')
    sort = models.IntegerField(verbose_name='排序')
    controlCode = models.CharField(max_length=50,verbose_name='布控编号')
    pullApp = models.CharField(max_length=50,verbose_name='')
    pullName = models.CharField(max_length=50,verbose_name='')
    isPushStream = models.IntegerField(verbose_name='')
    pushApp = models.CharField(max_length=50, verbose_name='')
    pushName = models.CharField(max_length=50, verbose_name='')
    startTimestamp = models.IntegerField(verbose_name='')
    checkFps = models.IntegerField(verbose_name='')
    videoWidth = models.IntegerField(verbose_name='')
    videoHeight = models.IntegerField(verbose_name='')
    videoChannel = models.IntegerField(verbose_name='')
    videoFps = models.IntegerField(verbose_name='')
    frameCount = models.IntegerField(verbose_name='')
    detects = models.TextField(verbose_name='检测结果')
    image_dir = models.CharField(max_length=200, verbose_name='图片存储文件夹')
    image_path = models.CharField(max_length=200, verbose_name='图片存储路径')

    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    state = models.IntegerField(verbose_name='状态')  # 0:未读 1:已读 5:已删除
    is_calculate = models.IntegerField(verbose_name='是否计算')  # 0 未被计算 1 已被计算
    face_count = models.IntegerField(verbose_name='人脸数量')
    face_image_path = models.CharField(max_length=200,verbose_name='人脸图片地址')
    staff_code = models.CharField(max_length=200,verbose_name='员工编号')
    staff_name = models.CharField(max_length=200,verbose_name='员工名称')
    distance = models.FloatField(verbose_name='最小距离')

    def __repr__(self):
        return self.pullApp + self.pullName

    def __str__(self):
        return self.pullApp + self.pullName

    class Meta:
        db_table = 'av_alarm'
        verbose_name = '报警视频'
        verbose_name_plural = '报警视频'

class Staff(models.Model):
    user_id = models.IntegerField(verbose_name='用户')

    sort = models.IntegerField(verbose_name='排序')
    code = models.CharField(max_length=50, verbose_name='编号')
    name = models.CharField(max_length=50, verbose_name='员工姓名')
    extend_params = models.CharField(max_length=100, verbose_name='扩展参数')
    remark = models.CharField(max_length=100, verbose_name='备注')

    image_path = models.CharField(max_length=200, verbose_name='照片相对路径')
    face_image_path = models.CharField(max_length=200, verbose_name='照片提取人脸相对路径')
    face_feature = models.TextField(verbose_name='照片提取人脸特征')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    last_update_time = models.DateTimeField(auto_now_add=True, verbose_name='更新时间')
    state = models.IntegerField(verbose_name='状态')  # 0 未读
    is_from_author = models.IntegerField(verbose_name='是否来自于作者') # 1:来自作者 0:非来自作者

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'av_staff'
        verbose_name = '员工'
        verbose_name_plural = '员工'

class Control(models.Model):
    user_id = models.IntegerField(verbose_name='用户')
    sort = models.IntegerField(verbose_name='排序')
    code = models.CharField(max_length=50, verbose_name='编号')

    stream_app = models.CharField(max_length=50, verbose_name='视频流应用')
    stream_name = models.CharField(max_length=100, verbose_name='视频流名称')
    stream_video = models.CharField(max_length=100, verbose_name='视频流视频')
    stream_audio = models.CharField(max_length=100, verbose_name='视频流音频')

    remark = models.CharField(max_length=200, verbose_name='备注')

    push_stream = models.BooleanField(verbose_name='是否推流')
    push_stream_app = models.CharField(max_length=50, null=True,verbose_name='推流应用')
    push_stream_name = models.CharField(max_length=100, null=True,verbose_name='推流名称')

    state = models.IntegerField(default=0,verbose_name="布控状态") # 0：未布控  1：布控中  5：布控中断

    create_time = models.DateTimeField(auto_now_add=True,verbose_name='创建时间')
    last_update_time = models.DateTimeField(auto_now_add=True,verbose_name='更新时间')

    def __repr__(self):
        return self.code

    def __str__(self):
        return self.code

    class Meta:
        db_table = 'av_control'
        verbose_name = '布控'
        verbose_name_plural = '布控'

class Stream(models.Model):
    user_id = models.IntegerField(verbose_name='用户')
    sort = models.IntegerField(verbose_name='排序')
    code = models.CharField(max_length=50, verbose_name='编号')
    app = models.CharField(max_length=50, verbose_name='分组')
    name = models.CharField(max_length=50, verbose_name='名称')
    pull_stream_url = models.CharField(max_length=300, verbose_name='视频流来源')
    pull_stream_type = models.IntegerField(verbose_name='视频流来源类型')
    nickname = models.CharField(max_length=200, verbose_name='视频流昵称')
    remark = models.CharField(max_length=200, verbose_name='备注')
    forward_state = models.IntegerField(verbose_name='转发状态')  # 默认0, 0:未转发 1:转发中
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    last_update_time = models.DateTimeField(auto_now_add=True, verbose_name='更新时间')
    state = models.IntegerField(verbose_name='状态')

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'av_stream'
        verbose_name = '视频流'
        verbose_name_plural = '视频流'

