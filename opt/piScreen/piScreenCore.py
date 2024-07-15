#!/usr/bin/python3
import piScreenUtils
import os, subprocess, copy, json, datetime, threading, time, socket

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
			except Exception as err:
				piScreenUtils.logging.error("Error in display handler")
				piScreenUtils.logging.debug(err)
			
			time.sleep(2)
	
	def getInfos(self, output:str):
		result = subprocess.run(["wlr-randr", "--output", output], capture_output=True, text=True).stdout.splitlines()
		if len(result) == 0: self.info.setValue(output, None) ; return
		foundRes = False
		foundOrientation = False
		for line in result:
			if "current" in line:
				splited = line.split()[0].split("x")
				self.info.setValue(f"{output}/currentResolution/x", splited[0], True)
				self.info.setValue(f"{output}/currentResolution/y", splited[1], True)
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
		if foundRes == False: self.info.setValue(f"{output}/currentResolution", None)
		if foundOrientation == False: self.info.setValue(f"{output}/orientation", None)

	def checkOrientation(self, output:str):
		wantedOrientation = settings.getValue(f"display/{output}/orientation")
		currentOrientation = self.info.getValue(f"{output}/orientation")
		if wantedOrientation != currentOrientation:
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
			data = json.loads(data)
			if "cmd" not in data: piScreenUtils.logging.warning("There is no cmd field in the transmitted data")
			else:
				if data["cmd"] == 1: #Stop-Core
					global active
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
				elif data["cmd"] == 7: #Get-display-orientation
					returnValue["orientation"] = [dH.info.getValue("HDMI-A-1/orientation"), dH.info.getValue("HDMI-A-2/orientation")]
				elif data["cmd"] == 8: #Set-display-orientation
					if "orientation" not in data: returnValue["code"] = 2
					else:
						if piScreenUtils.isInt(data["orientation"]) == False: returnValue["code"] = 6
						else:
							if data["orientation"] not in [0, 1 , 2, 3, 4, 5, 6, 7]: returnValue["code"] = 7
							else:
								output = "HDMI-A-1"
								if "output" in data: output = data["output"]
								result = dH.setOrientation(output, data["orientation"])
								if result.returncode == 0:
									settings.setValue(f"display/{output}/orientation", data["orientation"])
								else:
									returnValue["code"] = 1

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
os.environ["WAYLAND_DISPLAY"] = "wayland-1"


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

	piScreenUtils.logging.info("Start communcation socket")
	sH = socketHandler()
	sH.start()
	
	while active:
		time.sleep(1)
	piScreenUtils.logging.info("Stop core")
	active = False