#ifndef BXC_CONTROLWORKER_H
#define BXC_CONTROLWORKER_H
#include <thread>
#include <queue>
#include <mutex>
#include <opencv2/opencv.hpp>

namespace BXC_Algorithm {
	class Scheduler;
	class AvPullStream;
	class AvPushStream;
	struct Control;
	struct Frame;
	class FramePool;
	struct DetectObject;

	class Worker
	{
	public:
		explicit Worker(Scheduler* scheduler, Control* control);
		~Worker();
	public:
		static void decodeVideoThread(void* arg);// （线程）解码视频帧和实时分析视频帧
		void handleDecodeVideo();
	public:
		bool start(std::string& msg);

		bool getState();
		void remove();
	public:
		Control* mControl;
		Scheduler* mScheduler;
		AvPullStream* mPullStream;
		AvPushStream* mPushStream;
		FramePool* mVideoFramePool;

	private:
		bool mState = false;
		std::vector<std::thread*> mThreads;

		unsigned char JPGBuf[1000000]; //bgr图片经过jpg压缩后的数据
		int			  JPGBufSize = 0;

		uint64_t lastAlarmTimestamp = 0;
		bool checkVideoFrame(int64_t frameCount, cv::Mat& image, std::vector<DetectObject>& detects, bool& happen, float& happenScore);


	};
}
#endif //BXC_CONTROLWORKER_H