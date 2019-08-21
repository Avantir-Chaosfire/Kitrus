class NamespaceMapping:
    def __init__(self, namespaceName):
        self.namespaceName = namespaceName
        self.functionNameEncrypter = None
        self.fileContentEncrypters = []

    def setFunctionNameEncrypter(self, functionNameEncrypter):
        self.functionNameEncrypter = functionNameEncrypter

    def setFileContentEncrypters(self, fileContentEncrypters):
        self.fileContentEncrypters = fileContentEncrypters

    def getEncryptedFunctionName(self, term):
        return self.functionNameEncrypter.encryptBaseTerm(term, 'function')

    def encryptFileContents(self, virtualFile):
        commands = virtualFile.contents.split('\n')
        newCommands = []

        for command in commands:
            if not command.startswith('#') and not command.isspace() and len(command) > 0:
                newCommands.append(self.encryptCommand(command))

        virtualFile.contents = '\n'.join(newCommands)

    def encryptCommand(self, command):
        for encrypter in self.fileContentEncrypters:
            command = encrypter.encrypt(command)
        return command

    def getUsageCounts(self):
        output = [self.namespaceName + ':']

        for encrypter in self.fileContentEncrypters:
            output.append('\t' + encrypter.name + ': ' + str(encrypter.usageCount))

        return output
