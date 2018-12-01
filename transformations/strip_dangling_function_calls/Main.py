import copy, os, codecs

from KitrusRoot_Transformation import *

from ConfigurationParsingException import *

#TODO: This could be made better by documenting all functions from all modules that use this
#transformation and then using that to strip dangling function calls as long as the namespace is
#associated with a module, instead of just the current module. That may not be something people want
#to do, so probably add a parameter for that in the configuration.
class Main(Transformation):
    def __init__(self, configurationDirectory, parametermodules):
        super(Main, self).__init__()
        
        self.MINECRAFT_FUNCTION_COMMAND = 'function'
        self.MINECRAFT_NAMESPACE_PATH_SEPARATOR = ':'
        self.MINECRAFT_FUNCTION_PATH_SEPARATOR = '/'
        self.MINECRAFT_FUNCTION_FILE_EXTENSION = '.mcfunction'
        self.NAMESPACE_CONFIGURATION_FILE_NAME = 'namespaces.cfg'

        lines = []
        for virtualFile in configurationDirectory.fileChildren:
            if virtualFile.name == self.NAMESPACE_CONFIGURATION_FILE_NAME:
                lines = virtualFile.contents.split('\n')

        self.moduleNamespaces = {}
        lineNumber = 1
        for line in lines:
            if not line == '':
                if '=' not in line:
                    raise ConfigurationParsingException('[' + self.NAMESPACE_CONFIGURATION_FILE_NAME + ':' + str(lineNumber) + '] Expected to find "=".')
                indexOfEquals = line.index('=')
                self.moduleNamespaces[line[:indexOfEquals]] = line[indexOfEquals + 1:]
            lineNumber += 1

    def apply(self, rootDirectory, kind):
        functionIdentifier = self.MINECRAFT_FUNCTION_COMMAND + ' ' + self.moduleNamespaces[rootDirectory.name] + self.MINECRAFT_NAMESPACE_PATH_SEPARATOR
        
        functionNames = self.getFunctionNames('', rootDirectory)
        self.stripFromDirectory(rootDirectory, functionNames, functionIdentifier)

    def getFunctionNames(self, path, virtualDirectory):
        functionNames = [self.assemblePath(path, virtualFile.name[:-len(self.MINECRAFT_FUNCTION_FILE_EXTENSION)]) for virtualFile in virtualDirectory.fileChildren if virtualFile.name.endswith(self.MINECRAFT_FUNCTION_FILE_EXTENSION)]

        for virtualChildDirectory in virtualDirectory.directoryChildren:
            functionNames += self.getFunctionNames(self.assemblePath(path, virtualChildDirectory.name), virtualChildDirectory)

        return functionNames

    def assemblePath(self, path, item):
        return item if path == '' else path + self.MINECRAFT_FUNCTION_PATH_SEPARATOR + item

    def stripFromDirectory(self, virtualDirectory, functionNames, functionIdentifier):
        for virtualFile in virtualDirectory.fileChildren:
            self.stripFromFile(virtualFile, functionNames, functionIdentifier)

        for virtualChildDirectory in virtualDirectory.directoryChildren:
            self.stripFromDirectory(virtualChildDirectory, functionNames, functionIdentifier)

    def stripFromFile(self, virtualFile, functionNames, functionIdentifier):
        lines = virtualFile.contents.split('\n')
        newLines = []

        for line in lines:
            addLine = True

            if functionIdentifier in line:
                pathIndex = line.index(functionIdentifier) + len(functionIdentifier)
                functionName = line[pathIndex:]
                if functionName not in functionNames:
                    addLine = False

            if addLine:
                newLines.append(line)

        virtualFile.contents = '\n'.join(newLines)
