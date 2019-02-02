class NamespaceMappings:
    def __init__(self, namespaceName, functionNameEncrypter, fileContentEncrypters):
        self.namespaceName = namespaceName
        self.functionNameEncrypter = functionNameEncrypter
        self.fileContentEncrypters = fileContentEncrypters

    def getEncryptedFunctionName(self, term):
        return self.functionNameEncrypter.encryptBaseTerm(term, 'function')

    def getEncryptedFileContents(self, virtualFile):
        for encrypter in self.fileContentEncrypters:
            virtualFile.contents = encrypter.encrypt(virtualFile.contents)
