from Encrypters.Utilities.BaseEncrypter import *

class ItemEncrypter(BaseEncrypter):
    def __init__(self, namespaces, encryptedTerms):
        super(ItemEncrypter, self).__init__(namespaces, encryptedTerms)

        self.name = 'Item Sub-Parts'
        
        self.commands = [
            'clear',
            'clone',
            'data',
            'execute',
            'fill',
            'give',
            'particle',
            'replaceitem',
            'setblock'
        ]
        advanceRegularExpressions = [
            ['clear ' + self.generalRegularExpressions['selector'], ''],
            ['clone ' + self.generalRegularExpressions['vector'] + ' ' + self.generalRegularExpressions['vector'] + ' ' + self.generalRegularExpressions['vector'] + ' (filtered|masked|replace) (force|move|normal)'],
            ['data (merge|modify) block ' + self.generalRegularExpressions['vector']],
            ['(if|unless) (data)? block ' + self.generalRegularExpressions['vector']],
            ['fill ' + self.generalRegularExpressions['vector'] + ' ' + self.generalRegularExpressions['vector']],
            ['replace'],
            ['give ' + self.generalRegularExpressions['selector'], ''],
            ['replaceitem block ' + self.generalRegularExpressions['vector'] + ' [^ ]+ '],
            ['replaceitem entity ' + self.generalRegularExpressions['selector'], ' [^ ]+ '],
            ['particle (minecraft:)?(item|block)'],
            ['setblock ' + self.generalRegularExpressions['vector']]
        ]

        self.createTemplates(advanceRegularExpressions, self.generalRegularExpressions['item'])

    def encryptTerm(self, term):
        return self.encryptItem(term)
