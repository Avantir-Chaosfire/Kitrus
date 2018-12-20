import secrets, string

from KitrusRoot_Transformation import *
from NamespaceMappings import *
from ParsingData import *

class Main(Transformation):
    def __init__(self, configurationDirectory, transformationDataDirectory, saveData):
        self.TRANSFORMATION_NAME = 'encrypt'
        self.ENCRYPT_DIRECTORY = 'encrypt'
        self.NAMESPACES_DIRECTORY = 'namespaces'
        self.NAMESPACE_CONFIGURATION_FILE_NAME = 'namespaces.cfg'
        self.ENCRYPT_FILE_EXTENSION = '.cfg'
        self.ENCRYPT_FILE_NAMES_PARAMETER_NAME = 'encrypt_file_names'
        self.TRUE = 'true'

        self.transformationDataDirectory = transformationDataDirectory
        self.modifiedData = False
        self.saveData = saveData

        namespaceConfigurationDirectory = VirtualDirectory(self.NAMESPACES_DIRECTORY)
        for virtualDirectory in configurationDirectory.directoryChildren:
            if virtualDirectory.name == self.NAMESPACES_DIRECTORY:
                namespaceConfigurationDirectory = virtualDirectory
                break

        encryptConfigurationDirectory = VirtualDirectory(self.ENCRYPT_DIRECTORY)
        for virtualDirectory in configurationDirectory.directoryChildren:
            if virtualDirectory.name == self.ENCRYPT_DIRECTORY:
                encryptConfigurationDirectory = virtualDirectory
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

        self.moduleEncryptionConfiguration = {}
        for virtualFile in encryptConfigurationDirectory.fileChildren():
            moduleName = virtualFile.name[:-len(self.ENCRYPT_FILE_EXTENSION)]
            self.moduleEncryptionConfiguration[moduleName] = {}
            lines = virtualFile.getContentsLines()

            lineNumber = 1
            for line in line:
                if '=' not in line:
                    raise ConfigurationParsingException('[' + virtualFile.name + ':' + str(lineNumber) + '] Expected to find "=".')
                indexOfEquals = line.index('=')
                self.moduleEncryptionConfiguration[moduleName][line[:indexOfEquals]] = line[indexOfEquals + 1:]
                lineNumber += 1

        self.namespaceMappings = {}
        self.parsingData = ParsingData(self.moduleNamespaces.values())

    def apply(self, modules):
        modulesToEncryptFileNames = [
            module
            for module in modules
            if self.ENCRYPT_FILE_NAMES_PARAMETER_NAME in self.moduleEncryptionConfiguration[module.name]
                and self.moduleEncryptionConfiguration[module.name][self.ENCRYPT_FILE_NAMES_PARAMETER_NAME] == self.TRUE]

        for module in modulesToEncryptFileNames:
            self.namespaceMappings[module.name] = NamespaceMapping(self.moduleNamespaces[module.name], '')
            self.encryptFunctionNames(module.name, module.rootDirectory)

        for module in modules:
            self.encryptTagsObjectivesAndFunctionCalls(module.name, module.rootDirectory)

        if self.modifiedData:
            self.saveData(self.transformationDataDirectory)
            self.modifiedData = False

    def encryptFunctionNames(self, moduleName, virtualDirectory):
        virtualDirectory.fileChildren = self.getFunctionNameMappings(moduleName, virtualDirectory, '')
        virtualDirectory.directoryChildren = []        

    def getFunctionNameMappings(self, moduleName, virtualDirectory, path):
        encryptedFiles = []
        for virtualFile in virtualDirectory.fileChildren:
            fileName, fileExtension = os.path.splittext(virtualFile.name)
            uniqueName = self.generateUniqueFunctionName()
            self.namespaceMappings[moduleName].functions[self.joinFunctionPath(path, fileName)] = uniqueName
            encryptedFile = VirtualFile(uniqueName + fileExtension)
            encryptedFile.contents = virtualFile.contents
            encryptedFiles.append(encryptedFile)

        for virtualChildDirectory in virtualDirectory.directoryChildren:
            encryptedFiles += self.getFunctionMappings(moduleName, virtualChildDirectory, self.joinFunctionPath(path, virtualChildDirectory.name))

        return encryptedFiles

    def encryptTagsObjectivesAndFunctionCalls(moduleName, virtualDirectory, path):
        for virtualFile in virtualDirectory.fileChildren:
            self.encryptContents(moduleName, virtualFile)

        for virtualChildDirectory in virtualDirectory.directoryChildren:
            self.encryptTagsObjectivesAndFunctionCalls(moduleName, virtualChildDirectory, self.joinFunctionPath(path, virtualChildDirectory.name))

    def encryptContents(self, moduleName, virtualFile):
        lines = virtualFile.getContentsLines()
        for i in range(len(lines)):
            if lines[i] == '' or lines[i][0] == '#' or lines[i].isspace():
                continue
            commandName = line.split(' ')[0]
            if commandName in self.FUNCTION_COMMANDS:
                lines[i] = self.encryptFunctionCommand(moduleName, lines[i])
            if commandName in self.TAG_COMMANDS:
                lines[i] = self.encryptTagCommand(moduleName, lines[i])
            if commandName in self.OBJECTIVE_COMMANDS:
                lines[i] = self.encryptObjectiveCommand(moduleName, lines[i])
            if commandName in self.SELECTOR_COMMANDS:
                lines[i] = self.encryptSelectorCommand(moduleName, lines[i])
        virtualFile.setContentsLines(lines)

##    def encryptFunctionCommand(self, moduleName, command):
##        args = command.split(' ')
##
##        indexOfFunction = -1
##        try:
##            indexOfFunction = args.index('function')
##        except ValueError:
##            return command
##
##        if self.validateArgs(args[indexOfFunction:], 1,
##            [
##                lambda a: self.isFunctionName(self.namespaceMappings[moduleName].namespaceName, a)
##            ]):
##            indexOfFunction += 1
##        else:
##            return command
##
##        function = args[indexOfFunction]
##        if function not in self.namespaceMapping[moduleName].keys():
##            self.namespaceMapping[moduleName][function] = self.generateUniqueFunctionName()
##        args[indexOfFunction] = self.namespaceMapping[moduleName][function]
##
##        return ' '.join(args)
##
##    def encryptTagCommand(self, moduleName, command):
##        args = command.split(' ')
##
##        indexOfTag = -1
##        try:
##            indexOfTag = args.index('tag')
##        except ValueError:
##            return command
##
##        if self.validateArgs(args[indexOfTag:], 3,
##            [
##                self.isSelector,
##                lambda a: a in ['add', 'remove']
##            ]):
##            indexOfTag += 3
##        else:
##            return command
##
##        tag = args[indexOfTag]
##        if tag not in self.namespaceMapping[moduleName].keys():
##            self.namespaceMapping[moduleName][tag] = self.generateUniqueTagName()
##        args[indexOfTag] = self.namespaceMapping[moduleName][tag]
##
##        return ' '.join(args)
##
##    def encryptObjectiveCommand(self, moduleName, command):
##        args = command.split(' ')
##
##        indexOfScoreboard = -1
##        try:
##            indexOfScoreboard = args.index('scoreboard')
##        except ValueError:
##            return command
##
##        if self.validateArgs(args[indexOfTag:], 3,
##            [
##                self.isSelector,
##                lambda a: a in ['add', 'remove']
##            ]):
##            indexOfTag += 3
##        else:
##            return command
##
##        tag = args[indexOfTag]
##        if tag not in self.namespaceMapping[moduleName].keys():
##            self.namespaceMapping[moduleName][tag] = self.generateUniqueTagName()
##        args[indexOfTag] = self.namespaceMapping[moduleName][tag]
##
##        return ' '.join(args)
##
##    def encryptSelectorCommand(self, moduleName, command):
##        pass
##
##    def validateArgs(self, args, amount, validations):
##        if not self.hasArgs(args, amount):
##            return False
##
##        if amount < len(validations):
##            raise InvalidParsingException() #Need to implement, and should also rename all kitrus exceptions to errors
##        
##        for i in range(len(validations)):
##            if not validations[i] == None and not validations[i](args[i + 1]):
##                return False
##
##        return True
##
##    def hasArgs(self, args, amount):
##        if len(args) < amount + 1:
##            return False
##        
##        for i in range(len(amount)):
##            if args[i + 1] == '':
##                return False
##
##        return True
##
##    def isSelector(self, arg):
##        return not re.match(, arg) == None #This is only a basic match/check. It doesn't validate any of the selectors arguments
    
    def joinFunctionPath(self, path, name):
        return name if path == '' else path + '/' + name

    def generateUniqueFunctionName(self): #Possible to gunarantee these will be unique? or at least figure out the chance of a duplicate?
        return self.generateUniqueName(self.parsingData.functions.validCharacters, 40)

    def generateUniqueTagName(self):
        return self.generateUniqueName(self.parsingData.tags.validCharacters, 40)

    def generateUniqueObjectiveName(self):
        return self.generateUniqueName(self.parsingData.objectives.validCharacters, 16)

    def generateUniqueName(self, characterSet, length):
        return ''.join(secrets.choice(characterSet) for _ in range(length))
