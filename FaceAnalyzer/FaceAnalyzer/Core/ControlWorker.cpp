#include "ControlWorker.h"
#include "Utils/Log.h"
#include "Utils/Common.h"
#include "Scheduler.h"
#include "Config.h"
#include "Algorithm.h"
#include "Control.h"
#include "AvPullStream.h"
#include "AvPushStream.h"
#include "Frame.h"
#include "Utils/ImageUtils.h"
#include "Utils/Base64.h"
#include "Utils/Request.h"
#include <json/json.h>
#include <opencv2/opencv.hpp>    //opencv header file

extern "C" {
#include "libswscale/swscale.h"
#include <libavutil/imgutils.h>
#include <libswresample/swresample.h>
}


namespace BXC_Algorithm {

    Worker::Worker(Scheduler* scheduler, Control* control) :
        mScheduler(scheduler),
        mControl(new Control(*control)),
        mPullStream(nullptr),
        mPushStream(nullptr),
        mState(false)
    {

        mControl->startTimestamp = getCurTimestamp();

        LOGI("");
    }

    Worker::~Worker()
    {
        LOGI("");

        std::this_thread::sleep_for(std::chrono::milliseconds(1));

        mState = false;// 将执行状态设置为false

        for (auto th : mThreads) {
            th->join();
        }

        for (auto th : mThreads) {
            delete th;
            th = nullptr;
        }
        mThreads.clear();

        if (mPullStream) {
            delete mPullStream;
            mPullStream = nullptr;
        }
        if (mPushStream) {
            delete mPushStream;
            mPushStream = nullptr;
        }


        if (mControl) {
            delete mControl;
            mControl = nullptr;
        }
        //最有一步释放mFramePool
        if (mVideoFramePool) {
            delete mVideoFramePool;
            mVideoFramePool = nullptr;
        }

    }
    bool Worker::start(std::string& msg) {

        this->mPullStream = new AvPullStream(this);
        if (this->mPullStream->connect()) {
            if (mControl->isPushStream) {
                this->mPushStream = new AvPushStream(this);
                if (this->mPushStream->connect()) {
                    // success
                }
                else {
                    msg = "pull stream connect success, push stream connect error";
                    return false;
                }
            }
            else {
                // success
            }
        }
        else {
            msg = "pull stream connect error";
            return false;
        }

        int videoBgrSize = mControl->videoHeight * mControl->videoWidth * mControl->videoChannel;
        this->mVideoFramePool = new FramePool(videoBgrSize);

        mState = true;// 将执行状态设置为true


        std::thread* th = new std::thread(AvPullStream::readThread, this->mPullStream);
        mThreads.push_back(th);

        th = new std::thread(Worker::decodeVideoThread, this);
        mThreads.push_back(th);

        if (mControl->isPushStream) {
            if (mControl->videoIndex > -1) {
                th = new std::thread(AvPushStream::encodeVideoThread, this->mPushStream);
                mThreads.push_back(th);
            }
        }

        for (auto th : mThreads) {
            th->native_handle();
        }


        return true;
    }


    bool Worker::getState() {
        return mState;
    }
    void Worker::remove() {
        mState = false;
        mScheduler->removeWorker(mControl);
    }

    void Worker::decodeVideoThread(void* arg) {
        Worker* worker = (Worker*)arg;
        worker->handleDecodeVideo();
    }
    void Worker::handleDecodeVideo() {
   
        int width = mPullStream->mVideoCodecCtx->width;
        int height = mPullStream->mVideoCodecCtx->height;

        AVPacket pkt; // 未解码的视频帧
        int      pktQSize = 0; // 未解码视频帧队列当前长度

        AVFrame* frame_yuv420p = av_frame_alloc();// pkt->解码->frame
        AVFrame* frame_bgr = av_frame_alloc();

        int frame_bgr_buff_size = av_image_get_buffer_size(AV_PIX_FMT_BGR24, width, height, 1);
        uint8_t* frame_bgr_buff = (uint8_t*)av_malloc(frame_bgr_buff_size);
        av_image_fill_arrays(frame_bgr->data, frame_bgr->linesize, frame_bgr_buff, AV_PIX_FMT_BGR24, width, height, 1);

        SwsContext* sws_ctx_yuv420p2bgr = sws_getContext(width, height,
            mPullStream->mVideoCodecCtx->pix_fmt,
            mPullStream->mVideoCodecCtx->width,
            mPullStream->mVideoCodecCtx->height,
            AV_PIX_FMT_BGR24,
            SWS_BICUBIC, nullptr, nullptr, nullptr);

        int fps = mControl->videoFps;

        //算法检测参数start
        bool cur_is_check = false;// 当前帧是否进行算法检测
        int  continuity_check_count = 0;// 当前连续进行算法检测的帧数
        int  continuity_check_max_time = 6000;//连续进行算法检测，允许最长的时间。单位毫秒
        int64_t continuity_check_start = getCurTime();//单位毫秒
        int64_t continuity_check_end = 0;
        //算法检测参数end

        int ret = -1;
        int64_t frameCount = 0;
        bool happen = false;
        float happenScore = 0.0;
        std::vector<DetectObject> detects;

        while (getState())
        {
            if (mPullStream->getVideoPkt(pkt, pktQSize)) {

                if (mControl->videoIndex > -1) {

                    ret = avcodec_send_packet(mPullStream->mVideoCodecCtx, &pkt);
                    if (ret == 0) {
                        ret = avcodec_receive_frame(mPullStream->mVideoCodecCtx, frame_yuv420p);

                        if (ret == 0) {
                            frameCount++;

                            // frame（yuv420p） 转 frame_bgr
                            sws_scale(sws_ctx_yuv420p2bgr,
                                frame_yuv420p->data, frame_yuv420p->linesize, 0, height,
                                frame_bgr->data, frame_bgr->linesize);

                            cv::Mat image(mControl->videoHeight, mControl->videoWidth, CV_8UC3, frame_bgr->data[0]);

                            if (pktQSize == 0) {
                                cur_is_check = this->checkVideoFrame(frameCount, image, detects, happen, happenScore);
                                if (cur_is_check) {
                                    continuity_check_count += 1;
                                }
                            }
                            else {
                                cur_is_check = false;
                            }



                            continuity_check_end = getCurTime();
                            if (continuity_check_end - continuity_check_start > continuity_check_max_time) {
                                mControl->checkFps = float(continuity_check_count) / (float(continuity_check_end - continuity_check_start) / 1000);
                                continuity_check_count = 0;
                                continuity_check_start = getCurTime();
                            }

                            //绘制检测框和fps start
                            int x1, y1, x2, y2;
                            for (int i = 0; i < detects.size(); i++)
                            {
                                x1 = detects[i].x1;
                                y1 = detects[i].y1;
                                x2 = detects[i].x2;
                                y2 = detects[i].y2;

                                std::vector<double> object_d;
                                object_d.push_back(x1);
                                object_d.push_back(y1);

                                object_d.push_back(x2);
                                object_d.push_back(y1);

                                object_d.push_back(x2);
                                object_d.push_back(y2);

                                object_d.push_back(x1);
                                object_d.push_back(y2);


                                std::string class_name = detects[i].class_name;
                                float       class_score = detects[i].score;

                                //if (class_name == mControl->objectCode && class_score >= mControl->classThresh) {
                                std::stringstream class_ss;
                                class_ss << std::setprecision(2) << class_score;
                                std::string class_ss_str = class_name + class_ss.str();

                                cv::rectangle(image, cv::Rect(x1, y1, (x2 - x1), (y2 - y1)), cv::Scalar(0, 255, 0), 2, cv::LINE_8, 0);
                                cv::putText(image, class_ss_str, cv::Point(x1 + 5, y1 + 15), cv::FONT_HERSHEY_SIMPLEX, 1, cv::Scalar(0, 255, 0), 2, cv::LINE_AA);
                                //}

                            }
                            std::stringstream fps_stream;
                            fps_stream << std::setprecision(4) << mControl->checkFps;
                            std::string fps_title = "checkfps: " + fps_stream.str();
                            cv::putText(image, fps_title, cv::Point(20, 40), cv::FONT_HERSHEY_COMPLEX, 1, cv::Scalar(0, 0, 255), 2, cv::LINE_AA);
                            
                     
                            cv::putText(image, mScheduler->mConfig->algorithmName, cv::Point(20, 80), cv::FONT_HERSHEY_COMPLEX, 1, cv::Scalar(0, 0, 255), 2, cv::LINE_AA);

                            //绘制检测框和fps end

     
                            //LOGI("decode 1 frame frameCount=%lld,pktQSize=%d,fps=%d,check=%d,checkFps=%f",
                            //    frameCount, pktQSize, fps, check, mControl->checkFps);

                            if (mControl->isPushStream) {//需要推算法实时流
                                int size = mPushStream->getVideoFrameQSize();
                                if (size < 3) {
                                    Frame* frame = mVideoFramePool->gain();
                                    frame->setBuf(frame_bgr->data[0], frame_bgr_buff_size);
                                    frame->happen = happen;
                                    frame->happenScore = happenScore;
                                    mPushStream->addVideoFrame(frame);
                                }
    
                            }
                            
                        
                        }
                        else {
                            LOGE("avcodec_receive_frame error : ret=%d", ret);
                        }
                    }
                    else {
                        LOGE("avcodec_send_packet error : ret=%d", ret);
                    }
                }

                // 队列获取的pkt，必须释放!!!
                //av_free_packet(&pkt);//过时
                av_packet_unref(&pkt);
            }
            else {
                std::this_thread::sleep_for(std::chrono::milliseconds(1));
            }
        }


        av_frame_free(&frame_yuv420p);
        //av_frame_unref(frame_yuv420p);
        frame_yuv420p = NULL;

        av_frame_free(&frame_bgr);
        //av_frame_unref(frame_bgr);
        frame_bgr = NULL;


        av_free(frame_bgr_buff);
        frame_bgr_buff = NULL;


        sws_freeContext(sws_ctx_yuv420p2bgr);
        sws_ctx_yuv420p2bgr = NULL;

    }
    bool Worker::checkVideoFrame(int64_t frameCount, cv::Mat& image, std::vector<DetectObject>& detects, bool& happen, float& happenScore) {
        
        bool cur_is_check = false;//该参数的意义是，判断本次执行，是否真正调用了算法。用于统计checkfps



        happen = false;
        happenScore = 0.0;

        bool cur_is_happen = false;
        Algorithm* algorihtm = mScheduler->gainAlgorithm();
        if (algorihtm) {

            cur_is_happen = algorihtm->objectDetect(mControl->videoHeight, mControl->videoWidth, image, detects);
            mScheduler->giveBackAlgorithm(algorihtm);

            if (cur_is_happen) {

                uint64_t curTimestamp = getCurTimestamp();
                uint64_t spendMs = curTimestamp - lastAlarmTimestamp;
                if (spendMs > 1000 * 1) {
                    lastAlarmTimestamp = getCurTimestamp();

                    //本次检测发生了事件，裁剪所有的人脸子图片
                    std::string url = mScheduler->getConfig()->adminHost + "/alarm/postAdd";
                    Json::Value param;
                    param["controlCode"] = mControl->code;
                    param["pullApp"] = mControl->pullApp;
                    param["pullName"] = mControl->pullName;
                    param["isPushStream"] = mControl->isPushStream;
                    param["pushApp"] = mControl->pushApp;
                    param["pushName"] = mControl->pushName;

                    param["startTimestamp"] = mControl->startTimestamp;
                    param["checkFps"] = mControl->checkFps;
                    param["videoWidth"] = mControl->videoWidth;
                    param["videoHeight"] = mControl->videoHeight;
                    param["videoChannel"] = mControl->videoChannel;
                    param["videoIndex"] = mControl->videoIndex;
                    param["videoFps"] = mControl->videoFps;

                    param["frameCount"] = frameCount;

                    JPGBufSize = 0;
                    if (CheckIsSupportTurboJpeg()) {
                        bgr2Jpg_by_turboJpeg(
                            mControl->videoHeight,
                            mControl->videoWidth,
                            mControl->videoChannel,
                            image.data,
                            JPGBuf,
                            JPGBufSize);
                    }
                    else {

                        std::vector<int> JPEG_QUALITY = { 75 };
                        std::vector<uchar> jpg;
                        cv::imencode(".jpg", image, jpg, JPEG_QUALITY);
                        JPGBufSize = jpg.size();
                        memcpy(JPGBuf, jpg.data(), JPGBufSize);
                    }


                    Base64 base64;
                    std::string imageBase64;
                    base64.encode(JPGBuf, JPGBufSize, imageBase64);
                    param["image_base64"] = imageBase64;

                    Json::Value param_detects;
                    Json::Value param_detects_item;
                    for (int i = 0; i < detects.size(); i++)
                    {
                        param_detects_item["x1"] = detects[i].x1;
                        param_detects_item["y1"] = detects[i].y1;
                        param_detects_item["x2"] = detects[i].x2;
                        param_detects_item["y2"] = detects[i].y2;
                        param_detects_item["score"] = detects[i].score;
                        param_detects_item["class_name"] = detects[i].class_name;

                        param_detects.append(param_detects_item);
                    }
                    param["detects"] = param_detects;
                    std::string data = param.toStyledString();
                    Request request;
                    std::string response;
                    request.post(url.data(), data.data(), response);

                    LOGI("\n \t request:%s \n \t response:%s",
                        url.data(),
                        response.data());


                    happen = true;
                    happenScore = 1.0;
                
                
                }


            }
            cur_is_check = true;
        }

        return cur_is_check;

    }

}