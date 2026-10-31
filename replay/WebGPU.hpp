#pragma once

#if WEBGPU_BACKEND_DAWN
#include <dawn/webgpu.h>
#endif

#if WEBGPU_BACKEND_WGPU
#include <wgpu.h>

inline void wgpuDeviceTick(WGPUDevice device) {
    wgpuDevicePoll(device, false, nullptr);
}

#define WGPUVertexFormat_Snorm10_10_10_2 WGPUVertexFormat_Force32

#endif
