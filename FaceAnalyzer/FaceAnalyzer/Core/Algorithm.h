#ifndef BXC_ALGORITHM_H
#define BXC_ALGORITHM_H

#include <string>
#include <vector>
#include <opencv2/opencv.hpp>    //opencv header file

namespace BXC_Algorithm {

	class Config;
	struct DetectObject
	{
		int x1;
		int y1;
		int x2;
		int y2;
		float score;
		std::string class_name;
	};

    class Algorithm
    {
    public:
        Algorithm() = delete;
        Algorithm(Config* config);
        virtual ~Algorithm();
    public:
        virtual bool objectDetect(int height, int width, cv::Mat &image, std::vector<DetectObject>& detects) = 0;
    protected:
        Config* mConfig;

    };

}
#endif //BXC_ALGORITHM_H

