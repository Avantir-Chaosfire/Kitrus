from BaseEncrypter import *

def TagEncrypter(BaseEncrypter):
    def __init__(self):
        super(TagEncrypter, self).__init__()
        
        self.commands = [
            'execute',
            'tag'
        ]
        advanceRegularExpressions = [
            'tag (add|remove)'
        ]

        super.createTemplates(advanceRegularExpressions, super.generalRegularExpressions['tag'])

    def encryptTerm(self, term):
        return super.encryptBaseTerm(term, 'tag')
