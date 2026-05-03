#pragma once

#if WEBGPU_BACKEND_DAWN
#include <dawn/webgpu.h>
#endif

#if WEBGPU_BACKEND_WGPU
#include <wgpu.h>

inline void wgpuDeviceTick(WGPUDevice device) {
    wgpuDevicePoll(device, false, nullptr);
}
#endif
