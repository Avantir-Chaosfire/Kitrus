import re, json, secrets

from Encrypters.Utilities.Template import *
from Encrypters.Utilities.EncryptedTerms import *

class BaseEncrypter:
    def __init__(self, namespaces, encryptedTerms, encryptCommand):
        self.encryptedTerms = encryptedTerms
        self.encryptCommand = encryptCommand
        self.fileEncryptedNamespaces = namespaces

        self.numericalRegularExpression = '-?[0123456789]+(\.[0123456789]+)?'
        self.coordinateRegularExpression = '(([~^]' + self.numericalRegularExpression + ')|(' + self.numericalRegularExpression + ')|([~^]))'
        self.improperJSONObjectRegularExpression = '{([^ ]+:.+)*}'

        self.generalRegularExpressions = {
            'function': '(' + '|'.join(namespaces) + '):([' + re.escape(encryptedTerms['function'].validCharacters) + '/]+)',
            'tag': '([' + re.escape(encryptedTerms['tag'].validCharacters) + ']+)',
            'objective': '([' + re.escape(encryptedTerms['objective'].validCharacters) + ']+)',
            'selector': '@[aeprs]\[?',
            'numerical': self.numericalRegularExpression,
            'vector': self.coordinateRegularExpression + ' ' + self.coordinateRegularExpression + ' ' + self.coordinateRegularExpression,
            'improperJSONObject': self.improperJSONObjectRegularExpression,
            'properJSONObject': '{("[^ ]+":.+)*}',
            'item': '[^ ]+' + self.improperJSONObjectRegularExpression
        }

        self.encryptTextFollowingMatch = False
        self.usageCount = 0

    def createTemplates(self, advanceRegularExpressions, targetRegularExpression):
        self.templates = []

        for regularExpression in advanceRegularExpressions:
            regularExpression[-1] += ' '
            self.templates.append(Template(regularExpression, targetRegularExpression, self))

    def encrypt(self, command):
        commandName = command.split(' ')[0]
        if commandName in self.commands:
            for template in self.templates:
                matches = template.match(command)
                matches.sort(key = lambda m: m.end, reverse = True)
                for match in matches:
                    commandBeforeMatch = command[:match.start]
                    if self.encryptTextFollowingMatch:
                        command = commandBeforeMatch + self.encryptTerm(command[match.start:])
                    else:
                        commandAfterMatch = command[match.end:]
                        matchedTerm = command[match.start:match.end]
                        command = commandBeforeMatch + self.encryptTerm(matchedTerm) + commandAfterMatch
        return command

    def encryptTerm(self, term):
        raise NotImplementedError()

    def encryptSelector(self, selector):
        if '[' in selector and ']' in selector:
            indexOfOpeningBracket = selector.index('[')
            (data, indexOfEndingBracket) = self.getFlatImproperJSONKeyValuePairs(selector[len('@x'):], '[', ']', '=')
            if indexOfEndingBracket == None:
                return selector
            
            if 'tag' in data:
                data['tag'] = list(map(self.encryptSelectorTag, data['tag']))
            if 'scores' in data:
                data['scores'] = list(map(self.encryptObjectivesList, data['scores']))
            if 'nbt' in data:
                data['nbt'] = [self.encryptImproperJSONSelector(nbt) for nbt in data['nbt'] if self.isImproperJSON(nbt)]

            return selector[:indexOfOpeningBracket] + self.encloseAsList(list(map(self.assembleRawKeyValuePairList, data.items()))) + selector[indexOfEndingBracket + 1 + len('@x'):]
        return selector

    def encryptImproperJSONSelector(self, improperJSON):
        if improperJSON.startswith('!'):
            return '!' + self.encryptImproperJSON(improperJSON[1:])
        return self.encryptImproperJSON(improperJSON)

    def encryptImproperJSON(self, improperJSON):
        (data, indexOfEndingBracket) = self.getFlatImproperJSONKeyValuePairs(improperJSON, '{', '}', ':')
        if not indexOfEndingBracket == len(improperJSON) - 1:
            raise Exception('Case not handled - there was text after the end of the improper JSON: ' + improperJSON)
        
        if 'Tags' in data:
            encryptedTags = []
            for tags in data['Tags']:
                if tags.startswith('[') and tags.endswith(']'):
                    encryptedTags += map(self.encryptQuotedTag, tags[1:-1].split(','))
            data['Tags'] = [self.encloseAsList(encryptedTags)]
        if 'Passengers' in data:
            encryptedPassengers = []
            for passengers in data['Passengers']:
                if passengers.startswith('[') and passengers.endswith(']'):
                    encryptedPassengers.append(self.encryptImproperJSON(passengers[1:-1]))
            data['Passengers'] = [self.encloseAsList(encryptedPassengers)]
            
        return self.encloseAsObject([key + ':' + value[0] for key, value in data.items()])

    def encryptProperJSON(self, properJSON):
        data = json.loads(properJSON)
        data = self.encryptFlatJSONText(data)

        if 'extra' in data:
            data['extra'] = list(map(self.encryptFlatJSONText, data['extra']))

        return json.dumps(data)

    def encryptItem(self, item):
        startOfImproperJSON = item.index('{')
        if startOfImproperJSON > 0 and item.endswith('}'):
            item = item[:startOfImproperJSON] + self.encryptImproperJSON(item[startOfImproperJSON:])
        return item

    def encryptFlatJSONText(self, flatJSONText):
        x = False
        if 'selector' in flatJSONText:
            flatJSONText['selector'] = self.encryptSelector(flatJSONText['selector'])

        if 'score' in flatJSONText:
            if 'name' in flatJSONText['score'] and flatJSONText['score']['name'].startswith('@'):
                flatJSONText['score']['name'] = self.encryptSelector(flatJSONText['score']['name'])
                
            if 'objective' in flatJSONText['score']:
                flatJSONText['score']['objective'] = self.encryptBaseTerm(flatJSONText['score']['objective'], 'objective')

        if 'clickEvent' in flatJSONText and 'value' in flatJSONText['clickEvent']:
            command = flatJSONText['clickEvent']['value']
            if command.startswith('/'):
                x = True
                command = command[1:]
                flatJSONText['clickEvent']['value'] = '/' + self.encryptCommand(command)

        return flatJSONText

    def getFlatImproperJSONKeyValuePairs(self, sequence, openingBrace, closingBrace, assignmentOperator):
        result = {}
        indexOfEndingBrace = None
        if sequence.startswith(openingBrace):
            sequence = sequence
            state = 'key'
            key = ''
            value = ''
            escapeLevel = 0
            currentIndex = 1
            while True:
                if currentIndex == 1 and sequence[currentIndex] == closingBrace:
                    indexOfEndingBrace = currentIndex
                    break
                if state == 'key':
                    if sequence[currentIndex] == assignmentOperator:
                        state = 'value'
                    else:
                        key += sequence[currentIndex]
                elif state == 'value':
                    if sequence[currentIndex] in '{[':
                        escapeLevel += 1
                        value += sequence[currentIndex]
                    elif sequence[currentIndex] in '}]' and escapeLevel > 0:
                        escapeLevel -= 1
                        value += sequence[currentIndex]
                    elif escapeLevel > 0:
                        value += sequence[currentIndex]
                    elif sequence[currentIndex] == ',':
                        if key not in result:
                            result[key] = []
                        result[key].append(value)
                        state = 'key'
                        key = ''
                        value = ''
                    elif sequence[currentIndex] == closingBrace:
                        if key not in result:
                            result[key] = []
                        result[key].append(value)
                        indexOfEndingBrace = currentIndex
                        break
                    else:
                        value += sequence[currentIndex]
                currentIndex += 1
        return (result, indexOfEndingBrace)

    def encryptQuotedTag(self, tag):
        return '"' + self.encryptBaseTerm(tag[1:-1], 'tag') + '"' if tag.startswith('"') and tag.endswith('"') else tag

    def assembleRawKeyValuePairList(self, keyValuesPair):
        (key, values) = keyValuesPair
        return ','.join([key + '=' + value for value in values])

    def encryptObjectivesList(self, objectives):
        (data, indexOfEndingBracket) = self.getFlatImproperJSONKeyValuePairs(objectives, '{', '}', '=')
        if not indexOfEndingBracket == len(objectives) - 1:
            raise Exception('Case not handled - there was text after the end of the improper JSON')
        listOfListOfScoreComparisons = list(map(self.assembleObjectiveKeyValuePair, data.items()))
        flatList = [item for sublist in listOfListOfScoreComparisons for item in sublist]
        return self.encloseAsObject(flatList)

    def assembleObjectiveKeyValuePair(self, keyValuesPair):
        (key, values) = keyValuesPair
        return list(map(lambda value: self.encryptBaseTerm(key, 'objective') + '=' + value, values))

    def isImproperJSON(self, term):
        return not re.match('(!)?' + self.generalRegularExpressions['improperJSONObject'] + '$', term) == None

    def encryptSelectorTag(self, tag):
        if tag.startswith('!'):
            return '!' + self.encryptBaseTerm(tag[len('!'):], 'tag')
        else:
            return self.encryptBaseTerm(tag, 'tag')

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
