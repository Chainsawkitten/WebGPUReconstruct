chrome.storage.local.get(
    {
        captureFilename: "capture.wgpur",
        captureMaxFrames: "0",
        externalTextureScale: "100"
    },
    (items) => {
        window.dispatchEvent(new CustomEvent("__WebGPUReconstruct_options", { detail: JSON.stringify(items) }));
    }
);
