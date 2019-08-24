import json

from ConfigurationException import *

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

    def encryptFileContents(self, virtualFile, kind):
        if kind == 'functions':
            self.encryptFunctionsFileContents(virtualFile)
        elif kind == 'advancements':
            self.encryptAdvancementsFileContents(virtualFile)
        elif kind == 'tags':
            self.encryptTagsFileContents(virtualFile)
        else:
            raise ConfigurationException('Module kind "' + kind + '" not supported for encryption.')

    def encryptFunctionsFileContents(self, virtualFile):
        commands = virtualFile.contents.split('\n')
        newCommands = []

        for command in commands:
            if not command.startswith('#') and not command.isspace() and len(command) > 0:
                newCommands.append(self.encryptCommand(command))

        virtualFile.contents = '\n'.join(newCommands)

    def encryptAdvancementsFileContents(self, virtualFile):
        data = json.loads(virtualFile.contents)

        if 'rewards' in data and 'function' in data['rewards']:
            functionCall = data['rewards']['function']
            [namespace, functionName] = functionCall.split(':')
            if len(self.fileContentEncrypters) > 0 and namespace in self.fileContentEncrypters[0].fileEncryptedNamespaces:
                data['rewards']['function'] = namespace + ':' + self.functionNameEncrypter.encryptBaseTerm(functionName, 'function')

        if 'criteria' in data:
            for (key, value) in data['criteria'].items():
                if 'conditions' in value:
                    if 'entity' in value['conditions'] and 'nbt' in value['conditions']['entity']:
                        improperJSON = value['conditions']['entity']['nbt']
                        data['criteria'][key]['conditions']['entity']['nbt'] = self.functionNameEncrypter.encryptImproperJSON(improperJSON)
                    if 'damage' in value['conditions'] and 'source_entity' in value['conditions']['damage'] and 'nbt' in value['conditions']['damage']['source_entity']:
                        improperJSON = value['conditions']['damage']['source_entity']['nbt']
                        data['criteria'][key]['conditions']['damage']['source_entity']['nbt'] = self.functionNameEncrypter.encryptImproperJSON(improperJSON)

        virtualFile.contents = json.dumps(data)

    def encryptTagsFileContents(self, virtualFile):
        data = json.loads(virtualFile.contents)

        if 'values' in data:
            for i in range(len(data['values'])):
                functionCall = data['values'][i]
                [namespace, functionName] = functionCall.split(':')
                if len(self.fileContentEncrypters) > 0 and namespace in self.fileContentEncrypters[0].fileEncryptedNamespaces:
                    data['values'][i] = namespace + ':' + self.functionNameEncrypter.encryptBaseTerm(functionName, 'function')

        virtualFile.contents = json.dumps(data)

    def encryptCommand(self, command):
        for encrypter in self.fileContentEncrypters:
            command = encrypter.encrypt(command)
        return command

    def getUsageCounts(self):
        output = [self.namespaceName + ':']

        for encrypter in self.fileContentEncrypters:
            output.append('\t' + encrypter.name + ': ' + str(encrypter.usageCount))

        return output
