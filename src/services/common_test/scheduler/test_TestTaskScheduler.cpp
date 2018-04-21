
#include <boost/test/unit_test.hpp>
#include <network/protocol/JSONProtocol.h>
#include <network/publisher/TestTaskPublisher.h>
#include <task/TestTask.h>
#include "task/TestInappropriateTask.h"
#include "TestTaskScheduler.h"

BOOST_AUTO_TEST_SUITE(TestTaskScheduler)

    void OnResult(services::ITaskResult* forExternalSaving, services::ITaskResult res) {
        *forExternalSaving = res;
    }

    BOOST_AUTO_TEST_CASE(inappropriative_task) {
        auto publisher = std::make_unique<services::TestTaskPublisher>(std::make_unique<services::JSONProtocol>());
        services::TestTaskScheduler scheduler(std::move(publisher));
        scheduler.Run();
        services::ITaskResult res;
        services::ResponseCallback callback = std::bind(OnResult, &res, std::placeholders::_1);
        services::TaskHeader header(services::TaskType::TT_TestInappropriate, callback);
        auto task = std::make_shared<services::TestInappropriateTask>(header);
        BOOST_CHECK_EQUAL(scheduler.AddTask(task),
                          services::AddTaskResult::ATR_Success);
        std::this_thread::sleep_for(std::chrono::milliseconds(300));
//        scheduler.Stop();
        BOOST_CHECK_EQUAL(res.GetId(),  task->GetId() );
        BOOST_CHECK_EQUAL(res.GetStatus(), services::TaskResultStatus::TRS_InappropriateTask);
    }

    BOOST_AUTO_TEST_CASE(add_tasks_multithreaded) {
        const size_t SENDERS_NUMBER = 20;
        const size_t SENDS_PER_THREAD = 10;

        auto publisher = std::make_unique<services::TestTaskPublisher>(std::make_unique<services::JSONProtocol>());
        services::TestTaskScheduler scheduler(std::move(publisher));
        scheduler.Run();
        services::ITaskResult res;
        services::ResponseCallback callback = std::bind(OnResult, &res, std::placeholders::_1);
        services::TaskHeader hdr (services::TT_Test, callback);

        std::vector<std::thread> threads;
        auto threadRoutine = [SENDS_PER_THREAD, hdr](services::TestTaskScheduler& scheduler){
            for (size_t i = 0; i < SENDS_PER_THREAD; ++i) {
                auto task = std::make_shared<services::TestTask>(hdr);
                BOOST_CHECK_EQUAL(scheduler.AddTask(task), services::AddTaskResult::ATR_Success);
            }
        };
        for (int i = 0; i < SENDERS_NUMBER; ++i) {
            threads.emplace_back(threadRoutine, std::ref(scheduler));
        }
        for (auto& thread : threads) thread.join();
        std::this_thread::sleep_for(std::chrono::milliseconds(300));
    }

    BOOST_AUTO_TEST_CASE(no_callback_set) {
        auto publisher = std::make_unique<services::TestTaskPublisher>(std::make_unique<services::JSONProtocol>());
        services::TestTaskScheduler scheduler(std::move(publisher));
        scheduler.Run();
        BOOST_CHECK_EQUAL(scheduler.AddTask(std::make_shared<services::FinishTask>()),
                          services::AddTaskResult::ATR_ResponseCallbackNotSet);
    }

BOOST_AUTO_TEST_SUITE_END()
