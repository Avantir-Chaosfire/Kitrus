from BaseEncrypter import *

def ObjectiveEncrypter(BaseEncrypter):
    def __init__(self):
        super(ObjectiveEncrypter, self).__init__()
        
        self.commands = [
            'execute',
            'scoreboard',
            'trigger'
        ]
        advanceRegularExpressions = [
            'scoreboard objectives (add|remove|modify)',
            'scoreboard objectives setdisplay (list|belowName|sidebar|(sidebar\.team\.[^ ]+))',
            'scoreboard players (get|add|remove|reset|enable|operation) ' + super.generalRegularExpressions['selector'],
            'trigger',
            '(if|unless) score ' + super.generalRegularExpressions['selector'],
            '(\+=|\-=|\*=|/=|%=|=|<|>|><|<=|>=)' + super.generalRegularExpressions['selector'],
            'store (result|success) score' + super.generalRegularExpressions['selector']
        ]

        super.createTemplates(advanceRegularExpressions, super.generalRegularExpressions['objective'])

    def encryptTerm(self, term):
        return super.encryptBaseTerm(term, 'objective')
