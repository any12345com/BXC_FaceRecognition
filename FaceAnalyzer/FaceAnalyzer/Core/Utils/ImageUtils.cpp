#include "ImageUtils.h"
#include "Log.h"
#include "Common.h"
#include <opencv2/opencv.hpp>
#include <opencv2/imgcodecs/legacy/constants_c.h>
#ifdef WIN32
#ifndef _DEBUG
#include <turbojpeg.h>// windows+release环境下，图像的jpg压缩和解压缩均使用turboJpeg库实现，其余环境则使用opencv
#endif
#endif
#define BGR2JPG_MAX_SIZE 800000

namespace BXC_Algorithm {
    bool CheckIsSupportTurboJpeg() {

#ifdef WIN32
#ifndef _DEBUG
        return true; //windows+release 
#endif // !_DEBUG
#endif //WIN32
        return false;
    }

    bool __bgr2Jpg_by_turboJpeg(int height, int width, int channels, unsigned char* in_bgr, unsigned char*& out_jpg, unsigned long* out_jpg_size) {

#ifdef WIN32
#ifndef _DEBUG

        tjhandle handle = tjInitCompress();
        if (nullptr == handle) {
            return false;
        }

        //pixel_format : TJPF::TJPF_BGR or other
        const int JPEG_QUALITY = 70;
        int pixel_format = TJPF::TJPF_BGR;
        int pitch = tjPixelSize[pixel_format] * width;
        int ret = tjCompress2(handle, in_bgr, width, pitch, height, pixel_format,
            &out_jpg, out_jpg_size, TJSAMP_444, JPEG_QUALITY, TJFLAG_FASTDCT);

        tjDestroy(handle);

        if (ret != 0) {
            return false;
        }
        return true;

#endif // !_DEBUG
#endif //WIN32

        return false;
    }
    bool bgr2Jpg_by_turboJpeg(int height, int width, int channels, unsigned char* inBgr, unsigned char* outJpg, int& outJpgSize) {

        unsigned char* out_jpg_buf = nullptr;
        unsigned long  out_jpg_size = 0;

        bool ret = __bgr2Jpg_by_turboJpeg(height, width, channels, inBgr, out_jpg_buf, &out_jpg_size);

        if (ret) {//使用turboJpeg库进行图像压缩成功
            if (out_jpg_size > 0 && out_jpg_buf != nullptr) {

                outJpgSize = out_jpg_size;
                if (outJpgSize <= BGR2JPG_MAX_SIZE) {
                    memcpy(outJpg, out_jpg_buf, outJpgSize);
                }
                else {
                    outJpgSize = 0;
                }

                free(out_jpg_buf);
                out_jpg_buf = nullptr;
                return true;
            }
            else {
                return false;
            }

        }
        return false;
    }


}