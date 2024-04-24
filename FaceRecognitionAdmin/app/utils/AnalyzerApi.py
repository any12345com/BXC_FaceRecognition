import requests
import json
import time


class AnalyzerApi():
    def __init__(self, host):
        self.host = host
        self.timeout = 30
        self.default_user_agent = "FaceAlgorithmWeb"
        self.analyzerServerState = False  # 分析器服务状态

    def controls(self):
        """
        """
        __state = False
        __msg = "error"
        __data = []

        try:
            headers = {
                "User-Agent": self.default_user_agent,
                "Content-Type": "application/json;"
            }
            url = '%s/api/controls' % self.host
            res = requests.get(url=url, headers=headers, timeout=self.timeout)
            if res.status_code:
                res_result = res.json()
                __msg = res_result["msg"]
                if res_result["code"] == 1000:

                    res_result_data = res_result.get("data")
                    if res_result_data:
                        __data = res_result_data
                    __state = True
            else:
                __msg = "status_code=%d " % (res.status_code)
            self.analyzerServerState = True
        except Exception as e:
            self.analyzerServerState = False
            __msg = str(e)
        return __state, __msg, __data

    def control_add(self, code, pullApp, pullName, isPushStream, pushApp, pushName):
        __state = False
        __msg = "error"

        try:
            headers = {
                "User-Agent": self.default_user_agent,
                "Content-Type": "application/json;"
            }

            data = {
                "code": code,
                "pullApp": pullApp,
                "pullName": pullName,
                "isPushStream": isPushStream,
                "pushApp": pushApp,
                "pushName": pushName,
            }

            data_json = json.dumps(data)
            res = requests.post(url='%s/api/control/add' % self.host, headers=headers,
                                data=data_json, timeout=self.timeout)
            if res.status_code:
                res_result = res.json()
                __msg = res_result["msg"]
                if res_result["code"] == 1000:
                    __state = True

            else:
                __msg = "status_code=%d " % (res.status_code)
            self.analyzerServerState = True
        except Exception as e:
            self.analyzerServerState = False
            __msg = str(e)

        return __state, __msg

    def control_cancel(self, code):
        """
        @code   布控编号    [str]  xxxxxxxxx
        """
        __state = False
        __msg = "error"

        try:
            headers = {
                "User-Agent": self.default_user_agent,
                "Content-Type": "application/json;"
            }
            data = {
                "code": code,
            }

            data_json = json.dumps(data)
            res = requests.post(url='%s/api/control/cancel' % self.host, headers=headers,
                                data=data_json, timeout=self.timeout)
            if res.status_code:
                res_result = res.json()
                __msg = res_result["msg"]
                if res_result["code"] == 1000:
                    __state = True

            else:
                __msg = "status_code=%d " % (res.status_code)
            self.analyzerServerState = True
        except Exception as e:
            self.analyzerServerState = False
            __msg = str(e)

        return __state, __msg
