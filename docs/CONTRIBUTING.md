# Contributing
Before reporting an issue, please search for any existing issues first.

To contribute, fork the repository on GitHub and open a pull request with your suggested changes. When pulling upstream changes, please use rebase to keep a clean history.

## LLMs
Large language models or generative AI must not be used when contributing to this project.

## Tests
WebGPUReconstructs includes a test suite. To run it:

1. [Build WebGPUReconstruct with both wgpu and Dawn backends.](BUILDING.md)
1. Host the test web page by running `python -m http.server` in `build/tests`.

Then to run a test:
1. Navigate to `localhost:8000?test=<TEST NAME>` in your web browser. Make sure the WebGPUReconstruct extension is disabled before doing so, as the tests use the module version of WebGPUReconstruct, which could interfere with the extension.
1. Check the browser's debug console for any error messages.
1. Run the resulting capture file through the native replayer with `--verify-readbacks`.
1. Ensure the replay finished without any errors.

## Versioning
Whenever the capture file format is modified in any way, increment `fileVersion` in `code_generation\code_generation.py`.