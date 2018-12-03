import sys

class Transformation:
    initialized = False
    
    def __init__(self):
        self.transformationDataDirectory = None

    def outputMessage(self, message):
        if Transformation.initialized:
            sys.stdout.write('\t' + message + '\n')
        else:
            sys.stdout.write('\t\t' + message + '\n')

    def outputWarnings(self, warning):
        if initialized:
            sys.stdout.write('\tWARNING: ' + warning + '\n')
        else:
            sys.stdout.write('\t\tWARNING: ' + warning + '\n')

    def apply(self, modules):
        pass
