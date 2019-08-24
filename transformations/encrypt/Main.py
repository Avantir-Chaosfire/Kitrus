import string, re

from KitrusRoot_Transformation import *
from KitrusRoot_VirtualDirectory import *
from NamespaceMapping import *
from ConfigurationException import *
from ConfigurationParsingException import *
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
        self.LOOK_FOR_WARNINGS_PARAMETER_NAME = 'lookForWarnings'
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
            if not line.isspace() and len(line) > 0:
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
                if not line.isspace() and len(line) > 0:
                    if '=' not in line:
                        raise ConfigurationParsingException('[' + virtualFile.name + ':' + str(lineNumber) + '] Expected to find "=".')
                    indexOfEquals = line.index('=')
                    self.moduleEncryptionConfiguration[moduleName][line[:indexOfEquals]] = line[indexOfEquals + 1:]
                lineNumber += 1

        self.namespaceMappings = {}

    def apply(self, modules):
        self.outputWarning('The encrypter does not use the same algorithm as regular minecraft command parsing, and doesn\'t even use a proper parser. If you are using this transformation, ERRORS WILL LIKELY OCCUR. Make sure to carefully test the results of this transformation, and update it for whatever cases you need to handle.')
        
        for module in modules:
            if not module.name in self.moduleEncryptionConfiguration:
                raise ConfigurationException('No configuration file found for ' + module.name + '.')
            if not module.name in self.moduleNamespaces:
                raise ConfigurationException('No namespace defined for ' + module.name + '.')
        
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

        namespaces = [self.moduleNamespaces[module.name] for module in modulesToEncryptFileNames]
        for module in modules:
            self.namespaceMappings[module.name] = NamespaceMapping(self.moduleNamespaces[module.name])
            encryptCommand = self.namespaceMappings[module.name].encryptCommand

            functionNameEncrypter = BaseEncrypter(self.moduleNamespaces.values(), encryptedTerms, encryptCommand)
            fileContentEncrypters = [
                FunctionCallEncrypter(namespaces, encryptedTerms, encryptCommand),
                TagEncrypter(namespaces, encryptedTerms, encryptCommand),
                ObjectiveEncrypter(namespaces, encryptedTerms, encryptCommand),
                SelectorEncrypter(namespaces, encryptedTerms, encryptCommand),
                ImproperJSONObjectEncrypter(namespaces, encryptedTerms, encryptCommand),
                ProperJSONObjectEncrypter(namespaces, encryptedTerms, encryptCommand),
                #ItemEncrypter(namespaces, encryptedTerms, encryptCommand)
            ]

            self.namespaceMappings[module.name].setFunctionNameEncrypter(functionNameEncrypter)
            self.namespaceMappings[module.name].setFileContentEncrypters(fileContentEncrypters)

        for module in modulesToEncryptFileNames:
            self.encryptFunctionNames(module.name, module.rootDirectory)

        lookForWarnings = False
        for module in modules:
            self.encryptFileContents(module.name, module.kind, module.rootDirectory)
            for message in self.namespaceMappings[module.name].getUsageCounts():
                self.outputMessage(message)

            lookForWarnings |= self.LOOK_FOR_WARNINGS_PARAMETER_NAME in self.moduleEncryptionConfiguration[module.name] and self.moduleEncryptionConfiguration[module.name][self.LOOK_FOR_WARNINGS_PARAMETER_NAME] == self.TRUE

        if lookForWarnings:
            for kind, terms in encryptedTerms.items():
                unencryptedTermValues = terms.values.keys()
                encryptedTermValues = terms.values.values()
                commonTerms = list(set(unencryptedTermValues) & set(encryptedTermValues))
                if len(commonTerms) > 0:
                    self.outputWarning('Found values common to encrypted and unecrypted ' + kind + ':')
                    for term in commonTerms:
                        self.outputWarning('\t' + term)

                for term in terms.values.keys():
                    filesContainingTerm = []
                    for module in modules:
                        for virtualFile in module.rootDirectory.fileChildren:
                            if not re.search('(^|[{,"! ])' + re.escape(term) + '($|[= \n\r\],"])', virtualFile.contents) == None:
                                filesContainingTerm.append(virtualFile)
                    if len(filesContainingTerm) > 0:
                        self.outputWarning('Found "' + term + '" in:')
                        for virtualFile in filesContainingTerm:
                            self.outputWarning('\t' + virtualFile.name)

        self.writeEncryptedTermsToTransformationDataDirectory(encryptedTerms)
        self.saveData(self.transformationDataDirectory)

    def loadEncryptedTermsFromTransformationDataDirectory(self, encryptedTerms):
        for virtualFile in self.transformationDataDirectory.fileChildren:
            name = virtualFile.name[:-len('.cfg')]
            if name in encryptedTerms:
                for line in virtualFile.contents.split('\n'):
                    if not line.isspace() and len(line) > 0:
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

    def encryptFileContents(self, moduleName, kind, virtualDirectory):
        for virtualFile in virtualDirectory.fileChildren:
            self.namespaceMappings[moduleName].encryptFileContents(virtualFile, kind)

        for virtualChildDirectory in virtualDirectory.directoryChildren:
            self.encryptFileContents(moduleName, kind, virtualChildDirectory)
    
    def joinFunctionPath(self, path, name):
        return name if path == '' else path + '/' + name
