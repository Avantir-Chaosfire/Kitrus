import os, shutil

from KitrusRoot_VirtualDirectory import *
from KitrusRoot_VirtualFile import *
from KitrusRoot_ParameterModule import *

class Module:
    def __init__(self, name, kind, destination):
        self.name = name
        self.kind = kind
        self.destination = destination

        #Generate virtual files
        self.rootDirectory = VirtualDirectory(self.name, '.')

        #Delete everything at self.destination
        try:
            shutil.rmtree(self.destination)
        except FileNotFoundError:
            pass

    def export(self):
        (parentDirectory, directoryName) = os.path.split(self.destination)
        self.rootDirectory.name = directoryName
        self.rootDirectory.write(parentDirectory)

    def getAsParameter(self):
        return ParameterModule(self.name, self.kind, self.rootDirectory)
