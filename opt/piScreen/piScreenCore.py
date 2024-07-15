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
				result = subprocess.run(["wlr-randr", "--output", "HDMI-A-1"], capture_output=True, text=True).stdout.splitlines()
				found = False
				for line in result:
					if "current" in line:
						splited = line.split()[0].split("x")
						self.info.setValue("0/currentResolution/x", splited[0], True)
						self.info.setValue("0/currentResolution/y", splited[1], True)
						found = True
				if found == False: self.info.setValue("0", None)
				result = subprocess.run(["wlr-randr", "--output", "HDMI-A-2"], capture_output=True, text=True).stdout.splitlines()
				found = False
				for line in result:
					if "current" in line:
						splited = line.split()[0].split("x")
						self.info.setValue("1/currentResolution/x", splited[0], True)
						self.info.setValue("1/currentResolution/y", splited[1], True)
						found = True
				if found == False: self.info.setValue("1", None)
			except Exception as err:
				piScreenUtils.logging.error("Error in display handler")
				piScreenUtils.logging.debug(err)
			
			time.sleep(2)

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
					returnValue["currentResolution"] = [dH.info.getValue("0/currentResolution"), dH.info.getValue("1/currentResolution")]

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