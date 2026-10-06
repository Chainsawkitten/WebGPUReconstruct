#pragma once

#include "WebGPU.hpp"

namespace WebGPUNativeReplay {

class Adapter;

class Device {
  public:
    explicit Device(Adapter& adapter);
    ~Device();

    WGPUDevice GetDevice();
    WGPUQueue GetQueue();
    bool HasError() const;

  private:
    WGPUDevice device;
    WGPUQueue queue;
    bool error = false;

    Device() = delete;
    Device(const Device&) = delete;
    Device& operator=(const Device&) = delete;
};

}
