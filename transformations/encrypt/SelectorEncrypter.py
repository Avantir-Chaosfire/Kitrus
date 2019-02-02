from BaseEncrypter import *

def SelectorEncrypter(BaseEncrypter):
    def __init__(self):
        super(SelectorEncrypter, self).__init__()
        
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
            'data (get|merge|remove) entity',
            'effect (give|clear)',
            '(experience|xp) (add|set|query)',
            '(positioned|rotated)? as',
            'facing entity',
            '(if|unless) (entity|score)',
            '(\+=|\-=|\*=|/=|%=|=|<|>|><|<=|>=)',
            'store (result|success) (score|entity)',
            'gamemode (survival|creative|adventure|spectator)',
            'loot replace entity',
            'loot give',
            'particle [^ ]+(((block|falling_dust|item) [^ ]+)|(dust ' + super.generalRegularExpressions['vector'] + ' ' + super.generalRegularExpressions['vector'] + '))? ' + super.generalRegularExpressions['vector'] + ' ' + super.generalRegularExpressions['vector'] + ' ' + super.generalRegularExpressions['numerical'] + ' ' + super.generalRegularExpressions['numerical'] + ' (normal|force)',
            'playsound [^ ]+ (master|music|record|weather|block|hostile|neutral|player|ambient|voice)',
            'recipe (give|take)',
            'replaceitem entity',
            'say .*',
            'scoreboard players (list|get|set|add|remove|reset|enable|operation)',
            'spreadplayers ' + super.generalRegularExpressions['vector'] + ' ' + super.generalRegularExpressions['numerical'] + ' (true|false)',
            'team join [^ ]+',
            'team leave'
        ]

        super.createTemplates(advanceRegularExpressions, super.generalRegularExpressions['selector'])

    def encryptTerm(self, term):
        super.encryptSelector(term)
