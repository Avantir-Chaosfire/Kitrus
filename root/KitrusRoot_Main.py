#!python3

import sys, os, imp

from KitrusRoot_Transformation import *
from KitrusRoot_Module import *

from KitrusRoot_ParsingException import *
from KitrusRoot_UnknownTransformationException import *

def parseConfigurationLine(line, lineNumber):
    parts = line.split('=')
    if len(parts) < 2:
        raise ParsingException('[Kitrusfile:' + str(lineNumber) + ']: Expected "=" in configuration line')
    elif len(parts) > 2:
        raise ParsingException('[Kitrusfile:' + str(lineNumber) + ']: Too many "=" in configuration line')
    
    return parts[0], parts[1]

def parseModuleLine(line, lineNumber, configuration):
    for key in configuration.keys():
        line = line.replace('#' + key + '#', configuration[key])

    args = line.split(' : ')
    if len(args) not in [3, 4]:
        raise ParsingException('[Kitrusfile:' + str(lineNumber) + ']: ' + str(len(args)) + ' arguments found in module line, expected 3 or 4')

    moduleName = args[0]
    sys.stdout.write('\t' + moduleName + '...\n')
    sys.stdout.flush()
    
    transformationNames = []
    
    if len(args) == 4:
        transformationNames = args[3].split(',')

    return Module(moduleName, args[1], args[2], transformationNames)

def getModules():
    lines = []
    with open(os.path.join('Kitrusfile'), 'r') as modulesFile:
        lines = modulesFile.readlines()

    mode = ''
    lineNumber = 1
    configuration = {}
    modules = []

    for line in lines:
        line = line.rstrip('\n')
        if line == '#configuration':
            mode = 'configuration'
        elif line == '#modules':
            mode = 'modules'
        else:
            if mode == '':
                raise ParsingException('[Kitrusfile:' + str(lineNumber) + ']: Must defined a mode (Either #configuration or #modules).')
            elif mode == 'configuration':
                if not line == '':
                    key, value = parseConfigurationLine(line, lineNumber)
                    configuration[key] = value
            elif mode == 'modules':
                modules.append(parseModuleLine(line, lineNumber, configuration))
            else:
                raise ParsingException('[Kitrusfile:' + str(lineNumber) + ']: Unknown mode (Use either #configuration or #modules).')
        lineNumber += 1

    return modules

def getTransformations(requestedTransformationNames, installationDirectoryRoot):
    transformations = {}

    transformationsDirectory = os.path.join(installationDirectoryRoot, '..', 'transformations')
    for transformationName in requestedTransformationNames.keys():
        if os.path.isdir(os.path.join(transformationsDirectory, transformationName)):
            sys.stdout.write('\t' + transformationName + '...\n')
            sys.stdout.flush()

            sys.path.append(os.path.join(transformationsDirectory, transformationName))
            mainTransformationPythonModule = imp.load_source('Main', os.path.join(transformationsDirectory, transformationName, 'Main.py'))
            sys.path.remove(os.path.join(transformationsDirectory, transformationName))
            transformations[transformationName] = mainTransformationPythonModule.Main()

            writeOutput(transformations[transformationName])
        else:
            raise UnknownTransformationException('[modules.mli:' + str(requestedTransformationNames[transformationName]) + ']: Unknown transformation: ' + transformationName)

    return transformations

def writeOutput(transformation):
    for message in transformation.output.messages:
        sys.stdout.write('\t\t' + message + '\n')

    for warning in transformation.output.warnings:
        sys.stdout.write('\t\tWARNING: ' + warning + '\n')
        
    transformation.output = Output()

def main(projectDirectory):
    installationDirectoryRoot = os.getcwd()
    os.chdir(projectDirectory)
    
    sys.stdout.write('Initializing modules...\n')
    modules = getModules()

    sys.stdout.write('Initializing transformations...\n')
    requestedTransformationNames = {}
    lineNumber = 1
    for module in modules:
        for transformationName in module.transformationNames:
            if not transformationName in requestedTransformationNames.keys():
                requestedTransformationNames[transformationName] = lineNumber
        lineNumber += 1
    
    transformations = getTransformations(requestedTransformationNames, installationDirectoryRoot)

    for module in modules:
        sys.stdout.write('Exporting ' + module.name + '...\n')

        for transformationName in module.transformationNames:
            sys.stdout.write('\tApplying ' + transformationName + '...\n')
            sys.stdout.flush()
            module.transform(transformations[transformationName])
            writeOutput(transformations[transformationName])
                    
        sys.stdout.flush()
        module.export()

if __name__ == '__main__':
    if len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        print('Error: Kitrus takes exactly one argument: The project directory.')
