# Limitations

## iframe
Capturing content in an `<iframe>` is not supported. Instead, navigate directly to the page the `<iframe>` is embedding and capture it directly.

## Web workers
Since workers run in a separate context, WebGPUReconstruct is not able to capture any of their WebGPU calls. Content using WebGPU from a worker will not work. (Using workers for non-WebGPU tasks should work.)

## Unsupported features
The following optional WebGPU features are not supported:
- `dual-source-blending`
- `texture-formats-tier1`

During capture, `GPUAdapter` will behave as if these features are not supported, even if the device supports them.

The following properties are not supported:
- `GPURenderPassDescriptor.maxDrawCount`
- `GPUShaderModuleDescriptor.compilationHints`

These properties will be treated as if they were set to `undefined`. Setting an unsupported property will give you a warning during capture (but not during replay).

The following methods are not supported:
- `GPUDevice.importExternalTexture()` and everything else related to external textures

Calling any of these methods will give you a warning during both capture and replay.

## Object lifetimes
During replay, all GPU objects will be kept alive for the entire duration of the capture. This is because, afaik, there is no way to know when JavaScript objects are garbage collected so I can't know when objects should be destroyed. It would be possible to at least destroy objects that are explicitly destroyed with the `destroy` method. However, this has not yet been implemented.

Do *not* use WebGPUReconstruct to profile memory usage as it will not be representative.

## Labels
WebGPUReconstruct records the `label` supplied with the `GPUObjectDescriptorBase` when creating an object. However, it will ignore any changes to a `GPUObject`'s `label` after creation.

## Performance
The goal is for WebGPUReconstruct to have representative performance when replaying a capture (making profiling of captures useful). However, it is *not* representative for profiling memory usage.

It is *not* a goal for WebGPUReconstruct not to affect performance when taking captures. Having the browser extension active *will* affect both CPU and GPU performance. It is recommended to disable the extension during regular web browsing and only enable it when you want to capture something. See the [capturing instructions](CAPTURING.md) for how to do this.