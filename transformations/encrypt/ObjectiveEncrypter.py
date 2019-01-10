from BaseEncrypter import *

def ObjectiveEncrypter(BaseEncrypter):
    def __init__(self, generalRegularExpressions, encryptedTerms):
        self.commands = [
            'execute',
            'scoreboard',
            'trigger'
        ]
        advanceRegularExpressions = [
            'scoreboard objectives (add|remove|modify)',
            'scoreboard objectives setdisplay (list|belowName|sidebar|(sidebar\.team\.[^ ]+))',
            'scoreboard players (get|add|remove|reset|enable|operation) ' + generalRegularExpressions['selector'],
            'trigger',
            '(if|unless) score ' + generalRegularExpressions['selector'],
            '(\+=|\-=|\*=|/=|%=|=|<|>|><|<=|>=)' + generalRegularExpressions['selector'],
            'store (result|success) score' + generalRegularExpressions['selector']
        ]

        super(ObjectiveEncrypter, self).__init__(encryptedTerms, advanceRegularExpressions, generalRegularExpressions['objective'])

    def encryptTerm(self, term):
        return super.encryptBaseTerm(term, 'objective')
