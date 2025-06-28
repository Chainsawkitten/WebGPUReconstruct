#pragma once

#if WEBGPU_BACKEND_DAWN
#include <dawn/webgpu.h>

typedef WGPUPassTimestampWrites WGPUComputePassTimestampWrites;
typedef WGPUPassTimestampWrites WGPURenderPassTimestampWrites;
#endif

#if WEBGPU_BACKEND_WGPU
#include <wgpu.h>

inline void wgpuDeviceTick(WGPUDevice device) {
    wgpuDevicePoll(device, false, nullptr);
}

// Dummy struct for external textures until they are added to wgpu.
typedef struct {
    WGPUChainedStruct chain;
} WGPUExternalTextureBindingLayout;
#define WGPUSType_ExternalTextureBindingLayout WGPUSType_Force32
#endif
