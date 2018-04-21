
#pragma once


#include <scheduler/ITaskScheduler.h>

namespace services {
    class ImageTaskScheduler : public ITaskScheduler{
    public:
        ImageTaskScheduler(std::unique_ptr<ITaskPublisher> publisher) : ITaskScheduler(std::move(publisher)) {}

        ITaskScheduler* Clone() const override {
            return new ImageTaskScheduler(std::unique_ptr<ITaskPublisher>(publisher->Clone()));
        }

    protected:
        bool IsAppropriateTask(std::shared_ptr<ITask>& task) override {
            return task->GetType() == TaskType::TT_Image;
        }

        void HandleTask(std::shared_ptr<ITask>& task) override {
            if (publisher) {
                publisher->Send(task);
            }
        }
    };
}

