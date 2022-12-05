#!/usr/bin/python -u
def checkIfProcessRunning(processName):
	for proc in psutil.process_iter():
		try:
			if processName.lower() in proc.name().lower():
				return True
		except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
			pass
	return False

def isInt(s):
	try: 
		int(s)
		return True
	except ValueError:
		return False

print("Start piScreen")
print("Load modules")
import os, json, sys, time, psutil, subprocess

print("Set environment setting")
skriptPath = os.path.dirname(os.path.abspath(__file__))
os.chdir(skriptPath)
os.environ["DISPLAY"] = ":0"
ramdisk = "/media/ramdisk/"
piScreenModeFirefox = ramdisk + "piScreenModeFirefox"
piScreenModeVLC = ramdisk + "piScreenModeVLC"
piScreenDisplayOn = ramdisk + "piScreenDisplayOn"
piScreenDisplaySwitch = ramdisk + "piScreenDisplaySwitch"
piScreenDisplayCEC = ramdisk + "piScreenDisplayCEC"
piScreenDisplayDDC = ramdisk + "piScreenDisplayDDC"
piScreenScheduleActive = ramdisk + "piScreenScheduleActive"
piScreenSettings = "./settings.json"
piScreenSyscall = "./piScreenCmd.py"
piScreenScreenshotPath = ramdisk + "piScreenScreenshot.png"

print("Load settings")
try:
	conf = json.load(open(piScreenSettings))
	configModify = os.path.getmtime(piScreenSettings)
	#Next line is tmp
	conf = conf["settings"]
	if "display" in conf:
		if "protocol" in conf["display"]:
			piScreenDisplayProtocol = conf["display"]["protocol"]
			if os.path.exists(piScreenDisplayCEC): os.remove(piScreenDisplayCEC)
			if os.path.exists(piScreenDisplayDDC): os.remove(piScreenDisplayDDC)
			if piScreenDisplayProtocol == "cec":
				os.system(f"touch {piScreenDisplayCEC}")
			elif piScreenDisplayProtocol == "ddc":
				os.system(f"touch {piScreenDisplayDDC}")

except ValueError as err:
	print(err)
	sys.exit(1)

os.system("touch " + piScreenScheduleActive)

print("Start subprocesses")
os.system("killall -q unclutter")
os.system("unclutter -idle 5 &")
os.system("killall -q piScreenDisplay")
os.system("./piScreenDisplay.sh &")
os.system("killall -q piScreenSchedule")
time.sleep(5)
os.system("./piScreenSchedule.py &")

print("Start observation")
while True:
	#Check in which mode we are
	if os.path.exists(piScreenModeFirefox):
		if not checkIfProcessRunning("firefox-esr"):
			parameter = open(piScreenModeFirefox,"r").read()
			os.system(f'firefox-esr -kiosk "{parameter}" &')
	if os.path.exists(piScreenModeVLC):
		pass
	#check if settings has changed
	if configModify != os.path.getmtime(piScreenSettings):
		try:
			print("settings.json seems to be changed")
			conf = json.load(open(piScreenSettings))
			#Next line is tmp
			conf = conf["settings"]
			configModify = os.path.getmtime(piScreenSettings)
		except:
			print("settings.json seems to be damaged")
	#check screen orientation
	if "orientation" in conf["display"]:
		if isInt(conf["display"]["orientation"]):
			if subprocess.check_output(f"{piScreenSyscall} --get-display-orientation",shell=True).decode("utf-8").replace("\n","") == str(conf['display']['orientation']):
				pass
			else:
				os.system(f"{piScreenSyscall} --set-display-orientation --no-save {conf['display']['orientation']}")
	#createScreenshot
	os.system(f"scrot -z {piScreenScreenshotPath}.png")
	os.system(f"mv {piScreenScreenshotPath}.png {piScreenScreenshotPath}")
	time.sleep(5)