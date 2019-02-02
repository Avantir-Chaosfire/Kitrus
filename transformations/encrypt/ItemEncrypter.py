from BaseEncrypter import *

def ItemEncrypter(BaseEncrypter):
    def __init__(self):
        super(ItemEncrypter, self).__init__()
        
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
            'clear ' + super.generalRegularExpressions['selector'],
            'clone ' + super.generalRegularExpressions['vector'] + ' ' + super.generalRegularExpressions['vector'] + ' ' + super.generalRegularExpressions['vector'] + ' (filtered|masked|replace) (force|move|normal)',
            'data merge block ' + super.generalRegularExpressions['vector'],
            '(if|unless) block ' + super.generalRegularExpressions['vector'],
            'fill ' + super.generalRegularExpressions['vector'] + ' ' + super.generalRegularExpressions['vector'],
            'replace',
            'give ' + super.generalRegularExpressions['selector'],
            'replaceitem block ' + super.generalRegularExpressions['vector'] + ' [^ ]+ ',
            'replaceitem entity ' + super.generalRegularExpressions['selector'] + ' [^ ]+ ',
            'particle (minecraft:)(item|block)',
            'setblock ' + super.generalRegularExpressions['vector']
        ]

        super.createTemplates(advanceRegularExpressions, super.generalRegularExpressions['item'])

    def encryptTerm(self, term):
        super.encryptItem(term)
