#!/usr/bin/python3

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