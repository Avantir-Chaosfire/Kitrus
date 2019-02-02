from BaseEncrypter import *

def ImproperJSONObjectEncrypter(BaseEncrypter):
    def __init__(self):
        super(ImproperJSONObjectEncrypter, self).__init__()
        
        self.commands = [
            'data',
            'summon'
        ]
        advanceRegularExpressions = [
            'data merge entity ' + super.generalRegularExpressions['selector'],
            'summon [^ ]+ ' + super.generalRegularExpressions['vector']
        ]

        super.createTemplates(advanceRegularExpressions, super.generalRegularExpressions['improperJSONObject'])

    def encryptTerm(self, term):
        return super.encryptImproperJSON(term)
