#!/usr/bin/python
import json
import datetime
import sys
import os
import threading
import time

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
	def __init__(self,jsonObj):
		self.parse(jsonObj)
	
	def parse(self,jsonObj):
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
			if isinstance(jsonObj["command"],int):
				self.command = jsonObj["command"]
		if "parameter" in jsonObj:
			self.parameter = jsonObj["parameter"]
		if "start" in jsonObj:
			try:
				self.start = datetime.datetime.strptime(jsonObj["start"],"%Y-%m-%d %H:%M:%S")
			except ValueError:
				pass
		if "end" in jsonObj:
			try:
				self.end = datetime.datetime.strptime(jsonObj["end"],"%Y-%m-%d %H:%M:%S")
			except ValueError:
				pass
		if "pattern" in jsonObj:
			if all(ch in "0123456789/-*, " for ch in jsonObj["pattern"]) and len(jsonObj["pattern"].split(" ")) == 5:
				self.pattern = jsonObj["pattern"].split(" ")

	def run(self):
		#Check if runnable
		print("Check")
		if not self.enabled:
			return False
		now = datetime.datetime.today()
		if self.start is not None:
			if self.start > now:
				#Startdatum liegt in der Zukunft
				return False
		if self.end is not None:
			if self.end < now:
				#Enddatum bereits überschritten
				return False
		if self.pattern is None:
			return False
		else:
			if not self.checkPattern(self.pattern[4],now.weekday()):
				return False
			if not self.checkPattern(self.pattern[3],now.month):
				return False
			if not self.checkPattern(self.pattern[2],now.day):
				return False
			if not self.checkPattern(self.pattern[1],now.hour):
				return False
			if not self.checkPattern(self.pattern[0],now.minute):
				return False		
		
		print("Jup")
		return True

	def checkPattern(self,pattern,check):
		if pattern == "*":
			print("*")
			return True
		elif isInt(pattern):
			#x
			print("x")
			if int(pattern) == check:
				return True
		else:
			#---Cases---------------------------

			#x,x-x/x			
			if pattern.find("-") != -1 and pattern.find(",") != -1 and pattern.find("/") != -1:
				print("x,x-x/x")
				#Die Variante gibt es wohl nicht
			#x-x/x
			elif pattern.find("-") != -1 and pattern.find("/") != -1:
				print("x-x/x")
				splited1 = pattern.split("-")
				if len(splited1) > 1:
					splited2 = splited1[1].split("/")
					if len(splited2) > 1:
						if isInt(splited1[0]) and isInt(splited2[0]) and isInt(splited2[1]):
							for item in range(int(splited1[0]),int(splited2[0])+1,int(splited2[1])):
								if item == check:
									return True
			#x,x/x
			elif pattern.find("-") != -1 and pattern.find("/") != -1:
				print("x,x/x")
				#Die Variante gibt es wohl nicht
			#x,x-x
			elif pattern.find("-") != -1 and pattern.find(",") != -1:
				print("x,x-x")
				for item in pattern.split(","):
					if isInt(item):
						if int(item) == check:
							return True
					else:
						splited = item.split("-")
						if len(splited) > 1:
							if isInt(splited[0]) and isInt(splited[1]):
								for item in range(int(splited[0]),int(splited[1])+1):
									if item == check:
										return True
			#x/x
			elif pattern.find("/") != -1:
				print("x/x")
				splited = pattern.split("/")
				if len(splited) > 1:
					if (isInt(splited[0]) or splited[0] == "*") and isInt(splited[1]):
						if splited[0] == "*":
							if check % int(splited[1]) == 0:
								return True
						else:
							#Die Variante gibt es wohl nicht
							pass
			#x-x
			elif pattern.find("-") != -1:
				print("x-x")
				splited = pattern.split("-")
				if len(splited) > 1:
					if isInt(splited[0]) and isInt(splited[1]):
						for item in range(int(splited[0]),int(splited[1])+1):
							if item == check:
								return True
			#x,x
			elif pattern.find(",") != -1:
				print("x,x")
				for item in pattern.split(","):
					if isInt(item):
						if int(item) == check:
							return True
						

			#---End-Cases---------------------------
			#---Validate---------------------------	
		return False

class cron(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)

	def doCron(self):
		if "cron" in globalConf.conf:
			for item in globalConf.conf["cron"]:
				cronItem = cronEntry(item)
				cronItem.run()
	
	def run(self):
		lastMinute = 60
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
			return False
		return True

#Main
globalConf = config()
if not globalConf.loadConfig():
	print("Json File seems to be damaged")
	exit(1)
loadCrons()
loadTrigger()
try:
	while active:
		active = os.path.exists(activePath)
		time.sleep(1)
except KeyboardInterrupt:
	active = False