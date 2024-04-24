﻿#include "AlgorithmOpenVINO.h"
#include "Config.h"
#include "Utils/Log.h"
#include "Utils/Common.h"


namespace BXC_Algorithm {
    static std::vector<cv::Scalar> colors = {
        cv::Scalar(0, 0, 255) ,
        cv::Scalar(0, 255, 0) ,
        cv::Scalar(255, 0, 0) ,
        cv::Scalar(255, 100, 50) ,
        cv::Scalar(50, 100, 255) ,
        cv::Scalar(255, 50, 100)
    };

    // Keep the ratio before resize
    static cv::Mat letterbox(const cv::Mat& source)
    {
        int col = source.cols;
        int row = source.rows;
        int _max = MAX(col, row);
        cv::Mat result = cv::Mat::zeros(_max, _max, CV_8UC3);
        source.copyTo(result(cv::Rect(0, 0, col, row)));
        return result;
    }

	AlgorithmOpenVINO::AlgorithmOpenVINO(Config* config):Algorithm(config){
        LOGI("");
		std::string weightDir = config->uploadDir+"/weight";
		std::string modelPath = weightDir + "/yolov8_face_openvino_model/face.xml";

		LOGI("weightDir=%s", weightDir.data());
		LOGI("modelPath=%s", modelPath.data());

        this->core = new ov::Core;
        this->compiled_model = this->core->compile_model(modelPath, mConfig->algorithmDevice);

        this->infer_request = compiled_model.create_infer_request();

    }

	AlgorithmOpenVINO::~AlgorithmOpenVINO()
    {
        LOGI("");
    }

    bool AlgorithmOpenVINO::objectDetect(int height, int width, cv::Mat& image, std::vector<DetectObject>& detects){

        // -------- Step 4.Read a picture file and do the preprocess --------
        // Preprocess the image
        cv::Mat letterbox_img = letterbox(image);

        int letterbox_img_h = letterbox_img.size[0];
        float scale = letterbox_img_h / 640.0;
        cv::Mat blob = cv::dnn::blobFromImage(letterbox_img, 1.0 / 255.0, cv::Size(640, 640), cv::Scalar(), true);

        //int letterbox_img_h = letterbox_img.size[0];
        //float scale = letterbox_img_h / float(1280);
        //cv::Mat blob = cv::dnn::blobFromImage(letterbox_img, 1.0 / 255.0, cv::Size(1280, 1280), cv::Scalar(), true);

        // -------- Step 5. Feed the blob into the input node of the Model -------
        // Get input port for model with one input
        auto input_port = compiled_model.input();
        // Create tensor from external memory
        ov::Tensor input_tensor(input_port.get_element_type(), input_port.get_shape(), blob.ptr(0));

        //std::cout << "start set_input_tensor" << std::endl;



        // Set input tensor for model with one input
        infer_request.set_input_tensor(input_tensor);
        //std::cout << "set_input_tensor success" << std::endl;

        // -------- Step 6. Start inference --------
        infer_request.infer();
        //std::cout << "infer success" << std::endl;

        // -------- Step 7. Get the inference result --------
        auto output = infer_request.get_output_tensor(0);
        auto output_shape = output.get_shape();
        //std::cout << "The shape of output tensor:" << output_shape << std::endl;
        int rows = output_shape[2];        //8400
        int dimensions = output_shape[1];  //84: box[cx, cy, w, h]+80 classes scores

        // -------- Step 8. Postprocess the result --------
        float* data = output.data<float>();
        cv::Mat output_buffer(output_shape[1], output_shape[2], CV_32F, data);
        cv::transpose(output_buffer, output_buffer); //[8400,84]
        float score_threshold = 0.1;
        float nms_threshold = 0.1;
        std::vector<int> class_ids;
        std::vector<float> class_scores;
        std::vector<cv::Rect> boxes;


        // Figure out the bbox, class_id and class_score
        for (int i = 0; i < output_buffer.rows; i++) {
            //cv::Mat classes_scores = output_buffer.row(i).colRange(4, 84);// 1-4对应x,y,w,h。 5-84对应80个分类
            cv::Mat classes_scores = output_buffer.row(i).colRange(4, 5);

            cv::Point class_id;
            double maxClassScore;
            cv::minMaxLoc(classes_scores, 0, &maxClassScore, 0, &class_id);

            if (maxClassScore > score_threshold) {
                class_scores.push_back(maxClassScore);
                class_ids.push_back(class_id.x);
                float cx = output_buffer.at<float>(i, 0);
                float cy = output_buffer.at<float>(i, 1);
                float w = output_buffer.at<float>(i, 2);
                float h = output_buffer.at<float>(i, 3);

                //std::cout << "i=" << i << ",cx=" << cx << ",cy=" << cy << ",w=" << w << ",h=" << h << std::endl;


                int x = int((cx - 0.5 * w) * scale);
                int y = int((cy - 0.5 * h) * scale);
                int width = int(w * scale);
                int height = int(h * scale);

                boxes.push_back(cv::Rect(x,y, width, height));
            }
        }
        //NMS
        std::vector<int> indices;
        cv::dnn::NMSBoxes(boxes, class_scores, score_threshold, nms_threshold, indices);


        if (indices.size() > 0) {
            detects.clear();
            // -------- Visualize the detection results -----------
            for (size_t i = 0; i < indices.size(); i++) {
                int index = indices[i];
                int class_id = class_ids[index];
                cv::Rect rect = boxes[index];
                int x = rect.x;
                int y = rect.y;
                int width = rect.width;
                int height = rect.height;
                DetectObject detect;
                detect.x1 = x;
                detect.y1 = y;
                detect.x2 = x + width;
                detect.y2 = y + height;
                detect.class_name = "face:" + std::to_string(class_id);
                detect.score = class_scores[index];

                detects.push_back(detect);

                cv::rectangle(image, rect, colors[class_id % 6], 2, 8);

                //设置类型背景和文字
                cv::Size textSize = cv::getTextSize(detect.class_name, cv::FONT_HERSHEY_SIMPLEX, 0.5, 1, 0);
                cv::Rect textBox(x, y - 15, textSize.width, textSize.height + 5);
                cv::rectangle(image, textBox, colors[class_id % 6], cv::FILLED);
                putText(image, detect.class_name, cv::Point(x, y - 5),
                    cv::FONT_HERSHEY_SIMPLEX, 0.5, cv::Scalar(255, 255, 255));
            }

            return true;
        }

        return false;
    }

}