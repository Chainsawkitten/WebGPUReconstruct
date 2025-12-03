import shutil
import os
import subprocess
from pathlib import Path

version = (1, 0)
# Increment the file version whenever a change is introduced.
fileVersion = 16

versionString = str(version[0]) + "." + str(version[1])
versionInt = version[0] * 10000 + version[1]

from code_generation.commands import *

def replace_string_in_file(filename, oldString, newString):
    file = open(filename, "r")
    contents = file.read()
    file.close()
    
    contents = contents.replace(oldString, newString)
    
    file = open(filename, "w")
    file.write(contents)
    file.close()

def add_prefix_to_file(filename, prefix):
    file = open(filename, "r")
    contents = file.read()
    file.close()
    
    contents = prefix + contents
    
    file = open(filename, "w")
    file.write(contents)
    file.close()

def add_suffix_to_file(filename, suffix):
    file = open(filename, "r")
    contents = file.read()
    file.close()
    
    contents = contents + suffix
    
    file = open(filename, "w")
    file.write(contents)
    file.close()

def write_browser_extension(configuration, browser):
    shutil.copytree("capture", "build/capture/" + browser, dirs_exist_ok=True)
    manifestPath = "build/capture/" + browser + "/manifest.json"
    replace_string_in_file(manifestPath, "$VERSION", versionString)
    if browser == "firefox":
        replace_string_in_file(manifestPath, "$BROWSER_SPECIFIC", """
    "background": {
        "scripts": ["scripts/background.js"]
    },
    "browser_specific_settings": {
        "gecko": {
            "id": "webgpureconstruct@chainsawkitten.net"
        },
        "gecko_android": {
            "id": "webgpureconstruct@chainsawkitten.net"
        }
    }
""")
    else:
        replace_string_in_file(manifestPath, "$BROWSER_SPECIFIC", """
    "background": {
        "service_worker": "scripts/background.js"
    }
""")
    
    contentPath = "build/capture/" + browser + "/scripts/mainContent.js"
    write_content_script(contentPath, configuration)
    add_suffix_to_file(contentPath, """
let __webGPUReconstruct = new __WebGPUReconstruct();

// Listener that listens for the "capture" button to be pressed.
// When this happens, finish up the capture and store it to file.
document.addEventListener('__WebGPUReconstruct_saveCapture', function() {
    __webGPUReconstruct.finishCapture();
});

__webGPUReconstruct.optionsPromise = new Promise((resolve) => {
    window.addEventListener("__WebGPUReconstruct_options", function __WebGPUReconstruct_Options(event) {
        __webGPUReconstruct.configure(JSON.parse(event.detail));
        window.removeEventListener("__WebGPUReconstruct_options", __WebGPUReconstruct_Options);
        resolve();
    });
});
""")
    
    shutil.make_archive("build/capture/" + browser, 'zip', "build/capture/" + browser)

def write_module(configuration):
    Path("build/capture/module").mkdir(parents=True, exist_ok=True)
    contentPath = "build/capture/module/WebGPUReconstruct.js"
    shutil.copyfile("capture/scripts/mainContent.js", contentPath)
    write_content_script(contentPath, configuration)
    add_suffix_to_file(contentPath, """
let __webGPUReconstruct;

function start(configuration) {
    __webGPUReconstruct = new __WebGPUReconstruct();
    __webGPUReconstruct.configure(configuration);
    __webGPUReconstruct.optionsPromise = new Promise((resolve) => { resolve() });
}

function finish() {
    __webGPUReconstruct.finishCapture();
}

export default { start, finish };
""")

def write_content_script(path, configuration):
    add_prefix_to_file(path, "const __WebGPUReconstruct_DEBUG = " + ("true" if configuration["debug"] else "false") + ";\n")
    replace_string_in_file(path, "$FILE_VERSION", str(fileVersion))
    replace_string_in_file(path, "$VERSION_MAJOR", str(version[0]))
    replace_string_in_file(path, "$VERSION_MINOR", str(version[1]))
    replace_string_in_file(path, "$CAPTURE_COMMANDS", captureCommandsString)
    replace_string_in_file(path, "$WRAP_COMMANDS", wrapCommandsString)
    replace_string_in_file(path, "$RESET_COMMANDS", resetCommandsString)
    replace_string_in_file(path, "$ENUM_SAVE_FUNCTIONS", enumSaveFunctionsString)
    replace_string_in_file(path, "$STRUCT_SAVE_FUNCTIONS", structSaveFunctionsString)
    

def run_query(rootDir, workingDirectory, arguments):
    os.chdir(rootDir + workingDirectory)
    result = subprocess.run(arguments, shell = False, capture_output = True, text = True)
    os.chdir(rootDir)
    
    if result.returncode != 0:
        print("Failed")
        exit(1)
    
    return result.stdout.strip("\n")

def write_replay_files(rootDir, configuration):
    shutil.copyfile("replay/Capture.cpp", "build/replay/Capture.cpp")
    shutil.copyfile("replay/Capture.hpp", "build/replay/Capture.hpp")
    shutil.copyfile("replay/Constants.hpp", "build/replay/Constants.hpp")
    
    replace_string_in_file("build/replay/Capture.cpp", "$RUN_COMMANDS", runCommandsString)
    replace_string_in_file("build/replay/Capture.cpp", "$ENUM_CONVERSIONS", enumConversionsString)
    replace_string_in_file("build/replay/Capture.cpp", "$STRUCT_LOAD_FUNCTIONS", structLoadFunctionsString)
    replace_string_in_file("build/replay/Capture.hpp", "$MAPS", mapString)
    replace_string_in_file("build/replay/Capture.hpp", "$STRUCT_FUNCTION_DECLARATIONS", structFunctionDeclarationsString)
    replace_string_in_file("build/replay/Constants.hpp", "$VERSION_MAJOR", str(version[0]))
    replace_string_in_file("build/replay/Constants.hpp", "$VERSION_MINOR", str(version[1]))
    replace_string_in_file("build/replay/Constants.hpp", "$FILE_VERSION", str(fileVersion))
    
    if configuration["dawn"]:
        replace_string_in_file("build/replay/Constants.hpp", "$DAWN_BRANCH", '"' + run_query(rootDir, "/replay/dawn", ["git",  "branch", "--show-current"]) + '"')
        replace_string_in_file("build/replay/Constants.hpp", "$DAWN_COMMIT", '"' + run_query(rootDir, "/replay/dawn", ["git",  "rev-parse", "--short", "HEAD"]) + '"')
    else:
        replace_string_in_file("build/replay/Constants.hpp", "$DAWN_BRANCH", '""')
        replace_string_in_file("build/replay/Constants.hpp", "$DAWN_COMMIT", '""')
    
    if configuration["wgpu"]:
        replace_string_in_file("build/replay/Constants.hpp", "$WGPU_TAG", '"' + run_query(rootDir, "/replay/wgpu-native", ["git", "describe", "--tags", "--abbrev=0"]) + '"')
        replace_string_in_file("build/replay/Constants.hpp", "$WGPU_COMMIT", '"' + run_query(rootDir, "/replay/wgpu-native", ["git",  "rev-parse", "--short", "HEAD"]) + '"')
    else:
        replace_string_in_file("build/replay/Constants.hpp", "$WGPU_TAG", '""')
        replace_string_in_file("build/replay/Constants.hpp", "$WGPU_COMMIT", '""')
    