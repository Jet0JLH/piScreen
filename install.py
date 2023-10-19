#!/usr/bin/python3
import json, os, sys, pwd, shutil, subprocess
from OpenSSL.crypto import FILETYPE_PEM, load_certificate
from base64 import b64encode
from datetime import datetime

from home.pi.piScreen.piScreenUtils import Paths

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

if os.geteuid() != 0:
	printError("Please run this script with root privileges!",1)
import home.pi.piScreen.piScreenUtils as piScreenUtils

SHA256OID = "OID.2.16.840.1.101.3.4.2.1"
SHA384OID = "OID.2.16.840.1.101.3.4.2.2"
SHA512OID = "OID.2.16.840.1.101.3.4.2.3"

tmpPath = "/tmp"
aptPackages = {
	"current": {"unclutter","apache2","php","cec-utils","ddcutil","firefox","vlc","libreoffice-impress","libcec-dev","build-essential","python-dev-is-python3","libapache2-mpm-itk","python3-cec","python3-vlc"},
	"deprecated": {}
}
pipPackages = {
	"current": {"monitorcontrol", "marionette_driver"},
	"deprecated": {}
}
piScreenFiles = {
	"user": [
		{"type":"dir","path":f"{Paths.SOFTWARE_DIR}certs","tmp":f"{tmpPath}/certs","chown":["pi","pi"]},
		{"type":"file","path":f"{Paths.SETTINGS}","tmp":f"{tmpPath}/settings.json","chown":["pi","pi"]},
		{"type":"file","path":f"{Paths.SCHEDULE}","tmp":f"{tmpPath}/schedule.json","chown":["pi","pi"]},
		{"type":"file","path":"/etc/apache2/.piScreen_htpasswd","tmp":f"{tmpPath}/.piScreen_htpasswd","chown":["pi","pi"]},
		{"type":"dir","path":f"{Paths.WWW_DIR}/admin/data","tmp":f"{tmpPath}/data","chown":["pi","pi"]}
	],
	"old": [
		{"type":"dir","path":Paths.SOFTWARE_DIR},
		{"type":"dir","path":"/srv/piScreen"},
		{"type":"file","path":"/etc/apache2/.piScreen_htpasswd"},
		{"type":"file","path":"/etc/apache2/sites-available/piScreen.conf"},
		{"type":"file","path":"/home/pi/.config/autostart/piScreenCore.desktop"},
		{"type":"file","path":"/etc/sudoers.d/050_piScreen-nopasswd"},
		{"type":"file","path":"/etc/firefox/piScreen.js"},
		{"type":"file","path":"/etc/systemd/system/piScreen.service"}
	],
	"install": [
		{"type":"dir","path":Paths.SOFTWARE_DIR,"chown":["pi","pi"],"chmod":"775","facl":[["pi","rwx"],["www-data","rwx"]]},
		{"type":"dir","path":"/srv/piScreen","chown":["www-data","www-data"],"chmod":"775","facl":[["pi","rwx"],["www-data","rwx"]]},
		{"type":"file","path":"/home/pi/.config/autostart/piScreenCore.desktop","chown":["root","root"],"chmod":"755","facl":[["pi","rwx"],["www-data","rwx"]]},
		{"type":"file","path":"/etc/systemd/system/piScreen.service","chown":["root","root"],"chmod":"744"},
		{"type":"file","path":"/etc/apache2/sites-available/piScreen.conf"},
		{"type":"file","path":"/etc/sudoers.d/050_piScreen-nopasswd","chmod":"0440"},
		{"type":"file","path":"/etc/firefox/piScreen.js"},
		{"type":"file","path":"/home/pi/.bash_completion","chown":["pi","pi"]},
		{"type":"file","path":"/usr/share/plymouth/themes/pix/splash.png"},
		{"type":"mkdir","path":f"/home/pi/piScreen/certs"},
		{"type":"mkdir","path":f"{Paths.WWW_DIR}/admin/data/general"},
		{"type":"mkdir","path":f"{Paths.WWW_DIR}/admin/data/firefox"},
		{"type":"mkdir","path":f"{Paths.WWW_DIR}/admin/data/vlc"},
		{"type":"mkdir","path":f"{Paths.WWW_DIR}/admin/data/impress"}
	]
}

def install():
	killProcesses()
	doPackages(True)
	configureRamdisk(True)
	saveUserFiles()
	deletePiScreenFiles()
	installPiScreenFiles()
	restoreUserFiles()
	convertSchedule()
	printInfo("Update settings file")
	mergedJson = mergeJsons(Paths.SETTINGS,"./defaults/default_settings.json")
	settingsFile = info["dry"] or open(Paths.SETTINGS, "w")
	printInfo("Write settings file")
	info["dry"] or settingsFile.write(json.dumps(mergedJson,indent=4))
	info["dry"] or settingsFile.close()
	configureWebserver(True)
	configureWebbrowser()
	configureScreensaver()
	configureDesktop()
	printInfo("Create symlink for screenshot")
	exitCode = info["dry"] or os.system(f"ln -s {Paths.SCREENSHOT} /srv/piScreen/admin/")
	exitCode = info["dry"] or os.system(f"ln -s {Paths.SCREENSHOT_THUMBNAIL} /srv/piScreen/admin/")
	if exitCode != True and exitCode != 0: printError("Unable to create symlink for screenshot")

def uninstall():
	killProcesses()
	doPackages(False)
	configureRamdisk(False)
	configureWebserver(False)
	deletePiScreenFiles()

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
	printInfo("Remove deprecated pip packages",style=1)
	for item in pipPackages["deprecated"]:
		printInfo(f"Remove {item}")
		exitCode = info["dry"] or os.system(f"python3 -m pip uninstall {item}")
		if exitCode != True and exitCode != 0: printError(f"Error while removing pip package {item}",1)
	if add: printInfo("Install pip packages",style=1)
	else: printInfo("Remove pip packages",style=1)
	for item in pipPackages["current"]:
		if add: printInfo(f"Install {item}")
		else: printInfo(f"Uninstall {item}")
		if add:
			exitCode = info["dry"] or os.system(f"python3 -m pip install {item} --break-system-packages")
		else:
			exitCode = info["dry"] or os.system(f"python3 -m pip uninstall {item}")
		if exitCode != True and exitCode != 0: printError(f"Error while installing pip package {item}",1)

def configureRamdisk(add:bool):
	printInfo("Configure ramdisk",style=1)
	try:
		printInfo(f"{('Remove','Add')[add]} ramdisk entry in fstab")
		lines = open("/etc/fstab", "r").readlines()
		newLines = []
		for line in lines:
			if "/media/ramdisk" not in line: newLines.append(line)
			else: printInfo(f"Found old entry: {line[:-2]}")
		add and newLines.append("tmpfs\t/media/ramdisk\ttmpfs\tdefaults,size=5%,mode=0777\t0\t0\n")
		info["dry"] or open("/etc/fstab", "w").writelines(newLines)
	except: printError(f"Unable to write entry in fstab")
	try:
		printInfo(f"{('Remove','Add')[add]} ramdisk folder")
		if add: info["dry"] or os.makedirs(Paths.RAMDISK,exist_ok=True)
		else: info["dry"] or (os.path.exists(Paths.RAMDISK) and os.system(f"umount -l {Paths.RAMDISK}") and shutil.rmtree(Paths.RAMDISK))
	except: printError(f"Unable to {('remove','add')[add]} ramdisk folder")

def configureScreensaver():
	try:
		printInfo("Configure screensaver",style=1)
		lines = open("/etc/xdg/lxsession/LXDE-pi/autostart","r").readlines()
		newLines = []
		for line in lines:
			if "@lxpanel --profile LXDE-pi" not in line and "@xset s" not in line and "@xset +dpms" not in line and "@xset -dpms" not in line:
				newLines.append(line)
		#newLines.append("@lxpanel --profile LXDE-pi\n")
		newLines.append("@xset s 0\n")
		newLines.append("@xset -dpms\n")
		info["dry"] or open("/etc/xdg/lxsession/LXDE-pi/autostart","w").writelines(newLines)
	except: printError("Unable to edit LXDE configuration")

def configureDesktop():
	printInfo("Configure desktop",style=1)
	try:
		printInfo("Remove desktop wallpaper")
		info["dry"] or os.system(f"export DISPLAY=:0;export XAUTHORITY=/home/pi/.Xauthority;export XDG_RUNTIME_DIR=/run/user/1000;pcmanfm --wallpaper-mode=color")
	except: printError("Unable to set desktop wallpaper")
	try:
		printInfo("Remove desktop icons")
		lines = open("/home/pi/.config/pcmanfm/LXDE-pi/desktop-items-0.conf","r").readlines()
		newLines = []
		for line in lines:
			if "show_trash=" not in line and "show_mounts=" not in line:
				newLines.append(line)
		newLines.append("show_trash=0\n")
		newLines.append("show_mounts=0\n")
		info["dry"] or open("/home/pi/.config/pcmanfm/LXDE-pi/desktop-items-0.conf","w").writelines(newLines)
	except: printError("Unable to edit pcmanfm configuration")

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

def configureWebserver(add:bool):
	printInfo("Configure webserver",style=1)
	if add:
		if not info["dry"]:
			exitCode = 0
			exitCode += os.system("a2dissite -q 000-default")
			exitCode += os.system("a2ensite -q piScreen")
			exitCode += os.system("a2enmod -q rewrite")
			exitCode += os.system("a2enmod -q ssl")
			exitCode += os.system("a2enmod -q mpm_itk")
			if exitCode > 0: printError("Error while configure apache2 mods and sites")
		try:
			if not os.path.exists(f"{Paths.SOFTWARE_DIR}certs"):
				printInfo("Create cert dir")
				os.mkdir(f"{Paths.SOFTWARE_DIR}certs")
		except: printError("Unable to create cert dir")
		if os.path.exists("/etc/apache2/.piScreen_htpasswd"): printInfo("Weblogin allready configured")
		else:
			exitCode = -1
			while info["dry"] == False and exitCode != 0:
				printInfo("Configure user pi for weblogin")
				exitCode = os.system("htpasswd -c /etc/apache2/.piScreen_htpasswd pi")
		if os.path.exists(f"{Paths.SOFTWARE_DIR}certs/server.key") and os.path.exists(f"{Paths.SOFTWARE_DIR}certs/server.csr") and os.path.exists(f"{Paths.SOFTWARE_DIR}certs/server.crt"):
			printInfo("Webserver certs allready exists")
		else:
			printInfo("Generate webserver certs")
			if not info["dry"]:
				exitCode = 0
				exitCode += os.system(f"openssl genrsa -out {Paths.SOFTWARE_DIR}certs/server.key 4096")
				exitCode += os.system(f"openssl req -new -key {Paths.SOFTWARE_DIR}certs/server.key -out {Paths.SOFTWARE_DIR}certs/server.csr -sha256 -subj /C=DE/ST=BW/L=/O=PiScreen/OU=/CN=")
				exitCode += os.system(f"openssl req -noout -text -in {Paths.SOFTWARE_DIR}certs/server.csr")
				exitCode += os.system(f"openssl x509 -req -days 3650 -in {Paths.SOFTWARE_DIR}certs/server.csr -signkey {Paths.SOFTWARE_DIR}certs/server.key -out {Paths.SOFTWARE_DIR}certs/server.crt")
				if exitCode > 0: printError("Error while generating webserver certs")
	else:
		info["dry"] or os.system("a2dissite -q piScreen")

def configureWebbrowser():
	firefoxProfilePath = "/home/pi/.mozilla/firefox/"
	certOverridePath = firefoxProfilePath
	printInfo("Configure webbrowser",style=1)
	printInfo("Start firefox for profile generation")
	os.system("sudo -u pi timeout 5 firefox --headless > /dev/null 2>&1")
	printInfo("Search for firefox profile")
	if not os.path.exists(firefoxProfilePath):
		printError("Unable to find firefox profiles directory")
		return
	for item in os.listdir(firefoxProfilePath):
		if os.path.isdir(f"{firefoxProfilePath}{item}"):
			if ".default-esr" in item:
				printInfo("Default firefox profile found")
				certOverridePath = f"{firefoxProfilePath}{item}/cert_override.txt"
				break
	if not certOverridePath.endswith("cert_override.txt"):
		printError("There is no default firefox profile!")
	else:
		entry = getEntry("localhost", 443, f"{Paths.SOFTWARE_DIR}certs/server.crt")
		if not os.path.exists(certOverridePath):
			try:
				printInfo("Create empty firefox cert override file")
				open(certOverridePath,"w").write("")
			except:
				printError("Unable to create firefox certfile")
		try:
			if entry not in open(certOverridePath).read():
				printInfo("Write cert entry to firefox cert override file")
				info["dry"] or open(certOverridePath,"a").write(entry)
			else:
				printInfo("Firefox cert override file entry already exists")
		except:
			printError("Unable to append firefox certfile")

def getSha():
	output = subprocess.run(["timeout", "1", "openssl", "s_client", "-showcerts", "-connect", "localhost:443"], capture_output=True).stdout.decode("utf-8").split("\n")
	for item in output:
		if "Peer signing digest" in item:
			return item.split(": ")[1].upper()
	return "SHA256"

def base64Append(data):
	missing = len(data) % 4
	if missing:
		data += b'=' * (4 - missing)
	return data

def getEntry(hostname, port, certPath):
	cert = load_certificate(FILETYPE_PEM, open(certPath).read())
	sha = getSha()

	returnVal = hostname
	returnVal += ":"
	returnVal += str(port)
	returnVal += ":"
	returnVal += "\t"
	if sha == "SHA256":
		returnVal += SHA256OID
	elif sha == "SHA384":
		returnVal += SHA384OID
	elif sha == "SHA512":
		returnVal += SHA512OID
	else:
		exit("Hashing of certificate " + hostname + ":" + port + " not correct! Exiting...")
	returnVal += "\t"

	fingerprint = cert.digest(sha).decode('utf-8')
	returnVal += fingerprint
	returnVal += "\t"
	returnVal += "MUT"
	returnVal += "\t"

	serialNumber = cert.get_serial_number()
	serialNumber = serialNumber.to_bytes((serialNumber.bit_length() // 8) + 1, 'big')
	issuer = cert.get_issuer().der()
	cryptKey = b''.join([
		(0).to_bytes(4, 'big'),
		(0).to_bytes(4, 'big'),
		len(serialNumber).to_bytes(4, 'big'),
		len(issuer).to_bytes(4, 'big'),
		serialNumber,
		issuer
	])

	cryptKey = base64Append(b64encode(cryptKey)).decode('utf-8')
	returnVal += cryptKey
	returnVal += "\n"

	return returnVal

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

def mergeJsons(userFilePath:str,defaultFilePath:str) -> json:
	def mergeSubobject(userObj:dict,defaultObj:dict):
		for item in defaultObj.keys():
			if type(defaultObj[item]) == dict:
				if item not in userObj: userObj[item] = {}
				mergeSubobject(userObj[item],defaultObj[item])
			else:
				if item not in userObj: userObj[item] = defaultObj[item]
	try: userFile = json.load(open(userFilePath))
	except: printError(f"Unable to load {userFilePath}. Generate empty file") ; userFile = json.loads("{}")
	try: defaultFile = json.load(open(defaultFilePath))
	except: printError(f"Unable to load {defaultFilePath}",1)
	mergeSubobject(userFile,defaultFile)
	return userFile

def convertSchedule():
	printInfo("Convert schedule if necessary",style=1)
	printInfo("Load schedule file")
	try:
		changed = False
		scheduleJson = json.load(open(Paths.SCHEDULE))
		if scheduleJson["structureVersion"] == "0.1":
			printInfo("Structure version is 0.1 and will be converted to 0.2")
			changed = True
			scheduleJson["structureVersion"] = "0.2"
			for item in scheduleJson["trigger"]:
				item["cases"] = {}
				item["cases"]["true"] = {}
				if "command" in item: item["cases"]["true"]["command"] = item["command"] ; del item["command"]
				if "parameter" in item: item["cases"]["true"]["parameter"] = item["parameter"] ; del item["parameter"]
				if "commandset" in item: item["cases"]["true"]["commandset"] = item["commandset"] ; del item["commandset"]


		if changed:
			printInfo("Schedule is now converted and will be written to file")
			if not info["dry"]:
				scheduleFile = open(Paths.SCHEDULE, "w")
				scheduleFile.write(json.dumps(scheduleJson,indent=4))
				scheduleFile.close()
		else:
			printInfo("Nothing to convert")
	except:
		printError("Unable to convert schedule")
		try:
			if os.path.exists(Paths.SCHEDULE):
				printInfo("Remove schedule")
				info["dry"] or os.unlink(Paths.SCHEDULE)
			printInfo("Restore default schedule")
			info["dry"] or shutil.copyfile("./defaults/default_schedule.json",Paths.SCHEDULE)
			for item in piScreenFiles["user"]:
				if item["path"] == Paths.SCHEDULE: setRights(item)
		except:
			printError("Unable to reset schedule to default")


def killProcesses():
	printInfo("Kill possible running piScreen processes",style=1)
	printInfo("Try to stop service if exist")
	os.system("systemctl stop piScreen")
	os.system("killall piScreenCore.py")
	os.system("killall piScreenDisplay.py")
	os.system("killall piScreenSchedule.py")
	os.system("killall firefox")
	os.system("killall vlc")
	os.system("killall soffice.bin")

info = {"log":[]}
if "--dry" in sys.argv: info["dry"] = True ; printInfo("Script is in dryrun")
else: info["dry"] = False
if "--verbose" in sys.argv: info["verbose"] = True
else: info["verbose"] = False

if __name__ == "__main__":
	skriptPath = os.path.dirname(os.path.abspath(__file__))
	os.chdir(skriptPath)
	printInfo("Checking for pi user",style=1)
	try:
		pwd.getpwnam('pi')
	except KeyError:
		printError("User pi does not exist. Script is working only with user pi",1)
	try:
		printInfo("Load new manifest file",style=1)
		info["manifestNew"] = json.load(open("home/pi/piScreen/manifest.json"))
		printInfo(f"Installer of {info['manifestNew']['application-name']} in Version {info['manifestNew']['version']['major']}.{info['manifestNew']['version']['minor']}.{info['manifestNew']['version']['patch']}")
	except:
		printError("Unable to load mainifest.json! Installationfile is corrupted",1)
	try:
		printInfo("Check if piScreen is allready installed",style=1)
		if os.path.exists(Paths.MANIFEST):
			printInfo("piScreen is allready installed. Load old manifest")
			info["manifestOld"] = json.load(open(Paths.MANIFEST))
			printInfo(f"Version {info['manifestOld']['version']['major']}.{info['manifestOld']['version']['minor']}.{info['manifestOld']['version']['patch']} current installed")
			if info['manifestNew']['version']['major'] > info['manifestOld']['version']['major'] or (info['manifestNew']['version']['major'] == info['manifestOld']['version']['major'] and info['manifestNew']['version']['minor'] > info['manifestOld']['version']['minor']) or (info['manifestNew']['version']['major'] == info['manifestOld']['version']['major'] and info['manifestNew']['version']['minor'] == info['manifestOld']['version']['minor'] and info['manifestNew']['version']['patch'] > info['manifestOld']['version']['patch']):
				printInfo("It's a old version. Update is possible")
				info["isNewerVersion"] = 1
			elif info['manifestNew']['version']['major'] == info['manifestOld']['version']['major'] and info['manifestNew']['version']['minor'] == info['manifestOld']['version']['minor'] and info['manifestNew']['version']['patch'] == info['manifestOld']['version']['patch']:
				printInfo("It's the same version. Reinstall is possible")
				info["isNewerVersion"] = 0
			else:
				printInfo("It's a newer Version. Downgrade is not intended.")
				info["isNewerVersion"] = -1
	except:
		printError("Unable to load old manifest.json", 1)
		info["unableToLoadOldManifest"] = True
	if "isNewerVersion" not in info:
		printInfo("Install piScreen")
		install()
		printInfo("Installation has been finished. You have to reboot your system next. Do you want to perform a reboot now? [Y/n]",style=1)
		inp = input()
		if "y" == inp.lower() or "" == inp:
			printInfo("Your system will reboot in 10 seconds")
			info["dry"] or os.system("sleep 10 && reboot &")
	elif "--update" in sys.argv and ("isNewerVersion" in info and info["isNewerVersion"] == 1):
		printInfo("Start automatic update")
		info["autoUpdate"] = True
		install()
		printInfo("Update has been finished. Reboot will be performed in 10 seconds.",style=1)
		info["dry"] or os.system("sleep 10 && reboot &")
	elif "--override" in sys.argv and ("isNewerVersion" in info and info["isNewerVersion"] == 0):
		printInfo("Start automatic override")
		info["autoOverride"] = True
		install()
		printInfo("Override has been finished. Reboot will be performed in 10 seconds.",style=1)
		info["dry"] or os.system("sleep 10 && reboot &")
	elif "--force" in sys.argv and ("isNewerVersion" in info and info["isNewerVersion"] == -1):
		printInfo("Start automatic force override")
		info["autoForceOverride"] = True
		uninstall()
		install()
		printInfo("Force downgrade has been finished. Reboot will be performed in 10 seconds.",style=1)
		info["dry"] or os.system("sleep 10 && reboot &")
	elif "--uninstall" in sys.argv and "isNewerVersion" in info:
		printInfo("Start automatic uninstall")
		info["autoUninstall"] = True
		uninstall()
		printInfo("Uninstall has been finished",style=1)
	elif info["isNewerVersion"] == 1:
		userInput = None
		while userInput not in {"n","N","y","Y",""}:
			userInput = input("Do you want to update? [Y/n]")
		if userInput.lower() == "n":
			printInfo("Abort update",0)
		else:
			install()
			printInfo("Update has been finished. You have to reboot your system next. Do you want to perform a reboot now? [Y/n]",style=1)
			inp = input()
			if "y" == inp.lower() or "" == inp:
				printInfo("Your system will reboot in 10 seconds")
				info["dry"] or os.system("sleep 10 && reboot &")
	elif info["isNewerVersion"] == 0:
		printInfo("Use parameter --override to reinstall piScreen",0)
	elif info["isNewerVersion"] == -1:
		printInfo("If you want to reinstall it anyway, you should use the parameter --force\nIt will uninstall piScreen and starts installation after",0)


	info["verbose"] and print(info)