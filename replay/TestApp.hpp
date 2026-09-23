#pragma once

#include "Adapter.hpp"
#include "Device.hpp"
#include "SwapChain.hpp"
#include <string>
#include <string_view>
#include <functional>

namespace WebGPUNativeReplay {

struct Window;
class Configuration;

class TestApp {
  public:
    TestApp(const Window& window, const Configuration& configuration);
    ~TestApp();

    void RunCapture(std::string_view filename, std::function<bool(void)> frameCallback);

  private:
    Adapter adapter;
    Device device;
    SwapChain swapChain;
    bool offscreen = false;
    bool verifyReadbacks = false;
    std::string statsFile;

    TestApp(const TestApp&) = delete;
    TestApp& operator=(const TestApp&) = delete;
};

}
