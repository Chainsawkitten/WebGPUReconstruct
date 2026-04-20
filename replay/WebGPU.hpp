#pragma once

#if WEBGPU_BACKEND_DAWN
#include <dawn/webgpu.h>
#endif

#if WEBGPU_BACKEND_WGPU
#include <wgpu.h>

inline void wgpuDeviceTick(WGPUDevice device) {
    wgpuDevicePoll(device, false, nullptr);
}

// Dummy structs until they are added to wgpu.
typedef struct {
    WGPUChainedStruct chain;
} WGPUTextureBindingViewDimensionDescriptor;
#define WGPUSType_TextureBindingViewDimensionDescriptor WGPUSType_Force32
#endif
