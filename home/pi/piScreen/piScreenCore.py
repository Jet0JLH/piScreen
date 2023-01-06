#!/usr/bin/python3 -u
import os, json, sys, time, psutil, subprocess, piScreenUtils
def checkIfProcessRunning(processName):
	for proc in psutil.process_iter():
		try:
			if processName.lower() in proc.name().lower():
				return True
		except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
			piScreenUtils.logging.critical("Unable to check if tasks are running")
	return False

piScreenUtils.logging.info("Start piScreen")
piScreenUtils.logging.debug("Set environment setting")
skriptPath = os.path.dirname(os.path.abspath(__file__))
os.chdir(skriptPath)
os.environ["DISPLAY"] = ":0"

piScreenUtils.logging.info("Load settings")
try:
	conf = json.load(open(piScreenUtils.paths.settings))
	configModify = os.path.getmtime(piScreenUtils.paths.settings)
	#Next line is tmp
	conf = conf["settings"]
	if "display" in conf:
		if "protocol" in conf["display"]:
			piScreenDisplayProtocol = conf["display"]["protocol"]
			if os.path.exists(piScreenUtils.paths.displayCEC): piScreenUtils.logging.debug("Remove old CEC file") ; os.remove(piScreenUtils.paths.displayCEC)
			if os.path.exists(piScreenUtils.paths.displayDDC): piScreenUtils.logging.debug("Remove old DDC file") ; os.remove(piScreenUtils.paths.displayDDC)
			if os.path.exists(piScreenUtils.paths.displayMANUALLY): piScreenUtils.logging.debug("Remove old MANUALLY file") ; os.remove(piScreenUtils.paths.displayMANUALLY)
			if piScreenDisplayProtocol == "cec": piScreenUtils.logging.info("Create file for cec mode") ; os.system(f"touch {piScreenUtils.paths.displayCEC}")
			elif piScreenDisplayProtocol == "ddc": piScreenUtils.logging.info("Create file for ddc mode") ; os.system(f"touch {piScreenUtils.paths.displayDDC}")
			elif piScreenDisplayProtocol == "manually": piScreenUtils.logging.info("Create file for manually mode") ; os.system(f"touch {piScreenUtils.paths.displayMANUALLY}")

except ValueError as err:
	piScreenUtils.logging.critical(err)
	sys.exit(1)

os.system("touch " + piScreenUtils.paths.scheduleActive)

piScreenUtils.logging.info("Start subprocesses")
os.system("killall -q unclutter")
os.system("unclutter -idle 5 &")
os.system("killall -q piScreenDisplay")
os.system("./piScreenDisplay.sh &")
os.system("killall -q piScreenSchedule")
time.sleep(5)
os.system("./piScreenSchedule.py &")

piScreenUtils.logging.info("Start observation")
modeFileModify = 0
while True:
	#Check in which mode we are
	if os.path.exists(piScreenUtils.paths.modeFirefox):
		if not checkIfProcessRunning("firefox-esr"):
			piScreenUtils.logging.info("Load firefox parameter")
			parameter = open(piScreenUtils.paths.modeFirefox,"r").read()
			piScreenUtils.logging.info(f"Start firefox ({parameter})")
			modeFileModify = os.path.getmtime(piScreenUtils.paths.modeFirefox)
			os.system(f'firefox-esr -kiosk "{parameter}" &')
		else:
			if modeFileModify != os.path.getmtime(piScreenUtils.paths.modeFirefox):
				piScreenUtils.logging.info("Firefox parameter has changed")
				modeFileModify = os.path.getmtime(piScreenUtils.paths.modeFirefox)
	elif os.path.exists(piScreenUtils.paths.modeVLC):
		if not checkIfProcessRunning("vlc"):
			piScreenUtils.logging.info("Load VLC parameter")
			parameter = open(piScreenUtils.paths.modeVLC,"r").read()
			piScreenUtils.logging.info(f"Start VLC ({parameter})")
			modeFileModify = os.path.getmtime(piScreenUtils.paths.modeVLC)
			os.system(f'vlc --no-qt-privacy-ask -L --no-qt-name-in-title --no-video-title-show --no-qt-fs-controller --rc-host=127.0.0.1:9999 --intf=rc --video-wallpaper "{parameter}" &')
		else:
			if modeFileModify != os.path.getmtime(piScreenUtils.paths.modeVLC):
				piScreenUtils.logging.info("VLC parameter has changed")
				modeFileModify = os.path.getmtime(piScreenUtils.paths.modeVLC)
	elif os.path.exists(piScreenUtils.paths.modeImpress):
		if not checkIfProcessRunning("soffice.bin"):
			piScreenUtils.logging.info("Load impress parameter")
			parameter = open(piScreenUtils.paths.modeImpress,"r").read()
			piScreenUtils.logging.info(f"Start impress ({parameter})")
			modeFileModify = os.path.getmtime(piScreenUtils.paths.modeImpress)
			os.system(f'soffice --nolockcheck --norestore --nologo --show "{parameter}" &')
		else:
			if modeFileModify != os.path.getmtime(piScreenUtils.paths.modeImpress):
				piScreenUtils.logging.info("Impress parameter has changed")
				modeFileModify = os.path.getmtime(piScreenUtils.paths.modeImpress)
	#check if settings has changed
	if configModify != os.path.getmtime(piScreenUtils.paths.settings):
		try:
			piScreenUtils.logging.info("settings.json seems to be changed")
			conf = json.load(open(piScreenUtils.paths.settings))
			#Next line is tmp
			conf = conf["settings"]
			configModify = os.path.getmtime(piScreenUtils.paths.settings)
		except:
			piScreenUtils.logging.error("settings.json seems to be damaged")
	#check screen orientation
	if "orientation" in conf["display"]:
		if piScreenUtils.isInt(conf["display"]["orientation"]):
			if subprocess.check_output(f"{piScreenUtils.paths.syscall} --get-display-orientation",shell=True).decode("utf-8").replace("\n","") != str(conf['display']['orientation']):
				piScreenUtils.logging.info("Change display orientation")
				os.system(f"{piScreenUtils.paths.syscall} --set-display-orientation --no-save {conf['display']['orientation']}")
	#createScreenshot
	try:
		os.system(f"scrot -z {piScreenUtils.paths.screenshot}.png")
		os.system(f"mv {piScreenUtils.paths.screenshot}.png {piScreenUtils.paths.screenshot}")
	except:
		piScreenUtils.logging.error("Error while creating screenshot")
	time.sleep(5)