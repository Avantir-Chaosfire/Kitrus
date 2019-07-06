import copy, os

from KitrusRoot_Transformation import *
from KitrusRoot_VirtualDirectory import *
from StringLibrary import *
from Class import *
from Object import *
from UnescapeFunctions import *

class Main(Transformation):
    def __init__(self, configurationDirectory, transformationDataDirectory, saveData):
        self.OBJECT_FILE_EXTENSION = '.odefs'
        self.CLASS_KEYWORD = 'class'
        self.CLASS_LINE_METACHARACTER = '#'
        self.OBJECT_PARAMETER_METACHARACTER_START = '<'
        self.OBJECT_PARAMETER_METACHARACTER_END = '>'
        self.OBJECT_ARGUMENT_SEPARATION_METACHARACTER = '$'
        self.CLASS_OBJECT_ASSOCIATION_METACHARACTER = '$'
        self.CLASS_OBJECT_ASSOCIATION_DEFAULT_NAME = 'objects'
        self.STRINGS_DIRECTORY = 'strings'
        self.PRIORITY_KEYWORD = 'priority'

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
                self.outputWarnings(warning)

    def applyToDirectory(self, directory, kind, path):
        path = os.path.join(path, directory.name)

        newDirectoryFileChildren = copy.copy(directory.fileChildren)
        self.priorityValues = {}

        classesToExpand = []

        i = 0
        for virtualFile in directory.fileChildren:
            if virtualFile.name.endswith(self.OBJECT_FILE_EXTENSION):
                newDirectoryFileChildren.remove(virtualFile)
                
                virtualFile.contents = self.replaceStringKeys(virtualFile, kind, path)
                virtualObjectFileLines = virtualFile.getContentsLines()
                
                priority = 0
                if len(virtualObjectFileLines) > 0 and virtualObjectFileLines[0].startswith(self.CLASS_LINE_METACHARACTER + self.PRIORITY_KEYWORD + ' '):
                    priorityString = virtualObjectFileLines[0][len(self.CLASS_LINE_METACHARACTER + self.PRIORITY_KEYWORD + ' '):]
                    virtualObjectFileLines = virtualObjectFileLines[1:]
                    try:
                        priority = int(priorityString)
                    except ValueError:
                        self.strings.raiseExportWarning(os.path.join(path, virtualFile.name), 1, 'Cannot parse priority value (Must be an integer): ' + str(priorityString))
                    if priority < 0:
                        self.strings.raiseExportWarning(os.path.join(path, virtualFile.name), 1, 'Illegal priority value (Must be positive): ' + str(priority))
                        priority = 0
                    
                objects = [Object(self.parseObject(line)) for line in virtualObjectFileLines if self.lineIsObject(line)]
                classObjectAssociationName = virtualFile.name[:-len(self.OBJECT_FILE_EXTENSION)]

                classesToExpand.append(Class(objects, priority, classObjectAssociationName))
            i += 1

        classesToExpand.sort(key = lambda c: c.priority, reverse = True)
        for classToExpand in classesToExpand:
            classKeyword = self.CLASS_KEYWORD
            if not classToExpand.classObjectAssociationName == self.CLASS_OBJECT_ASSOCIATION_DEFAULT_NAME:
                classKeyword = self.CLASS_KEYWORD + self.CLASS_OBJECT_ASSOCIATION_METACHARACTER + classToExpand.classObjectAssociationName

            #directory class
            for virtualClassDirectory in directory.directoryChildren:
                if virtualClassDirectory.name == classKeyword:
                    directory.directoryChildren.remove(virtualClassDirectory)
                        
                    for obj in classToExpand.objects:
                        merge = False
                        for virtualObjectDirectory in directory.directoryChildren:
                            if virtualObjectDirectory.name == obj.name:
                                merge = True
                                transientVirtualObjectDirectory = copy.deepcopy(virtualClassDirectory)
                                self.replaceObjectKeysInDirectory(transientVirtualObjectDirectory, obj.args)
                                self.mergeDirectories(virtualObjectDirectory, transientVirtualObjectDirectory, classToExpand.priority, os.path.join(path, obj.name))
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

                    for obj in classToExpand.objects:
                        virtualObjectFile = copy.copy(virtualClassFile)
                        virtualObjectFile.name = obj.name + classFileExtension
                        if virtualObjectFile.name not in list(map(lambda f: f.name, newDirectoryFileChildren)):
                            self.replaceObjectKeysInFile(virtualObjectFile, obj.args)
                            newDirectoryFileChildren.append(virtualObjectFile)
                        
                #line class
                else:
                    classLineEstablisher = self.CLASS_LINE_METACHARACTER + classKeyword + ' '
                    virtualClassFileLines = virtualClassFile.getContentsLines()
                    virtualClassFileLines = [line + '\n' for line in virtualClassFileLines]

                    virtualClassFile.contents = ''
                    for line in virtualClassFileLines:
                        if line.startswith(classLineEstablisher):
                            classLine = line[len(classLineEstablisher):]
                            line = ''

                            for obj in classToExpand.objects:
                                objectLine = classLine
                                
                                i = 0
                                while i < len(obj.args):
                                    objectLine = objectLine.replace(self.OBJECT_PARAMETER_METACHARACTER_START + str(i) + self.OBJECT_PARAMETER_METACHARACTER_END, obj.args[i])
                                    i += 1

                                line += objectLine
                        virtualClassFile.contents += line
                    virtualClassFile.contents = virtualClassFile.contents.rstrip('\n')

        directory.fileChildren = newDirectoryFileChildren

        for virtualFile in directory.fileChildren:
            virtualFile.contents = self.replaceStringKeys(virtualFile, kind, path)

        for virtualDirectory in directory.directoryChildren:
            self.applyToDirectory(virtualDirectory, kind, path)

    def replaceStringKeys(self, virtualFile, kind, path):
        return self.strings.replaceStringKeys(path.split(os.sep)[1:], virtualFile.contents, kind, lambda l, m: self.strings.raiseExportWarning(os.path.join(path, virtualFile.name), l, m))

    def mergeDirectories(self, existingDirectory, transientDirectory, priority, path):
        #Merge files
        for transientFile in transientDirectory.fileChildren:
            found = False
            fullTransientName = os.path.join(path, transientFile.name)
            for file in existingDirectory.fileChildren:
                if file.name == transientFile.name:
                    if fullTransientName in self.priorityValues.keys():
                        if priority > self.priorityValues[fullTransientName]:
                            self.priorityValues[fullTransientName] = priority
                            file.contents = transientFile.contents
                        elif priority == self.priorityValues[fullTransientName]:
                            self.strings.raiseExportWarning(fullTransientName, -1, 'Inheritance conflict between files of equal priority (' + ('None' if priority == 0 else str(priority)) + ').')
                    found = True
                    break
            if not found:
                self.priorityValues[fullTransientName] = priority
                existingDirectory.fileChildren.append(transientFile)

        #Merge child directories
        for transientChildDirectory in transientDirectory.directoryChildren:
            merge = False
            for childDirectory in existingDirectory.directoryChildren:
                if childDirectory.name == transientChildDirectory.name:
                    merge = True
                    self.mergeDirectories(childDirectory, transientChildDirectory, priority, os.path.join(path, childDirectory.name))
                    break
            if not merge:
                existingDirectory.directoryChildren.append(transientChildDirectory)

    def lineIsObject(self, line):
        notEmpty = not line == ''
        notComment = not line.startswith(self.OBJECT_ARGUMENT_SEPARATION_METACHARACTER)

        return notEmpty and notComment

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
            virtualFile.contents = virtualFile.contents.replace(self.OBJECT_PARAMETER_METACHARACTER_START + str(i) + self.OBJECT_PARAMETER_METACHARACTER_END, args[i])
            i += 1

        virtualFile.contents = unescapeSymbols(virtualFile.contents, ESCAPED_PARAMETER_PATTERN)
