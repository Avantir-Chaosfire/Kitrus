from Encrypters.Utilities.BaseEncrypter import *

class SelectorEncrypter(BaseEncrypter):
    def __init__(self, namespaces, encryptedTerms):
        super(SelectorEncrypter, self).__init__(namespaces, encryptedTerms)

        self.name = 'Selector Sub-Parts'
        
        self.commands = [
            'advancement',
            'bossbar',
            'clear',
            'data',
            'effect',
            'enchant',
            'execute',
            'experience',
            'gamemode',
            'give',
            'kill',
            'loot',
            'msg',
            'particle',
            'playsound',
            'recipe',
            'replaceitem',
            'say',
            'scoreboard',
            'spawnpoint',
            'spreadplayers',
            'stopsound',
            'tag',
            'team',
            'teleport',
            'tell',
            'tellraw',
            'title',
            'tp',
            'w',
            'xp',
        ]
        advanceRegularExpressions = [
            'advancement (grant|revoke)',
            'bossbar set [^ ]+ players',
            '(clear|enchant|give|kill|tell|msg|w|at|spawnpoint|stopsound|tag|teleport|tp|tellraw|title)',
            'data (get|merge|remove|modify) entity',
            'effect (give|clear)',
            '(experience|xp) (add|set|query)',
            '(positioned|rotated)? as',
            'facing entity',
            '(if|unless) (data)? (entity|score)',
            '(\+=|\-=|\*=|/=|%=|=|<|>|><|<=|>=)',
            'store (result|success) (score|entity)',
            'gamemode (survival|creative|adventure|spectator)',
            'loot (entity|give)',
            'particle [^ ]+(((block|falling_dust|item) [^ ]+)|(dust ' + self.generalRegularExpressions['vector'] + ' ' + self.generalRegularExpressions['vector'] + '))? ' + self.generalRegularExpressions['vector'] + ' ' + self.generalRegularExpressions['vector'] + ' ' + self.generalRegularExpressions['numerical'] + ' ' + self.generalRegularExpressions['numerical'] + ' (normal|force)',
            'playsound [^ ]+ (master|music|record|weather|block|hostile|neutral|player|ambient|voice)',
            'recipe (give|take)',
            'replaceitem entity',
            'say .*',
            'scoreboard players (list|get|set|add|remove|reset|enable|operation)',
            'spreadplayers ' + self.generalRegularExpressions['vector'] + ' ' + self.generalRegularExpressions['numerical'] + ' (true|false)',
            'team join [^ ]+',
            'team leave'
        ]

        self.createTemplates(advanceRegularExpressions, self.generalRegularExpressions['selector'])

    def encryptTerm(self, term):
        return self.encryptSelector(term)
