import json
import os
from framework.settings import BASE_DIR
class Config:
    def __init__(self):
        pass

        # filename = os.path.join("D:\\Project\\bxc\\BXC_VideoAnalyzer_v3\\Analyzer_v3", "config.json")

        BASE_DIR_PARENT_DIR = os.path.dirname(BASE_DIR) # 根目录的父级目录
        filename = os.path.join(BASE_DIR_PARENT_DIR, "config.json")

        f = open(filename, 'r', encoding='gbk')
        content = f.read()
        config_data = json.loads(content)
        f.close()

        print("Config.__init__",os.path.abspath(__file__))
        print("Config.__init__",config_data)

        host = config_data.get("host")
        videoAnalyzerPort =config_data.get("videoAnalyzerPort")
        adminPort =config_data.get("adminPort")
        analyzerPort =config_data.get("analyzerPort")
        mediaHttpPort =config_data.get("mediaHttpPort")
        mediaRtspPort =config_data.get("mediaRtspPort")
        mediaSecret =config_data.get("mediaSecret")
        uploadDir =config_data.get("uploadDir")
        algorithmName =config_data.get("algorithmName")
        algorithmDevice =config_data.get("algorithmDevice")
        # mediaRootDir =config_data.get("mediaRootDir")

        self.host = host
        self.videoAnalyzerHost = "http://"+host +":"+ str(videoAnalyzerPort)  # http://127.0.0.1:9000
        self.adminHost = "http://"+host +":"+ str(adminPort)         # http://127.0.0.1:9001
        self.analyzerHost = "http://"+host +":"+ str(analyzerPort)   # http://127.0.0.1:9002
        self.mediaHttpHost = "http://"+host +":"+ str(mediaHttpPort) # http://127.0.0.1:80
        self.mediaWsHost = "ws://"+host +":"+ str(mediaHttpPort)     # http://127.0.0.1:80
        self.mediaRtspHost = "rtsp://"+host +":"+ str(mediaRtspPort) # http://127.0.0.1:554
        self.mediaSecret = mediaSecret
        self.uploadDir = uploadDir
        self.algorithmName = algorithmName
        self.algorithmDevice = algorithmDevice

        self.uploadTempDir = os.path.join(self.uploadDir, "temp") # 临时缓存文件夹，可以不用清理
        self.uploadAlgorithmWeightDir = os.path.join(self.uploadDir, "weight")
        # self.uploadAudioDir = os.path.join(self.uploadDir,"audio")
        self.uploadStaffDir = os.path.join(self.uploadDir,"staff")
        self.uploadAlarmDir = os.path.join(self.uploadDir,"alarm")

        # self.mediaRootDir = mediaRootDir

        self.uploadDir_www = "/static/upload/"
        # self.uploadAudioDir_www = "/static/upload/audio/"
        self.uploadStaffDir_www = "/static/upload/staff/"
        self.uploadAlarmDir_www = "/static/upload/alarm/"


    def __del__(self):
        pass

    def show(self):
        pass


