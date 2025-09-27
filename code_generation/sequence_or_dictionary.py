from code_generation.primitive_types import *
from code_generation.string_type import *
from code_generation.id_types import *

structSaveFunctionsString = ""
structLoadFunctionsString = ""
structFunctionDeclarationsString = ""

class SequenceOrDictionary():
    def __init__(self, webName, type, members):
        global structSaveFunctionsString
        global structLoadFunctionsString
        global structFunctionDeclarationsString
        
        self.webName = webName
        self.nativeName = "W" + webName
        self.members = members
        
        capture = 'function __WebGPUReconstruct_' + webName + '_Save(value) {\n'
        capture += 'if (value[Symbol.iterator] != undefined) {\n'
        capture += 'let array = Array.from(value);\n'
        i = 0
        for member in self.members:
            capture += 'if (array[' + str(i) + '] == undefined) {\n'
            capture += type.save(member[1])
            capture += '} else {\n'
            capture += type.save('array[' + str(i) + ']')
            capture += '}\n'
            i += 1
        capture += '} else {\n'
        for member in self.members:
            capture += 'if (value.' + member[0] + ' == undefined) {\n'
            capture += type.save(member[1])
            capture += '} else {\n'
            capture += type.save('value.' + member[0])
            capture += '}\n'
        capture += '}\n'
        capture += '}\n'
        
        structSaveFunctionsString += capture
        
        load = 'void Capture::Load' + self.webName + '(' + self.nativeName + '* value) {\n'
        load += '*value = {};\n'
        for member in self.members:
            load += type.load('value->' + member[0])
        load += '}\n'
        
        structLoadFunctionsString += load
        
        functionDeclarations = 'void Load' + self.webName + '(' + self.nativeName + '* value);\n'
        
        structFunctionDeclarationsString += functionDeclarations
        
    def save(self, name):
        return '__WebGPUReconstruct_' + self.webName + '_Save(' + name + ');\n'
    
    def load(self, name):
        return 'Load' + self.webName + '(&' + name + ');\n'
    
    def declare_argument(self, name):
        return self.nativeName + ' ' + name + ';\n'
    
    def as_argument(self, name):
        return '&' + name
    
    def cleanup(self, name):
        return ""
    
    def to_dictionary(self, name, output):
        code = 'let ' + output + ' = {};\n'
        code += 'if (' + name + '[Symbol.iterator] != undefined) {\n'
        code += 'let array = Array.from(' + name + ');\n'
        i = 0
        for member in self.members:
            code += 'if (array[' + str(i) + '] == undefined) {\n'
            code += output + '.' + member[0] + ' = ' + member[1] + ';\n'
            code += '} else {\n'
            code += output + '.' + member[0] + ' = array[' + str(i) + '];\n'
            code += '}\n'
            i += 1
        code += '} else {\n'
        for member in self.members:
            code += 'if (' + name + '.' + member[0] + ' == undefined) {\n'
            code += output + '.' + member[0] + ' = ' + member[1] + ';\n'
            code += '} else {\n'
            code += output + '.' + member[0] + ' = ' + name + '.' + member[0] + ';\n'
            code += '}\n'
        code += '}'
        return code

GPUColor = SequenceOrDictionary("GPUColor", Float64, [
    ["r", "0"],
    ["g", "0"],
    ["b", "0"],
    ["a", "0"]
])

GPUExtent3D = SequenceOrDictionary("GPUExtent3D", Uint32, [
    ["width", "1"],
    ["height", "1"],
    ["depthOrArrayLayers", "1"]
])

GPUOrigin3D = SequenceOrDictionary("GPUOrigin3D", Uint32, [
    ["x", "0"],
    ["y", "0"],
    ["z", "0"]
])
