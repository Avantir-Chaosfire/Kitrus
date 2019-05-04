import re

ESCAPED_PARAMETER_PATTERN = '<(\\\\)+(([1-9]([0-9])*)|0)>'
PARAMETER_ESCAPE_METACHARACTER = '\\'
TEMPLATE_ARGUMENT_SEPARATION_METACHARACTER = '$'

def unescapeSymbols(contents, pattern):
    escapedSymbol = re.search(pattern, contents)
    startIndex = 0
    while not escapedSymbol == None:
        backslashIndex = escapedSymbol.span()[0] + 1 + startIndex
        contents = contents[:backslashIndex] + contents[backslashIndex + 1:]
        escapedSymbol = re.search(pattern, contents[backslashIndex:])

        startIndex = backslashIndex

    return contents

def unescapeParameterSeparators(arguments):
    while PARAMETER_ESCAPE_METACHARACTER in arguments:
        backslashArgumentIndex = arguments.index(PARAMETER_ESCAPE_METACHARACTER, 1)
        if backslashArgumentIndex in [-1, len(arguments) - 1]:
            break
        arguments = arguments[:backslashArgumentIndex - 1] + [arguments[backslashArgumentIndex - 1] + TEMPLATE_ARGUMENT_SEPARATION_METACHARACTER + arguments[backslashArgumentIndex + 1]] + arguments[backslashArgumentIndex + 2:]

    return arguments
