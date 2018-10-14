import os, codecs, glob, random, re

from StringSet import *
from StringParsingException import *
from UnescapeFunctions import *

class StringLibrary:
    def __init__(self):
        self.complete = False
        self.warnings = []
        
        self.predefinitions = {}
        self.predefinitions['UUID'] = lambda: str(random.randint(-2147483648, 2147483647))
        self.predefinitions['Newline'] = lambda: '\n'

        self.stringSets = {}
        self.parsedStringSetNames = []
        self.stringFilesToParse = []

        stringDirectoryName = os.path.join('strings', '')
        self.stringsDirectoryNameLength = len(stringDirectoryName)

        directories = [stringDirectoryName]
        expandingDirectories = directories
        while True:
            subdirectories = []
            for directory in expandingDirectories:
                subdirectories += [os.path.join(directory, o) for o in os.listdir(directory) if os.path.isdir(os.path.join(directory, o))]
            if not subdirectories:
                break
            expandingDirectories = subdirectories
            directories += subdirectories

        for directory in directories:
            self.stringFilesToParse += glob.glob(os.path.join(directory, '*.str'))

        while len(self.stringFilesToParse) > 0:
            self.parseStringFile(self.stringFilesToParse[0])

        self.complete = True

    def parseStringFile(self, fileName):
        lines = []
        with codecs.open(fileName, encoding = 'utf-8') as stringsFile:
            lines = stringsFile.readlines()

        setName = fileName[self.stringsDirectoryNameLength:-4].replace('\\', '/')

        self.stringSets[setName] = StringSet(setName)

        lineNumber = 1
        for line in lines:
            line = line.rstrip('\n')

            if not line == '':
                args = self.getArgs(line)

                if args[0] == '#include':
                    if len(args) != 2:
                        raise StringParsingException(setName, lineNumber, 'Expected 2 arguments to #include, but found ' + str(len(args)))
                        
                    dependency = args[1]
                    self.stringSets[setName].dependencies.append(dependency)

                    if dependency not in self.parsedStringSetNames:
                        if dependency not in self.stringSets.keys():
                            self.parseStringFile(os.path.join('strings', *(dependency.split('/'))) + '.str')
                        else:
                            raise StringParsingException(setName, lineNumber, 'Cyclic dependency found; Cannot be resolved.')

                    for kind in self.stringSets[dependency].kinds:
                        if kind not in self.stringSets[setName].kinds:
                            self.stringSets[setName].kinds.append(kind)
                
                elif args[0] == '#join':
                    if len(args) != 3:
                        raise StringParsingException(setName, lineNumber, 'Expected 3 arguments to #join, but found ' + str(len(args)))
                    
                    kind = args[1]
                    join = self.replacePredefinedKeys(args[2])
                    
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
        self.stringFilesToParse.remove(fileName)

    def raiseException(self, e):
        raise e

    def raiseExportWarning(self, fileName, lineNumber, message):
        self.warnings.append('[' + fileName + ':' + str(lineNumber) + ']: ' + message)

    def size(self):
        size = 0
        for stringSet in self.stringSets.values():
            size += len(stringSet.strings)
        return size

    def addToStringSet(self, setName, key, value, lineNumber):
        if key not in self.stringSets[setName].strings.keys():
            self.stringSets[setName].strings[key] = {}

        for kind in self.stringSets[setName].kinds:
            stringValue = self.replaceStringKeys(value, kind, lambda l, m: self.raiseException(StringParsingException(setName, lineNumber, m)))
                
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

    def stringKeysOf(self, stringSet):
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

    def replacePredefinedKeys(self, contents):
        endIndex = len(contents)
        
        for (key, value) in self.predefinitions.items():
            hashKey = '#' + key + '#'
            while hashKey in contents:
                contents = contents.replace(hashKey, value(), 1)

        return unescapeSymbols(contents, '#(\\\\)+(' + '|'.join(self.predefinitions.keys()) + ')#')

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

    def escape(self, string):
        string = string.replace('\\', '\\\\')
        string = string.replace('"', '\\"')

        return string

    def replaceStringKeys(self, contents, kind, errorFunction):
        contents = self.replacePredefinedKeys(contents)

        if self.containsParameter(contents):
            return contents
        
        endIndex = len(contents)

        while True:
            keyEndIndex = contents.rfind('##', 0, endIndex)
            if keyEndIndex == -1:
                break
            keyEndIndex += 2
            
            keyStartIndex = contents.rfind('##', 0, keyEndIndex - 2)
            if keyStartIndex == -1:
                break
            key = contents[keyStartIndex + 2:keyEndIndex - 2]

            arguments = key.split('$')

            lineNumber = self.getLineNumber(contents, keyStartIndex)

            if not key.startswith('\\'): #Key is not escaped
                if len(arguments) == 1:
                    if key in self.stringKeys():
                        value = self.getValue(key, kind)
                        contents = contents[:keyStartIndex] + value + contents[keyEndIndex:]
                    else:
                        errorFunction(lineNumber, 'Unknown string key "' + key + '"')
                elif len(arguments) > 1:
                    if arguments[0] in self.stringKeys():
                        value = self.replaceParameters(arguments, kind, lineNumber, errorFunction)
                        contents = contents[:keyStartIndex] + value + contents[keyEndIndex:]
                    else:
                        errorFunction(lineNumber, 'Unknown string key "' + arguments[0] + '"')
                else:
                    raise Exception('Unknown error: No string keys found')
            else: #Key is escaped, remove escape
                key = key[1:]
                if len(key) == 0:
                    contents = contents[:keyStartIndex] + '##' + contents[keyEndIndex:]
                else:
                    contents = contents[:keyStartIndex + 2] + key + contents[keyEndIndex - 2:]

            endIndex = keyStartIndex
            
        return contents

    def replaceParameters(self, arguments, kind, lineNumber, errorFunction):
        arguments = unescapeParameterSeparators(arguments)
            
        value = self.getValue(arguments[0], kind)

        i = 1
        while i < len(arguments) and '#' + str(i) + '#' in value:
            value = value.replace('#' + str(i) + '#', arguments[i])
            i += 1

        if i < len(arguments):
            errorFunction(lineNumber, 'Missing parameter in string "' + arguments[0] + '": #' + str(i) + '#')
            
        if self.containsParameter(value):
            errorFunction(lineNumber, 'Extra parameter present in string "' + arguments[0] + '"')

        value = unescapeSymbols(value, ESCAPED_PARAMETER_PATTERN)

        return self.replaceStringKeys(value, kind, errorFunction)

    def containsParameter(self, contents):
        return not re.search('#(([1-9]([0-9])*)|0)#', contents) == None

    def getWarnings(self):
        tempWarnings = self.warnings
        self.warnings = []
        return tempWarnings
