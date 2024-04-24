﻿#include "Core/Config.h"
#include "Core/Scheduler.h"
#include "Core/Server.h"
#include "Core/Utils/Version.h"
using namespace BXC_Algorithm;

int main(int argc, char** argv)
{
	//testRequest();
	//return 0;

#ifdef WIN32
	srand(time(NULL));//时间初始化
#endif // WIN32

	const char* file = NULL;

	for (int i = 1; i < argc; i += 2)
	{
		if (argv[i][0] != '-')
		{
			printf("parameter error:%s\n", argv[i]);
			return -1;
		}
		switch (argv[i][1])
		{
			case 'h': {
				//打印help信息
				printf("-h 打印参数配置信息并退出\n");
				printf("-f 配置文件    如：-f config.json \n");
				system("pause\n"); 
				exit(0); 
				return -1;
			}
			case 'f': {
				file = argv[i + 1];
				break;
			}
			default: {
				printf("set parameter error:%s\n", argv[i]);
				return -1;

			}
		}
	}
	
	if (file == NULL) {
		printf("failed to read config file\n");
		return -1;
	}
	Config config(file);
	if (!config.read()) {
		printf("failed to read config file: %s\n", file);
		return -1;
	}
	printf("人脸打卡系统 %s \n", PROJECT_VERSION);
	config.show();
	printf("\n");
	printf("\n");

	Scheduler scheduler(&config);
	if (!scheduler.initAlgorithm()) {
		return -1;
	}
	Server server;
	server.start(&scheduler);
	scheduler.loop();

	return 0;
}