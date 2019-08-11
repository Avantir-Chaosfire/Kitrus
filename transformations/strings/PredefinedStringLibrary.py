import random

class PredefinedStringLibrary:
    def __init__(self):
        self.MINECRAFT_FUNCTION_DIRECTORY_SEPARATOR = '/'
        
        self.predefinitions = {}
        self.predefinitions['UUID'] = lambda path: str(random.randint(-2147483648, 2147483647))
        self.predefinitions['Newline'] = lambda path: '\n'
        self.predefinitions['~'] = lambda path: self.MINECRAFT_FUNCTION_DIRECTORY_SEPARATOR.join(path)

    def getValue(self, name, path):
        if name in self.predefinitions:
            return self.predefinitions[name](path)
        return None
