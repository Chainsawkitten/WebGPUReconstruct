# Basic line indentation based on {}.
def format(code, baseIndentation = 0):
    formatted = ''
    indentation = baseIndentation
    
    split = code.splitlines(True)
    for line in split:
        indentation -= line.count('}') - line.count('{}')
        for i in range(indentation):
            formatted += '    '
        formatted += line.strip() + '\n'
        indentation += line.count('{') - line.count('{}')
    
    return formatted