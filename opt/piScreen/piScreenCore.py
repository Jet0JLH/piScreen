#!/opt/piScreen/env/bin/python
import piScreenUtils
import os, subprocess, copy, json, datetime, threading, time, socket, psutil, vlc, re
from marionette_driver.marionette import Marionette

###############
### Classes ###
###############

class JsonData:
	def loadFile(self):
		if not os.path.exists(self.path): piScreenUtils.logging.error(f"Unable to find {self.path}") ; return
		try:
			piScreenUtils.logging.debug(f"Load JSON from {self.path}")
			self.file = json.load(open(self.path))
			self.origFile = copy.deepcopy(self.file)
			self.whenChanged = os.path.getmtime(self.path)
			self.whenSaved = os.path.getmtime(self.path)
		except: piScreenUtils.logging.error(f"Unable to load {self.path}") ; return

	def saveFile(self, orig:bool=False):
		if not os.path.exists(self.path): piScreenUtils.logging.error(f"Unable to find {self.path}") ; return
		try:
			with open(self.path, "w") as f:
				if orig: 
					piScreenUtils.logging.debug(f"Save original JSON to {self.path}")
					json.dump(self.origFile, f, indent=4)
				else:
					piScreenUtils.logging.debug(f"Save JSON to {self.path}")
					json.dump(self.file, f, indent=4)
					self.origFile = copy.deepcopy(self.file)
			self.whenSaved = os.path.getmtime(self.path)
		except:
			piScreenUtils.logging.error(f"Unable to save {self.path}")

	def __init__(self, path:str, autosave:bool=False):
		self.path = path
		self.file = {}
		self.origFile = {}
		self.autosave = autosave
		self.whenChanged = datetime.datetime.strptime("1900-01-01 00:00", piScreenUtils.Constants.DATE_FORMATE)
		self.whenSaved = datetime.datetime.strptime("1900-01-01 00:00",piScreenUtils.Constants.DATE_FORMATE)
		if path != "": self.loadFile()

	def getValue(self, keyPath:str, orig:bool=False):
		keys = keyPath.split('/')
		if orig: value = self.origFile 
		else: value = self.file
		try:
			for key in keys:
				value = value[key]
			return value
		except KeyError:
			return None

	def getAllValues(self, orig:bool=False):
		if orig: return self.origFile
		else: return self.file

	def setValue(self, keyPath:str, value, convert:bool=True, orig:bool=False):
		oldValue = self.getValue(keyPath,orig)
		if oldValue == value: piScreenUtils.logging.debug(f"Value {value} for key {keyPath} is already set") ; return
		keys = keyPath.split('/')
		if orig: currentDict = self.origFile
		else: currentDict = self.file
		for key in keys[:-1]:
			if key not in currentDict:
				currentDict[key] = {}
			currentDict = currentDict[key]
		if value is None:
			currentDict.pop(keys[-1], None)
		else:
			try: #Try to convert value to old datatype
				if convert:
					if type(oldValue) == int: value = int(value)
					if type(oldValue) == float: value = float(value)
					if type(oldValue) == bool:
						if value.lower() == "true": value = True
						elif value.lower() == "false": value = False
			except:
				piScreenUtils.logging.info(f"Changed setting seems to change datatype from {type(oldValue)} to String")
			currentDict[keys[-1]] = value
		self.whenChanged = datetime.datetime.now()
		if self.autosave: self.saveFile()

	def hasChanged(self): return self.origFile != self.file

	def hasExternalChanged(self): return os.path.getmtime(self.path) != self.whenSaved

#########################
### General functions ###
#########################

def checkIfProcessRunning(processName):
	for proc in psutil.process_iter():
		try:
			if processName.lower() in proc.name().lower():
				return True
		except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
			piScreenUtils.logging.critical("Unable to check if tasks are running")
	return False

def changeDesktopConfiguration(para:str, value:str):	
	for f in os.listdir(desktopConfigPath):
		desktopConfig = open(desktopConfigPath + f,"r").readlines()
		count = 0
		found = False
		for i in desktopConfig:
			if i.startswith(para):
				desktopConfig[count] = f"{para}{value}\n"
				found = True
				break
			count = count + 1
		if not found:
			desktopConfig.append(f"{para}{value}\n")
		open(desktopConfigPath + f,"w").writelines(desktopConfig)

#############
### Modes ###
#############

class firefoxHandler(threading.Thread):
	client = Marionette(host='127.0.0.1', port=2828, socket_timeout=20)
	info = JsonData("", False)
	actions = []
	lastContent = None

	def __init__(self):
		threading.Thread.__init__(self)

	def run(self):
		while active:
			try:
				while mode == 1 and active:
					if not checkIfProcessRunning("firefox-esr"):
						piScreenUtils.logging.info(f"Start firefox ({content})")
						os.system(f'firefox-esr --marionette --kiosk-monitor 0 "{content}" &')
						self.lastContent = content
						time.sleep(2)
					if checkIfProcessRunning("crashreporter"):
						piScreenUtils.logging.warning("There is a crashreporter open. It will be killed now")
						os.system("killall crashreporter")
					#Marionette
					try:
						self.info.setValue(f"url", self.client.get_url(), True)
						self.info.setValue(f"title", self.client.title, True)
						for item in self.actions:
							if item == "refresh": piScreenUtils.logging.info("Refresh firefox") ; self.client.refresh()
							elif item == "restart":
								if checkIfProcessRunning("firefox-esr"): os.system("killall firefox-esr")
						self.actions.clear()
						if self.lastContent != content:
							self.lastContent = content
							piScreenUtils.logging.info(f"Navigate browser to {content}")
							self.client.navigate(content)
					except:
						try:
							self.client.delete_session()
							self.client.start_session(timeout=2)
						except Exception as err:
							piScreenUtils.logging.error("Unable to create marionette session")
							piScreenUtils.logging.debug(err)
					time.sleep(1)
			except Exception as err:
				piScreenUtils.logging.error("Error in firefox handler")
				piScreenUtils.logging.debug(err)
			
			if checkIfProcessRunning("firefox-esr"): os.system("killall firefox-esr")
			self.actions.clear()
			time.sleep(1)
		piScreenUtils.logging.info("End firefox handler")

class vlcHandler(threading.Thread):
	info = JsonData("", False)
	actions = []
	lastContent = None
	vlcPlayer = vlc.Instance('--video-wallpaper','--input-repeat=999999999')
	vlcMediaPlayer = vlcPlayer.media_player_new()
	vlcMedia = vlc.Media("")

	def __init__(self):
		threading.Thread.__init__(self)

	def run(self):
		while active:
			while mode == 2 and active:
				try:
					if self.lastContent != content:
						self.vlcMedia = vlc.Media(content)
						self.vlcMediaPlayer.set_media(self.vlcMedia)
						self.vlcMediaPlayer.play()
						self.lastContent = content
					self.info.setValue(f"source", self.vlcMedia.get_mrl(), True)
					self.info.setValue(f"state", str(self.vlcMediaPlayer.get_state()), True)
					self.info.setValue(f"time", self.vlcMediaPlayer.get_time(), True)
					self.info.setValue(f"length", self.vlcMediaPlayer.get_length(), True)
					self.info.setValue(f"volume", self.vlcMediaPlayer.audio_get_volume(), True)
					for item in self.actions:
						if item == "play": piScreenUtils.logging.info("Play VLC") ; self.vlcMediaPlayer.play()
						elif item == "play/pause": piScreenUtils.logging.info("Play / Pause VLC") ; self.vlcMediaPlayer.pause()
						elif item == "pause": piScreenUtils.logging.info("Pause VLC") ; self.vlcMediaPlayer.set_pause(1)
						elif item == "restart": piScreenUtils.logging.info("Restart VLC") ; self.vlcMediaPlayer.play() ; self.vlcMediaPlayer.set_position(0.0)
						elif item.startswith("volume"):
							try:
								piScreenUtils.logging.info(f"Set volume to {item[6:]}")
								self.vlcMediaPlayer.audio_set_volume(int(item[6:]))
							except:
								piScreenUtils.logging.error("The volume is no int")
					self.actions.clear()
				except Exception as err:
					piScreenUtils.logging.error("Error in vlc handler")
					piScreenUtils.logging.debug(err)
				time.sleep(1)
			
			self.vlcMediaPlayer.stop()
			self.actions.clear()
			time.sleep(1)
		piScreenUtils.logging.info("End vlc handler")

#########################
### Display functions ###
#########################

class displayHandler(threading.Thread):
	info = JsonData("", False)
	actions = []

	def __init__(self):
		threading.Thread.__init__(self)
		
	def run(self):
		while active:
			try:
				self.getInfos("HDMI-A-1")
				self.getInfos("HDMI-A-2")
				self.checkOrientation("HDMI-A-1")
				self.checkOrientation("HDMI-A-2")
				self.checkResolution("HDMI-A-1")
				self.checkResolution("HDMI-A-2")
				self.checkActions()
			except Exception as err:
				piScreenUtils.logging.error("Error in display handler")
				piScreenUtils.logging.debug(err)
			
			time.sleep(2)
	
	def checkActions(self):
		if len(self.actions) == 0: return
		action = self.actions.pop()
		if action["cmd"] == 0: #On/Off
			if action["data"]["value"] == 0:
				subprocess.run(["wlr-randr", "--output", action["data"]["output"], "--off"])
			elif action["data"]["value"] == 1:
				subprocess.run(["wlr-randr", "--output", action["data"]["output"], "--on"])
 
	def getInfos(self, output:str):
		result = subprocess.run(["wlr-randr", "--output", output], capture_output=True, text=True).stdout.splitlines()
		if len(result) == 0: self.info.setValue(output, None) ; return
		foundPreferred = True
		foundRes = False
		foundOrientation = False
		foundStatus = False
		for line in result:
			if "preferred" in line:
				splited = line.split()[0].split("x")
				self.info.setValue(f"{output}/preferredResolution/width", splited[0], True)
				self.info.setValue(f"{output}/preferredResolution/height", splited[1], True)
				foundPreferred = True
			if "current" in line:
				splited = line.split()[0].split("x")
				self.info.setValue(f"{output}/currentResolution/width", splited[0], True)
				self.info.setValue(f"{output}/currentResolution/height", splited[1], True)
				foundRes = True
			elif "Transform:" in line:
				orientation = line.split()[1]
				if orientation == "normal": self.info.setValue(f"{output}/orientation", 0, True)
				elif orientation == "90": self.info.setValue(f"{output}/orientation", 1, True)
				elif orientation == "180": self.info.setValue(f"{output}/orientation", 2, True)
				elif orientation == "270": self.info.setValue(f"{output}/orientation", 3, True)
				elif orientation == "flipped": self.info.setValue(f"{output}/orientation", 4, True)
				elif orientation == "flipped-90": self.info.setValue(f"{output}/orientation", 5, True)
				elif orientation == "flipped-180": self.info.setValue(f"{output}/orientation", 6, True)
				elif orientation == "flipped-270": self.info.setValue(f"{output}/orientation", 7, True)
				foundOrientation = True
			elif "Enabled:" in line:
				status = line.split()[1]
				if status == "no": self.info.setValue(f"{output}/status", 0, True)
				elif status == "yes": self.info.setValue(f"{output}/status", 1, True)
				foundStatus = True
		if foundPreferred == False: self.info.setValue(f"{output}/preferredResolution", None)
		if foundRes == False: self.info.setValue(f"{output}/currentResolution", None)
		if foundOrientation == False: self.info.setValue(f"{output}/orientation", None)
		if foundStatus == False: self.info.setValue(f"{output}/status", None)

	def checkOrientation(self, output:str):
		wantedOrientation = settings.getValue(f"display/{output}/orientation")
		currentOrientation = self.info.getValue(f"{output}/orientation")
		if wantedOrientation != None and wantedOrientation != currentOrientation:
			piScreenUtils.logging.debug(f"Wanted display orientation differs to current orientation. Change orientation from {currentOrientation} to {wantedOrientation}")
			self.setOrientation(output, wantedOrientation)
	
	def setOrientation(self, output:str, wantedOrientation:int):
		piScreenUtils.logging.debug(f"Change display orientation to {wantedOrientation}")
		orientation = "normal"
		if wantedOrientation == 1: orientation = "90"
		elif wantedOrientation == 2: orientation = "180"
		elif wantedOrientation == 3: orientation = "270"
		elif wantedOrientation == 4: orientation = "flipped"
		elif wantedOrientation == 5: orientation = "flipped-90"
		elif wantedOrientation == 6: orientation = "flipped-180"
		elif wantedOrientation == 7: orientation = "flipped-270"
		return subprocess.run(["wlr-randr", "--output", output, "--transform", orientation])

	def checkResolution(self, output:str):
		wantedWidth = settings.getValue(f"display/{output}/resolution/width")
		wantedHeight = settings.getValue(f"display/{output}/resolution/height")
		currentWidth = self.info.getValue(f"{output}/currentResolution/width")
		currentHeight = self.info.getValue(f"{output}/currentResolution/height")
		preferredWidth = self.info.getValue(f"{output}/preferredResolution/width")
		preferredHeight = self.info.getValue(f"{output}/preferredResolution/height")
		if wantedWidth == None or wantedHeight == None:
			if currentWidth != preferredWidth or currentHeight != preferredHeight:
				result = subprocess.run(["wlr-randr", "--output", output, "--preferred"])
		elif wantedWidth != currentWidth or wantedHeight != currentHeight:
			result = subprocess.run(["wlr-randr", "--output", output, "--mode", f"{wantedWidth}x{wantedHeight}"])
			if result.returncode != 0:
				piScreenUtils.logging.error(f"Unable to set display resolution to {wantedWidth}x{wantedHeight}. Remove wanted resolution from config.")
				settings.setValue(f"display/{output}/resolution", None)


############################
### Socket communication ###
############################

class socketHandler(threading.Thread):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	def __init__(self):
		threading.Thread.__init__(self)
		self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.server_socket.bind(("127.0.0.1", piScreenUtils.Constants.CORE_MGMT_PORT))
		self.server_socket.listen(5)
		#self.server_socket.settimeout(5)

	def run(self):
		piScreenUtils.logging.info("Start socket listener")
		while active:
			try:
				client_socket, address = self.server_socket.accept()
				piScreenUtils.logging.debug(f"Connection from {address} accepted.")
				data = client_socket.recv(16384)
				if data:
					self.cmdInterpreter(client_socket, data.decode())
				else:
					client_socket.close()
			except socket.error as e:
				piScreenUtils.logging.error("Error while reciving data")
				piScreenUtils.logging.debug(f"Socket error: {e}")
		piScreenUtils.logging.info("Close all connections")
		try:
			client_socket.close()
		except socket.timeout: pass
		self.server_socket.close()
		piScreenUtils.logging.info("End socket listener")

	def cmdInterpreter(self, client_socket:socket.socket, data):
		returnValue = {"code":0}
		try:
			global mode
			global content
			global active
			data = json.loads(data)
			if "cmd" not in data: piScreenUtils.logging.warning("There is no cmd field in the transmitted data")
			else:
				if data["cmd"] == 1: #Stop-Core
					active = False
				elif data["cmd"] == 2: pass #Get-Core-Status
				elif data["cmd"] == 3: #Get Setting
					if "path" in data:
						returnValue.update({"value": settings.getValue(data["path"])})
					else:
						returnValue.update(settings.file)
				elif data["cmd"] == 4: #Set Setting
					if {"path", "value", "type"} <= data.keys():
						try:
							if data["type"].lower() == "int": data["value"] = int(data["value"])
							elif data["type"].lower() == "float": data["value"] = float(data["value"])
							elif data["type"].lower() == "str": data["value"] = str(data["value"])
							elif data["type"].lower() == "json": data["value"] = json.loads(data["value"])
							elif data["type"].lower() == "bool":
								if data["value"].lower() == "true": data["value"] = True
								elif data["value"].lower() == "false": data["value"] = False
								else: returnValue["code"] = 4
							else: returnValue["code"] = 3
						except:
							returnValue["code"] = 5
						if returnValue["code"] == 0: settings.setValue(data["path"], data["value"], convert=False)
					elif {"path", "value"} <= data.keys():
						settings.setValue(data["path"], data["value"])
					elif {"path"} <= data.keys():
						settings.setValue(data["path"], None)
					else:
						returnValue["code"] = 2
				elif data["cmd"] == 5: #Get-display-resolution
					returnValue["currentResolution"] = [dH.info.getValue("HDMI-A-1/currentResolution"), dH.info.getValue("HDMI-A-2/currentResolution")]
				elif data["cmd"] == 6: #Set-display-resolution
					output = piScreenUtils.Constants.DEFAULT_DISPLAY_OUTPUT
					if "output" in data: output = data["output"]
					if {"width", "height"} <= data.keys():
						if type(data["width"]) == int and type(data["height"]) == int:
							settings.setValue(f"display/{output}/resolution/width", data["width"])
							settings.setValue(f"display/{output}/resolution/height", data["height"])
						else:
							returnValue["code"] = 6
					else:
						settings.setValue(f"display/{output}/resolution", None)
				elif data["cmd"] == 7: #Get-display-orientation
					returnValue["orientation"] = [dH.info.getValue("HDMI-A-1/orientation"), dH.info.getValue("HDMI-A-2/orientation")]
				elif data["cmd"] == 8: #Set-display-orientation
					if "orientation" not in data: returnValue["code"] = 2
					else:
						if piScreenUtils.isInt(data["orientation"]) == False: returnValue["code"] = 6
						else:
							if data["orientation"] not in [0, 1 , 2, 3, 4, 5, 6, 7]: returnValue["code"] = 7
							else:
								output = piScreenUtils.Constants.DEFAULT_DISPLAY_OUTPUT
								if "output" in data: output = data["output"]
								result = dH.setOrientation(output, data["orientation"])
								if result.returncode == 0:
									settings.setValue(f"display/{output}/orientation", data["orientation"])
								else:
									returnValue["code"] = 1
				elif data["cmd"] == 9: #Get-display-status
					returnValue["status"] = [dH.info.getValue("HDMI-A-1/status"), dH.info.getValue("HDMI-A-2/status")]
				elif data["cmd"] == 10: #Set-display-status
					if "value" in data:
						if data["value"] in [0, 1]: 
							if "output" in data: dH.actions.push({"cmd": 0, "data": {"value": data["value"], "output": data["output"]}})
							else: dH.actions.insert(0, {"cmd": 0, "data": {"value": data["value"], "output": piScreenUtils.Constants.DEFAULT_DISPLAY_OUTPUT}})
						else: returnValue["code"] = 7
					else: returnValue["code"] = 2
				elif data["cmd"] == 11: #reboot
					piScreenUtils.logging.info("Perform system reboot")
					active = False
					os.system("sudo reboot")
				elif data["cmd"] == 12: #shutdown
					piScreenUtils.logging.info("Perform system shutdown")
					active = False
					os.system("sudo poweroff")
				elif data["cmd"] == 13: #set-desktop-configuration
					try:
						if "value" in data:
							if "mode" in data["value"]:
								if data["value"]["mode"] in ["color", "stretch", "fit", "crop", "center", "tile", "screen"]:
									piScreenUtils.logging.info(f"Set wallpaper mode to {data['value']['mode']}")
									os.system(f"pcmanfm --wallpaper-mode={data['value']['mode']}")
									time.sleep(0.5)
							if "wallpaper" in data["value"]:
								if os.path.exists(data["value"]["wallpaper"]):
									piScreenUtils.logging.info(f"Set wallpaper to {data['value']['wallpaper']}")
									os.system(f'pcmanfm "--set-wallpaper={data["value"]["wallpaper"]}"')
									time.sleep(0.5)
							if "background-color" in data["value"]:
								if re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', data["value"]["background-color"]):
									piScreenUtils.logging.info(f"Set backgroundcolor to {data['value']['background-color']}")
									changeDesktopConfiguration("desktop_bg=", data['value']['background-color'])
									os.system("pcmanfm --reconfigure")
							if "show-trash" in data["value"]:
								data["value"]["show-trash"] = data["value"]["show-trash"].lower()
								if data["value"]["show-trash"] == "true" or data["value"]["show-trash"] == "1":
									piScreenUtils.logging.info("Make trash icon visible")
									changeDesktopConfiguration("show_trash=", "1")
									os.system("pcmanfm --reconfigure")
								elif data["value"]["show-trash"] == "false" or data["value"]["show-trash"] == "0":
									piScreenUtils.logging.info("Make trash icon invisible")
									changeDesktopConfiguration("show_trash=", "0")
									os.system("pcmanfm --reconfigure")
							if "show-documents" in data["value"]:
								data["value"]["show-documents"] = data["value"]["show-documents"].lower()
								if data["value"]["show-documents"] == "true" or data["value"]["show-documents"] == "1":
									piScreenUtils.logging.info("Make trash icon visible")
									changeDesktopConfiguration("show_documents=", "1")
									os.system("pcmanfm --reconfigure")
								elif data["value"]["show-documents"] == "false" or data["value"]["show-documents"] == "0":
									piScreenUtils.logging.info("Make trash icon invisible")
									changeDesktopConfiguration("show_documents=", "0")
									os.system("pcmanfm --reconfigure")
							if "show-mounts" in data["value"]:
								data["value"]["show-mounts"] = data["value"]["show-mounts"].lower()
								if data["value"]["show-mounts"] == "true" or data["value"]["show-mounts"] == "1":
									piScreenUtils.logging.info("Make trash icon visible")
									changeDesktopConfiguration("show_mounts=", "1")
									os.system("pcmanfm --reconfigure")
								elif data["value"]["show-mounts"] == "false" or data["value"]["show-mounts"] == "0":
									piScreenUtils.logging.info("Make trash icon invisible")
									changeDesktopConfiguration("show_mounts=", "0")
									os.system("pcmanfm --reconfigure")
					except Exception as err:
						piScreenUtils.logging.error("Unable to set desktop configuration")
						piScreenUtils.logging.debug(err)
				elif data["cmd"] == 14: #get-desktop-configuration
					returnValue["config"] = {}
					returnValue["config"]["desktop_bg"] = ""
					returnValue["config"]["wallpaper"] = ""
					returnValue["config"]["wallpaper_mode"] = ""
					returnValue["config"]["show_trash"] = ""
					returnValue["config"]["show_documents"] = ""
					returnValue["config"]["show_mounts"] = ""
					for f in os.listdir(desktopConfigPath):
						desktopConfig = open(desktopConfigPath + f,"r").readlines()
						for i in desktopConfig:
							if i.startswith("desktop_bg="): returnValue["config"]["desktop_bg"] = i[11:-1]
							elif i.startswith("wallpaper="): returnValue["config"]["wallpaper"] = i[10:-1]
							elif i.startswith("wallpaper_mode="): returnValue["config"]["wallpaper_mode"] = i[15:-1]
							elif i.startswith("show_trash="): returnValue["config"]["show_trash"] = i[11:-1]
							elif i.startswith("show_documents="): returnValue["config"]["show_documents"] = i[15:-1]
							elif i.startswith("show_mounts="): returnValue["config"]["show_mounts"] = i[12:-1]
						break
				elif data["cmd"] == 15: #get-status
					returnValue["status"] = {}
					returnValue["status"]["mode"] = mode
					returnValue["status"]["displayInfo"] = {}
					returnValue["status"]["displayInfo"] = dH.info.getAllValues()
					returnValue["status"]["modeInfo"] = {}
					if mode == 1:
						returnValue["status"]["modeInfo"] = fH.info.getAllValues()
					elif mode == 2:
						returnValue["status"]["modeInfo"] = vH.info.getAllValues()
				elif data["cmd"] == 99: #stop-modes
					mode = 0
					content = None
				elif data["cmd"] == 100: #start-firefox
					if "value" in data:
						mode = 1
						content = data["value"]
				elif data["cmd"] == 101: #do-firefox-restart
					fH.actions.append("restart")
				elif data["cmd"] == 102: #do-firefox-refresh
					fH.actions.append("refresh")
				elif data["cmd"] == 200: #start-vlc
					if "value" in data:
						mode = 2
						content = data["value"]
				elif data["cmd"] == 201: #play
					vH.actions.append("play")
				elif data["cmd"] == 202: #play/pause
					vH.actions.append("play/pause")
				elif data["cmd"] == 203: #pause
					vH.actions.append("pause")
				elif data["cmd"] == 204: #restart
					vH.actions.append("restart")
				elif data["cmd"] == 205: #volume
					if "value" in data:
						vH.actions.append("volume" + str(data["value"]))

		except Exception as err:
			piScreenUtils.logging.error("Unable to convert recieved command to json")
			piScreenUtils.logging.debug(err)

		try:
			client_socket.sendall(json.dumps(returnValue).encode())
		except:
			piScreenUtils.logging.warning("Unable to send return value to requester")
		client_socket.close()




###################
### Global vars ###
###################

active = True
os.environ["DISPLAY"] = ":0"
mode = 0
content = None
desktopConfigPath = "/home/pi/.config/pcmanfm/LXDE-pi/"


############
### Main ###
############

if __name__ == "__main__":
	piScreenUtils.logging.info("Startup core")
	piScreenUtils.logging.debug("Loading settings")
	settings = JsonData(piScreenUtils.Paths.SETTINGS, True)

	piScreenUtils.logging.info("Start display handler")
	dH = displayHandler()
	dH.start()

	piScreenUtils.logging.info("Start firefox handler")
	fH = firefoxHandler()
	fH.start()

	piScreenUtils.logging.info("Start vlc handler")
	vH = vlcHandler()
	vH.start()

	piScreenUtils.logging.info("Start communcation socket")
	sH = socketHandler()
	sH.start()
	
	while active:
		#Create screenshot
		subprocess.run(["grim", "-t", "png", piScreenUtils.Paths.SCREENSHOT])
		time.sleep(5)
	piScreenUtils.logging.info("Stop core")
	active = False
	mode = 0
	content = None