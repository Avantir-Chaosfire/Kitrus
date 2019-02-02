import secrets, string

from KitrusRoot_Transformation import *
from NamespaceMappings import *
from  import *

#TODO:
#-Save data
#-Fill in encryptTerm methods
#-Read in saved data
#-Check details about uniqueness of generated terms

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

    def apply(self, modules):
        modulesToEncryptFileNames = [
            module
            for module in modules
            if self.ENCRYPT_FILE_NAMES_PARAMETER_NAME in self.moduleEncryptionConfiguration[module.name]
                and self.moduleEncryptionConfiguration[module.name][self.ENCRYPT_FILE_NAMES_PARAMETER_NAME] == self.TRUE
        ]

        for module in modulesToEncryptFileNames:
            fileContentEncrypters = [
                FunctionCallEncrypter(),
                TagEncrypter(),
                ObjectiveEncrypter(),
                SelectorEncrypter(),
                ImproperJSONObjectEncrypter(),
                ProperJSONObjectEncrypter(),
                ItemEncrypter()
            ]

            functionNameEncrypter = BaseEncrypter()

            self.namespaceMappings[module.name] = NamespaceMapping(self.moduleNamespaces[module.name], functionNameEncrypter, fileContentEncrypters)
            self.encryptFunctionNames(module.name, module.rootDirectory)

        for module in modules:
            self.encryptFileContents(module.name, module.rootDirectory)

        if self.modifiedData: #This is not being set, and i don't think self.saveData is implemented
            self.saveData(self.transformationDataDirectory)
            self.modifiedData = False

    def encryptFunctionNames(self, moduleName, virtualDirectory):
        virtualDirectory.fileChildren = self.getFunctionNameMappings(moduleName, virtualDirectory)
        virtualDirectory.directoryChildren = []

    def getFunctionNameMappings(self, moduleName, virtualDirectory, path = ''):
        encryptedFiles = []
        for virtualFile in virtualDirectory.fileChildren:
            fileName, fileExtension = os.path.splittext(virtualFile.name)
            uniqueName = self.namespaceMappings[moduleName].getEncryptedFunctionName(fileName)
            encryptedFile = VirtualFile(uniqueName + fileExtension)
            encryptedFile.contents = virtualFile.contents
            encryptedFiles.append(encryptedFile)

        for virtualChildDirectory in virtualDirectory.directoryChildren:
            encryptedFiles += self.getFunctionNameMappings(moduleName, virtualChildDirectory, self.joinFunctionPath(path, virtualChildDirectory.name))

        return encryptedFiles

    def encryptFileContents(moduleName, virtualDirectory, path = ''):
        for virtualFile in virtualDirectory.fileChildren:
            self.namespaceMappings[moduleName].getEncryptedFileContents(virtualFile)

        for virtualChildDirectory in virtualDirectory.directoryChildren:
            self.encryptFileContents(moduleName, virtualChildDirectory, self.joinFunctionPath(path, virtualChildDirectory.name))
    
    def joinFunctionPath(self, path, name):
        return name if path == '' else path + '/' + name
