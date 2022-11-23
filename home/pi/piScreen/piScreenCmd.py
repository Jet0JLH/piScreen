#!/usr/bin/python -u
import json, sys, os, time, datetime

ramdisk = "/media/ramdisk/"
piScreenModeFirefox = ramdisk + "piScreenModeFirefox"
piScreenModeVLC = ramdisk + "piScreenModeVLC"

def printHelp():
	print("This tool is desigend for syscalls.\nSo you have one script, which controlls everything and get every info about.")
	print("""
-h or --help
	Show this information
-v
	Shows detailed informations during execution
--start-browser
	Starts the Browser
--stop-browser
	Stops the Browser
--restart-browser
	Restart the Browser when active
--reboot
	Restarts the Device
--shutdown
	Shutdown the Device
--get-status
	Returns a JSON String with statusinfos
--screen-on
	Turns the screen on
--screen-standby
	Turns the screen in standby
--screen-off
	Turns the screen off
--screen-switch-input
	Tells the display to change the input to our system,
	if it is not currently displayed
--get-website
	Get the current in settings configured website
--set-pw <user> [-f <file with password>] [password]
	Change the password for the weblogin user. Removes the old password.
	You can set the password directly --change-pw <user> <password>
	or you can set the password by file --change-pw <user> -f <file>
	File will be erased after command!
	Special characters in password are only in file mode available!
--check-update [--draft] [--pre-release]
	Check for updates on Github
	If you are using --draft or --pre-release parameter, then you check this channels too
--do-upgrade [--draft] [--pre-release]
	Check for updates, download install files if release is available and do upgrade.
	Sudo rights are requiered!
--set-display-protocol <protocol>
	Set the display protocol to CEC or DDC.
--get-display-protocol
	Retuns the current activ display protocol. CEC or DDC
--set-display-orientation [--no-save] <orientation ID>
	0 = 0 degrees
	1 = 90 degrees
	2 = 180 degrees
	3 = 270 degrees
	If --no-save is set, the orientation will be not permanent.
--get-display-orientation-settings
	Returns the display orientation in settingsfile.
--get-display-orientation
	Returns the display orientation from os.
--schedule-firstrun
	Start schedule firstrun manually.
--add-cron <--pattern <pattern>> [--enabled <false/true>] [--commandset <commandsetID>] [--start <"JJJJ-MM-DD hh:mm">] [--end <"JJJJ-MM-DD hh:mm">] [--command <commandID>] [--parameter <parameter>]
	Add a cronentry to schedule.json.
--update-cron <--index <cronIndex>> [--enabled [false/true]] [--commandset [commandsetID]] [--start ["JJJJ-MM-DD hh:mm"]] [--end ["JJJJ-MM-DD hh:mm"]] [--command [commandID]] [--parameter [parameter]] [--pattern <pattern>]
	Update a cronentry by index in schedule.json.
--delete-cron <--index <cronIndex>>
	Delete a cronentry by index from schedule.json.
--add-trigger <--trigger <triggerID>> [--enabled <false/true>] [--command [commandID]] [--parameter [parameter]] [--commandset [commandsetID]]
	Add a trigger to schedule.json.
--update-trigger <--index <triggerIndex> [--enabled <false/true>] [--trigger <triggerID>] [--command [commandID]] [--parameter [parameter]] [--commandset [commandsetID]]
	Update a trigger by index in schedule.json.
--delete-trigger <--index <triggerIndex>
	Delete a trigger by index from schedule.json.
--add-commandset [--name <name>] [--command <commandID> [parameter]]
	Add a commandset to schedule.json.
--update-commandset <--id <id>> [--name <name>] [--command <commandID> [parameter]]
	Update a commandset by id in schedule.json.
--delete-commandset <--id <id>>
	Delete a commandset by id from schedule.json.
	""")

def isInt(s):
	try: 
		int(s)
		return True
	except ValueError:
		return False

def checkForRootPrivileges():
	if os.geteuid() != 0:
		verbose and print("Please run this function with root privileges.")
		return False
	return True

def loadSettings():
	return json.load(open(f"{os.path.dirname(__file__)}/settings.json"))

def loadSchedule():
	return json.load(open(f"{os.path.dirname(__file__)}/schedule.json"))

def loadManifest():
	return json.load(open(f"{os.path.dirname(__file__)}/manifest.json"))

def endAllModes():
	if os.path.exists(piScreenModeFirefox):
		os.remove(piScreenModeFirefox)
		os.system("killall -q -SIGTERM firefox-esr")
	if os.path.exists(piScreenModeVLC):
		os.remove(piScreenModeVLC)
	

def startBrowser(parameter):
	endAllModes()
	f = open(piScreenModeFirefox,"w")
	f.write(parameter)
	f.close()

def stopBrowser():
	endAllModes()

def restartBrowser():
	os.system("killall -q -SIGTERM firefox-esr")

def reboot():
	verbose and print("Reboot system")
	os.system("reboot")

def shutdown():
	verbose and print("Shutdown system")
	os.system("poweroff")

def getStatus():
	import psutil
	verbose and print("Collect data")
	cpuLoad = round(psutil.getloadavg()[0] / psutil.cpu_count() * 100,2)
	ramTotal = round(psutil.virtual_memory().total / 1024)
	ramUsed = round(ramTotal - psutil.virtual_memory().available / 1024)
	upTime = time.time() - psutil.boot_time()
	upSecound = int(upTime % 60)
	upMinutes = int((upTime / 60) % 60)
	upHours = int((upTime / 60 / 60) % 24)
	upDays = int(upTime / 60 / 60 / 24)
	displayState = open("/media/ramdisk/piScreenDisplay.txt","r").read().strip()
	cpuTemp = round(psutil.sensors_temperatures()["cpu_thermal"][0].current * 1000)
	screenshotTime = 0
	if os.path.isfile("/media/ramdisk/piScreenScreenshot.png"):
		screenshotTime = os.path.getctime("/media/ramdisk/piScreenScreenshot.png")
	return '{"uptime":{"secs":%d,"mins":%d,"hours":%d,"days":%d},"displayState":"%s","cpuTemp":%d,"cpuLoad":%d,"ramTotal":%d,"ramUsed":%d,"display":{"standbySet":%s,"onSet":%s},"screenshotTime":%d}' % (upSecound,upMinutes,upHours,upDays,displayState,cpuTemp,cpuLoad,ramTotal,ramUsed,str(os.path.isfile("/media/ramdisk/piScreenDisplayStandby")).lower(),str(os.path.isfile("/media/ramdisk/piScreenDisplayOn")).lower(),screenshotTime)

def getWebsite():
	if os.path.exists(piScreenModeFirefox): print(open(piScreenModeFirefox,"r").read())

def screenOn():
	verbose and print("Create file for turning on the screen")
	open("/media/ramdisk/piScreenDisplayOn","w").close()

def screenStandby():
	verbose and print("Create file for turning screen to standby")
	open("/media/ramdisk/piScreenDisplayStandby","w").close()

def screenOff():
	verbose and print("Create file for turning of the screen")
	open("/media/ramdisk/piScreenDisplayOff","w").close()

def screenSwitchInput():
	verbose and print("Create file for switching display input")
	open("/media/ramdisk/piScreenDisplaySwitch","w").close()

def checkUpdate(draft,prerelease,silent):
	manifest = loadManifest()
	verbose and print(f"Current version {manifest['version']['major']}.{manifest['version']['minor']}.{manifest['version']['patch']}")
	latestRelease = getLatestVersion(draft,prerelease)
	if latestRelease:
		releaseVersion = latestRelease["tag_name"][1:].split(".")
		releaseVersion[0] = int(releaseVersion[0])
		releaseVersion[1] = int(releaseVersion[1])
		releaseVersion[2] = int(releaseVersion[2])
		if (
		manifest['version']['major'] < releaseVersion[0] or
		(manifest['version']['major'] == releaseVersion[0] and manifest['version']['minor'] < releaseVersion[1]) or
		(manifest['version']['major'] == releaseVersion[0] and manifest['version']['minor'] == releaseVersion[1] and manifest['version']['patch'] < releaseVersion[2])):
			if verbose:
				releaseChannel = "Stable"
				if latestRelease["prerelease"]:
					releaseChannel = "Pre-release"
				if latestRelease["draft"]:
					releaseChannel = "Draft"    
				print(f"New version {releaseVersion[0]}.{releaseVersion[1]}.{releaseVersion[2]} ({releaseChannel}) available")
			else:
				not silent and print(f"{releaseVersion[0]}.{releaseVersion[1]}.{releaseVersion[2]}")
			return latestRelease
		else:
			verbose and print("No new release available")
			return	
	else:
		verbose and print("No new release available")
		return	
	

def getLatestVersion(draft,prerelease):
	import requests
	releases = requests.get("https://api.github.com/repos/Jet0JLH/piScreen/releases")
	if releases.status_code != 200:
		verbose and print("Don't able to connect to Github API")
		return
	for release in releases.json():
		isPrerelease = release["prerelease"]
		isDraft = release["draft"]
		if not isDraft and not isPrerelease:
			#Stable Release
			return release
		elif isPrerelease and not isDraft:
			#Prerelease
			if prerelease or draft:
				return release
		elif isDraft:
			#Draft
			if draft:
				return release
	return

def downloadUpdate(draft,prerelease):
	import requests
	verbose and print("Check for updates")
	update = checkUpdate(draft,prerelease,True)
	if update:
		verbose and print("Download update")
		updateVersion = update["tag_name"][1:].split(".")
		downloadDir = f"/tmp/piScreen{updateVersion[0]}.{updateVersion[1]}.{updateVersion[2]}"
		os.path.isdir(downloadDir) and rmDir(downloadDir)
		os.mkdir(downloadDir)
		downloadUrl = ""
		for asset in update["assets"]:
			if asset["name"] == "install.zip" and asset["state"] == "uploaded":
				downloadUrl = asset["browser_download_url"]
				break
		if downloadUrl != "":
			verbose and print(downloadUrl)
			open(f"{downloadDir}/install.zip","wb").write(requests.get(downloadUrl).content)
			verbose and print("Download finished")
			verbose and print("Extract files")
			import zipfile
			with zipfile.ZipFile(f"{downloadDir}/install.zip", 'r') as installZip:
				installZip.extractall(downloadDir)
			verbose and print("Set rights for installation routine")
			os.system(f"chmod +x {downloadDir}/install/install.py")
			verbose and print("Start installation")
			import subprocess
			updateProcess = subprocess.Popen([f"{downloadDir}/install/install.py", "--update", "-y"])
			updateProcess.wait()
			updateProcess.returncode != 0 and verbose and print("Something went wrong during installation")
		else:
			verbose and print("Something went wrong while downloading Updatefile")
		verbose and print("Cleanup installation")
		rmDir(downloadDir)
		try:
			os.remove("/media/ramdisk/piScreenUpdateStatus.txt")
		except:
			print("Could not remove Updatestatus File")
	else:
		verbose and print("Update not possible")

def rmDir(path):
	for root, dirs, files in os.walk(path, topdown=False):
		for name in files:
			os.remove(os.path.join(root, name))
		for name in dirs:
			os.rmdir(os.path.join(root, name))
	os.rmdir(path)

def setDisplayProtocol(protocol):
	protocol = protocol.lower()
	if protocol == "cec" or protocol == "ddc":
		verbose and print(f"Write {protocol} as display protocol in settings.json")
		settingsJson = loadSettings()
		settingsJson["settings"]["display"]["protocol"] = protocol
		settingsFile = open(f"{os.path.dirname(__file__)}/settings.json", "w")
		settingsFile.write(json.dumps(settingsJson,indent=4))
		settingsFile.close()
		if os.path.exists("/media/ramdisk/piScreenDisplayCEC"):
			os.remove("/media/ramdisk/piScreenDisplayCEC")
		if os.path.exists("/media/ramdisk/piScreenDisplayDDC"):
			os.remove("/media/ramdisk/piScreenDisplayDDC")
		if protocol == "cec":
			open("/media/ramdisk/piScreenDisplayCEC","w").close()
		elif protocol == "ddc":
			open("/media/ramdisk/piScreenDisplayDDC","w").close()
	else:
		verbose and print(f"{protocol} is no permitted protocol")

def getDisplayProtocol():
	settingsJson = loadSettings()
	print(settingsJson["settings"]["display"]["protocol"])

def getDisplayOrientation():
	import subprocess
	orientation = subprocess.check_output("DISPLAY=:0 xrandr --query --verbose | grep HDMI-1 | cut -d ' ' -f 6",shell=True).decode("utf-8").replace("\n","")
	if orientation == "normal":
		return 0
	elif orientation == "right":
		return 1
	elif orientation == "inverted":
		return 2
	elif orientation == "left":
		return 3
	return None

def modifySchedule(element,typ,scheduleJson):
	changed = False
	if f"--{element}" in sys.argv:
		indexOfElement = sys.argv.index(f"--{element}") + 1
		if indexOfElement >= len(sys.argv) or sys.argv[indexOfElement].startswith("--"):
			try:
				del scheduleJson[element]
				changed = True
			except:
				pass
		else:
			if typ == bool:
				if sys.argv[indexOfElement].lower() == "true":
					scheduleJson[element] = True
					changed = True
				elif sys.argv[indexOfElement].lower() == "false":
					scheduleJson[element] = False
					changed = True
				else:
					verbose and print(f"{element} is not true or false")
			elif typ == int:
				if isInt(sys.argv[indexOfElement]):
					scheduleJson[element] = int(sys.argv[indexOfElement])
					changed = True
				else:
					verbose and print(f"{element} is no number")
			elif typ == datetime.datetime:
				try:
					datetime.datetime.strptime(sys.argv[indexOfElement], "%Y-%m-%d %H:%M")
					scheduleJson[element] = sys.argv[indexOfElement]
					changed = True
				except:
					verbose and print(f"{element} is no valid date")
			elif typ == "pattern":
				if all(ch in "0123456789/-*, " for ch in sys.argv[indexOfElement]) and len(sys.argv[indexOfElement].split(" ")) == 5:
					scheduleJson[element] = sys.argv[indexOfElement]
					changed = True
				else:
					verbose and print(f"{element} is no valid pattern")
			else:
				#Normal String without validation
				scheduleJson[element] = sys.argv[indexOfElement]
				changed = True
				pass
	return changed

def addCron():
	if i + 2 < len(sys.argv):
		if "--pattern" in sys.argv:
			pattern = sys.argv.index("--pattern") + 1
			if pattern < len(sys.argv):
				changed = False
				item = {}
				changed = modifySchedule("enabled",bool,item) or changed
				changed = modifySchedule("commandset",int,item) or changed
				changed = modifySchedule("start",datetime.datetime,item) or changed
				changed = modifySchedule("end",datetime.datetime,item) or changed
				changed = modifySchedule("pattern","pattern",item) or changed
				changed = modifySchedule("command",int,item) or changed
				changed = modifySchedule("parameter",None,item) or changed
				if changed:
					try:
						scheduleJson = loadSchedule()
						scheduleJson["cron"].append(item)
						scheduleFile = open(f"{os.path.dirname(__file__)}/schedule.json", "w")
						scheduleFile.write(json.dumps(scheduleJson,indent=4))
						scheduleFile.close()
						verbose and print("Changed schedule.json")
					except:
						verbose and print("Error with schedule.json")
						exit(1)
				else:
					verbose and print("Empty cron element")
					exit(1)
			else:
				verbose and print("No pattern value")
				exit(1)
		else:
			verbose and print("Argument --pattern expected")
			exit(1)
	else:
		verbose and print("Not enough arguments")
		exit(1)

def updateCron():
	if i + 2 < len(sys.argv):
		if "--index" in sys.argv:
			index = sys.argv.index("--index") + 1
			if index < len(sys.argv):
				if isInt(sys.argv[index]):
					index = int(sys.argv[index])
					try:
						scheduleJson = loadSchedule()
						if index < len(scheduleJson["cron"]) and index >= 0:
							changed = False
							changed = modifySchedule("enabled",bool,scheduleJson["cron"][index]) or changed
							changed = modifySchedule("commandset",int,scheduleJson["cron"][index]) or changed
							changed = modifySchedule("start",datetime.datetime,scheduleJson["cron"][index]) or changed
							changed = modifySchedule("end",datetime.datetime,scheduleJson["cron"][index]) or changed
							changed = modifySchedule("pattern","pattern",scheduleJson["cron"][index]) or changed
							changed = modifySchedule("command",int,scheduleJson["cron"][index]) or changed
							changed = modifySchedule("parameter",None,scheduleJson["cron"][index]) or changed
							if changed:
								scheduleFile = open(f"{os.path.dirname(__file__)}/schedule.json", "w")
								scheduleFile.write(json.dumps(scheduleJson,indent=4))
								scheduleFile.close()
								verbose and print("Changed schedule.json")
						else:
							verbose and print("Index is bigger than count of cron entries")
							exit(1)
					except:
						verbose and print("Error with schedule.json")
						exit(1)
				else:
					verbose and print("Index is no number")
					exit(1)
			else:
				verbose and print("No index value")
				exit(1)
		else:
			verbose and print("Argument --index expected")
			exit(1)
	else:
		verbose and print("Not enough arguments")
		exit(1)

def addTrigger():
	if i + 2 < len(sys.argv):
		if "--trigger" in sys.argv:
			if isInt(sys.argv.index("--trigger") + 1):
				changed = False
				item = {}
				changed = modifySchedule("enabled",bool,item) or changed
				changed = modifySchedule("trigger",int,item) or changed
				changed = modifySchedule("command",int,item) or changed
				changed = modifySchedule("parameter",None,item) or changed
				changed = modifySchedule("commandset",int,item) or changed
				if changed:
					try:
						scheduleJson = loadSchedule()
						scheduleJson["trigger"].append(item)
						scheduleFile = open(f"{os.path.dirname(__file__)}/schedule.json", "w")
						scheduleFile.write(json.dumps(scheduleJson,indent=4))
						scheduleFile.close()
						verbose and print("Changed schedule.json")
					except:
						verbose and print("Error with schedule.json")
						exit(1)
				else:
					verbose and print("Empty trigger element")
					exit(1)
			else:
				verbose and print("No pattern value")
				exit(1)
		else:
			verbose and print("Argument --trigger expected")
			exit(1)
	else:
		verbose and print("Not enough arguments")
		exit(1)

def updateTrigger():
	if i + 2 < len(sys.argv):
		if "--index" in sys.argv:
			index = sys.argv.index("--index") + 1
			if index < len(sys.argv):
				if isInt(sys.argv[index]):
					index = int(sys.argv[index])
					try:
						scheduleJson = loadSchedule()
						if index < len(scheduleJson["trigger"]) and index >= 0:
							changed = False
							changed = modifySchedule("enabled",bool,scheduleJson["trigger"][index]) or changed
							changed = modifySchedule("trigger",int,scheduleJson["trigger"][index]) or changed
							changed = modifySchedule("command",int,scheduleJson["trigger"][index]) or changed
							changed = modifySchedule("parameter",None,scheduleJson["trigger"][index]) or changed
							changed = modifySchedule("commandset",int,scheduleJson["trigger"][index]) or changed
							if changed:
								scheduleFile = open(f"{os.path.dirname(__file__)}/schedule.json", "w")
								scheduleFile.write(json.dumps(scheduleJson,indent=4))
								scheduleFile.close()
								verbose and print("Changed schedule.json")
						else:
							verbose and print("Index is bigger than count of trigger entries")
							exit(1)
					except:
						verbose and print("Error with schedule.json")
						exit(1)
				else:
					verbose and print("Index is no number")
					exit(1)
			else:
				verbose and print("No index value")
				exit(1)
		else:
			verbose and print("Argument --index expected")
			exit(1)
	else:
		verbose and print("Not enough arguments")
		exit(1)

#Main
verbose = False
sys.argv.pop(0) #Remove Path
if len(sys.argv) < 1:
	printHelp()

if "-v" in sys.argv:
    verbose = True
    sys.argv.remove("-v")

for i, origItem in enumerate(sys.argv):
	item = origItem.lower()
	if (
		item == "-h" or
		item == "--help"
	):
		printHelp()
	elif item == "--start-browser":
		if i + 1 < len(sys.argv):
			startBrowser(sys.argv[i + 1])
		else:
			print("Not enough arguments")
	elif item == "--restart-browser":
		restartBrowser()
	elif item == "--stop-browser":
		stopBrowser()
	elif item == "--reboot":
		reboot()
	elif item == "--shutdown":
		shutdown()
	elif item == "--get-status":
		print(getStatus())
	elif item == "--screen-on":
		screenOn()
	elif item == "--screen-standby":
		screenStandby()
	elif item == "--screen-off":
		screenOff()
	elif item == "--screen-switch-input":
		screenSwitchInput()
	elif item == "--get-website":
		getWebsite()
	elif item == "--set-pw":
		if i + 2 < len(sys.argv):
			if sys.argv[i + 2].lower() == "-f": #Check file Mode
				verbose and print("Set weblogin password with file")
				if i + 3 < len(sys.argv):
					if os.path.isfile(sys.argv[i + 3]):
						os.system(f"head -1 {sys.argv[i + 3]} | tr -d '\n' | sudo xargs -0 htpasswd -c -b /etc/apache2/.piScreen_htpasswd '{sys.argv[i + 1]}'")
						os.remove(sys.argv[i + 3])
					else:
						verbose and print("Passwordfile doesn't exist")
				else:
					verbose and print("No Passwordfile specified")
			else: #Check direct mode
				verbose and print("Set weblogin password with next parameter")
				os.system(f"sudo htpasswd -c -b /etc/apache2/.piScreen_htpasswd '{sys.argv[i + 1]}' '{sys.argv[i + 2]}'")
		else:
			verbose and print("Not enough arguments")
	elif item == "--check-update":
		prerelease = False
		draft = False
		if i + 2 < len(sys.argv):
			if sys.argv[i + 2].lower() == "--draft":
				draft = True
			elif sys.argv[i + 2].lower() == "--pre-release":
				prerelease = True
		if i + 1 < len(sys.argv):
			if sys.argv[i + 1].lower() == "--draft":
				draft = True
			elif sys.argv[i + 1].lower() == "--pre-release":
				prerelease = True
		
		checkUpdate(draft,prerelease,False)
	elif item == "--do-upgrade":
		not checkForRootPrivileges() and sys.exit(1)
		prerelease = False
		draft = False
		if i + 2 < len(sys.argv):
			if sys.argv[i + 2].lower() == "--draft":
				draft = True
			elif sys.argv[i + 2].lower() == "--pre-release":
				prerelease = True
		if i + 1 < len(sys.argv):
			if sys.argv[i + 1].lower() == "--draft":
				draft = True
			elif sys.argv[i + 1].lower() == "--pre-release":
				prerelease = True
		downloadUpdate(draft,prerelease)
	elif item == "--set-display-protocol":
		if i + 1 < len(sys.argv):
			setDisplayProtocol(sys.argv[i + 1])
		else:
			verbose and print("Not enough arguments")
	elif item == "--get-display-protocol":
		getDisplayProtocol()
	elif item == "--set-display-orientation":
		saveSettings = True
		if "--no-save" in sys.argv:
			saveSettings = False
			sys.argv.remove("--no-save")
		if i + 1 < len(sys.argv):
			found = False
			if sys.argv[i + 1] == "0":
				found = True
				os.system("DISPLAY=:0 xrandr -o normal")
				verbose and print("Change displayorientation to normal")
			elif sys.argv[i + 1] == "1":
				found = True
				os.system("DISPLAY=:0 xrandr -o right")
				verbose and print("Change displayorientation to right")
			elif sys.argv[i + 1] == "2":
				found = True
				os.system("DISPLAY=:0 xrandr -o inverted")
				verbose and print("Change displayorientation to inverted")
			elif sys.argv[i + 1] == "3":
				found = True
				os.system("DISPLAY=:0 xrandr -o left")
				verbose and print("Change displayorientation to left")
			if found and saveSettings:
				settingsJson = loadSettings()
				settingsJson["settings"]["display"]["orientation"] = int(sys.argv[i + 1])
				settingsFile = open(f"{os.path.dirname(__file__)}/settings.json", "w")
				settingsFile.write(json.dumps(settingsJson,indent=4))
				settingsFile.close()
				verbose and print("Write orientation in settings")
		else:
			verbose and print("Not enough arguments")
	elif item == "--get-display-orientation-settings":
		settingsJson = loadSettings()
		try:
			print(settingsJson["settings"]["display"]["orientation"])
		except:
			print(0)
	elif item == "--get-display-orientation":
		print(getDisplayOrientation())
	elif item == "--schedule-firstrun":
		open("/media/ramdisk/piScreenScheduleFirstRun","w").close()
	elif item == "--add-cron":
		addCron()
	elif item == "--update-cron":
		updateCron()
	elif item == "--delete-cron":
		if i + 2 < len(sys.argv):
			if sys.argv[i + 1] == "--index":
				if isInt(sys.argv[i + 2]):
					try:
						scheduleJson = loadSchedule()
						index = int(sys.argv[i + 2])
						if index < len(scheduleJson["cron"]) and index >= 0:
							del scheduleJson["cron"][index]
							scheduleFile = open(f"{os.path.dirname(__file__)}/schedule.json", "w")
							scheduleFile.write(json.dumps(scheduleJson,indent=4))
							scheduleFile.close()
							verbose and print("Changed schedule.json")
						else:
							verbose and print("Index is bigger than count of cron entries")
							exit(1)
					except:
						verbose and print("Error with schedule.json")
						exit(1)
				else:
					verbose and print("Index is no number")
					exit(1)
			else:
				verbose and print("Argument --index expected")
				exit(1)
		else:
			verbose and print("Not enough arguments")
			exit(1)
	elif item == "--delete-commandset":
		if i + 2 < len(sys.argv):
			if sys.argv[i + 1] == "--id":
				if isInt(sys.argv[i + 2]):
					try:
						found = False
						scheduleJson = loadSchedule()
						max = len(scheduleJson["commandsets"])
						for x in range(0,max):
							if "id" in scheduleJson["commandsets"][x]:
								if scheduleJson["commandsets"][x]["id"] == int(sys.argv[i + 2]):
									del scheduleJson["commandsets"][x]
									found = True
									max = max - 1
						if found:
							scheduleFile = open(f"{os.path.dirname(__file__)}/schedule.json", "w")
							scheduleFile.write(json.dumps(scheduleJson,indent=4))
							scheduleFile.close()
							verbose and print("Changed schedule.json")
					except:
						verbose and print("Error with schedule.json")
						exit(1)
				else:
					verbose and print("Index is no number")
					exit(1)
			else:
				verbose and print("Argument --id expected")
				exit(1)
		else:
			verbose and print("Not enough arguments")
			exit(1)
	elif item == "--add-trigger":
		addTrigger()
	elif item == "--update-trigger":
		updateTrigger()
	elif item == "--delete-trigger":
		if i + 2 < len(sys.argv):
			if sys.argv[i + 1] == "--index":
				if isInt(sys.argv[i + 2]):
					try:
						scheduleJson = loadSchedule()
						index = int(sys.argv[i + 2])
						if index < len(scheduleJson["trigger"]) and index >= 0:
							del scheduleJson["trigger"][index]
							scheduleFile = open(f"{os.path.dirname(__file__)}/schedule.json", "w")
							scheduleFile.write(json.dumps(scheduleJson,indent=4))
							scheduleFile.close()
							verbose and print("Changed schedule.json")
						else:
							verbose and print("Index is bigger than count of trigger entries")
							exit(1)
					except:
						verbose and print("Error with schedule.json")
						exit(1)
				else:
					verbose and print("Index is no number")
					exit(1)
			else:
				verbose and print("Argument --index expected")
				exit(1)
		else:
			verbose and print("Not enough arguments")
			exit(1)