#!/usr/bin/python3
import os, json, sys, time, psutil, subprocess, threading, socket, vlc, piScreenUtils
from marionette_driver.marionette import Marionette

def checkIfProcessRunning(processName):
	for proc in psutil.process_iter():
		try:
			if processName.lower() in proc.name().lower():
				return True
		except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
			piScreenUtils.logging.critical("Unable to check if tasks are running")
	return False

def killAllSubprocesses():
	os.system("killall -q unclutter")
	os.system("killall -q piScreenDisplay")
	os.system("killall -q piScreenSchedule")
	os.system("killall -q firefox-esr")
	os.system("killall -q vlc")
	os.system("killall -q soffice.bin")

class firefoxHandler(threading.Thread):
	client = Marionette(host='127.0.0.1', port=2828)
	client.timeout = 2

	info = {"url":""}
	
	def __init__(self):
		threading.Thread.__init__(self)

	def run(self):
		lastParameter = ""
		while active:
			if mode == 1:
				piScreenUtils.logging.info("Running in firefox mode")
			while mode == 1 and active:
				if not checkIfProcessRunning("firefox-esr"):
					piScreenUtils.logging.info(f"Start firefox ({parameter})")
					os.system(f'firefox-esr --marionette -kiosk "{parameter}" &')
					lastParameter = parameter
					time.sleep(2)
				if checkIfProcessRunning("crashreporter"):
					piScreenUtils.logging.warning("There is a crashreporter open. It will be killed now")
					os.system("killall crashreporter")
				try:
					self.info["url"] = self.client.get_url()
					if lastParameter != parameter:
						lastParameter = parameter
						piScreenUtils.logging.info(f"Navigate browser to {parameter}")
						self.client.navigate(parameter)
				except:
					try:
						self.info["url"] = ""
						self.client.start_session()
					except:
						piScreenUtils.logging.error("Unable to create marionette session")
				time.sleep(1)
			if checkIfProcessRunning("firefox-esr"): os.system("killall firefox-esr")
			self.info["url"] = ""
			time.sleep(1)
		piScreenUtils.logging.info("End firefox handler")

class vlcHandler(threading.Thread):

	info = {}
	vlcPlayer = vlc.Instance('--video-wallpaper','--input-repeat=999999999')
	vlcMediaPlayer = vlcPlayer.media_player_new()
	vlcMedia = vlc.Media("")
	def __init__(self):
		threading.Thread.__init__(self)

	def run(self):
		lastParameter = ""
		while active:
			if mode == 2:
				piScreenUtils.logging.info("Running in vlc mode")
			while mode == 2 and active:
				try:
					if lastParameter != parameter:
						self.vlcMedia = vlc.Media(parameter)
						self.vlcMediaPlayer.set_media(self.vlcMedia)
						self.vlcMediaPlayer.play()
						lastParameter = parameter
				except:
					self.info = {}
					piScreenUtils.logging.error("Unable to control VLC")
				time.sleep(1)

			self.vlcMediaPlayer.stop()
			self.info = {}
			time.sleep(1)
		piScreenUtils.logging.info("End vlc handler")

class impressHandler(threading.Thread):
	info = {}

	def __init__(self):
		threading.Thread.__init__(self)

	def run(self):
		lastParameter = ""
		while active:
			if mode == 3: piScreenUtils.logging.info("Running in impress mode")
			while mode == 3 and active:
				if not checkIfProcessRunning("soffice.bin"):
					piScreenUtils.logging.info(f"Start Impress ({parameter})")
					os.system(f'soffice --nolockcheck --norestore --nologo --show "{parameter}" &')
					lastParameter = parameter
					time.sleep(10)
				if lastParameter != parameter:
					piScreenUtils.logging.info("Impress parameter has been changed")
					lastParameter = parameter
					if checkIfProcessRunning("soffice.bin"): os.system("killall soffice.bin")
					time.sleep(2)
				time.sleep(1)
			if checkIfProcessRunning("soffice.bin"): os.system("killall soffice.bin")
			self.info = {}
			time.sleep(1)
		piScreenUtils.logging.info("End impress handler")

class socketHandler(threading.Thread):
	s = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
	def __init__(self):
		threading.Thread.__init__(self)

	def run(self):
		self.s.bind((HOST,PORT))
		while active:
			bytesAddressPair = self.s.recvfrom(bufferSize)
			try:
				jsonData = json.loads(bytesAddressPair[0].decode("utf-8"))
				returnValue = cmdInterpreter(jsonData)
				self.s.sendto(str.encode(json.dumps(returnValue)),bytesAddressPair[1])
			except:
				piScreenUtils.logging.error("Unable to convert recieved command to json")
		piScreenUtils.logging.info("End socket listener")

def cmdInterpreter(data:dict) -> dict:
	global active
	global mode
	global parameter
	if "cmd" not in data:
		piScreenUtils.logging.error("Recived data has no cmd field in it")
		return {"code":2} #Package format is wrong
	if piScreenUtils.isInt(data["cmd"]) == False:
		piScreenUtils.logging.error("Recived cmd is no integer")
		return {"code":2} #Package format is wrong
	cmd = int(data["cmd"])
	returnValue = {"code":0,"cmd":cmd}
	if cmd == 1: #Exit
		piScreenUtils.logging.info("Stop core by command")
		active = False
		return returnValue
	elif cmd == 2: #Get Status
		return returnValue
	elif cmd == 3: #Change Mode
		if "parameter" not in data: 
			piScreenUtils.logging.error("Recived data has no needed parameter field in it")
			return {"code":2} #Package format is wrong
		if "mode" not in data["parameter"]:
			piScreenUtils.logging.error("Recived data has no needed mode field in parameter field")
			return {"code":2} #Package format is wrong
		if piScreenUtils.isInt(data["parameter"]["mode"]) == False:
			piScreenUtils.logging.error("Recived mode is no integer")
			return {"code":2} #Package format is wrong
		if "parameter" not in data["parameter"]:
			piScreenUtils.logging.error("Recived data has no needed parameter field in parameter field")
			return {"code":2} #Package format is wrong
		mode = int(data["parameter"]["mode"])
		parameter = data["parameter"]["parameter"]
		return returnValue
	else:
		piScreenUtils.logging.warning("Recived cmd is unknown")
		returnValue["code"] = 1
		return returnValue #Unkown cmd

HOST = "127.0.0.1"
PORT = 28888
bufferSize = 1024
active = True
mode = 0
parameter = None

if __name__ == "__main__":
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

	except ValueError as err:
		piScreenUtils.logging.critical(err)
		sys.exit(1)

	os.system("touch " + piScreenUtils.paths.scheduleActive)
	piScreenUtils.logging.info("Start subprocesses")
	killAllSubprocesses()
	os.system("unclutter -idle 5 &")
	os.system("./piScreenDisplay.py &")
	time.sleep(5)
	os.system("./piScreenSchedule.py &")

	piScreenUtils.logging.info("Start mode threads")
	firefoxMode = firefoxHandler()
	vlcMode = vlcHandler()
	impressMode = impressHandler()
	firefoxMode.start()
	vlcMode.start()
	impressMode.start()

	piScreenUtils.logging.info("Start udp communcation socket")
	sH = socketHandler()
	sH.start()

	piScreenUtils.logging.info("Start observation")
	while active:
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
		#createScreenshot
		try:
			os.system(f"scrot -z {piScreenUtils.paths.screenshot}.png")
			os.system(f"mv {piScreenUtils.paths.screenshot}.png {piScreenUtils.paths.screenshot}")
		except:
			piScreenUtils.logging.error("Error while creating screenshot")
		if not checkIfProcessRunning("piScreenDisplay"):
			piScreenUtils.logging.warning("piScreenDisplay.py skript is not running")
			os.system("./piScreenDisplay.py &")
		if not checkIfProcessRunning("piScreenSchedul"):
			piScreenUtils.logging.warning("piScreenSchedule.py skript is not running")
			os.system("./piScreenSchedule.py &")
		time.sleep(5)
	active = False
	killAllSubprocesses()