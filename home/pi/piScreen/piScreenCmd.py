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
	""")

def loadSettings():
	return json.load(open(f"{os.path.dirname(__file__)}/settings.json"))

def startBrowser():
	verbose and print("Load settings")
	settingsJson = json.load(open(f"{os.path.dirname(__file__)}/settings.json"))
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

def getStatus():
	import psutil
	verbose and print("Collect data")
	cpuLoad = round(psutil.getloadavg()[0] / psutil.cpu_count() * 100,2)
	ramTotal = round(psutil.virtual_memory().total / 1024)
	ramUsed = round(ramTotal - psutil.virtual_memory().available / 1024)
	upTime = time.time() - psutil.boot_time()
	upSecound = round(upTime % 60)
	upMinutes = round((upTime / 60) % 60)
	upHours = round((upTime / 60 / 60) % 24)
	upDays = round(upTime / 60 / 60 / 24)
	displayState = open("/media/ramdisk/piScreenDisplay.txt","r").read().strip()
	cpuTemp = round(psutil.sensors_temperatures()["cpu_thermal"][0].current * 1000)
	return '{"uptime":{"secs":%d,"mins":%d,"hours":%d,"days":%d},"displayState":"%s","cpuTemp":%d,"cpuLoad":%d,"ramTotal":%d,"ramUsed":%d,"display":{"standbySet":%s,"onSet":%s}}' % (upSecound,upMinutes,upHours,upDays,displayState,cpuTemp,cpuLoad,ramTotal,ramUsed,str(os.path.isfile("/media/ramdisk/piScreenDisplayStandby")).lower(),str(os.path.isfile("/media/ramdisk/piScreenDisplayOn")).lower())

verbose = False
sys.argv.pop(0) #Remove Path
if len(sys.argv) < 1:
	printHelp()

for item in sys.argv:
	item = item.lower()
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