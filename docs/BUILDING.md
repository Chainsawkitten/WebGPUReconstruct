# Building

## Dependencies
Install the following dependencies:
- [git](https://git-scm.com/)
- [Python](https://www.python.org/)
- [CMake](https://cmake.org/)
- A C++ compiler (eg. MSVC, gcc, clang)
- If building on Linux, [GLFW dependencies](https://www.glfw.org/docs/latest/compile_guide.html#compile_deps)

## Setup
Download the repository's submodules. Dawn has a lot of dependencies so this can take a while.
```
git submodule update --init --recursive
```

Use the `configure` script to configure the build. Use `--help` to see the options.
```
python ./configure.py --dawn --wgpu --target release
```

### Dawn
To build with the Dawn backend (`--dawn`), you need to setup Dawn's dependencies.

- Install [depot_tools](http://commondatastorage.googleapis.com/chrome-infra-docs/flat/depot_tools/docs/html/depot_tools_tutorial.html#_setting_up).
- If on Windows, add `DEPOT_TOOLS_WIN_TOOLCHAIN` environment variable and set it to `0`.
- In `replay/dawn/` run:
  ```
  cp scripts/standalone.gclient .gclient
  gclient sync
  ```

### wgpu
To build with the wgpu backend (`--wgpu`), you need to setup wgpu's dependencies.

- Download and install the wgpu-native prerequisites described in the [docs](https://github.com/gfx-rs/wgpu-native/wiki/Getting-Started#prerequisites). You don't need the dependencies for the native examples.

### Android
Install [Android Studio](https://developer.android.com/studio) and use it to download Android SDK and NDK.

Enable Android builds and set the NDK path when configuring the build.
```
python ./configure.py --dawn --wgpu --android --ndk PATH_TO_NDK_DIRECTORY --target release
```

## Build
```
python ./build.py
```

If you get errors about missing `lunwind` when compiling for Android, use a newer NDK. 25.1.8937393 has been verified to work.