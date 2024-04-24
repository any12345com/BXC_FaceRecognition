#include "Config.h"
#include <fstream>
#include <iostream>
#include <filesystem>
#include <json/json.h>
#include "Utils/Log.h"

namespace BXC_Algorithm {
    Config::Config(const char* file) : file(file)
    {
    }
    Config::~Config()
    {
    }
    bool Config::read() {
        bool ret = false;
        std::ifstream ifs(file, std::ios::binary);

        if (!ifs.is_open()) {
            LOGE("open %s error", file);
            return ret;
        }
        else {
            Json::CharReaderBuilder builder;
            builder["collectComments"] = true;
            JSONCPP_STRING errs;
            Json::Value root;

            if (parseFromStream(builder, ifs, &root, &errs)) {
                //this->host = root["host"].asString();
                this->host = "127.0.0.1";

                this->adminPort = root["adminPort"].asInt();
                this->adminHost = "http://" + this->host + ":" + std::to_string(this->adminPort);

                this->analyzerPort = root["analyzerPort"].asInt();
                this->analyzerHost = "http://" + this->host + ":" + std::to_string(this->analyzerPort);

                this->mediaHttpPort = root["mediaHttpPort"].asInt();
                this->mediaRtspPort = root["mediaRtspPort"].asInt();
                this->mediaSecret = root["mediaSecret"].asCString();
                this->mediaHttpHost = "http://" + this->host + ":" + std::to_string(this->mediaHttpPort);
                this->mediaRtspHost = "rtsp://" + this->host + ":" + std::to_string(this->mediaRtspPort);

                this->uploadDir = root["uploadDir"].asString();
                this->algorithmName = root["algorithmName"].asString();
                this->algorithmDevice = root["algorithmDevice"].asString();

                this->supportHardwareVideoDecode = root["supportHardwareVideoDecode"].asBool();
                this->supportHardwareVideoEncode = root["supportHardwareVideoEncode"].asBool();

                ret = true;
            }
            else {
                LOGE("parse %s error, errs: %s", file, errs.c_str());
            }
            ifs.close();
        }
    
        return ret;
    }
    void Config::show() {

        printf("file=%s\n", file);
        printf("host=%s\n", host.data());
        printf("adminPort=%d\n", adminPort);
        printf("analyzerPort=%d\n", analyzerPort);
        printf("mediaHttpPort=%d\n", mediaHttpPort);
        printf("mediaRtspPort=%d\n", mediaRtspPort);
        printf("mediaSecret=%s\n", mediaSecret.data());
        printf("uploadDir=%s\n", uploadDir.data());
        printf("algorithmName=%s\n", algorithmName.data());
        printf("algorithmDevice=%s\n", algorithmDevice.data());
        printf("supportHardwareVideoDecode=%d\n", supportHardwareVideoDecode);
        printf("supportHardwareVideoEncode=%d\n", supportHardwareVideoEncode);
 
    }
}