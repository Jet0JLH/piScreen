#!/usr/bin/python

import os, sys, subprocess
from re import template

operationPath = "/tmp/"
destinationPath = operationPath + "install/"
outputZipName = "install.zip"
outputZipPath = operationPath + outputZipName

excludeFiles = [".gitignore", "README.md", "runForDev.sh", "prepareInstallZip.py"]
excludeDirs = [".git", "home/pi/piScreen/certs"]

def executeWait(command):
    args = command.split(" ")
    process = subprocess.Popen(args)
    process.wait()
    return process.returncode

def removeDir(path):
    executeWait(f"rm -f -R {path}")

def removeFile(path):
    executeWait(f"rm -f {path}")

def copyDir(source, destination):
    executeWait(f"cp -R {source} {destination}")

def renameDir(fromPath, toPath):
    executeWait(f"mv {fromPath} {toPath}")

if len(sys.argv) == 2:
    if os.geteuid() != 0:
        exit("Please run this script with root privileges.")

    global inputPath
    inputPath = sys.argv[1]

    if inputPath == ".":
        inputPath = os.getcwd()

    if inputPath == "--help" or inputPath == "-h":
        exit("""Usage: sudo ./prepareInstallZip.py [piScreenDirPath]
        (use . for the current working directory)""")

    if not os.path.exists(inputPath):
        exit("Path does not exist.")

    removeDir(destinationPath)
    removeFile(f"/tmp/{outputZipName}")

    tempList = inputPath.split("/")
    try: 
        tempList.remove("")
        tempList.remove("")
    except: pass
    
    inputDirName = tempList[(len(tempList) - 1)]

    copyDir(inputPath, operationPath)

    renameDir(operationPath + inputDirName, destinationPath)

    for file in excludeFiles:
        removeFile(destinationPath + file)
        print("Excluding file: ", end="")
        print(destinationPath + file)

    for dir in excludeDirs:
        removeDir(destinationPath + dir)
        print("Excluding dir: ", end="")
        print(destinationPath + dir)

    executeWait(f"zip -q -r /tmp/{outputZipName} {destinationPath}")
    print(f"{inputPath} was zipped to {outputZipPath}.")
else:
    exit("Only one argument is required and accepted.")






