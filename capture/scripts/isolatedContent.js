chrome.storage.local.get(
    {
        captureFilename: "capture.wgpur",
        captureMaxFrames: "0",
        externalTextureScale: "100"
    },
    (items) => {
        window.postMessage({ type: "WebGPUReconstruct Options", message: items }, "*");
    }
);
