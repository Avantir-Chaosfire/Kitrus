import re

from UnescapeFunctions import *

class StringLibrary:
    def __init__(self, stringParser):
        self.PARAMETER_METACHARACTER_START = '<'
        self.PARAMETER_METACHARACTER_END = '>'
        self.STRING_KEY_METACHARACTER_START = '<#'
        self.STRING_KEY_METACHARACTER_END = '#>'
        self.STRING_KEY_COMMON_METACHARACTER = ''.join([c for c in self.STRING_KEY_METACHARACTER_START if c in self.STRING_KEY_METACHARACTER_END])
        self.TEMPLATE_ARGUMENT_SEPARATION_METACHARACTER = '$'

        self.stringParser = stringParser
        self.stringSets = {}
        self.complete = False

    def size(self):
        size = 0
        for stringSet in self.stringSets.values():
            size += len(stringSet.strings)
        return size

    def evaluateStringKey(self, key, kind, path, stringSetName, errorFunction, lineNumber):
        arguments = key.split(self.TEMPLATE_ARGUMENT_SEPARATION_METACHARACTER)

        result = None

        if not key.startswith('\\'): #Key is not escaped
            if len(arguments) == 1:
                result = self.getValue(key, kind, stringSetName)
                if result == None:
                    result = '[UNKNOWN STRING KEY]'
                    errorFunction(lineNumber, 'Unknown string key "' + key + '"')
            elif len(arguments) > 1:
                result = self.replaceParameters(path, arguments, kind, lineNumber, errorFunction, stringSetName)
                if result == None:
                    result = '[UNKNOWN STRING KEY]'
                    errorFunction(lineNumber, 'Unknown string key "' + arguments[0] + '"')
            else:
                raise Exception('Unknown error: No string keys found')
        else: #Key is escaped, remove escape
            key = key[1:]
            if len(key) == 0:
                result = self.STRING_KEY_COMMON_METACHARACTER
            else:
                result = self.STRING_KEY_METACHARACTER_START + key + self.STRING_KEY_METACHARACTER_END

        return result

    def replaceParameters(self, path, arguments, kind, lineNumber, errorFunction, stringSetName):
        arguments = unescapeParameterSeparators(arguments)
            
        value = self.getValue(arguments[0], kind, stringSetName)
        if value == None:
            return None

        i = 1
        while i < len(arguments) and self.PARAMETER_METACHARACTER_START + str(i) + self.PARAMETER_METACHARACTER_END in value:
            value = value.replace(self.PARAMETER_METACHARACTER_START + str(i) + self.PARAMETER_METACHARACTER_END, arguments[i])
            i += 1

        if i < len(arguments):
            errorFunction(lineNumber, 'Missing parameter in string "' + arguments[0] + '": ' + self.PARAMETER_METACHARACTER_START + str(i) + self.PARAMETER_METACHARACTER_END)
            
        if self.containsParameter(value):
            errorFunction(lineNumber, 'Extra parameter present in string "' + arguments[0] + '"')

        value = unescapeSymbols(value, ESCAPED_PARAMETER_PATTERN)

        return self.stringParser.replaceStringKeys(path, value, kind, errorFunction, stringSetName)

    def containsParameter(self, contents):
        return not re.search(self.PARAMETER_METACHARACTER_START + '(([1-9]([0-9])*)|0)' + self.PARAMETER_METACHARACTER_END, contents) == None

    def stringSetsToSearchFrom(self, stringSetName):
        stringSet = self.stringSets[stringSetName]
        
        stringSets = [self.stringSets[dependency] for dependency in stringSet.dependencies]
        stringSets.append(stringSet)

        return stringSets

    def getValue(self, key, kind, stringSetName = None):
        value = None

        foundInSet = ''

        stringSetsToSearch = []
        if stringSetName == None:
            stringSetsToSearch = self.stringSets.values()
        else:
            stringSetsToSearch = self.stringSetsToSearchFrom(stringSetName)
        
        for stringSet in stringSetsToSearch:
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

        if self.complete and kind in ['loot_tables', 'advancements'] and not value == None:
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
