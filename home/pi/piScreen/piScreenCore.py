#!/usr/bin/python3
import os, json, sys, time, psutil, subprocess, threading, socket, vlc, fcntl, piScreenUtils
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
	os.system("killall -q soffice.bin")

class firefoxHandler(threading.Thread):
	client = Marionette(host='127.0.0.1', port=2828, socket_timeout=20)

	info = {}
	actions = []
	
	def __init__(self):
		threading.Thread.__init__(self)

	def run(self):
		while active:
			if mode == 1: piScreenUtils.logging.info("Running in firefox mode") ; lastParameter = ""
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
					for item in self.actions:
						if item == "refresh": piScreenUtils.logging.info("Refresh firefox") ; self.client.refresh()
					self.actions.clear()
					if lastParameter != parameter:
						lastParameter = parameter
						piScreenUtils.logging.info(f"Navigate browser to {parameter}")
						self.client.navigate(parameter)
				except:
					try:
						self.info = {}
						self.client.delete_session()
						self.client.start_session(timeout=2)
					except:
						piScreenUtils.logging.error("Unable to create marionette session")
				time.sleep(1)
			if checkIfProcessRunning("firefox-esr"): os.system("killall firefox-esr")
			self.info = {}
			time.sleep(1)
		piScreenUtils.logging.info("End firefox handler")

class vlcHandler(threading.Thread):

	info = {}
	actions = []
	vlcPlayer = vlc.Instance('--video-wallpaper','--input-repeat=999999999')
	vlcMediaPlayer = vlcPlayer.media_player_new()
	vlcMedia = vlc.Media("")
	def __init__(self):
		threading.Thread.__init__(self)

	def run(self):
		while active:
			if mode == 2: piScreenUtils.logging.info("Running in vlc mode") ; lastParameter = ""
			while mode == 2 and active:
				try:
					if lastParameter != parameter:
						self.vlcMedia = vlc.Media(parameter)
						self.vlcMediaPlayer.set_media(self.vlcMedia)
						self.vlcMediaPlayer.play()
						lastParameter = parameter
					self.info["source"] = self.vlcMedia.get_mrl()
					self.info["state"] = str(self.vlcMediaPlayer.get_state())
					self.info["time"] = self.vlcMediaPlayer.get_time()
					self.info["length"] = self.vlcMediaPlayer.get_length()
					for item in self.actions:
						if item == "play": piScreenUtils.logging.info("Play VLC") ; self.vlcMediaPlayer.play()
						elif item == "play/pause": piScreenUtils.logging.info("Play / Pause VLC") ; self.vlcMediaPlayer.pause()
						elif item == "pause": piScreenUtils.logging.info("Pause VLC") ; self.vlcMediaPlayer.set_pause(1)
						elif item == "restart": piScreenUtils.logging.info("Restart VLC") ; self.vlcMediaPlayer.set_position(0)
					self.actions.clear()
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
	actions = []

	def __init__(self):
		threading.Thread.__init__(self)

	def run(self):
		while active:
			if mode == 3: piScreenUtils.logging.info("Running in impress mode") ; lastParameter = ""
			while mode == 3 and active:
				if not checkIfProcessRunning("soffice.bin"):
					piScreenUtils.logging.info(f"Start Impress ({parameter})")
					os.system(f'soffice --nolockcheck --norestore --nologo --show "{parameter}" &')
					lastParameter = parameter
					self.info["file"] = parameter
					time.sleep(10)
				if lastParameter != parameter:
					piScreenUtils.logging.info("Impress parameter has been changed")
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
	global status
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
		returnValue["data"] = status
		return returnValue
	elif cmd == 3 or cmd == 4: #Change mode and configure mode
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
		if cmd == 3:
			mode = int(data["parameter"]["mode"])
			parameter = data["parameter"]["parameter"]
			return returnValue
		elif cmd == 4:
			if int(data["parameter"]["mode"]) == mode:
				if mode == 1: #Firefox
					firefoxMode.actions.append(data["parameter"]["parameter"])
				elif mode == 2: #VLC
					vlcMode.actions.append(data["parameter"]["parameter"])
				elif mode == 3: #Impress
					impressMode.actions.append(data["parameter"]["parameter"])
			else:
				return {"code":3} #Wrong mode

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
status = {}

if __name__ == "__main__":
	piScreenUtils.logging.info("Start piScreen")
	try:
		lockFile = open(piScreenUtils.paths.lockCore,"w")
		fcntl.lockf(lockFile, fcntl.LOCK_EX | fcntl.LOCK_NB)
	except IOError:
		piScreenUtils.logging.critical("There is a piScreenCore instance already running")
		exit(1)
	piScreenUtils.logging.debug("Set environment setting")
	skriptPath = os.path.dirname(os.path.abspath(__file__))
	os.chdir(skriptPath)
	os.environ["DISPLAY"] = ":0"

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

	os.system("touch " + piScreenUtils.paths.scheduleActive)
	piScreenUtils.logging.info("Start subprocesses")
	killAllSubprocesses()
	os.system("unclutter -idle 5 &")
	os.system("./piScreenDisplay.py &")
	time.sleep(5)
	os.system("./piScreenSchedule.py &")

	piScreenUtils.logging.info("Start observation")
	while active:
		#check if threads active
		if not firefoxMode.is_alive():
			piScreenUtils.logging.critical("Firefox handler thread is down!")
			firefoxMode.run()
		if not vlcMode.is_alive():
			piScreenUtils.logging.critical("VLC handler thread is down!")
			vlcMode.run()
		if not impressMode.is_alive():
			piScreenUtils.logging.critical("Impress handler thread is down!")
			impressMode.run()
		if not sH.is_alive():
			piScreenUtils.logging.critical("Socket handler thread is down!")
			sH.run()
			
		#readStatus
		upTime = time.time() - psutil.boot_time()
		status["cpuLoad"] = round(psutil.getloadavg()[0] / psutil.cpu_count() * 100,2)
		status["ramTotal"] = round(psutil.virtual_memory().total / 1024)
		status["ramUsed"] = round(status["ramTotal"] - psutil.virtual_memory().available / 1024)
		status["cpuTemp"] = round(psutil.sensors_temperatures()["cpu_thermal"][0].current * 1000)
		if os.path.isfile(piScreenUtils.paths.screenshot):
			status["screenshotTime"] = os.path.getctime(piScreenUtils.paths.screenshot)
		status["uptime"] = {}
		status["uptime"]["secs"] = int(upTime % 60)
		status["uptime"]["mins"] = int((upTime / 60) % 60)
		status["uptime"]["hours"] = int((upTime / 60 / 60) % 24)
		status["uptime"]["days"] = int(upTime / 60 / 60 / 24)
		if os.path.exists(piScreenUtils.paths.displayStatus): status["displayState"] = open(piScreenUtils.paths.displayStatus,"r").read().strip()
		status["display"] = {}
		status["display"]["standbySet"] = os.path.isfile(piScreenUtils.paths.displayStandby)
		status["display"]["onSet"] = os.path.isfile(piScreenUtils.paths.displayOn)
		status["modeInfo"] = {}
		status["modeInfo"]["mode"] = mode
		if mode == 1:
			status["modeInfo"]["info"] = firefoxMode.info
		elif mode == 2:
			status["modeInfo"]["info"] = vlcMode.info
		elif mode == 3:
			status["modeInfo"]["info"] = impressMode.info

		#createScreenshot
		try:
			os.system(f"scrot -z -o -t 50 {piScreenUtils.paths.screenshot}.jpg")
			os.system(f"mv {piScreenUtils.paths.screenshot}.jpg {piScreenUtils.paths.screenshot}")
			os.system(f"mv {piScreenUtils.paths.screenshot}-thumb.jpg {piScreenUtils.paths.screenshotThumbnail}")
		except:
			piScreenUtils.logging.error("Error while creating screenshot")
		if not checkIfProcessRunning("piScreenDisplay"):
			piScreenUtils.logging.warning("piScreenDisplay.py skript is not running")
			os.system("./piScreenDisplay.py &")
		if not checkIfProcessRunning("piScreenSchedul"):
			piScreenUtils.logging.warning("piScreenSchedule.py skript is not running")
			os.system("./piScreenSchedule.py &")
		time.sleep(5)

	piScreenUtils.logging.info("Stop core")
	active = False
	killAllSubprocesses()
	os.unlink(piScreenUtils.paths.lockCore)