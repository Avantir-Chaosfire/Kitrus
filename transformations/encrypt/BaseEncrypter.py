import re

from Template import *

def BaseEncrypter:
    def __init__(self):
        self.encryptedTerms = {
            'function': EncryptedTerms(string.digits + string.ascii_lowercase + '-_', 40),
            'tag': EncryptedTerms(string.digits + string.ascii_letters + '-_+.', 40),
            'objective': EncryptedTerms(string.digits + string.ascii_letters + '-_+.', 16)
        }
    
        self.numericalRegularExpression = '[0123456789]+(\.[0123456789]+)?'
        self.improperJSONObjectRegularExpression = '{([^ ]+:.+)*}'

        self.generalRegularExpressions = {
            'function': '(' + '|'.join(self.moduleNamespaces.values()) + '):([' + re.escape(encryptedTerms['function'].validCharacters) + ']+)'
            'tag': '([' + re.escape(encryptedTerms['tag'].validCharacters) + ']+)'
            'objective': '([' + re.escape(encryptedTerms['objective'].validCharacters) + ']+)'
            'selector': '@[aeprs](\[(.+=.+)*\])?'
            'numerical': numericalRegularExpression
            'vector': numericalRegularExpression + ' ' + numericalRegularExpression + ' ' + numericalRegularExpression
            'improperJSONObject': improperJSONObjectRegularExpression
            'properJSONObject': '{("[^ ]+":.+)*}'
            'item': '[^ ]+' + improperJSONObjectRegularExpression
        }

    def createTemplates(self, advanceRegularExpressions, targetRegularExpression)
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
                            commandBeforeMatch = command[:match.start()]
                            commandAfterMatch = command[match.end():]
                            matchedTerm = command[match.start():match.end()]
                            command = commandBeforeMatch + self.encryptTerm(matchedTerm) + commandAfterMatch
                newCommands.append(command)

        return '\n'.join(newCommands)

    def encryptTerm(self, term):
        raise NotImplementedError()

    def encryptSelector(self, selector):
        indexOfOpeningBracket = selector.index('[')

        if indexOfOpeningBracket == len('@x') and selector.endswith(']'):
            data = self.getFlatImproperJSONKeyValuePairs(selector[2:], '[', ']', '=')
            if 'tag' in data:
                data['tag'] = map(data['tag'], self.encryptSelectorTag)
            if 'scores' in data:
                data['scores'] = map(data['scores'], self.encryptObjectivesList)
            if 'nbt' in data:
                data['nbt'] = [self.encryptImproperJSON(nbt) for nbt in data['nbt'] if self.isImproperJSON(nbt)]

        return selector[:2] + self.encloseAsList(map(data.items(), self.assembleRawKeyValuePairList))

    def encryptImproperJSON(self, improperJSON):
        data = self.getFlatImproperJSONKeyValuePairs(improperJSON, '{', '}', ':')
        if 'Tags' in data and data['Tags'].startswith('[') and data['Tags'].endswith(']'):
            data['Tags'] = self.encloseAsList(map(data['Tags'][1:-1].split(','), self.encryptQuotedTag))
        reurn self.encloseAsObject([key + ':' + value[0] for key, value in data.items()])

    def encryptProperJSON(self, properJSON):
        data = json.loads(properJSON)

        data = encryptFlatJSONText(data)

        if 'extra' in data:
            map(encryptFlatJSONText, data['extra'])

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
        return '"' + self.encryptBaseTerm(tag[1:-1] 'tag') + '"' if tag.startswith('"') and tag.endswith('"') else tag

    def assembleRawKeyValuePairList(self, key, values):
        return ','.join([key + '=' + value for value in values])

    def encryptObjectivesList(self, objectives):
        return self.encloseAsObject(map(self.getFlatImproperJSONKeyValuePairs(objectives, '{', '}', '=').items(), self.assembleObjectiveKeyValuePair))

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
        if term not in self.encryptedTerms[kind].values:
            self.encryptedTerms[kind].values[term] = self.generateUniqueName(kind)
        return self.encryptedTerms[kind].values[term]

    def generateUniqueName(self, kind):
        return ''.join(secrets.choice(self.validCharacters[kind]) for _ in range(self.encryptedTermLengths[kind]))
