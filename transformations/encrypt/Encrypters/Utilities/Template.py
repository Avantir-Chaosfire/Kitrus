import re

from Encrypters.Utilities.Match import *

class Template:
    def __init__(self, advanceRegularExpressions, targetRegularExpression, encrypter):
        self.advanceRegularExpressions = advanceRegularExpressions
        self.targetRegularExpression = targetRegularExpression
        self.encrypter = encrypter

    def match(self, command):
        endOfLastMatch = 0
        matches = []
        match = not None
        while not match == None:
            match = re.search(self.advanceRegularExpressions[0], command[endOfLastMatch:])
            if not match == None:
                startOfSearchIndex = match.end() + endOfLastMatch
                for advanceRegularExpression in self.advanceRegularExpressions[1:]:
                    (unusedSelectorData, endOfSelector) = self.encrypter.getFlatImproperJSONKeyValuePairs(command[startOfSearchIndex - 1:], '[', ']', '=')
                    if not endOfSelector == None:
                        startOfSearchIndex += endOfSelector
                    match = re.match(advanceRegularExpression, command[startOfSearchIndex:])
                    if match == None:
                        break
                    startOfSearchIndex += match.end()

                if not match == None:
                    match = re.match(self.targetRegularExpression, command[startOfSearchIndex:])
                    if not match == None:
                        matches.append(Match(match.start() + startOfSearchIndex, match.end() + startOfSearchIndex))
                        endOfLastMatch = match.end() + startOfSearchIndex
        return matches
