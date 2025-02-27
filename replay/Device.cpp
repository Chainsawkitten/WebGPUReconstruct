#include "Device.hpp"
#include "Adapter.hpp"
#include "Logging.hpp"

#include <atomic>
#include <string_view>
#include <thread>
#include <vector>

namespace WebGPUNativeReplay {

Device::Device(Adapter& adapter) {
    // Query features.
    std::vector<WGPUFeatureName> features;

    std::vector<WGPUFeatureName> desiredFeatures = {
        WGPUFeatureName_DepthClipControl,
        WGPUFeatureName_Depth32FloatStencil8,
        WGPUFeatureName_TimestampQuery,
        WGPUFeatureName_TextureCompressionBC,
#if WEBGPU_BACKEND_WGPU
        WGPUFeatureName_TextureCompressionBCSliced3D,
#endif
        WGPUFeatureName_TextureCompressionETC2,
        WGPUFeatureName_TextureCompressionASTC,
#if WEBGPU_BACKEND_WGPU
        WGPUFeatureName_TextureCompressionASTCSliced3D,
#endif
        WGPUFeatureName_IndirectFirstInstance,
        WGPUFeatureName_ShaderF16,
        WGPUFeatureName_RG11B10UfloatRenderable,
        WGPUFeatureName_BGRA8UnormStorage,
        WGPUFeatureName_Float32Filterable,
        WGPUFeatureName_Float32Blendable,
        WGPUFeatureName_ClipDistances
    };
    for (WGPUFeatureName feature : desiredFeatures) {
        if (wgpuAdapterHasFeature(adapter.GetAdapter(), feature)) {
            features.push_back(feature);
        }
    }

    // Query limits.
    WGPUSupportedLimits supportedLimits = {};
    wgpuAdapterGetLimits(adapter.GetAdapter(), &supportedLimits);

    WGPURequiredLimits requiredLimits = {};
#if WEBGPU_BACKEND_DAWN
    requiredLimits.limits = supportedLimits.limits;
#else
    requiredLimits = supportedLimits;
#endif

    WGPUDeviceDescriptor deviceDescriptor = {};
    deviceDescriptor.requiredFeatureCount = features.size();
    deviceDescriptor.requiredFeatures = features.data();
    deviceDescriptor.requiredLimits = &requiredLimits;

#if WEBGPU_BACKEND_DAWN
    deviceDescriptor.deviceLostCallbackInfo2.mode = WGPUCallbackMode_WaitAnyOnly;
    deviceDescriptor.deviceLostCallbackInfo2.callback = [](const WGPUDevice* device, WGPUDeviceLostReason reason, WGPUStringView message, void* userdata1, void* userdata2) {
        Logging::Error("Device lost " + std::to_string(reason) + ": " + std::string(std::string_view(message.data, message.length)) + "\n");
    };

    deviceDescriptor.uncapturedErrorCallbackInfo2.callback = [](const WGPUDevice* device, WGPUErrorType type, WGPUStringView message, void* userdata1, void* userdata2) {
        Logging::Error("Uncaptured device error " + std::to_string(type) + ": " + std::string(std::string_view(message.data, message.length)) + "\n");
    };
#else
    deviceDescriptor.deviceLostCallbackInfo.mode = WGPUCallbackMode_WaitAnyOnly;
    deviceDescriptor.deviceLostCallbackInfo.callback = [](const WGPUDevice* device, WGPUDeviceLostReason reason, WGPUStringView message, void* userdata1, void* userdata2) {
        Logging::Error("Device lost " + std::to_string(reason) + ": " + std::string(std::string_view(message.data, message.length)) + "\n");
    };

    deviceDescriptor.uncapturedErrorCallbackInfo.callback = [](const WGPUDevice* device, WGPUErrorType type, WGPUStringView message, void* userdata1, void* userdata2) {
        Logging::Error("Uncaptured device error " + std::to_string(type) + ": " + std::string(std::string_view(message.data, message.length)) + "\n");
    };
#endif

#if WEBGPU_BACKEND_DAWN
    // Make sure debug labels are forwarded.
    std::vector<const char*> toggles;
    toggles.push_back("use_user_defined_labels_in_backend");
    toggles.push_back("use_dxc");

    WGPUDawnTogglesDescriptor dawnToggles = {};
    dawnToggles.chain.sType = WGPUSType_DawnTogglesDescriptor;
    dawnToggles.enabledToggles = toggles.data();
    dawnToggles.enabledToggleCount = toggles.size();

    deviceDescriptor.nextInChain = reinterpret_cast<const WGPUChainedStruct*>(&dawnToggles);
#endif

    struct UserData {
        WGPUDevice device;
        std::atomic<bool> finished = false;
    };
    UserData userData;

    WGPURequestDeviceCallbackInfo2 callbackInfo = {};
    callbackInfo.mode = WGPUCallbackMode_AllowSpontaneous;
    callbackInfo.callback = [](WGPURequestDeviceStatus status, WGPUDevice device, WGPUStringView message, void* userdata1, void* userdata2) {
        UserData* userData = reinterpret_cast<UserData*>(userdata1);
        userData->device = device;
        userData->finished = true;
    };
    callbackInfo.userdata1 = &userData;

    wgpuAdapterRequestDevice2(adapter.GetAdapter(), &deviceDescriptor, callbackInfo);

    // Wait for request to finish.
    while (!userData.finished) {
        std::this_thread::yield();
    }

    device = userData.device;

    // Get queue.
    queue = wgpuDeviceGetQueue(device);
}

Device::~Device() {
    wgpuDeviceRelease(device);
}

WGPUDevice Device::GetDevice() {
    return device;
}

WGPUQueue Device::GetQueue() {
    return queue;
}

}
