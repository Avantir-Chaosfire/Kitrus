import re, json, secrets

from Encrypters.Utilities.Template import *
from Encrypters.Utilities.EncryptedTerms import *

class BaseEncrypter:
    def __init__(self, namespaces, encryptedTerms):
        self.encryptedTerms = encryptedTerms
    
        self.numericalRegularExpression = '[0123456789]+(\.[0123456789]+)?'
        self.improperJSONObjectRegularExpression = '{([^ ]+:.+)*}'

        self.generalRegularExpressions = {
            'function': '(' + '|'.join(namespaces) + '):([' + re.escape(encryptedTerms['function'].validCharacters) + ']+)',
            'tag': '([' + re.escape(encryptedTerms['tag'].validCharacters) + ']+)',
            'objective': '([' + re.escape(encryptedTerms['objective'].validCharacters) + ']+)',
            'selector': '@[aeprs](\[(.+=.+)*\])?',
            'numerical': self.numericalRegularExpression,
            'vector': self.numericalRegularExpression + ' ' + self.numericalRegularExpression + ' ' + self.numericalRegularExpression,
            'improperJSONObject': self.improperJSONObjectRegularExpression,
            'properJSONObject': '{("[^ ]+":.+)*}',
            'item': '[^ ]+' + self.improperJSONObjectRegularExpression
        }

        self.usageCount = 0

    def createTemplates(self, advanceRegularExpressions, targetRegularExpression):
        self.templates = []

        for regularExpression in advanceRegularExpressions:
            self.templates.append(Template(regularExpression, targetRegularExpression))

    def encrypt(self, rawCommands):
        commands = rawCommands.split('\n')
        newCommands = []

        for command in commands:
            if not command.startswith('#') and not command.isspace():
                commandName = command.split(' ')[0]
                if commandName in self.commands:
                    for template in self.templates:
                        match = template.match(command)
                        if not match == None:
                            commandBeforeMatch = command[:match.start]
                            commandAfterMatch = command[match.end:]
                            matchedTerm = command[match.start:match.end]
                            command = commandBeforeMatch + self.encryptTerm(matchedTerm) + commandAfterMatch
                newCommands.append(command)

        return '\n'.join(newCommands)

    def encryptTerm(self, term):
        raise NotImplementedError()

    def encryptSelector(self, selector):
        if '[' in selector and ']' in selector:
            indexOfOpeningBracket = selector.index('[')

            if indexOfOpeningBracket == len('@x') and selector.endswith(']'):
                data = self.getFlatImproperJSONKeyValuePairs(selector[2:], '[', ']', '=')
                if 'tag' in data:
                    data['tag'] = list(map(self.encryptSelectorTag, data['tag']))
                if 'scores' in data:
                    data['scores'] = list(map(self.encryptObjectivesList, data['scores']))
                if 'nbt' in data:
                    data['nbt'] = [self.encryptImproperJSON(nbt) for nbt in data['nbt'] if self.isImproperJSON(nbt)]

            return selector[:2] + self.encloseAsList(list(map(self.assembleRawKeyValuePairList, data.items())))
        return selector

    def encryptImproperJSON(self, improperJSON):
        data = self.getFlatImproperJSONKeyValuePairs(improperJSON, '{', '}', ':')
        if 'Tags' in data and data['Tags'].startswith('[') and data['Tags'].endswith(']'):
            data['Tags'] = self.encloseAsList(list(map(self.encryptQuotedTag, data['Tags'][1:-1].split(','))))
        return self.encloseAsObject([key + ':' + value[0] for key, value in data.items()])

    def encryptProperJSON(self, properJSON):
        data = json.loads(properJSON)

        data = encryptFlatJSONText(data)

        if 'extra' in data:
            data['extra'] = list(map(encryptFlatJSONText, data['extra']))

        return json.dumps(data)

    def encryptItem(self, item):
        startOfImproperJSON = item.index('{')
        if startOfImproperJSON > 0 and item.endswith('}'):
            item = item[:startOfImproperJSON] + self.encryptImproperJSON(item[startOfImproperJSON:])

    def encryptFlatJSONText(self, flatJSONText):
        if 'selector' in flatJSONText:
            flatJSONText['selector'] = self.encryptSelector(flatJSONText['selector'])

        if 'score' in flatJSONText:
            if 'name' in flatJSONText['score'] and flatJSONText['score']['name'].startswith('@'):
                flatJSONText['score']['name'] = self.encryptSelector(flatJSONText['score']['name'])
                
            if 'objective' in flatJSONText['score']:
                flatJSONText['score']['objective'] = self.encryptBaseTerm(flatJSONText['score']['objective'], 'objective')
        
        return flatJSONText

    def getFlatImproperJSONKeyValuePairs(self, sequence, openingBrace, closingBrace, assignmentOperator):
        result = {}
        if sequence.startswith(openingBrace) and sequence.endswith(closingBrace):
            sequence = sequence[1:-1]
            state = 'key'
            key = ''
            value = ''
            escapeLevel = 0
            currentIndex = 0
            while currentIndex < len(sequence):
                if state == 'key':
                    if sequence == assignmentOperator:
                        state = 'value'
                    else:
                        key += sequence[currentIndex]
                elif state == 'value':
                    if sequence[currentIndex] in '{[':
                        escapeLevel += 1
                    elif sequence[currentIndex] in '}]':
                        escapeLevel -= 1
                    elif sequence[currentIndex] == ',':
                        if key not in result:
                            result[key] = []
                        result[key].append(value)
                        state = 'key'
                    else:
                        value += sequence[currentIndex]
                currentIndex += 1
            if not key == '' and not value == '':
                if key not in result:
                    result[key] = []
                result[key].append(value)
        return result

    def encryptQuotedTag(self, tag):
        return '"' + self.encryptBaseTerm(tag[1:-1], 'tag') + '"' if tag.startswith('"') and tag.endswith('"') else tag

    def assembleRawKeyValuePairList(self, key, values):
        return ','.join([key + '=' + value for value in values])

    def encryptObjectivesList(self, objectives):
        return self.encloseAsObject(list(map(self.getFlatImproperJSONKeyValuePairs(objectives, '{', '}', '=').items(), self.assembleObjectiveKeyValuePair)))

    def assembleObjectiveKeyValuePair(self, key, value):
        return self.encryptBaseTerm(key, 'objective') + '=' + value

    def isImproperJSON(self, term):
        return not re.match(self.generalRegularExpressions['improperJSONObject'] + '$', term) == None

    def encryptSelectorTag(self, tag):
        return self.encryptBaseTerm(tag[1:], 'tag') if tag.startswith('!') else self.encryptBaseTerm(tag, 'tag')

    def encloseAsList(self, terms):
        return '[' + ','.join(terms) + ']'

    def encloseAsObject(self, terms):
        return '{' + ','.join(terms) + '}'

    def encryptBaseTerm(self, term, kind):
        self.usageCount += 1
        
        if term not in self.encryptedTerms[kind].values:
            uniqueName = self.generateUniqueName(kind)
            while uniqueName in self.encryptedTerms[kind].values.values():
                uniqueName = self.generateUniqueName(kind)
            self.encryptedTerms[kind].values[term] = uniqueName
        return self.encryptedTerms[kind].values[term]

    def generateUniqueName(self, kind):
        return ''.join(secrets.choice(self.encryptedTerms[kind].validCharacters) for _ in range(self.encryptedTerms[kind].length))
