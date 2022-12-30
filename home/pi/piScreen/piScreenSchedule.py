#!/usr/bin/python
import json, datetime, os, threading, time

skriptPath = os.path.dirname(os.path.abspath(__file__))
os.chdir(skriptPath)
syscall = "./piScreenCmd.py"
configFile = "./schedule.json"
activePath = "/media/ramdisk/piScreenScheduleActive"
doFirstRunPath = "/media/ramdisk/piScreenScheduleFirstRun"
doLastCronPath = "/media/ramdisk/piScreenScheduleLastCron"
doManuallyPath = "/media/ramdisk/piScreenScheduleManually"
active = os.path.exists(activePath)
allTrigger = []
threadLock = threading.Lock()

def isInt(s):
	try: 
		int(s)
		return True
	except ValueError:
		return False

def isFloat(s):
	try:
		float(s)
		return True
	except ValueError:
		return False

def firstRun(noTrigger):
	global saveMode
	saveMode = True
	#Check if startup trigger (1) enabled
	if noTrigger or not runTrigger(1,"true"):
		if "cron" in globalConf.conf:
			found = False
			entries = []
			for item in globalConf.conf["cron"]:
				cronItem = cronEntry(item)
				entries.append(cronItem)
			count = 0
			now = datetime.datetime.today()
			oneMinute = datetime.timedelta(minutes=1)
			#Check last commandsets in a Week
			while count < 10080 and not found:
				for item in entries:
					if item.run(now,False):
						found = True
				now = now - oneMinute
				count = count + 1
	saveMode = False

def loadCrons():
	cronThread = cron()
	cronThread.start()

def loadTrigger():
	if not "trigger" in globalConf.conf:
		return False
	founds = []
	outerCounter = 0
	for item in globalConf.conf["trigger"]:
		if "enabled" in item and item["enabled"]:
			tmpTrigger = trigger()
			tmpTrigger.config = item
			found = -1
			innerCounter = 0
			for triggerItem in allTrigger:
				if tmpTrigger == triggerItem:
					found = innerCounter
				innerCounter = innerCounter + 1
			if found == -1:
				tmpTrigger.start()
				allTrigger.append(tmpTrigger)
				founds.append(innerCounter)
			else:
				founds.append(found)
			outerCounter = outerCounter + 1
	founds.sort()
	missingTrigger = set(range(len(allTrigger))).difference(founds)
	offset = 0
	for item in missingTrigger:
		allTrigger[item + offset].stop()
		del allTrigger[item + offset]
		offset = offset - 1
def stopAllTrigger():
	for triggerItem in allTrigger:
		triggerItem.stop()

class cronEntry():
	enabled = False
	commandset = None
	command = None
	parameter = None
	start = None
	end = None
	pattern = None
	def __init__(self):
		pass
	def __init__(self, jsonObj):
		self.parse(jsonObj)
	
	def parse(self, jsonObj):
		self.enabled = False
		self.commandset = None
		self.command = None
		self.parameter = None
		self.start = None
		self.end = None
		self.pattern = None
		if "enabled" in jsonObj:
			if jsonObj["enabled"]:
				self.enabled = True
			else:
				self.enabled = False
		if "commandset" in jsonObj:
			self.commandset = jsonObj["commandset"]
		if "command" in jsonObj:
			if isinstance(jsonObj["command"], int):
				self.command = jsonObj["command"]
		if "parameter" in jsonObj:
			self.parameter = jsonObj["parameter"]
		if "start" in jsonObj:
			try:
				self.start = datetime.datetime.strptime(jsonObj["start"], "%Y-%m-%d %H:%M")
			except ValueError:
				pass
		if "end" in jsonObj:
			try:
				self.end = datetime.datetime.strptime(jsonObj["end"], "%Y-%m-%d %H:%M")
			except ValueError:
				pass
		if "pattern" in jsonObj:
			if all(ch in "0123456789/-*, " for ch in jsonObj["pattern"]) and len(jsonObj["pattern"].split(" ")) == 5:
				self.pattern = jsonObj["pattern"].split(" ")

	def run(self, timestamp, manually):
		if not manually:
			if not self.enabled:
				return False
			if self.start is not None:
				if self.start > timestamp:
					#Startdate in future
					return False
			if self.end is not None:
				if self.end < timestamp:
					#Enddate in past
					return False
			if self.pattern is None:
				return False
			else:
				if not self.checkPattern(self.pattern[4], timestamp.weekday()):
					return False
				if not self.checkPattern(self.pattern[3], timestamp.month):
					return False
				if not self.checkPattern(self.pattern[2], timestamp.day):
					return False
				if not self.checkPattern(self.pattern[1], timestamp.hour):
					return False
				if not self.checkPattern(self.pattern[0], timestamp.minute):
					return False		
		commandInterpreter(self.command, self.parameter)
		runCommandset(self.commandset)
		return True

	def checkPattern(self, pattern, check):
		if pattern == "*":
			return True
		elif isInt(pattern):
			#x
			if int(pattern) == check:
				return True
		else:
			#---Cases---------------------------

			#x,x-x/x			
			if pattern.find("-") != -1 and pattern.find(",") != -1 and pattern.find("/") != -1:
				pass
				#This case does not exist
			#x-x/x
			elif pattern.find("-") != -1 and pattern.find("/") != -1:
				splited1 = pattern.split("-")
				if len(splited1) > 1:
					splited2 = splited1[1].split("/")
					if len(splited2) > 1:
						if isInt(splited1[0]) and isInt(splited2[0]) and isInt(splited2[1]):
							for item in range(int(splited1[0]), int(splited2[0])+1, int(splited2[1])):
								if item == check:
									return True
			#x,x/x
			elif pattern.find("-") != -1 and pattern.find("/") != -1:
				pass
				#This case does not exist
			#x,x-x
			elif pattern.find("-") != -1 and pattern.find(",") != -1:
				for item in pattern.split(","):
					if isInt(item):
						if int(item) == check:
							return True
					else:
						splited = item.split("-")
						if len(splited) > 1:
							if isInt(splited[0]) and isInt(splited[1]):
								for item in range(int(splited[0]), int(splited[1])+1):
									if item == check:
										return True
			#x/x
			elif pattern.find("/") != -1:
				splited = pattern.split("/")
				if len(splited) > 1:
					if (isInt(splited[0]) or splited[0] == "*") and isInt(splited[1]):
						if splited[0] == "*":
							if check % int(splited[1]) == 0:
								return True
						else:
							#This case does not exist
							pass
			#x-x
			elif pattern.find("-") != -1:
				splited = pattern.split("-")
				if len(splited) > 1:
					if isInt(splited[0]) and isInt(splited[1]):
						for item in range(int(splited[0]), int(splited[1])+1):
							if item == check:
								return True
			#x,x
			elif pattern.find(",") != -1:
				for item in pattern.split(","):
					if isInt(item):
						if int(item) == check:
							return True
						

			#---End-Cases---------------------------
		return False

class cron(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)

	def doCron(self):
		if "cron" in globalConf.conf:
			now = datetime.datetime.today()
			for item in globalConf.conf["cron"]:
				cronItem = cronEntry(item)
				cronItem.run(now,False)
	
	def run(self):
		now = datetime.datetime.today()
		lastMinute = now.minute
		firstRun(False)
		while active:
			now = datetime.datetime.today()
			if lastMinute is not now.minute:
				lastMinute = now.minute
				threadLock.acquire()
				self.doCron()
				threadLock.release()
			time.sleep(1)

class config():
	conf = json.loads("{}")
	def __init__(self):
		pass

	def loadConfig(self):
		try:
			threadLock.acquire()
			self.conf = json.load(open(configFile))
			threadLock.release()
		except ValueError as err:
			threadLock.release()
			return False
		return True

class trigger(threading.Thread):
	active = True
	config = {}
	mode = 0
	lastState = None
	def __init__(self):
		threading.Thread.__init__(self)
		self.config = json.dumps({})
	def __exit__(self, exc_type, exc_value, traceback):
		self.active = False
		self.package_obj.cleanup()
	def stop(self):
		self.active = False
	def __eq__(self, __o: object) -> bool:
		return self.config == __o.config
	def __hash__(self) -> int:
		return 0
		

	def run(self):
		if "trigger" in self.config:
			self.mode = self.config["trigger"]
			if self.mode == 1: #Firstrun
				self.active = False
			elif self.mode == 10: #File exists
				if "file" in self.config:
					while self.active:
						exists = os.path.exists(self.config["file"])
						if exists != self.lastState:
							self.lastState = exists
							self.execute("onChange")
							if exists:
								self.execute("true")
							else:
								self.execute("false")
						time.sleep(1)
			elif self.mode == 11: #File changed
				while self.active:
					time.sleep(1)
			elif self.mode == 20: #Ping
				while self.active:
					time.sleep(1)
			elif self.mode == 30: #Display state changed
				while self.active:
					time.sleep(1)
			elif self.mode == 40: #GPiO pin high
				while self.active:
					time.sleep(1)
			

	def execute(self,state:str):
		if state in self.config:
			if "command" in self.config[state]:
				if "parameter" in self.config[state]:
					commandInterpreter(self.config[state]["command"],self.config[state]["parameter"])
				else:
					commandInterpreter(self.config[state]["command"],None)
			if "commandset" in self.config[state]:
				runCommandset(self.config[state]["commandset"])

def runCommandset(commandsetID):
	if "commandsets" in globalConf.conf:
		for item in globalConf.conf["commandsets"]:
			if "id" in item:
				if item["id"] == commandsetID:
					if "commands" in item:
						for commandset in item["commands"]:
							if "command" in commandset:
								if "parameter" in commandset:
									commandInterpreter(commandset["command"], commandset["parameter"])
								else:
									commandInterpreter(commandset["command"], None)
def findTrigger(mode:int):
	found = False
	for item in allTrigger:
		if item.mode == mode:
			found = True
	return found

def runTrigger(mode:int,state:str="true"):
	found = False
	for item in allTrigger:
		if item.mode == mode:
			found = True
			item.execute(state)
	return found

def commandInterpreter(cmd:int, parameter:str):
	if not cmd: return False
	if not isInt(cmd): return False
	cmd = int(cmd)
	if cmd == 1:
		#Sleep
		if isFloat(parameter):
			time.sleep(float(parameter))
	elif cmd == 10:
		#Universal Call
		if parameter:
			try:
				os.system(parameter)
			except:
				#Error
				pass
	elif cmd == 11:
		#Reboot
		if saveMode: time.sleep(300)
		os.system("reboot")
	elif cmd == 12:
		#Shutdown
		if saveMode: time.sleep(300)
		os.system("poweroff")
	elif cmd == 30:
		#Control display [0 = Standby, 1 = On]
		if isInt(parameter):
			if int(parameter) == 0:
				os.system(syscall + " --screen-standby")
			else:
				os.system(syscall + " --screen-on")
		pass
	elif cmd == 31:
		#Switch display input
		os.system(syscall + " --screen-switch-input")
	elif cmd == 32:
		#Change display protocol [0 = CEC, 1 = DDC]
		if isInt(parameter):
			if int(parameter):
				os.system(syscall + " --set-display-protocol cec")
			else:
				os.system(syscall + " --set-display-protocol ddc")
	elif cmd == 40:
		#StartBrowser
		if parameter:
			os.system(f'{syscall} --start-browser "{parameter}"')
	elif cmd == 41:
		#RestartBrowser
		os.system(f'{syscall} --restart-browser')
	elif cmd == 42:
		#ReloadBrowser
		pass
	elif cmd == 43:
		#CloseBrowser
		os.system(f"{syscall} --stop-browser")
	elif cmd == 50:
		#StartVLC
		if parameter:
			os.system(f'{syscall} --start-vlc "{parameter}"')
	elif cmd == 51:
		#RestartVLC
		os.system(f"{syscall} --restart-vlc")
	elif cmd == 52:
		#StopVLC
		os.system(f"{syscall} --stop-vlc")
	elif cmd == 53:
		#Pause/PlayVLC
		os.system(f"{syscall} --pause-vlc")
	elif cmd == 54:
		#PlayVLC
		os.system(f"{syscall} --play-vlc")
	elif cmd == 60:
		#StartImpress
		if parameter:
			os.system(f'{syscall} --start-impress "{parameter}"')
	elif cmd == 61:
		#RestartImpress
		os.system(f"{syscall} --restart-impress")
	elif cmd == 62:
		#StopImpress
		os.system(f"{syscall} --stop-impress")
	

	

#Main
globalConf = config()
if not globalConf.loadConfig():
	print("Json File seems to be damaged")
	exit(1)
loadTrigger()
loadCrons()
configModify = os.path.getmtime(configFile)
while active:
	try:
		if configModify != os.path.getmtime(configFile):
			#Config changed
			if not globalConf.loadConfig():
				print("Json File seems to be damaged")
			else:
				loadTrigger()
		configModify = os.path.getmtime(configFile)
		active = os.path.exists(activePath)
		if os.path.exists(doFirstRunPath):
			firstRun(False)
			try:
				os.remove(doFirstRunPath)
			except:
				print("Unable to remove firstrun file in ramdisk")
		if os.path.exists(doLastCronPath):
			firstRun(True)
			try:
				os.remove(doLastCronPath)
			except:
				print("Unable to remove lastCron file in ramdisk")
		if os.path.exists(doManuallyPath):
			try:
				manually = json.load(open(doManuallyPath))
				if "type" in manually:
					if manually["type"] == "command":
						if "command" in manually and "parameter" in manually:
							commandInterpreter(manually["command"],manually["parameter"])
						elif "command" in manually:
							commandInterpreter(manually["command"])
					elif manually["type"] == "commandset":
						if "id" in manually:
							runCommandset(manually["id"])
					elif manually["type"] == "cron":
						if "index" in manually:
							if isInt(manually["index"]) and len(globalConf.conf["cron"]) > int(manually["index"]):
								cronEntry(globalConf.conf["cron"][int(manually["index"])]).run(None,True)
					elif manually["type"] == "trigger":
						if "index" in manually:
							if isInt(manually["index"]) and len(globalConf.conf["trigger"]) > int(manually["index"]):
								item = globalConf.conf["trigger"][int(manually["index"])]
								if "command" in item:
									if "parameter" in item:
										commandInterpreter(item["command"],item["parameter"])
									else:
										commandInterpreter(item["command"],None)
									if "commandset" in item:
										runCommandset(item["commandset"])
			except:
				print("Error with 'manually' json file in ramdisk")
			try:
				os.remove(doManuallyPath)
			except:
				print("Unable to remove 'manually' file in ramdisk")
		time.sleep(1)
	except KeyboardInterrupt:
		active = False
		stopAllTrigger()