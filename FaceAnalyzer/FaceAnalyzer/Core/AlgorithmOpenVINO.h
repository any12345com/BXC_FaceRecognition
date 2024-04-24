#ifndef BXC_ALGORITHMOPENVINO_H
#define BXC_ALGORITHMOPENVINO_H

#include <string>
#include <vector>
#include "Algorithm.h"
#include <openvino/openvino.hpp> //openvino header file
#include <opencv2/opencv.hpp>    //opencv header file

namespace BXC_Algorithm {
	class Config;

	class AlgorithmOpenVINO : public Algorithm
	{
	public:
		AlgorithmOpenVINO(Config* config);
		virtual ~AlgorithmOpenVINO();
	public:
		virtual bool objectDetect(int height, int width, cv::Mat& image, std::vector<DetectObject>& detects);

	private:
		ov::Core* core = nullptr;
		ov::CompiledModel compiled_model;
		ov::InferRequest  infer_request;

	};


}
#endif //BXC_ALGORITHMOPENVINO_H

