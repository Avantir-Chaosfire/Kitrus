from Encrypters.Utilities.BaseEncrypter import *

class ObjectiveEncrypter(BaseEncrypter):
    def __init__(self, namespaces, encryptedTerms, encryptCommand):
        super(ObjectiveEncrypter, self).__init__(namespaces, encryptedTerms, encryptCommand)

        self.name = 'Scoreboard Objective Names'
        
        self.commands = [
            'execute',
            'scoreboard',
            'trigger'
        ]
        advanceRegularExpressions = [
            ['scoreboard objectives (add|remove|modify)'],
            ['scoreboard objectives setdisplay (list|belowName|sidebar|(sidebar\.team\.[^ ]+))'],
            ['scoreboard players (get|set|add|remove|reset|enable|operation) ' + self.generalRegularExpressions['selector'], ''],
            ['trigger'],
            ['(if|unless) score ' + self.generalRegularExpressions['selector'], ''],
            ['(\+=|\-=|\*=|/=|%=|=|<|>|><|<=|>=) ' + self.generalRegularExpressions['selector'], ''],
            ['store (result|success) score ' + self.generalRegularExpressions['selector'], '']
        ]

        self.createTemplates(advanceRegularExpressions, self.generalRegularExpressions['objective'])

    def encryptTerm(self, term):
        return self.encryptBaseTerm(term, 'objective')
