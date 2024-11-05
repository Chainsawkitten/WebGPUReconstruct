cmake_minimum_required(VERSION 3.7.0)

project(WebGPUNativeReplay)

option(WEBGPU_NATIVE_REPLAY_DAWN_BACKEND "Build native replay with Dawn backend" ON)
option(WEBGPU_NATIVE_REPLAY_WGPU_BACKEND "Build native replay with wgpu backend" ON)

if (NOT ANDROID)
    set(GLFW_BUILD_DOCS OFF CACHE BOOL "Don't build GLFW docs" FORCE)
    set(GLFW_BUILD_EXAMPLES OFF CACHE BOOL "Don't build GLFW examples" FORCE)
    set(GLFW_BUILD_TESTS OFF CACHE BOOL "Don't build GLFW tests" FORCE)
    add_subdirectory(glfw)
endif()

# Native replayer
set(SRC
    Adapter.cpp
    Adapter.hpp
    ../build/replay/Capture.cpp
    ../build/replay/Capture.hpp
    Device.cpp
    Device.hpp
    SwapChain.cpp
    SwapChain.hpp
    TestApp.cpp
    TestApp.hpp
    Uint8Reader.cpp
    Uint8Reader.hpp
    WebGPU.hpp
    Window.hpp
    )

# Dawn
if (WEBGPU_NATIVE_REPLAY_DAWN_BACKEND)
    set(DAWN_BUILD_SAMPLES OFF CACHE BOOL "Don't build Dawn samples" FORCE)
    set(TINT_BUILD_CMD_TOOLS OFF CACHE BOOL "Don't build Tint command line tools" FORCE)
    set(TINT_BUILD_TESTS OFF CACHE BOOL "Don't build Tint tests" FORCE)
    set(TINT_BUILD_SPV_READER OFF CACHE BOOL "Don't build SPIR-V reader" FORCE)
    add_subdirectory(dawn)

    # Replayer
    if (ANDROID)
        find_package(game-activity REQUIRED CONFIG)
        add_library(WebGPUNativeReplayDawn SHARED ${SRC} AndroidMain.cpp)
        target_link_libraries(WebGPUNativeReplayDawn PUBLIC log android game-activity::game-activity_static)
    else()
        add_executable(WebGPUNativeReplayDawn ${SRC} main.cpp)
        target_link_libraries(WebGPUNativeReplayDawn PUBLIC glfw ${GLFW_LIBRARIES})
    endif()
    target_link_libraries(WebGPUNativeReplayDawn PUBLIC dawn_native dawn_proc)
    target_compile_definitions(WebGPUNativeReplayDawn PUBLIC WEBGPU_BACKEND_DAWN)
    set_property(TARGET WebGPUNativeReplayDawn PROPERTY CXX_STANDARD 20)
    set_property(TARGET WebGPUNativeReplayDawn PROPERTY CXX_STANDARD_REQUIRED ON)
endif()

# wgpu
if (WEBGPU_NATIVE_REPLAY_WGPU_BACKEND)
    # Find library
    if (ANDROID)
        set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY BOTH)
        find_library(WGPU_LIBRARY
            NAMES libwgpu_native.a wgpu_native
            HINTS "${CMAKE_CURRENT_SOURCE_DIR}/wgpu-native/target/aarch64-linux-android/release"
        )
    else()
        find_library(WGPU_LIBRARY
            NAMES wgpu_native.lib libwgpu_native.a wgpu_native
            HINTS "${CMAKE_CURRENT_SOURCE_DIR}/wgpu-native/target/release"
        )
    endif()

    # Setup WebGPU headers.
    add_library(wgpu_headers INTERFACE)
    target_include_directories(wgpu_headers INTERFACE wgpu-native/ffi wgpu-native/ffi/webgpu-headers)

    # Dependencies
    if(MSVC)
        set(WGPU_OS_LIBRARIES "userenv" "ws2_32" "Dwmapi" "dbghelp" "d3dcompiler" "D3D12" "D3D11" "DXGI" "setupapi" "Bcrypt" "ntdll" "opengl32")
    elseif(APPLE)
        set(WGPU_OS_LIBRARIES "-framework Cocoa" "-framework CoreVideo" "-framework IOKit" "-framework QuartzCore")
    endif()

    # Replayer
    if (ANDROID)
        find_package(game-activity REQUIRED CONFIG)
        add_library(WebGPUNativeReplayWgpu SHARED ${SRC} AndroidMain.cpp)
        target_link_libraries(WebGPUNativeReplayWgpu PUBLIC log android game-activity::game-activity_static)
    else()
        add_executable(WebGPUNativeReplayWgpu ${SRC} main.cpp)
        target_link_libraries(WebGPUNativeReplayWgpu PUBLIC glfw ${GLFW_LIBRARIES})
    endif()
    target_link_libraries(WebGPUNativeReplayWgpu PUBLIC ${WGPU_LIBRARY} wgpu_headers ${WGPU_OS_LIBRARIES})
    target_compile_definitions(WebGPUNativeReplayWgpu PUBLIC WEBGPU_BACKEND_WGPU)
    set_property(TARGET WebGPUNativeReplayWgpu PROPERTY CXX_STANDARD 20)
    set_property(TARGET WebGPUNativeReplayWgpu PROPERTY CXX_STANDARD_REQUIRED ON)
endif()