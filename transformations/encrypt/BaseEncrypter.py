from Template import *

def BaseEncrypter:
    def __init__(self):
        self.validCharacters = ''
        self.commands = []
        self.templates = []

    def createTemplates(self, advanceRegularExpressions, targetRegularExpression)
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

    def encryptTerm(self):
        raise NotImplementedError()
