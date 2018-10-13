## About

Kitrus is a tool for storing sets of files in one location and utilising transformed copies of them in another. It was originally developed to facilitate Minecraft: Java Edition data pack development, but can be used for anything at all.

I built the first version of Kitrus slowly over the course of 9 months, only adding features as I needed them. The result is a program that is not only highly practical but has proven its usefulness and is easily extendible for future functionality.

As of 9 months in development, Kitrus has saved my project 858 files and 2950 lines of code whilst also allowing me to develop in a more convenient location.

## Features

Running Kitrus will copy files from a set of predefined locations to a set of predefined destinations. In the process, it will apply transformations to those files and report the results of those transformations. At present, Kitrus has a mere two transformations:

### Strings

Strings were the original purpose of Kitrus; To allow constant string definitions in data packs. Thus, the strings transformation allows you to associate string keys with string values in a collection of .str files. These string keys can then be referenced anywhere in the files being transformed. When the files are exported by Kitrus, the string keys will be replaced with their associated values. This allows you to write something once, and use it in multiple locations without having to worry about what those files will be used for.

For example, Minecraft does not support strings, so referencing the name of an item in multiple places (Say, in a loot table and in a command) requires you to write it out twice. If you want to change it any point, you would have to change it in multiple places. This is an issue that mature programming langugaes solved eons ago, but fledgling languages like Minecraft commands and other systems that have more rigid requirements have not solved the issue. In these cases, Kitrus' strings transformations can save huge amounts of time and effort.

Strings don't just stop at constant string definitions though. They also allow you to use strings keys inside string defintions, define templates for string substitution and create classes of directories, files and lines of code that will be instantiated with predefined objects during the transformation.

### Stats

The stats transformation does not change the files in any way. It simply reports what file types there are and how many of each type there are.

## Usage in Data Pack development



## Quick Start Guide



## Full Installation Instructions



## How it Works



## Developing Transformations