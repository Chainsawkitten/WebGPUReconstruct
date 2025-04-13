# Unfortunately, can't just be done as an array of chars.
class StringType:
    def save(self, name):
        capture = 'if (' + name + ' == undefined) {\n'
        capture += '__WebGPUReconstruct_file.writeUint64(0);\n'
        capture += '} else {\n'
        capture += '__WebGPUReconstruct_file.writeString(String(' + name + '));\n'
        capture += '}\n'
        return capture
    
    def load(self, name):
        replay = name + ' = reader.ReadString();\n'
        return replay
    
    def declare_argument(self, name):
        declare = 'WGPUStringView ' + name + ';\n'
        return declare
    
    def as_argument(self, name):
        return name
    
    def cleanup(self, name):
        cleanup = 'if (' + name + '.length > 0) {\n'
        cleanup += 'delete[] ' + name + '.data;\n'
        cleanup += '}\n'
        return cleanup
String = StringType()