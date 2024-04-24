import psutil
import os
import time
import logging
import json
import threading
import argparse
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler


LOGFILE_TIMEFMT = "%Y-%m-%d_%H%M%S"
LOGFILE_WHEN = 'd'
LOGFILE_BACKUPCOUNT = 7


class App():
    def __init__(self, process_name, process_start_path):
        self.__process_name = process_name  # 例 MediaServer
        self.__process_start_path = process_start_path  # 例 D:\\bin\\MediaServer -c D:\\bin\\config.json

    def get_info(self):

        info = {
            "process": self.__process_name,
            "started": None,
            "status": None,
            "pid": None,
            "state": False
        }
        try:
            for pid in psutil.pids():
                process = psutil.Process(pid)

                process_name_lower = process.name().lower()
                __process_name_lower = self.__process_name.lower()

                if process_name_lower.startswith(__process_name_lower):
                    info["status"] = process.status()
                    info["pid"] = pid
                    timeArray = time.localtime(int(process.create_time()))
                    dateStr = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
                    info["started"] = dateStr
                    info["state"] = True
        except Exception as e:
            info["error"] = str(e)

        return info

    def __start_process(self):
        logger.info("start process_name=%s,process_start_path=%s" % (self.__process_name, self.__process_start_path))
        state = False
        try:
            res = os.popen(self.__process_start_path)
            res.read()
            state = True
        except Exception as e:
            logger.error("start %s error: %s" % (self.__process_name, str(e)))

        return state

    def __kill_process(self):

        for pid in psutil.pids():
            try:
                process = psutil.Process(pid)
                # print(u"进程名 %-20s  内存利用率 %-18s 进程状态 %-10s 创建时间 %-10s "
                #       % (p.name(), p.memory_percent(), p.status(), p.create_time()))

                process_name_lower = process.name().lower()
                __process_name_lower = self.__process_name.lower()

                if process_name_lower.startswith(__process_name_lower):
                    try:
                        process.kill()
                    except Exception as e:
                        logger.error("__kill_process error：%s" % (str(e)))

            except Exception as e:
                logger.error("__kill_process error：%s" % (str(e)))

        return True

    def start(self):

        self.__kill_process()
        self.__start_process()


class StartTools():
    def __init__(self):
        pass

    def run(self):

        ts = []
        self.__apps = []

        app = App("FaceMediaServer", "FaceMediaServer\\FaceMediaServer.exe -c FaceMediaServer\\config.ini")
        t = threading.Thread(target=app.start)
        ts.append(t)
        self.__apps.append(app)

        app = App("manage", "FaceRecognitionAdmin\\FaceRecognitionAdmin.exe runserver 0.0.0.0:%s --noreload" % str(g_adminPort))
        t = threading.Thread(target=app.start)
        ts.append(t)
        self.__apps.append(app)

        app = App("Analyzer", "FaceAnalyzer\\FaceAnalyzer.exe -f config.json")
        t = threading.Thread(target=app.start)
        ts.append(t)
        self.__apps.append(app)

        t = threading.Thread(target=self.__recordLog)
        ts.append(t)

        for t in ts:
            t.start()
        for t in ts:
            t.join()

    def __recordLog(self):

        recordLog_count = 0
        while True:
            time.sleep(g_recordLogInterval)

            recordLog_count += 1
            for app in self.__apps:
                info = app.get_info()
                info_str = str(info)
                logger.info("recordLog_count=%d,info=%s" % (recordLog_count, info_str))


def getLogger(logDir, is_show_console=False):
    if not os.path.exists(logDir):
        os.makedirs(logDir)

    fileName = os.path.join(logDir, "%s.log" % (datetime.now().strftime(LOGFILE_TIMEFMT)))
    level = logging.INFO
    logger = logging.getLogger()
    logger.setLevel(level)
    formatter = logging.Formatter('%(asctime)s %(name)s %(lineno)s %(levelname)s %(message)s')

    # 最基础
    # fileHandler = logging.FileHandler(fileName, encoding='utf-8')  # 指定utf-8格式编码，避免输出的日志文本乱码
    # fileHandler.setLevel(level)
    # fileHandler.setFormatter(formatter)
    # logger.addHandler(fileHandler)

    # 时间滚动切分
    # when:备份的时间单位，backupCount:备份保存的时间长度
    timedRotatingFileHandler = TimedRotatingFileHandler(fileName,
                                                        when=LOGFILE_WHEN,
                                                        backupCount=LOGFILE_BACKUPCOUNT,
                                                        encoding='utf-8')

    timedRotatingFileHandler.setLevel(level)
    timedRotatingFileHandler.setFormatter(formatter)
    logger.addHandler(timedRotatingFileHandler)

    # 控制台打印
    if is_show_console:
        streamHandler = logging.StreamHandler()
        streamHandler.setLevel(level)
        streamHandler.setFormatter(formatter)
        logger.addHandler(streamHandler)

    return logger


if __name__ == '__main__':
    logger = getLogger(logDir="log", is_show_console=True)
    logger.info("人脸考勤系统 built on 2024/01/18")

    parser = argparse.ArgumentParser()
    parser.add_argument('-config', type=str, default="config.json", help='config.json')
    args = parser.parse_args()
    config_filepath = args.config

    try:
        f = open(config_filepath, 'r', encoding='gbk')
        content = f.read()
        config_data = json.loads(content)
        f.close()

        g_adminPort = int(config_data.get("adminPort"))  # int
        g_recordLogInterval = 30

        startTools = StartTools()
        startTools.run()

    except Exception as e:
        logger.error("start error: %s" % str(e))
