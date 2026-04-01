const saveOptions = () => {
$SAVE_OPTIONS
};

const restoreOptions = () => {
$RESTORE_OPTIONS
};

document.addEventListener('DOMContentLoaded', restoreOptions);
document.getElementById('save').addEventListener('click', saveOptions);