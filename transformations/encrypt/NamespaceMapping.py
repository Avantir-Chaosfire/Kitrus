class NamespaceMapping:
    def __init__(self, namespaceName, functionNameEncrypter, fileContentEncrypters):
        self.namespaceName = namespaceName
        self.functionNameEncrypter = functionNameEncrypter
        self.fileContentEncrypters = fileContentEncrypters

    def getEncryptedFunctionName(self, term):
        return self.functionNameEncrypter.encryptBaseTerm(term, 'function')

    def encryptFileContents(self, virtualFile):
        for encrypter in self.fileContentEncrypters:
            virtualFile.contents = encrypter.encrypt(virtualFile.contents)

    def getUsageCounts(self):
        output = [self.namespaceName + ':']

        for encrypter in self.fileContentEncrypters:
            output.append('\t' + encrypter.name + ': ' + str(encrypter.usageCount))

        return output
