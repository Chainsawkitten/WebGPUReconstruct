import os
import subprocess
import json
from pathlib import Path
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

def fetch_submodule(module, recursive = False):
    if recursive:
        run("", ["git", "submodule", "update", "--init", "--recursive", module])
    else:
        run("", ["git", "submodule", "update", "--init", module])

def fetch_replay_modules(configuration):
    print("Fetching common modules")
    fetch_submodule("replay/glfw", True)
    
    if configuration["dawn"]:
        print("Fetching Dawn modules")
        fetch_submodule("replay/dawn", False)
    
    if configuration["wgpu"]:
        print("Fetching wgpu modules")
        fetch_submodule("replay/wgpu-native", True)

def fetch_modules(configuration):
    start = default_timer()
    
    fetch_replay_modules(configuration)
    
    end = default_timer()
    print("Fetched modules in " + str(timedelta(seconds = end - start)))

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
    fetch_modules(configuration)

main()
