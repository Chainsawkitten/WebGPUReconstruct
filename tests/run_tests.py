import argparse
import http.server
import socketserver
import subprocess
import threading
import time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

# Parse arguments.
parser = argparse.ArgumentParser(description = "WebGPUReconstruct unit tests.")
parser.add_argument("--dawn-replayer", help = "Path to the Dawn replayer to use when replaying test captures.")
parser.add_argument("--wgpu-replayer", help = "Path to the wgpu replayer to use when replaying test captures.")
parser.add_argument("--port", default = "8000", help = "Port to host test web page on. Default: 8000.")
parser.add_argument("--test", help = "Run only one specific test.")
args=parser.parse_args()

# Request handler that doesn't print every request.
class QuietHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def log_request(self, code='-', size='-'):
        pass

EXPECTED_FAILURE_DAWN = 1
EXPECTED_FAILURE_WGPU = 2

class Test:
    def __init__(self, name, flags = 0):
        self.name = name
        self.flags = flags

class Tests:
    def __init__(self, args):
        self.tests = []
        self.port = int(args.port)
        self.dawn_replayer = args.dawn_replayer
        self.wgpu_replayer = args.wgpu_replayer
    
    def add(self, name, flags = 0):
        self.tests.append(Test(name, flags))
    
    def run_server(self):
        while not self.done:
            self.server.handle_request()
    
    def setup(self):
        print("Running WebGPUReconstruct unit tests")
        
        # Run web server
        self.server = socketserver.TCPServer(("", self.port), QuietHTTPRequestHandler)
        self.server.timeout = 1
        self.thread = threading.Thread(target=self.run_server)
        self.done = False
        self.thread.start()
        
        # Create captures folder.
        Path("captures").mkdir(parents=True, exist_ok=True)
    
    def teardown(self):
        # Shut down web server
        self.done = True
        self.thread.join()
    
    def run_all_tests(self):
        self.setup()
        
        # Run tests
        successes = 0
        failures = []
        for test in self.tests:
            success = self.run_test(test)
            if success:
                successes += 1
                print("SUCCESS\n")
            else:
                print("FAILED\n")
                failures.append(test.name)
        
        self.teardown()
        
        # Collect results
        print("===RESULTS===")
        print(f"{successes} tests succeeded")
        print(f"{len(failures)} tests failed")
        
        if len(failures) > 0:
            print("Failing tests:")
            print(failures)
    
    def run_one_test(self, test_name):
        self.setup()
        
        found = False
        for test in self.tests:
            if test.name == test_name:
                success = self.run_test(test)
                found = True
                
                if success:
                    print("SUCCESS\n")
                else:
                    print("FAILED\n")
        
        if not found:
            print(f"Could not find test {test_name}")
        
        self.teardown()
    
    def run_test(self, test):
        print(f"Running {test.name}")
        
        # Delete any capture file from previous runs.
        capture_path = Path(f"captures/{test.name}.wgpur")
        capture_path.unlink(missing_ok=True)
        
        options = webdriver.ChromeOptions()
        options.set_capability("goog:loggingPrefs", {"browser": "ALL"})
        options.add_experimental_option("prefs", {"download.default_directory": str(Path("captures").absolute())});
        
        driver = webdriver.Chrome(options = options)
        driver.get(f"http://localhost:{self.port}/tests.html?test={test.name}")
        
        # Wait until test has finished.
        element = driver.find_element(By.ID, "result")
        wait = WebDriverWait(driver, timeout=20)
        try:
            wait.until(lambda _ : element.is_displayed())
        except:
            print("Test timed out")
            driver.quit()
            return False
        
        logs = driver.get_log('browser')
        
        # Check the logs for any warnings or errors.
        errors = False
        for entry in logs:
            if entry['level'] == "WARNING" or entry['level'] == "SEVERE":
                print(f"{entry['level']} - {entry['message']}")
                errors = True
        
        if errors:
            driver.quit()
            return False
        
        # Ensure "download" has finalized.
        while not capture_path.exists():
            pass
        
        driver.quit()
        
        # Run the replayer
        if test.flags & EXPECTED_FAILURE_DAWN:
            print("Expected failure, skipping Dawn replay")
        else:
            if not self.replay(test, "Dawn", self.dawn_replayer):
                errors = True
        
        if test.flags & EXPECTED_FAILURE_WGPU:
            print("Expected failure, skipping wgpu replay")
        else:
            if not self.replay(test, "wgpu", self.wgpu_replayer):
                errors = True
        
        return not errors
    
    def replay(self, test, replayer_name, replayer_path):
        result = subprocess.run([replayer_path, str(Path(f"captures/{test.name}.wgpur")), '--verify-readbacks', '--offscreen'], shell = False, capture_output=True)
        if result.returncode != 0:
            print(f"{replayer_name} replay failed")
            print(result.stderr.decode())
            return False
        return True

# Verify the specified replayers exist.
if not Path(str(args.dawn_replayer)).exists():
    print(f"Could not find Dawn replayer: {args.dawn_replayer}")
    exit()

if not Path(str(args.wgpu_replayer)).exists():
    print(f"Could not find wgpu replayer: {args.wgpu_replayer}")
    exit()


tests = Tests(args)

# Test list
tests.add("simpleClear")
tests.add("drawTriangle")
tests.add("characterEncoding")
tests.add("pipelineOverridableConstant")
tests.add("timestampQueries")
tests.add("sequenceOrDictionary")
tests.add("immediatesCompute", EXPECTED_FAILURE_WGPU) # Creating pipeline with immediates and automatic pipeline layout fails.
tests.add("immediatesGraphics", EXPECTED_FAILURE_WGPU) # Creating pipeline with immediates and automatic pipeline layout fails.
tests.add("writeBuffer")
tests.add("depthClipControl")
tests.add("textureComponentSwizzle", EXPECTED_FAILURE_WGPU) # wgpu-native hasn't implemented texture-component-swizzle.
tests.add("dualSourceBlending")

if args.test is None:
    tests.run_all_tests()
else:
    tests.run_one_test(args.test)
