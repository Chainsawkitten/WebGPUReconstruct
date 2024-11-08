#include "Capture.hpp"

#include "../../replay/Adapter.hpp"
#include "../../replay/Device.hpp"
#include "../../replay/SwapChain.hpp"
#include <algorithm>
#include <iostream>
#include <cassert>
#include <climits>
#include <cmath>
#include <string>
#include <thread>
#if __ANDROID__
#include <android/log.h>
#endif

using namespace std;

namespace WebGPUNativeReplay {

// These values are used when capturing commands. Ensure they match the C API.
static_assert(WGPU_ARRAY_LAYER_COUNT_UNDEFINED == UINT32_MAX);
static_assert(WGPU_COPY_STRIDE_UNDEFINED == UINT32_MAX);
static_assert(WGPU_DEPTH_SLICE_UNDEFINED == UINT32_MAX);
static_assert(WGPU_MIP_LEVEL_COUNT_UNDEFINED == UINT32_MAX);

// Generated functions to convert enum values will be inserted here.
$ENUM_CONVERSIONS

Capture::Capture(string_view filename, Adapter& adapter, Device& device, SwapChain& swapChain) : reader(filename), adapter(adapter), device(device), swapChain(swapChain) {
    const uint32_t version = reader.ReadUint32();
    if (version != $FILE_VERSION) {
        cerr << "The capture file was saved using a different version of WebGPUReconstruct.\n";
        cerr << "Capture version: " << version << "\n";
        cerr << "WebGPUNativeReplay version: " << $FILE_VERSION << "\n";
        exit(1);
    }
    
    // Create render pipeline to copy "swapchain" texture to actual swapchain texture.
    WGPUShaderModuleWGSLDescriptor wgslDescriptor = {};
    wgslDescriptor.chain.sType = WGPUSType_ShaderModuleWGSLDescriptor;
    wgslDescriptor.code = R"(
struct VertexOutput {
  @builtin(position) Position : vec4f,
  @location(0) fragUV : vec2f,
}

@vertex
fn main(
  @builtin(vertex_index) VertexIndex : u32
) -> VertexOutput {
  var pos = array<vec2f, 3>(
    vec2(-1.0, 3.0),
    vec2(-1.0, -1.0),
    vec2(3.0, -1.0)
  );
  var uv = array<vec2f, 3>(
    vec2(0.0, -1.0),
    vec2(0.0, 1.0),
    vec2(2.0, 1.0)
  );
  
  var output : VertexOutput;
  output.Position = vec4f(pos[VertexIndex], 0.0, 1.0);
  output.fragUV = uv[VertexIndex];

  return output;
}
)";
    
    WGPUShaderModuleDescriptor moduleDescriptor = {};
    moduleDescriptor.nextInChain = reinterpret_cast<const WGPUChainedStruct*>(&wgslDescriptor);
    copyVertexShader = wgpuDeviceCreateShaderModule(device.GetDevice(), &moduleDescriptor);
    
    wgslDescriptor.code = R"(
@group(0) @binding(0) var mySampler: sampler;
@group(0) @binding(1) var myTexture: texture_2d<f32>;

@fragment
fn main(@location(0) fragUV: vec2f) -> @location(0) vec4f {
  return textureSample(myTexture, mySampler, fragUV);
}
)";
    
    copyFragmentShader = wgpuDeviceCreateShaderModule(device.GetDevice(), &moduleDescriptor);
    
    WGPUColorTargetState target = {};
    target.format = swapChain.GetFormat();
    target.writeMask = 0xF;
    
    WGPUFragmentState fragment = {};
    fragment.module = copyFragmentShader;
    fragment.entryPoint = "main";
    fragment.targetCount = 1;
    fragment.targets = &target;
    
    WGPURenderPipelineDescriptor descriptor = {};
    descriptor.vertex.module = copyVertexShader;
    descriptor.vertex.entryPoint = "main";
    descriptor.fragment = &fragment;
    descriptor.primitive.topology = WGPUPrimitiveTopology_TriangleList;
    descriptor.multisample.count = 1;
    descriptor.multisample.mask = 0xFFFFFFFF;
    
    copyRenderPipeline = wgpuDeviceCreateRenderPipeline(device.GetDevice(), &descriptor);
    
    sampler = wgpuDeviceCreateSampler(device.GetDevice(), nullptr);
}

Capture::~Capture() {
    for (const auto &it : canvasTextures) {
        wgpuTextureRelease(it.second.texture);
        if (it.second.viewFormatCount != 0) {
            delete[] it.second.viewFormats;
        }
    }
    
    wgpuRenderPipelineRelease(copyRenderPipeline);
    wgpuShaderModuleRelease(copyVertexShader);
    wgpuShaderModuleRelease(copyFragmentShader);
    wgpuSamplerRelease(sampler);
}

void Capture::DebugOutput(string text) {
#ifndef NDEBUG
#if __ANDROID__
    __android_log_print(ANDROID_LOG_INFO, "WebGPUNativeReplay", "%s", text.c_str());
#else
    cout << text;
#endif
#endif
}

void Capture::ErrorOutput(string text) {
#if __ANDROID__
    __android_log_print(ANDROID_LOG_ERROR, "WebGPUNativeReplay", "%s", text.c_str());
#else
    cerr << text;
#endif
}

bool Capture::RunNextCommand() {
    const uint32_t commandCode = reader.ReadUint32();
    size_t stringLength;

    switch (commandCode) {
    case 0:
        DebugOutput("End of capture reached.\n");
        return false;
    case 1:
        DebugOutput("Start of frame.\n");
        hasBegun = true;
        break;
    case 2:
    {
        // Ignore any "end of frame" before the first "start of frame".
        if (!hasBegun) {
            return true;
        }
        
        DebugOutput("End of frame\n");
        
        if (canvasTextures.empty()) {
            return true;
        }
        
        // Copy our "swapchain" textures to the actual swapchain texture.
        WGPUCommandEncoder encoder = wgpuDeviceCreateCommandEncoder(device.GetDevice(), nullptr);
        
        WGPUTexture swapChainTexture = swapChain.GetCurrentTexture().texture;
        uint32_t swapChainWidth = wgpuTextureGetWidth(swapChainTexture);
        uint32_t swapChainHeight = wgpuTextureGetHeight(swapChainTexture);
        
        WGPURenderPassColorAttachment attachment = {};
        attachment.view = wgpuTextureCreateView(swapChainTexture, nullptr);
        attachment.depthSlice = 0xffffffff;
        attachment.loadOp = WGPULoadOp_Clear;
        attachment.storeOp = WGPUStoreOp_Store;
        attachment.clearValue.r = 0.0;
        attachment.clearValue.g = 0.0;
        attachment.clearValue.b = 0.0;
        attachment.clearValue.a = 1.0;
        
        WGPURenderPassDescriptor renderPassDescriptor = {};
        renderPassDescriptor.colorAttachmentCount = 1;
        renderPassDescriptor.colorAttachments = &attachment;
        
        WGPURenderPassEncoder renderPassEncoder = wgpuCommandEncoderBeginRenderPass(encoder, &renderPassDescriptor);
        wgpuRenderPassEncoderSetPipeline(renderPassEncoder, copyRenderPipeline);
        
        const size_t canvasCount = canvasTextures.size();
        const uint32_t canvasesPerRow = static_cast<uint32_t>(ceil(sqrt(static_cast<double>(canvasCount))));
        const uint32_t rows = static_cast<uint32_t>(ceil(canvasCount / canvasesPerRow));
        const float canvasWidth = static_cast<float>(swapChainWidth) / canvasesPerRow;
        const float canvasHeight = static_cast<float>(swapChainHeight) / rows;
        
        uint32_t i = 0;
        for (const auto &it : canvasTextures) {
            WGPUBindGroupEntry entries[2];
            entries[0] = {};
            entries[0].sampler = sampler;
            entries[1] = {};
            entries[1].binding = 1;
            entries[1].textureView = wgpuTextureCreateView(it.second.texture, nullptr);
            
            WGPUBindGroupDescriptor bindGroupDescriptor = {};
            bindGroupDescriptor.layout = wgpuRenderPipelineGetBindGroupLayout(copyRenderPipeline, 0);
            bindGroupDescriptor.entryCount = 2;
            bindGroupDescriptor.entries = entries;
            
            WGPUBindGroup bindGroup = wgpuDeviceCreateBindGroup(device.GetDevice(), &bindGroupDescriptor);
            wgpuRenderPassEncoderSetBindGroup(renderPassEncoder, 0, bindGroup, 0, nullptr);
            
            const float x = static_cast<float>(i % canvasesPerRow) * canvasWidth;
            const float y = static_cast<float>(i / canvasesPerRow) * canvasHeight;
            wgpuRenderPassEncoderSetViewport(renderPassEncoder, x, y, min(canvasWidth, static_cast<float>(swapChainWidth) - x), min(canvasHeight, static_cast<float>(swapChainHeight) - y), 0.0f, 1.0f);
            wgpuRenderPassEncoderDraw(renderPassEncoder, 3, 1, 0, 0);
            
            wgpuBindGroupRelease(bindGroup);
            wgpuTextureViewRelease(entries[1].textureView);
            ++i;
        }
        
        wgpuRenderPassEncoderEnd(renderPassEncoder);
        wgpuRenderPassEncoderRelease(renderPassEncoder);
        
        WGPUCommandBuffer commandBuffer = wgpuCommandEncoderFinish(encoder, nullptr);
        wgpuCommandEncoderRelease(encoder);
        wgpuQueueSubmit(device.GetQueue(), 1, &commandBuffer);
        
        // Present the swapchain texture.
        wgpuSurfacePresent(adapter.GetSurface());
        
        // Cleanup temporary resources.
        wgpuTextureViewRelease(attachment.view);
        break;
    }
    case 3:
    {
        DebugOutput("unmap\n");
        
        WGPUBuffer buffer = GetIdType(mapGPUBuffer, reader.ReadUint32());
        
        // Make sure the buffer has actually been mapped.
        while (wgpuBufferGetMapState(buffer) != WGPUBufferMapState_Mapped) {
            wgpuDeviceTick(device.GetDevice());
            this_thread::yield();
        }
        
        const uint64_t ranges = reader.ReadUint64();
        for (uint64_t range = 0; range < ranges; ++range) {
            const uint64_t offset = reader.ReadUint64();
            const uint64_t size = reader.ReadUint64();
            
            // Write contents to buffer range.
            uint8_t* bufferContents = reinterpret_cast<uint8_t*>(wgpuBufferGetMappedRange(buffer, offset, size));
            reader.ReadBuffer(bufferContents, size);
        }
        
        wgpuBufferUnmap(buffer);
        break;
    }
    case 4:
    {
        DebugOutput("unmap (read)\n");
        
        WGPUBuffer buffer = GetIdType(mapGPUBuffer, reader.ReadUint32());
        
        // Make sure the buffer has actually been mapped.
        while (wgpuBufferGetMapState(buffer) != WGPUBufferMapState_Mapped) {
            wgpuDeviceTick(device.GetDevice());
            this_thread::yield();
        }
        
        wgpuBufferUnmap(buffer);
        break;
    }
// Generated code will be inserted here.
$RUN_COMMANDS
    default:
        ErrorOutput(string("Unknown command code: ") + to_string(commandCode) + "\n");
        exit(1);
    }

    return true;
}

}
