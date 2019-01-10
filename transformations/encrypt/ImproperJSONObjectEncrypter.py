from BaseEncrypter import *

def ImproperJSONObjectEncrypter(BaseEncrypter):
    def __init__(self, generalRegularExpressions, encryptedTerms):
        self.commands = [
            'data',
            'summon'
        ]
        advanceRegularExpressions = [
            'data merge entity ' + generalRegularExpressions['selector'],
            'summon [^ ]+ ' + generalRegularExpressions['vector']
        ]

        super(ImproperJSONObjectEncrypter, self).__init__(encryptedTerms, advanceRegularExpressions, generalRegularExpressions['improperJSONObject'])

    def encryptTerm(self, term):
        pass
