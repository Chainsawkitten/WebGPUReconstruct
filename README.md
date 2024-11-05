# WebGPUReconstruct
A tool to record web WebGPU content and save it in a capture file. The capture file can then be replayed using native WebGPU ([Dawn](https://dawn.googlesource.com/dawn) or [wgpu](https://github.com/gfx-rs/wgpu-native)). This allows you to use debugging and profiling tools made for the underlying graphics API, such as [RenderDoc](https://renderdoc.org/), [PIX](https://devblogs.microsoft.com/pix/), [Nsight](https://developer.nvidia.com/nsight-graphics), [Radeon GPU Profiler](https://gpuopen.com/rgp/), [Performance Studio](https://developer.arm.com/Tools%20and%20Software/Arm%20Performance%20Studio), etc.

The goal is also to get consistent replays of web content which can be used to test changes to WebGPU implementations without having to build and run the full browser.

## Releases
Binary releases are available for Windows and Android. Get them [here](https://github.com/Chainsawkitten/WebGPUReconstruct/releases).

## Building
If you want to build yourself, instructions are available [here](docs/BUILDING.md).

## Usage
[Capturing content](docs/CAPTURING.md)

[Replaying captures](docs/REPLAYING.md)

Not everything is expected to work. See the [known limitations](docs/LIMITATIONS.md).

## License
WebGPUReconstruct is licensed under the [MIT license](LICENSE).