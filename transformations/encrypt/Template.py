import re

def Template:
    def __init__(self, advanceRegularExpression, targetRegularExpression):
        self.advanceRegularExpression = advanceRegularExpression
        self.targetRegularExpression = targetRegularExpression

    def match(self, command):
        match = re.search(self.advanceRegularExpression, command)
        if not match == None and len(command) > match.end() + 1 and command[match.end() + 1] == ' ':
            return re.search(self.targetRegularExpression, command, match.end() + 1)
        return None
