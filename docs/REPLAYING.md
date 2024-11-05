# Replaying captures
This page assumes you already have a `.wgpur` capture to replay. For instructions on how to record a capture, see [capturing content](CAPTURING.md).

## Desktop
WebGPUReconstruct provides two native replayer executables, one for each backend: `WebGPUNativeReplayDawn` and `WebGPUNativeReplayWgpu`. To replay a capture, simply run the executable from the command line and specify the path to the capture file, eg.:

```
./WebGPUNativeReplayDawn capture.wgpur
```

By default, a window of size 640x480 will be used. To specify a different size, use:

```
./WebGPUNativeReplayDawn capture.wgpur --width WIDTH --height HEIGHT
```

Use `--help` to see more options.

### Why do I need to manually specify the width and height?
It would be nice if the size of the window could automatically match that of the captured canvas. However, this is not as simple as it may initially appear. WebGPUReconstruct supports capturing WebGPU content using [multiple canvases](https://webgpu.github.io/webgpu-samples/sample/multipleCanvases/) or where the canvas size [changes at runtime](https://webgpu.github.io/webgpu-samples/sample/resizeCanvas/). In addition, on Android the application is not responsible for creating the window, it is simply handed a window by the OS. This makes things more complicated. I would definitely like to have something more user friendly while still supporting all those features, but for now you have to manually specify the window dimensions.

### Requesting a specific backend
You can use `--vulkan`, `--d3d11`, `--d3d12` or `--metal` to request a specific backend (will only work if your device supports that backend). If no backend is specified, WebGPUReconstruct will choose whatever is the default backend on your device.

## Android
WebGPUReconstruct provides two native replayer apks, one for each backend. Install your preferred backend using `adb install apk_name.apk`. Since both apks use the same application ID, you can't have both backends installed at the same time.

The Android replayer is rather barebones and doesn't allow any configuration. It will always replay the capture file located in: `/sdcard/Android/data/net.chainsawkitten.webgpunativereplay/files/capture.wgpur`. So move your capture file to that location and rename it before starting the replayer. I would like to have something more user-friendly in the future.

## Replaying on a different device
WebGPUReconstruct captures are designed to be relatively portable. This means you can replay a capture on a different device than the device it was captured on, even if the device eg. has a different preferred canvas/swapchain format. However, this assumes that the device supports all the features/limits the capture uses. You can't replay a capture that uses features your device doesn't support.

A common example is content using block-compressed textures. Desktops generally support `texture-compression-bc` whereas Android supports `texture-compression-etc2` and `texture-compression-astc`. Capturing content that uses block-compressed textures on desktop and replaying on Android, or vice versa, will most likely not work.

## Troubleshooting
If you are getting the following message:
```
The capture file was saved using a different version of WebGPUReconstruct.
```
make sure you are using the same version of WebGPUReconstruct when capturing and when replaying. `.wgpur` captures are neither forward nor backward compatible.

If you're still having issues, see the [known limitations](LIMITATIONS.md). If none of those apply, see if there are [any issues](https://github.com/Chainsawkitten/WebGPUReconstruct/issues) related to your problem. If not, open an issue and mention the content you were trying to capture.