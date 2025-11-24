chrome.storage.local.get(
    {
        captureFilename: "capture.wgpur",
        externalTextureScale: "100"
    },
    (items) => {
        window.postMessage({ type: "WebGPUReconstruct Options", message: items }, "*");
    }
);
