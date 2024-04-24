#ifndef BXC_CONFIG_H
#define BXC_CONFIG_H

#include <string>
#include <vector>

namespace BXC_Algorithm {
	class Config
	{
	public:
		explicit Config(const char* file);
		~Config();
	public:
		bool read();
		void show();
	public:
		const char* file = nullptr;
		int number = 0;

		std::string host{};//主机IP地址 127.0.0.1
		int adminPort;// 后台管理服务端口 9001
		std::string adminHost{};//后台管理服务地址 http://192.168.1.4:9001
		int analyzerPort;// 分析服务端口 9002
		std::string analyzerHost{};//分析器服务地址 http://192.168.1.4:9002

		int mediaHttpPort;// 80
		int mediaRtspPort;// 554
		std::string mediaSecret;//流媒体服务安全密钥
		std::string mediaHttpHost{};//流媒体Http服务地址 http://192.168.1.4:9003
		std::string mediaRtspHost{};//流媒体Rtsp服务地址 http://192.168.1.4:9554

		std::string uploadDir{};//上传路径
		std::string algorithmName{};//算法名称
		std::string algorithmDevice{};//算法设备

		int maxConcurrency = 10000;// 布控最大并发数（默认10000，默认等于不限制数量）
		bool supportHardwareVideoDecode = false;
		bool supportHardwareVideoEncode = false;
	};
}
#endif //BXC_CONFIG_H