import copy, os, codecs

from KitrusRoot_Transformation import *
from KitrusRoot_VirtualDirectory import *

from ConfigurationParsingException import *

class Main(Transformation):
    def __init__(self, configurationDirectory, transformationDataDirectory, saveData):
        self.MINECRAFT_FUNCTION_COMMAND = 'function'
        self.MINECRAFT_NAMESPACE_PATH_SEPARATOR = ':'
        self.MINECRAFT_FUNCTION_PATH_SEPARATOR = '/'
        self.MINECRAFT_FUNCTION_FILE_EXTENSION = '.mcfunction'
        self.NAMESPACES_DIRECTORY = 'namespaces'
        self.NAMESPACE_CONFIGURATION_FILE_NAME = 'namespaces.cfg'

        namespaceConfigurationDirectory = VirtualDirectory(self.NAMESPACES_DIRECTORY)
        for virtualDirectory in configurationDirectory.directoryChildren:
            if virtualDirectory.name == self.NAMESPACES_DIRECTORY:
                namespaceConfigurationDirectory = virtualDirectory
                break

        lines = []
        for virtualFile in namespaceConfigurationDirectory.fileChildren:
            if virtualFile.name == self.NAMESPACE_CONFIGURATION_FILE_NAME:
                lines = virtualFile.getContentsLines()
                break

        self.moduleNamespaces = {}
        lineNumber = 1
        for line in lines:
            if not line == '':
                if '=' not in line:
                    raise ConfigurationParsingException('[' + self.NAMESPACE_CONFIGURATION_FILE_NAME + ':' + str(lineNumber) + '] Expected to find "=".')
                indexOfEquals = line.index('=')
                self.moduleNamespaces[line[:indexOfEquals]] = line[indexOfEquals + 1:]
            lineNumber += 1

    def apply(self, modules):
        for module in modules:
            self.outputMessage('Transforming ' + module.name + '...')
            functionIdentifier = self.MINECRAFT_FUNCTION_COMMAND + ' ' + self.moduleNamespaces[module.rootDirectory.name] + self.MINECRAFT_NAMESPACE_PATH_SEPARATOR
            
            functionNames = self.getFunctionNames('', module.rootDirectory)
            self.stripFromDirectory(module.rootDirectory, functionNames, functionIdentifier)

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
        lines = virtualFile.getContentsLines()
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

        virtualFile.setContentsLines(newLines)
