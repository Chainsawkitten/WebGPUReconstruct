chrome.storage.local.get(
    {
        externalTextureScale: 100
    },
    (items) => {
        window.postMessage({ type: "WebGPUReconstruct Options", message: items }, "*");
    }
);
