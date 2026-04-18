const saveOptions = () => {
$SAVE_OPTIONS
};

const restoreOptions = () => {
$RESTORE_OPTIONS
};

const resetOptions = () => {
$RESET_OPTIONS
};

document.addEventListener('DOMContentLoaded', restoreOptions);
document.getElementById('save').addEventListener('click', saveOptions);
document.getElementById('reset').addEventListener('click', resetOptions);