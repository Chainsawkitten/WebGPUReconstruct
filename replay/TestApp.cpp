#include "TestApp.hpp"

#include "../build/replay/Capture.hpp"
#include "../build/replay/Constants.hpp"
#include <chrono>
#include <string>
#include <iomanip>
#include <fstream>
#include <sstream>
#include "Configuration.hpp"
#include "Logging.hpp"

using namespace std;

namespace WebGPUNativeReplay {

TestApp::TestApp(const Window& window, const Configuration& configuration) :
    adapter(window, configuration.backendType),
    device(adapter),
    swapChain(adapter, device, window, configuration.width, configuration.height, configuration.mailbox),
    offscreen(configuration.offscreen),
    statsFile(configuration.statsFile)
{

}

TestApp::~TestApp() {

}

void TestApp::RunCapture(string_view filename, std::function<bool(void)> frameCallback) {
    Capture capture(filename, adapter, device, swapChain, offscreen);
    if (!capture.IsValid()) {
        return;
    }

    const chrono::high_resolution_clock::time_point start = chrono::high_resolution_clock::now();
    const chrono::system_clock::time_point startUnix = chrono::system_clock::now();

    uint32_t frameCount = 0;
    uint32_t emptyFrames = 0;
    bool empty = true;
    bool started = false;
    bool finished = false;
    bool prematureQuit = false;
    while (!finished) {
        Capture::Status status = capture.RunNextCommand();
        switch (status) {
        case Capture::Status::END_OF_CAPTURE:
            finished = true;
            break;
        case Capture::Status::FRAME_START:
            started = true;
            empty = true;
            break;
        case Capture::Status::FRAME_END:
            if (!frameCallback()) {
                finished = true;
                prematureQuit = true;
            }
            if (started) {
                frameCount++;
                if (empty) {
                    emptyFrames++;
                }
            }
            break;
        default:
            empty = false;
            break;
        }
    }

    if (!prematureQuit) {
        const chrono::high_resolution_clock::time_point end = chrono::high_resolution_clock::now();
        const chrono::system_clock::time_point endUnix = chrono::system_clock::now();

        const chrono::duration<double> duration = chrono::duration_cast<chrono::duration<double>>(end - start);
        const auto startUnixTimestamp = chrono::duration_cast<chrono::milliseconds>(startUnix.time_since_epoch());
        const auto endUnixTimestamp = chrono::duration_cast<chrono::milliseconds>(endUnix.time_since_epoch());

        stringstream stats;
        stats << "Ran " << frameCount << " frames in " << duration.count() << " seconds (" << (static_cast<double>(frameCount) / duration.count()) << " FPS).\n";
        if (emptyFrames > 0) {
            stats << "Of which " << emptyFrames << " frames were empty (contained no commands).\n";
        }
        stats << setprecision(4) << fixed;
        stats << "Start UNIX timestamp: " << startUnixTimestamp.count() / 1000.0 << "\n";
        stats << "End UNIX timestamp: " << endUnixTimestamp.count() / 1000.0 << "\n";

        stats << "Canvas: ";
        Capture::CanvasSize canvasSize = capture.GetCanvasSize();
        switch (canvasSize.state) {
        case Capture::CanvasSize::State::NONE:
            stats << "None";
            break;
        case Capture::CanvasSize::State::SINGLE:
            stats << canvasSize.width << " x " << canvasSize.height;
            break;
        case Capture::CanvasSize::State::MULTIPLE:
            stats << "Multiple sizes";
            break;
        }
        stats << "\n";

        stats << "Capture version " << capture.GetVersionMajor() << "." << capture.GetVersionMinor() << "\n";
        stats << "Replayer version " << VERSION_MAJOR << "." << VERSION_MINOR << "\n";
        stats << Configuration::GetImplementationVersion() << "\n";

        Logging::Info(stats.str());

        if (!statsFile.empty()) {
            ofstream file;
            file.open(statsFile);
            file << stats.str();
            file.close();
        }
    }
}

}
