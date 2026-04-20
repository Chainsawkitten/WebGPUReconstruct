#pragma once

#include "Window.hpp"
#include "WebGPU.hpp"

namespace WebGPUNativeReplay {

class Adapter {
  public:
    Adapter(const Window& window, WGPUBackendType backendType);
    ~Adapter();

    WGPUInstance GetInstance();
    WGPUAdapter GetAdapter();
    WGPUSurface GetSurface();

    uint32_t GetSubgroupMinSize() const;
    uint32_t GetSubgroupMaxSize() const;

  private:
    WGPUInstance instance;
    WGPUSurface surface;
    WGPUAdapter adapter;

    uint32_t subgroupMinSize;
    uint32_t subgroupMaxSize;

    void InitializeBackend();
    void CreateInstance();
    void CreateSurface(const Window& window);
    void RequestAdapter(WGPUBackendType backendType);

    Adapter() = delete;
    Adapter(const Adapter&) = delete;
    Adapter& operator=(const Adapter&) = delete;
};

}
