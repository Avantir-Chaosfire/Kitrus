import re

from Encrypters.Utilities.Match import *

class Template:
    def __init__(self, advanceRegularExpression, targetRegularExpression):
        self.advanceRegularExpression = advanceRegularExpression
        self.targetRegularExpression = targetRegularExpression

    def match(self, command):
        match = re.search(self.advanceRegularExpression, command)
        if not match == None and len(command) > match.end() + 1 and command[match.end() + 1] == ' ':
            termOffset = match.end() + 1
            termMatch = re.search(self.targetRegularExpression, command[termOffset:])
            if not termMatch == None:
                return Match(termMatch.start() + termOffset, termMatch.end() + termOffset)
            return None
        return None
