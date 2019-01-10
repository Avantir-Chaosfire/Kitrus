from BaseEncrypter import *

def FunctionCallEncrypter(BaseEncrypter):
    def __init__(self, generalRegularExpressions, encryptedTerms):
        self.commands = [
            'execute',
            'function',
            'schedule'
        ]
        advanceRegularExpressions = [
            'function'
        ]

        super(FunctionCallEncrypter, self).__init__(encryptedTerms, advanceRegularExpressions, generalRegularExpressions['function'])

    def encryptTerm(self, term):
        [namespace, functionName] = term.split(':')
        return namespace + ':' + super.encryptBaseTerm(functionName, 'function')
