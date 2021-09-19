import random

class PredefinedStringLibrary:
    def __init__(self):
        self.MINECRAFT_FUNCTION_DIRECTORY_SEPARATOR = '/'

        self.RNG = random.Random()
        
        self.predefinitions = {}
        self.predefinitions['UUID'] = lambda path: self.getUUID(path)
        self.predefinitions['Newline'] = lambda path: '\n'
        self.predefinitions['~'] = lambda path: self.getMinecraftFunctionPath(path)

    def getValue(self, name, path):
        if name in self.predefinitions:
            return self.predefinitions[name](path)
        return None

    def getUUIDComponent(self):
        return str(self.RNG.randint(-2147483648, 2147483647))

    def getUUID(self, path):
        return 'UUID:[I;' + self.getUUIDComponent() + ',' + self.getUUIDComponent() + ',' + self.getUUIDComponent() + ',' + self.getUUIDComponent() + ']'

    def getMinecraftFunctionPath(self, path):
        return self.MINECRAFT_FUNCTION_DIRECTORY_SEPARATOR.join(path)

    def seed(self, path):
        self.RNG.seed(path)
