#include "Adapter.hpp"

#if WEBGPU_BACKEND_DAWN
#include <dawn/dawn_proc.h>
#include <dawn/native/DawnNative.h>
#endif
#include <atomic>
#include <thread>
#include <iostream>

#if __ANDROID__

#else
    #include <GLFW/glfw3.h>
    #if defined(_WIN32) || defined(WIN32)
        #define GLFW_EXPOSE_NATIVE_WIN32
    #elif __APPLE__
        #define GLFW_EXPOSE_NATIVE_COCOA
    #elif __linux__
        /// @todo Wayland?
        #define GLFW_EXPOSE_NATIVE_X11
    #endif
    #include <GLFW/glfw3native.h>
#endif

namespace WebGPUNativeReplay {

Adapter::Adapter(const Window& window, WGPUBackendType backendType) {
    InitializeBackend();
    CreateInstance();
    CreateSurface(window);
    RequestAdapter(backendType);
}

Adapter::~Adapter() {
    wgpuAdapterRelease(adapter);
    wgpuSurfaceRelease(surface);
    wgpuInstanceRelease(instance);
}

WGPUAdapter Adapter::GetAdapter() {
    return adapter;
}

WGPUSurface Adapter::GetSurface() {
    return surface;
}

void Adapter::InitializeBackend() {
#if WEBGPU_BACKEND_DAWN
    // Initialize Dawn
    DawnProcTable procs = dawn::native::GetProcs();
    dawnProcSetProcs(&procs);
    std::cout << "Using Dawn backend.\n";
#else
    std::cout << "Using wgpu backend.\n";
#endif
}

void Adapter::CreateInstance() {
    WGPUInstanceDescriptor instanceDescriptor = {};
    instanceDescriptor.nextInChain = nullptr;

    instance = wgpuCreateInstance(&instanceDescriptor);
}

void Adapter::CreateSurface(const Window& window) {
#if __ANDROID__
    WGPUSurfaceDescriptorFromAndroidNativeWindow platformSurfaceDescriptor = {};
    platformSurfaceDescriptor.chain.next = nullptr;
    platformSurfaceDescriptor.chain.sType = WGPUSType_SurfaceDescriptorFromAndroidNativeWindow;
    platformSurfaceDescriptor.window = window.window;
#elif defined(_WIN32) || defined(WIN32)
    WGPUSurfaceDescriptorFromWindowsHWND platformSurfaceDescriptor = {};
    platformSurfaceDescriptor.chain.next = nullptr;
    platformSurfaceDescriptor.chain.sType = WGPUSType_SurfaceDescriptorFromWindowsHWND;
    platformSurfaceDescriptor.hinstance = GetModuleHandle(NULL);
    platformSurfaceDescriptor.hwnd = glfwGetWin32Window(window.window);
#elif __APPLE__
#error "WebGPU surface support has not been implemented on Mac."
    /// @todo Implement WGPUSurfaceDescriptorFromMetalLayer
#elif __linux__
    WGPUSurfaceDescriptorFromXlibWindow platformSurfaceDescriptor = {};
    platformSurfaceDescriptor.chain.next = nullptr;
    platformSurfaceDescriptor.chain.sType = WGPUSType_SurfaceDescriptorFromXlibWindow;
    platformSurfaceDescriptor.display = glfwGetX11Display();
    platformSurfaceDescriptor.window = glfwGetX11Window(window.window);
#else
#error "Unsupported platform"
#endif

    WGPUSurfaceDescriptor surfaceDescriptor = {};
    surfaceDescriptor.label = nullptr;
    surfaceDescriptor.nextInChain = reinterpret_cast<const WGPUChainedStruct*>(&platformSurfaceDescriptor);

    surface = wgpuInstanceCreateSurface(instance, &surfaceDescriptor);
}

void Adapter::RequestAdapter(WGPUBackendType backendType) {
    WGPURequestAdapterOptions options = {};
    options.backendType = backendType;
    options.compatibleSurface = surface;
    options.forceFallbackAdapter = false;
    options.powerPreference = WGPUPowerPreference_HighPerformance;

    struct UserData {
        WGPUAdapter adapter = nullptr;
        std::atomic<bool> finished = false;
    };
    UserData userData;

    wgpuInstanceRequestAdapter(
        instance, &options, [](WGPURequestAdapterStatus status, WGPUAdapter adapter, char const* message, void* userdata) {
            UserData* userData = reinterpret_cast<UserData*>(userdata);
            userData->adapter = adapter;
            userData->finished = true;
        }, &userData);

    // Wait for request to finish.
    while (!userData.finished) {
        std::this_thread::yield();
    };

    adapter = userData.adapter;

    // Get information about the adapter.
    WGPUAdapterInfo info = {};
    wgpuAdapterGetInfo(adapter, &info);

    std::cout << "Selected adapter " << info.device << "\n";

    std::cout << "Backend type: ";
    switch (info.backendType) {
    case WGPUBackendType_Null:
        std::cout << "Null.\n";
        break;
    case WGPUBackendType_WebGPU:
        std::cout << "WebGPU.\n";
        break;
    case WGPUBackendType_D3D11:
        std::cout << "D3D11.\n";
        break;
    case WGPUBackendType_D3D12:
        std::cout << "D3D12.\n";
        break;
    case WGPUBackendType_Metal:
        std::cout << "Metal.\n";
        break;
    case WGPUBackendType_Vulkan:
        std::cout << "Vulkan.\n";
        break;
    case WGPUBackendType_OpenGL:
        std::cout << "OpenGL.\n";
        break;
    case WGPUBackendType_OpenGLES:
        std::cout << "OpenGL ES.\n";
        break;
    }
}

}
