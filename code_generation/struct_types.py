from code_generation.non_captured_types import *
from code_generation.enum_types import *
from code_generation.custom_types import *
from code_generation.unsupported_type import *

# Composite type.
class StructType:
    def __init__(self, webName, members):
        self.webName = webName
        self.nativeName = "W" + webName
        self.members = members
    
    def save(self, name, isInArray = False):
        capture = ''
        if isInArray:
            for member in self.members:
                if len(member) >= 3:
                    capture += 'if (' + name + '.' + member[1] + ' == undefined) {\n'
                    capture += name + '.' + member[1] + ' = ' + member[2] + '\n'
                    capture += '}\n'
                
                capture += member[0].save(name + '.' + member[1])
        else:
            capture += 'if (' + name  + ' == undefined) {\n'
            capture += '__WebGPUReconstruct_file.writeUint8(0);\n'
            capture += '} else {\n'
            capture += '__WebGPUReconstruct_file.writeUint8(1);\n'
            for member in self.members:
                # Set default value (if one was specified).
                if len(member) >= 3:
                    capture += 'if (' + name + '.' + member[1] + ' == undefined) {\n'
                    capture += name + '.' + member[1] + ' = ' + member[2] + '\n'
                    capture += '}\n'
                
                capture += member[0].save(name + '.' + member[1])
            capture += '}\n'
        return capture
    
    def load(self, name, isInArray = False):
        replay = ''
        if isInArray:
            replay += name + ' = {};\n'
            for member in self.members:
                replay += member[0].load(name + '.' + member[1])
        else:
            replay += 'if (reader.ReadUint8()) {\n'
            replay += name + ' = new ' + self.nativeName + ';\n'
            replay += '*const_cast<' + self.nativeName + '*>(' + name + ') = {};\n'
            
            for member in self.members:
                replay += member[0].load('const_cast<' + self.nativeName + '*>(' + name + ')->' + member[1])
            
            replay += '} else {\n'
            replay += name + ' = nullptr;\n'
            replay += '}\n'
        return replay
    
    def declare_argument(self, name):
        return self.nativeName + '* ' + name + ';\n'
    
    def as_argument(self, name):
        return name
    
    def cleanup(self, name, isInArray = False):
        cleanup = ''
        if isInArray:
            for member in self.members:
                cleanup += member[0].cleanup(name + '.' + member[1])
        else:
            cleanup += 'if (' + name + ' != nullptr) {\n'
            for member in self.members:
                cleanup += member[0].cleanup(name + '->' + member[1])
            cleanup += 'delete ' + name + ';\n'
            cleanup += '}\n'
        return cleanup

# Struct that's included directly inside another struct (as opposed to a pointer to a struct).
class SubStructType:
    def __init__(self, members):
        self.members = members
    
    def save(self, name):
        capture = ''
        for member in self.members:
            # Set default value (if one was specified).
            if len(member) >= 3:
                capture += 'if (' + name + '.' + member[1] + ' == undefined) {\n'
                capture += name + '.' + member[1] + ' = ' + member[2] + '\n'
                capture += '}\n'
            
            capture += member[0].save(name + '.' + member[1])
        return capture
    
    def load(self, name):
        replay = name + ' = {};\n'
        
        for member in self.members:
            replay += member[0].load(name + '.' + member[1])
        
        return replay
    
    def declare_argument(self, name):
        assert(False)
        return ''
    
    def as_argument(self, name):
        assert(False)
        return name
    
    def cleanup(self, name, isInArray = False):
        cleanup = ''
        for member in self.members:
            cleanup += member[0].cleanup(name + '.' + member[1])
        return cleanup

# Array type.
arrayDepth = 0
class ArrayType:
    def __init__(self, type):
        self.type = type
    
    def get_plural_name(self, name):
        if name[-1] == 'y':
            return name[0:-1] + 'ies'
        return name + 's'
    
    def save(self, name):
        global arrayDepth
        arrayDepth += 1
        plural = self.get_plural_name(name)
        
        capture = 'if (' + plural + ' == undefined) {\n'
        capture += plural + ' = [];\n'
        capture += '}\n'
        capture += '__WebGPUReconstruct_file.writeUint64(' + plural + '.length);\n'
        capture += 'for (let i' + str(arrayDepth) + ' = 0; i' + str(arrayDepth) + ' < ' + plural + '.length; i' + str(arrayDepth) + ' += 1) {\n'
        if isinstance(self.type, StructType):
            capture += self.type.save(plural + '[i' + str(arrayDepth) + ']', True)
        else:
            capture += self.type.save(plural + '[i' + str(arrayDepth) + ']')
        capture += '}\n'
        
        arrayDepth -= 1
        return capture
    
    def load(self, name):
        global arrayDepth
        arrayDepth += 1
        plural = self.get_plural_name(name)
        
        replay = name + 'Count = reader.ReadUint64();\n'
        replay += 'if (' + name + 'Count > 0) {\n'
        replay += plural + ' = new ' + self.type.nativeName + '[' + name + 'Count];\n'
        replay += '} else {\n'
        replay += plural + ' = nullptr;\n';
        replay += '}\n'
        replay += 'for (uint64_t i' + str(arrayDepth) + ' = 0; i' + str(arrayDepth) + ' < ' + name + 'Count; ++i' + str(arrayDepth) + ') {\n'
        if isinstance(self.type, StructType):
            replay += self.type.load('const_cast<' + self.type.nativeName + '*>(' + plural + ')[i' + str(arrayDepth) + ']', True)
        else:
            replay += self.type.load('const_cast<' + self.type.nativeName + '*>(' + plural + ')[i' + str(arrayDepth) + ']')
        replay += '}\n'
        arrayDepth -= 1
        return replay
    
    def declare_argument(self, name):
        declare = 'uint64_t ' + name + 'Count;\n'
        declare += self.type.nativeName + '* ' + self.get_plural_name(name) + ';\n'
        return declare
    
    def as_argument(self, name):
        return name + 'Count, ' + self.get_plural_name(name)
    
    def cleanup(self, name):
        cleanup = ''
        if isinstance(self.type, StructType):
            cleanup += 'for (uint64_t i = 0; i < ' + name + 'Count; ++i) {\n'
            self.type.cleanup(self.get_plural_name(name) + '[i]', True)
            cleanup += '}\n'
        cleanup += 'delete[] ' + self.get_plural_name(name) + ';\n'
        return cleanup

GPUCommandEncoderDescriptor = StructType("GPUCommandEncoderDescriptor", [
    [String, "label"],
])

GPUCommandBufferDescriptor = StructType("GPUCommandBufferDescriptor", [
    [String, "label"],
])

GPURenderBundleDescriptor = StructType("GPURenderBundleDescriptor", [
    [String, "label"],
])

GPUTextureViewDescriptor = StructType("GPUTextureViewDescriptor", [
    [String, "label"],
    [GPUTextureFormat, "format"],
    [GPUTextureViewDimension, "dimension"],
    [GPUTextureAspect, "aspect", '"all"'],
    [Uint32, "baseMipLevel", '0'],
    [Uint32DefaultMax, "mipLevelCount"],
    [Uint32, "baseArrayLayer", '0'],
    [Uint32DefaultMax, "arrayLayerCount"]
])

GPURenderPassColorAttachment = StructType("GPURenderPassColorAttachment", [
    [GPUTextureView, "view"],
    [Uint32DefaultMax, "depthSlice"],
    [GPUTextureView, "resolveTarget"],
    [GPUColor, "clearValue", '[0, 0, 0, 0]'],
    [GPULoadOp, "loadOp"],
    [GPUStoreOp, "storeOp"]
])

GPURenderPassDepthStencilAttachment = StructType("GPURenderPassDepthStencilAttachment", [
    [GPUTextureView, "view"],
    [Float32, "depthClearValue"],
    [GPULoadOp, "depthLoadOp"],
    [GPUStoreOp, "depthStoreOp"],
    [Bool, "depthReadOnly"],
    [Uint32, "stencilClearValue"],
    [GPULoadOp, "stencilLoadOp"],
    [GPUStoreOp, "stencilStoreOp"],
    [Bool, "stencilReadOnly"],
])

GPURenderPassTimestampWrites = StructType("GPURenderPassTimestampWrites", [
    [GPUQuerySet, "querySet"],
    [Uint32, "beginningOfPassWriteIndex"],
    [Uint32, "endOfPassWriteIndex"]
])

GPURenderPassDescriptor = StructType("GPURenderPassDescriptor", [
    [String, "label"],
    [ArrayType(GPURenderPassColorAttachment), "colorAttachment"],
    [GPURenderPassDepthStencilAttachment, "depthStencilAttachment"],
    [GPUQuerySet, "occlusionQuerySet"],
    [GPURenderPassTimestampWrites, "timestampWrites"],
    [Unsupported, "maxDrawCount"] # <- TODO In native spec, this is a chained struct.
])

GPUBlendComponent = SubStructType([
    [GPUBlendOperation, "operation"],
    [GPUBlendFactor, "srcFactor", '"one"'],
    [GPUBlendFactor, "dstFactor"]
])

GPUBlendState = StructType("GPUBlendState", [
    [GPUBlendComponent, "color"],
    [GPUBlendComponent, "alpha"]
])

GPUVertexAttribute = StructType("GPUVertexAttribute", [
    [GPUVertexFormat, "format"],
    [Uint64, "offset"],
    [Uint32, "shaderLocation"]
])

GPUVertexBufferLayout = StructType("GPUVertexBufferLayout", [
    [Uint64, "arrayStride"],
    [GPUVertexStepMode, "stepMode"],
    [ArrayType(GPUVertexAttribute), "attribute"]
])

GPUVertexState = SubStructType([
    [GPUShaderModule, "module"],
    [String, "entryPoint"],
    [GPUConstants, "constant"],
    [ArrayType(GPUVertexBufferLayout), "buffer"],
])

GPUPrimitiveState = SubStructType([
    [GPUPrimitiveTopology, "topology", '"triangle-list"'],
    [GPUIndexFormat, "stripIndexFormat"],
    [GPUFrontFace, "frontFace", '"ccw"'],
    [GPUCullMode, "cullMode", '"none"'],
    #[Unsupported, "unclippedDepth"] # <- TODO depth-clip-control
])

GPUStencilFaceState = SubStructType([
    [GPUCompareFunction, "compare", '"always"'],
    [GPUStencilOperation, "failOp", '"keep"'],
    [GPUStencilOperation, "depthFailOp", '"keep"'],
    [GPUStencilOperation, "passOp", '"keep"']
])

GPUDepthStencilState = StructType("GPUDepthStencilState", [
    [GPUTextureFormat, "format"],
    [DepthWriteEnabled, "depthWriteEnabled"],
    [GPUCompareFunction, "depthCompare"],
    [GPUStencilFaceState, "stencilFront", '{}'],
    [GPUStencilFaceState, "stencilBack", '{}'],
    [Uint32, "stencilReadMask", '0xFFFFFFFF'],
    [Uint32, "stencilWriteMask", '0xFFFFFFFF'],
    [Int32, "depthBias"],
    [Float32, "depthBiasSlopeScale", '0'],
    [Float32, "depthBiasClamp", '0']
])

GPUColorTargetState = StructType("GPUColorTargetState", [
    [GPUTextureFormat, "format"],
    [GPUBlendState, "blend"],
    [Uint32, "writeMask", '0xF']
])

GPUFragmentState = StructType("GPUFragmentState", [
    [GPUShaderModule, "module"],
    [String, "entryPoint"],
    [GPUConstants, "constant"],
    [ArrayType(GPUColorTargetState), "target"],
])

GPUMultisampleState = SubStructType([
    [Uint32, "count", '1'],
    [Uint32, "mask", '0xFFFFFFFF'],
    [Bool, "alphaToCoverageEnabled"],
])

GPURenderPipelineDescriptor = StructType("GPURenderPipelineDescriptor", [
    [String, "label"],
    [GPUPipelineLayout, "layout"],
    [GPUVertexState, "vertex"],
    [GPUPrimitiveState, "primitive", '{}'],
    [GPUDepthStencilState, "depthStencil"],
    [GPUMultisampleState, "multisample", '{}'],
    [GPUFragmentState, "fragment"]
])

GPUBufferDescriptor = StructType("GPUBufferDescriptor", [
    [String, "label"],
    [Uint64, "size"],
    [Uint32, "usage"],
    [Bool, "mappedAtCreation"]
])

GPUTextureDescriptor = StructType("GPUTextureDescriptor", [
    [String, "label"],
    [GPUExtent3D, "size"],
    [Uint32, "mipLevelCount", '1'],
    [Uint32, "sampleCount", '1'],
    [GPUTextureDimension, "dimension", '"2d"'],
    [GPUTextureFormat, "format"],
    [Uint32, "usage"],
    [ArrayType(GPUTextureFormat), "viewFormat", '[]']
])

GPUBindGroupDescriptor = StructType("GPUBindGroupDescriptor", [
    [String, "label"],
    [GPUBindGroupLayout, "layout"],
    [ArrayType(GPUBindGroupEntry), "entry"]
])

GPUSamplerDescriptor = StructType("GPUSamplerDescriptor", [
    [String, "label"],
    [GPUAddressMode, "addressModeU", '"clamp-to-edge"'],
    [GPUAddressMode, "addressModeV", '"clamp-to-edge"'],
    [GPUAddressMode, "addressModeW", '"clamp-to-edge"'],
    [GPUFilterMode, "magFilter", '"nearest"'],
    [GPUFilterMode, "minFilter", '"nearest"'],
    [GPUMipmapFilterMode, "mipmapFilter", '"nearest"'],
    [Float32, "lodMinClamp", '0'],
    [Float32, "lodMaxClamp", '32'],
    [GPUCompareFunction, "compare"],
    [Uint16, "maxAnisotropy", '1']
])

GPUImageCopyTexture = StructType("GPUImageCopyTexture", [
    [GPUTexture, "texture"],
    [Uint32, "mipLevel", '0'],
    [GPUOrigin3D, "origin", '{}'],
    [GPUTextureAspect, "aspect", '"all"']
])

GPUBufferBindingLayout = SubStructType([
    [GPUBufferBindingType, "type", '"uniform"'],
    [Bool, "hasDynamicOffset"],
    [Uint64, "minBindingSize"]
])

GPUSamplerBindingLayout = SubStructType([
    [GPUSamplerBindingType, "type", '"filtering"']
])

GPUTextureBindingLayout = SubStructType([
    [GPUTextureSampleType, "sampleType", '"float"'],
    [GPUTextureViewDimension, "viewDimension", '"2d"'],
    [Bool, "multisampled"]
])

GPUStorageTextureBindingLayout = SubStructType([
    [GPUStorageTextureAccess, "access", '"write-only"'],
    [GPUTextureFormat, "format"],
    [GPUTextureViewDimension, "viewDimension", '"2d"']
])

GPUBindGroupLayoutEntry = StructType("GPUBindGroupLayoutEntry", [
    [Uint32, "binding"],
    [Uint32, "visibility"],
    [GPUBufferBindingLayout, "buffer", '{type:""}'],
    [GPUSamplerBindingLayout, "sampler", '{type:""}'],
    [GPUTextureBindingLayout, "texture", '{sampleType:""}'],
    [GPUStorageTextureBindingLayout, "storageTexture", '{access:""}'],
    [Unsupported, "externalTexture"] # <- TODO Needs emulation.
])

GPUBindGroupLayoutDescriptor = StructType("GPUBindGroupLayoutDescriptor", [
    [String, "label"],
    [ArrayType(GPUBindGroupLayoutEntry), "entry"]
])

GPUPipelineLayoutDescriptor = StructType("GPUPipelineLayoutDescriptor", [
    [String, "label"],
    [ArrayType(GPUBindGroupLayout), "bindGroupLayout"]
])

GPUProgrammableStageDescriptor = SubStructType([
    [GPUShaderModule, "module"],
    [String, "entryPoint"],
    [GPUConstants, "constant"]
])

GPUComputePipelineDescriptor = StructType("GPUComputePipelineDescriptor", [
    [String, "label"],
    [GPUPipelineLayout, "layout"],
    [GPUProgrammableStageDescriptor, "compute"]
])

GPUComputePassTimestampWrites = StructType("GPUComputePassTimestampWrites", [
    [GPUQuerySet, "querySet"],
    [Uint32, "beginningOfPassWriteIndex"],
    [Uint32, "endOfPassWriteIndex"]
])

GPUComputePassDescriptor = StructType("GPUComputePassDescriptor", [
    [String, "label"],
    [GPUComputePassTimestampWrites, "timestampWrites"]
])

GPUQuerySetDescriptor = StructType("GPUQuerySetDescriptor", [
    [String, "label"],
    [GPUQueryType, "type"],
    [Uint32, "count"]
])

GPURenderBundleEncoderDescriptor = StructType("GPURenderBundleEncoderDescriptor", [
    [String, "label"],
    [ArrayType(GPUTextureFormat), "colorFormat"],
    [GPUTextureFormat, "depthStencilFormat"],
    [Uint32, "sampleCount", '1'],
    [Bool, "depthReadOnly"],
    [Bool, "stencilReadOnly"]
])

GPUTextureDataLayout = StructType("GPUTextureDataLayout", [
    [Uint64, "offset"],
    [Uint32DefaultMax, "bytesPerRow"],
    [Uint32DefaultMax, "rowsPerImage"]
])