from Encrypters.Utilities.BaseEncrypter import *

class TagEncrypter(BaseEncrypter):
    def __init__(self, namespaces, encryptedTerms):
        super(TagEncrypter, self).__init__(namespaces, encryptedTerms)

        self.name = 'Tags'
        
        self.commands = [
            'execute',
            'tag'
        ]
        advanceRegularExpressions = [
            ['tag ' + self.generalRegularExpressions['selector'], ' (add|remove)']
        ]

        self.createTemplates(advanceRegularExpressions, self.generalRegularExpressions['tag'])

    def encryptTerm(self, term):
        return self.encryptBaseTerm(term, 'tag')
