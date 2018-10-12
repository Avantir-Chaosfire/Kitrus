import os, shutil

from KitrusRoot_VirtualDirectory import *
from KitrusRoot_VirtualFile import *
from KitrusRoot_Output import *

class Module:
    def __init__(self, name, kind, destination, transformationNames):
        self.name = name
        self.kind = kind
        self.destination = destination
        self.transformationNames = transformationNames

        #Generate virtual files
        self.rootDirectory = VirtualDirectory('.', self.name)

        #Delete everything at self.destination
        try:
            shutil.rmtree(self.destination)
        except FileNotFoundError:
            pass
            
    def transform(self, transformation):
        transformation.apply(self.rootDirectory, self.kind)

    def export(self):
        (parentDirectory, directoryName) = os.path.split(self.destination)
        self.rootDirectory.name = directoryName
        self.rootDirectory.write(parentDirectory)
