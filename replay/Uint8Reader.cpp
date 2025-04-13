#include "Uint8Reader.hpp"

#include "Logging.hpp"

using namespace std;

namespace WebGPUNativeReplay {

Uint8Reader::Uint8Reader(string_view filename) {
    file.open(filename.data(), ios_base::in | ios_base::binary);
    
    if (!file.good()) {
        Logging::Error("Failed to open file: " + std::string(filename) + "\n");
        exit(1);
    }
}

Uint8Reader::~Uint8Reader() {
    file.close();
}

uint8_t Uint8Reader::ReadUint8() {
    constexpr size_t size = sizeof(uint8_t);
    char a[size];
    file.read(a, size);
    return *reinterpret_cast<uint8_t*>(a);
}

uint16_t Uint8Reader::ReadUint16() {
    constexpr size_t size = sizeof(uint16_t);
    char a[size];
    file.read(a, size);
    return *reinterpret_cast<uint16_t*>(a);
}

uint32_t Uint8Reader::ReadUint32() {
    constexpr size_t size = sizeof(uint32_t);
    char a[size];
    file.read(a, size);
    return *reinterpret_cast<uint32_t*>(a);
}

uint64_t Uint8Reader::ReadUint64() {
    constexpr size_t size = sizeof(uint64_t);
    char a[size];
    file.read(a, size);
    return *reinterpret_cast<uint64_t*>(a);
}

int32_t Uint8Reader::ReadInt32() {
    constexpr size_t size = sizeof(int32_t);
    char a[size];
    file.read(a, size);
    return *reinterpret_cast<int32_t*>(a);
}

float Uint8Reader::ReadFloat32() {
    constexpr size_t size = sizeof(float);
    char a[size];
    file.read(a, size);
    return *reinterpret_cast<float*>(a);
}

double Uint8Reader::ReadFloat64() {
    constexpr size_t size = sizeof(double);
    char a[size];
    file.read(a, size);
    return *reinterpret_cast<double*>(a);
}

void Uint8Reader::ReadBuffer(uint8_t* buffer, uint64_t size) {
    file.read(reinterpret_cast<char*>(buffer), size);
}

WGPUStringView Uint8Reader::ReadString() {
    WGPUStringView value = { nullptr, WGPU_STRLEN };
    uint64_t stringLength = ReadUint64();
    if (stringLength > 0) {
        value.data = new char[stringLength];
        ReadBuffer(reinterpret_cast<uint8_t*>(const_cast<char*>(value.data)), stringLength);
        value.length = stringLength;
    }
    return value;
}

}
