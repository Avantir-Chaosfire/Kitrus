from BaseEncrypter import *
from ParsingData import *

def FunctionEncrypter(BaseEncrypter):
    def __init__(self, generalRegularExpressions):
        super(FunctionEncrypter, self).__init__()

        self.validCharacters = string.digits + string.ascii_lowercase + '-_'
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
        pass
