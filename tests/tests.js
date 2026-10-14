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
}

const tests = new Tests();

const searchParams = new URLSearchParams(window.location.search);
await tests.runTest(searchParams.get("test"));
