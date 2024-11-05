#include <cstdlib>
#include <iostream>
#include <cstring>
#include <GLFW/glfw3.h>
#include "Adapter.hpp"
#include "Device.hpp"
#include "SwapChain.hpp"
#include "TestApp.hpp"

using namespace std;

int main(int argc, char* argv[]) {
    // Configuration.
    bool fullscreen = false;
    int width = 640;
    int height = 480;
    const char* filename = nullptr;
    bool showHelp = false;
    bool profile = false;
    WGPUBackendType backendType = WGPUBackendType_Undefined;
    
    // Parse command line arguments.
    for (int i = 1; i < argc; ++i) {
        if (strcmp("--width", argv[i]) == 0) {
            if (i + 1 < argc) {
                // Read width.
                width = atoi(argv[i + 1]);
                ++i;
            }
        } else if (strcmp("--height", argv[i]) == 0) {
            if (i + 1 < argc) {
                // Read height.
                height = atoi(argv[i + 1]);
                ++i;
            }
        } else if (strcmp("--help", argv[i]) == 0) {
            showHelp = true;
        } else if (strcmp("--fullscreen", argv[i]) == 0) {
            fullscreen = true;
        } else if (strcmp("--vulkan", argv[i]) == 0) {
            backendType = WGPUBackendType_Vulkan;
        } else if (strcmp("--d3d11", argv[i]) == 0) {
            backendType = WGPUBackendType_D3D11;
        } else if (strcmp("--d3d12", argv[i]) == 0) {
            backendType = WGPUBackendType_D3D12;
        } else if (strcmp("--metal", argv[i]) == 0) {
            backendType = WGPUBackendType_Metal;
        } else if (strcmp("--profile", argv[i]) == 0) {
            profile = true;
        } else {
            filename = argv[i];
        }
    }
    
    // If no filename was specified (or user asked for help), print usage instructions.
    if (filename == nullptr || showHelp) {
        cout << "WebGPUNativeReplay [options] filename.wgpur\n";
        cout << "  --help          Show this help screen.\n";
        cout << "  --width  WIDTH  Specify the width of the window.\n";
        cout << "  --height HEIGHT Specify the height of the window.\n";
        cout << "  --fullscreen    Run capture in fullscreen mode.\n";
        cout << "  --vulkan        Request Vulkan backend.\n";
        cout << "  --d3d11         Request Direct3D 11 backend.\n";
        cout << "  --d3d12         Request Direct3D 12 backend.\n";
        cout << "  --metal         Request Metal backend.\n";
        cout << "  --profile       Turn off VSync and measure replay time.\n";
        return 0;
    }
    
    // Create window.
    if (!glfwInit())
        return 1;

    glfwWindowHint(GLFW_CLIENT_API, GLFW_NO_API);
    GLFWmonitor* monitor = fullscreen ? glfwGetPrimaryMonitor() : nullptr;
    
    WebGPUNativeReplay::Window window;
    window.window = glfwCreateWindow(width, height, "WebGPU Native Replay", monitor, nullptr);
    if (!window.window) {
        cerr << "Failed to create window.\n";
        glfwTerminate();
        return 1;
    }

    // Start replay.
    {
        WebGPUNativeReplay::TestApp testApp(window, width, height, backendType, profile);
        testApp.RunCapture(filename);
    }

    glfwDestroyWindow(window.window);
    glfwTerminate();
    
    return 0;
}
