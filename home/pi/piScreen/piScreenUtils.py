#!/usr/bin/python3
import logging, __main__, os

class paths:
	ramdisk = "/media/ramdisk/"
	settings = "./settings.json"
	schedule = "./schedule.json"
	manifest = "./manifest.json"
	syscall = "./piScreenCmd.py"
	screenshot = f"{ramdisk}piScreenScreenshot.png"
	displayStatus = f"{ramdisk}piScreenDisplay.txt"
	displayOff = f"{ramdisk}piScreenDisplayOff"
	displayOn = f"{ramdisk}piScreenDisplayOn"
	displayStandby = f"{ramdisk}piScreenDisplayStandby"
	displaySwitchChannel = f"{ramdisk}piScreenDisplaySwitch"
	displayCEC = f"{ramdisk}piScreenDisplayCEC"
	displayDDC = f"{ramdisk}piScreenDisplayDDC"
	displayMANUALLY = f"{ramdisk}piScreenDisplayMANUALLY"
	modeFirefox = f"{ramdisk}piScreenModeFirefox"
	modeVLC = f"{ramdisk}piScreenModeVLC"
	modeImpress = f"{ramdisk}piScreenModeImpress"
	scheduleActive = f"{ramdisk}piScreenScheduleActive"
	scheduleDoFirstRun = f"{ramdisk}piScreenScheduleFirstRun"
	scheduleDoLastCron = f"{ramdisk}piScreenScheduleLastCron"
	scheduleDoManually = f"{ramdisk}piScreenScheduleManually"
	log = f"{ramdisk}piScreen.log"

def isInt(s):
	if s == None: return False
	try: 
		int(s)
		return True
	except ValueError:
		return False

def isFloat(s):
	if s == None: return False
	try:
		float(s)
		return True
	except ValueError:
		return False

os.umask(0) #Needed for execut with www-data
if "__file__" in __main__.__dir__():
	mainFileName = __main__.__file__[-(len(__main__.__file__)-__main__.__file__.rindex("/"))+1:]
else:
	mainFileName = "NoScript"
logging.basicConfig(filename=paths.log, format=f"%(asctime)s [%(levelname)s] ({mainFileName}) %(funcName)s(%(lineno)d) | %(message)s", level="INFO")