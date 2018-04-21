#include <boost/test/unit_test.hpp>
#include <iostream>
#include <sstream>
#include <task/TestTaskWithAdditionalField.h>
#include <unordered_set>
#include <dispatcher/TaskDispatcher.h>
#include <network/publisher/TestTaskPublisher.h>
#include <scheduler/TestTaskScheduler.h>
#include "task/TestTask.h"
#include "network/protocol/JSONProtocol.h"
#include "network/publisher/BoostAsioTaskPublisher.h"

BOOST_AUTO_TEST_SUITE(test_WholeServiceSystem)
    using namespace services;

    std::unique_ptr<ITaskPublisher> MakePublisher(){
        return std::make_unique<BoostAsioTaskPublisher>(std::make_unique<services::JSONProtocol>());
    }

    std::unique_ptr<ITaskScheduler> MakeSchedluler(){
        return std::make_unique<TestTaskScheduler>(MakePublisher());
    }

    BOOST_AUTO_TEST_CASE(test_service_system_from_TaskDispatcher) {
        TaskDispatcher taskDispatcher;

//        auto factory = std::make_unique<SchedulerFactory>();
//        auto executorDispatcher = std::make_unique<ExecutorDispatcher>();
//        taskDispatcher.Register(TaskType::TT_Test, executorDispatcher);
//
//        auto publisher = std::make_unique<services::TestTaskPublisher>(std::make_unique<services::JSONProtocol>());
//        services::TestTaskScheduler scheduler(std::move(publisher));
//        scheduler.Run();
//        services::ITaskResult res;
//        services::ResponseCallback callback = std::bind(OnResultRecieve, &res, std::placeholders::_1);
//        services::TaskHeader header(services::TaskType::TT_TestInappropriate, callback);
//        auto task = std::make_shared<services::TestInappropriateTask>(header);
//        BOOST_CHECK_EQUAL(scheduler.AddTask(task),
//                          services::AddTaskResult::ATR_Success);
//        std::this_thread::sleep_for(std::chrono::milliseconds(300));
////        scheduler.Stop();
//        BOOST_CHECK_EQUAL(res.GetId(),  task->GetId() );
//        BOOST_CHECK_EQUAL(res.GetStatus(), services::TaskResultStatus::TRS_InappropriateTask);
    }

    BOOST_AUTO_TEST_CASE(no_callback_set) {
        auto publisher = std::make_unique<services::TestTaskPublisher>(std::make_unique<services::JSONProtocol>());
        services::TestTaskScheduler scheduler(std::move(publisher));
        scheduler.Run();
        BOOST_CHECK_EQUAL(scheduler.AddTask(std::make_shared<services::FinishTask>()),
                          services::AddTaskResult::ATR_ResponseCallbackNotSet);
    }

BOOST_AUTO_TEST_SUITE_END()

