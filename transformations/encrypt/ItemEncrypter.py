from BaseEncrypter import *

def ItemEncrypter(BaseEncrypter):
    def __init__(self, generalRegularExpressions, encryptedTerms):
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
            'clear ' + generalRegularExpressions['selector'],
            'clone ' + generalRegularExpressions['vector'] + ' ' + generalRegularExpressions['vector'] + ' ' + generalRegularExpressions['vector'] + ' (filtered|masked|replace) (force|move|normal)',
            'data merge block ' + generalRegularExpressions['vector'],
            '(if|unless) block ' + generalRegularExpressions['vector'],
            'fill ' + generalRegularExpressions['vector'] + ' ' + generalRegularExpressions['vector'],
            'replace',
            'give ' + generalRegularExpressions['selector'],
            'replaceitem block ' + generalRegularExpressions['vector'] + ' [^ ]+ ',
            'replaceitem entity ' + generalRegularExpressions['selector'] + ' [^ ]+ ',
            'particle (minecraft:)(item|block)',
            'setblock ' + generalRegularExpressions['vector']
        ]

        super(ItemEncrypter, self).__init__(encryptedTerms, advanceRegularExpressions, generalRegularExpressions['item'])

    def encryptTerm(self, term):
        pass
