import string

from KitrusRoot_Transformation import *
from NamespaceMapping import *
from Encrypters.FunctionCallEncrypter import *
from Encrypters.ImproperJSONObjectEncrypter import *
from Encrypters.ItemEncrypter import *
from Encrypters.ObjectiveEncrypter import *
from Encrypters.ProperJSONObjectEncrypter import *
from Encrypters.SelectorEncrypter import *
from Encrypters.TagEncrypter import *

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
            if not line.isspace():
                if '=' not in line:
                    raise ConfigurationParsingException('[' + self.NAMESPACE_CONFIGURATION_FILE_NAME + ':' + str(lineNumber) + '] Expected to find "=".')
                indexOfEquals = line.index('=')
                self.moduleNamespaces[line[:indexOfEquals]] = line[indexOfEquals + 1:]
            lineNumber += 1

        self.moduleEncryptionConfiguration = {}
        for virtualFile in encryptConfigurationDirectory.fileChildren:
            moduleName = virtualFile.name[:-len(self.ENCRYPT_FILE_EXTENSION)]
            self.moduleEncryptionConfiguration[moduleName] = {}
            lines = virtualFile.getContentsLines()

            lineNumber = 1
            for line in lines:
                if not line.isspace():
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

        encryptedTerms = {
            'function': EncryptedTerms(string.digits + string.ascii_lowercase + '-_', 40),
            'tag': EncryptedTerms(string.digits + string.ascii_letters + '-_+.', 40),
            'objective': EncryptedTerms(string.digits + string.ascii_letters + '-_+.', 16)
        }

        self.loadEncryptedTermsFromTransformationDataDirectory(encryptedTerms)

        for module in modules:
            fileContentEncrypters = [
                FunctionCallEncrypter(self.moduleNamespaces.values(), encryptedTerms),
                TagEncrypter(self.moduleNamespaces.values(), encryptedTerms),
                ObjectiveEncrypter(self.moduleNamespaces.values(), encryptedTerms),
                SelectorEncrypter(self.moduleNamespaces.values(), encryptedTerms),
                ImproperJSONObjectEncrypter(self.moduleNamespaces.values(), encryptedTerms),
                ProperJSONObjectEncrypter(self.moduleNamespaces.values(), encryptedTerms),
                ItemEncrypter(self.moduleNamespaces.values(), encryptedTerms)
            ]

            functionNameEncrypter = BaseEncrypter(self.moduleNamespaces.values(), encryptedTerms)
            self.namespaceMappings[module.name] = NamespaceMapping(self.moduleNamespaces[module.name], functionNameEncrypter, fileContentEncrypters)

        for module in modulesToEncryptFileNames:
            self.encryptFunctionNames(module.name, module.rootDirectory)

        for module in modules:
            self.encryptFileContents(module.name, module.rootDirectory)
            for message in self.namespaceMappings[module.name].getUsageCounts():
                self.outputMessage(message)

        self.writeEncryptedTermsToTransformationDataDirectory(encryptedTerms)
        self.saveData(self.transformationDataDirectory)

    def loadEncryptedTermsFromTransformationDataDirectory(self, encryptedTerms):
        for virtualFile in self.transformationDataDirectory.fileChildren:
            name = virtualFile.name[:-len('.cfg')]
            if name in encryptedTerms:
                for line in virtualFile.contents.split('\n'):
                    if not line.isspace():
                        components = line.split('=')
                        if not len(components) == 2:
                            raise Exception('Can\'t parse encryption configuration line: ' + line)
                        encryptedTerms[name].values[components[0]] = components[1]

    def writeEncryptedTermsToTransformationDataDirectory(self, encryptedTerms):
        self.transformationDataDirectory.fileChildren = []
        for (name, terms) in encryptedTerms.items():
            virtualFile = VirtualFile(name + '.cfg')
            for (unencryptedValue, encryptedValue) in terms.values.items():
                virtualFile.contents += unencryptedValue + '=' + encryptedValue + '\n'
            self.transformationDataDirectory.fileChildren.append(virtualFile)

    def encryptFunctionNames(self, moduleName, virtualDirectory):
        virtualDirectory.fileChildren = self.getFunctionNameMappings(moduleName, virtualDirectory)
        virtualDirectory.directoryChildren = []

    def getFunctionNameMappings(self, moduleName, virtualDirectory, path = ''):
        encryptedFiles = []
        for virtualFile in virtualDirectory.fileChildren:
            fileName, fileExtension = os.path.splitext(virtualFile.name)
            uniqueName = self.namespaceMappings[moduleName].getEncryptedFunctionName(self.joinFunctionPath(path, fileName))
            encryptedFile = VirtualFile(uniqueName + fileExtension)
            encryptedFile.contents = virtualFile.contents
            encryptedFiles.append(encryptedFile)

        for virtualChildDirectory in virtualDirectory.directoryChildren:
            encryptedFiles += self.getFunctionNameMappings(moduleName, virtualChildDirectory, self.joinFunctionPath(path, virtualChildDirectory.name))

        return encryptedFiles

    def encryptFileContents(self, moduleName, virtualDirectory):
        for virtualFile in virtualDirectory.fileChildren:
            self.namespaceMappings[moduleName].encryptFileContents(virtualFile)

        for virtualChildDirectory in virtualDirectory.directoryChildren:
            self.encryptFileContents(moduleName, virtualChildDirectory)
    
    def joinFunctionPath(self, path, name):
        return name if path == '' else path + '/' + name
