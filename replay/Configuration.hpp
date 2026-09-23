#pragma once

#include "WebGPU.hpp"

#include <vector>
#include <string>

namespace WebGPUNativeReplay {

class Configuration {
  public:
    explicit Configuration(const std::vector<std::string>& arguments);

    static void ShowVersion();
    static void ShowHelp();
    static std::string GetImplementationVersion();

    bool fullscreen = false;
    int width = 640;
    int height = 480;
    std::string filename = "";
    std::string statsFile = "";
    bool showHelp = false;
    bool showVersion = false;
    bool mailbox = false;
    bool offscreen = false;
    bool verifyReadbacks = false;
    WGPUBackendType backendType = WGPUBackendType_Undefined;
};

}
