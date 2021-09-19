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
        self.STRIP_DANGLING_FUNCTION_CALLS_DIRECTORY = 'strip_dangling_function_calls'
        self.NAMESPACE_CONFIGURATION_FILE_NAME = 'namespaces.cfg'
        self.PARAMETER_CONFIGURATION_FILE_NAME = 'parameters.cfg'
        self.WARN_ABOUT_STRIPPED_CALLS_PARAMETER_NAME = 'warnAboutStrippedCalls'
        self.TRUE = 'true'

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

        sdfcConfigurationDirectory = VirtualDirectory(self.STRIP_DANGLING_FUNCTION_CALLS_DIRECTORY)
        for virtualDirectory in configurationDirectory.directoryChildren:
            if virtualDirectory.name == self.STRIP_DANGLING_FUNCTION_CALLS_DIRECTORY:
                sdfcConfigurationDirectory = virtualDirectory
                break

        lines = []
        for virtualFile in sdfcConfigurationDirectory.fileChildren:
            if virtualFile.name == self.PARAMETER_CONFIGURATION_FILE_NAME:
                lines = virtualFile.getContentsLines()
                break

        self.parameters = {}
        lineNumber = 1
        for line in lines:
            if not line == '':
                if '=' not in line:
                    raise ConfigurationParsingException('[' + self.PARAMETER_CONFIGURATION_FILE_NAME + ':' + str(lineNumber) + '] Expected to find "=".')
                indexOfEquals = line.index('=')
                self.parameters[line[:indexOfEquals]] = line[indexOfEquals + 1:]
            lineNumber += 1

        self.warnAboutStrippedCalls = False
        if self.WARN_ABOUT_STRIPPED_CALLS_PARAMETER_NAME in self.parameters and self.parameters[self.WARN_ABOUT_STRIPPED_CALLS_PARAMETER_NAME] == self.TRUE:
            self.warnAboutStrippedCalls = True

    def apply(self, modules):
        for module in modules:
            self.outputMessage('Transforming ' + module.name + '...')
            functionIdentifier = self.MINECRAFT_FUNCTION_COMMAND + ' ' + self.moduleNamespaces[module.rootDirectory.name] + self.MINECRAFT_NAMESPACE_PATH_SEPARATOR
            
            functionNames = self.getFunctionNames('', module.rootDirectory)
            self.stripFromDirectory(module.rootDirectory.name, module.rootDirectory, functionNames, functionIdentifier)

    def getFunctionNames(self, path, virtualDirectory):
        functionNames = [self.assemblePath(path, virtualFile.name[:-len(self.MINECRAFT_FUNCTION_FILE_EXTENSION)]) for virtualFile in virtualDirectory.fileChildren if virtualFile.name.endswith(self.MINECRAFT_FUNCTION_FILE_EXTENSION)]

        for virtualChildDirectory in virtualDirectory.directoryChildren:
            functionNames += self.getFunctionNames(self.assemblePath(path, virtualChildDirectory.name), virtualChildDirectory)

        return functionNames

    def assemblePath(self, path, item):
        return item if path == '' else path + self.MINECRAFT_FUNCTION_PATH_SEPARATOR + item

    def stripFromDirectory(self, path, virtualDirectory, functionNames, functionIdentifier):
        for virtualFile in virtualDirectory.fileChildren:
            self.stripFromFile(path, virtualFile, functionNames, functionIdentifier)

        for virtualChildDirectory in virtualDirectory.directoryChildren:
            self.stripFromDirectory(path + '/' + virtualChildDirectory.name, virtualChildDirectory, functionNames, functionIdentifier)

    def stripFromFile(self, path, virtualFile, functionNames, functionIdentifier):
        lines = virtualFile.getContentsLines()
        newLines = []

        for line in lines:
            addLine = True

            if functionIdentifier in line:
                pathIndex = line.index(functionIdentifier) + len(functionIdentifier)
                functionName = line[pathIndex:]
                if functionName not in functionNames:
                    if self.warnAboutStrippedCalls:
                        self.outputWarning(functionName + ' - [' + path + '/' + virtualFile.name.split('.')[0] + ']')
                    addLine = False

            if addLine:
                newLines.append(line)

        virtualFile.setContentsLines(newLines)
