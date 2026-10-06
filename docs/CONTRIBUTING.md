# Contributing
Before reporting an issue, please search for any existing issues first.

To contribute, fork the repository on GitHub and open a pull request with your suggested changes. When pulling upstream changes, please use rebase to keep a clean history.

## LLMs
Large language models or generative AI must not be used when contributing to this project.

## Tests
WebGPUReconstruct uses [Selenium](https://www.selenium.dev) to automate tests. To install it, run:

```
pip install -U selenium
```

Then, to run the test suite:

1. [Build WebGPUReconstruct with both wgpu and Dawn backends.](BUILDING.md)
1. In `build/tests`, run
```
python ./run_tests.py --dawn-replayer <PATH_TO_DAWN_REPLAYER> --wgpu-replayer <PATH_TO_WGPU_REPLAYER>
```

## Versioning
Whenever the capture file format is modified in any way, increment `fileVersion` in `code_generation\code_generation.py`.