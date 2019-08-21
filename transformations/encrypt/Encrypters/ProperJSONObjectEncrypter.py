from Encrypters.Utilities.BaseEncrypter import *

class ProperJSONObjectEncrypter(BaseEncrypter):
    def __init__(self, namespaces, encryptedTerms, encryptCommand):
        super(ProperJSONObjectEncrypter, self).__init__(namespaces, encryptedTerms, encryptCommand)

        self.name = 'Proper JSON Sub-Parts'
        
        self.commands = [
            'tellraw',
            'title',
            'execute'
        ]
        advanceRegularExpressions = [
            ['tellraw ' + self.generalRegularExpressions['selector'], ''],
            ['title ' + self.generalRegularExpressions['selector'], ' (title|subtitle|actionbar)']
        ]

        self.createTemplates(advanceRegularExpressions, self.generalRegularExpressions['properJSONObject'])

    def encryptTerm(self, term):
        return self.encryptProperJSON(term)
