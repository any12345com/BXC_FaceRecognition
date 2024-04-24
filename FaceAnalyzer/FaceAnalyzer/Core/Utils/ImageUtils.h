#ifndef ANALYZER_IMAGEUTILS_H
#define ANALYZER_IMAGEUTILS_H

#include <string>

namespace BXC_Algorithm {
	bool CheckIsSupportTurboJpeg();

	//压缩图片（turboJpeg）
	bool bgr2Jpg_by_turboJpeg(int height, int width, int channels, unsigned char* inBgr, unsigned char* outJpg,int& outJpgSize);
}
#endif //ANALYZER_IMAGEUTILS_H