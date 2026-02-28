# Start at 100 to leave some room for hardcoded commands.
commandId = 100
mapString = ""
finalizationRegistryString = ""
runCommandsString = ""

# A type that is identified by an id.
class IdType:
    def __init__(self, webName, nativeName = "", releaseFunction = ""):
        global commandId
        global mapString
        global finalizationRegistryString
        global runCommandsString
        
        self.webName = webName
        self.nativeName = nativeName
        self.releaseFunction = releaseFunction
        if nativeName == "":
            self.nativeName = 'W' + webName
        if releaseFunction != "":
            commandId += 1
            
            finalizationRegistryString += '__WebGPUReconstruct_DebugOutput("' + self.webName + ' destroyed");\n'
            finalizationRegistryString += 'this.' + self.webName + 'FinalizationRegistry = new FinalizationRegistry((id) => {\n'
            finalizationRegistryString += '__WebGPUReconstruct_file.writeUint32(' + str(commandId) + ');\n'
            finalizationRegistryString += '__WebGPUReconstruct_file.writeUint32(id);\n'
            finalizationRegistryString += '});\n'
            
            runCommandsString += 'case ' + str(commandId) + ':\n{\n'
            runCommandsString += 'DebugOutput("' + self.webName + ' destroyed\\n");\n'
            runCommandsString += 'ReleaseIdType(map' + self.webName + ', reader.ReadUint32(), ' + releaseFunction + ');\n'
            runCommandsString += 'break;\n}\n'
        
        mapString += 'std::unordered_map<uint32_t, ' + self.nativeName + '> map' + self.webName + ';\n'
    
    def save(self, name):
        capture = 'if (' + name + ' == undefined) {\n'
        capture += '__WebGPUReconstruct_file.writeUint32(0);\n'
        capture += '} else {\n'
        capture += '__WebGPUReconstruct_file.writeUint32(' + name + '.__id);\n'
        capture += '}\n'
        return capture
    
    def load(self, name):
        replay = name + ' = GetIdType(map' + self.webName + ', reader.ReadUint32());\n'
        return replay
    
    def declare_argument(self, name):
        return self.nativeName + ' ' + name + ';\n'
    
    def as_argument(self, name):
        return name
    
    def cleanup(self, name):
        return ''
    
    def finalization(self, name):
        if self.releaseFunction != "":
            return '__webGPUReconstruct.' + self.webName + 'FinalizationRegistry.register(' + name + ', ' + name + '.__id);\n'
        return ''

GPUBuffer = IdType("GPUBuffer", "", "wgpuBufferRelease")
GPUTexture = IdType("GPUTexture", "", "wgpuTextureRelease")
GPUTextureView = IdType("GPUTextureView", "", "wgpuTextureViewRelease")
GPUSampler = IdType("GPUSampler", "", "wgpuSamplerRelease")
GPUBindGroupLayout = IdType("GPUBindGroupLayout", "", "wgpuBindGroupLayoutRelease")
GPUBindGroup = IdType("GPUBindGroup", "", "wgpuBindGroupRelease")
GPUPipelineLayout = IdType("GPUPipelineLayout", "", "wgpuPipelineLayoutRelease")
GPUShaderModule = IdType("GPUShaderModule", "", "wgpuShaderModuleRelease")
GPUComputePipeline = IdType("GPUComputePipeline", "", "wgpuComputePipelineRelease")
GPURenderPipeline = IdType("GPURenderPipeline", "", "wgpuRenderPipelineRelease")
GPUCommandBuffer = IdType("GPUCommandBuffer", "", "wgpuCommandBufferRelease")
GPUCommandEncoder = IdType("GPUCommandEncoder", "", "wgpuCommandEncoderRelease")
GPUComputePassEncoder = IdType("GPUComputePassEncoder", "", "wgpuComputePassEncoderRelease")
GPURenderPassEncoder = IdType("GPURenderPassEncoder", "", "wgpuRenderPassEncoderRelease")
GPURenderBundle = IdType("GPURenderBundle", "", "wgpuRenderBundleRelease")
GPURenderBundleEncoder = IdType("GPURenderBundleEncoder", "", "wgpuRenderBundleEncoderRelease")
GPUQuerySet = IdType("GPUQuerySet", "", "wgpuQuerySetRelease")