import WebGPUReconstruct from "./WebGPUReconstruct.js";

class Tests {
    async runTest(test) {
        WebGPUReconstruct.start({
            captureFilename: `${test}.wgpur`,
            bufferCaptureReadbackData: true
        });

        this.canvas = document.querySelector('canvas');
        this.adapter = await navigator.gpu.requestAdapter();
        await this[test]();

        WebGPUReconstruct.finish();

        document.getElementById("result").style.display = "inline";
    }

    async createDevice(features) {
        // TODO Check feature support before attempting to create the device.

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
}

const tests = new Tests();

const searchParams = new URLSearchParams(window.location.search);
await tests.runTest(searchParams.get("test"));
