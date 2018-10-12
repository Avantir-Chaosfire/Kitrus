class StringParsingException(Exception):
    def __init__(self, setName, lineNumber, message):
        super().__init__('[' + setName + ':' + str(lineNumber) + ']: ' + message)
