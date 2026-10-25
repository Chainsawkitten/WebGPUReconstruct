import WebGPUReconstruct from "./WebGPUReconstruct.js";

class Tests {
    async runTest(test) {
        WebGPUReconstruct.start({
            captureFilename: `${test}.wgpur`,
            bufferCaptureReadbackData: true
        });

        this.canvas = document.querySelector('canvas');
        this.adapter = await navigator.gpu.requestAdapter();
        try {
            await this[test]();
        } catch (e) {
            console.error(e.toString());
        }

        WebGPUReconstruct.finish();

        document.getElementById("result").style.display = "inline";
    }

    async createDevice(features) {
        // Check feature support before attempting to create the device.
        for (let feature of features) {
            if (!this.adapter.features.has(feature)) {
                console.error(`Adapter does not support the required feature ${feature}.`);
                return false;
            }
        }

        this.device = await this.adapter.requestDevice({ requiredFeatures : features });
        return true;
    }

    async verifyTexture(texture, goldenImage, threshold = 0) {
        console.assert(texture.format == 'rgba8unorm');

        let bytesPerRow = 4 * texture.width;
        bytesPerRow = (Math.floor((bytesPerRow - 1) / 256) + 1) * 256;

        const readbackBuffer = this.device.createBuffer({
            size: bytesPerRow * texture.height,
            usage: GPUBufferUsage.COPY_DST | GPUBufferUsage.MAP_READ
        });

        const commandEncoder = this.device.createCommandEncoder();
        commandEncoder.copyTextureToBuffer({
            texture: texture
        }, {
            buffer: readbackBuffer,
            bytesPerRow: bytesPerRow,
            rowsPerImage: texture.height
        }, {
            width: texture.width,
            height: texture.height
        });
        this.device.queue.submit([commandEncoder.finish()]);

        await readbackBuffer.mapAsync(GPUMapMode.READ);
        const contents = readbackBuffer.getMappedRange();

        const data = new Uint8Array(contents);
        for (let y = 0; y < texture.height; y++) {
            for (let x = 0; x < texture.width; x++) {
                let d = '[';
                for (let component = 0; component < 4; component++) {
                    const value = data[y * bytesPerRow + x * 4 + component];
                    const reference = goldenImage[y * texture.width + x][component];
                    if (reference == null) {
                        console.error(`Missing reference value at x: ${x}, y: ${y}`);
                        return;
                    }
                    if (Math.abs(value - reference) > threshold) {
                        console.error(`Result image doesn't match reference. x: ${x}, y: ${y}, component ${component} was ${value}. Expected ${reference}.`);
                        return;
                    }
                }
            }
        }

        readbackBuffer.unmap();
    }

    async verifyBuffer(buffer, reference) {
        console.assert(buffer.size % 4 == 0);

        const readbackBuffer = this.device.createBuffer({
            size: buffer.size,
            usage: GPUBufferUsage.COPY_DST | GPUBufferUsage.MAP_READ
        });

        const commandEncoder = this.device.createCommandEncoder();
        commandEncoder.copyBufferToBuffer(buffer, readbackBuffer);
        this.device.queue.submit([commandEncoder.finish()]);

        await readbackBuffer.mapAsync(GPUMapMode.READ);
        const contents = readbackBuffer.getMappedRange();

        const data = new Uint32Array(contents);
        const referenceArray = new Uint32Array(reference);
        for (let i = 0; i < data.length; i++) {
            if (data[i] != referenceArray[i]) {
                console.error(`Result buffer doesn't match reference. [${i}] = ${data[i]}. Expected ${referenceArray[i]}.`);
                return;
            }
        }

        readbackBuffer.unmap();
    }

    // The simplest test. Clears a 1x1 render target with green.
    async simpleClear() {
        if (!await this.createDevice([])) {
            return;
        }
        
        const renderTarget = this.device.createTexture({
            size: {
                width: 1,
                height: 1
            },
            format: 'rgba8unorm',
            usage: GPUTextureUsage.RENDER_ATTACHMENT | GPUTextureUsage.COPY_SRC
        });

        const commandEncoder = this.device.createCommandEncoder();

        const passEncoder = commandEncoder.beginRenderPass({
            colorAttachments: [
                {
                    view: renderTarget.createView(),
                    clearValue: [0, 1, 0, 1],
                    loadOp: 'clear',
                    storeOp: 'store',
                }
            ]
        });
        passEncoder.end();

        this.device.queue.submit([commandEncoder.finish()]);
        
        await this.verifyTexture(renderTarget, [
            [0, 255, 0, 255]
        ]);
    }

    // Draws a yellow triangle against a 5x5 blue background.
    // Tests graphics pipelines, vertex & index buffers, writeBuffer.
    async drawTriangle() {
        if (!await this.createDevice([])) {
            return;
        }

        const pipeline = this.device.createRenderPipeline({
            layout: 'auto',
            vertex: {
                module: this.device.createShaderModule({
                    code:
`struct VSOut {
  @builtin(position) pos : vec4f
};

@vertex
fn main(
  @location(0) position : vec2f
) -> VSOut {
  var out : VSOut;
  out.pos = vec4f(position, 0.0, 1.0);
  return out;
}
`
                }),
                buffers: [
                    {
                        arrayStride: 2 * 4,
                        attributes: [
                            {
                                // position
                                shaderLocation: 0,
                                offset: 0,
                                format: 'float32x2',
                            }
                        ],
                    },
                ],
            },
            fragment: {
                module: this.device.createShaderModule({
                    code:
`@fragment
fn main(
  
) -> @location(0) vec4f {
  var color : vec4f = vec4f(1.0, 1.0, 0.0, 1.0);
  return color;
}`
                }),
                targets: [
                    {
                        format: 'rgba8unorm'
                    }
                ]
            },
            primitive: {
                topology: 'triangle-strip',
                stripIndexFormat: 'uint32'
            },
        });

        const vertexBuffer = this.device.createBuffer({
            size: 2*4*3,
            usage: GPUBufferUsage.VERTEX | GPUBufferUsage.COPY_DST
        });
        this.device.queue.writeBuffer(vertexBuffer, 0, new Float32Array([
            -1.0, -1.0,
            -1.0, 1.0,
            1.0, -1.0
        ]));

        const indexBuffer = this.device.createBuffer({
            size: 3*4,
            usage: GPUBufferUsage.INDEX | GPUBufferUsage.COPY_DST,
        });
        this.device.queue.writeBuffer(indexBuffer, 0, new Uint32Array([ 0, 1, 2 ]));

        const renderTarget = this.device.createTexture({
            size: {
                width: 5,
                height: 5
            },
            format: 'rgba8unorm',
            usage: GPUTextureUsage.RENDER_ATTACHMENT | GPUTextureUsage.COPY_SRC
        });

        const commandEncoder = this.device.createCommandEncoder();

        const passEncoder = commandEncoder.beginRenderPass({
            colorAttachments: [
                {
                    view: renderTarget.createView(),
                    clearValue: [0, 0, 1, 1],
                    loadOp: 'clear',
                    storeOp: 'store',
                }
            ]
        });
        passEncoder.setPipeline(pipeline);
        passEncoder.setVertexBuffer(0, vertexBuffer);
        passEncoder.setIndexBuffer(indexBuffer, "uint32")
        passEncoder.drawIndexed(3);
        passEncoder.end();

        this.device.queue.submit([commandEncoder.finish()]);

        await this.verifyTexture(renderTarget, [
            [  0,   0, 255, 255], [  0,   0, 255, 255], [  0,   0, 255, 255], [  0,   0, 255, 255], [  0,   0, 255, 255],
            [255, 255,   0, 255], [  0,   0, 255, 255], [  0,   0, 255, 255], [  0,   0, 255, 255], [  0,   0, 255, 255],
            [255, 255,   0, 255], [255, 255,   0, 255], [  0,   0, 255, 255], [  0,   0, 255, 255], [  0,   0, 255, 255],
            [255, 255,   0, 255], [255, 255,   0, 255], [255, 255,   0, 255], [  0,   0, 255, 255], [  0,   0, 255, 255],
            [255, 255,   0, 255], [255, 255,   0, 255], [255, 255,   0, 255], [255, 255,   0, 255], [  0,   0, 255, 255]
        ]);
    }

    // Create shader containing UTF-8 characters.
    async characterEncoding() {
        if (!await this.createDevice([])) {
            return;
        }
        
        const pipeline = this.device.createComputePipeline({
            layout: 'auto',
            compute: {
                module: this.device.createShaderModule({
                    code:
`@compute
@workgroup_size(1)
fn main() {
    // Test comment containing UTF-8 characters: 😀😎😰
}
`
                })
            }
        });
    }

    // Writes a value to a storage buffer based on a pipeline overridable constant.
    async pipelineOverridableConstant() {
        if (!await this.createDevice([])) {
            return;
        }

        const value = 23;
        const multiplier = 2;

        const pipeline = this.device.createComputePipeline({
            layout: 'auto',
            compute: {
                module: this.device.createShaderModule({
                    code:
`@group(0) @binding(0) var<storage, read_write> data: array<u32>;

@id(12) override value : u32 = 2;
override multiplier : u32 = 1;

@compute
@workgroup_size(1)
fn main() {
    data[0] = value * multiplier;
}
`
                }),
                constants: {
                    12: value,
                    multiplier: multiplier
                }
            }
        });

        const buffer = this.device.createBuffer({
            size: 4,
            usage: GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_SRC
        });

        const bindGroup = this.device.createBindGroup({
            layout: pipeline.getBindGroupLayout(0),
            entries: [
                {
                    binding: 0,
                    resource: buffer
                }
            ]
        });

        const commandEncoder = this.device.createCommandEncoder();
        const passEncoder = commandEncoder.beginComputePass({});
        passEncoder.setPipeline(pipeline);
        passEncoder.setBindGroup(0, bindGroup);
        passEncoder.dispatchWorkgroups(1, 1, 1);
        passEncoder.end();
        this.device.queue.submit([commandEncoder.finish()]);

        await this.verifyBuffer(buffer, [
            value * multiplier
        ]);
    }

    // Test that timestamp queries don't cause failures.
    // We can't test the timestamp values as they are non-deterministic.
    async timestampQueries() {
        if (!await this.createDevice(['timestamp-query'])) {
            return;
        }

        const querySet = this.device.createQuerySet({
            type: "timestamp",
            count: 4
        });

        // Timestamp queries in compute pass.
        const computePipeline = this.device.createComputePipeline({
            layout: 'auto',
            compute: {
                module: this.device.createShaderModule({
                    code:
`@group(0) @binding(0) var<storage, read_write> data: array<u32>;

@compute
@workgroup_size(1)
fn main() {
    data[0] = 54;
}
`
                })
            }
        });

        const buffer = this.device.createBuffer({
            size: 4,
            usage: GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_SRC
        });

        const resolveBuffer = this.device.createBuffer({
            size: 4 * 8,
            usage: GPUBufferUsage.QUERY_RESOLVE
        });

        const bindGroup = this.device.createBindGroup({
            layout: computePipeline.getBindGroupLayout(0),
            entries: [
                {
                    binding: 0,
                    resource: buffer
                }
            ]
        });

        const commandEncoder = this.device.createCommandEncoder();
        const computePassEncoder = commandEncoder.beginComputePass({
            timestampWrites: {
                querySet: querySet,
                beginningOfPassWriteIndex: 0,
                endOfPassWriteIndex: 1
            }
        });
        computePassEncoder.setPipeline(computePipeline);
        computePassEncoder.setBindGroup(0, bindGroup);
        computePassEncoder.dispatchWorkgroups(1, 1, 1);
        computePassEncoder.end();

        // Timestamp queries in render pass.
        const renderTarget = this.device.createTexture({
            size: {
                width: 1,
                height: 1
            },
            format: 'rgba8unorm',
            usage: GPUTextureUsage.RENDER_ATTACHMENT | GPUTextureUsage.COPY_SRC
        });

        const renderPassEncoder = commandEncoder.beginRenderPass({
            colorAttachments: [
                {
                    view: renderTarget.createView(),
                    clearValue: [0, 1, 0, 1],
                    loadOp: 'clear',
                    storeOp: 'store',
                }
            ],
            timestampWrites: {
                querySet: querySet,
                beginningOfPassWriteIndex: 2,
                endOfPassWriteIndex: 3
            }
        });
        renderPassEncoder.end();

        commandEncoder.resolveQuerySet(querySet, 0, 4, resolveBuffer, 0);

        this.device.queue.submit([commandEncoder.finish()]);

        await this.verifyBuffer(buffer, [54]);
        await this.verifyTexture(renderTarget, [
            [0, 255, 0, 255]
        ]);
    }

    // Test properties that can be either a sequence or a dictionary.
    // These are: GPUColor, GPUExtent2D, GPUExtent3D, GPUOrigin2D and GPUOrigin3D
    async sequenceOrDictionary() {
        if (!await this.createDevice([])) {
            return;
        }

        const runTest = async (clearColor, srcOrigin, dstOrigin, copySize, goldenImage) => {
            const renderTarget = this.device.createTexture({
                size: {
                    width: 2,
                    height: 2
                },
                format: 'rgba8unorm',
                usage: GPUTextureUsage.RENDER_ATTACHMENT | GPUTextureUsage.COPY_SRC | GPUTextureUsage.COPY_DST
            });

            // Use a render pass to clear the render target with the given clear color.
            const commandEncoder = this.device.createCommandEncoder();
            const renderPassEncoder = commandEncoder.beginRenderPass({
                colorAttachments: [
                    {
                        view: renderTarget.createView(),
                        clearValue: clearColor,
                        loadOp: 'clear',
                        storeOp: 'store',
                    }
                ]
            });
            renderPassEncoder.end();
            this.device.queue.submit([commandEncoder.finish()]);

            // Copy the specified part of the external image to the render target.
            const response = await fetch('externalImage.png');
            const imageBitmap = await createImageBitmap(await response.blob());
            this.device.queue.copyExternalImageToTexture({
                source: imageBitmap,
                origin: srcOrigin
            }, {
                texture: renderTarget,
                origin: dstOrigin
            }, copySize);

            await this.verifyTexture(renderTarget, goldenImage);
        };

        // Default values.
        await runTest(undefined, undefined, undefined, { width: 1 }, [
            [255, 255, 255, 255], [  0,   0,   0,   0],
            [  0,   0,   0,   0], [  0,   0,   0,   0]
        ]);

        // Dictionary with as many default values as possible.
        await runTest({ r: 1.0, g: 0.0, b: 1.0, a: 0}, {}, {}, { width: 1 }, [
            [255, 255, 255, 255], [255,   0, 255,   0],
            [255,   0, 255,   0], [255,   0, 255,   0]
        ]);

        // Fully specified dictionary.
        await runTest({ r: 1.0, g: 0.0, b: 1.0, a: 0}, { x: 1, y: 0 }, { x: 1, y: 0, z: 0 }, { width: 1, height: 2, depthOrArrayLayers: 1 }, [
            [255,   0, 255,   0], [255,   0,   0, 255],
            [255,   0, 255,   0], [  0, 255, 255, 255]
        ]);

        // Array with as many default values as possible.
        await runTest([1.0, 0.0, 1.0, 0.0], [], [], [1], [
            [255, 255, 255, 255], [255,   0, 255,   0],
            [255,   0, 255,   0], [255,   0, 255,   0]
        ]);

        // Fully specified array.
        await runTest([1.0, 0.0, 1.0, 0.0], [1, 0], [1, 0, 0], [1, 2, 1], [
            [255,   0, 255,   0], [255,   0,   0, 255],
            [255,   0, 255,   0], [  0, 255, 255, 255]
        ]);

        // Typed arrays with default values.
        await runTest(new Float32Array([1.0, 0.0, 1.0, 0.0]), new Float64Array([]), new Uint32Array([]), new Int32Array([1]), [
            [255, 255, 255, 255], [255,   0, 255,   0],
            [255,   0, 255,   0], [255,   0, 255,   0]
        ]);

        // Fully specified typed arrays.
        await runTest(new Float32Array([1.0, 0.0, 1.0, 0.0]), new Float64Array([1, 0]), new Uint32Array([1, 0, 0]), new Int32Array([1, 2, 1]), [
            [255,   0, 255,   0], [255,   0,   0, 255],
            [255,   0, 255,   0], [  0, 255, 255, 255]
        ]);

        // Fully specified Symbol.iterator
        await runTest({
            *[Symbol.iterator]() {
                yield 1.0;
                yield 0.0;
                yield 1.0;
                yield 0.0;
            },
        }, {
            *[Symbol.iterator]() {
                yield 1;
                yield 0;
            },
        }, {
            *[Symbol.iterator]() {
                yield 1;
                yield 0;
                yield 0;
            },
        }, {
            *[Symbol.iterator]() {
                yield 1;
                yield 2;
                yield 1;
            },
        }, [
            [255,   0, 255,   0], [255,   0,   0, 255],
            [255,   0, 255,   0], [  0, 255, 255, 255]
        ]);
    }

    // Test using immediates in compute pass encoder.
    async immediatesCompute() {
        if (!await this.createDevice([])) {
            return;
        }

        const runTest = async (rangeOffset, data, dataOffset, dataSize, referenceValue) => {
            const runInternal = async(autoLayout, rangeOffset, data, dataOffset, dataSize, referenceValue) => {
                const bindGroupLayout = this.device.createBindGroupLayout({
                    entries: [
                        {
                            binding: 0,
                            visibility: GPUShaderStage.COMPUTE,
                            buffer: {
                                type: "storage"
                            }
                        }
                    ]
                });

                const pipelineLayout = autoLayout ? undefined : this.device.createPipelineLayout({
                    bindGroupLayouts: [bindGroupLayout],
                    immediateSize: 16
                });

                const computePipeline = this.device.createComputePipeline({
                    layout: autoLayout ? 'auto' : pipelineLayout,
                    compute: {
                        module: this.device.createShaderModule({
                            code:
`@group(0) @binding(0) var<storage, read_write> data: array<u32>;

struct Immediates {
    value0: u32,
    value1: u32,
    value2: u32,
    value3: u32
};

var<immediate> immediates : Immediates;

@compute
@workgroup_size(1)
fn main() {
    data[0] = immediates.value2;
}
`
                        })
                    }
                });

                const buffer = this.device.createBuffer({
                    size: 4,
                    usage: GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_SRC
                });

                const bindGroup = this.device.createBindGroup({
                    layout: computePipeline.getBindGroupLayout(0),
                    entries: [
                        {
                            binding: 0,
                            resource: buffer
                        }
                    ]
                });

                const commandEncoder = this.device.createCommandEncoder();
                const passEncoder = commandEncoder.beginComputePass({});
                passEncoder.setPipeline(computePipeline);
                passEncoder.setBindGroup(0, bindGroup);
                passEncoder.setImmediates(0, new Uint32Array([0, 0, 0, 0]));
                passEncoder.setImmediates(rangeOffset, data, dataOffset, dataSize);
                passEncoder.dispatchWorkgroups(1, 1, 1);
                passEncoder.end();
                this.device.queue.submit([commandEncoder.finish()]);

                await this.verifyBuffer(buffer, [
                    referenceValue
                ]);
            };

            // Auto layout, TypedArray.
            await runInternal(true, rangeOffset, new Uint32Array(data), dataOffset, dataSize, referenceValue);

            // Explicit layout, TypedArray.
            await runInternal(false, rangeOffset, new Uint32Array(data), dataOffset, dataSize, referenceValue);

            // Auto layout, ArrayBuffer.
            const arrayBufferDataOffset = dataOffset === undefined ? undefined : dataOffset * 4;
            const arrayBufferDataSize = dataSize === undefined ? undefined : dataSize * 4;
            await runInternal(true, rangeOffset, new Uint32Array(data).buffer, arrayBufferDataOffset, arrayBufferDataSize, referenceValue);

            // Explicit layout, ArrayBuffer.
            await runInternal(false, rangeOffset, new Uint32Array(data).buffer, arrayBufferDataOffset, arrayBufferDataSize, referenceValue);

            // Auto layout, DataView
            await runInternal(true, rangeOffset, new DataView(new Uint32Array(data).buffer), arrayBufferDataOffset, arrayBufferDataSize, referenceValue);
            
            // Explicit layout, DataView.
            await runInternal(false, rangeOffset, new DataView(new Uint32Array(data).buffer), arrayBufferDataOffset, arrayBufferDataSize, referenceValue);
        };

        // Write full immediate data with default offset and size.
        await runTest(0, [0, 1, 54, 2], undefined, undefined, 54);

        // Write only value 2.
        await runTest(8, [54], undefined, undefined, 54);

        // Ensure we don't write over value 2 when specifying size.
        await runTest(4, [1, 2, 3, 4], undefined, 1, 0);

        // Write only value 2, with offset.
        await runTest(8, [1, 2, 3, 4, 54, 5, 6, 7], 4, 1, 54);
    }

    // Test using immediates in render pass encoder and render bundle encoder.
    async immediatesGraphics() {
        if (!await this.createDevice([])) {
            return;
        }
        
        const runTest = async (rangeOffset, data, dataOffset, dataSize, referenceValue) => {
            const runInternal = async(autoLayout, useRenderBundle, rangeOffset, data, dataOffset, dataSize, referenceValue) => {
                const pipelineLayout = autoLayout ? undefined : this.device.createPipelineLayout({
                    bindGroupLayouts: [],
                    immediateSize: 16
                });

                const pipeline = this.device.createRenderPipeline({
                    layout: autoLayout ? 'auto' : pipelineLayout,
                    vertex: {
                        module: this.device.createShaderModule({
                            code:
`struct VSOut {
  @builtin(position) pos : vec4f
};

@vertex
fn main(
    @builtin(vertex_index) VertexIndex : u32
) -> VSOut {
    var pos = array<vec2f, 3>(
        vec2(-1.0, 3.0),
        vec2(-1.0, -1.0),
        vec2(3.0, -1.0)
    );
    
    var out : VSOut;
    out.pos = vec4f(pos[VertexIndex], 0.0, 1.0);
    return out;
}
`
                        })
                    },
                    fragment: {
                        module: this.device.createShaderModule({
                            code:
`var<immediate> immediates : vec4f;

@fragment
fn main(

) -> @location(0) vec4f {
    var color : vec4f = immediates;
    return color;
}`
                        }),
                        targets: [
                            {
                                format: 'rgba8unorm'
                            }
                        ]
                    }
                });

                const renderTarget = this.device.createTexture({
                    size: {
                        width: 1,
                        height: 1
                    },
                    format: 'rgba8unorm',
                    usage: GPUTextureUsage.RENDER_ATTACHMENT | GPUTextureUsage.COPY_SRC
                });

                const commandEncoder = this.device.createCommandEncoder();

                const passEncoder = commandEncoder.beginRenderPass({
                    colorAttachments: [
                        {
                            view: renderTarget.createView(),
                            clearValue: [0, 0, 0, 0],
                            loadOp: 'clear',
                            storeOp: 'store',
                        }
                    ]
                });

                if (useRenderBundle) {
                    const bundleEncoder = this.device.createRenderBundleEncoder({
                        colorFormats: ['rgba8unorm']
                    });
                    bundleEncoder.setPipeline(pipeline);
                    bundleEncoder.setImmediates(0, new Float32Array([0.0, 0.0, 0.0, 0.0]));
                    bundleEncoder.setImmediates(rangeOffset, data, dataOffset, dataSize);
                    bundleEncoder.draw(3);

                    passEncoder.executeBundles([bundleEncoder.finish()]);
                } else {
                    passEncoder.setPipeline(pipeline);
                    passEncoder.setImmediates(0, new Float32Array([0.0, 0.0, 0.0, 0.0]));
                    passEncoder.setImmediates(rangeOffset, data, dataOffset, dataSize);
                    passEncoder.draw(3);
                }
                passEncoder.end();

                this.device.queue.submit([commandEncoder.finish()]);

                await this.verifyTexture(renderTarget, [referenceValue]);
            };

            const arrayBufferDataOffset = dataOffset === undefined ? undefined : dataOffset * 4;
            const arrayBufferDataSize = dataSize === undefined ? undefined : dataSize * 4;

            // Auto layout, render pass encoder, TypedArray.
            await runInternal(true, false, rangeOffset, new Float32Array(data), dataOffset, dataSize, referenceValue);

            // Explicit layout, render pass encoder, TypedArray.
            await runInternal(false, false, rangeOffset, new Float32Array(data), dataOffset, dataSize, referenceValue);

            // Auto layout, render bundle encoder, TypedArray.
            await runInternal(true, true, rangeOffset, new Float32Array(data), dataOffset, dataSize, referenceValue);

            // Explicit layout, render bundle encoder, TypedArray.
            await runInternal(false, true, rangeOffset, new Float32Array(data), dataOffset, dataSize, referenceValue);

            // Auto layout, render pass encoder, ArrayBuffer.
            await runInternal(true, false, rangeOffset, new Float32Array(data).buffer, arrayBufferDataOffset, arrayBufferDataSize, referenceValue);

            // Explicit layout, render pass encoder, ArrayBuffer.
            await runInternal(false, false, rangeOffset, new Float32Array(data).buffer, arrayBufferDataOffset, arrayBufferDataSize, referenceValue);

            // Auto layout, render bundle encoder, ArrayBuffer.
            await runInternal(true, true, rangeOffset, new Float32Array(data).buffer, arrayBufferDataOffset, arrayBufferDataSize, referenceValue);

            // Explicit layout, render bundle encoder, ArrayBuffer.
            await runInternal(false, true, rangeOffset, new Float32Array(data).buffer, arrayBufferDataOffset, arrayBufferDataSize, referenceValue);
            
            // Auto layout, render pass encoder, DataView.
            await runInternal(true, false, rangeOffset, new DataView(new Float32Array(data).buffer), arrayBufferDataOffset, arrayBufferDataSize, referenceValue);

            // Explicit layout, render pass encoder, DataView.
            await runInternal(false, false, rangeOffset, new DataView(new Float32Array(data).buffer), arrayBufferDataOffset, arrayBufferDataSize, referenceValue);

            // Auto layout, render bundle encoder, DataView.
            await runInternal(true, true, rangeOffset, new DataView(new Float32Array(data).buffer), arrayBufferDataOffset, arrayBufferDataSize, referenceValue);

            // Explicit layout, render bundle encoder, DataView.
            await runInternal(false, true, rangeOffset, new DataView(new Float32Array(data).buffer), arrayBufferDataOffset, arrayBufferDataSize, referenceValue);
        };

        // Write full immediate data with default offset and size.
        await runTest(0, [1.0, 1.0, 0.0, 1.0], undefined, undefined, [255, 255, 0, 255]);

        // Partial write.
        await runTest(4, [1.0, 1.0, 1.0], undefined, 2, [0, 255, 255, 0]);

        // Partial write with offset.
        await runTest(4, [0.3, 0.4, 0.5, 1.0, 1.0, 1.0], 3, 2, [0, 255, 255, 0]);
    }

    // Test GPUQueue.writeBuffer with different data sources, offsets and sizes.
    async writeBuffer() {
        if (!await this.createDevice([])) {
            return;
        }

        const runTest = async (bufferOffset, data, dataOffset, dataSize, referenceValue) => {
            const runInternal = async(bufferOffset, data, dataOffset, dataSize, referenceValue) => {
                const buffer = this.device.createBuffer({
                    size: 16,
                    usage: GPUBufferUsage.COPY_DST | GPUBufferUsage.COPY_SRC
                });

                this.device.queue.writeBuffer(buffer, bufferOffset, data, dataOffset, dataSize);

                await this.verifyBuffer(buffer, referenceValue);
            };

            const arrayBufferDataOffset = dataOffset === undefined ? undefined : dataOffset * 4;
            const arrayBufferDataSize = dataSize === undefined ? undefined : dataSize * 4;

            // TypedArray
            await runInternal(bufferOffset, new Uint32Array(data), dataOffset, dataSize, referenceValue);

            // ArrayBuffer
            await runInternal(bufferOffset, new Uint32Array(data).buffer, arrayBufferDataOffset, arrayBufferDataSize, referenceValue);

            // DataView
            await runInternal(bufferOffset, new DataView(new Uint32Array(data).buffer), arrayBufferDataOffset, arrayBufferDataSize, referenceValue);
        };

        // Full write with default offset and size.
        await runTest(0, [1, 2, 3, 4], undefined, undefined, [1, 2, 3, 4]);

        // Partial write.
        await runTest(4, [1, 2, 3], undefined, 2, [0, 1, 2, 0]);

        // Partial write with offset.
        await runTest(4, [1, 2, 3, 4, 5, 6], 3, undefined, [0, 4, 5, 6]);
    }

    // Create pipeline with/without unclippedDepth and ensure primitive is/isn't culled.
    async depthClipControl() {
        if (!await this.createDevice(['depth-clip-control'])) {
            return;
        }

        const runTest = async (unclippedDepth, referenceValue) => {
            const pipeline = this.device.createRenderPipeline({
                layout: 'auto',
                vertex: {
                    module: this.device.createShaderModule({
                        code:
`struct VSOut {
  @builtin(position) pos : vec4f
};

@vertex
fn main(
    @builtin(vertex_index) VertexIndex : u32
) -> VSOut {
    var pos = array<vec2f, 3>(
        vec2(-1.0, 3.0),
        vec2(-1.0, -1.0),
        vec2(3.0, -1.0)
    );
    
    var out : VSOut;
    out.pos = vec4f(pos[VertexIndex], 20.0, 1.0);
    return out;
}
`
                    })
                },
                fragment: {
                    module: this.device.createShaderModule({
                        code:
`@fragment
fn main(

) -> @location(0) vec4f {
    return vec4f(0.0, 1.0, 0.0, 1.0);
}`
                    }),
                    targets: [
                        {
                            format: 'rgba8unorm'
                        }
                    ]
                },
                primitive: {
                    unclippedDepth: unclippedDepth
                }
            });

            const renderTarget = this.device.createTexture({
                size: {
                    width: 1,
                    height: 1
                },
                format: 'rgba8unorm',
                usage: GPUTextureUsage.RENDER_ATTACHMENT | GPUTextureUsage.COPY_SRC
            });

            const commandEncoder = this.device.createCommandEncoder();

            const passEncoder = commandEncoder.beginRenderPass({
                colorAttachments: [
                    {
                        view: renderTarget.createView(),
                        clearValue: [1, 0, 0, 0],
                        loadOp: 'clear',
                        storeOp: 'store',
                    }
                ]
            });

            passEncoder.setPipeline(pipeline);
            passEncoder.draw(3);

            passEncoder.end();

            this.device.queue.submit([commandEncoder.finish()]);

            await this.verifyTexture(renderTarget, [referenceValue]);
        };

        await runTest(false, [255, 0, 0, 0]);
        await runTest(true, [0, 255, 0, 255]);
    }
}

const tests = new Tests();

const searchParams = new URLSearchParams(window.location.search);
await tests.runTest(searchParams.get("test"));
