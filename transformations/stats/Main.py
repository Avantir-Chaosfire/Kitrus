from KitrusRoot_Transformation import *

class Main(Transformation):
    def __init__(self, configurationDirectory, transformationDataDirectory, saveData):
        self.fileTypeCounts = {}
        self.totalCommandCount = 0

    def apply(self, modules):
        for module in modules:
            self.outputMessage(module.name + ':')
            self.fileTypeCounts = {}
            self.totalCommandCount = 0
                
            rootDirectory = self.countDirectory(module.rootDirectory)

            self.outputMessage('\tFile Types:')

            for fileExtension, fileCount in self.fileTypeCounts.items():
                self.outputMessage('\t\t' + fileExtension + ': ' + str(fileCount))

            if self.totalCommandCount > 0:
                self.outputMessage('\tCommands: ' + str(self.totalCommandCount))

    def countDirectory(self, directory):
        for virtualFile in directory.fileChildren:
            self.countFile(virtualFile)

        for virtualDirectory in directory.directoryChildren:
            self.countDirectory(virtualDirectory)
            
    def countFile(self, virtualFile):
        fileNameComponents = virtualFile.name.split('.', 1)
        fileExtension = fileNameComponents[1] if len(fileNameComponents) > 1 else 'no extension'

        if fileExtension == 'mcfunction':
            commandCount = 0
            lines = virtualFile.getContentsLines()

            for line in lines:
                if not line == '' and not line[0] == '#' and not line.isspace():
                    commandCount += 1
            self.totalCommandCount += commandCount

        if fileExtension in self.fileTypeCounts:
            self.fileTypeCounts[fileExtension] += 1
        else:
            self.fileTypeCounts[fileExtension] = 1
