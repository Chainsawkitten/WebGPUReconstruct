const saveOptions = () => {
    const externalTextureScale = document.getElementById('externalTextureScale').value;

    chrome.storage.local.set(
        {
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
            externalTextureScale: 100
        },
        (items) => {
            document.getElementById('externalTextureScale').value = items.externalTextureScale;
        }
    );
};

document.addEventListener('DOMContentLoaded', restoreOptions);
document.getElementById('save').addEventListener('click', saveOptions);