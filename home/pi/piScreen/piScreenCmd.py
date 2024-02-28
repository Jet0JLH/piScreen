#!/usr/bin/python3 -u
import json, sys, os, time, datetime, socket, piScreenUtils
from piScreenUtils import Paths

skriptPath = os.path.dirname(os.path.abspath(__file__))
os.chdir(skriptPath)


def printHelp():
	print("""This tool is desigend for syscalls.
So you have one script, which controlls everything and get every info about.

=== General ===
-h or --help
	Show this information.
-v or --verbose
	Shows detailed informations during execution.
--get-status
	Returns a JSON String with statusinfos.
--set-language <countryCode>
	Changes website language.
--set-password <user> [-f <file with password>] [password]
	Change the password for the weblogin user. Removes the old password.
	You can set the password directly --change-pw <user> <password>
	or you can set the password by file --change-pw <user> -f <file>
	File will be erased after command!
	Special characters in password are only in file mode available!
--check-update [--draft] [--pre-release]
	Check for updates on Github.
	If you are using --draft or --pre-release parameter, then you check this channels too.
--do-upgrade [--draft] [--pre-release]
	Check for updates, download install files if release is available and do upgrade.
	Sudo rights are requiered!
--do-write-log <--level <debug/info/warning/error/critical>> <message>
	Writes a logentry.

=== Hostcontrol ===
--do-reboot
	Restarts the Device.
--do-shutdown
	Shutdown the Device.
--get-desktop-configuration
	Returns the full desktop configuration.
--set-desktop-configuration [<--mode> <mode>] [<--wallpaper> <path>] [<--background-color> <hexColor>]
	Configure the desktop wallpaper.
	Possible modes are: color|stretch|fit|crop|center|tile|screen
	Hex colors has 6 characters and starts with a hash. Keep in mind, this character has to be escaped with a backslash!

=== Display ===
--get-display-protocol
	Retuns the current activ display protocol. CEC or DDC.
--set-display-protocol <protocol>
	Set the display protocol to CEC, DDC or MANUALLY.
--get-display-orientation [--settings]
	Returns the display orientation from os.
	If parameter --settings is given, it returns the display orientation in settings file.
--set-display-orientation [--no-save] <orientationID>
	0 = 0 degrees
	1 = 90 degrees
	2 = 180 degrees
	3 = 270 degrees
	If --no-save is set, the orientation will be not permanent.
--set-display <[on][off]>
	Set the display to on or off. Using the set display protocol.
--set-display-input
	Tells the display to change the input to our system, if it is not currently displayed.
	Currently only available on cec.
--get-display-resolution [--settings]
	Returns the current display resolution.
	With the parameter --settings it will return the settings value.
--set-display-resolution [<width> <height>]
	Set the display resolution to a fixed value
	To reset the resolution to automatic, use no parameters
--get-display-forcemode
	Returns the value of the display forcemode as True or False.
--set-display-forcemode <true/false>
	Enables or disables the display forcemode.
	If eanbled, piScreen will try to keep the display in the last setted state.
	Even if an user will try to change the state direct on the display.

=== Modes ===
--stop-mode
	Stops the current running mode and switches back to 'none'.
 == Firefox ==
--start-firefox <URL>
	Starts the Browser or navigate it to new location if already open.
--do-firefox-restart
	Restart the Browser when active.
--do-firefox-refresh
	Refresh browser when active.
 == VLC ==
--start-vlc <pathToFile>
	Starts VLC Player.
--do-vlc-restart
	Restarts VLC Player.
--do-vlc-play
	Play the video if mode is VLC.
--do-vlc-pause
	Pause the video if mode is VLC.
--do-vlc-toggle-play-pause
	Pause/Play the video if mode is VLC.
--set-vlc-volume <valueInPercent>
	Set the audio volume to the given value.
 == Impress ==
--start-impress <pathToFile>
	Starts Libreoffice Impress.
--do-impress-restart
	Restarts Libreoffice Impress when active.

=== Schedule ===
--run-command-manually <--command <commandID>> [<--parameter <parameter>>]
	Runs a single command selected by commandid.
 == Cron ==
--run-firstrun
	Start schedule firstrun manually.
--run-lastcron
	Start last cron entry.
--run-cron-manually <--index <cronIndex>>
	Runs the cron entry selected by index in schedule.
--add-cron-entry <--pattern <pattern>> [--enabled <false/true>] [--commandset <commandsetID>] [--start <"YYYY-MM-DD hh:mm">] [--end <"YYYY-MM-DD hh:mm">] [--command <commandID>] [--parameter <parameter>] [--description <description>]
	Add a cronentry to schedule.json.
--update-cron-entry <--index <cronIndex>> [--enabled [false/true]] [--commandset [commandsetID]] [--start ["YYYY-MM-DD hh:mm"]] [--end ["YYYY-MM-DD hh:mm"]] [--command [commandID]] [--parameter [parameter]] [--pattern <pattern>] [--description <description>]
	Update a cronentry by index in schedule.json.
--delete-cron-entry <--index <cronIndex>>
	Delete a cronentry by index from schedule.json.
--set-cron-ignore-timespan [%Y-%m-%d %H:%M %Y-%m-%d %H:%M]
	Set ignore time from date <-> to date.
	If no parameter is set, the ignore time will be deleted.
 == Commandset ==
--run-commandset-manually <--id <commandsetID>>
	Runs the commandset selected by id in schedule.
--add-commandset-entry <--description <description>> [--command <commandID> [parameter]]
	Add a commandset to schedule.json.
--update-commandset-entry <--id <id>> [--description <description>] [--command <commandID> [parameter]]
	Update a commandset by id in schedule.json.
--delete-commandset-entry <--id <id>>
	Delete a commandset by id from schedule.json.
 == Trigger ==
--add-trigger-entry <--trigger <triggerID>> [--enabled <true/false>] [--first-state-dont-trigger <true/false>] [--run-once <true/false>] [--command:<caseName> <commandID>] [--parameter:<caseName> <parameter>] [--commandset:<caseName> <commandsetID>] [--description <description>]
	Add a trigger to schedule.json.
	If the trigger needs additional parameters, so you can add them like this: [--<parameterName> <parameterValue>].
--update-trigger-entry <--index <triggerIndex>> [--trigger <triggerID>] [--enabled <true/false>] [--first-state-dont-trigger <true/false>] [--run-once <true/false>] [--command:<caseName> <commandID>] [--parameter:<caseName> <parameter>] [--commandset:<caseName> <commandsetID>] [--description <description>]
	Update a trigger by index in schedule.json.
	If the trigger needs additional parameters, so you can add them like this: [--<parameterName> <parameterValue>].
--delete-trigger-entry <--index <triggerIndex>>
	Delete a trigger by index from schedule.json.
	""")

def sendToCore(data:dict) -> dict:
	bufferSize = 1024
	SOCKET = 28888
	try:
		s = socket.socket(family=socket.AF_INET,type=socket.SOCK_DGRAM)
		s.settimeout(5)
		s.sendto(str.encode(json.dumps(data)),("127.0.0.1",SOCKET))
		msg = s.recvfrom(bufferSize)
		return json.loads(msg[0].decode("utf-8"))
	except Exception as err:
		piScreenUtils.logging.error("Unable to reach core")
		piScreenUtils.logging.debug(err)
		verbose and print("Unable to reach core")
		return {"code":-1}

def checkForRootPrivileges():
	if os.geteuid() != 0:
		verbose and print("Please run this function with root privileges.")
		return False
	return True

def loadSchedule():
	return json.load(open(Paths.SCHEDULE))

def loadManifest():
	return json.load(open(Paths.MANIFEST))

def startBrowser(parameter):
	piScreenUtils.logging.info(f"Navigate browser to {parameter}")
	sendToCore({"cmd":3,"parameter":{"mode":1,"parameter":parameter}})

def stopMode():
	piScreenUtils.logging.info("Stop mode")
	sendToCore({"cmd":3,"parameter":{"mode":0,"parameter":""}})

def restartBrowser():
	piScreenUtils.logging.info("Restart browser")
	os.system("killall -q -SIGTERM firefox-esr")

def startVLC(parameter,soft=False):
	piScreenUtils.logging.info(f"Load VLC file {parameter}")
	sendToCore({"cmd":3,"parameter":{"mode":2,"parameter":parameter}})

def startImpress(parameter):
	piScreenUtils.logging.info(f"Load Impress file {parameter}")
	sendToCore({"cmd":3,"parameter":{"mode":3,"parameter":parameter}})

def restartImpress():
	piScreenUtils.logging.info("Restart impress")
	os.system("killall -q -SIGTERM soffice.bin")

def reboot():
	piScreenUtils.logging.info("Reboot system")
	verbose and print("Reboot system")
	os.system("reboot")

def shutdown():
	piScreenUtils.logging.info("Shutdown system")
	verbose and print("Shutdown system")
	os.system("poweroff")

def configureDesktop():
	piScreenUtils.logging.debug("Configure desktop")
	try:
		os.environ["DISPLAY"] = ":0"
		os.environ["XAUTHORITY"] = "/home/pi/.Xauthority"
		os.environ["XDG_RUNTIME_DIR"] = "/run/user/1000"
		os.environ["XDG_SESSION_TYPE"] = "tty"
		if f"--mode" in sys.argv:
			indexOfElement = sys.argv.index(f"--mode") + 1
			if indexOfElement >= len(sys.argv) or sys.argv[indexOfElement].startswith("--"):
				piScreenUtils.logging.warning("No parameter given")
				verbose and print("No parameter given")
			else:
				if sys.argv[indexOfElement].lower() in ["color", "stretch", "fit", "crop", "center", "tile", "screen"]:
					piScreenUtils.logging.info(f"Set wallpaper mode to {os.path.abspath(sys.argv[indexOfElement])}")
					os.system(f"pcmanfm --wallpaper-mode={sys.argv[indexOfElement].lower()}")
				else:
					piScreenUtils.logging.warning("No possible mode selected")
					verbose and print("No possible mode selected")
		time.sleep(0.5)
		if f"--wallpaper" in sys.argv:
			indexOfElement = sys.argv.index(f"--wallpaper") + 1
			if indexOfElement >= len(sys.argv) or sys.argv[indexOfElement].startswith("--"):
				piScreenUtils.logging.warning("No parameter given")
				verbose and print("No parameter given")
			else:
				if os.path.exists(sys.argv[indexOfElement]):
					piScreenUtils.logging.info(f"Set wallpaper to {os.path.abspath(sys.argv[indexOfElement])}")
					os.system(f'pcmanfm "--set-wallpaper={os.path.abspath(sys.argv[indexOfElement])}"')
				else:
					piScreenUtils.logging.warning("Wallpaper File doesn't exist")
					verbose and print("Wallpaper File doesn't exist")
		time.sleep(0.5)
		if f"--background-color" in sys.argv:
			indexOfElement = sys.argv.index(f"--background-color") + 1
			if indexOfElement >= len(sys.argv) or sys.argv[indexOfElement].startswith("--"):
				piScreenUtils.logging.warning("No parameter given")
				verbose and print("No parameter given")
			else:
				import re
				if re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', sys.argv[indexOfElement]):
					piScreenUtils.logging.info(f"Set backgroundcolor to {os.path.abspath(sys.argv[indexOfElement])}")
					desktopConfig = open("/home/pi/.config/pcmanfm/LXDE-pi/desktop-items-0.conf","r").readlines()
					count = 0
					found = False
					for i in desktopConfig:
						if i.startswith("desktop_bg="):
							desktopConfig[count] = f"desktop_bg={sys.argv[indexOfElement]}\n"
							found = True
						count = count + 1
					if not found:
						desktopConfig.append(f"desktop_bg={sys.argv[indexOfElement]}\n")
					open("/home/pi/.config/pcmanfm/LXDE-pi/desktop-items-0.conf","w").writelines(desktopConfig)
					os.system("pcmanfm --reconfigure")
				else:
					piScreenUtils.logging.warning("Given color is no valid hex string")
					verbose and print("Given color is no valid hex string")

	except Exception as err:
		piScreenUtils.logging.warning("Error while access desktop configuration")
		piScreenUtils.logging.debug(err)
		verbose and print("Error while access desktop configuration")
		exit(1)

def getDekstopConfig():
	desktopJson = {}
	desktopConfig = open("/home/pi/.config/pcmanfm/LXDE-pi/desktop-items-0.conf","r").readlines()
	for i in desktopConfig:
		tmp = i.split("=")
		if len(tmp) > 1:
			desktopJson[tmp[0]] = tmp[1].replace("\n","")
	print(json.dumps(desktopJson))

def getStatus():
	status = sendToCore({"cmd":2})
	if "data" in status: return json.dumps(status["data"])
	else: return json.dumps({})

def screenOn():
	piScreenUtils.logging.info("Send display on command to core")
	verbose and print("Send display on command to core")
	sendToCore({"cmd":5,"parameter":1})

def screenOff():
	piScreenUtils.logging.info("Send display off command to core")
	verbose and print("Send display off command to core")
	sendToCore({"cmd":5,"parameter":2})

def screenSwitchInput():
	piScreenUtils.logging.info("Send display change input command to core")
	verbose and print("Send display change input command to core")
	sendToCore({"cmd":5,"parameter":3})

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
		verbose and print("Unable to connect to Github API")
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
			piScreenUtils.logging.error("Something went wrong while downloading Updatefile")
			verbose and print("Something went wrong while downloading Updatefile")
		verbose and print("Cleanup installation")
		rmDir(downloadDir)
	else:
		verbose and print("Update not possible")

def rmDir(path):
	for root, dirs, files in os.walk(path, topdown=False):
		for name in files:
			os.remove(os.path.join(root, name))
		for name in dirs:
			os.rmdir(os.path.join(root, name))
	os.rmdir(path)

def modifySchedule(element,typ,scheduleJson,elementName:str=""):
	if elementName == "": elementName = element
	changed = False
	if f"--{element}" in sys.argv:
		indexOfElement = sys.argv.index(f"--{element}") + 1
		if indexOfElement >= len(sys.argv) or sys.argv[indexOfElement].startswith("--"):
			try:
				del scheduleJson[elementName]
				changed = True
			except Exception as err:
				piScreenUtils.logging.debug(err)
		else:
			if typ == bool:
				if sys.argv[indexOfElement].lower() == "true":
					scheduleJson[elementName] = True
					changed = True
				elif sys.argv[indexOfElement].lower() == "false":
					scheduleJson[elementName] = False
					changed = True
				else:
					piScreenUtils.logging.warning(f"{element} is not true or false")
					verbose and print(f"{element} is not true or false")
			elif typ == int:
				if piScreenUtils.isInt(sys.argv[indexOfElement]):
					scheduleJson[elementName] = int(sys.argv[indexOfElement])
					changed = True
				else:
					piScreenUtils.logging.warning(f"{element} is no number")
					verbose and print(f"{element} is no number")
			elif typ == datetime.datetime:
				try:
					datetime.datetime.strptime(sys.argv[indexOfElement], dateFormate)
					scheduleJson[elementName] = sys.argv[indexOfElement]
					changed = True
				except Exception as err:
					piScreenUtils.logging.warning(f"{element} is no valid date")
					piScreenUtils.logging.debug(err)
					verbose and print(f"{element} is no valid date")
			elif typ == "pattern":
				if all(ch in "0123456789/-*, " for ch in sys.argv[indexOfElement]) and len(sys.argv[indexOfElement].split(" ")) == 5:
					scheduleJson[elementName] = sys.argv[indexOfElement]
					changed = True
				else:
					piScreenUtils.logging.warning(f"{element} is no valid pattern")
					verbose and print(f"{element} is no valid pattern")
			else:
				#Normal String without validation
				scheduleJson[elementName] = sys.argv[indexOfElement]
				changed = True
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
				changed = modifySchedule("description",None,item) or changed
				if changed:
					try:
						scheduleJson = loadSchedule()
						scheduleJson["cron"].append(item)
						scheduleFile = open(Paths.SCHEDULE, "w")
						scheduleFile.write(json.dumps(scheduleJson,indent=4))
						scheduleFile.close()
						piScreenUtils.logging.info("Changed schedule.json")
						verbose and print("Changed schedule.json")
					except Exception as err:
						piScreenUtils.logging.error("Error with schedule.json")
						piScreenUtils.logging.debug(err)
						verbose and print("Error with schedule.json")
						exit(1)
				else:
					piScreenUtils.logging.warning("Empty cron element")
					verbose and print("Empty cron element")
					exit(1)
			else:
				piScreenUtils.logging.warning("No pattern value")
				verbose and print("No pattern value")
				exit(1)
		else:
			piScreenUtils.logging.warning("Argument --pattern expected")
			verbose and print("Argument --pattern expected")
			exit(1)
	else:
		piScreenUtils.logging.warning("Not enough arguments")
		verbose and print("Not enough arguments")
		exit(1)

def updateCron():
	if i + 2 < len(sys.argv):
		if "--index" in sys.argv:
			index = sys.argv.index("--index") + 1
			if index < len(sys.argv):
				if piScreenUtils.isInt(sys.argv[index]):
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
							changed = modifySchedule("description",None,scheduleJson["cron"][index]) or changed
							if changed:
								scheduleFile = open(Paths.SCHEDULE, "w")
								scheduleFile.write(json.dumps(scheduleJson,indent=4))
								scheduleFile.close()
								piScreenUtils.logging.info("Changed schedule.json")
								verbose and print("Changed schedule.json")
						else:
							piScreenUtils.logging.warning("Index is bigger than count of cron entries")
							verbose and print("Index is bigger than count of cron entries")
							exit(1)
					except Exception as err:
						piScreenUtils.logging.error("Error with schedule.json")
						piScreenUtils.logging.debug(err)
						verbose and print("Error with schedule.json")
						exit(1)
				else:
					piScreenUtils.logging.warning("Index is no number")
					verbose and print("Index is no number")
					exit(1)
			else:
				piScreenUtils.logging.warning("No index value")
				verbose and print("No index value")
				exit(1)
		else:
			piScreenUtils.logging.warning("Argument --index expected")
			verbose and print("Argument --index expected")
			exit(1)
	else:
		piScreenUtils.logging.warning("Not enough arguments")
		verbose and print("Not enough arguments")
		exit(1)

def addTrigger():
	if i + 2 < len(sys.argv):
		sys.argv.remove("--add-trigger-entry")
		if "--trigger" in sys.argv:
			if piScreenUtils.isInt(sys.argv.index("--trigger") + 1):
				changed = False
				item = {}
				item["cases"] = {}
				changed = modifySchedule("enabled",bool,item) or changed
				changed = modifySchedule("stick-to-cron-ignore",bool,item,"stickToCronIgnore") or changed
				changed = modifySchedule("trigger",int,item) or changed
				changed = modifySchedule("first-state-dont-trigger",bool,item,"firstStateDontTrigger") or changed
				changed = modifySchedule("run-once",bool,item,"runOnce") or changed
				changed = modifySchedule("description",None,item) or changed
				for i2 in sys.argv:
					if i2.startswith("--command:") and len(i2) > 10:
						if i2[i2.index(":")+1:] not in item["cases"]: item["cases"][i2[i2.index(":")+1:]] = {}
						changed = modifySchedule(i2[2:],int,item["cases"][i2[i2.index(":")+1:]],i2[2:i2.index(":")]) or changed
					elif i2.startswith("--parameter:") and len(i2) > 12:
						if i2[i2.index(":")+1:] not in item["cases"]: item["cases"][i2[i2.index(":")+1:]] = {}
						changed = modifySchedule(i2[2:],None,item["cases"][i2[i2.index(":")+1:]],i2[2:i2.index(":")]) or changed
					elif i2.startswith("--commandset:") and len(i2) > 13:
						if i2[i2.index(":")+1:] not in item["cases"]: item["cases"][i2[i2.index(":")+1:]] = {}
						changed = modifySchedule(i2[2:],int,item["cases"][i2[i2.index(":")+1:]],i2[2:i2.index(":")]) or changed
					elif i2.startswith("--") and i2 not in {"--index","--enabled","--trigger","--first-state-dont-trigger","--firstStateDontTrigger","--run-once","--runOnce","--","--stick-to-cron-ignore"}:
						changed = modifySchedule(i2[2:],None,item) or changed
				if changed:
					try:
						scheduleJson = loadSchedule()
						scheduleJson["trigger"].append(item)
						scheduleFile = open(Paths.SCHEDULE, "w")
						scheduleFile.write(json.dumps(scheduleJson,indent=4))
						scheduleFile.close()
						piScreenUtils.logging.info("Changed schedule.json")
						verbose and print("Changed schedule.json")
					except Exception as err:
						piScreenUtils.logging.error("Error with schedule.json")
						piScreenUtils.logging.debug(err)
						verbose and print("Error with schedule.json")
						exit(1)
				else:
					piScreenUtils.logging.warning("Empty trigger element")
					verbose and print("Empty trigger element")
					exit(1)
			else:
				piScreenUtils.logging.warning("No pattern value")
				verbose and print("No pattern value")
				exit(1)
		else:
			piScreenUtils.logging.warning("Argument --trigger expected")
			verbose and print("Argument --trigger expected")
			exit(1)
	else:
		piScreenUtils.logging.warning("Not enough arguments")
		verbose and print("Not enough arguments")
		exit(1)

def updateTrigger():
	if i + 2 < len(sys.argv):
		sys.argv.remove("--update-trigger-entry")
		if "--index" in sys.argv:
			index = sys.argv.index("--index") + 1
			if index < len(sys.argv):
				if piScreenUtils.isInt(sys.argv[index]):
					index = int(sys.argv[index])
					try:
						scheduleJson = loadSchedule()
						if index < len(scheduleJson["trigger"]) and index >= 0:
							item = scheduleJson["trigger"][index]
							changed = False
							changed = modifySchedule("enabled",bool,item) or changed
							changed = modifySchedule("stick-to-cron-ignore",bool,item,"stickToCronIgnore") or changed
							changed = modifySchedule("trigger",int,item) or changed
							changed = modifySchedule("first-state-dont-trigger",bool,item,"firstStateDontTrigger") or changed
							changed = modifySchedule("run-once",bool,item,"runOnce") or changed
							changed = modifySchedule("description",None,item) or changed
							for i2 in sys.argv:
								if i2.startswith("--command:") and len(i2) > 10:
									if i2[i2.index(":")+1:] not in item["cases"]: item["cases"][i2[i2.index(":")+1:]] = {}
									changed = modifySchedule(i2[2:],int,item["cases"][i2[i2.index(":")+1:]],i2[2:i2.index(":")]) or changed
								elif i2.startswith("--parameter:") and len(i2) > 12:
									if i2[i2.index(":")+1:] not in item["cases"]: item["cases"][i2[i2.index(":")+1:]] = {}
									changed = modifySchedule(i2[2:],None,item["cases"][i2[i2.index(":")+1:]],i2[2:i2.index(":")]) or changed
								elif i2.startswith("--commandset:") and len(i2) > 13:
									if i2[i2.index(":")+1:] not in item["cases"]: item["cases"][i2[i2.index(":")+1:]] = {}
									changed = modifySchedule(i2[2:],int,item["cases"][i2[i2.index(":")+1:]],i2[2:i2.index(":")]) or changed
								elif i2.startswith("--") and i2 not in {"--index","--enabled","--trigger","--first-state-dont-trigger","--firstStateDontTrigger","--run-once","--runOnce","--","--stick-to-cron-ignore"}:
									changed = modifySchedule(i2[2:],None,item) or changed
							if changed:
								cases = []
								for case in item["cases"]:
									cases.append(case)
								for case in cases:
									if item["cases"][case] == {}: del item["cases"][case]
								scheduleFile = open(Paths.SCHEDULE, "w")
								scheduleFile.write(json.dumps(scheduleJson,indent=4))
								scheduleFile.close()
								piScreenUtils.logging.info("Changed schedule.json")
								verbose and print("Changed schedule.json")
						else:
							piScreenUtils.logging.warning("Index is bigger than count of trigger entries")
							verbose and print("Index is bigger than count of trigger entries")
							exit(1)
					except Exception as err:
						piScreenUtils.logging.error("Error with schedule.json")
						piScreenUtils.logging.debug(err)
						verbose and print("Error with schedule.json")
						exit(1)
				else:
					piScreenUtils.logging.warning("Index is no number")
					verbose and print("Index is no number")
					exit(1)
			else:
				piScreenUtils.logging.warning("No index value")
				verbose and print("No index value")
				exit(1)
		else:
			piScreenUtils.logging.warning("Argument --index expected")
			verbose and print("Argument --index expected")
			exit(1)
	else:
		piScreenUtils.logging.warning("Not enough arguments")
		verbose and print("Not enough arguments")
		exit(1)

def addCommandset(update):
	if i + 2 < len(sys.argv):
		if "--description" in sys.argv or update:
			import random
			item = {}
			if update and modifySchedule("id",int,item):
				deleteCommandset()
			else:
				item["id"] = random.randint(100000,999999)
			modifySchedule("description",str,item)
			item["commands"] = []
			for x in range(len(sys.argv)):
				if sys.argv[x] == "--command":
					if len(sys.argv) > x + 2:
						if not sys.argv[x + 1].startswith("--"):
							if piScreenUtils.isInt(sys.argv[x + 1]):
								subitem = {}
								subitem["command"] = int(sys.argv[x + 1])
								if not sys.argv[x + 2].startswith("--"):
									subitem["parameter"] = sys.argv[x + 2]
								item["commands"].append(subitem)
					elif len(sys.argv) > x + 1:
						if not sys.argv[x + 1].startswith("--"):
							if piScreenUtils.isInt(sys.argv[x + 1]):
								subitem = {}
								subitem["command"] = int(sys.argv[x + 1])
								item["commands"].append(subitem)
			try:
				scheduleJson = loadSchedule()
				scheduleJson["commandsets"].append(item)
				scheduleFile = open(Paths.SCHEDULE, "w")
				scheduleFile.write(json.dumps(scheduleJson,indent=4))
				scheduleFile.close()
				piScreenUtils.logging.info("Changed schedule.json")
				verbose and print("Changed schedule.json")
				print(item["id"])
			except Exception as err:
				piScreenUtils.logging.error("Error with schedule.json")
				piScreenUtils.logging.debug(err)
				verbose and print("Error with schedule.json")
				exit(1)
		else:
			piScreenUtils.logging.warning("Argument --description expected")
			verbose and print("Argument --description expected")
			exit(1)
	else:
		piScreenUtils.logging.warning("Not enough arguments")
		verbose and print("Not enough arguments")
		exit(1)

def updateCommandset():
	if i + 2 < len(sys.argv):
		if "--id" in sys.argv:
			addCommandset(True)
		else:
			piScreenUtils.logging.warning("Argument --id expected")
			verbose and print("Argument --id expected")
			exit(1)
	else:
		piScreenUtils.logging.warning("Not enough arguments")
		verbose and print("Not enough arguments")
		exit(1)

def deleteCommandset():
	if i + 2 < len(sys.argv):
		if "--id" in sys.argv:
			if len(sys.argv) > sys.argv.index("--id") + 1 and piScreenUtils.isInt(sys.argv[sys.argv.index("--id") + 1]):
				try:
					found = False
					scheduleJson = loadSchedule()
					max = len(scheduleJson["commandsets"])
					for x in range(0,max):
						if "id" in scheduleJson["commandsets"][x]:
							if scheduleJson["commandsets"][x]["id"] == int(sys.argv[sys.argv.index("--id") + 1]):
								del scheduleJson["commandsets"][x]
								found = True
								max = max - 1
								break
					if found:
						scheduleFile = open(Paths.SCHEDULE, "w")
						scheduleFile.write(json.dumps(scheduleJson,indent=4))
						scheduleFile.close()
						piScreenUtils.logging.info("Changed schedule.json")
						verbose and print("Changed schedule.json")
				except Exception as err:
					piScreenUtils.logging.error("Error with schedule.json")
					piScreenUtils.logging.debug(err)
					verbose and print("Error with schedule.json")
					exit(1)
			else:
				piScreenUtils.logging.warning("Index is no number")
				verbose and print("Index is no number")
				exit(1)
		else:
			piScreenUtils.logging.warning("Argument --id expected")
			verbose and print("Argument --id expected")
			exit(1)
	else:
		piScreenUtils.logging.warning("Not enough arguments")
		verbose and print("Not enough arguments")
		exit(1)

#Main
verbose = False
dateFormate = "%Y-%m-%d %H:%M"
sys.argv.pop(0) #Remove Path
if len(sys.argv) < 1:
	printHelp()

if "-v" in sys.argv:
	verbose = True
	sys.argv.remove("-v")
if "--verbose" in sys.argv:
	verbose = True
	sys.argv.remove("--verbose")

for i, origItem in enumerate(sys.argv):
	item = origItem.lower()
	if (
		item == "-h" or
		item == "--help"
	):
		printHelp()
	elif item == "--stop-mode":
		stopMode()
	elif item == "--start-firefox":
		if i + 1 < len(sys.argv):
			startBrowser(sys.argv[i + 1])
		else:
			piScreenUtils.logging.warning("Not enough arguments")
			verbose and print("Not enough arguments")
	elif item == "--do-firefox-restart":
		restartBrowser()
	elif item == "--do-firefox-refresh":
		sendToCore({"cmd":4,"parameter":{"mode":1,"parameter":"refresh"}})
	elif item == "--start-vlc":
		if i + 1 < len(sys.argv):
			startVLC(sys.argv[i + 1])
		else:
			piScreenUtils.logging.warning("Not enough arguments")
			verbose and print("Not enough arguments")
	elif item == "--do-vlc-restart":
		sendToCore({"cmd":4,"parameter":{"mode":2,"parameter":"restart"}})
	elif item == "--do-vlc-toggle-play-pause":
		sendToCore({"cmd":4,"parameter":{"mode":2,"parameter":"play/pause"}})
	elif item == "--do-vlc-pause":
		sendToCore({"cmd":4,"parameter":{"mode":2,"parameter":"pause"}})
	elif item == "--do-vlc-play":
		sendToCore({"cmd":4,"parameter":{"mode":2,"parameter":"play"}})
	elif item == "--set-vlc-volume":
		if i + 1 < len(sys.argv):
			if piScreenUtils.isInt(sys.argv[i + 1]):
				sendToCore({"cmd":4,"parameter":{"mode":2,"parameter":f"volume{sys.argv[i + 1]}"}})
			else:
				piScreenUtils.logging.warning("Volume is no int")
				verbose and print("Volume is no int")
		else:
			piScreenUtils.logging.warning("Not enough arguments")
			verbose and print("Not enough arguments")
	elif item == "--start-impress":
		if i + 1 < len(sys.argv):
			startImpress(sys.argv[i + 1])
		else:
			piScreenUtils.logging.warning("Not enough arguments")
			verbose and print("Not enough arguments")
	elif item == "--do-impress-restart":
		restartImpress()
	elif item == "--do-reboot":
		reboot()
	elif item == "--do-shutdown":
		shutdown()
	elif item == "--set-desktop-configuration":
		configureDesktop()
	elif item == "--get-desktop-configuration":
		getDekstopConfig()
	elif item == "--get-status":
		print(getStatus())
	elif item == "--set-display":
		if "on" in sys.argv:
			screenOn()
		elif "off" in sys.argv:
			screenOff()
		else:
			verbose and print("You need to give the parameter 'on' or 'off'")
	elif item == "--set-display-input":
		screenSwitchInput()
	elif item == "--set-password":
		if i + 2 < len(sys.argv):
			if sys.argv[i + 2].lower() == "-f": #Check file Mode
				verbose and print("Set weblogin password with file")
				if i + 3 < len(sys.argv):
					if os.path.isfile(sys.argv[i + 3]):
						os.system(f"head -1 {sys.argv[i + 3]} | tr -d '\n' | sudo xargs -0 htpasswd -c -b /etc/apache2/.piScreen_htpasswd '{sys.argv[i + 1]}'")
						os.remove(sys.argv[i + 3])
					else:
						piScreenUtils.logging.error("Passwortfile dorsn't exist")
						verbose and print("Passwordfile doesn't exist")
				else:
					piScreenUtils.logging.error("No passwordfile specified")
					verbose and print("No passwordfile specified")
			else: #Check direct mode
				verbose and print("Set weblogin password with next parameter")
				os.system(f"sudo htpasswd -c -b /etc/apache2/.piScreen_htpasswd '{sys.argv[i + 1]}' '{sys.argv[i + 2]}'")
		else:
			piScreenUtils.logging.warning("Not enough arguments")
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
			piScreenUtils.logging.info(f"Set displayprotocol to {sys.argv[i + 1]}")
			sys.argv[i + 1] = sys.argv[i + 1].lower()
			if sys.argv[i + 1] == "cec" or sys.argv[i + 1] == "ddc" or sys.argv[i + 1] == "manually":
				sendToCore({"cmd":9,"parameter":sys.argv[i + 1]})
			else:
				piScreenUtils.logging.warning(f"{sys.argv[i + 1]} is no permitted protocol")
				verbose and print(f"{sys.argv[i + 1]} is no permitted protocol")
		else:
			piScreenUtils.logging.warning("Not enough arguments")
			verbose and print("Not enough arguments")
	elif item == "--get-display-protocol":
		returnValue = sendToCore({"cmd":14,"parameter":{"displayprotocol":1}})
		if returnValue and returnValue["code"] == 0: print(returnValue["displayprotocol"])
		else: piScreenUtils.logging.error("Unable to get display protocol")
	elif item == "--set-display-orientation":
		saveSettings = True
		orientation = None
		if "--no-save" in sys.argv:
			saveSettings = False
			sys.argv.remove("--no-save")
		if i + 1 < len(sys.argv):
			try:
				orientation = int(sys.argv[i + 1])
				sendToCore({"cmd":10,"parameter":{"orientation":orientation,"save":saveSettings}})
			except:
				piScreenUtils.logging.warning("Parameter is not int")
				verbose and print("Parameter is not int")
		else:
			piScreenUtils.logging.warning("Not enough arguments")
			verbose and print("Not enough arguments")
	elif item == "--get-display-orientation":
		if "--settings" in sys.argv:
			returnValue = sendToCore({"cmd":14,"parameter":{"displayorientationsettings":1}})
			if returnValue and returnValue["code"] == 0: print(returnValue["displayorientationsettings"])
			else: piScreenUtils.logging.error("Unable to get display orientation")
		else:
			returnValue = sendToCore({"cmd":14,"parameter":{"displayorientation":1}})
			if returnValue and returnValue["code"] == 0: print(returnValue["displayorientation"])
			else: piScreenUtils.logging.error("Unable to get display orientation")
	elif item == "--get-display-forcemode":
		returnValue = sendToCore({"cmd":14,"parameter":{"displayforcemode":1}})
		if returnValue and returnValue["code"] == 0: print(returnValue["displayforcemode"])
		else: piScreenUtils.logging.error("Unable to get display forcemode")
	elif item == "--set-display-forcemode":
		if i + 1 < len(sys.argv):
			if sys.argv[i + 1].lower() == "true": sendToCore({"cmd":12,"parameter":True})
			elif sys.argv[i + 1].lower() == "false": sendToCore({"cmd":12,"parameter":False})
			else: 
				piScreenUtils.logging.warning("No bool value")
				verbose and print("No bool value")
		else:
			piScreenUtils.logging.warning("Not enough arguments")
			verbose and print("Not enough arguments")
			exit(1)
	elif item == "--run-firstrun":
		piScreenUtils.logging.info("Send command for schedule firstrun")
		sendToCore({"cmd":6,"parameter":{}})
	elif item == "--run-lastcron":
		piScreenUtils.logging.info("Send command for schedule last cron")
		sendToCore({"cmd":7,"parameter":{}})
	elif item == "--run-command-manually":
		if i + 2 < len(sys.argv):
			if sys.argv[i + 1] == "--command":
				if piScreenUtils.isInt(sys.argv[i + 2]):
					command = {}
					command["type"] = 1
					command["command"] = int(sys.argv[i + 2])
					if i + 4 < len(sys.argv):
						if sys.argv[i + 3] == "--parameter":
							command["parameter"] = sys.argv[i + 4]
						else:
							piScreenUtils.logging.warning("Missing parameter flag")
							verbose and print("Missing parameter flag")
							exit(1)
					piScreenUtils.logging.info("Send command for manually command run")
					sendToCore({"cmd":8,"parameter":command})
				else:
					piScreenUtils.logging.warning("Command is no number")
					verbose and print("Command is no number")
					exit(1)
			else:
				piScreenUtils.logging.warning("Argument --command expected")
				verbose and print("Argument --command expected")
				exit(1)
		else:
			piScreenUtils.logging.warning("Not enough arguments")
			verbose and print("Not enough arguments")
			exit(1)
	elif item == "--run-commandset-manually":
		if i + 2 < len(sys.argv):
			if sys.argv[i + 1] == "--id":
				if piScreenUtils.isInt(sys.argv[i + 2]):
					piScreenUtils.logging.info("Send command for manually commandset run")
					sendToCore({"cmd":8,"parameter":{"type":2,"id":int(sys.argv[i + 2])}})
				else:
					piScreenUtils.logging.warning("ID is no number")
					verbose and print("ID is no number")
					exit(1)
			else:
				piScreenUtils.logging.warning("Argument --id expected")
				verbose and print("Argument --id expected")
				exit(1)
		else:
			piScreenUtils.logging.warning("Not enough arguments")
			verbose and print("Not enough arguments")
			exit(1)
	elif item == "--run-cron-manually":
		if i + 2 < len(sys.argv):
			if sys.argv[i + 1] == "--index":
				if piScreenUtils.isInt(sys.argv[i + 2]):
					piScreenUtils.logging.info("Send command for manually cron run")
					sendToCore({"cmd":8,"parameter":{"type":3,"index":int(sys.argv[i + 2])}})
				else:
					piScreenUtils.logging.warning("Index is no number")
					verbose and print("Index is no number")
					exit(1)
			else:
				piScreenUtils.logging.warning("Argument --index expected")
				verbose and print("Argument --index expected")
				exit(1)
		else:
			piScreenUtils.logging.warning("Not enough arguments")
			verbose and print("Not enough arguments")
			exit(1)
	elif item == "--add-cron-entry":
		addCron()
	elif item == "--update-cron-entry":
		updateCron()
	elif item == "--delete-cron-entry":
		if i + 2 < len(sys.argv):
			if sys.argv[i + 1] == "--index":
				if piScreenUtils.isInt(sys.argv[i + 2]):
					try:
						scheduleJson = loadSchedule()
						index = int(sys.argv[i + 2])
						if index < len(scheduleJson["cron"]) and index >= 0:
							del scheduleJson["cron"][index]
							scheduleFile = open(Paths.SCHEDULE, "w")
							scheduleFile.write(json.dumps(scheduleJson,indent=4))
							scheduleFile.close()
							piScreenUtils.logging.info("Changed schedule.json")
							verbose and print("Changed schedule.json")
						else:
							piScreenUtils.logging.warning("Index is bigger than count of cron entries")
							verbose and print("Index is bigger than count of cron entries")
							exit(1)
					except Exception as err:
						piScreenUtils.logging.error("Error with schedule.json")
						piScreenUtils.logging.debug(err)
						verbose and print("Error with schedule.json")
						exit(1)
				else:
					piScreenUtils.logging.warning("Index is no number")
					verbose and print("Index is no number")
					exit(1)
			else:
				piScreenUtils.logging.warning("Argument --index expected")
				verbose and print("Argument --index expected")
				exit(1)
		else:
			piScreenUtils.logging.warning("Not enough arguments")
			verbose and print("Not enough arguments")
			exit(1)
	elif item == "--add-commandset-entry":
		addCommandset(False)
	elif item == "--update-commandset-entry":
		updateCommandset()
	elif item == "--delete-commandset-entry":
		deleteCommandset()
	elif item == "--add-trigger-entry":
		addTrigger()
	elif item == "--update-trigger-entry":
		updateTrigger()
	elif item == "--delete-trigger-entry":
		if i + 2 < len(sys.argv):
			if sys.argv[i + 1] == "--index":
				if piScreenUtils.isInt(sys.argv[i + 2]):
					try:
						scheduleJson = loadSchedule()
						index = int(sys.argv[i + 2])
						if index < len(scheduleJson["trigger"]) and index >= 0:
							del scheduleJson["trigger"][index]
							scheduleFile = open(Paths.SCHEDULE, "w")
							scheduleFile.write(json.dumps(scheduleJson,indent=4))
							scheduleFile.close()
							piScreenUtils.logging.info("Changed schedule.json")
							verbose and print("Changed schedule.json")
						else:
							piScreenUtils.logging.warning("Index is bigger than count of tigger entries")
							verbose and print("Index is bigger than count of trigger entries")
							exit(1)
					except Exception as err:
						piScreenUtils.logging.error("Error with schedule.json")
						piScreenUtils.logging.debug(err)
						verbose and print("Error with schedule.json")
						exit(1)
				else:
					piScreenUtils.logging.warning("Index is no number")
					verbose and print("Index is no number")
					exit(1)
			else:
				piScreenUtils.logging.warning("Argument --index expected")
				verbose and print("Argument --index expected")
				exit(1)
		else:
			piScreenUtils.logging.warning("Not enough arguments")
			verbose and print("Not enough arguments")
			exit(1)
	elif item == "--do-write-log":
		if "--level" in sys.argv:
			index = sys.argv.index("--level") + 1
			if index + 1 < len(sys.argv):
				sys.argv[index] = sys.argv[index].lower()
				if sys.argv[index] == "debug":
					piScreenUtils.logging.debug(sys.argv[index + 1])
				elif sys.argv[index] == "info":
					piScreenUtils.logging.info(sys.argv[index + 1])
				elif sys.argv[index] == "warning":
					piScreenUtils.logging.warning(sys.argv[index + 1])
				elif sys.argv[index] == "error":
					piScreenUtils.logging.error(sys.argv[index + 1])
				elif sys.argv[index] == "critical":
					piScreenUtils.logging.critical(sys.argv[index + 1])
				else:
					piScreenUtils.logging.warning(f"{sys.argv[index]} is no known loglevel")
					verbose and print(f"{sys.argv[index]} is no known loglevel")
			else:
				piScreenUtils.logging.warning("There are not enough parameter")
				verbose and print("There are not enough parameter")
		else:
			piScreenUtils.logging.warning("Argument --level expected")
			verbose and print("Argument --level expected")
	elif item == "--set-language":
		if i + 1 < len(sys.argv):
			sendToCore({"cmd":13,"parameter":sys.argv[i + 1]})
		else:
			piScreenUtils.logging.warning("Not enough arguments")
	elif item == "--set-cron-ignore-timespan":
		index = sys.argv.index("--set-cron-ignore-timespan") + 1
		tmp = ""
		for i in range(index,len(sys.argv)):
			if tmp == "": tmp = sys.argv[i]
			else: tmp = tmp + " " + sys.argv[i]
		splitedString = tmp.split(" ")
		if len(splitedString) == 4:
			try:
				piScreenUtils.logging.info("Set cron ignore time")
				ignoreCronFrom = datetime.datetime.strptime(splitedString[0] + " " + splitedString[1],dateFormate)
				ignoreCronTo = datetime.datetime.strptime(splitedString[2] + " " + splitedString[3],dateFormate)
				try:
					scheduleJson = loadSchedule()
					scheduleJson["ignoreCronFrom"] = ignoreCronFrom.strftime(dateFormate)
					scheduleJson["ignoreCronTo"] = ignoreCronTo.strftime(dateFormate)
					scheduleFile = open(Paths.SCHEDULE, "w")
					scheduleFile.write(json.dumps(scheduleJson,indent=4))
					scheduleFile.close()
				except Exception as err:
					verbose and print("Unable to change schedule")
					piScreenUtils.logging.error("Unable to change schedule")
					piScreenUtils.logging.debug(err)
			except Exception as err:
				verbose and print(f"Datetime string not in right format: {dateFormate}")
				piScreenUtils.logging.error(f"Datetime string not in right format: {dateFormate}")
				piScreenUtils.logging.debug(err)
		elif splitedString[0] == "":
			try:
				piScreenUtils.logging.info("Delete cron ignore time")
				scheduleJson = loadSchedule()
				del scheduleJson["ignoreCronFrom"]
				del scheduleJson["ignoreCronTo"]
				scheduleFile = open(Paths.SCHEDULE, "w")
				scheduleFile.write(json.dumps(scheduleJson,indent=4))
				scheduleFile.close()
			except Exception as err:
				verbose and print("Unable to change schedule")
				piScreenUtils.logging.error("Unable to change schedule")
				piScreenUtils.logging.debug(err)
		else:
			verbose and print("Not enough arguments")
			piScreenUtils.logging.warning("Not enough arguments")
	elif item == "--stop-core":
		#Secret command to send stop message to piScreenCore.py
		if sendToCore({"cmd":1})["code"] == 0:
			verbose and print("Core will stop")
			piScreenUtils.logging.info("Core will stop")
		else:
			verbose and print("Core doesn't seem to respond")
			piScreenUtils.logging.info("Core doesn't seem to respond")
	elif item == "--set-display-resolution":
		if len(sys.argv) > 2:
			if piScreenUtils.isInt(sys.argv[1]) and piScreenUtils.isInt(sys.argv[2]):
				verbose and print(f"Set to {sys.argv[1]}x{sys.argv[2]}")
				piScreenUtils.logging.info(f"Set to {sys.argv[1]}x{sys.argv[2]}")
				sendToCore({"cmd":11,"parameter":{"width":sys.argv[1],"height":sys.argv[2]}})
			else:
				verbose and print("Parameter are no int")
				piScreenUtils.logging.warning("Parameter are no int")
		elif len(sys.argv) == 1:
			sendToCore({"cmd":11,"parameter":None})
		else:
			verbose and print("Not enough arguments")
			piScreenUtils.logging.warning("Not enough arguments")
	elif item == "--get-display-resolution":
		if "--settings" in sys.argv:
			returnValue = sendToCore({"cmd":14,"parameter":{"displayresolutionsettings":1}})
			if returnValue and returnValue["code"] == 0: print(returnValue["displayresolutionsettings"])
			else: piScreenUtils.logging.error("Unable to get display resolution")
		else:
			returnValue = sendToCore({"cmd":14,"parameter":{"displayresolution":1}})
			if returnValue and returnValue["code"] == 0: print(returnValue["displayresolution"])
			else: piScreenUtils.logging.error("Unable to get current display resolution")
