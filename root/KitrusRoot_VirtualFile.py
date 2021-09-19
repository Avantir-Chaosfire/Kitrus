import os, codecs

from KitrusRoot_DuplicateFileException import *

class VirtualFile:
    DOS_LINE_ENDINGS = '\r\n'
    UNIX_LINE_ENDINGS = '\n'
    def __init__(self, name, directory = None):
        self.name = name
        if directory == None:
            self.contents = ''
            self.path = self.name
        else:
            self.path = os.path.join(directory, self.name)
            try:
                with codecs.open(self.path, encoding = 'utf-8') as file:
                    self.contents = file.read()
            except UnicodeDecodeError as e:
                e.reason += ', in file ' + self.name
                raise e

    def write(self, directory):
        filePath = os.path.join(directory, self.name)
        
        if not os.path.isfile(filePath):
            with codecs.open(filePath, encoding = 'utf-8', mode = 'w') as file:
                file.write(self.contents)
        else:
            raise DuplicateFileException('A transformation duplicated a file "' + filePath + '". Unable to complete export.')

    def getLineEndings(self):
        return VirtualFile.DOS_LINE_ENDINGS if VirtualFile.DOS_LINE_ENDINGS in self.contents else VirtualFile.UNIX_LINE_ENDINGS

    def getContentsLines(self):
        return self.contents.split(self.getLineEndings())

    def setContentsLines(self, lines):
        self.contents = self.getLineEndings().join(lines)
