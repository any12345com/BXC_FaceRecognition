#ifndef BXC_ALGORITHMOPENCV_H
#define BXC_ALGORITHMOPENCV_H

#include <string>
#include <vector>
#include <mutex>
#include <queue>
#include "Algorithm.h"
#include <opencv2/dnn.hpp>
#include <opencv2/imgproc.hpp>
#include <opencv2/highgui.hpp>

namespace BXC_Algorithm {
	class Config;

	class AlgorithmOpenCV : public Algorithm
	{
	public:
		AlgorithmOpenCV(Config* config);
		virtual ~AlgorithmOpenCV();
	public:
		virtual bool objectDetect(int height, int width, cv::Mat& image, std::vector<DetectObject>& detects);

	private:
		cv::Mat resize_image(cv::Mat srcimg, int* newh, int* neww, int* padh, int* padw);
		const bool keep_ratio = true;
		const int inpWidth = 640;
		const int inpHeight = 640;
		float confThreshold;
		float nmsThreshold;
		const int num_class = 1;  ///只有人脸这一个类别
		const int reg_max = 16;
		cv::dnn::Net net;
		void softmax_(const float* x, float* y, int length);
		void generate_proposal(cv::Mat out, std::vector<cv::Rect>& boxes, std::vector<float>& confidences, std::vector<std::vector<cv::Point>>& landmarks, int imgh, int imgw, float ratioh, float ratiow, int padh, int padw);
		void drawPred(float conf, int left, int top, int right, int bottom, cv::Mat& frame, std::vector<cv::Point> landmark);
	};


}
#endif //BXC_ALGORITHMOPENCV_H

