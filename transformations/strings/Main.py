import copy, os

from KitrusRoot_Transformation import *
from KitrusRoot_VirtualDirectory import *
from StringLibrary import *
from Object import *
from UnescapeFunctions import *

class Main(Transformation):
    def __init__(self, configurationDirectory):
        self.OBJECT_FILE_EXTENSION = '.odefs'
        self.CLASS_KEYWORD = 'class'
        self.CLASS_LINE_METACHARACTER = '#'
        self.OBJECT_PARAMETER_METACHARACTER = '#'
        self.OBJECT_ARGUMENT_SEPARATION_METACHARACTER = '$'
        self.CLASS_OBJECT_ASSOCIATION_METACHARACTER = '$'
        self.CLASS_OBJECT_ASSOCIATION_DEFAULT_NAME = 'objects'
        self.STRINGS_DIRECTORY = 'strings'

        stringsConfigurationDirectory = VirtualDirectory(self.STRINGS_DIRECTORY)
        for virtualDirectory in configurationDirectory.directoryChildren:
            if virtualDirectory.name == self.STRINGS_DIRECTORY:
                stringsConfigurationDirectory = virtualDirectory
                break

        self.strings = StringLibrary(stringsConfigurationDirectory)
        self.outputMessage('Strings: ' + str(self.strings.size()))

    def apply(self, modules):
        for module in modules:
            self.outputMessage('Transforming ' + module.name + '...')
            module.rootDirectory = self.applyToDirectory(module.rootDirectory, module.kind, '')

            warnings = self.strings.getWarnings()
            for warning in warnings:
                self.outputWarning(warning)

#TODO: There's a semi-major problem here. Namely if you have two classes both with instances of the
#same name and both classes have a file with the same name, then which file actually gets used is
#arbitrary, based upon the order in which the classes' odefs files are parsed.
    def applyToDirectory(self, directory, kind, path):
        path = os.path.join(path, directory.name)

        newDirectoryFileChildren = copy.copy(directory.fileChildren)

        i = 0
        for virtualFile in directory.fileChildren:
            if virtualFile.name.endswith(self.OBJECT_FILE_EXTENSION):
                newDirectoryFileChildren.remove(virtualFile)
                
                virtualFile.contents = self.replaceStringKeys(virtualFile, kind, path)
                virtualObjectFileLines = virtualFile.contents.split('\n')
                objects = [Object(self.parseObject(line)) for line in virtualObjectFileLines if not line == '']

                classObjectAssociationName = virtualFile.name[:-len(self.OBJECT_FILE_EXTENSION)]
                classKeyword = self.CLASS_KEYWORD
                if not classObjectAssociationName == self.CLASS_OBJECT_ASSOCIATION_DEFAULT_NAME:
                    classKeyword = self.CLASS_KEYWORD + self.CLASS_OBJECT_ASSOCIATION_METACHARACTER + classObjectAssociationName

                #directory class
                for virtualClassDirectory in directory.directoryChildren:
                    if virtualClassDirectory.name == classKeyword:
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
                    if virtualClassFile.name.startswith(classKeyword + '.') or virtualClassFile.name == classKeyword:
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
                        classLineEstablisher = self.CLASS_LINE_METACHARACTER + classKeyword + ' '
                        virtualClassFileLines = virtualClassFile.contents.split('\n')
                        virtualClassFileLines = [line + '\n' for line in virtualClassFileLines]

                        virtualClassFile.contents = ''
                        for line in virtualClassFileLines:
                            if line.startswith(classLineEstablisher):
                                classLine = line[len(classLineEstablisher):]
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
            i += 1

        directory.fileChildren = newDirectoryFileChildren

        for virtualFile in directory.fileChildren:
            virtualFile.contents = self.replaceStringKeys(virtualFile, kind, path)

        for virtualDirectory in directory.directoryChildren:
            self.applyToDirectory(virtualDirectory, kind, path)

    def replaceStringKeys(self, virtualFile, kind, path):
        return self.strings.replaceStringKeys(path.split(os.sep)[1:], virtualFile.contents, kind, lambda l, m: self.strings.raiseExportWarning(os.path.join(path, virtualFile.name), l, m))

    def mergeDirectories(self, existingDirectory, transientDirectory):
        #Merge files
        for transientFile in transientDirectory.fileChildren:
            found = False
            for file in existingDirectory.fileChildren:
                if file.name == transientFile.name:
                    found = True
                    break
            if not found:
                existingDirectory.fileChildren.append(transientFile)

        #Merge child directories
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
