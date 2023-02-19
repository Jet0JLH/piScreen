#!/usr/bin/python3
import json, datetime, os, threading, time, piScreenUtils

skriptPath = os.path.dirname(os.path.abspath(__file__))
os.chdir(skriptPath)
active = os.path.exists(piScreenUtils.paths.scheduleActive)
allTrigger = []
threadLock = threading.Lock()

def firstRun(noTrigger):
	piScreenUtils.logging.debug(f"noTrigger={noTrigger}")
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
		if self.commandset != None:
			commandsetTask(self.commandset)
		return True

	def checkPattern(self, pattern, check):
		if pattern == "*":
			return True
		elif piScreenUtils.isInt(pattern):
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
						if piScreenUtils.isInt(splited1[0]) and piScreenUtils.isInt(splited2[0]) and piScreenUtils.isInt(splited2[1]):
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
					if piScreenUtils.isInt(item):
						if int(item) == check:
							return True
					else:
						splited = item.split("-")
						if len(splited) > 1:
							if piScreenUtils.isInt(splited[0]) and piScreenUtils.isInt(splited[1]):
								for item in range(int(splited[0]), int(splited[1])+1):
									if item == check:
										return True
			#x/x
			elif pattern.find("/") != -1:
				splited = pattern.split("/")
				if len(splited) > 1:
					if (piScreenUtils.isInt(splited[0]) or splited[0] == "*") and piScreenUtils.isInt(splited[1]):
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
					if piScreenUtils.isInt(splited[0]) and piScreenUtils.isInt(splited[1]):
						for item in range(int(splited[0]), int(splited[1])+1):
							if item == check:
								return True
			#x,x
			elif pattern.find(",") != -1:
				for item in pattern.split(","):
					if piScreenUtils.isInt(item):
						if int(item) == check:
							return True
						

			#---End-Cases---------------------------
		return False

class cron(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)

	def doCron(self):
		piScreenUtils.logging.debug("Do cron")
		if "cron" in globalConf.conf:
			now = datetime.datetime.today()
			for item in globalConf.conf["cron"]:
				cronItem = cronEntry(item)
				cronItem.run(now,False)
	
	def run(self):
		piScreenUtils.logging.debug("Start cron thread")
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
			piScreenUtils.logging.info("Load configuration")
			self.conf = json.load(open(piScreenUtils.paths.schedule))
			threadLock.release()
		except ValueError as err:
			piScreenUtils.logging.error("Problem while loading configuration")
			threadLock.release()
			return False
		return True

class trigger(threading.Thread):
	active = True
	config = {}
	mode = 0
	lastState = None
	runOnce = False
	firstStateDontTrigger = False
	isInFirstrun = True

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
			if "runOnce" in self.config: self.runOnce = self.config["runOnce"]
			if "firstStateDontTrigger" in self.config: self.firstStateDontTrigger = self.config["firstStateDontTrigger"]
			piScreenUtils.logging.info(f"Trigger {self.mode} is starting")
			if self.mode == 1: #Firstrun
				self.active = False
				self.isInFirstrun = False
			elif self.mode == 10: #File exists [change,true,false]
				if "file" in self.config:
					while self.active:
						exists = os.path.exists(self.config["file"])
						if exists != self.lastState:
							self.lastState = exists
							self.execute("change")
							if exists:
								self.execute("true")
							else:
								self.execute("false")
						self.isInFirstrun = False
						time.sleep(1)
			elif self.mode == 11: #File changed [true]
				if "file" in self.config:
					fileModifyDate = 0
					if os.path.exists(self.config["file"]):
						fileModifyDate = os.path.getmtime(self.config["file"])
					while self.active:
						if os.path.exists(self.config["file"]):
							newModifyDate = os.path.getmtime(self.config["file"])
							if newModifyDate != fileModifyDate:
								fileModifyDate = newModifyDate
								self.execute("true")
						time.sleep(1)
			elif self.mode == 20: #Ping [change,true,false]
				while self.active:
					self.isInFirstrun = False
					time.sleep(1)
			elif self.mode == 21: #TCP connection [change,true,false]
				if "host" in self.config and "port" in self.config and piScreenUtils.isInt(self.config["port"]) and "timeout" in self.config and piScreenUtils.isInt(self.config["timeout"]) and "runs" in self.config and piScreenUtils.isInt(self.config["runs"]):
					import socket
					host = self.config["host"]
					port = int(self.config["port"])
					timeout = int(self.config["timeout"])
					runs = int(self.config["runs"])
					trueCounter = 0
					falseCounter = 0
					while self.active:
						try:
							socket.setdefaulttimeout(timeout)
							socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
							if falseCounter > 0: falseCounter = 0 ; self.execute("change")
							trueCounter = trueCounter + 1
							if trueCounter == runs: self.execute("true")
							time.sleep(timeout)
						except:
							if trueCounter > 0: trueCounter = 0 ; self.execute("change")
							falseCounter = falseCounter + 1
							if falseCounter == runs: self.execute("false")
						self.isInFirstrun = False
			elif self.mode == 30: #Display state on [change,true,false]
				while self.active:
					try:
						state = open(piScreenUtils.paths.displayStatus,"r").read().strip()
						if self.lastState != state:
							if state == "on":
								self.execute("change")
								self.execute("true")
							elif self.lastState == "on" or self.lastState == None:
								self.execute("change")
								self.execute("false")
							self.lastState = state
							
					except:
						pass #Error
					self.isInFirstrun = False
					time.sleep(1)
			elif self.mode == 40: #Mode changed [true,<mode>]
				import subprocess
				while self.active:
					try:
						state = subprocess.check_output(f"{piScreenUtils.paths.syscall} --get-mode",shell=True).decode("utf-8").strip()
						if self.lastState != state:
							self.lastState = state
							self.execute("true")
							self.execute(state)
					except:
						pass #Error
					self.isInFirstrun = False
					time.sleep(1)
			elif self.mode == 50: #GPiO pin high [change,true,false]
				while self.active:
					self.isInFirstrun = False
					time.sleep(1)
			piScreenUtils.logging.info(f"Trigger {self.mode} has been stopped")
		else:
			piScreenUtils.logging.warning("Trigger is not right defined")
			
	def execute(self,state:str):
		if self.isInFirstrun and self.firstStateDontTrigger: return #should not execute in firstrun
		piScreenUtils.logging.info(f"Run trigger {self.mode}")
		if "cases" not in self.config: return
		if state not in self.config["cases"]: return
		if "command" in self.config["cases"][state]:
			if "parameter" in self.config["cases"][state]:
				commandInterpreter(self.config["cases"][state]["command"],self.config["cases"][state]["parameter"])
			else:
				commandInterpreter(self.config["cases"][state]["command"],None)
		if "commandset" in self.config["cases"][state]:
			commandsetTask(self.config["cases"][state]["commandset"])
		if self.runOnce: self.active = False

class commandsetTask(threading.Thread):
	def __init__(self,commandsetID):
		threading.Thread.__init__(self)
		self.commandsetID = commandsetID
		self.start()

	def run(self):
		runCommandset(self.commandsetID)
		del self

def runCommandset(commandsetID):
	if not piScreenUtils.isInt(commandsetID):
		piScreenUtils.logging.warning("Given commandsetID is not a number")
		return False
	piScreenUtils.logging.info(f"Run commandset {commandsetID}")
	commandsetID = int(commandsetID)
	if "commandsets" not in globalConf.conf:
		piScreenUtils.logging.info(f"Commandset {commandsetID} is not in config")
		return False
	for item in globalConf.conf["commandsets"]:
		if "id" not in item:
			continue
		if item["id"] != commandsetID:
			continue
		if "commands" not in item:
			continue
		for commandset in item["commands"]:
			if "command" not in commandset:
				continue
			if "parameter" in commandset:
				commandInterpreter(commandset["command"], commandset["parameter"])
			else:
				commandInterpreter(commandset["command"], None)
		break
	return True

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
	if not piScreenUtils.isInt(cmd): return False
	piScreenUtils.logging.debug(f"Run command {cmd} with parameter {parameter}")
	cmd = int(cmd)
	if cmd == 1: #Sleep
		if piScreenUtils.isFloat(parameter):
			time.sleep(float(parameter))
		else:
			piScreenUtils.logging.warning("There is no parameter given")
	elif cmd == 2: #LastCron
		firstRun(True)
	elif cmd == 3: #Write Log
		parameter = parameter.split(":-:")
		if len(parameter) >= 2:
			os.system(f'{piScreenUtils.paths.syscall} --write-log --level {parameter[0]} "{parameter[1]}"')
		else:
			piScreenUtils.logging.error("Wrong structure of log command parameter")
	elif cmd == 10: #Universal Call
		if parameter:
			try:
				os.system(parameter)
			except:
				piScreenUtils.logging.error("Error while executing universal call")
		else:
			piScreenUtils.logging.warning("There is no parameter given")
	elif cmd == 11: #Reboot
		if saveMode: time.sleep(300) ; piScreenUtils.logging.info("We are in save mode. Reboot starts in 300s")
		os.system(piScreenUtils.paths.syscall + "--reboot")
	elif cmd == 12: #Shutdown
		if saveMode: time.sleep(300) ; piScreenUtils.logging.info("We are in save mode. Shutdown starts in 300s")
		os.system(piScreenUtils.paths.syscall + "--shutdown")
	elif cmd == 13: #Call commandset
		if parameter:
			commandsetTask(parameter)
		else:
			piScreenUtils.logging.warning("There is no parameter given")
	elif cmd == 30: #Control display [0 = Standby, 1 = On]
		if piScreenUtils.isInt(parameter):
			if int(parameter) == 0:
				os.system(piScreenUtils.paths.syscall + " --screen-standby")
			else:
				os.system(piScreenUtils.paths.syscall + " --screen-on")
		else:
			piScreenUtils.logging.warning("There is no parameter given")
	elif cmd == 31: #Switch display input
		os.system(piScreenUtils.paths.syscall + " --screen-switch-input")
	elif cmd == 32: #Change display protocol [0 = CEC, 1 = DDC]
		if piScreenUtils.isInt(parameter):
			if int(parameter):
				os.system(piScreenUtils.paths.syscall + " --set-display-protocol cec")
			else:
				os.system(piScreenUtils.paths.syscall + " --set-display-protocol ddc")
		else:
			piScreenUtils.logging.warning("There is no parameter given")
	elif cmd == 40: #StartBrowser
		if parameter:
			os.system(f'{piScreenUtils.paths.syscall} --start-browser "{parameter}"')
		else:
			piScreenUtils.logging.warning("There is no parameter given")
	elif cmd == 41: #RestartBrowser
		os.system(f'{piScreenUtils.paths.syscall} --restart-browser')
	elif cmd == 42: #ReloadBrowser
		os.system(f'{piScreenUtils.paths.syscall} --refresh-browser')
	elif cmd == 43: #CloseBrowser
		os.system(f"{piScreenUtils.paths.syscall} --stop-browser")
	elif cmd == 50: #StartVLC
		if parameter:
			os.system(f'{piScreenUtils.paths.syscall} --start-vlc "{parameter}"')
		else:
			piScreenUtils.logging.warning("There is no parameter given")
	elif cmd == 51: #RestartVLC
		os.system(f"{piScreenUtils.paths.syscall} --restart-vlc")
	elif cmd == 52: #StopVLC
		os.system(f"{piScreenUtils.paths.syscall} --stop-vlc")
	elif cmd == 53: #Pause/PlayVLC
		os.system(f"{piScreenUtils.paths.syscall} --pause-vlc")
	elif cmd == 54: #PlayVLC
		os.system(f"{piScreenUtils.paths.syscall} --play-vlc")
	elif cmd == 60: #StartImpress
		if parameter:
			os.system(f'{piScreenUtils.paths.syscall} --start-impress "{parameter}"')
		else:
			piScreenUtils.logging.warning("There is no parameter given")
	elif cmd == 61: #RestartImpress
		os.system(f"{piScreenUtils.paths.syscall} --restart-impress")
	elif cmd == 62: #StopImpress
		os.system(f"{piScreenUtils.paths.syscall} --stop-impress")
	

	

#Main
piScreenUtils.logging.info("Startup")
globalConf = config()
if not globalConf.loadConfig():
	piScreenUtils.logging.error("Json file seems to be damaged")
	print("Json file seems to be damaged")
	exit(1)
loadTrigger()
loadCrons()
configModify = os.path.getmtime(piScreenUtils.paths.schedule)
while active:
	try:
		if configModify != os.path.getmtime(piScreenUtils.paths.schedule):
			piScreenUtils.logging.info("Config seems to be changed")
			#Config changed
			if not globalConf.loadConfig():
				piScreenUtils.logging.error("Json file seems to be damaged")
				print("Json File seems to be damaged")
			else:
				loadTrigger()
		configModify = os.path.getmtime(piScreenUtils.paths.schedule)
		active = os.path.exists(piScreenUtils.paths.scheduleActive)
		if os.path.exists(piScreenUtils.paths.scheduleDoFirstRun):
			firstRun(False)
			try:
				os.remove(piScreenUtils.paths.scheduleDoFirstRun)
			except:
				piScreenUtils.logging.error("Unable to remove firstrun file in ramdisk")
				print("Unable to remove firstrun file in ramdisk")
		if os.path.exists(piScreenUtils.paths.scheduleDoLastCron):
			firstRun(True)
			try:
				os.remove(piScreenUtils.paths.scheduleDoLastCron)
			except:
				piScreenUtils.logging.error("Unable to remove lastCron file in ramdisk")
				print("Unable to remove lastCron file in ramdisk")
		if os.path.exists(piScreenUtils.paths.scheduleDoManually):
			try:
				manually = json.load(open(piScreenUtils.paths.scheduleDoManually))
				if "type" in manually:
					if manually["type"] == "command":
						piScreenUtils.logging.info("Running command manually")
						if "command" in manually and "parameter" in manually:
							commandInterpreter(manually["command"],manually["parameter"])
						elif "command" in manually:
							commandInterpreter(manually["command"])
						else:
							piScreenUtils.logging.warning("There is no command attribut in manually file")
					elif manually["type"] == "commandset":
						piScreenUtils.logging.info("Running commandset manually")
						if "id" in manually:
							commandsetTask(manually["id"])
						else:
							piScreenUtils.logging.warning("There is no id attribut in manually file")
					elif manually["type"] == "cron":
						piScreenUtils.logging.info("Running cron manually")
						if "index" in manually:
							if piScreenUtils.isInt(manually["index"]) and len(globalConf.conf["cron"]) > int(manually["index"]):
								cronEntry(globalConf.conf["cron"][int(manually["index"])]).run(None,True)
							piScreenUtils.logging.warning("There is something wrong in manually file")
						else:
							piScreenUtils.logging.warning("There is no index attribut in manually file")
					elif manually["type"] == "trigger":
						piScreenUtils.logging.info("Running trigger manually")
						if "index" in manually:
							if piScreenUtils.isInt(manually["index"]) and len(globalConf.conf["trigger"]) > int(manually["index"]):
								item = globalConf.conf["trigger"][int(manually["index"])]
								tmpTrigger = trigger()
								#Ignore enabled flag
								tmpTrigger.config = item
								tmpTrigger.runOnce = True
								tmpTrigger.start()
							else:
								piScreenUtils.logging.warning("There is something wrong in manually file")
						else:
							piScreenUtils.logging.warning("There is no index attribut in manually file")
				else:
					piScreenUtils.logging.warning("Manually file has no type attribut")
			except:
				piScreenUtils.logging.error("Error with manually json file in ramdisk")
			try:
				os.remove(piScreenUtils.paths.scheduleDoManually)
			except:
				piScreenUtils.logging.error("Unable to remove manually file in ramdisk")
		time.sleep(1)
	except KeyboardInterrupt:
		active = False
		stopAllTrigger()