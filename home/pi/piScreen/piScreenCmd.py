#!/usr/bin/python
import json
import sys
import os

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
		pass
	elif item == "--shutdown":
		pass




#print (settingsJson["settings"]["appearence"])