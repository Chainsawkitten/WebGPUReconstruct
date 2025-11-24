const __WebGPUReconstruct_blockSize = 1024 * 1024;

class __WebGPUReconstruct_Uint8Writer {
    grow() {
        this.currentSize = 0;
        this.arrays.push(new Uint8Array(__WebGPUReconstruct_blockSize));
    }
    
    constructor() {
        this.arrays = [];
        this.currentSize = 0;
        this.grow();
        
        // Create conversion buffers once and reuse them.
        this.convertUint64Array = new BigUint64Array(1);
        this.convertUint64ArrayUint8 = new Uint8Array(this.convertUint64Array.buffer);
        
        this.convertInt32Array = new Int32Array(1);
        this.convertInt32ArrayUint8 = new Uint8Array(this.convertInt32Array.buffer);
        
        this.convertFloat32Array = new Float32Array(1);
        this.convertFloat32ArrayUint8 = new Uint8Array(this.convertFloat32Array.buffer);
        
        this.convertFloat64Array = new Float64Array(1);
        this.convertFloat64ArrayUint8 = new Uint8Array(this.convertFloat64Array.buffer);
    }
    
    writeUint8(value) {
        if (this.currentSize >= __WebGPUReconstruct_blockSize) {
            this.grow();
        }
        
        this.arrays[this.arrays.length - 1][this.currentSize] = value;
        this.currentSize += 1;
    }
    
    writeUint16(value) {
        this.writeUint8(value);
        this.writeUint8(value >>> 8);
    }
    
    writeUint32(value) {
        this.writeUint8(value);
        this.writeUint8(value >>> 8);
        this.writeUint8(value >>> 16);
        this.writeUint8(value >>> 24);
    }
    
    writeUint64(value) {
        if (value == undefined) {
            value = 0;
        }
        
        this.convertUint64Array[0] = BigInt(value);
        
        this.writeUint8(this.convertUint64ArrayUint8[0]);
        this.writeUint8(this.convertUint64ArrayUint8[1]);
        this.writeUint8(this.convertUint64ArrayUint8[2]);
        this.writeUint8(this.convertUint64ArrayUint8[3]);
        this.writeUint8(this.convertUint64ArrayUint8[4]);
        this.writeUint8(this.convertUint64ArrayUint8[5]);
        this.writeUint8(this.convertUint64ArrayUint8[6]);
        this.writeUint8(this.convertUint64ArrayUint8[7]);
    }
    
    writeInt32(value) {
        this.convertInt32Array[0] = value;
        
        this.writeUint8(this.convertInt32ArrayUint8[0]);
        this.writeUint8(this.convertInt32ArrayUint8[1]);
        this.writeUint8(this.convertInt32ArrayUint8[2]);
        this.writeUint8(this.convertInt32ArrayUint8[3]);
    }
    
    writeFloat32(value) {
        this.convertFloat32Array[0] = value;
        
        this.writeUint8(this.convertFloat32ArrayUint8[0]);
        this.writeUint8(this.convertFloat32ArrayUint8[1]);
        this.writeUint8(this.convertFloat32ArrayUint8[2]);
        this.writeUint8(this.convertFloat32ArrayUint8[3]);
    }
    
    writeFloat64(value) {
        this.convertFloat64Array[0] = value;
        
        this.writeUint8(this.convertFloat64ArrayUint8[0]);
        this.writeUint8(this.convertFloat64ArrayUint8[1]);
        this.writeUint8(this.convertFloat64ArrayUint8[2]);
        this.writeUint8(this.convertFloat64ArrayUint8[3]);
        this.writeUint8(this.convertFloat64ArrayUint8[4]);
        this.writeUint8(this.convertFloat64ArrayUint8[5]);
        this.writeUint8(this.convertFloat64ArrayUint8[6]);
        this.writeUint8(this.convertFloat64ArrayUint8[7]);
    }
    
    writeString(value) {
        this.writeUint64(value.length);
        for (let i = 0; i < value.length; i += 1) {
            this.writeUint8(value.charCodeAt(i));
        }
    }
    
    reserve(size) {
        let reservedPosition = { array: this.arrays.length - 1, size: this.currentSize };
        
        this.currentSize += size;
        while (this.currentSize >= __WebGPUReconstruct_blockSize) {
            this.arrays.push(new Uint8Array(__WebGPUReconstruct_blockSize));
            this.currentSize -= __WebGPUReconstruct_blockSize;
        }
        
        return reservedPosition;
    }
    
    writeReserved(reservedPosition, uint8Array) {
        let currentArray = reservedPosition.array;
        let currentSize = reservedPosition.size;
        
        let offset = 0;
        let bytesToWrite = uint8Array.length;
        
        while (bytesToWrite > 0) {
            if (currentSize + bytesToWrite < __WebGPUReconstruct_blockSize) {
                // Write all the remaining bytes.
                this.arrays[currentArray].set(uint8Array.subarray(offset, offset + bytesToWrite), currentSize);
                bytesToWrite = 0;
            } else {
                // Write as many bytes as we can fit.
                let bytesThatFit = __WebGPUReconstruct_blockSize - currentSize;
                this.arrays[currentArray].set(uint8Array.subarray(offset, offset + bytesThatFit), currentSize);
                currentArray++;
                currentSize = 0;
                bytesToWrite -= bytesThatFit;
                offset += bytesThatFit;
            }
        }
    }
    
    writeBuffer(uint8Array, offset, size) {
        let reservedPosition = this.reserve(size);
        this.writeReserved(reservedPosition, uint8Array.subarray(offset, offset + size));
    }
}

function __WebGPUReconstruct_DebugOutput(output) {
    if (__WebGPUReconstruct_DEBUG) {
        console.log(output);
    }
}

let __WebGPUReconstruct_file = new __WebGPUReconstruct_Uint8Writer();

// Used to add an ID to WebGPU objects for tracking purposes.
let __WebGPUReconstruct_nextId = 1;
function __WebGPUReconstruct_AddId(object) {
    object.__id = __WebGPUReconstruct_nextId
    __WebGPUReconstruct_nextId += 1
}

// Helper functions.
function __WebGPUReconstruct_get_block_size(format) {
    switch (format) {
        // BC compressed formats.
        case "bc1-rgba-unorm":
        case "bc1-rgba-unorm-srgb":
        case "bc4-r-unorm":
        case "bc4-r-snorm":
        case "bc2-rgba-unorm":
        case "bc2-rgba-unorm-srgb":
        case "bc3-rgba-unorm":
        case "bc3-rgba-unorm-srgb":
        case "bc5-rg-unorm":
        case "bc5-rg-snorm":
        case "bc6h-rgb-ufloat":
        case "bc6h-rgb-float":
        case "bc7-rgba-unorm":
        case "bc7-rgba-unorm-srgb":
        return {x: 4, y: 4};

        // ETC2 compressed formats.
        case "etc2-rgb8unorm":
        case "etc2-rgb8unorm-srgb":
        case "etc2-rgb8a1unorm":
        case "etc2-rgb8a1unorm-srgb":
        case "eac-r11unorm":
        case "eac-r11snorm":
        case "etc2-rgba8unorm":
        case "etc2-rgba8unorm-srgb":
        case "eac-rg11unorm":
        case "eac-rg11snorm":
        return {x: 4, y: 4};

        // ASTC compressed formats.
        case "astc-4x4-unorm":
        case "astc-4x4-unorm-srgb":
        return {x: 4, y: 4};
        case "astc-5x4-unorm":
        case "astc-5x4-unorm-srgb":
        return {x: 5, y: 4};
        case "astc-5x5-unorm":
        case "astc-5x5-unorm-srgb":
        return {x: 5, y: 5};
        case "astc-6x5-unorm":
        case "astc-6x5-unorm-srgb":
        return {x: 6, y: 5};
        case "astc-6x6-unorm":
        case "astc-6x6-unorm-srgb":
        return {x: 6, y: 6};
        case "astc-8x5-unorm":
        case "astc-8x5-unorm-srgb":
        return {x: 8, y: 5};
        case "astc-8x6-unorm":
        case "astc-8x6-unorm-srgb":
        return {x: 8, y: 6};
        case "astc-8x8-unorm":
        case "astc-8x8-unorm-srgb":
        return {x: 8, y: 8};
        case "astc-10x5-unorm":
        case "astc-10x5-unorm-srgb":
        return {x: 10, y: 5};
        case "astc-10x6-unorm":
        case "astc-10x6-unorm-srgb":
        return {x: 10, y: 6};
        case "astc-10x8-unorm":
        case "astc-10x8-unorm-srgb":
        return {x: 10, y: 8};
        case "astc-10x10-unorm":
        case "astc-10x10-unorm-srgb":
        return {x: 10, y: 10};
        case "astc-12x10-unorm":
        case "astc-12x10-unorm-srgb":
        return {x: 12, y: 10};
        case "astc-12x12-unorm":
        case "astc-12x12-unorm-srgb":
        return {x: 12, y: 12};
        
        default:
        return {x: 1, y: 1};
    }
}

function __WebGPUReconstruct_get_bytes_per_block(format) {
    switch (format) {
        // 8-bit formats
        case "r8unorm":
        case "r8snorm":
        case "r8uint":
        case "r8sint":
        case "stencil8":
        return 1;
        
        // 16-bit formats
        case "r16uint":
        case "r16sint":
        case "r16float":
        case "rg8unorm":
        case "rg8snorm":
        case "rg8uint":
        case "rg8sint":
        case "depth16unorm":
        return 2;
        
        // 32-bit formats
        case "r32uint":
        case "r32sint":
        case "r32float":
        case "rg16uint":
        case "rg16sint":
        case "rg16float":
        case "rgba8unorm":
        case "rgba8unorm-srgb":
        case "rgba8snorm":
        case "rgba8uint":
        case "rgba8sint":
        case "bgra8unorm":
        case "bgra8unorm-srgb":
        case "rgb9e5ufloat":
        case "rgb10a2uint":
        case "rgb10a2unorm":
        case "rg11b10ufloat":
        return 4;
        
        // 64-bit formats
        case "rg32uint":
        case "rg32sint":
        case "rg32float":
        case "rgba16uint":
        case "rgba16sint":
        case "rgba16float":
        return 8;
        
        // 128-bit formats
        case "rgba32uint":
        case "rgba32sint":
        case "rgba32float":
        return 16;
        
        // Depth/stencil formats
        case "depth24plus":
        case "depth24plus-stencil8":
        case "depth32float":
        case "depth32float-stencil8":
        console.assert(false);
        return 0;

        // BC compressed formats.
        case "bc1-rgba-unorm":
        case "bc1-rgba-unorm-srgb":
        case "bc4-r-unorm":
        case "bc4-r-snorm":
        return 8;
        case "bc2-rgba-unorm":
        case "bc2-rgba-unorm-srgb":
        case "bc3-rgba-unorm":
        case "bc3-rgba-unorm-srgb":
        case "bc5-rg-unorm":
        case "bc5-rg-snorm":
        case "bc6h-rgb-ufloat":
        case "bc6h-rgb-float":
        case "bc7-rgba-unorm":
        case "bc7-rgba-unorm-srgb":
        return 16;

        // ETC2 compressed formats.
        case "etc2-rgb8unorm":
        case "etc2-rgb8unorm-srgb":
        case "etc2-rgb8a1unorm":
        case "etc2-rgb8a1unorm-srgb":
        case "eac-r11unorm":
        case "eac-r11snorm":
        return 8;
        case "etc2-rgba8unorm":
        case "etc2-rgba8unorm-srgb":
        case "eac-rg11unorm":
        case "eac-rg11snorm":
        return 16;

        // ASTC compressed formats.
        case "astc-4x4-unorm":
        case "astc-4x4-unorm-srgb":
        case "astc-5x4-unorm":
        case "astc-5x4-unorm-srgb":
        case "astc-5x5-unorm":
        case "astc-5x5-unorm-srgb":
        case "astc-6x5-unorm":
        case "astc-6x5-unorm-srgb":
        case "astc-6x6-unorm":
        case "astc-6x6-unorm-srgb":
        case "astc-8x5-unorm":
        case "astc-8x5-unorm-srgb":
        case "astc-8x6-unorm":
        case "astc-8x6-unorm-srgb":
        case "astc-8x8-unorm":
        case "astc-8x8-unorm-srgb":
        case "astc-10x5-unorm":
        case "astc-10x5-unorm-srgb":
        case "astc-10x6-unorm":
        case "astc-10x6-unorm-srgb":
        case "astc-10x8-unorm":
        case "astc-10x8-unorm-srgb":
        case "astc-10x10-unorm":
        case "astc-10x10-unorm-srgb":
        case "astc-12x10-unorm":
        case "astc-12x10-unorm-srgb":
        case "astc-12x12-unorm":
        case "astc-12x12-unorm-srgb":
        return 16;
        
        default:
        console.assert(false);
        return 0;
    }
}

// Features supported by WebGPUReconstruct. We will pretend the adapter doesn't support any other features.
// TODO: dual-source-blending, texture-formats-tier1, texture-formats-tier2, texture-component-swizzle
const __WebGPUReconstruct_supportedFeatures = new Set([
    "core-features-and-limits",
    "depth-clip-control",
    "depth32float-stencil8",
    "texture-compression-bc",
    "texture-compression-bc-sliced-3d",
    "texture-compression-etc2",
    "texture-compression-astc",
    "texture-compression-astc-sliced-3d",
    "timestamp-query",
    "indirect-first-instance",
    "shader-f16",
    "rg11b10ufloat-renderable",
    "bgra8unorm-storage",
    "float32-filterable",
    "float32-blendable",
    "clip-distances",
    "subgroups",
    "primitive-index",
]);

function __WebGPUReconstruct_GPUAdapter_requestDevice(originalMethod, descriptor) {
    __WebGPUReconstruct_DebugOutput("requestDevice");
    __WebGPUReconstruct_file.writeUint32(5);
    
    let overrideDescriptor = {};
    overrideDescriptor.requiredFeatures = [];
    
    if (descriptor != undefined) {
        overrideDescriptor.label = descriptor.label;
        overrideDescriptor.requiredLimits = descriptor.requiredLimits;
        overrideDescriptor.defaultQueue = descriptor.defaultQueue;
        
        if (descriptor.requiredFeatures != undefined) {
            for (const feature of descriptor.requiredFeatures) {
                if (__WebGPUReconstruct_supportedFeatures.has(String(feature))) {
                    overrideDescriptor.requiredFeatures.push(feature);
                } else {
                    console.error("Unsupported feature: " + feature);
                }
            }
        }
    }
    
    __WebGPUReconstruct_file.writeUint8(overrideDescriptor.requiredFeatures.includes("subgroups") ? 1 : 0);
    __WebGPUReconstruct_file.writeUint32(this.info.subgroupMinSize);
    __WebGPUReconstruct_file.writeUint32(this.info.subgroupMaxSize);
    
    return originalMethod.call(this, overrideDescriptor).then((device) => {
        // Store the device so it can be used to create textures and buffers in copyExternalImageToTexture.
        device.queue.__device = device;
        return device;
    });
}

// Functions used to store enums.
// Generated code will be inserted here.
$ENUM_SAVE_FUNCTIONS

// Functions used to store information about WebGPU structs.
// Generated code will be inserted here.
$STRUCT_SAVE_FUNCTIONS

// Functions used to store information about WebGPU function calls.
// Generated code will be inserted here.
$CAPTURE_COMMANDS

function __WebGPUReconstruct_GPU_requestAdapter(originalMethod, options) {
    __WebGPUReconstruct_DebugOutput("requestAdapter");
    
    return __webGPUReconstruct.optionsPromise.then(() => {
        return originalMethod.call(this, options).then((adapter) => {
            let features = new Set();
            for (const value of adapter.features) {
                if (__WebGPUReconstruct_supportedFeatures.has(value)) {
                    features.add(value);
                }
            }
            adapter.__defineGetter__("features", function() { return features;});
            return adapter;
        });
    });
}

let __WebGPUReconstruct_firstAnimationFrame = true;
let __WebGPUReconstruct_getCurrentTexture_called = false;

function __WebGPUReconstruct_requestAnimationFrame_callback(timestamp) {
    if (__WebGPUReconstruct_firstAnimationFrame) {
        __WebGPUReconstruct_file.writeUint32(1);
        __WebGPUReconstruct_firstAnimationFrame = false;
    } else if (__WebGPUReconstruct_getCurrentTexture_called) {
        __WebGPUReconstruct_file.writeUint32(2);
        __WebGPUReconstruct_file.writeUint32(1);
        __WebGPUReconstruct_getCurrentTexture_called = false;
    }
    __webGPUReconstruct.animationFrameID = requestAnimationFrame(__WebGPUReconstruct_requestAnimationFrame_callback);
}

function __WebGPUReconstruct_getExternalTextureBlitPipeline(device) {
    if (device.__externalTextureBlitPipeline == undefined) {
        const vertexWgsl =
`
struct VertexOutput {
  @builtin(position) Position : vec4f,
  @location(0) fragUV : vec2f,
}

@vertex
fn main(
  @builtin(vertex_index) VertexIndex : u32
) -> VertexOutput {
  var pos = array<vec2f, 3>(
    vec2(-1.0, 3.0),
    vec2(-1.0, -1.0),
    vec2(3.0, -1.0)
  );
  var uv = array<vec2f, 3>(
    vec2(0.0, -1.0),
    vec2(0.0, 1.0),
    vec2(2.0, 1.0)
  );
  
  var output : VertexOutput;
  output.Position = vec4f(pos[VertexIndex], 0.0, 1.0);
  output.fragUV = uv[VertexIndex];

  return output;
}
`;

        const fragmentWgsl =
`
struct FSIn {
  @location(0) uv : vec2f
};

@group(0) @binding(0) var mySampler: sampler;
@group(0) @binding(1) var myTexture: texture_external;

@fragment
fn main(in : FSIn) -> @location(0) vec4f {
  var color : vec4f = textureSampleBaseClampToEdge(myTexture, mySampler, in.uv);
  return color;
}
`;

        device.__externalTextureBlitPipeline = __webGPUReconstruct.GPUDevice_createRenderPipeline_original.call(device, {
            label: "External texture blit pipeline",
            layout: "auto",
            vertex: {
                module: __webGPUReconstruct.GPUDevice_createShaderModule_original.call(device, {
                    code: vertexWgsl
                })
            },
            fragment: {
                module: __webGPUReconstruct.GPUDevice_createShaderModule_original.call(device, {
                    code: fragmentWgsl
                }),
                targets: [
                    {
                        format: "rgba8unorm"
                    },
                ]
            }
        });
    }
    
    return device.__externalTextureBlitPipeline;
}

function __WebGPUReconstruct_getExternalTextureBlitSampler(device) {
    if (device.__externalTextureBlitSampler == undefined) {
        device.__externalTextureBlitSampler = __webGPUReconstruct.GPUDevice_createSampler_original.call(device);
    }
    
    return device.__externalTextureBlitSampler;
}

function __WebGPUReconstruct_GPUBuffer_unmap(originalMethod) {
    __WebGPUReconstruct_DebugOutput("unmap");
    if (this.__readOnly) {
        __WebGPUReconstruct_file.writeUint32(4);
        __WebGPUReconstruct_file.writeUint32(this.__id);
    } else {
        __WebGPUReconstruct_file.writeUint32(3);
        __WebGPUReconstruct_file.writeUint32(this.__id);
        
        // Capture buffer contents in all mapped ranges right before unmap().
        if (this.__mappedRanges == undefined) {
            this.__mappedRanges = [];
        }
        
        __WebGPUReconstruct_file.writeUint64(this.__mappedRanges.length);
        for (let range = 0; range < this.__mappedRanges.length; range += 1) {
            __WebGPUReconstruct_file.writeUint64(this.__mappedRanges[range][0]);
            let size = this.__mappedRanges[range][1];
            __WebGPUReconstruct_file.writeUint64(size);
            let bufferContents = new Uint8Array(this.__mappedRanges[range][2]);
            for (let i = 0; i < size; i += 1) {
                __WebGPUReconstruct_file.writeUint8(bufferContents[i]);
            }
        }
    }
    
    this.__mappedRanges = undefined;
    
    originalMethod.call(this);
}

function __WebGPUReconstruct_GPUDevice_createRenderPipelineAsync(originalMethod, descriptor) {
    __WebGPUReconstruct_DebugOutput("createRenderPipelineAsync");
    let pipeline = this.createRenderPipeline(descriptor);
    return new Promise((resolve, reject) => { resolve(pipeline); });
}

function __WebGPUReconstruct_GPUDevice_createComputePipelineAsync(originalMethod, descriptor) {
    __WebGPUReconstruct_DebugOutput("createComputePipelineAsync");
    let pipeline = this.createComputePipeline(descriptor);
    return new Promise((resolve, reject) => { resolve(pipeline); });
}

// Class used to hook WebGPU functions.
class __WebGPUReconstruct {
    constructor() {
        __WebGPUReconstruct_DebugOutput("Starting WebGPU Reconstruct");
        
        this.firstCapture = true;
        
        __WebGPUReconstruct_file.writeUint32($FILE_VERSION);
        __WebGPUReconstruct_file.writeUint32($VERSION_MAJOR);
        __WebGPUReconstruct_file.writeUint32($VERSION_MINOR);
        
        GPUAdapter.prototype.requestDevice = this.wrapMethodPre(GPUAdapter.prototype.requestDevice, __WebGPUReconstruct_GPUAdapter_requestDevice, "GPUAdapter_requestDevice");
        GPU.prototype.requestAdapter = this.wrapMethodPre(GPU.prototype.requestAdapter, __WebGPUReconstruct_GPU_requestAdapter, "GPU_requestAdapter");
        GPUBuffer.prototype.unmap = this.wrapMethodPre(GPUBuffer.prototype.unmap, __WebGPUReconstruct_GPUBuffer_unmap, "GPUBuffer_unmap");
        GPUDevice.prototype.createRenderPipelineAsync = this.wrapMethodPre(GPUDevice.prototype.createRenderPipelineAsync, __WebGPUReconstruct_GPUDevice_createRenderPipelineAsync, "GPUDevice_createRenderPipelineAsync");
        GPUDevice.prototype.createComputePipelineAsync = this.wrapMethodPre(GPUDevice.prototype.createComputePipelineAsync, __WebGPUReconstruct_GPUDevice_createComputePipelineAsync, "GPUDevice_createComputePipelineAsync");

$WRAP_COMMANDS

        requestAnimationFrame(__WebGPUReconstruct_requestAnimationFrame_callback);
        this.configure({});
    }
    
    wrapMethodPost(originalMethod, hook, originalName) {
        this[originalName + "_original"] = originalMethod;
        const reconstruct = this;
        return function() {
            const object = this;
            const args = [...arguments];
            
            const result = originalMethod.call(object, ...args);
            
            hook.call(object, result, ...args);
            
            return result;
        }
    }
    
    wrapMethodPre(originalMethod, hook, originalName) {
        this[originalName + "_original"] = originalMethod;
        return function() {
            const args = [...arguments];
            return hook.call(this, originalMethod, ...args);
        }
    }

    configure(configuration) {
        this.configuration = configuration;
        if (this.configuration == undefined) {
            this.configuration = {};
        }
        
        if (this.configuration.externalTextureScale === undefined) {
            this.configuration.externalTextureScale = 100;
        } else {
            this.configuration.externalTextureScale = Number(this.configuration.externalTextureScale);
        }
        
        if (this.configuration.captureFilename === undefined) {
            this.configuration.captureFilename = "capture.wgpur";
        }
    }

    finishCapture() {
        if (!this.firstCapture) {
            console.error("You need to reload the page between captures.");
            return;
        }
        this.firstCapture = false;

        // End of last frame.
        if (__WebGPUReconstruct_getCurrentTexture_called) {
            __WebGPUReconstruct_file.writeUint32(2);
        }
        
        // End of capture.
        __WebGPUReconstruct_file.writeUint32(0);

        if (this.animationFrameID != undefined) {
            cancelAnimationFrame(this.animationFrameID);
        }

        // Reset wrapped functions.
        GPUAdapter.prototype.requestDevice = this.GPUAdapter_requestDevice_original;
        GPU.prototype.requestAdapter = this.GPU_requestAdapter_original;
        GPUBuffer.prototype.unmap = this.GPUBuffer_unmap_original;
        GPUDevice.prototype.createRenderPipelineAsync = this.GPUDevice_createRenderPipelineAsync_original;
        GPUDevice.prototype.createComputePipelineAsync = this.GPUDevice_createComputePipelineAsync_original;

$RESET_COMMANDS

        const blob = new Blob(__WebGPUReconstruct_file.arrays);

        if (typeof(document) !== "undefined") {
            // Create and click on a download link to save capture.
            let a = document.createElement('a');
            a.download = this.configuration.captureFilename;
            a.href = URL.createObjectURL(blob);
            a.click();
        } else {
            // Post a message for the main script to handle.
            postMessage({ type: "WebGPUCapture", data: blob });
        }
    }
}
