import math

from ExpressionTree import *

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
        self.cachedExpressions = {}

    def formatResult(self, result):
        return '{0:g}'.format(result)

    def getFormattedValue(self, expression, kind, path, stringSetName, errorFunction, lineNumber):
        result = expression.getValue(kind, path, stringSetName, errorFunction, lineNumber)
        if not result == None:
            return self.formatResult(result)
        errorFunction(lineNumber, 'Cannot evaluate string expression "' + key + '"')
        return '[CANNOT EVALUATE STRING EXPRESSION]'

    def evaluate(self, key, kind, path, stringSetName, errorFunction, lineNumber):
        if key in self.cachedExpressions:
            return self.getFormattedValue(self.cachedExpressions[key], kind, path, stringSetName, errorFunction, lineNumber)
        
        operators = key[1:].split(' ')

        expressionTreeStack = []

        for operator in operators:
            if operator in self.BINARY_OPERATORS:
                if len(expressionTreeStack) < 2:
                    errorFunction(lineNumber, 'Not enough values to operate "' + operator + '" upon.')
                else:
                    argument2 = expressionTreeStack.pop()
                    argument1 = expressionTreeStack.pop()

                    expressionTreeStack.append(BinaryExpressionOperation(self.BINARY_OPERATORS[operator], argument1, argument2))
            elif operator in self.UNARY_OPERATORS:
                if len(expressionTreeStack) < 1:
                    errorFunction(lineNumber, 'Not enough values to operate "' + operator + '" upon.')
                else:
                    argument = expressionTreeStack.pop()

                    expressionTreeStack.append(UnaryExpressionOperation(self.UNARY_OPERATORS[operator], argument))
            elif operator == '=':
                if len(expressionTreeStack) < 2:
                    errorFunction(lineNumber, 'Not enough values to operate "' + operator + '" upon.')
                else:
                    argument = expressionTreeStack.pop()
                    key = expressionTreeStack.pop()

                    expressionTreeStack.append(AssignmentOperation(key.name, argument, self.stringLibrary, self.formatResult))
            else:
                argument = None
                try:
                    value = float(operator)
                    argument = NumericalExpressionArgument(operator, value)
                except ValueError:
                    argument = StringKeyExpressionArgument(operator, self.stringLibrary)
                expressionTreeStack.append(argument)
                
        if len(expressionTreeStack) == 1:
            expression = expressionTreeStack[0]
            self.cachedExpressions[key] = expression
            return self.getFormattedValue(expression, kind, path, stringSetName, errorFunction, lineNumber)
        elif not variableStack:
            errorFunction(lineNumber, 'No expression result.')
        else:
            errorFunction(lineNumber, 'Too many expression results.')
        return None
