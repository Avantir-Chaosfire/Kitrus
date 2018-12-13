import os, codecs

from KitrusRoot_DuplicateFileException import *

class VirtualFile:
    def __init__(self, name, directory = None):
        self.name = name
        if directory == None:
            self.contents = ''
        else:
            with codecs.open(os.path.join(directory, self.name), encoding = 'utf-8') as file:
                self.contents = file.read()

    def write(self, directory):
        filepath = os.path.join(directory, self.name)
        
        if not os.path.isfile(filepath):
            with codecs.open(filepath, encoding = 'utf-8', mode = 'w') as file:
                file.write(self.contents)
        else:
            raise DuplicateFileException('A transformation duplicated a file. Unable to complete export.')
