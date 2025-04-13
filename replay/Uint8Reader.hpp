#pragma once

#include <fstream>
#include <string_view>
#include <cstdint>
#include "WebGPU.hpp"

namespace WebGPUNativeReplay {

class Uint8Reader {
  public:
    explicit Uint8Reader(std::string_view filename);
    ~Uint8Reader();

    uint8_t ReadUint8();
    uint16_t ReadUint16();
    uint32_t ReadUint32();
    uint64_t ReadUint64();
    int32_t ReadInt32();
    float ReadFloat32();
    double ReadFloat64();
    void ReadBuffer(uint8_t* buffer, uint64_t size);
    WGPUStringView ReadString();

  private:
    std::ifstream file;

    Uint8Reader() = delete;
    Uint8Reader(const Uint8Reader&) = delete;
    Uint8Reader& operator=(const Uint8Reader&) = delete;
};

}
