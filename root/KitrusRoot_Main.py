#!python3

import sys, os, imp

from KitrusRoot_Transformation import *
from KitrusRoot_Module import *

from KitrusRoot_ParsingException import *
from KitrusRoot_UnknownTransformationException import *

CONFIGURATION_FILE_NAME = 'Kitrusfile'
COMMON_PATH_MODE_NAME = 'configuration'
MODULE_DEFINITION_MODE_NAME = 'modules'
MODE_SET_METACHARACTER = '#'
COMMON_PATH_METACHARACTER = '#'
TRANSFORMATION_MAIN_MODULE_NAME = 'Main'
TRANSFORMATIONS_DIRECTORY = os.path.join('..', 'transformations')

def parseConfigurationLine(line, lineNumber):
    parts = line.split('=')
    if len(parts) < 2:
        raise ParsingException('[' + CONFIGURATION_FILE_NAME + ':' + str(lineNumber) + ']: Expected "=" in configuration line')
    elif len(parts) > 2:
        raise ParsingException('[' + CONFIGURATION_FILE_NAME + ':' + str(lineNumber) + ']: Too many "=" in configuration line')
    
    return parts[0], parts[1]

def parseModuleLine(line, lineNumber, configuration):
    for key in configuration.keys():
        line = line.replace(COMMON_PATH_METACHARACTER + key + COMMON_PATH_METACHARACTER, configuration[key])

    args = line.split(' : ')
    if len(args) not in [3, 4]:
        raise ParsingException('[' + CONFIGURATION_FILE_NAME + ':' + str(lineNumber) + ']: ' + str(len(args)) + ' arguments found in module line, expected 3 or 4')

    moduleName = args[0]
    sys.stdout.write('\t' + moduleName + '...\n')
    sys.stdout.flush()
    
    transformationNames = []
    
    if len(args) == 4:
        transformationNames = args[3].split(',')

    return Module(moduleName, args[1], args[2], transformationNames)

def getModules():
    lines = []
    with open(CONFIGURATION_FILE_NAME, 'r') as kitrusFile:
        lines = kitrusFile.readlines()

    mode = ''
    lineNumber = 1
    configuration = {}
    modules = []

    for line in lines:
        line = line.rstrip('\n')
        if line == MODE_SET_METACHARACTER + COMMON_PATH_MODE_NAME:
            mode = COMMON_PATH_MODE_NAME
        elif line == MODE_SET_METACHARACTER + MODULE_DEFINITION_MODE_NAME:
            mode = MODULE_DEFINITION_MODE_NAME
        else:
            if mode == '':
                raise ParsingException('[' + CONFIGURATION_FILE_NAME + ':' + str(lineNumber) + ']: Must defined a mode (Either ' + MODE_SET_METACHARACTER + COMMON_PATH_MODE_NAME + ' or ' + MODE_SET_METACHARACTER + MODULE_DEFINITION_MODE_NAME + ').')
            elif mode == COMMON_PATH_MODE_NAME:
                if not line == '':
                    key, value = parseConfigurationLine(line, lineNumber)
                    configuration[key] = value
            elif mode == MODULE_DEFINITION_MODE_NAME:
                modules.append(parseModuleLine(line, lineNumber, configuration))
            else:
                raise ParsingException('[' + CONFIGURATION_FILE_NAME + ':' + str(lineNumber) + ']: Unknown mode (Use either ' + MODE_SET_METACHARACTER + COMMON_PATH_MODE_NAME + ' or ' + MODE_SET_METACHARACTER + MODULE_DEFINITION_MODE_NAME + ').')
        lineNumber += 1

    return modules

def getTransformations(requestedTransformationNames, installationDirectoryRoot):
    transformations = {}

    transformationsDirectory = os.path.join(installationDirectoryRoot, TRANSFORMATIONS_DIRECTORY)
    for transformationName in requestedTransformationNames.keys():
        if os.path.isdir(os.path.join(transformationsDirectory, transformationName)):
            sys.stdout.write('\t' + transformationName + '...\n')
            sys.stdout.flush()

            sys.path.append(os.path.join(transformationsDirectory, transformationName))
            mainTransformationPythonModule = imp.load_source(TRANSFORMATION_MAIN_MODULE_NAME, os.path.join(transformationsDirectory, transformationName, TRANSFORMATION_MAIN_MODULE_NAME + '.py'))
            sys.path.remove(os.path.join(transformationsDirectory, transformationName))
            transformations[transformationName] = mainTransformationPythonModule.Main()

            writeOutput(transformations[transformationName])
        else:
            raise UnknownTransformationException('[' + CONFIGURATION_FILE_NAME + ':' + str(requestedTransformationNames[transformationName]) + ']: Unknown transformation: ' + transformationName)

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

        sys.stdout.write('\tWriting...\n')
        sys.stdout.flush()
        module.export()

if __name__ == '__main__':
    if len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        print('Error: Kitrus takes exactly one argument: The project directory.')
