from BaseEncrypter import *

def FunctionEncrypter(BaseEncrypter):
    def __init__(self, generalRegularExpressions, encryptedTerms):
        self.commands = []

        super(FunctionEncrypter, self).__init__(encryptedTerms, [], '')

    def encryptTerm(self, term):
        return super.encryptBaseTerm(term, 'function')
