#!python3

import importlib.machinery, importlib.util
import sys, os, copy, ctypes

from KitrusRoot_Transformation import *
from KitrusRoot_Module import *
from KitrusRoot_Step import *

from KitrusRoot_ParsingException import *
from KitrusRoot_UnknownTransformationException import *

CONFIGURATION_FILE_NAME = 'Kitrusfile'
COMMON_PATH_MODE_NAME = 'configuration'
MODULE_DEFINITION_MODE_NAME = 'modules'
PROCEDURE_DEFINITION_MODE_NAME = 'procedure'
MODE_SET_METACHARACTER = '#'
COMMON_PATH_METACHARACTER = '#'
TRANSFORMATION_MAIN_MODULE_NAME = 'Main'
CONFIGURATION_DIRECTORY = 'configuration'
TRANSFORMATION_DATA_DIRECTORY = '.transformation_data'
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
    if not len(args) == 3:
        raise ParsingException('[' + CONFIGURATION_FILE_NAME + ':' + str(lineNumber) + ']: ' + str(len(args)) + ' arguments found in module line, expected 3')

    moduleName = args[0]
    sys.stdout.write('\t' + moduleName + '...\n')
    sys.stdout.flush()

    return Module(moduleName, args[1], args[2])

def parseProcedureLine(line, lineNumber, modules):
    args = line.split(' : ')
    if not len(args) == 2:
        raise ParsingException('[' + CONFIGURATION_FILE_NAME + ':' + str(lineNumber) + ']: ' + str(len(args)) + ' arguments found in procedure line, expected 2')

    allModuleNames = [module.name for module in modules]
    moduleNames = args[1].split(',')
    for moduleName in moduleNames:
        if not moduleName in allModuleNames:
            raise ParsingException('[' + CONFIGURATION_FILE_NAME + ':' + str(lineNumber) + ']: Unknown module name: ' + moduleName)

    return Step(args[0], moduleNames, lineNumber)

def getConfiguration():
    lines = []
    with open(CONFIGURATION_FILE_NAME, 'r') as kitrusFile:
        lines = kitrusFile.readlines()

    mode = ''
    lineNumber = 1
    configuration = {}
    modules = []
    procedure = []

    for line in lines:
        line = line.rstrip('\n')
        if not line == '':
            if line == MODE_SET_METACHARACTER + COMMON_PATH_MODE_NAME:
                mode = COMMON_PATH_MODE_NAME
            elif line == MODE_SET_METACHARACTER + MODULE_DEFINITION_MODE_NAME:
                mode = MODULE_DEFINITION_MODE_NAME
            elif line == MODE_SET_METACHARACTER + PROCEDURE_DEFINITION_MODE_NAME:
                mode = PROCEDURE_DEFINITION_MODE_NAME
            else:
                if mode == '':
                    raise ParsingException('[' + CONFIGURATION_FILE_NAME + ':' + str(lineNumber) + ']: Must defined a mode (Either ' + MODE_SET_METACHARACTER + COMMON_PATH_MODE_NAME + ' or ' + MODE_SET_METACHARACTER + MODULE_DEFINITION_MODE_NAME + ').')
                elif mode == COMMON_PATH_MODE_NAME:
                    if not line == '':
                        key, value = parseConfigurationLine(line, lineNumber)
                        configuration[key] = value
                elif mode == MODULE_DEFINITION_MODE_NAME:
                    modules.append(parseModuleLine(line, lineNumber, configuration))
                elif mode == PROCEDURE_DEFINITION_MODE_NAME:
                    procedure.append(parseProcedureLine(line, lineNumber, modules))
                else:
                    raise ParsingException('[' + CONFIGURATION_FILE_NAME + ':' + str(lineNumber) + ']: Unknown mode (Use either ' + MODE_SET_METACHARACTER + COMMON_PATH_MODE_NAME + ' or ' + MODE_SET_METACHARACTER + MODULE_DEFINITION_MODE_NAME + ').')
        lineNumber += 1

    return modules, procedure

def writeTransformationDataDirectory(transformationName, transformationDataDirectory):
    try:
        shutil.rmtree(os.path.join(TRANSFORMATION_DATA_DIRECTORY, transformationName))
    except FileNotFoundError:
        pass
    
    transformationDataDirectory.name = transformationName
    transformationDataDirectory.write(TRANSFORMATION_DATA_DIRECTORY)

def getTransformationMainModule(transformationsDirectoryPath, transformationName):
    loader = importlib.machinery.SourceFileLoader(TRANSFORMATION_MAIN_MODULE_NAME, os.path.join(transformationsDirectoryPath, transformationName, TRANSFORMATION_MAIN_MODULE_NAME + '.py'))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module

def getTransformations(requestedTransformationNames, installationDirectoryRoot):
    transformations = {}

    if not os.path.isdir(TRANSFORMATION_DATA_DIRECTORY):
        os.mkdir(TRANSFORMATION_DATA_DIRECTORY)
        if os.name == 'nt':
            ctypes.windll.kernel32.SetFileAttributesW(TRANSFORMATION_DATA_DIRECTORY, 2)

    configurationDirectory = VirtualDirectory(CONFIGURATION_DIRECTORY, '.')
    transformationsDirectoryPath = os.path.join(installationDirectoryRoot, TRANSFORMATIONS_DIRECTORY)
    
    for transformationName in requestedTransformationNames.keys():
        if os.path.isdir(os.path.join(transformationsDirectoryPath, transformationName)):
            sys.stdout.write('\t' + transformationName + '...\n')
            sys.stdout.flush()

            transformationDataDirectory = None
            if os.path.isdir(os.path.join(TRANSFORMATION_DATA_DIRECTORY, transformationName)):
                transformationDataDirectory = VirtualDirectory(transformationName, TRANSFORMATION_DATA_DIRECTORY)
            else:
                transformationDataDirectory = VirtualDirectory(transformationName)
            
            sys.path.append(os.path.join(transformationsDirectoryPath, transformationName))
            mainTransformationPythonModule = getTransformationMainModule(transformationsDirectoryPath, transformationName)
            sys.path.remove(os.path.join(transformationsDirectoryPath, transformationName))
            transformations[transformationName] = mainTransformationPythonModule.Main(copy.copy(configurationDirectory), transformationDataDirectory, lambda d: writeTransformationDataDirectory(transformationName, d))
        else:
            raise UnknownTransformationException('[' + CONFIGURATION_FILE_NAME + ':' + str(requestedTransformationNames[transformationName]) + ']: Unknown transformation: ' + transformationName)

    return transformations

def listFormat(strings):
    if len(strings) > 1:
        return ', '.join(strings[:-1]) + ' and ' + strings[-1]
    elif len(strings) == 1:
        return strings[0]
    else:
        return ''

def main(projectDirectory):
    installationDirectoryRoot = os.getcwd()
    os.chdir(projectDirectory)
    
    sys.stdout.write('Initializing modules...\n')
    modules, procedure = getConfiguration()

    sys.stdout.write('Initializing transformations...\n')
    requestedTransformationNames = {}
    for step in procedure:
        if not step.transformationName in requestedTransformationNames.keys():
            requestedTransformationNames[step.transformationName] = step.lineNumber
    
    transformations = getTransformations(requestedTransformationNames, installationDirectoryRoot)

    Transformation.initialized = True

    for step in procedure:
        sys.stdout.write('Applying ' + step.transformationName + '...\n')
        sys.stdout.flush()

        transformations[step.transformationName].apply([module.getAsParameter() for module in modules if module.name in step.moduleNames])

    sys.stdout.write('Writing...\n')
    for module in modules:
        sys.stdout.write('\t' + module.name + '...\n')
        sys.stdout.flush()
        module.export()

    sys.stdout.write('Done\n')

if __name__ == '__main__':
    if len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        print('Error: Kitrus takes exactly one argument: The project directory.')
