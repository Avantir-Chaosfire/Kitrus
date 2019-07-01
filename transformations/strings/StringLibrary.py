import os, codecs, glob, random, re

from StringSet import *
from StringParsingException import *
from UnescapeFunctions import *

class StringLibrary:
    def __init__(self, configurationDirectory):
        self.TRANSFORMATION_NAME = 'strings'
        self.STRING_FILE_EXTENSION = '.str'
        self.LINE_START_METACHARACTER = '#'
        self.INCLUDE_STATEMENT_KEYWORD = 'include'
        self.JOIN_STATEMENT_KEYWORD = 'join'
        self.PREDEFINED_KEY_METACHARACTER_START = '<'
        self.PREDEFINED_KEY_METACHARACTER_END = '>'
        self.PARAMETER_METACHARACTER_START = '<'
        self.PARAMETER_METACHARACTER_END = '>'
        self.STRING_KEY_METACHARACTER_START = '<#'
        self.STRING_KEY_METACHARACTER_END = '#>'
        self.STRING_KEY_METACHARACTERS_LENGTH = len(self.STRING_KEY_METACHARACTER_START) + len(self.STRING_KEY_METACHARACTER_END)
        self.STRING_KEY_COMMON_METACHARACTER = ''.join([c for c in self.STRING_KEY_METACHARACTER_START if c in self.STRING_KEY_METACHARACTER_END])
        self.ILLEGAL_STRING_KEY_CHARACTERS = ['\\', '#', '$', '!', '=', '+', '-', '*', '/', '%', ' ', '\t', '\n']
        self.KITRUS_STRING_DIRECTORY_SEPARATOR = '/'
        self.MINECRAFT_FUNCTION_DIRECTORY_SEPARATOR = '/'

        self.EXPRESSION_OPERATORS = {
            '+': lambda x, y: x + y,
            '-': lambda x, y: x - y,
            '*': lambda x, y: x * y,
            '/': lambda x, y: x / y,
            '%': lambda x, y: x % y
        }
        
        self.complete = False
        self.warnings = []
        
        self.predefinitions = {}
        self.predefinitions['UUID'] = lambda path: str(random.randint(-2147483648, 2147483647))
        self.predefinitions['Newline'] = lambda path: '\n'
        self.predefinitions['~'] = lambda path: self.MINECRAFT_FUNCTION_DIRECTORY_SEPARATOR.join(path)

        self.stringSets = {}
        self.parsedStringSetNames = []
        self.stringFilesToParse = self.getAllStringFiles(configurationDirectory)

        while len(self.stringFilesToParse) > 0:
            self.parseStringFile(self.stringFilesToParse[0])

        self.complete = True

    def getAllStringFiles(self, configurationDirectory):
        stringFiles = [file for file in configurationDirectory.fileChildren if file.name.endswith(self.STRING_FILE_EXTENSION)]

        for stringFile in stringFiles:
            stringFile.name = stringFile.name[:-len(self.STRING_FILE_EXTENSION)]

        for virtualChildDirectory in configurationDirectory.directoryChildren:
            stringFiles += self.getAllStringFiles(virtualChildDirectory)

        if not configurationDirectory.name == self.TRANSFORMATION_NAME:
            for stringFile in stringFiles:
                stringFile.name = configurationDirectory.name + self.KITRUS_STRING_DIRECTORY_SEPARATOR + stringFile.name

        return stringFiles

    def parseStringFile(self, virtualFile):
        lines = virtualFile.getContentsLines()

        setName = virtualFile.name
        self.stringSets[setName] = StringSet(setName)

        lineNumber = 1
        for line in lines:
            if not line == '':
                args = self.getArgs(line)

                if args[0] == self.LINE_START_METACHARACTER + self.INCLUDE_STATEMENT_KEYWORD:
                    if len(args) != 2:
                        raise StringParsingException(setName, lineNumber, 'Expected 2 arguments to ' + self.LINE_START_METACHARACTER + self.INCLUDE_STATEMENT_KEYWORD + ', but found ' + str(len(args)))
                        
                    dependency = args[1]
                    self.stringSets[setName].dependencies.append(dependency)

                    if dependency not in self.parsedStringSetNames:
                        if dependency not in self.stringSets.keys():
                            for virtualFileToParse in self.stringFilesToParse:
                                if virtualFileToParse.name == dependency:
                                    self.parseStringFile(virtualFileToParse)
                                    break
                        else:
                            raise StringParsingException(setName, lineNumber, 'Cyclic dependency found; Cannot be resolved.')

                    if dependency not in self.stringSets.keys():
                        raise StringParsingException(setName, lineNumber, 'Unknown string set: ' + str(dependency))

                    for kind in self.stringSets[dependency].kinds:
                        if kind not in self.stringSets[setName].kinds:
                            self.stringSets[setName].kinds.append(kind)
                
                elif args[0] == self.LINE_START_METACHARACTER + self.JOIN_STATEMENT_KEYWORD:
                    if len(args) != 3:
                        raise StringParsingException(setName, lineNumber, 'Expected 3 arguments to ' + self.LINE_START_METACHARACTER + self.JOIN_STATEMENT_KEYWORD + ' but found ' + str(len(args)))
                    
                    kind = args[1]
                    join = self.replacePredefinedKeys([], args[2])
                    
                    self.stringSets[setName].joins[kind] = join

                    if kind not in self.stringSets[setName].kinds:
                        self.stringSets[setName].kinds.append(kind)
                        
                else:
                    key = args[0]
                    value = ' '.join(args[1:])

                    self.addToStringSet(setName, key, value, lineNumber)

                    if key[-1].isdigit():
                        while key[-1].isdigit():
                            key = key[:-1]
                        self.addToStringSet(setName, key, value, lineNumber)
            lineNumber += 1

        self.parsedStringSetNames.append(setName)
        self.stringFilesToParse.remove(virtualFile)

    def raiseException(self, e):
        raise e

    def raiseExportWarning(self, fileName, lineNumber, message):
        if lineNumber > -1:
            self.warnings.append('[' + fileName + ':' + str(lineNumber) + ']: ' + message)
        else:
            self.warnings.append('[' + fileName + ']: ' + message)

    def size(self):
        size = 0
        for stringSet in self.stringSets.values():
            size += len(stringSet.strings)
        return size

    def addToStringSet(self, setName, key, value, lineNumber):
        for illegalCharacter in self.ILLEGAL_STRING_KEY_CHARACTERS:
            if illegalCharacter in key:
                raise StringParsingException(setName, lineNumber, 'Illegal character "' + illegalCharacter + '" found in string key: ' + key)
        
        if key not in self.stringSets[setName].strings.keys():
            self.stringSets[setName].strings[key] = {}

        for kind in self.stringSets[setName].kinds:
            stringValue = self.replaceStringKeys([], value, kind, lambda l, m: self.raiseException(StringParsingException(setName, lineNumber, m)), setName)
                
            if kind in self.stringSets[setName].strings[key].keys():
                if kind in self.stringSets[setName].joins.keys():
                    self.stringSets[setName].strings[key][kind] += self.stringSets[setName].joins[kind] + stringValue
                else:
                    self.stringSets[setName].strings[key][kind] += stringValue
            else:
                self.stringSets[setName].strings[key][kind] = stringValue

    def stringKeys(self):
        keys = []

        for stringSet in self.stringSets.values():
            keys += stringSet.strings.keys()
        keys = list(set(keys))

        return keys

    def stringKeysOf(self, stringSetName):
        stringSet = self.stringSets[stringSetName]
        
        keys = []
        keys += stringSet.strings.keys()

        for dependency in stringSet.dependencies:
            keys += self.stringSets[dependency].strings.keys()
        keys = list(set(keys))

        return keys

    def getArgs(self, line):
        quoted = False
        args = []
        arg = ''

        for c in line:
            if c == '‘':
                quoted = not quoted
            elif quoted:
                arg += c
            elif not quoted:
                if c in [' ', '\t']:
                    if not arg == '':
                        args.append(arg)
                        arg = ''
                else:
                    arg += c

        if not arg == '':
            args.append(arg)

        return args

    def getLineNumber(self, string, targetIndex):
        lineNumber = 1

        index = 0
        while index < len(string) and index < targetIndex:
            if string[index] == '\n':
                lineNumber += 1
            index += 1

        return lineNumber

    def isValidParameter(self, parameter):
        if len(parameter) == 0:
            return False
        
        for digit in parameter:
            if not digit.isdigit():
                return False
            
        if len(parameter) > 1 and parameter[0] == '0':
            return False
        
        return True

    def replacePredefinedKeys(self, path, contents):
        endIndex = len(contents)
        
        for (key, value) in self.predefinitions.items():
            hashKey = self.PREDEFINED_KEY_METACHARACTER_START + key + self.PREDEFINED_KEY_METACHARACTER_END
            while hashKey in contents:
                contents = contents.replace(hashKey, value(path), 1)

        return unescapeSymbols(contents, self.PREDEFINED_KEY_METACHARACTER_START + '(\\\\)+(' + '|'.join(self.predefinitions.keys()) + ')' + self.PREDEFINED_KEY_METACHARACTER_END)

    def getValue(self, key, kind):
        value = ''

        foundInSet = ''
        
        for stringSet in self.stringSets.values():
            if key in stringSet.strings.keys():
                if foundInSet == '':
                    joinString = ''
                    if kind in stringSet.strings[key].keys():
                        value = stringSet.strings[key][kind]
                    else:
                        value = stringSet.strings[key]['']

                    foundInSet = stringSet.name
                else:
                    self.raiseExportWarning(stringSet.name, -1, 'Duplicate string key "' + key + '" also defined in ' + foundInSet)

        if self.complete and kind in ['loot_tables', 'advancements']:
            value = self.escape(value)
            
        return value

    def setValue(self, key, kind, value):
        foundInSet = ''
        
        for stringSet in self.stringSets.values():
            if key in stringSet.strings.keys():
                if foundInSet == '':
                    joinString = ''
                    if kind in stringSet.strings[key].keys():
                        stringSet.strings[key][kind] = value
                    else:
                        stringSet.strings[key][''] = value

                    foundInSet = stringSet.name
                else:
                    self.raiseExportWarning(stringSet.name, -1, 'Duplicate string key "' + key + '" also defined in ' + foundInSet)

    def escape(self, string):
        string = string.replace('\\', '\\\\')
        string = string.replace('"', '\\"')

        return string

    def replaceStringKeys(self, path, contents, kind, errorFunction, stringSetName = None):
        contents = self.replacePredefinedKeys(path, contents)

        if self.containsParameter(contents):
            return contents

        stringKeys = []
        if stringSetName == None:
            stringKeys = self.stringKeys()
        else:
            stringKeys = self.stringKeysOf(stringSetName)
        
        while True:
            keyEndIndex = -1
            keyStartIndex = -1

            currentStartSearchIndex = -1
            currentEndSearchIndex = 0
            while True:
                keyEndIndex = contents.find(self.STRING_KEY_METACHARACTER_END, currentEndSearchIndex)
                if keyEndIndex == -1:
                    break

                if currentStartSearchIndex == -1:
                    currentStartSearchIndex = keyEndIndex
                
                keyStartIndex = contents.rfind(self.STRING_KEY_METACHARACTER_START, 0, currentStartSearchIndex)
                if not keyStartIndex == -1 and not contents[keyStartIndex + 2] == '\\':
                    break

                currentStartSearchIndex = keyStartIndex
                currentEndSearchIndex = keyEndIndex + 2

            if keyEndIndex == -1:
                break
            
            keyEndIndex += 2
            key = contents[keyStartIndex + 2:keyEndIndex - 2]

            lineNumber = self.getLineNumber(contents, keyStartIndex)
            
            if key.startswith('!'):
                operators = key[1:].split(' ')

                variableStack = []

                for operator in operators:
                    if operator in self.EXPRESSION_OPERATORS:
                        if len(variableStack) < 2:
                            errorFunction(lineNumber, 'Not enough values to operate "' + operator + '" upon.')
                        else:
                            argument1String = variableStack.pop()
                            argument2String = variableStack.pop()

                            argument1 = self.parseStringOperator(path, stringKeys, argument1String, kind, errorFunction, lineNumber, stringSetName)
                            argument2 = self.parseStringOperator(path, stringKeys, argument2String, kind, errorFunction, lineNumber, stringSetName)

                            if None not in [argument1, argument2]:
                                variableStack.append(self.EXPRESSION_OPERATORS[operator](argument2, argument1))
                    elif operator == '=':
                        if len(variableStack) < 2:
                            errorFunction(lineNumber, 'Not enough values to operate "' + operator + '" upon.')
                        else:
                            stringValueString = variableStack.pop()
                            stringValue = self.parseStringOperator(path, stringKeys, stringValueString, kind, errorFunction, lineNumber, stringSetName)
                            stringKeyName = variableStack.pop()
                            if not stringValue == None:
                                self.setValue(stringKeyName, kind, '{0:g}'.format(stringValue))
                            variableStack.append(stringValue)
                    else:
                        variableStack.append(operator)
                if len(variableStack) == 1:
                    stringValue = self.parseStringOperator(path, stringKeys, variableStack[0], kind, errorFunction, lineNumber, stringSetName)
                    if not stringValue == None:
                        value = '{0:g}'.format(stringValue)
                        contents = contents[:keyStartIndex] + value + contents[keyEndIndex:]
                    else:
                        errorFunction(lineNumber, 'Unknown string key "' + variableStack[0] + '"')
                elif not variableStack:
                    errorFunction(lineNumber, 'No expression result.')
                else:
                    errorFunction(lineNumber, 'Too many expression results.')
                    
            else:
                contents = self.replaceStringKey(contents, keyStartIndex, keyEndIndex, path, stringKeys, key, kind, errorFunction, lineNumber, stringSetName)

        currentEndSearchIndex = 0
        while True:
            keyEndIndex = -1
            keyStartIndex = -1

            while True:
                keyEndIndex = contents.find(self.STRING_KEY_METACHARACTER_END, currentEndSearchIndex)
                if keyEndIndex == -1:
                    break
                
                keyStartIndex = contents.rfind(self.STRING_KEY_METACHARACTER_START, 0, keyEndIndex)
                if not keyStartIndex == -1 and contents[keyStartIndex + 2] == '\\':
                    break

                currentEndSearchIndex = keyEndIndex + 2

            if keyEndIndex == -1:
                break
            
            keyEndIndex += 2
            key = contents[keyStartIndex + 2:keyEndIndex - 2]

            lineNumber = self.getLineNumber(contents, keyStartIndex)

            contents = self.replaceStringKey(contents, keyStartIndex, keyEndIndex, path, stringKeys, key, kind, errorFunction, lineNumber, stringSetName)

        return contents

    def replaceStringKey(self, contents, keyStartIndex, keyEndIndex, path, stringKeys, key, kind, errorFunction, lineNumber, stringSetName):
        arguments = key.split(TEMPLATE_ARGUMENT_SEPARATION_METACHARACTER)

        if not key.startswith('\\'): #Key is not escaped
            if len(arguments) == 1:
                if key in stringKeys:
                    value = self.getValue(key, kind)
                    contents = contents[:keyStartIndex] + value + contents[keyEndIndex:]
                else:
                    errorFunction(lineNumber, 'Unknown string key "' + key + '"')
                    contents = contents[:keyStartIndex] + '[UNKNOWN STRING KEY]' + contents[keyEndIndex:]
            elif len(arguments) > 1:
                if arguments[0] in stringKeys:
                    value = self.replaceParameters(path, arguments, kind, lineNumber, errorFunction, stringSetName)
                    contents = contents[:keyStartIndex] + value + contents[keyEndIndex:]
                else:
                    errorFunction(lineNumber, 'Unknown string key "' + arguments[0] + '"')
                    contents = contents[:keyStartIndex] + '[UNKNOWN STRING KEY]' + contents[keyEndIndex:]
            else:
                raise Exception('Unknown error: No string keys found')
        else: #Key is escaped, remove escape
            key = key[1:]
            if len(key) == 0:
                contents = contents[:keyStartIndex] + self.STRING_KEY_COMMON_METACHARACTER + contents[keyEndIndex:]
            else:
                contents = contents[:keyStartIndex + 2] + key + contents[keyEndIndex - 2:]

        return contents

    def parseStringOperator(self, path, stringKeys, operator, kind, errorFunction, lineNumber, stringSetName):
        try:
            return float(operator)
        except ValueError:
            value = self.replaceStringKey('', 0, 0, path, stringKeys, operator, kind, errorFunction, lineNumber, stringSetName)
            try:
                return float(value)
            except ValueError:
                errorFunction(lineNumber, '"' + operator + '" does not evaluate to a number.')
                return None

    def replaceParameters(self, path, arguments, kind, lineNumber, errorFunction, stringSetName):
        arguments = unescapeParameterSeparators(arguments)
            
        value = self.getValue(arguments[0], kind)

        i = 1
        while i < len(arguments) and self.PARAMETER_METACHARACTER_START + str(i) + self.PARAMETER_METACHARACTER_END in value:
            value = value.replace(self.PARAMETER_METACHARACTER_START + str(i) + self.PARAMETER_METACHARACTER_END, arguments[i])
            i += 1

        if i < len(arguments):
            errorFunction(lineNumber, 'Missing parameter in string "' + arguments[0] + '": ' + self.PARAMETER_METACHARACTER_START + str(i) + self.PARAMETER_METACHARACTER_END)
            
        if self.containsParameter(value):
            errorFunction(lineNumber, 'Extra parameter present in string "' + arguments[0] + '"')

        value = unescapeSymbols(value, ESCAPED_PARAMETER_PATTERN)

        return self.replaceStringKeys(path, value, kind, errorFunction, stringSetName)

    def containsParameter(self, contents):
        return not re.search(self.PARAMETER_METACHARACTER_START + '(([1-9]([0-9])*)|0)' + self.PARAMETER_METACHARACTER_END, contents) == None

    def getWarnings(self):
        tempWarnings = self.warnings
        self.warnings = []
        return tempWarnings
