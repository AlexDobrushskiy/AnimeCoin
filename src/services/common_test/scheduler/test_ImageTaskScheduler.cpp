#include <boost/test/unit_test.hpp>
#include <network/protocol/JSONProtocol.h>
#include <network/publisher/TestTaskPublisher.h>
#include <network/publisher/BoostAsioTaskPublisher.h>
#include <scheduler/common_schedulers/ImageTaskScheduler.h>
#include <task/task/common_tasks/ImageTask.h>
#include <fstream>
#include "task/TestInappropriateTask.h"
#include "TestTaskScheduler.h"

BOOST_AUTO_TEST_SUITE(test_ImageTaskScheduler)

    void OnResultRecieve(services::ITaskResult* forExternalSaving, services::ITaskResult res) {
        *forExternalSaving = res;
    }

    std::vector<services::byte> GetImage() {
        std::string filename = __FILE__;
        filename.replace(filename.begin() + filename.find("test_ImageTaskScheduler.cpp"), filename.end(), "bart.jpg");
        std::vector<services::byte> vec;
        std::ifstream fileStream(filename, std::ifstream::binary);
        if (fileStream) {
            // get length of file:
            fileStream.seekg(0, fileStream.end);
            long length = fileStream.tellg();
            fileStream.seekg(0, fileStream.beg);
            vec = std::vector<services::byte>(length);
            fileStream.read((char*) vec.data(), length);
            fileStream.close();
        }
        return vec;
    }

    void
    SimpleMultipleListenServer(unsigned short port, size_t connectionsCount, std::vector<std::string>& allReceived) {
        typedef std::shared_ptr<boost::asio::ip::tcp::socket> socket_ptr;
        boost::asio::io_service service;
        boost::asio::ip::tcp::endpoint ep(boost::asio::ip::tcp::v4(), port);
        boost::asio::ip::tcp::acceptor acc(service, ep);
        std::vector<std::thread> threads;
        std::vector<std::string> strings(connectionsCount);
        auto ConnectionHandler = [](socket_ptr sock, std::string& receivedData) {
            char data[512];
            std::vector<char> dataVector;
            boost::system::error_code ec;
            long len;
            do {
                len = sock->read_some(boost::asio::buffer(data, 512), ec);
                if (ec && ec.value() != boost::asio::error::eof) {
                    std::cout << ec.message() << std::endl;
                }
                if (len > 0) {
                    dataVector.insert(dataVector.end(), data, data + len);
                } else {
                    break;
                }
            } while (true);
            receivedData = std::string(dataVector.begin(), dataVector.end());
        };
        for (size_t i = 0; i < connectionsCount; ++i) {
            socket_ptr sock(new boost::asio::ip::tcp::socket(service));
            acc.accept(*sock);
            threads.emplace_back(std::thread(ConnectionHandler, sock, std::ref(strings[i])));
        }
        for (auto& thread : threads) thread.join();
        allReceived = strings;
    }

    BOOST_AUTO_TEST_CASE(send_image_success) {
        auto timeout = std::chrono::milliseconds(500);
        unsigned short port = 60000;
        const size_t SENDERS_NUMBER = 10;
        const size_t SENDS_PER_THREAD = 10;
        std::vector<std::thread> threads;
        std::vector<std::string> received;
        std::thread testServer(SimpleMultipleListenServer, port, SENDERS_NUMBER * SENDS_PER_THREAD, std::ref(received));
        auto protocol = std::make_unique<services::JSONProtocol>();
        auto publisher = std::make_unique<services::BoostAsioTaskPublisher>(std::move(protocol));
        publisher->SetRemoteEndPoint("127.0.0.1", 60000);
        services::ImageTaskScheduler scheduler(std::move(publisher));
        bool runSucceded = scheduler.Run();
        BOOST_REQUIRE(runSucceded);
        auto image = GetImage();
        if (image.empty()) {
            BOOST_REQUIRE(0);
        }


        auto senderRoutine = [SENDS_PER_THREAD, image](services::ImageTaskScheduler& scheduler, size_t threadIndex) {
            for (size_t i = 0; i < SENDS_PER_THREAD; ++i) {
                services::ITaskResult res;
                services::ResponseCallback callback = std::bind(OnResultRecieve, &res, std::placeholders::_1);
                services::TaskHeader header(services::TaskType::TT_Image, callback);
                auto task = std::make_shared<services::ImageTask>(header);
                task->SetRawImage(image);

                auto addTaskResult = scheduler.AddTask(task);
                BOOST_CHECK_EQUAL(addTaskResult, services::AddTaskResult::ATR_Success);
            }
        };

        for (int i = 0; i < SENDERS_NUMBER; ++i) {
            threads.emplace_back(senderRoutine, std::ref(scheduler), i);
        }
        for (auto& thread : threads) thread.join();
        std::this_thread::sleep_for(timeout);
        testServer.join();
        scheduler.Stop();
        BOOST_CHECK_EQUAL(received.size(), SENDERS_NUMBER * SENDS_PER_THREAD);
    }

    BOOST_AUTO_TEST_CASE(send_image_all_attempts_exhausted) {
        auto image = GetImage();
        if (image.empty()) {
            BOOST_REQUIRE(0);
        }
        auto publisher = std::make_unique<services::BoostAsioTaskPublisher>(std::make_unique<services::JSONProtocol>());
        services::ImageTaskScheduler scheduler(std::move(publisher));
        bool runSucceded = scheduler.Run();
        services::ITaskResult res;
        services::ResponseCallback callback = std::bind(OnResultRecieve, &res, std::placeholders::_1);
        services::TaskHeader header(services::TaskType::TT_Image, callback);
        auto task = std::make_shared<services::ImageTask>(header);
        task->SetRawImage(image);
        BOOST_CHECK_EQUAL(scheduler.AddTask(task),
                          services::AddTaskResult::ATR_Success);
        std::this_thread::sleep_for(std::chrono::milliseconds(300));
        scheduler.Stop();
        BOOST_CHECK_EQUAL(res.GetId(), task->GetId());
        BOOST_CHECK_EQUAL(res.GetStatus(), services::TaskResultStatus::TRS_AllAttemptsExhausted);
    }


BOOST_AUTO_TEST_SUITE_END()

