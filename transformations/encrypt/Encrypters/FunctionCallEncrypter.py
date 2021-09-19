from Encrypters.Utilities.BaseEncrypter import *

class FunctionCallEncrypter(BaseEncrypter):
    def __init__(self, namespaces, encryptedTerms, encryptCommand, outputMessage):
        super(FunctionCallEncrypter, self).__init__(namespaces, encryptedTerms, encryptCommand, outputMessage)

        self.name = 'Function Calls'
        
        self.commands = [
            'execute',
            'function',
            'schedule'
        ]
        advanceRegularExpressions = [
            ['function']
        ]

        self.createTemplates(advanceRegularExpressions, self.generalRegularExpressions['function'])

    def encryptTerm(self, term):
        [namespace, functionName] = term.split(':')
        return namespace + ':' + self.encryptBaseTerm(functionName, 'function')
