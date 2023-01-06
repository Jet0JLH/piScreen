#!/usr/bin/python3 -u
import os, json, sys, time, psutil, subprocess, piScreenUtils
def checkIfProcessRunning(processName):
	for proc in psutil.process_iter():
		try:
			if processName.lower() in proc.name().lower():
				return True
		except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
			pass
	return False

print("Start piScreen")
print("Set environment setting")
skriptPath = os.path.dirname(os.path.abspath(__file__))
os.chdir(skriptPath)
os.environ["DISPLAY"] = ":0"

print("Load settings")
try:
	conf = json.load(open(piScreenUtils.paths.settings))
	configModify = os.path.getmtime(piScreenUtils.paths.settings)
	#Next line is tmp
	conf = conf["settings"]
	if "display" in conf:
		if "protocol" in conf["display"]:
			piScreenDisplayProtocol = conf["display"]["protocol"]
			if os.path.exists(piScreenUtils.paths.displayCEC): os.remove(piScreenUtils.paths.displayCEC)
			if os.path.exists(piScreenUtils.paths.displayDDC): os.remove(piScreenUtils.paths.displayDDC)
			if os.path.exists(piScreenUtils.paths.displayMANUALLY): os.remove(piScreenUtils.paths.displayMANUALLY)
			if piScreenDisplayProtocol == "cec":
				os.system(f"touch {piScreenUtils.paths.displayCEC}")
			elif piScreenDisplayProtocol == "ddc":
				os.system(f"touch {piScreenUtils.paths.displayDDC}")
			elif piScreenDisplayProtocol == "manually":
				os.system(f"touch {piScreenUtils.paths.displayMANUALLY}")

except ValueError as err:
	print(err)
	sys.exit(1)

os.system("touch " + piScreenUtils.paths.scheduleActive)

print("Start subprocesses")
os.system("killall -q unclutter")
os.system("unclutter -idle 5 &")
os.system("killall -q piScreenDisplay")
os.system("./piScreenDisplay.sh &")
os.system("killall -q piScreenSchedule")
time.sleep(5)
os.system("./piScreenSchedule.py &")

print("Start observation")
modeFileModify = 0
while True:
	#Check in which mode we are
	if os.path.exists(piScreenUtils.paths.modeFirefox):
		if not checkIfProcessRunning("firefox-esr"):
			parameter = open(piScreenUtils.paths.modeFirefox,"r").read()
			modeFileModify = os.path.getmtime(piScreenUtils.paths.modeFirefox)
			os.system(f'firefox-esr -kiosk "{parameter}" &')
		else:
			if modeFileModify != os.path.getmtime(piScreenUtils.paths.modeFirefox):
				modeFileModify = os.path.getmtime(piScreenUtils.paths.modeFirefox)
	elif os.path.exists(piScreenUtils.paths.modeVLC):
		if not checkIfProcessRunning("vlc"):
			parameter = open(piScreenUtils.paths.modeVLC,"r").read()
			modeFileModify = os.path.getmtime(piScreenUtils.paths.modeVLC)
			os.system(f'vlc --no-qt-privacy-ask -L --no-qt-name-in-title --no-video-title-show --no-qt-fs-controller --rc-host=127.0.0.1:9999 --intf=rc --video-wallpaper "{parameter}" &')
		else:
			if modeFileModify != os.path.getmtime(piScreenUtils.paths.modeVLC):
				modeFileModify = os.path.getmtime(piScreenUtils.paths.modeVLC)
	elif os.path.exists(piScreenUtils.paths.modeImpress):
		if not checkIfProcessRunning("soffice.bin"):
			parameter = open(piScreenUtils.paths.modeImpress,"r").read()
			fileModmodeFileModifyify = os.path.getmtime(piScreenUtils.paths.modeImpress)
			os.system(f'soffice --nolockcheck --norestore --nologo --show "{parameter}" &')
		else:
			if modeFileModify != os.path.getmtime(piScreenUtils.paths.modeImpress):
				modeFileModify = os.path.getmtime(piScreenUtils.paths.modeImpress)
	#check if settings has changed
	if configModify != os.path.getmtime(piScreenUtils.paths.settings):
		try:
			print("settings.json seems to be changed")
			conf = json.load(open(piScreenUtils.paths.settings))
			#Next line is tmp
			conf = conf["settings"]
			configModify = os.path.getmtime(piScreenUtils.paths.settings)
		except:
			print("settings.json seems to be damaged")
	#check screen orientation
	if "orientation" in conf["display"]:
		if piScreenUtils.isInt(conf["display"]["orientation"]):
			if subprocess.check_output(f"{piScreenUtils.paths.syscall} --get-display-orientation",shell=True).decode("utf-8").replace("\n","") == str(conf['display']['orientation']):
				pass
			else:
				os.system(f"{piScreenUtils.paths.syscall} --set-display-orientation --no-save {conf['display']['orientation']}")
	#createScreenshot
	os.system(f"scrot -z {piScreenUtils.paths.screenshot}.png")
	os.system(f"mv {piScreenUtils.paths.screenshot}.png {piScreenUtils.paths.screenshot}")
	time.sleep(5)