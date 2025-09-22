# Building

## Dependencies
Install the following dependencies:
- [git](https://git-scm.com/)
- [Python](https://www.python.org/)
- [CMake](https://cmake.org/)
- A C++ compiler (eg. MSVC, gcc, clang)
- If building on Linux, [GLFW dependencies](https://www.glfw.org/docs/latest/compile_guide.html#compile_deps)

## Setup
Use the `configure` script to configure the build. Use `--help` to see the options.
```
python ./configure.py --dawn --wgpu --target release
```

### Dawn
To build with the Dawn backend (`--dawn`), you need to setup Dawn's dependencies.

- If on Linux, install:
  ```
  sudo apt-get install libxrandr-dev libxinerama-dev libxcursor-dev mesa-common-dev libx11-xcb-dev pkg-config nodejs npm
  ```
Otherwise, no additional work is necessary.

### wgpu
To build with the wgpu backend (`--wgpu`), you need to setup wgpu's dependencies.

- Download and install the wgpu-native prerequisites described in the [docs](https://github.com/gfx-rs/wgpu-native/wiki/Getting-Started#prerequisites). You don't need the dependencies for the native examples.

### Android
Install [Android Studio](https://developer.android.com/studio) and use it to download Android SDK and NDK 26.3.11579264.

Enable Android builds and set the NDK path when configuring the build.
```
python ./configure.py --dawn --wgpu --android --ndk PATH_TO_NDK_DIRECTORY --target release
```

## Fetch modules
Use the `fetch_modules` script to download submodules according to the configuration.
```
python ./fetch_modules.py
```
Rerun the command after changing the configuration or checking out a new commit.

## Build
```
python ./build.py
```
