import os
import platform
import subprocess
import shutil
import json
from pathlib import Path
from code_generation.code_generation import *
from timeit import default_timer
from datetime import timedelta

rootDir = os.getcwd()

def run(workingDirectory, arguments, runInShell = False):
    os.chdir(rootDir + workingDirectory)
    result = subprocess.run(arguments, shell = runInShell)
    os.chdir(rootDir)
    
    if result.returncode != 0:
        print("Failed")
        exit(1)

def build_capture(configuration):
    print("Building capture browser extension")
    write_browser_extension(configuration, "chromium")
    write_browser_extension(configuration, "firefox")
    write_module(configuration)

def build_replay_host(configuration):
    print("Building WebGPUNativeReplay for the host platform")
    
    if configuration["wgpu"]:
        print("Compiling wgpu")
        run("/replay/wgpu-native", ["cargo", "update"])
        run("/replay/wgpu-native", ["cargo", "build", "--release"])
    
    dawnString = "-DWEBGPU_NATIVE_REPLAY_DAWN_BACKEND=" + ("ON" if configuration["dawn"] else "OFF")
    wgpuString = "-DWEBGPU_NATIVE_REPLAY_WGPU_BACKEND=" + ("ON" if configuration["wgpu"] else "OFF")
    buildTypeString = "-DCMAKE_BUILD_TYPE=" + ("Debug" if configuration["debug"] else "Release")
    configString = "Debug" if configuration["debug"] else "Release"
    
    print("Compiling WebGPUNativeReplay")
    run("/build/replay", ["cmake", "../../replay", dawnString, wgpuString, buildTypeString])
    run("/build/replay", ["cmake", "--build", ".", "--config", configString])

def build_replay_android(configuration):
    print("Building WebGPUNativeReplay for Android")
    
    if configuration["wgpu"]:
        print("Compiling wgpu")
        # Environment variables
        if platform.system() == "Windows":
            os.environ["BINDGEN_EXTRA_CLANG_ARGS"] = "-isysroot " + configuration["ndk"] + "/toolchains/llvm/prebuilt/windows-x86_64/sysroot"
            clang_path = configuration["ndk"] + "/toolchains/llvm/prebuilt/windows-x86_64/bin/aarch64-linux-android24-clang++.cmd"
            os.environ["CLANG_PATH"] = clang_path
            os.environ["CC"] = clang_path
            os.environ["CXX"] = clang_path
            os.environ["CARGO_TARGET_AARCH64_LINUX_ANDROID_LINKER"] = clang_path
        elif platform.system() == "Linux":
            os.environ["BINDGEN_EXTRA_CLANG_ARGS"] = "-isysroot " + configuration["ndk"] + "/toolchains/llvm/prebuilt/linux-x86_64/sysroot"
            clang_path = configuration["ndk"] + "/toolchains/llvm/prebuilt/linux-x86_64/bin/aarch64-linux-android24-clang"
            os.environ["CLANG_PATH"] = clang_path
            os.environ["CC"] = clang_path
            os.environ["CXX"] = clang_path
            os.environ["CARGO_TARGET_AARCH64_LINUX_ANDROID_LINKER"] = clang_path
        else:
            print("Don't know how to build Android replayer on " + platform.system() + ".")
            print("PRs welcome :)")
        run("/replay/wgpu-native", ["rustup", "target", "add", "aarch64-linux-android"])
        run("/replay/wgpu-native", ["cargo", "build", "--target", "aarch64-linux-android", "--release"])
    
    buildType = "assemble" + ("Debug" if configuration["debug"] else "Release")
    
    gradlew = "gradlew"
    if platform.system() == "Linux":
        gradlew = "./gradlew"
        run("/build/replay/AndroidDawn", ["chmod", "+x", "./gradlew"])
    
    if configuration["dawn"]:
        print("Compiling WebGPUNativeReplay (Dawn)")
        shutil.copytree("replay/Android", "build/replay/AndroidDawn", dirs_exist_ok=True)
        
        replace_string_in_file("build/replay/AndroidDawn/app/src/main/AndroidManifest.xml", "$LIBNAME", "WebGPUNativeReplayDawn")
        replace_string_in_file("build/replay/AndroidDawn/app/src/main/java/net/chainsawkitten/webgpunativereplay/MainActivity.java", "$LIBNAME", "WebGPUNativeReplayDawn")
        replace_string_in_file("build/replay/AndroidDawn/app/build.gradle", "$VERSION_CODE", str(versionInt))
        replace_string_in_file("build/replay/AndroidDawn/app/build.gradle", "$VERSION_STRING", versionString)
        replace_string_in_file("build/replay/AndroidDawn/app/build.gradle", "$BUILD_WITH_DAWN", "ON")
        replace_string_in_file("build/replay/AndroidDawn/app/build.gradle", "$BUILD_WITH_WGPU", "OFF")
        
        run("/build/replay/AndroidDawn", [gradlew, buildType, "-x", "lint"], True)
    
    if configuration["wgpu"]:
        print("Compiling WebGPUNativeReplay (wgpu)")
        shutil.copytree("replay/Android", "build/replay/AndroidWgpu", dirs_exist_ok=True)
        
        replace_string_in_file("build/replay/AndroidWgpu/app/src/main/AndroidManifest.xml", "$LIBNAME", "WebGPUNativeReplayWgpu")
        replace_string_in_file("build/replay/AndroidWgpu/app/src/main/java/net/chainsawkitten/webgpunativereplay/MainActivity.java", "$LIBNAME", "WebGPUNativeReplayWgpu")
        replace_string_in_file("build/replay/AndroidWgpu/app/build.gradle", "$VERSION_CODE", str(versionInt))
        replace_string_in_file("build/replay/AndroidWgpu/app/build.gradle", "$VERSION_STRING", versionString)
        replace_string_in_file("build/replay/AndroidWgpu/app/build.gradle", "$BUILD_WITH_DAWN", "OFF")
        replace_string_in_file("build/replay/AndroidWgpu/app/build.gradle", "$BUILD_WITH_WGPU", "ON")
        
        run("/build/replay/AndroidWgpu", [gradlew, buildType, "-x", "lint"], True)

def build_replay(configuration):
    if configuration["host"] or configuration["android"]:
        Path("build/replay").mkdir(parents=True, exist_ok=True)
        write_replay_files(rootDir, configuration)
    
    if configuration["host"]:
        build_replay_host(configuration)
    
    if configuration["android"]:
        build_replay_android(configuration)

def build(configuration):
    start = default_timer()
    
    build_capture(configuration)
    build_replay(configuration)
    
    end = default_timer()
    print("Built WebGPUReconstruct in " + str(timedelta(seconds = end - start)))

def get_configuration():
    if not Path("build/configuration.json").is_file():
        print("Could not find build/configuration.json. Configure the build with python ./configure.py")
        quit()
    
    file = open("build/configuration.json", "r")
    contents = file.read()
    file.close()
    
    return json.loads(contents)
    
def main():
    configuration = get_configuration()
    build(configuration)

main()
