#!/usr/bin/python
import json
import sys
import os
import time

def printHelp():
	print("This tool is desigend for syscalls.\nSo you have one script, which controlls everything and get every info about.")
	print("""
-h or --help
	Show this information
-v or --verbose
	Shows detailed informations during execution
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
--set-website [website]
	Changes the website
--get-website
	Get the current in settings configured website
--check-update
	Check for updates
""")

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

def checkUpdates():
    manifest = loadMainifest()
    print(f"Current version {manifest['version']['major']}.{manifest['version']['minor']}.{manifest['version']['patch']}")

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
	elif item == "--check-updates":
		checkUpdates()