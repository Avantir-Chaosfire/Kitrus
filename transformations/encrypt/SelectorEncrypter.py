from BaseEncrypter import *

def SelectorEncrypter(BaseEncrypter):
    def __init__(self, generalRegularExpressions, encryptedTerms):
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
            'particle [^ ]+(((block|falling_dust|item) [^ ]+)|(dust ' + generalRegularExpressions['vector'] + ' ' + generalRegularExpressions['vector'] + '))? ' + generalRegularExpressions['vector'] + ' ' + generalRegularExpressions['vector'] + ' ' + generalRegularExpressions['numerical'] + ' ' + generalRegularExpressions['numerical'] + ' (normal|force)',
            'playsound [^ ]+ (master|music|record|weather|block|hostile|neutral|player|ambient|voice)',
            'recipe (give|take)',
            'replaceitem entity',
            'say .*',
            'scoreboard players (list|get|set|add|remove|reset|enable|operation)',
            'spreadplayers ' + generalRegularExpressions['vector'] + ' ' + generalRegularExpressions['numerical'] + ' (true|false)',
            'team join [^ ]+',
            'team leave'
        ]

        super(SelectorEncrypter, self).__init__(encryptedTerms, advanceRegularExpressions, generalRegularExpressions['selector'])

    def encryptTerm(self, term):
        pass
