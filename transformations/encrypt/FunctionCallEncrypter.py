from BaseEncrypter import *

def FunctionCallEncrypter(BaseEncrypter):
    def __init__(self):
        super(FunctionCallEncrypter, self).__init__()
        
        self.commands = [
            'execute',
            'function',
            'schedule'
        ]
        advanceRegularExpressions = [
            'function'
        ]

        super.createTemplates(advanceRegularExpressions, generalRegularExpressions['function'])

    def encryptTerm(self, term):
        [namespace, functionName] = term.split(':')
        return namespace + ':' + super.encryptBaseTerm(functionName, 'function')
