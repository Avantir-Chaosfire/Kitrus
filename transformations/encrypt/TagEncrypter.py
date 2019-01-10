from BaseEncrypter import *

def TagEncrypter(BaseEncrypter):
    def __init__(self, generalRegularExpressions, encryptedTerms):
        self.commands = [
            'execute',
            'tag'
        ]
        advanceRegularExpressions = [
            'tag (add|remove)'
        ]

        super(TagEncrypter, self).__init__(encryptedTerms, advanceRegularExpressions, generalRegularExpressions['tag'])

    def encryptTerm(self, term):
        return super.encryptBaseTerm(term, 'tag')
