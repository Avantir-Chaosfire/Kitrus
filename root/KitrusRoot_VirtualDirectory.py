import os

from KitrusRoot_VirtualFile import *

class VirtualDirectory:
    def __init__(self, name, parentDirectory = ''):
        self.name = name
        self.fileChildren = []
        self.directoryChildren = []

        if not parentDirectory == '':
            directory = os.path.join(parentDirectory, self.name)

            for fileName in os.listdir(directory):
                if not fileName.startswith('.'):
                    if os.path.isdir(os.path.join(directory, fileName)):
                        self.directoryChildren.append(VirtualDirectory(fileName, directory))
                    else:
                        self.fileChildren.append(VirtualFile(fileName, directory))

    def write(self, parentDirectory):
        directory = os.path.join(parentDirectory, self.name)
        os.makedirs(directory)

        for virtualFile in self.fileChildren:
            virtualFile.write(directory)
        for virtualDirectory in self.directoryChildren:
            virtualDirectory.write(directory)
