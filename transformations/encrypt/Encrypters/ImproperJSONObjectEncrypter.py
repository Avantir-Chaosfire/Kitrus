from Encrypters.Utilities.BaseEncrypter import *

class ImproperJSONObjectEncrypter(BaseEncrypter):
    def __init__(self, namespaces, encryptedTerms, encryptCommand):
        super(ImproperJSONObjectEncrypter, self).__init__(namespaces, encryptedTerms, encryptCommand)

        self.name = 'Improper JSON Sub-Parts'
        
        self.commands = [
            'data',
            'summon',
            'execute'
        ]
        advanceRegularExpressions = [
            ['data merge entity ' + self.generalRegularExpressions['selector'], ''],
            ['summon [^ ]+ ' + self.generalRegularExpressions['vector']]
        ]

        self.createTemplates(advanceRegularExpressions, self.generalRegularExpressions['improperJSONObject'])

    def encryptTerm(self, term):
        return self.encryptImproperJSON(term)
