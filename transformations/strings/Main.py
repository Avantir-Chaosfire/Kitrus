import copy, os

from KitrusRoot_Transformation import *
from StringLibrary import *
from Object import *
from UnescapeFunctions import *

class Main(Transformation):
    def __init__(self):
        super(Main, self).__init__()

        self.strings = StringLibrary()
        self.output.messages.append('Strings: ' + str(self.strings.size()))

    def apply(self, rootDirectory, kind):
        rootDirectory = self.applyToDirectory(rootDirectory, kind, '')

        self.output.warnings = self.strings.getWarnings()

    def applyToDirectory(self, directory, kind, errorPath):
        errorPath = os.path.join(errorPath, directory.name)
        
        i = 0
        for virtualFile in directory.fileChildren:
            if virtualFile.name == 'objects.odefs':
                directory.fileChildren.remove(virtualFile)

                virtualFile.contents = self.replaceStringKeys(virtualFile, kind)
                virtualObjectFileLines = virtualFile.contents.split('\n')
                objects = [Object(self.parseObject(line)) for line in virtualObjectFileLines]

                #directory class
                for virtualClassDirectory in directory.directoryChildren:
                    if virtualClassDirectory.name == 'class':
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
                
                for virtualClassFile in directory.fileChildren:
                    #file class
                    if virtualClassFile.name.startswith('class.') or virtualClassFile.name == 'class':
                        directory.fileChildren.remove(virtualClassFile)
                        
                        classFileNameComponents = virtualClassFile.name.split('.', 1)
                        classFileExtension = '.' + classFileNameComponents[1] if len(classFileNameComponents) > 1 else ''

                        for obj in objects:
                            virtualObjectFile = copy.copy(virtualClassFile)
                            virtualObjectFile.name = obj.name + classFileExtension
                            self.replaceObjectKeysInFile(virtualObjectFile, obj.args)
                            directory.fileChildren.append(virtualObjectFile)
                    #line class
                    else:
                        virtualClassFileLines = virtualClassFile.contents.split('\n')
                        virtualClassFileLines = [line + '\n' for line in virtualClassFileLines]

                        virtualClassFile.contents = ''
                        for line in virtualClassFileLines:
                            if line.startswith('#class '):
                                classLine = line[7:]
                                line = ''

                                for obj in objects:
                                    objectLine = classLine
                                    
                                    i = 0
                                    while i < len(obj.args):
                                        objectLine = objectLine.replace('#' + str(i) + '#', obj.args[i])
                                        i += 1

                                    line += objectLine
                            virtualClassFile.contents += line
                        virtualClassFile.contents = virtualClassFile.contents.rstrip('\n')
                break
            i += 1

        for virtualFile in directory.fileChildren:
            virtualFile.contents = self.replaceStringKeys(virtualFile, kind)

        for virtualDirectory in directory.directoryChildren:
            self.applyToDirectory(virtualDirectory, kind, errorPath)

    def replaceStringKeys(self, virtualFile, kind):
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
        arguments = line.split('$')

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
            virtualFile.contents = virtualFile.contents.replace('#' + str(i) + '#', args[i])
            i += 1

        virtualFile.contents = unescapeSymbols(virtualFile.contents, ESCAPED_PARAMETER_PATTERN)