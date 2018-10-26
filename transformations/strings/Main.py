import copy, os

from KitrusRoot_Transformation import *
from StringLibrary import *
from Object import *
from UnescapeFunctions import *

class Main(Transformation):
    def __init__(self):
        super(Main, self).__init__()

        self.OBJECT_FILE_NAME = 'objects.odefs'
        self.CLASS_KEYWORD = 'class'
        self.CLASS_LINE_METACHARACTER = '#'
        self.OBJECT_PARAMETER_METACHARACTER = '#'
        self.OBJECT_ARGUMENT_SEPARATION_METACHARACTER = '$'

        self.strings = StringLibrary()
        self.output.messages.append('Strings: ' + str(self.strings.size()))

    def apply(self, rootDirectory, kind):
        rootDirectory = self.applyToDirectory(rootDirectory, kind, '')

        self.output.warnings = self.strings.getWarnings()

    def applyToDirectory(self, directory, kind, errorPath):
        errorPath = os.path.join(errorPath, directory.name)

        i = 0
        for virtualFile in directory.fileChildren:
            if virtualFile.name == self.OBJECT_FILE_NAME:
                directory.fileChildren.remove(virtualFile)

                virtualFile.contents = self.replaceStringKeys(virtualFile, kind, errorPath)
                virtualObjectFileLines = virtualFile.contents.split('\n')
                objects = [Object(self.parseObject(line)) for line in virtualObjectFileLines]

                #directory class
                for virtualClassDirectory in directory.directoryChildren:
                    if virtualClassDirectory.name == self.CLASS_KEYWORD:
                        directory.directoryChildren.remove(virtualClassDirectory)
                            
                        for obj in objects:
                            merge = False
                            for virtualObjectDirectory in directory.directoryChildren:
                                if virtualObjectDirectory.name == obj.name:
                                    merge = True
                                    transientVirtualObjectDirectory = copy.deepcopy(virtualClassDirectory)
                                    self.replaceObjectKeysInDirectory(transientVirtualObjectDirectory, obj.args)
                                    self.mergeDirectories(virtualObjectDirectory, transientVirtualObjectDirectory)
                                    break
                                
                            if not merge:
                                virtualObjectDirectory = copy.deepcopy(virtualClassDirectory)
                                virtualObjectDirectory.name = obj.name
                                self.replaceObjectKeysInDirectory(virtualObjectDirectory, obj.args)
                                directory.directoryChildren.append(virtualObjectDirectory)
                        break
                    
                newDirectoryFileChildren = copy.copy(directory.fileChildren)
                for virtualClassFile in directory.fileChildren:
                    #file class
                    if virtualClassFile.name.startswith(self.CLASS_KEYWORD + '.') or virtualClassFile.name == self.CLASS_KEYWORD:
                        newDirectoryFileChildren.remove(virtualClassFile)
                        
                        classFileNameComponents = virtualClassFile.name.split('.', 1)
                        classFileExtension = '.' + classFileNameComponents[1] if len(classFileNameComponents) > 1 else ''

                        for obj in objects:
                            virtualObjectFile = copy.copy(virtualClassFile)
                            virtualObjectFile.name = obj.name + classFileExtension
                            self.replaceObjectKeysInFile(virtualObjectFile, obj.args)
                            newDirectoryFileChildren.append(virtualObjectFile)
                    #line class
                    else:
                        virtualClassFileLines = virtualClassFile.contents.split('\n')
                        virtualClassFileLines = [line + '\n' for line in virtualClassFileLines]

                        virtualClassFile.contents = ''
                        for line in virtualClassFileLines:
                            if line.startswith(self.CLASS_LINE_METACHARACTER + self.CLASS_KEYWORD + ' '):
                                classLine = line[7:]
                                line = ''

                                for obj in objects:
                                    objectLine = classLine
                                    
                                    i = 0
                                    while i < len(obj.args):
                                        objectLine = objectLine.replace(self.OBJECT_PARAMETER_METACHARACTER + str(i) + self.OBJECT_PARAMETER_METACHARACTER, obj.args[i])
                                        i += 1

                                    line += objectLine
                            virtualClassFile.contents += line
                        virtualClassFile.contents = virtualClassFile.contents.rstrip('\n')
                directory.fileChildren = newDirectoryFileChildren
                break
            i += 1

        for virtualFile in directory.fileChildren:
            virtualFile.contents = self.replaceStringKeys(virtualFile, kind, errorPath)

        for virtualDirectory in directory.directoryChildren:
            self.applyToDirectory(virtualDirectory, kind, errorPath)

    def replaceStringKeys(self, virtualFile, kind, errorPath):
        return self.strings.replaceStringKeys(virtualFile.contents, kind, lambda l, m: self.strings.raiseExportWarning(os.path.join(errorPath, virtualFile.name), l, m))

    def mergeDirectories(self, existingDirectory, transientDirectory):
        existingDirectory.fileChildren += transientDirectory.fileChildren
        for transientChildDirectory in transientDirectory.directoryChildren:
            merge = False
            for childDirectory in existingDirectory.directoryChildren:
                if childDirectory.name == transientChildDirectory.name:
                    merge = True
                    self.mergeDirectories(childDirectory, transientChildDirectory)
                    break
            if not merge:
                existingDirectory.directoryChildren.append(transientChildDirectory)

    def parseObject(self, line):
        arguments = line.split(self.OBJECT_ARGUMENT_SEPARATION_METACHARACTER)

        arguments = unescapeParameterSeparators(arguments)

        for i in range(0, len(arguments)):
            startIndex = 0
            endIndex = len(arguments[i])
            while startIndex < endIndex and arguments[i][startIndex] in [' ', '\t']:
                startIndex += 1
            while startIndex < endIndex and arguments[i][endIndex - 1] in [' ', '\t']:
                endIndex -= 1
            arguments[i] = arguments[i][startIndex:endIndex]

        return arguments

    def replaceObjectKeysInDirectory(self, virtualParentDirectory, args):
        for virtualFile in virtualParentDirectory.fileChildren:
            self.replaceObjectKeysInFile(virtualFile, args)
                    
        for virtualDirectory in virtualParentDirectory.directoryChildren:
            self.replaceObjectKeysInDirectory(virtualDirectory, args)

    def replaceObjectKeysInFile(self, virtualFile, args):
        i = 0
        while i < len(args):
            virtualFile.contents = virtualFile.contents.replace(self.OBJECT_PARAMETER_METACHARACTER + str(i) + self.OBJECT_PARAMETER_METACHARACTER, args[i])
            i += 1

        virtualFile.contents = unescapeSymbols(virtualFile.contents, ESCAPED_PARAMETER_PATTERN)
