import re

from StringLibrary import *
from PredefinedStringLibrary import *
from StringExpressionCalculator import *
from StringSet import *
from UnescapeFunctions import *
from StringParsingException import *

class StringParser:
    def __init__(self, configurationDirectory):
        self.TRANSFORMATION_NAME = 'strings'
        self.STRING_FILE_EXTENSION = '.str'
        self.LINE_START_METACHARACTER = '#'
        self.INCLUDE_STATEMENT_KEYWORD = 'include'
        self.JOIN_STATEMENT_KEYWORD = 'join'
        self.KITRUS_STRING_DIRECTORY_SEPARATOR = '/'
        self.PREDEFINED_KEY_METACHARACTER_START = '<'
        self.PREDEFINED_KEY_METACHARACTER_END = '>'
        self.ILLEGAL_STRING_KEY_CHARACTERS = [
            '\\', '#', '$', '!', #Metacharacters
            '=', '+', '-', '*', '/', '%', '@', '&', '|', '^', '<', '>', '~', #Expression operators
            ' ', '\t', '\n', '\r' #Whitespace
        ]

        self.warnings = []

        self.predefinedStringLibrary = PredefinedStringLibrary()
        self.stringLibrary = StringLibrary(self)
        self.stringExpressionCalculator = StringExpressionCalculator(self.stringLibrary)
        
        self.parsedStringSetNames = []
        self.stringFilesToParse = self.getAllStringFiles(configurationDirectory)

        while len(self.stringFilesToParse) > 0:
            self.parseStringFile(self.stringFilesToParse[0])

        self.stringLibrary.complete = True

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
        self.stringLibrary.stringSets[setName] = StringSet(setName)

        lineNumber = 1
        for line in lines:
            if not line == '':
                args = self.getArgs(line)

                if args[0] == self.LINE_START_METACHARACTER + self.INCLUDE_STATEMENT_KEYWORD:
                    if len(args) != 2:
                        raise StringParsingException(setName, lineNumber, 'Expected 2 arguments to ' + self.LINE_START_METACHARACTER + self.INCLUDE_STATEMENT_KEYWORD + ', but found ' + str(len(args)))
                        
                    dependency = args[1]
                    self.stringLibrary.stringSets[setName].dependencies.append(dependency)

                    if dependency not in self.parsedStringSetNames:
                        if dependency not in self.stringLibrary.stringSets.keys():
                            for virtualFileToParse in self.stringFilesToParse:
                                if virtualFileToParse.name == dependency:
                                    self.parseStringFile(virtualFileToParse)
                                    break
                        else:
                            raise StringParsingException(setName, lineNumber, 'Cyclic dependency found; Cannot be resolved.')

                    if dependency not in self.stringLibrary.stringSets.keys():
                        raise StringParsingException(setName, lineNumber, 'Unknown string set: ' + str(dependency))

                    for kind in self.stringLibrary.stringSets[dependency].kinds:
                        if kind not in self.stringLibrary.stringSets[setName].kinds:
                            self.stringLibrary.stringSets[setName].kinds.append(kind)
                
                elif args[0] == self.LINE_START_METACHARACTER + self.JOIN_STATEMENT_KEYWORD:
                    if len(args) != 3:
                        raise StringParsingException(setName, lineNumber, 'Expected 3 arguments to ' + self.LINE_START_METACHARACTER + self.JOIN_STATEMENT_KEYWORD + ' but found ' + str(len(args)))
                    
                    kind = args[1]
                    join = self.replacePredefinedKeys([], args[2])
                    
                    self.stringLibrary.stringSets[setName].joins[kind] = join

                    if kind not in self.stringLibrary.stringSets[setName].kinds:
                        self.stringLibrary.stringSets[setName].kinds.append(kind)
                        
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

    def addToStringSet(self, setName, key, value, lineNumber):
        for illegalCharacter in self.ILLEGAL_STRING_KEY_CHARACTERS:
            if illegalCharacter in key:
                raise StringParsingException(setName, lineNumber, 'Illegal character "' + illegalCharacter + '" found in string key: ' + key)
        
        if key not in self.stringLibrary.stringSets[setName].strings.keys():
            self.stringLibrary.stringSets[setName].strings[key] = {}

        for kind in self.stringLibrary.stringSets[setName].kinds:
            stringValue = self.replaceStringKeys('', value, kind, lambda l, m: self.raiseException(StringParsingException(setName, lineNumber, m)), setName)
                
            if kind in self.stringLibrary.stringSets[setName].strings[key].keys():
                if kind in self.stringLibrary.stringSets[setName].joins.keys():
                    self.stringLibrary.stringSets[setName].strings[key][kind] += self.stringLibrary.stringSets[setName].joins[kind] + stringValue
                else:
                    self.stringLibrary.stringSets[setName].strings[key][kind] += stringValue
            else:
                self.stringLibrary.stringSets[setName].strings[key][kind] = stringValue

    def raiseException(self, e):
        raise e

    def raiseExportWarning(self, fileName, lineNumber, message):
        if lineNumber > -1:
            self.warnings.append('[' + fileName + ':' + str(lineNumber) + ']: ' + message)
        else:
            self.warnings.append('[' + fileName + ']: ' + message)

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

    def replacePredefinedKeys(self, path, contents):
        matches = re.findall(self.PREDEFINED_KEY_METACHARACTER_START + '[^' + self.stringLibrary.STRING_KEY_COMMON_METACHARACTER + self.PREDEFINED_KEY_METACHARACTER_START + self.PREDEFINED_KEY_METACHARACTER_END + ']+' + self.PREDEFINED_KEY_METACHARACTER_END, contents)
        distinctMatches = list(set(matches))
        for match in distinctMatches:
            key = match[len(self.PREDEFINED_KEY_METACHARACTER_START):-len(self.PREDEFINED_KEY_METACHARACTER_END)]
            value = self.predefinedStringLibrary.getValue(key, path)
            if not value == None:
                contents = contents.replace(match, value)

        return unescapeSymbols(contents, self.PREDEFINED_KEY_METACHARACTER_START + '(\\\\)+(' + '|'.join(self.predefinedStringLibrary.predefinitions.keys()) + ')' + self.PREDEFINED_KEY_METACHARACTER_END)

    def replaceStringKeys(self, path, contents, kind, errorFunction, stringSetName = None):
        contents = self.replacePredefinedKeys(path, contents)

        if self.stringLibrary.containsParameter(contents):
            return contents
        
        while True:
            keyEndIndex = -1
            keyStartIndex = -1

            currentStartSearchIndex = -1
            currentEndSearchIndex = 0
            while True:
                keyEndIndex = contents.find(self.stringLibrary.STRING_KEY_METACHARACTER_END, currentEndSearchIndex)
                if keyEndIndex == -1:
                    break

                if currentStartSearchIndex == -1:
                    currentStartSearchIndex = keyEndIndex
                
                keyStartIndex = contents.rfind(self.stringLibrary.STRING_KEY_METACHARACTER_START, 0, currentStartSearchIndex)
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
                value = self.stringExpressionCalculator.evaluate(key, kind, path, stringSetName, errorFunction, lineNumber)
                if not value == None:
                    contents = contents[:keyStartIndex] + value + contents[keyEndIndex:]
                else:
                    contents = contents[:keyStartIndex] + '[INVALID STRING EXPRESSION]' + contents[keyEndIndex:]
            else:
                contents = self.replaceStringKey(contents, keyStartIndex, keyEndIndex, path, stringSetName, key, kind, errorFunction, lineNumber)

        return contents

    def replaceStringKey(self, contents, keyStartIndex, keyEndIndex, path, stringSetName, key, kind, errorFunction, lineNumber):
        value = self.stringLibrary.evaluateStringKey(key, kind, path, stringSetName, errorFunction, lineNumber)
        return contents[:keyStartIndex] + value + contents[keyEndIndex:]

    def getWarnings(self):
        tempWarnings = self.warnings
        self.warnings = []
        return tempWarnings
