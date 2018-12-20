from FunctionEncrypter import *

def ParsingData:
    def __init__(self, namespaces):
        generalRegularExpressions = {}
        
        generalRegularExpressions['function'] = '(' + '|'.join(namespaces) + '):([' + re.escape(self.functions.validCharacters) + ']+)'
        generalRegularExpressions['tag'] = '([' + re.escape(self.tags.validCharacters) + ']+)'
        generalRegularExpressions['objective'] = '([' + re.escape(self.objectives.validCharacters) + ']+)'
        generalRegularExpressions['selector'] = '@[aeprs](\[(.+=.+)*\])?'
        generalRegularExpressions['numerical'] = '[0123456789]+(\.[0123456789]+)?'
        generalRegularExpressions['vector'] = numericalRegularExpression + ' ' + numericalRegularExpression + ' ' + numericalRegularExpression
        generalRegularExpressions['improperJSONObject'] = '{([^ ]+:.+)*}'
        generalRegularExpressions['properJSONObject'] = '{("[^ ]+":.+)*}'
        generalRegularExpressions['item'] = '[^ ]+' + improperJSONObjectRegularExpression

        self.functionEncrypter = FunctionEncrypter(generalRegularExpressions)
    
        #Tags
        self.tags = Term()
        self.tags.validcharacters = string.digits + string.ascii_letters + '-_+.'
        self.tags.commands = [
            'execute',
            'tag'
        ]
        tagsAdvanceRegularExpressions = [
            'tag (add|remove)'
        ]
        for re in tagsAdvanceRegularExpressions:
            self.tags.templates.append(ParsingTemplate(re, tagRegularExpression))

        #Objectives
        self.objectives = Term()
        self.objectives.validCharacters = string.digits + string.ascii_letters + '-_+.'
        self.objectives.commands = [
            'execute',
            'scoreboard',
            'trigger'
        ]
        objectivesAdvanceRegularExpressions = [
            'scoreboard objectives (add|remove|modify)',
            'scoreboard objectives setdisplay (list|belowName|sidebar|(sidebar\.team\.[^ ]+))',
            'scoreboard players (get|add|remove|reset|enable|operation) ' + selectorRegularExpression,
            'trigger',
            '(if|unless) score ' + selectorRegularExpression,
            '(\+=|\-=|\*=|/=|%=|=|<|>|><|<=|>=)' + selectorRegularExpression,
            'store (result|success) score' + selectorRegularExpression
        ]
        for re in objectivesAdvanceRegularExpressions:
            self.objectives.templates.append(ParsingTemplate(re, objectiveRegularExpression))

        #Selectors
        self.selectors = TermParsingData()
        self.selectors.commands = [
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
        selectorsAdvanceRegularExpressions = [
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
            'particle [^ ]+(((block|falling_dust|item) [^ ]+)|(dust ' + vectorRegularExpression + ' ' + numericalRegularExpression + '))? ' + vectorRegularExpression + ' ' + vectorRegularExpression + ' ' + numericalRegularExpression + ' ' + numericalRegularExpression + ' (normal|force)',
            'playsound [^ ]+ (master|music|record|weather|block|hostile|neutral|player|ambient|voice)',
            'recipe (give|take)',
            'replaceitem entity',
            'say .*',
            'scoreboard players (list|get|set|add|remove|reset|enable|operation)',
            'spreadplayers ' + vectorRegularExpression + ' ' + numericalRegularExpression + ' (true|false)',
            'team join [^ ]+',
            'team leave'
        ]
        for re in selectorsAdvanceRegularExpressions:
            self.selectors.templates.append(ParsingTemplate(re, selectorRegularExpression))

        #Improper JSON Objects (Entities)
        self.improperJSONObjects = TermParsingData()
        self.improperJSONObjects.commands = [
            'data',
            'summon'
        ]
        improperJSONObjectsAdvanceRegularExpressions = [
            'data merge entity ' + selectorRegularExpression,
            'summon [^ ]+ ' + vectorRegularExpression
        ]
        for re in improperJSONObjectsAdvanceRegularExpressions:
            self.improperJSONObjects.templates.append(ParsingTemplate(re, improperJSONObjectRegularExpression))

        #Proper JSON Objects (Raw JSON Text)
        self.properJSONObjects = TermParsingData()
        self.properJSONObjects.commands = [
            'tellraw',
            'title'
        ]
        properJSONObjectsAdvanceRegularExpressions = [
            'tellraw ' + selectorRegularExpression,
            'title ' + selectorRegularExpression + ' (title|subtitle|actionbar)'
        ]
        for re in properJSONObjectsAdvanceRegularExpressions:
            self.properJSONObjects.templates.append(ParsingTemplate(re, properJSONObjectRegularExpression))

        #Items
        self.items = TermParsingData()
        self.items.commands = [
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
        itemsAdvanceRegularExpressions = [
            'clear ' + selectorRegularExpression,
            'clone ' + vectorRegularExpression + ' ' + vectorRegularExpression + ' ' + vectorRegularExpression + ' (filtered|masked|replace) (force|move|normal)',
            'data merge block ' + vectorRegularExpression,
            '(if|unless) block ' + vectorRegularExpression,
            'fill ' + vectorRegularExpression + ' ' + vectorRegularExpression,
            'replace',
            'give ' + selectorRegularExpression,
            'replaceitem block ' + vectorRegularExpression + ' [^ ]+ ',
            'replaceitem entity ' + selectorRegularExpression + ' [^ ]+ ',
            'particle (minecraft:)(item|block)',
            'setblock ' + vectorRegularExpression
        ]
        for re in itemsAdvanceRegularExpressions:
            self.items.templates.append(ParsingTemplate(re, itemRegularExpression))
