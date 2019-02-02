import json

from BaseEncrypter import *

def ProperJSONObjectEncrypter(BaseEncrypter):
    def __init__(self):
        super(ProperJSONObjectEncrypter, self).__init__()
        
        self.commands = [
            'tellraw',
            'title'
        ]
        advanceRegularExpressions = [
            'tellraw ' + super.generalRegularExpressions['selector'],
            'title ' + super.generalRegularExpressions['selector'] + ' (title|subtitle|actionbar)'
        ]

        super.createTemplates(advanceRegularExpressions, super.generalRegularExpressions['properJSONObject'])

    def encryptTerm(self, term):
        return super.encryptProperJSON(term)
