﻿#ifndef BXC_SCHEDULER_H
#define BXC_SCHEDULER_H
#include <map>
#include <mutex>
#include <condition_variable>
#include <queue>
#include <vector>
#include <thread>

namespace BXC_Algorithm {
	class Config;
	class Worker;
	class Algorithm;
	struct Control;

	class Scheduler
	{
	public:
		friend class Worker;

		Scheduler(Config* config);
		~Scheduler();
	public:
		Config* getConfig();

		bool initAlgorithm();
		Algorithm* gainAlgorithm();
		void giveBackAlgorithm(Algorithm*);
		void loop();


		void setState(bool state);
		bool getState();

		// ApiServer 对应的函数 start
		int  apiControls(std::vector<Control*>& controls);
		Control* apiControl(std::string& code);
		void apiControlAdd(Control* control, int& result_code, std::string& result_msg);
		void apiControlCancel(Control* control, int& result_code, std::string& result_msg);
		// ApiServer 对应的函数 end

	private:
		Config* mConfig;
		Algorithm* mAlgorithm = nullptr;
		std::mutex mAlgorithmMtx;

		bool  mState;

		std::map<std::string, Worker*> mWorkerMap; // <control.code,Worker*>
		std::mutex                     mWorkerMapMtx;
		int  getWorkerSize();
		bool isAdd(Control* control);
		bool addWorker(Control* control, Worker* worker);
		bool removeWorker(Control* control);//加入到待实际删除队列
		Worker* getWorker(Control* control);

		std::queue<Worker*> mTobeDeletedWorkerQ;
		std::mutex               mTobeDeletedWorkerQ_mtx;
		std::condition_variable  mTobeDeletedWorkerQ_cv;
		void handleDeleteWorker();

	};
}
#endif //BXC_SCHEDULER_H