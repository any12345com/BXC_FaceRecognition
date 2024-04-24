### 人脸考勤系统
* 作者：北小菜 
* 官网：http://www.beixiaocai.com
* 邮箱：bilibili_bxc@126.com
* QQ：1402990689
* 微信：bilibili_bxc
* gitee开源地址：https://gitee.com/Vanishi/BXC_FaceRecognition
* github开源地址：https://github.com/any12345com/BXC_FaceRecognition

### 人脸考勤系统介绍
* 人脸考勤系统已开源，人脸考勤系统是一个基于C++和Python开发，yolov8-face作为人脸检测器，dlib作为人脸识别器的人脸考勤系统。使用该系统不限制接入摄像头数量，不限制摄像头布控数量，只需要在系统中录入人员信息，所有出现在布控摄像头的人员都会被检测和识别，未录入系统的人会被标记为陌生人。

### 关于编译
* 源码支持跨平台，支持Windows和Linux，推荐Windows平台，部署Linux需要自行编写编译构建文件
* Windows平台编译FaceAnalyzer时，需要的依赖库请到网盘地址下载，链接：https://pan.quark.cn/s/84475c79d6d1 提取码：WJLY

### 作者基于源码编译的一键启动安装包
* 安装包下载地址：链接：https://pan.quark.cn/s/992c389e1358 提取码：H84u

### 人脸考勤系统视频教程
* 人脸考勤系统介绍视频 https://www.bilibili.com/video/BV1Kk4y1D77L/
* 人脸考勤系统源码第1讲视频 https://www.bilibili.com/video/BV1Fi4y1s7hw
* 人脸考勤系统源码第2讲视频 https://www.bilibili.com/video/BV1jH4y1L7hw


### 配置说明
~~~
//config.json
{
  "host": "127.0.0.1", //部署设备IP地址（可以使用127.0.0.1,建议使用ipconfig获取本设备IP地址，可以实现远程访问）
  "adminPort": 9001,   //后台管理服务器端口
  "analyzerPort": 9002,//视频分析服务端口
  "videoAnalyzerPort": 9004, //启动工具端口
  "mediaHttpPort": 9003, //流媒体服务器HTTP端口（如需修改，FaceMediaServer/config.ini的对应端口也要修改）
  "mediaRtspPort": 9554, //流媒体服务器RTSP端口（如需修改，FaceMediaServer/config.ini的对应端口也要修改）
  "mediaSecret": "aqxY9ps21fyhyKNRyYpGvJCTp1JBeGOM",//流媒体服务器安全码（如需修改，FaceMediaServer/config.ini的对应安全码也要修改）
  "uploadDir": "E:\\project\\bxc\\BXC_FaceRecognition\\FaceRecognitionAdmin\\static\\upload",//后台管理上传算法，音频，报警视频等文件根目录
  "algorithmName": "model_v1.1",//算法名称 model_v1.0是1.0版本，model_v1.1是1.1版本
  "algorithmDevice": "GPU",
  "supportHardwareVideoDecode": false,   //是否支持硬件解码（建议关闭硬件解码，将硬件资源留给算法）
  "supportHardwareVideoEncode": false   //是否支持硬件编码（建议关闭硬件编码，将硬件资源留给算法）
}

~~~

