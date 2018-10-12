class StringSet:
    def __init__(self, name):
        self.name = name
        self.dependencies = []
        self.kinds = ['']
        self.joins = {}
        self.strings = {}
