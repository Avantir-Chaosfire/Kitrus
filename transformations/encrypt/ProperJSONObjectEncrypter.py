from BaseEncrypter import *

def ProperJSONObjectEncrypter(BaseEncrypter):
    def __init__(self, generalRegularExpressions, encryptedTerms):
        self.commands = [
            'tellraw',
            'title'
        ]
        advanceRegularExpressions = [
            'tellraw ' + generalRegularExpressions['selector'],
            'title ' + generalRegularExpressions['selector'] + ' (title|subtitle|actionbar)'
        ]

        super(ProperJSONObjectEncrypter, self).__init__(encryptedTerms, advanceRegularExpressions, generalRegularExpressions['properJSONObject'])

    def encryptTerm(self, term):
        pass
