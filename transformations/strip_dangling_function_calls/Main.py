import copy, os

from KitrusRoot_Transformation import *

class Main(Transformation):
    def __init__(self):
        super(Main, self).__init__()
        self.MINECRAFT_FUNCTION_COMMAND = 'function'
        self.NAMESPACE = 'tlkot'
        self.MINECRAFT_NAMESPACE_PATH_SEPARATOR = ':'
        self.MINECRAFT_FUNCTION_PATH_SEPARATOR = '/'
        self.MINECRAFT_FUNCTION_FILE_EXTENSION = '.mcfunction'
        self.FUNCTION_IDENTIFIER = self.MINECRAFT_FUNCTION_COMMAND + ' ' + self.NAMESPACE + self.MINECRAFT_NAMESPACE_PATH_SEPARATOR

    def apply(self, rootDirectory, kind):
        functionNames = self.getFunctionNames('', rootDirectory)
        self.stripFromDirectory(rootDirectory, functionNames)

    def getFunctionNames(self, path, virtualDirectory):
        functionNames = [self.assemblePath(path, virtualFile.name[:-len(self.MINECRAFT_FUNCTION_FILE_EXTENSION)]) for virtualFile in virtualDirectory.fileChildren if virtualFile.name.endswith(self.MINECRAFT_FUNCTION_FILE_EXTENSION)]

        for virtualChildDirectory in virtualDirectory.directoryChildren:
            functionNames += self.getFunctionNames(self.assemblePath(path, virtualChildDirectory.name), virtualChildDirectory)

        return functionNames

    def assemblePath(self, path, item):
        return item if path == '' else path + self.MINECRAFT_FUNCTION_PATH_SEPARATOR + item

    def stripFromDirectory(self, virtualDirectory, functionNames):
        for virtualFile in virtualDirectory.fileChildren:
            self.stripFromFile(virtualFile, functionNames)

        for virtualChildDirectory in virtualDirectory.directoryChildren:
            self.stripFromDirectory(virtualChildDirectory, functionNames)

    def stripFromFile(self, virtualFile, functionNames):
        lines = virtualFile.contents.split('\n')
        newLines = []

        for line in lines:
            addLine = True

            if self.FUNCTION_IDENTIFIER in line:
                pathIndex = line.index(self.FUNCTION_IDENTIFIER) + len(self.FUNCTION_IDENTIFIER)
                functionName = line[pathIndex:]
                if functionName not in functionNames:
                    addLine = False

            if addLine:
                newLines.append(line)

        virtualFile.contents = '\n'.join(newLines)
