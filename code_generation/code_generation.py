import shutil
import os
import subprocess

version = (0, 3)
# Increment the file version whenever a change is introduced.
fileVersion = 6

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

def write_capture_files(configuration, browser):
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
    
    contentPath = "build/capture/" + browser + "/scripts/content.js"
    add_prefix_to_file(contentPath, "const __WebGPUReconstruct_DEBUG = " + ("true" if configuration["debug"] else "false") + ";\n")
    replace_string_in_file(contentPath, "$FILE_VERSION", str(fileVersion))
    replace_string_in_file(contentPath, "$VERSION_MAJOR", str(version[0]))
    replace_string_in_file(contentPath, "$VERSION_MINOR", str(version[1]))
    replace_string_in_file(contentPath, "$CAPTURE_COMMANDS", captureCommandsString)
    replace_string_in_file(contentPath, "$WRAP_COMMANDS", wrapCommandsString)
    replace_string_in_file(contentPath, "$ENUM_SAVE_FUNCTIONS", enumSaveFunctionsString)
    replace_string_in_file(contentPath, "$STRUCT_SAVE_FUNCTIONS", structSaveFunctionsString)
    
    shutil.make_archive("build/capture/" + browser, 'zip', "build/capture/" + browser)

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
    