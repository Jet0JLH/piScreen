#!/usr/bin/python
import json, datetime, os, threading, time

skriptPath = os.path.dirname(os.path.abspath(__file__))
os.chdir(skriptPath)
syscall = "./piScreenCmd.py"
configFile = "./schedule.json"
activePath = "/media/ramdisk/piScreenScheduleActive"
active = os.path.exists(activePath)
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

def firstRun():
	#Check if startup trigger (1) enabled
	if not runTrigger(1):
		if "cron" in globalConf.conf:
			found = False
			entries = []
			for item in globalConf.conf["cron"]:
				cronItem = cronEntry(item)
				entries.append(cronItem)
			count = 0
			now = datetime.datetime.today()
			oneMinute = datetime.timedelta(minutes=1)
			#Check last Events in a Week
			while count < 10080 and not found:
				for item in entries:
					if item.run(now):
						found = True
				now = now - oneMinute
				count = count + 1

def loadCrons():
	cronThread = cron()
	cronThread.start()

def loadTrigger():
	pass

class cronEntry():
	enabled = False
	event = None
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
		self.event = None
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
		if "event" in jsonObj:
			self.event = jsonObj["event"]
		if "command" in jsonObj:
			if isinstance(jsonObj["command"], int):
				self.command = jsonObj["command"]
		if "parameter" in jsonObj:
			self.parameter = jsonObj["parameter"]
		if "start" in jsonObj:
			try:
				self.start = datetime.datetime.strptime(jsonObj["start"], "%Y-%m-%d %H:%M:%S")
			except ValueError:
				pass
		if "end" in jsonObj:
			try:
				self.end = datetime.datetime.strptime(jsonObj["end"], "%Y-%m-%d %H:%M:%S")
			except ValueError:
				pass
		if "pattern" in jsonObj:
			if all(ch in "0123456789/-*, " for ch in jsonObj["pattern"]) and len(jsonObj["pattern"].split(" ")) == 5:
				self.pattern = jsonObj["pattern"].split(" ")

	def run(self, timestamp):
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
		runEvent(self.event)
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
				cronItem.run(now)
	
	def run(self):
		now = datetime.datetime.today()
		lastMinute = now.minute
		firstRun()
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

def runEvent(eventName):
	if "events" in globalConf.conf:
		for item in globalConf.conf["events"]:
			if "id" in item:
				#eventName is case sensitive
				if item["id"] == eventName:
					if "commands" in item:
						for event in item["commands"]:
							if "command" in event:
								if "parameter" in event:
									commandInterpreter(event["command"],event["parameter"])
								else:
									commandInterpreter(event["command"],None)

def runTrigger(trigger):
	found = False
	if not trigger: return False
	if not isInt(trigger): return False
	trigger = int(trigger)
	if "trigger" in globalConf.conf:
		for item in globalConf.conf["trigger"]:
			if "enabled" in item:
				if item["enabled"]:
					found = True
					if "trigger" in item:
						if isInt(item["trigger"]):
							if trigger == int(item["trigger"]):
								if "command" in item:
									if "parameter" in item:
										commandInterpreter(item["command"],item["parameter"])
									else:
										commandInterpreter(item["command"],None)
									if "event" in item:
										runEvent(item["event"])
	return found
				

def commandInterpreter(cmd, parameter):
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
		os.system("reboot")
	elif cmd == 12:
		#Shutdown
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
			os.system(f"{syscall} --start-browser {parameter}")
	elif cmd == 41:
		#RestartBrowser
		pass
	elif cmd == 42:
		#ReloadBrowser
		pass
	elif cmd == 43:
		#CloseBrowser
		os.system(f"{syscall} --stop-browser")
	

#Main
globalConf = config()
if not globalConf.loadConfig():
	print("Json File seems to be damaged")
	exit(1)
loadCrons()
loadTrigger()
configModify = os.path.getmtime(configFile)
while active:
	try:
		if configModify != os.path.getmtime(configFile):
			if not globalConf.loadConfig():
				print("Json File seems to be damaged")
		configModify = os.path.getmtime(configFile)
		active = os.path.exists(activePath)
		time.sleep(5)
	except KeyboardInterrupt:
		active = False