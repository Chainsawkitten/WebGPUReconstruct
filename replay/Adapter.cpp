#include "Adapter.hpp"

#if WEBGPU_BACKEND_DAWN
#include <dawn/dawn_proc.h>
#include <dawn/native/DawnNative.h>
#endif
#include <atomic>
#include <thread>
#include <string_view>
#include "Logging.hpp"

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
#if !WEBGPU_BACKEND_DAWN
    // TODO Remove Dawn bug workaround.
    wgpuSurfaceRelease(surface);
#endif
    wgpuInstanceRelease(instance);
}

WGPUInstance Adapter::GetInstance() {
    return instance;
}

WGPUAdapter Adapter::GetAdapter() {
    return adapter;
}

WGPUSurface Adapter::GetSurface() {
    return surface;
}

#if WEBGPU_BACKEND_DAWN
uint32_t Adapter::GetSubgroupMinSize() const {
    return subgroupMinSize;
}

uint32_t Adapter::GetSubgroupMaxSize() const {
    return subgroupMaxSize;
}
#endif

void Adapter::InitializeBackend() {
#if WEBGPU_BACKEND_DAWN
    // Initialize Dawn
    DawnProcTable procs = dawn::native::GetProcs();
    dawnProcSetProcs(&procs);
    Logging::Info("Using Dawn backend.\n");
#else
    Logging::Info("Using wgpu backend.\n");
#endif
}

void Adapter::CreateInstance() {
    WGPUInstanceDescriptor instanceDescriptor = {};

#if WEBGPU_BACKEND_WGPU
    WGPUInstanceExtras extras = {};
    extras.chain.sType = static_cast<WGPUSType>(WGPUSType_InstanceExtras);
    extras.flags = WGPUInstanceFlag_Debug;

    instanceDescriptor.nextInChain = reinterpret_cast<WGPUChainedStruct*>(&extras);
#endif

    instance = wgpuCreateInstance(&instanceDescriptor);
}

void Adapter::CreateSurface(const Window& window) {
#if __ANDROID__
    WGPUSurfaceSourceAndroidNativeWindow platformSurfaceSource = {};
    platformSurfaceSource.chain.next = nullptr;
    platformSurfaceSource.chain.sType = WGPUSType_SurfaceSourceAndroidNativeWindow;
    platformSurfaceSource.window = window.window;
#elif defined(_WIN32) || defined(WIN32)
    WGPUSurfaceSourceWindowsHWND platformSurfaceSource = {};
    platformSurfaceSource.chain.next = nullptr;
    platformSurfaceSource.chain.sType = WGPUSType_SurfaceSourceWindowsHWND;
    platformSurfaceSource.hinstance = GetModuleHandle(NULL);
    platformSurfaceSource.hwnd = glfwGetWin32Window(window.window);
#elif __APPLE__
#error "WebGPU surface support has not been implemented on Mac."
    /// @todo Implement WGPUSurfaceSourceMetalLayer
#elif __linux__
    WGPUSurfaceSourceXlibWindow platformSurfaceSource = {};
    platformSurfaceSource.chain.next = nullptr;
    platformSurfaceSource.chain.sType = WGPUSType_SurfaceSourceXlibWindow;
    platformSurfaceSource.display = glfwGetX11Display();
    platformSurfaceSource.window = glfwGetX11Window(window.window);
#else
#error "Unsupported platform"
#endif

    WGPUSurfaceDescriptor surfaceDescriptor = {};
    surfaceDescriptor.nextInChain = reinterpret_cast<WGPUChainedStruct*>(&platformSurfaceSource);

    surface = wgpuInstanceCreateSurface(instance, &surfaceDescriptor);
}

void Adapter::RequestAdapter(WGPUBackendType backendType) {
    WGPURequestAdapterOptions options = {};
    options.backendType = backendType;
    options.compatibleSurface = surface;
    options.forceFallbackAdapter = false;
    options.powerPreference = WGPUPowerPreference_HighPerformance;

#if WEBGPU_BACKEND_DAWN
    // Make sure debug labels are forwarded.
    std::vector<const char*> toggles;
    toggles.push_back("use_user_defined_labels_in_backend");
    toggles.push_back("use_dxc");
    // Needed for experimental features like TextureFormatsTier1 and TextureFormatsTier2
    toggles.push_back("allow_unsafe_apis");

    WGPUDawnTogglesDescriptor dawnToggles = {};
    dawnToggles.chain.sType = WGPUSType_DawnTogglesDescriptor;
    dawnToggles.enabledToggles = toggles.data();
    dawnToggles.enabledToggleCount = toggles.size();

    options.nextInChain = reinterpret_cast<WGPUChainedStruct*>(&dawnToggles);
#endif

    struct UserData {
        WGPUAdapter adapter = nullptr;
        std::atomic<bool> finished = false;
    };
    UserData userData;

    WGPURequestAdapterCallbackInfo callbackInfo = {};
    callbackInfo.mode = WGPUCallbackMode_AllowSpontaneous;
    callbackInfo.callback = [](WGPURequestAdapterStatus status, WGPUAdapter adapter, WGPUStringView message, void* userdata1, void* userdata2) {
        UserData* userData = reinterpret_cast<UserData*>(userdata1);
        userData->adapter = adapter;
        userData->finished = true;
    };
    callbackInfo.userdata1 = &userData;
    wgpuInstanceRequestAdapter(instance, &options, callbackInfo);

    // Wait for request to finish.
    while (!userData.finished) {
        std::this_thread::yield();
    };

    adapter = userData.adapter;

    // Get information about the adapter.
    WGPUAdapterInfo info = {};
    wgpuAdapterGetInfo(adapter, &info);

    const std::string_view deviceName(info.device.data, info.device.length);
    Logging::Info("Selected adapter " + std::string(deviceName) + "\n");

    Logging::Info("Backend type: ");
    switch (info.backendType) {
    case WGPUBackendType_Null:
        Logging::Info("Null.\n");
        break;
    case WGPUBackendType_WebGPU:
        Logging::Info("WebGPU.\n");
        break;
    case WGPUBackendType_D3D11:
        Logging::Info("D3D11.\n");
        break;
    case WGPUBackendType_D3D12:
        Logging::Info("D3D12.\n");
        break;
    case WGPUBackendType_Metal:
        Logging::Info("Metal.\n");
        break;
    case WGPUBackendType_Vulkan:
        Logging::Info("Vulkan.\n");
        break;
    case WGPUBackendType_OpenGL:
        Logging::Info("OpenGL.\n");
        break;
    case WGPUBackendType_OpenGLES:
        Logging::Info("OpenGL ES.\n");
        break;
    }

#if WEBGPU_BACKEND_DAWN
    subgroupMinSize = info.subgroupMinSize;
    subgroupMaxSize = info.subgroupMaxSize;
#endif
}

}
