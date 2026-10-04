#include <iostream>
#include <GLFW/glfw3.h>
#include "Adapter.hpp"
#include "../build/replay/Constants.hpp"
#include "Device.hpp"
#include "SwapChain.hpp"
#include "TestApp.hpp"
#include "Configuration.hpp"

using namespace std;

int main(int argc, char* argv[]) {
    // Parse command line arguments.
    std::vector<std::string> arguments;
    for (int i = 1; i < argc; ++i) {
        arguments.push_back(argv[i]);
    }

    WebGPUNativeReplay::Configuration configuration(arguments);
    
    // Show version information.
    if (configuration.showVersion) {
        WebGPUNativeReplay::Configuration::ShowVersion();
        return 0;
    }

    // If no filename was specified (or user asked for help), print usage instructions.
    if (configuration.filename.empty() || configuration.showHelp) {
        WebGPUNativeReplay::Configuration::ShowHelp();
        return 0;
    }
    
    // Create window.
    if (!glfwInit())
        return 1;

    glfwWindowHint(GLFW_CLIENT_API, GLFW_NO_API);
    GLFWmonitor* monitor = configuration.fullscreen ? glfwGetPrimaryMonitor() : nullptr;
    
    WebGPUNativeReplay::Window window;
    window.window = glfwCreateWindow(configuration.width, configuration.height, "WebGPU Native Replay", monitor, nullptr);
    if (!window.window) {
        cerr << "Failed to create window.\n";
        glfwTerminate();
        return 1;
    }

    // Start replay.
    bool success = true;
    {
        WebGPUNativeReplay::TestApp testApp(window, configuration);
        success = testApp.RunCapture(configuration.filename, [&window]() {
            glfwPollEvents();
            return !glfwWindowShouldClose(window.window);
        });
    }

    glfwDestroyWindow(window.window);
    glfwTerminate();
    
    return success ? 0 : 1;
}
