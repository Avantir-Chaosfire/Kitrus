import math

class StringExpressionCalculator:
    def __init__(self, stringLibrary):
        self.BINARY_OPERATORS = {
            '+': lambda x, y: x + y,
            '-': lambda x, y: x - y,
            '*': lambda x, y: x * y,
            '/': lambda x, y: x / y,
            '**': lambda x, y: x ** y,
            '@log': lambda x, y: math.log(x, y),
            '%': lambda x, y: x % y,
            '&': lambda x, y: x & y,
            '|': lambda x, y: x | y,
            '^': lambda x, y: x ^ y,
            '<<': lambda x, y: x << y,
            '>>': lambda x, y: x >> y,
            '<': lambda x, y: int(x < y),
            '>': lambda x, y: int(x > y),
            '<=': lambda x, y: int(x <= y),
            '>=': lambda x, y: int(x >= y),
            '==': lambda x, y: int(x == y )
        }
        self.UNARY_OPERATORS = {
            '~': lambda x: int(not x),
            '@abs': lambda x: abs(x),
            '@floor': lambda x: math.floor(x),
            '@ceiling': lambda x: math.ceil(x),
            '@sqrt': lambda x: math.sqrt(x),
        }

        self.stringLibrary = stringLibrary

    def formatResult(self, result):
        return '{0:g}'.format(result)

    def parseStringOperator(self, path, stringSetName, operator, kind, errorFunction, lineNumber):
        try:
            return float(operator)
        except ValueError:
            value = self.stringLibrary.evaluateStringKey(operator, kind, path, stringSetName, errorFunction, lineNumber)
            try:
                return float(value)
            except ValueError:
                errorFunction(lineNumber, '"' + operator + '" does not evaluate to a number.')
                return None

    def evaluate(self, key, kind, path, stringSetName, errorFunction, lineNumber):
        operators = key[1:].split(' ')

        variableStack = []

        for operator in operators:
            if operator in self.BINARY_OPERATORS:
                if len(variableStack) < 2:
                    errorFunction(lineNumber, 'Not enough values to operate "' + operator + '" upon.')
                else:
                    argument1String = variableStack.pop()
                    argument2String = variableStack.pop()

                    argument1 = self.parseStringOperator(path, stringSetName, argument1String, kind, errorFunction, lineNumber)
                    argument2 = self.parseStringOperator(path, stringSetName, argument2String, kind, errorFunction, lineNumber)

                    if None not in [argument1, argument2]:
                        variableStack.append(self.BINARY_OPERATORS[operator](argument2, argument1))
            elif operator in self.UNARY_OPERATORS:
                if len(variableStack) < 1:
                    errorFunction(lineNumber, 'Not enough values to operate "' + operator + '" upon.')
                else:
                    argumentString = variableStack.pop()
                    argument = self.parseStringOperator(path, stringSetName, argument1String, kind, errorFunction, lineNumber)

                    if None not in [argument]:
                        variableStack.append(self.UNARY_OPERATORS[operator](argument))
            elif operator == '=':
                if len(variableStack) < 2:
                    errorFunction(lineNumber, 'Not enough values to operate "' + operator + '" upon.')
                else:
                    stringValueString = variableStack.pop()
                    stringValue = self.parseStringOperator(path, stringSetName, stringValueString, kind, errorFunction, lineNumber)
                    stringKeyName = variableStack.pop()
                    if not stringValue == None:
                        self.stringLibrary.setValue(stringKeyName, kind, self.formatResult(stringValue))
                    variableStack.append(stringValue)
            else:
                variableStack.append(operator)
        if len(variableStack) == 1:
            stringValue = self.parseStringOperator(path, stringSetName, variableStack[0], kind, errorFunction, lineNumber)
            if not stringValue == None:
                return self.formatResult(stringValue)
            else:
                errorFunction(lineNumber, 'Unknown string key "' + variableStack[0] + '"')
        elif not variableStack:
            errorFunction(lineNumber, 'No expression result.')
        else:
            errorFunction(lineNumber, 'Too many expression results.')
        return None
