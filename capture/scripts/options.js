const saveOptions = () => {
    const captureFilename = document.getElementById('captureFilename').value;
    const captureMaxFrames = document.getElementById('captureMaxFrames').value;
    const adapterDefaultLimits = document.getElementById('adapterDefaultLimits').checked;
    const externalTextureScale = document.getElementById('externalTextureScale').value;

    chrome.storage.local.set(
        {
            captureFilename: captureFilename,
            captureMaxFrames: captureMaxFrames,
            adapterDefaultLimits: String(adapterDefaultLimits),
            externalTextureScale: externalTextureScale
        },
        () => {
            // Update status to let user know options were saved.
            const status = document.getElementById('status');
            status.textContent = 'Options saved.';
            setTimeout(() => {
                status.textContent = '';
            }, 750);
        }
    );
};

const restoreOptions = () => {
    chrome.storage.local.get(
        {
            captureFilename: "capture.wgpur",
            captureMaxFrames: "0",
            adapterDefaultLimits: "false",
            externalTextureScale: "100"
        },
        (items) => {
            document.getElementById('captureFilename').value = items.captureFilename;
            document.getElementById('captureMaxFrames').value = items.captureMaxFrames;
            document.getElementById('adapterDefaultLimits').checked = (items.adapterDefaultLimits === "true");
            document.getElementById('externalTextureScale').value = items.externalTextureScale;
        }
    );
};

document.addEventListener('DOMContentLoaded', restoreOptions);
document.getElementById('save').addEventListener('click', saveOptions);