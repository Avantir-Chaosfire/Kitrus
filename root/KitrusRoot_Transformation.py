import sys

class Transformation:
    initialized = False

    def outputMessage(self, message):
        if Transformation.initialized:
            sys.stdout.write('\t' + message + '\n')
        else:
            sys.stdout.write('\t\t' + message + '\n')

    def outputWarning(self, warning):
        if Transformation.initialized:
            sys.stdout.write('\tWARNING: ' + warning + '\n')
        else:
            sys.stdout.write('\t\tWARNING: ' + warning + '\n')

    def apply(self, modules):
        pass
