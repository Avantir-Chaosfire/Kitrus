from Template import *

def BaseEncrypter:
    def __init__(self, encryptedTerms, advanceRegularExpressions, targetRegularExpression):
        self.templates = []
        self.encryptedTerms = encryptedTerms

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

    def encryptBaseTerm(self, term, kind):
        if term not in self.encryptedTerms[kind].values:
            self.encryptedTerms[kind].values[term] = self.generateUniqueName(kind)
        return self.encryptedTerms[kind].values[term]

    def generateUniqueName(self, kind):
        return ''.join(secrets.choice(self.validCharacters[kind]) for _ in range(self.encryptedTermLengths[kind])) #Possible to gunarantee these will be unique? or at least figure out the chance of a duplicate?
