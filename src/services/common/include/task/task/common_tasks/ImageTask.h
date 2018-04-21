
#pragma once


#include <task/task/ITask.h>
#include <util/Exceptions.h>

namespace services {
    class ImageTask : public ITask {
    public:
        ImageTask(const TaskHeader& hdr) : ITask(hdr) {
        }

        std::unordered_map<std::string, std::vector<byte>> AdditionalFieldsToSerialize() override {
            std::unordered_map<std::string, std::vector<byte>> map;
            map.insert({"raw_image", rawImage});
            return map;
        }

        bool ParseAdditionalFields(std::unordered_map<std::string, std::vector<byte>> map) override {
            throw NotImplementedException();
        }

        const std::vector<byte>& GetRawImage() const {
            return rawImage;
        }

        void SetRawImage(const std::vector<byte>& rawImage) {
            ImageTask::rawImage = rawImage;
        }

    protected:
        std::vector<byte> rawImage;
    };
}

