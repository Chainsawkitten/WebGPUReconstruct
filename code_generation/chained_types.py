from code_generation.custom_types import *
from code_generation.enum_types import *

# Type which is a dictionary entry in JavaScript but a chained struct in C.
class ChainedType:
    def __init__(self, structName, saveCode, loadCode, declareArgumentCode = 'assert(false);\n', asArgumentCode = '$name', cleanupCode = ''):
        self.structName = structName
        self.saveCode = saveCode
        self.loadCode = loadCode
        self.declareArgumentCode = declareArgumentCode
        self.asArgumentCode = asArgumentCode
        self.cleanupCode = cleanupCode
    
    def get_parent_name(self, name):
        pos = max(map(name.rfind, ['.', '>']))
        assert pos > -1
        return name[:pos + 1]
    
    def save(self, name):
        capture = 'if (' + name + ' == undefined) {\n'
        capture += '__WebGPUReconstruct_file.writeUint8(0);\n'
        capture += '} else {\n'
        capture += '__WebGPUReconstruct_file.writeUint8(1);\n'
        capture += self.saveCode.replace('$name', name)
        capture += '}\n'
        return capture
    
    def load(self, name):
        baseName = self.get_parent_name(name)
        
        replay = 'if (reader.ReadUint8()) {\n'
        replay += 'WGPU' + self.structName + '* ' + self.structName + ' = static_cast<WGPU' + self.structName + '*>(malloc(sizeof(WGPU' + self.structName + ')));\n'
        replay += '*' + self.structName + ' = {};\n'
        replay += self.structName + '->chain.sType = WGPUSType_' + self.structName + ';\n'
        replay += self.loadCode.replace('$name', self.structName)
        replay += self.structName + '->chain.next = ' + baseName + 'nextInChain;\n'
        replay += baseName + 'nextInChain = reinterpret_cast<WGPUChainedStruct*>(' + self.structName + ');\n'
        replay += '}\n'
        return replay
    
    def declare_argument(self, name):
        assert(False)
        return ''
    
    def as_argument(self, name):
        assert(False)
        return ''
    
    def cleanup(self, name):
        baseName = self.get_parent_name(name)
        
        cleanup = self.cleanupCode.replace('$name', name)
        cleanup += 'FreeChainedStruct(' + baseName + 'nextInChain);\n'
        cleanup += baseName + 'nextInChain = nullptr;\n'
        return cleanup

GPURenderPassMaxDrawCount = ChainedType("RenderPassMaxDrawCount", """
__WebGPUReconstruct_file.writeUint64($name);
""",
"""
$name->maxDrawCount = reader.ReadUint64();
""")

GPUExternalTextureBindingLayout = ChainedType("ExternalTextureBindingLayout", """
""",
"""
#if WEBGPU_BACKEND_WGPU
ErrorOutput("External texture in bind group layout not supported in wgpu backend.\\n");
#endif
"""
)

GPUTextureBindingViewDimension = ChainedType("TextureBindingViewDimensionDescriptor", GPUTextureViewDimension.save("$name"),
"""
#if WEBGPU_BACKEND_WGPU
ErrorOutput("GPUTextureDescriptor.textureBindingViewDimension not supported in wgpu backend.\\n");
#else
""" + GPUTextureViewDimension.load("$name->textureBindingViewDimension") + """
#endif
"""
)
