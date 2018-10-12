import re

ESCAPED_PARAMETER_PATTERN = '#(\\\\)+(([1-9]([0-9])*)|0)#'

def unescapeSymbols(contents, pattern):
    escapedSymbol = re.search(pattern, contents)
    while not escapedSymbol == None:
        backslashIndex = escapedSymbol.span()[0] + 1
        contents = contents[:backslashIndex] + contents[backslashIndex + 1:]
        escapedSymbol = self.escapedSymbol(contents[escapedSymbol.span()[1]:])

    return contents

def unescapeParameterSeparators(arguments):
    while '\\' in arguments:
        backslashArgumentIndex = arguments.index('\\', 1)
        if backslashArgumentIndex in [-1, len(arguments) - 1]:
            break
        arguments = arguments[:backslashArgumentIndex - 1] + [arguments[backslashArgumentIndex - 1] + '$' + arguments[backslashArgumentIndex + 1]] + arguments[backslashArgumentIndex + 2:]

    return arguments
