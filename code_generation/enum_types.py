enumSaveFunctionsString = ""
enumConversionsString = ""

# Enums (strings in JavaScript...)
class EnumType:
    def __init__(self, webName, members):
        global enumSaveFunctionsString
        global enumConversionsString
        
        self.webName = webName
        self.nativeName = "W" + webName
        self.members = members
        
        enumSaveFunctionsString += 'function __WebGPUReconstruct_' + self.webName + '_Save(value) {\n'
        enumSaveFunctionsString += 'switch (String(value)) {\n'
        for i in range(len(self.members)):
            enumSaveFunctionsString += 'case "' + self.members[i][0] + '":\n'
            enumSaveFunctionsString += '__WebGPUReconstruct_file.writeUint32(' + str(i) + ');\n'
            enumSaveFunctionsString += 'break;\n'
        enumSaveFunctionsString += 'default:\n'
        enumSaveFunctionsString += '__WebGPUReconstruct_file.writeUint32(' + str(len(self.members)) + ');\n'
        enumSaveFunctionsString += '}\n'
        enumSaveFunctionsString += '}\n'
        
        enumConversionsString += 'static ' + self.nativeName + ' Convert' + self.webName + '(uint32_t value) {\n'
        enumConversionsString += 'switch (value) {\n'
        for i in range(len(self.members)):
            enumConversionsString += 'case ' + str(i) + ':\n'
            enumConversionsString += 'return ' + self.members[i][1] + ';\n'
        enumConversionsString += 'default:\n'
        enumConversionsString += 'return static_cast<' + self.nativeName + '>(0);\n'
        enumConversionsString += '}\n'
        enumConversionsString += '}\n'
    
    def save(self, name):
        capture = '__WebGPUReconstruct_' + self.webName + '_Save(' + name + ');\n'
        return capture
    
    def load(self, name):
        replay = name + ' = Convert' + self.webName + '(reader.ReadUint32());\n'
        return replay
    
    def declare_argument(self, name):
        return self.nativeName + ' ' + name + ';\n';
    
    def as_argument(self, name):
        return name
    
    def cleanup(self, name):
        return ''

GPUTextureFormat = EnumType("GPUTextureFormat", [
    ["r8unorm", "WGPUTextureFormat_R8Unorm"],
    ["r8snorm", "WGPUTextureFormat_R8Snorm"],
    ["r8uint", "WGPUTextureFormat_R8Uint"],
    ["r8sint", "WGPUTextureFormat_R8Sint"],
    ["r16uint", "WGPUTextureFormat_R16Uint"],
    ["r16sint", "WGPUTextureFormat_R16Sint"],
    ["r16float", "WGPUTextureFormat_R16Float"],
    ["rg8unorm", "WGPUTextureFormat_RG8Unorm"],
    ["rg8snorm", "WGPUTextureFormat_RG8Snorm"],
    ["rg8uint", "WGPUTextureFormat_RG8Uint"],
    ["rg8sint", "WGPUTextureFormat_RG8Sint"],
    ["r32uint", "WGPUTextureFormat_R32Uint"],
    ["r32sint", "WGPUTextureFormat_R32Sint"],
    ["r32float", "WGPUTextureFormat_R32Float"],
    ["rg16uint", "WGPUTextureFormat_RG16Uint"],
    ["rg16sint", "WGPUTextureFormat_RG16Sint"],
    ["rg16float", "WGPUTextureFormat_RG16Float"],
    ["rgba8unorm", "WGPUTextureFormat_RGBA8Unorm"],
    ["rgba8unorm-srgb", "WGPUTextureFormat_RGBA8UnormSrgb"],
    ["rgba8snorm", "WGPUTextureFormat_RGBA8Snorm"],
    ["rgba8uint", "WGPUTextureFormat_RGBA8Uint"],
    ["rgba8sint", "WGPUTextureFormat_RGBA8Sint"],
    ["bgra8unorm", "WGPUTextureFormat_BGRA8Unorm"],
    ["bgra8unorm-srgb", "WGPUTextureFormat_BGRA8UnormSrgb"],
    ["rgb9e5ufloat", "WGPUTextureFormat_RGB9E5Ufloat"],
    ["rgb10a2uint", "WGPUTextureFormat_RGB10A2Uint"],
    ["rgb10a2unorm", "WGPUTextureFormat_RGB10A2Unorm"],
    ["rg11b10ufloat", "WGPUTextureFormat_RG11B10Ufloat"],
    ["rg32uint", "WGPUTextureFormat_RG32Uint"],
    ["rg32sint", "WGPUTextureFormat_RG32Sint"],
    ["rg32float", "WGPUTextureFormat_RG32Float"],
    ["rgba16uint", "WGPUTextureFormat_RGBA16Uint"],
    ["rgba16sint", "WGPUTextureFormat_RGBA16Sint"],
    ["rgba16float", "WGPUTextureFormat_RGBA16Float"],
    ["rgba32uint", "WGPUTextureFormat_RGBA32Uint"],
    ["rgba32sint", "WGPUTextureFormat_RGBA32Sint"],
    ["rgba32float", "WGPUTextureFormat_RGBA32Float"],
    ["stencil8", "WGPUTextureFormat_Stencil8"],
    ["depth16unorm", "WGPUTextureFormat_Depth16Unorm"],
    ["depth24plus", "WGPUTextureFormat_Depth24Plus"],
    ["depth24plus-stencil8", "WGPUTextureFormat_Depth24PlusStencil8"],
    ["depth32float", "WGPUTextureFormat_Depth32Float"],
    ["depth32float-stencil8", "WGPUTextureFormat_Depth32FloatStencil8"],
    ["bc1-rgba-unorm", "WGPUTextureFormat_BC1RGBAUnorm"],
    ["bc1-rgba-unorm-srgb", "WGPUTextureFormat_BC1RGBAUnormSrgb"],
    ["bc2-rgba-unorm", "WGPUTextureFormat_BC2RGBAUnorm"],
    ["bc2-rgba-unorm-srgb", "WGPUTextureFormat_BC2RGBAUnormSrgb"],
    ["bc3-rgba-unorm", "WGPUTextureFormat_BC3RGBAUnorm"],
    ["bc3-rgba-unorm-srgb", "WGPUTextureFormat_BC3RGBAUnormSrgb"],
    ["bc4-r-unorm", "WGPUTextureFormat_BC4RUnorm"],
    ["bc4-r-snorm", "WGPUTextureFormat_BC4RSnorm"],
    ["bc5-rg-unorm", "WGPUTextureFormat_BC5RGUnorm"],
    ["bc5-rg-snorm", "WGPUTextureFormat_BC5RGSnorm"],
    ["bc6h-rgb-ufloat", "WGPUTextureFormat_BC6HRGBUfloat"],
    ["bc6h-rgb-float", "WGPUTextureFormat_BC6HRGBFloat"],
    ["bc7-rgba-unorm", "WGPUTextureFormat_BC7RGBAUnorm"],
    ["bc7-rgba-unorm-srgb", "WGPUTextureFormat_BC7RGBAUnormSrgb"],
    ["etc2-rgb8unorm", "WGPUTextureFormat_ETC2RGB8Unorm"],
    ["etc2-rgb8unorm-srgb", "WGPUTextureFormat_ETC2RGB8UnormSrgb"],
    ["etc2-rgb8a1unorm", "WGPUTextureFormat_ETC2RGB8A1Unorm"],
    ["etc2-rgb8a1unorm-srgb", "WGPUTextureFormat_ETC2RGB8A1UnormSrgb"],
    ["etc2-rgba8unorm", "WGPUTextureFormat_ETC2RGBA8Unorm"],
    ["etc2-rgba8unorm-srgb", "WGPUTextureFormat_ETC2RGBA8UnormSrgb"],
    ["eac-r11unorm", "WGPUTextureFormat_EACR11Unorm"],
    ["eac-r11snorm", "WGPUTextureFormat_EACR11Snorm"],
    ["eac-rg11unorm", "WGPUTextureFormat_EACRG11Unorm"],
    ["eac-rg11snorm", "WGPUTextureFormat_EACRG11Snorm"],
    ["astc-4x4-unorm", "WGPUTextureFormat_ASTC4x4Unorm"],
    ["astc-4x4-unorm-srgb", "WGPUTextureFormat_ASTC4x4UnormSrgb"],
    ["astc-5x4-unorm", "WGPUTextureFormat_ASTC5x4Unorm"],
    ["astc-5x4-unorm-srgb", "WGPUTextureFormat_ASTC5x4UnormSrgb"],
    ["astc-5x5-unorm", "WGPUTextureFormat_ASTC5x5Unorm"],
    ["astc-5x5-unorm-srgb", "WGPUTextureFormat_ASTC5x5UnormSrgb"],
    ["astc-6x5-unorm", "WGPUTextureFormat_ASTC6x5Unorm"],
    ["astc-6x5-unorm-srgb", "WGPUTextureFormat_ASTC6x5UnormSrgb"],
    ["astc-6x6-unorm", "WGPUTextureFormat_ASTC6x6Unorm"],
    ["astc-6x6-unorm-srgb", "WGPUTextureFormat_ASTC6x6UnormSrgb"],
    ["astc-8x5-unorm", "WGPUTextureFormat_ASTC8x5Unorm"],
    ["astc-8x5-unorm-srgb", "WGPUTextureFormat_ASTC8x5UnormSrgb"],
    ["astc-8x6-unorm", "WGPUTextureFormat_ASTC8x6Unorm"],
    ["astc-8x6-unorm-srgb", "WGPUTextureFormat_ASTC8x6UnormSrgb"],
    ["astc-8x8-unorm", "WGPUTextureFormat_ASTC8x8Unorm"],
    ["astc-8x8-unorm-srgb", "WGPUTextureFormat_ASTC8x8UnormSrgb"],
    ["astc-10x5-unorm", "WGPUTextureFormat_ASTC10x5Unorm"],
    ["astc-10x5-unorm-srgb", "WGPUTextureFormat_ASTC10x5UnormSrgb"],
    ["astc-10x6-unorm", "WGPUTextureFormat_ASTC10x6Unorm"],
    ["astc-10x6-unorm-srgb", "WGPUTextureFormat_ASTC10x6UnormSrgb"],
    ["astc-10x8-unorm", "WGPUTextureFormat_ASTC10x8Unorm"],
    ["astc-10x8-unorm-srgb", "WGPUTextureFormat_ASTC10x8UnormSrgb"],
    ["astc-10x10-unorm", "WGPUTextureFormat_ASTC10x10Unorm"],
    ["astc-10x10-unorm-srgb", "WGPUTextureFormat_ASTC10x10UnormSrgb"],
    ["astc-12x10-unorm", "WGPUTextureFormat_ASTC12x10Unorm"],
    ["astc-12x10-unorm-srgb", "WGPUTextureFormat_ASTC12x10UnormSrgb"],
    ["astc-12x12-unorm", "WGPUTextureFormat_ASTC12x12Unorm"],
    ["astc-12x12-unorm-srgb", "WGPUTextureFormat_ASTC12x12UnormSrgb"]
])

GPUTextureViewDimension = EnumType("GPUTextureViewDimension", [
    ["1d", "WGPUTextureViewDimension_1D"],
    ["2d", "WGPUTextureViewDimension_2D"],
    ["2d-array", "WGPUTextureViewDimension_2DArray"],
    ["cube", "WGPUTextureViewDimension_Cube"],
    ["cube-array", "WGPUTextureViewDimension_CubeArray"],
    ["3d", "WGPUTextureViewDimension_3D"]
])

GPUTextureAspect = EnumType("GPUTextureAspect", [
    ["all", "WGPUTextureAspect_All"],
    ["stencil-only", "WGPUTextureAspect_StencilOnly"],
    ["depth-only", "WGPUTextureAspect_DepthOnly"]
])

GPULoadOp = EnumType("GPULoadOp", [
    ["load", "WGPULoadOp_Load"],
    ["clear", "WGPULoadOp_Clear"]
])

GPUStoreOp = EnumType("GPUStoreOp", [
    ["store", "WGPUStoreOp_Store"],
    ["discard", "WGPUStoreOp_Discard"]
])

GPUBlendOperation = EnumType("GPUBlendOperation", [
    ["add", "WGPUBlendOperation_Add"],
    ["subtract", "WGPUBlendOperation_Subtract"],
    ["reverse-subtract", "WGPUBlendOperation_ReverseSubtract"],
    ["min", "WGPUBlendOperation_Min"],
    ["max", "WGPUBlendOperation_Max"]
])

GPUBlendFactor = EnumType("GPUBlendFactor", [
    ["zero", "WGPUBlendFactor_Zero"],
    ["one", "WGPUBlendFactor_One"],
    ["src", "WGPUBlendFactor_Src"],
    ["one-minus-src", "WGPUBlendFactor_OneMinusSrc"],
    ["src-alpha", "WGPUBlendFactor_SrcAlpha"],
    ["one-minus-src-alpha", "WGPUBlendFactor_OneMinusSrcAlpha"],
    ["dst", "WGPUBlendFactor_Dst"],
    ["one-minus-dst", "WGPUBlendFactor_OneMinusDst"],
    ["dst-alpha", "WGPUBlendFactor_DstAlpha"],
    ["one-minus-dst-alpha", "WGPUBlendFactor_OneMinusDstAlpha"],
    ["src-alpha-saturated", "WGPUBlendFactor_SrcAlphaSaturated"],
    ["constant", "WGPUBlendFactor_Constant"],
    ["one-minus-constant", "WGPUBlendFactor_OneMinusConstant"]
    # TODO Dual-source blending extension.
    #["src1", ],
    #["one-minus-src1", ],
    #["src1-alpha", ],
    #["one-minus-src1-alpha", ]
])

GPUVertexStepMode = EnumType("GPUVertexStepMode", [
    ["vertex", "WGPUVertexStepMode_Vertex"],
    ["instance", "WGPUVertexStepMode_Instance"]
])

GPUVertexFormat = EnumType("GPUVertexFormat", [
    ["uint8x2", "WGPUVertexFormat_Uint8x2"],
    ["uint8x4", "WGPUVertexFormat_Uint8x4"],
    ["sint8x2", "WGPUVertexFormat_Sint8x2"],
    ["sint8x4", "WGPUVertexFormat_Sint8x4"],
    ["unorm8x2", "WGPUVertexFormat_Unorm8x2"],
    ["unorm8x4", "WGPUVertexFormat_Unorm8x4"],
    ["snorm8x2", "WGPUVertexFormat_Snorm8x2"],
    ["snorm8x4", "WGPUVertexFormat_Snorm8x4"],
    ["uint16x2", "WGPUVertexFormat_Uint16x2"],
    ["uint16x4", "WGPUVertexFormat_Uint16x4"],
    ["sint16x2", "WGPUVertexFormat_Sint16x2"],
    ["sint16x4", "WGPUVertexFormat_Sint16x4"],
    ["unorm16x2", "WGPUVertexFormat_Unorm16x2"],
    ["unorm16x4", "WGPUVertexFormat_Unorm16x4"],
    ["snorm16x2", "WGPUVertexFormat_Snorm16x2"],
    ["snorm16x4", "WGPUVertexFormat_Snorm16x4"],
    ["float16x2", "WGPUVertexFormat_Float16x2"],
    ["float16x4", "WGPUVertexFormat_Float16x4"],
    ["float32", "WGPUVertexFormat_Float32"],
    ["float32x2", "WGPUVertexFormat_Float32x2"],
    ["float32x3", "WGPUVertexFormat_Float32x3"],
    ["float32x4", "WGPUVertexFormat_Float32x4"],
    ["uint32", "WGPUVertexFormat_Uint32"],
    ["uint32x2", "WGPUVertexFormat_Uint32x2"],
    ["uint32x3", "WGPUVertexFormat_Uint32x3"],
    ["uint32x4", "WGPUVertexFormat_Uint32x4"],
    ["sint32", "WGPUVertexFormat_Sint32"],
    ["sint32x2", "WGPUVertexFormat_Sint32x2"],
    ["sint32x3", "WGPUVertexFormat_Sint32x3"],
    ["sint32x4", "WGPUVertexFormat_Sint32x4"]
    #["unorm10-10-10-2", ] <- TODO Not in the native headers?!
])

GPUPrimitiveTopology = EnumType("GPUPrimitiveTopology", [
    ["point-list", "WGPUPrimitiveTopology_PointList"],
    ["line-list", "WGPUPrimitiveTopology_LineList"],
    ["line-strip", "WGPUPrimitiveTopology_LineStrip"],
    ["triangle-list", "WGPUPrimitiveTopology_TriangleList"],
    ["triangle-strip", "WGPUPrimitiveTopology_TriangleStrip"]
])

GPUIndexFormat = EnumType("GPUIndexFormat", [
    ["uint16", "WGPUIndexFormat_Uint16"],
    ["uint32", "WGPUIndexFormat_Uint32"]
])

GPUFrontFace = EnumType("GPUFrontFace", [
    ["ccw", "WGPUFrontFace_CCW"],
    ["cw", "WGPUFrontFace_CW"]
])

GPUCullMode = EnumType("GPUCullMode", [
    ["none", "WGPUCullMode_None"],
    ["front", "WGPUCullMode_Front"],
    ["back", "WGPUCullMode_Back"]
])

GPUCompareFunction = EnumType("GPUCompareFunction", [
    ["never", "WGPUCompareFunction_Never"],
    ["less", "WGPUCompareFunction_Less"],
    ["equal", "WGPUCompareFunction_Equal"],
    ["less-equal", "WGPUCompareFunction_LessEqual"],
    ["greater", "WGPUCompareFunction_Greater"],
    ["not-equal", "WGPUCompareFunction_NotEqual"],
    ["greater-equal", "WGPUCompareFunction_GreaterEqual"],
    ["always", "WGPUCompareFunction_Always"]
])

GPUStencilOperation = EnumType("GPUStencilOperation", [
    ["keep", "WGPUStencilOperation_Keep"],
    ["zero", "WGPUStencilOperation_Zero"],
    ["replace", "WGPUStencilOperation_Replace"],
    ["invert", "WGPUStencilOperation_Invert"],
    ["increment-clamp", "WGPUStencilOperation_IncrementClamp"],
    ["decrement-clamp", "WGPUStencilOperation_DecrementClamp"],
    ["increment-wrap", "WGPUStencilOperation_IncrementWrap"],
    ["decrement-wrap", "WGPUStencilOperation_DecrementWrap"]
])

GPUTextureDimension = EnumType("GPUTextureDimension", [
    ["1d", "WGPUTextureDimension_1D"],
    ["2d", "WGPUTextureDimension_2D"],
    ["3d", "WGPUTextureDimension_3D"]
])

GPUAddressMode = EnumType("GPUAddressMode", [
    ["clamp-to-edge", "WGPUAddressMode_ClampToEdge"],
    ["repeat", "WGPUAddressMode_Repeat"],
    ["mirror-repeat", "WGPUAddressMode_MirrorRepeat"]
])

GPUFilterMode = EnumType("GPUFilterMode", [
    ["nearest", "WGPUFilterMode_Nearest"],
    ["linear", "WGPUFilterMode_Linear"]
])

GPUMipmapFilterMode = EnumType("GPUMipmapFilterMode", [
    ["nearest", "WGPUMipmapFilterMode_Nearest"],
    ["linear", "WGPUMipmapFilterMode_Linear"]
])

GPUBufferBindingType = EnumType("GPUBufferBindingType", [
    ["uniform", "WGPUBufferBindingType_Uniform"],
    ["storage", "WGPUBufferBindingType_Storage"],
    ["read-only-storage", "WGPUBufferBindingType_ReadOnlyStorage"]
])

GPUSamplerBindingType = EnumType("GPUSamplerBindingType", [
    ["filtering", "WGPUSamplerBindingType_Filtering"],
    ["non-filtering", "WGPUSamplerBindingType_NonFiltering"],
    ["comparison", "WGPUSamplerBindingType_Comparison"]
])

GPUTextureSampleType = EnumType("GPUTextureSampleType", [
    ["float", "WGPUTextureSampleType_Float"],
    ["unfilterable-float", "WGPUTextureSampleType_UnfilterableFloat"],
    ["depth", "WGPUTextureSampleType_Depth"],
    ["sint", "WGPUTextureSampleType_Sint"],
    ["uint", "WGPUTextureSampleType_Uint"]
])

GPUStorageTextureAccess = EnumType("GPUStorageTextureAccess", [
    ["write-only", "WGPUStorageTextureAccess_WriteOnly"],
    ["read-only", "WGPUStorageTextureAccess_ReadOnly"],
    ["read-write", "WGPUStorageTextureAccess_ReadWrite"]
])

GPUQueryType = EnumType("GPUQueryType", [
    ["occlusion", "WGPUQueryType_Occlusion"],
    ["timestamp", "WGPUQueryType_Timestamp"]
])