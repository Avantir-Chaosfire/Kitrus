class BinaryExpressionOperation:
    def __init__(self, operation, argument1, argument2):
        self.operation = operation
        self.argument1 = argument1
        self.argument2 = argument2

    def getValue(self, kind, path, stringSetName, errorFunction, lineNumber):
        value1 = self.argument1.getValue(kind, path, stringSetName, errorFunction, lineNumber)
        value2 = self.argument2.getValue(kind, path, stringSetName, errorFunction, lineNumber)
        if None not in [value1, value2]:
            return self.operation(value1, value2)
        else:
            return None

class UnaryExpressionOperation:
    def __init__(self, operation, argument):
        self.operation = operation
        self.argument = argument

    def getValue(self, kind, path, stringSetName, errorFunction, lineNumber):
        value = self.argument.getValue(kind, path, stringSetName, errorFunction, lineNumber)
        if not value == None:
            return self.operation(value)
        else:
            return None

class AssignmentOperation:
    def __init__(self, key, argument, stringLibrary, formatResult):
        self.key = key
        self.argument = argument
        self.stringLibrary = stringLibrary
        self.formatResult = formatResult

    def getValue(self, kind, path, stringSetName, errorFunction, lineNumber):
        value = self.argument.getValue(kind, path, stringSetName, errorFunction, lineNumber)
        if not value == None:
            self.stringLibrary.setValue(self.key, kind, self.formatResult(value))
        return value

class NumericalExpressionArgument:
    def __init__(self, name, argument):
        self.argument = argument
        
    def getValue(self, kind, path, stringSetName, errorFunction, lineNumber):
        return self.argument

class StringKeyExpressionArgument:
    def __init__(self, argument, stringLibrary):
        self.name = argument
        self.argument = argument
        self.stringLibrary = stringLibrary

    def getValue(self, kind, path, stringSetName, errorFunction, lineNumber):
        value = self.stringLibrary.evaluateStringKey(self.argument, kind, path, stringSetName, errorFunction, lineNumber)
        try:
            return float(value)
        except ValueError:
            errorFunction(lineNumber, '"' + self.argument + '" does not evaluate to a number.')
            return None
