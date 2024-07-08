#!/usr/bin/python3
import piScreenUtils
import os, copy, json, datetime, threading, time, socket

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
		self.loadFile()

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
	
	def setValue(self, keyPath:str, value, orig:bool=False):
		if self.getValue(keyPath,orig) == value: piScreenUtils.logging.debug(f"Value {value} for key {keyPath} is already set") ; return
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
			currentDict[keys[-1]] = value
		self.whenChanged = datetime.datetime.now()
		if self.autosave: self.saveFile()

	def hasChanged(self): return self.origFile != self.file

	def hasExternalChanged(self): return os.path.getmtime(self.path) != self.whenSaved

#########################
### General functions ###
#########################


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
				elif data["cmd"] == 3: #Get Settings
					if "path" in data:
						returnValue.update({"value": settings.getValue(data["path"])})
					else:
						returnValue.update(settings.file)
				elif data["cmd"] == 4: #Set Settings
					if {"path", "value"} <= data.keys():
						settings.setValue(data["path"], data["value"])
					else:
						returnValue["code"] = 2

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


############
### Main ###
############

if __name__ == "__main__":
	piScreenUtils.logging.info("Startup core")
	piScreenUtils.logging.debug("Loading settings")
	settings = JsonData(piScreenUtils.Paths.SETTINGS, True)

	piScreenUtils.logging.info("Start communcation socket")
	sH = socketHandler()
	sH.start()
	
	while active:
		time.sleep(1)
	piScreenUtils.logging.info("Stop core")
	active = False