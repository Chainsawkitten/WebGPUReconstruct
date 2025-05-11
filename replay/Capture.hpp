#pragma once

#include "../../replay/Uint8Reader.hpp"
#include "../../replay/WebGPU.hpp"
#include <string>
#include <string_view>
#include <unordered_map>
#include <map>
#include <mutex>

namespace WebGPUNativeReplay {

class Adapter;
class Device;
class SwapChain;

class Capture {
  public:
    enum class Status {
        FRAME_START,
        FRAME_END,
        COMMAND,
        END_OF_CAPTURE
    };
    
    Capture(std::string_view filename, Adapter& adapter, Device& device, SwapChain& swapChain, bool offscreen);
    ~Capture();

    bool IsValid() const;
    Status RunNextCommand();

    struct CanvasSize {
        enum class State {
            NONE,
            SINGLE,
            MULTIPLE
        };
        State state = State::NONE;
        uint32_t width;
        uint32_t height;
    };

    const CanvasSize& GetCanvasSize() const;
    
    uint32_t GetVersionMajor() const;
    uint32_t GetVersionMinor() const;

  private:
    Adapter& adapter;
    Device& device;
    SwapChain& swapChain;
    bool offscreen;

    Uint8Reader reader;
    
    // Generated maps that map ID -> WebGPU object will be inserted here.
$MAPS

    // Generated functions for loading and clearing structs will be inserted here.
$STRUCT_FUNCTION_DECLARATIONS

    struct CanvasTexture {
        WGPUTexture texture = nullptr;
        uint32_t usage = 0;
        WGPUTextureFormat format = WGPUTextureFormat_Undefined;
        uint32_t width = 0;
        uint32_t height = 0;
        uint64_t viewFormatCount = 0;
        WGPUTextureFormat* viewFormats = nullptr;
    };
    std::map<uint32_t, CanvasTexture> canvasTextures;
    CanvasSize canvasSize;

    std::unordered_map<uint32_t, bool> bufferMapState;
    std::mutex bufferMapStateLock;

    bool valid = true;
    uint32_t versionMajor = 0;
    uint32_t versionMinor = 0;
    bool hasBegun = false;
    WGPUShaderModule copyVertexShader;
    WGPUShaderModule copyFragmentShader;
    WGPURenderPipeline copyRenderPipeline;
    WGPUSampler sampler;
    
    void DebugOutput(std::string text);
    void ErrorOutput(std::string text);
    
    void AddCanvasSize(uint32_t width, uint32_t height);
    void WaitForBufferMapping(uint32_t bufferID);
    
    template <class T>
    T GetIdType(std::unordered_map<uint32_t, T>& m, uint32_t id) {
        if (id == 0) {
            return nullptr;
        }
        return m[id];
    }
    
    template <class T>
    T* LoadStructPointer(void (Capture::*loadMethod)(T*)) {
        if (reader.ReadUint8()) {
            T* value = new T;
            (this->*loadMethod)(value);
            return value;
        }
        
        return nullptr;
    }

    Capture() = delete;
    Capture(const Capture&) = delete;
    Capture& operator=(const Capture&) = delete;
};

}
