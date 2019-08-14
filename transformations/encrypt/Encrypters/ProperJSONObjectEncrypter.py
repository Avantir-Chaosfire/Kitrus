from Encrypters.Utilities.BaseEncrypter import *

class ProperJSONObjectEncrypter(BaseEncrypter):
    def __init__(self, namespaces, encryptedTerms):
        super(ProperJSONObjectEncrypter, self).__init__(namespaces, encryptedTerms)

        self.name = 'Proper JSON Sub-Parts'
        
        self.commands = [
            'tellraw',
            'title'
        ]
        advanceRegularExpressions = [
            'tellraw ' + self.generalRegularExpressions['selector'],
            'title ' + self.generalRegularExpressions['selector'] + ' (title|subtitle|actionbar)'
        ]

        self.createTemplates(advanceRegularExpressions, self.generalRegularExpressions['properJSONObject'])

    def encryptTerm(self, term):
        return self.encryptProperJSON(term)
