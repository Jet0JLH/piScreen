#!/usr/bin/python3
# nano /home/pi/.config/wf-panel-pi.ini
# add lines
# autohide=true
# autohide_duration=500
import os, sys, subprocess, json
from datetime import datetime
from opt.piScreen.piScreenUtils import Paths

def printInfo(value:str,exitCode:int=-1,style=0):
	if style == 0: print(value)
	elif style == 1: print(f"\33[4;94m{value}\33[0m")
	elif style == 2: print(f"\33[92m{value}\33[0m")
	elif style == 3: print(f"\33[93m{value}\33[0m")
	info["log"].append(f"{datetime.now()} [INFO] {value}")
	if exitCode >= 0: info["verbose"] and print(info) ; exit(exitCode)

def printError(value:str,exitCode:int=-1):
	print(f"\33[91m{value}\33[0m",file=sys.stderr)
	info["log"].append(f"{datetime.now()} [ERROR] {value}")
	if exitCode >= 0: info["verbose"] and print(info) ; exit(exitCode)

tmpPath = "/tmp"
aptPackages = {
	"current": {
		"firefox-esr",
		"vlc",},
	"deprecated": {}
}

piScreenFiles = {
	"user": [
		{
			"type":"file","path":Paths.SETTINGS,"tmp":f"{tmpPath}/settings.json","chown":["pi","pi"],
		}
	],
	"old": [
		{
			"type":"dir","path":Paths.SOFTWARE_DIR,
		}
	],
	"install": [
		{
			"type":"dir","path":Paths.SOFTWARE_DIR,"chown":["pi","pi"],"chmod":"775","facl":[["pi","rwx"]],
		}
	]
}

def configurePythonEnv():
	not info["dry"] and subprocess.call(f"python -m venv env {Paths.SOFTWARE_DIR} && source {Paths.SOFTWARE_DIR}bin/activate && pip install -r {Paths.SOFTWARE_DIR}requirements.txt", shell=True)

def checkVersion():
	printInfo("Load new manifest file",style=1)
	info["manifestNew"] = json.load(open("opt/piScreen/manifest.json"))
	printInfo("Check if piScreen is allready installed",style=1)
	info["userdataSaved"] = False
	if os.path.exists(Paths.MANIFEST):
		printInfo("piScreen is allready installed. Load old manifest")
		info["manifestOld"] = json.load(open(Paths.MANIFEST))
		printInfo(f"Version {info['manifestOld']['version']['major']}.{info['manifestOld']['version']['minor']}.{info['manifestOld']['version']['patch']} current installed")
		if info['manifestNew']['version']['major'] > info['manifestOld']['version']['major'] or (info['manifestNew']['version']['major'] == info['manifestOld']['version']['major'] and info['manifestNew']['version']['minor'] > info['manifestOld']['version']['minor']) or (info['manifestNew']['version']['major'] == info['manifestOld']['version']['major'] and info['manifestNew']['version']['minor'] == info['manifestOld']['version']['minor'] and info['manifestNew']['version']['patch'] > info['manifestOld']['version']['patch']):
			printInfo("It's a old version. Update is possible")
			info["isNewerVersion"] = 1
			userInput = input("Do you want to upgrade? (Y/n): ")
			if userInput == "y" or userInput == "Y" or userInput == "": pass
			else: printInfo("Cancelled by user", 1)
			saveUserFiles()
		elif info['manifestNew']['version']['major'] == info['manifestOld']['version']['major'] and info['manifestNew']['version']['minor'] == info['manifestOld']['version']['minor'] and info['manifestNew']['version']['patch'] == info['manifestOld']['version']['patch']:
			printInfo("It's the same version. Reinstall is possible")
			info["isNewerVersion"] = 0
			userInput = input("Do you want to reinstall? (y/N): ")
			if userInput == "y" or userInput == "Y": pass
			else: printInfo("Cancelled by user", 1)
		else:
			printInfo("It's a newer Version. Downgrade is not intended.")
			info["isNewerVersion"] = -1
			userInput = input("Do you want to remove the newer version und install the oder version? (y/N): ")
			if userInput == "y" or userInput == "Y": pass
			else: printInfo("Cancelled by user", 1)

def doPackages(add:bool):
	printInfo("Update package sources",style=1)
	exitCode = info["dry"] or os.system(f"apt update -y -qq")
	printInfo("Remove deprecated apt packages",style=1)
	for item in aptPackages["deprecated"]:
		printInfo(f"Remove {item}")
		exitCode = info["dry"] or os.system(f"apt remove {item} -y -qq")
		if exitCode != True and exitCode != 0 and exitCode != 100: printError(f"Error while removing {item}",1)
	if add: printInfo("Install apt packages",style=1)
	else: printInfo("Remove apt packages",style=1)
	for item in aptPackages["current"]:
		if add: printInfo(f"Install {item}")
		else: printInfo(f"Remove {item}")
		if add:
			exitCode = info["dry"] or os.system(f"apt install {item} -y -qq")
		else:
			exitCode = info["dry"] or os.system(f"apt remove {item} -y -qq")
		if exitCode != True and exitCode != 0: printError(f"Error while installing {item}",1)

def deletePiScreenFiles():
	printInfo("Delete piScreen files",style=1)
	for item in piScreenFiles["old"]:
		printInfo(f"Delete {item['type']} {item['path']}")
		if os.path.exists(item["path"]):
			if item["type"] == "file":
				try: info["dry"] or os.unlink(item["path"])
				except: printError(f"Unable to remove file {item['path']}",1)
			elif item["type"] == "dir":
				try: info["dry"] or shutil.rmtree(item["path"])
				except: printError(f"Unable to delete dir {item['path']}",1)
		else:
			printInfo(f"{item['type']} {item['path']} does not exists",style=3)

def installPiScreenFiles():
	printInfo("Copy piScreen files",style=1)
	for item in piScreenFiles["install"]:
		tmpPath = os.path.abspath('.' + item['path'])
		if item["type"] == "file":
			printInfo(f"Copy {item['type']} {tmpPath} -> {item['path']}")
			try: 
				if not info["dry"]:
					os.makedirs(os.path.abspath(os.path.join(item["path"],os.pardir)),exist_ok=True)
					shutil.copyfile(tmpPath,item["path"])
					setRights(item)
			except: printError(f"Unable to copy file from {tmpPath} to {item['path']}",1)
		elif item["type"] == "dir":
			printInfo(f"Copy {item['type']} {tmpPath} -> {item['path']}")
			try:
				if not info["dry"]:
					os.makedirs(item["path"],exist_ok=True)
					shutil.copytree(tmpPath,item["path"],dirs_exist_ok=True)
					setRights(item)
			except: printError(f"Unable to copy dir from {tmpPath} to {item['path']}",1)
		elif item["type"] == "mkdir":
			printInfo(f"Create directory {item['path']}")
			try:
				if not info["dry"]: os.makedirs(item["path"],exist_ok=True)
			except: printError(f"Unable to create directory {item['path']}",1)
		elif item["type"] == "rights":
			printInfo(f"Set rights for {item['path']}")
			if not info["dry"]:
				setRights(item)
		else:
			printInfo(f"{item['type']} {item['path']} does not exists",style=3)

def setRights(item):
	if "chown" in item:
		printInfo(f"Set ownership {item['chown'][0]}:{item['chown'][1]} on {item['path']}")
		exitCode = info["dry"] or os.system(f'chown -R {item["chown"][0]}:{item["chown"][1]} "{item["path"]}"')
		if exitCode != 0 and exitCode != True: printError(f"Unable to set ownership {item['chown'][0]}:{item['chown'][1]} on {item['path']}")
	if "chmod" in item:
		printInfo(f"Set rights {item['chmod']} on {item['path']}")
		exitCode = info["dry"] or os.system(f'chmod -R {item["chmod"]} "{item["path"]}"')
		if exitCode != 0 and exitCode != True: printError(f"Unable to set rights {item['chmod']} on {item['path']}")
	if "facl" in item:
		printInfo(f"Remove old acl of {item['path']}")
		exitCode = info["dry"] or os.system(f'setfacl -R -b "{item["path"]}"')
		if exitCode != 0 and exitCode != True: printError(f"Unable to remove acl on {item['path']}")
		for acl in item["facl"]:
			printInfo(f"Set acl {acl[1]} for user {acl[0]} on {item['path']}")
			exitCode = info["dry"] or os.system(f'setfacl -Rm d:u:{acl[0]}:{acl[1]} "{item["path"]}" && setfacl -Rm u:{acl[0]}:{acl[1]} "{item["path"]}"')
			if exitCode != 0 and exitCode != True: printError(f"Unable to set acl {acl[1]} for user {acl[0]} on {item['path']}")

def saveUserFiles():
	printInfo("Save userfiles",style=1)
	for item in piScreenFiles["user"]:
		printInfo(f"Save {item['type']} {item['path']} -> {item['tmp']}")
		if os.path.exists(item["path"]):
			if item["type"] == "file":
				try:
					if not info["dry"]:
						if os.path.exists(item["tmp"]): os.unlink(item["tmp"])
						shutil.copyfile(item["path"],item["tmp"])
				except: printError(f"Unable to copy file from {item['path']} to {item['tmp']}",1)
			elif item["type"] == "dir":
				try:
					if not info["dry"]:
						if os.path.exists(item["tmp"]): shutil.rmtree(item["tmp"])
						shutil.copytree(item["path"],item["tmp"])
				except: printError(f"Unable to copy dir from {item['path']} to {item['tmp']}",1)
		else:
			printInfo(f"{item['type']} {item['path']} does not exists",style=3)
	info["userdataSaved"] = True

def restoreUserFiles():
	printInfo("Restore userfiles",style=1)
	for item in piScreenFiles["user"]:
		printInfo(f"Restore {item['type']} {item['tmp']} -> {item['path']}")
		if os.path.exists(item["tmp"]):
			if item["type"] == "file":
				try:
					if not info["dry"]:
						os.makedirs(os.path.abspath(os.path.join(item["path"],os.pardir)),exist_ok=True)
						if os.path.exists(item["path"]): os.unlink(item["path"])
						shutil.copyfile(item["tmp"],item["path"])
						os.unlink(item["tmp"])
						setRights(item)
				except: printError(f"Unable to copy file from {item['tmp']} to {item['path']}",1)
			elif item["type"] == "dir":
				try:
					if not info["dry"]:
						os.makedirs(item["path"],exist_ok=True)
						shutil.copytree(item["tmp"],item["path"],dirs_exist_ok=True)
						shutil.rmtree(item["tmp"])
						setRights(item)
				except: printError(f"Unable to copy dir from {item['tmp']} to {item['path']}",1)
		else:
			printInfo(f"{item['type']} {item['tmp']} does not exists",style=3)

def killProcesses():
	printInfo("Kill possible running piScreen processes",style=1)
	printInfo("Try to stop service if exist")
	os.system("systemctl stop piScreen")
	os.system("killall piScreenCore.py")
	os.system("killall firefox-esr")
	os.system("killall vlc")

if __name__ == "__main__":
	info = {"log":[]}
	if "--dry" in sys.argv: info["dry"] = True ; printInfo("Script is in dryrun")
	else: info["dry"] = False
	if "--verbose" in sys.argv: info["verbose"] = True
	else: info["verbose"] = False
	if os.geteuid() != 0: printError("Please run this script with root privileges!",1)
	skriptPath = os.path.dirname(os.path.abspath(__file__))
	os.chdir(skriptPath)
	printInfo("Start installation")

	printInfo("Check for allready installed piScreen version")
	checkVersion()
	printInfo("Stop all running piScreen processes")
	killProcesses()
	printInfo("Remove old directories")
	deletePiScreenFiles()
	printInfo("Install apt packages")
	doPackages(True)
	printInfo("Install files")
	installPiScreenFiles()
	printInfo("Configure python environment")
	configurePythonEnv()
	printInfo("Configure desktop")
	#Add routine
	printInfo("Configure firefox")
	#Add routine
	if info["userdataSaved"] == True: restoreUserFiles()
