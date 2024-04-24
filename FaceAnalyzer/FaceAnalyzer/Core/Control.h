#ifndef BXC_CONTROL_H
#define BXC_CONTROL_H

#include <string>
#include <vector>
#include <opencv2/opencv.hpp>
#include "Utils/Common.h"

namespace BXC_Algorithm {

	struct Control
	{
		// 布控请求必需参数
	public:
		std::string code;

		std::string pullApp;
		std::string pullName;
		std::string streamUrl;//拉流地址
		bool isPushStream = true;
		std::string pushApp;
		std::string pushName;
		std::string pushStreamUrl;//推流地址

	public:
		// 通过计算获得的参数
		int64_t startTimestamp = 0;// 执行器启动时毫秒级时间戳（13位）
		float   checkFps = 0;// 算法检测的帧率（每秒检测的次数）
		int     videoWidth = 0;  // 布控视频流的像素宽
		int     videoHeight = 0; // 布控视频流的像素高
		int     videoChannel = 0;
		int     videoIndex = -1;
		int     videoFps = 0;

	};

}
#endif //!BXC_CONTROL_H
