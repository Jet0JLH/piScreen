#!/usr/bin/python
import json, sys, os, time

def printHelp():
	print("This tool is desigend for syscalls.\nSo you have one script, which controlls everything and get every info about.")
	print("""
-h or --help
	Show this information
-v or --verbose
	Shows detailed informations during execution
	It have to ste befor other parameters!
--start-browser
	Starts the Browser
--stop-browser
	Stops the Browser
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
--set-website <website>
	Changes the website
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
	Sudo rights are requiered!""")

def checkForRootPrivileges():
	if os.geteuid() != 0:
		verbose and print("Please run this function with root privileges.")
		return False
	return True

def loadSettings():
	return json.load(open(f"{os.path.dirname(__file__)}/settings.json"))

def loadMainifest():
	return json.load(open(f"{os.path.dirname(__file__)}/manifest.json"))

def startBrowser():
	verbose and print("Load settings")
	settingsJson = loadSettings()
	verbose and print("Start browser")
	os.environ['DISPLAY'] = ":0"
	os.system(f'firefox -kiosk -private-window {settingsJson["settings"]["website"]}')
	verbose and print("Browser started")

def stopBrowser():
	verbose and print("Stop browser")
	os.system("kill $(pgrep -x firefox-esr)")
	verbose and print("Browser stopped")

def reboot():
	verbose and print("Reboot system")
	os.system("reboot")

def shutdown():
	verbose and print("Shutdown system")
	os.system("poweroff")

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
	return '{"uptime":{"secs":%d,"mins":%d,"hours":%d,"days":%d},"displayState":"%s","cpuTemp":%d,"cpuLoad":%d,"ramTotal":%d,"ramUsed":%d,"display":{"standbySet":%s,"onSet":%s}}' % (upSecound,upMinutes,upHours,upDays,displayState,cpuTemp,cpuLoad,ramTotal,ramUsed,str(os.path.isfile("/media/ramdisk/piScreenDisplayStandby")).lower(),str(os.path.isfile("/media/ramdisk/piScreenDisplayOn")).lower())

def setWebsite(website):
	verbose and print(f"Write {website} as website in settings.json")
	settingsJson = loadSettings()
	settingsJson["settings"]["website"] = website
	settingsFile = open(f"{os.path.dirname(__file__)}/settings.json", "w")
	settingsFile.write(json.dumps(settingsJson,indent=4))
	settingsFile.close()
	
def getWebsite():
	settingsJson = loadSettings()
	print(settingsJson["settings"]["website"])

def checkUpdate(draft,prerelease,silent):
	manifest = loadMainifest()
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
			if prerelease:
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
			updateProcess = subprocess.Popen([f"{downloadDir}/install/install.py", "--update"])
			updateProcess.wait()
			updateProcess.returncode != 0 and verbose and print("Something went wrong during installation")
		else:
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

verbose = False
sys.argv.pop(0) #Remove Path
if len(sys.argv) < 1:
	printHelp()

for i,origItem in enumerate(sys.argv):
	item = origItem.lower()
	if (
		item == "-v" or
		item == "--verbose"
	):
		verbose = True
	elif (
		item == "-h" or
		item == "--help"
	):
		printHelp()
	elif item == "--start-browser":
		startBrowser()
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
	elif item == "--set-website":
		if i + 1 < len(sys.argv):
			setWebsite(sys.argv[i + 1])
		else:
			verbose and print("Not enough arguments")
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
						verbose and print("Passwordfile dosen't exist")
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
