#!/usr/bin/python3
import logging, logging.handlers, __main__, os
from enum import StrEnum


class Paths(StrEnum):
	RAMDISK = "/media/ramdisk/"
	SOFTWARE_DIR = "/home/pi/piScreen/"
	WWW_DIR = "/srv/piScreen/"
	SETTINGS = f"{SOFTWARE_DIR}settings.json"
	SCHEDULE = f"{SOFTWARE_DIR}schedule.json"
	MANIFEST = f"{SOFTWARE_DIR}manifest.json"
	SYSCALL = f"{SOFTWARE_DIR}piScreenCmd.py"
	SCREENSHOT = f"{RAMDISK}piScreenScreenshot.jpg"
	SCREENSHOT_THUMBNAIL = f"{RAMDISK}piScreenScreenshot-thumb.jpg"
	LOG = f"{RAMDISK}piScreen.log"
	LOCK_CORE = f"{RAMDISK}piScreenCore.lock"


class paths:
	ramdisk = "/media/ramdisk/"
	softwareDir = "/home/pi/piScreen/"
	wwwDir = "/srv/piScreen/"
	settings = f"{softwareDir}settings.json"
	schedule = f"{softwareDir}schedule.json"
	manifest = f"{softwareDir}manifest.json"
	syscall = f"{softwareDir}piScreenCmd.py"
	screenshot = f"{ramdisk}piScreenScreenshot.jpg"
	screenshotThumbnail = f"{ramdisk}piScreenScreenshot-thumb.jpg"
	log = f"{ramdisk}piScreen.log"
	lockCore = f"{ramdisk}piScreenCore.lock"

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
if os.path.exists(Paths.RAMDISK):
	logging.basicConfig(
	format=f"%(asctime)s [%(levelname)s] ({mainFileName}) %(funcName)s(%(lineno)d) | %(message)s",
	level="INFO",
	encoding="utf-8",
	handlers=[logging.handlers.RotatingFileHandler(filename=Paths.LOG,mode="a",maxBytes=5242880,backupCount=2,encoding="utf-8",delay=0)])
else:
    logging.basicConfig(
	format=f"%(asctime)s [%(levelname)s] ({mainFileName}) %(funcName)s(%(lineno)d) | %(message)s",
	level="INFO",
	encoding="utf-8",
	handlers=[logging.handlers.RotatingFileHandler(filename="/tmp/piScreen.log",mode="a",maxBytes=5242880,backupCount=2,encoding="utf-8",delay=0)])