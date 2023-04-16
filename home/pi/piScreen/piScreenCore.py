#!/usr/bin/python3
import os, json, sys, time, psutil, subprocess, threading, socket, vlc, fcntl, datetime, cec, monitorcontrol, piScreenUtils
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
	os.system("killall -q firefox-esr")
	os.system("killall -q soffice.bin")

#######################
### Mode management ###
#######################

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
					except Exception as err:
						piScreenUtils.logging.error("Unable to create marionette session")
						piScreenUtils.logging.debug(err)
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
					self.info["volume"] = self.vlcMediaPlayer.audio_get_volume()
					for item in self.actions:
						if item == "play": piScreenUtils.logging.info("Play VLC") ; self.vlcMediaPlayer.play()
						elif item == "play/pause": piScreenUtils.logging.info("Play / Pause VLC") ; self.vlcMediaPlayer.pause()
						elif item == "pause": piScreenUtils.logging.info("Pause VLC") ; self.vlcMediaPlayer.set_pause(1)
						elif item == "restart": piScreenUtils.logging.info("Restart VLC") ; self.vlcMediaPlayer.set_position(0)
						elif item.startswith("volume"):
							try:
								piScreenUtils.logging.info(f"Set volume to {item[6:]}")
								self.vlcMediaPlayer.audio_set_volume(int(item[6:]))
							except:
								piScreenUtils.logging.error("The volume is no int")
					self.actions.clear()
				except Exception as err:
					self.info = {}
					piScreenUtils.logging.error("Unable to control VLC")
					piScreenUtils.logging.debug(err)
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

###############	
### Display ###
###############

class cecHandler(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)

	def run(self):
		global active
		global displayAction
		global displayActionTries
		global displayLastValue
		global displayForceMode
		self.device = cec.Device(cec.CECDEVICE_TV)
		cec.add_callback(self.cecEvent,cec.EVENT_COMMAND)
		self.updateStatus()
		while active:
			if displayProtocol == "cec": piScreenUtils.logging.info("Start display control over cec") ; displayLastValue = "Unknown"
			while displayProtocol == "cec" and active:
				for i in range(5):
					try:
						#Process actions
						if displayAction == 1: #On
							if displayLastValue == "on":
								if not displayForceMode: displayAction = 0
							elif displayActionTries < 60:
								piScreenUtils.logging.info("Set display to on")
								self.device.power_on()
								displayActionTries += 1
							else:
								piScreenUtils.logging.warning("Tries to often to set display to on")
								displayAction = 0
						elif displayAction == 2: #Off
							if displayLastValue == "off":
								if not displayForceMode: displayAction = 0
							elif displayActionTries < 60:
								piScreenUtils.logging.info("Set display to off")
								self.device.transmit(cec.CEC_OPCODE_STANDBY)
								displayActionTries += 1
							else:
								piScreenUtils.logging.warning("Tries to often to set display to off")
								displayAction = 0
						elif displayAction == 3: #Set Inputsource
							piScreenUtils.logging.info("Set display active source")
							cec.set_active_source()
							displayAction = 0
					except Exception as err:
						piScreenUtils.logging.error("Trouble while controling display")
						piScreenUtils.logging.debug(err)
					if not active or displayProtocol != "cec": break
					time.sleep(2)
				self.updateStatus()
			time.sleep(1)
		piScreenUtils.logging.info("End cec handler")

	def updateStatus(self):
		self.device.transmit(cec.CEC_OPCODE_GIVE_DEVICE_POWER_STATUS)

	def cecEvent(self,event, cmd):
		global displayLastValue
		opcodeName = "Unknown"
		for key, value in cec.__dict__.items():
			if value == cmd["opcode"]: opcodeName = key
		piScreenUtils.logging.debug(f"{opcodeName} -> {cmd}")
		if cmd["opcode"] == cec.CEC_OPCODE_STANDBY:
			if displayLastValue != "off": displayLastValue = "off" ; piScreenUtils.logging.info("Display status changed to off")
		elif cmd["opcode"] == cec.CEC_OPCODE_ROUTING_CHANGE: #https://community.openhab.org/t/hdmi-cec-binding/21246/112?page=6
			if displayLastValue != "on": displayLastValue = "on" ; piScreenUtils.logging.info("Display status changed to on")
		elif cmd["opcode"] == cec.CEC_OPCODE_REPORT_POWER_STATUS:
			if cmd["parameters"] == b'\x01':
				if displayLastValue != "off": displayLastValue = "off" ; piScreenUtils.logging.info("Display status changed to off")
			if cmd["parameters"] == b'\x00':
				if displayLastValue != "on": displayLastValue = "on" ; piScreenUtils.logging.info("Display status changed to on")
		elif cmd["opcode"] == cec.CEC_OPCODE_ACTIVE_SOURCE:
			if cmd["parameters"] == b'\x00\x00':
				if displayLastValue != "on": displayLastValue = "on" ; piScreenUtils.logging.info("Display status changed to on")
		elif cmd["opcode"] == cec.CEC_OPCODE_USER_CONTROL_PRESSED:
			if cmd["parameters"] == b'!':
				threading.Thread(target=runTrigger,args=(31,"1")).start()
			elif cmd["parameters"] == b'"':
				threading.Thread(target=runTrigger,args=(31,"2")).start()
			elif cmd["parameters"] == b'#':
				threading.Thread(target=runTrigger,args=(31,"3")).start()
			elif cmd["parameters"] == b'$':
				threading.Thread(target=runTrigger,args=(31,"4")).start()
			elif cmd["parameters"] == b'%':
				threading.Thread(target=runTrigger,args=(31,"5")).start()
			elif cmd["parameters"] == b'&':
				threading.Thread(target=runTrigger,args=(31,"6")).start()
			elif cmd["parameters"] == b"'":
				threading.Thread(target=runTrigger,args=(31,"7")).start()
			elif cmd["parameters"] == b'(':
				threading.Thread(target=runTrigger,args=(31,"8")).start()
			elif cmd["parameters"] == b')':
				threading.Thread(target=runTrigger,args=(31,"9")).start()
			elif cmd["parameters"] == b' ':
				threading.Thread(target=runTrigger,args=(31,"0")).start()
			elif cmd["parameters"] == b'\x00':
				threading.Thread(target=runTrigger,args=(31,"accept")).start()
			elif cmd["parameters"] == b'\x01':
				threading.Thread(target=runTrigger,args=(31,"up")).start()
			elif cmd["parameters"] == b'\x02':
				threading.Thread(target=runTrigger,args=(31,"down")).start()
			elif cmd["parameters"] == b'\x03':
				threading.Thread(target=runTrigger,args=(31,"left")).start()
			elif cmd["parameters"] == b'\x04':
				threading.Thread(target=runTrigger,args=(31,"right")).start()
			elif cmd["parameters"] == b'\r':
				threading.Thread(target=runTrigger,args=(31,"exit")).start()
			elif cmd["parameters"] == b'D':
				threading.Thread(target=runTrigger,args=(31,"play")).start()
			elif cmd["parameters"] == b'F':
				threading.Thread(target=runTrigger,args=(31,"pause")).start()
			elif cmd["parameters"] == b'E':
				threading.Thread(target=runTrigger,args=(31,"stop")).start()
			elif cmd["parameters"] == b'I':
				threading.Thread(target=runTrigger,args=(31,"forward")).start()
			elif cmd["parameters"] == b'H':
				threading.Thread(target=runTrigger,args=(31,"rewind")).start()
			elif cmd["parameters"] == b'G':
				threading.Thread(target=runTrigger,args=(31,"record")).start()
			elif cmd["parameters"] == b'r':
				threading.Thread(target=runTrigger,args=(31,"red")).start()
			elif cmd["parameters"] == b's':
				threading.Thread(target=runTrigger,args=(31,"green")).start()
			elif cmd["parameters"] == b't':
				threading.Thread(target=runTrigger,args=(31,"yellow")).start()
			elif cmd["parameters"] == b'q':
				threading.Thread(target=runTrigger,args=(31,"blue")).start()

class ddcHandler(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)

	def run(self):
		global active
		global displayAction
		global displayActionTries
		global displayLastValue
		global displayForceMode
		while active:
			if displayProtocol == "ddc": piScreenUtils.logging.info("Start display control over ddc") ; displayLastValue = "Unknown"
			while displayProtocol == "ddc" and active:
				try:
					monitors = monitorcontrol.get_monitors()
					if len(monitors) <= 0: piScreenUtils.logging.warning("Unable to find display") ; displayLastValue = "Unknown"
					else:
						with monitors[0]: 
							mode = monitors[0].get_power_mode()
							try:
								#Check current state
								if mode == mode.on:
									if  displayLastValue != "on":  displayLastValue = "on" ; piScreenUtils.logging.info("Display status changed to on")
								elif mode == mode.off_hard or mode == mode.off_soft:
									if  displayLastValue != "off":  displayLastValue = "off" ; piScreenUtils.logging.info("Display status changed to off")
								elif mode == mode.standby or mode == mode.suspend:
									if  displayLastValue != "standby":  displayLastValue = "standby" ; piScreenUtils.logging.info("Display status changed to standby")
								else:
									piScreenUtils.logging.warning(f"Unkown status: {mode}")
									displayLastValue = "Unknown"
							except Exception as err:
								piScreenUtils.logging.error("Unable to check display mode")
								piScreenUtils.logging.debug(err)
								displayLastValue = "Unknown"

							try:
								#Process actions
								if displayAction == 1: #On
									if displayLastValue == "on":
										if not displayForceMode: displayAction = 0
									elif displayActionTries < 60:
										piScreenUtils.logging.info("Set display to on")
										monitors[0].set_power_mode(mode.on)
										displayActionTries += 1
									else:
										piScreenUtils.logging.warning("Tries to often to set display to on")
										displayAction = 0
								elif displayAction == 2: #Off
									if displayLastValue == "off":
										if not displayForceMode: displayAction = 0
									elif displayActionTries < 60:
										piScreenUtils.logging.info("Set display to off")
										monitors[0].set_power_mode(mode.off_hard)
										displayActionTries += 1
									else:
										piScreenUtils.logging.warning("Tries to often to set display to off")
										displayAction = 0
								elif displayAction == 3: #Set Inputsource
									piScreenUtils.logging.info("DDC Mode doesn't support change of the display source")
									displayAction = 0
							except Exception as err:
								piScreenUtils.logging.error("Trouble while controling display")
								piScreenUtils.logging.debug(err)
				except Exception as err:
					piScreenUtils.logging.error("Trouble with reading DDC/CI Info")
					piScreenUtils.logging.debug(err)
					displayLastValue = "Unknown"
				time.sleep(2)
			time.sleep(1)
		piScreenUtils.logging.info("End ddc handler")
				

class manuallyHandler(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)

	def run(self):
		global active
		global displayAction
		global displayActionTries
		global displayLastValue
		global displayForceMode
		ran = True
		while active:
			if displayProtocol == "manually":
				piScreenUtils.logging.info("Start display control over manually")
				displayLastValue = "Unknown"
				os.system("xset +dpms")
				os.system("xset s 0")
				os.system("xset dpms 0 0 0")
				ran = True
				

			while displayProtocol == "manually" and active:
				try:
					#Check current state
					status = str(subprocess.check_output(["xset", "-q"]))
					if "Monitor is Off" in status:
						if displayLastValue != "off": displayLastValue = "off" ; piScreenUtils.logging.info("Display status changed to off")
					elif "Monitor is On" in status:
						if displayLastValue != "on": displayLastValue = "on" ; piScreenUtils.logging.info("Display status changed to on")
					elif "Monitor is in Standby" in status or "Monitor is in Suspend" in status:
						if displayLastValue != "standby": displayLastValue = "standby" ; piScreenUtils.logging.info("Display status changed to standby")
				except Exception as err:
					piScreenUtils.logging.error("Error while reading display state")
					piScreenUtils.logging.debug(err)
					displayLastValue = "Unknown"

				try:
					#Process actions
					if displayAction == 1: #On
						if displayLastValue == "on":
							if not displayForceMode: displayAction = 0
						elif displayActionTries < 60:
							piScreenUtils.logging.info("Set display to on")
							os.system("xset dpms force on")
							displayActionTries += 1
						else:
							piScreenUtils.logging.warning("Tries to often to set display to on")
							displayAction = 0
					elif displayAction == 2: #Off
						if displayLastValue == "off":
							if not displayForceMode: displayAction = 0
						elif displayActionTries < 60:
							piScreenUtils.logging.info("Set display to off")
							os.system("xset dpms force off")
							displayActionTries += 1
						else:
							piScreenUtils.logging.warning("Tries to often to set display to off")
							displayAction = 0
					elif displayAction == 3: #Set Inputsource
						piScreenUtils.logging.info("Manually Mode doesn't support change of the display source")
						displayAction = 0
				except Exception as err:
					piScreenUtils.logging.error("Trouble while controling display")
					piScreenUtils.logging.debug(err)
				time.sleep(2)
			if ran: ran = False ; os.system("xset -dpms")
			time.sleep(1)
		piScreenUtils.logging.info("End manually handler")

################
### Schedule ###
################

def scheduleFirstRun(noTrigger):
	global scheduleSaveMode
	scheduleSaveMode = True
	#Check if startup trigger (1) enabled
	if noTrigger or not runTrigger(1,"true"):
		if "cron" in schedule:
			found = False
			entries = []
			for item in schedule["cron"]:
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
	scheduleSaveMode = False

def loadTrigger():
	if not "trigger" in schedule:
		return False
	founds = []
	outerCounter = 0
	for item in schedule["trigger"]:
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

def runTrigger(mode:int,state:str="true"):
	found = False
	for item in allTrigger:
		if item.mode == mode:
			found = True
			item.execute(state)
	return found

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
			if ignoreCronFrom < timestamp < ignoreCronTo:
				return False
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
		scheduleCmdInterpreter(self.command, self.parameter)
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
						if self.lastState != displayLastValue:
							if displayLastValue == "on":
								self.execute("change")
								self.execute("true")
							elif self.lastState == "on" or self.lastState == None:
								self.execute("change")
								self.execute("false")
							self.lastState = displayLastValue
					except Exception as err:
						piScreenUtils.logging.debug(err)
					self.isInFirstrun = False
					time.sleep(1)
			elif self.mode == 31: #CEC key pressed
				pass #Execute external
			elif self.mode == 40: #Mode changed [true,<mode>]
				import subprocess
				while self.active:
					try:
						state = subprocess.check_output(f"{piScreenUtils.paths.syscall} --get-mode",shell=True).decode("utf-8").strip()
						if self.lastState != state:
							self.lastState = state
							self.execute("true")
							self.execute(state)
					except Exception as err:
						piScreenUtils.logging.debug(err)
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
				scheduleCmdInterpreter(self.config["cases"][state]["command"],self.config["cases"][state]["parameter"])
			else:
				scheduleCmdInterpreter(self.config["cases"][state]["command"],None)
		if "commandset" in self.config["cases"][state]:
			commandsetTask(self.config["cases"][state]["commandset"])
		if self.runOnce: self.active = False

class cron(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)

	def doCron(self):
		piScreenUtils.logging.debug("Do cron")
		if "cron" in schedule:
			now = datetime.datetime.today()
			for item in schedule["cron"]:
				cronItem = cronEntry(item)
				cronItem.run(now,False)
	
	def run(self):
		piScreenUtils.logging.debug("Start cron thread")
		now = datetime.datetime.today()
		lastMinute = now.minute
		scheduleFirstRun(False)
		while active:
			now = datetime.datetime.today()
			if lastMinute is not now.minute:
				lastMinute = now.minute
				self.doCron()
			time.sleep(1)
		piScreenUtils.logging.info("End cron thread")


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
	if "commandsets" not in schedule:
		piScreenUtils.logging.info(f"Commandset {commandsetID} is not in config")
		return False
	for item in schedule["commandsets"]:
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
				scheduleCmdInterpreter(commandset["command"], commandset["parameter"])
			else:
				scheduleCmdInterpreter(commandset["command"], None)
		break
	return True

def scheduleCmdInterpreter(cmd:int, parameter:str):
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
		scheduleFirstRun(True)
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
			except Exception as err:
				piScreenUtils.logging.error("Error while executing universal call")
				piScreenUtils.logging.debug(err)
		else:
			piScreenUtils.logging.warning("There is no parameter given")
	elif cmd == 11: #Reboot
		if scheduleSaveMode: time.sleep(300) ; piScreenUtils.logging.info("We are in save mode. Reboot starts in 300s")
		os.system(f"sudo {piScreenUtils.paths.syscall} --reboot")
	elif cmd == 12: #Shutdown
		if scheduleSaveMode: time.sleep(300) ; piScreenUtils.logging.info("We are in save mode. Shutdown starts in 300s")
		os.system(f"sudo {piScreenUtils.paths.syscall} --shutdown")
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
		os.system(f"{piScreenUtils.paths.syscall} --play-pause-vlc")
	elif cmd == 54: #PlayVLC
		os.system(f"{piScreenUtils.paths.syscall} --play-vlc")
	elif cmd == 55: #PauseVLC
		os.system(f"{piScreenUtils.paths.syscall} --pause-vlc")
	elif cmd == 56: #VolumeVLC
		if parameter:
			os.system(f'{piScreenUtils.paths.syscall} --volume-vlc "{parameter}"')
		else:
			piScreenUtils.logging.warning("There is no parameter given")
	elif cmd == 60: #StartImpress
		if parameter:
			os.system(f'{piScreenUtils.paths.syscall} --start-impress "{parameter}"')
		else:
			piScreenUtils.logging.warning("There is no parameter given")
	elif cmd == 61: #RestartImpress
		os.system(f"{piScreenUtils.paths.syscall} --restart-impress")
	elif cmd == 62: #StopImpress
		os.system(f"{piScreenUtils.paths.syscall} --stop-impress")

############################
### Socket communication ###
############################

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
				try:
					returnValue = socketCmdInterpreter(jsonData)
					self.s.sendto(str.encode(json.dumps(returnValue)),bytesAddressPair[1])
				except Exception as err:
					piScreenUtils.logging.error("Error while interpret data")
					piScreenUtils.logging.debug(err)
			except Exception as err:
				piScreenUtils.logging.error("Unable to convert recieved command to json")
				piScreenUtils.logging.debug(err)
				self.s.sendto(str.encode(json.dumps({"code":2})),bytesAddressPair[1])
		piScreenUtils.logging.info("End socket listener")

def socketCmdInterpreter(data:dict) -> dict:
	global active
	global mode
	global parameter
	global status
	global displayAction
	global displayActionTries
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
	elif cmd == 5: #Control display
		if piScreenUtils.isInt(data["parameter"]):
			displayAction = data["parameter"]
			displayActionTries = 0
		else:
			return {"code":2} #Package format is wrong
	elif cmd == 6: #scheduleDoFirstRun
		threading.Thread(target=scheduleFirstRun,kwargs={"noTrigger":False}).start()
		return returnValue
	elif cmd == 7: #scheduleDoLastCron
		threading.Thread(target=scheduleFirstRun,kwargs={"noTrigger":True}).start()
		return returnValue
	elif cmd == 8: #scheduleDoManually
		if "parameter" not in data:
			piScreenUtils.logging.error("Recived data has no needed parameter field in it")
			return {"code":2} #Package format is wrong
		if "type" not in data["parameter"]:
			piScreenUtils.logging.error("Recived data has no needed type field in parameter field")
			return {"code":2} #Package format is wrong
		if piScreenUtils.isInt(data["parameter"]["type"]):
			data["parameter"]["type"] = int(data["parameter"]["type"])
			if data["parameter"]["type"] == 1: #Command
				piScreenUtils.logging.info("Running command manually")
				if "command" in data["parameter"] and "parameter" in data["parameter"]:
					threading.Thread(target=scheduleCmdInterpreter,args=(data["parameter"]["command"],data["parameter"]["parameter"])).start()
				if "command" in data["parameter"]:
					threading.Thread(target=scheduleCmdInterpreter,args=(data["parameter"]["command"],"")).start()
				else:
					piScreenUtils.logging.warning("There is no command field in parameter")
					return {"code":2} #Package format is wrong
			elif data["parameter"]["type"] == 2: #Commandset
				piScreenUtils.logging.info("Running commandset manually")
				if "id" in data["parameter"]:
					commandsetTask(data["parameter"]["id"])
				else:
					piScreenUtils.logging.warning("There is no id field in parameter")
					return {"code":2} #Package format is wrong
			elif data["parameter"]["type"] == 3: #Cron
				piScreenUtils.logging.info("Running cron manually")
				if "index" in data["parameter"]:
					if piScreenUtils.isInt(data["parameter"]["index"]) and len(schedule["cron"]) > int(data["parameter"]["index"]):
						threading.Thread(target=cronEntry(schedule["cron"][int(data["parameter"]["index"])]).run,args=(None,True)).start()
					else:
						piScreenUtils.logging.warning("Cron index doesn't exists")
						return {"code":4} #Wrong index
				else:
					piScreenUtils.logging.warning("There is no index field in parameter")
					return {"code":2} #Package format is wrong
			elif data["parameter"]["type"] == 4: #Trigger
				piScreenUtils.logging.info("Running trigger manually is currently not implementet")
				returnValue["code"] = 1
				return returnValue #Unkown cmd
		else:
			piScreenUtils.logging.error("Type is not a int")
			return {"code":2} #Package format is wrong
	else:
		piScreenUtils.logging.warning("Recived cmd is unknown")
		returnValue["code"] = 1
		return returnValue #Unkown cmd

#########################
### Config management ###
#########################

def checkSettings():
	global settings
	global settingsFileModify
	global displayProtocol
	global displayOrientation
	global displayForceMode
	newSettingsFileModify = os.path.getmtime(piScreenUtils.paths.settings)
	if newSettingsFileModify != settingsFileModify:
		try:
			piScreenUtils.logging.info("Settings seems to be changed")
			settings = json.load(open(piScreenUtils.paths.settings))
			settingsFileModify = newSettingsFileModify
			if "settings" in settings and "display" in settings["settings"]:
				if "protocol" in settings["settings"]["display"]: displayProtocol = settings["settings"]["display"]["protocol"]
				if "orientation" in settings["settings"]["display"]: displayOrientation = settings["settings"]["display"]["orientation"]
				if "force" in settings["settings"]["display"]: displayForceMode = settings["settings"]["display"]["force"]
		except Exception as err:
			piScreenUtils.logging.critical("Settingsfile seems to be demaged and could not be loaded as JSON object")
			piScreenUtils.logging.debug(err)

def checkSchedule():
	global scheduleDateFormate
	global schedule
	global scheduleFileModify
	global ignoreCronFrom
	global ignoreCronTo
	newScheduleFileModify = os.path.getmtime(piScreenUtils.paths.schedule)
	if newScheduleFileModify != scheduleFileModify:
		try:
			piScreenUtils.logging.info("Schedule seems to be changed")
			schedule = json.load(open(piScreenUtils.paths.schedule))
			scheduleFileModify = newScheduleFileModify
			if "ignoreCronFrom" in schedule:
				try: ignoreCronFrom = datetime.datetime.strptime(schedule["ignoreCronFrom"],scheduleDateFormate)
				except Exception as err:
					piScreenUtils.logging.error("Wrong datetime format in ignoreCronFrom")
					piScreenUtils.logging.debug(err)
					ignoreCronFrom = datetime.datetime.strptime("01.01.1900 00:00",scheduleDateFormate)
			if "ignoreCronTo" in schedule:
				try: ignoreCronTo = datetime.datetime.strptime(schedule["ignoreCronTo"],scheduleDateFormate)
				except Exception as err:
					piScreenUtils.logging.error("Wrong datetime format in ignoreCronTo")
					piScreenUtils.logging.debug(err)
					ignoreCronTo = datetime.datetime.strptime("01.01.1900 00:00",scheduleDateFormate)
			loadTrigger()
		except Exception as err:
			piScreenUtils.logging.critical("Schedulefile seems to be demaged and could not be loaded as JSON object")
			piScreenUtils.logging.debug(err)

###################
### Global vars ###
###################

HOST = "127.0.0.1"
PORT = 28888
bufferSize = 1024
active = True
mode = 0 #0 = None, 1 = Firefox, 2 = VLC, 3 = Impress
settingsFileModify = 0
scheduleFileModify = 0
settings = json.dumps({})
schedule = json.dumps({})
scheduleDateFormate = "%d.%m.%Y %H:%M"
ignoreCronFrom = datetime.datetime.strptime("01.01.1900 00:00",scheduleDateFormate)
ignoreCronTo = datetime.datetime.strptime("01.01.1900 00:00",scheduleDateFormate)
allTrigger = []
displayProtocol = ""
displayOrientation:int = 0
displayForceMode:bool = False
displayAction:int = 0
displayActionTries:int = 0
displayLastValue:str = "Unknown"
parameter = None
status = {"hdmi0Connected":None}

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

	piScreenUtils.logging.info("Start display threads")
	cecMode = cecHandler()
	ddcMode = ddcHandler()
	manuallyMode = manuallyHandler()
	cec.init("/dev/cec0") #Can be run only once
	cecMode.start()
	ddcMode.start()
	manuallyMode.start()

	piScreenUtils.logging.info("Start udp communcation socket")
	sH = socketHandler()
	sH.start()

	piScreenUtils.logging.info("Start schedule thread")
	checkSchedule()
	loadTrigger()	
	cronThread = cron()
	cronThread.start()

	piScreenUtils.logging.info("Start subprocesses")
	killAllSubprocesses()
	os.system("unclutter -idle 5 &")

	piScreenUtils.logging.info("Start observation")
	while active:
		#check if threads active
		if not firefoxMode.is_alive():
			piScreenUtils.logging.critical("Firefox handler thread is down!")
			firefoxMode = firefoxHandler()
			firefoxMode.start()
		if not vlcMode.is_alive():
			piScreenUtils.logging.critical("VLC handler thread is down!")
			vlcMode = vlcHandler()
			vlcMode.start()
		if not impressMode.is_alive():
			piScreenUtils.logging.critical("Impress handler thread is down!")
			impressMode = impressHandler()
			impressMode.start()
		if not cecMode.is_alive():
			piScreenUtils.logging.critical("CEC handler thread is down!")
			cecMode = cecHandler()
			cecMode.start()
		if not ddcMode.is_alive():
			piScreenUtils.logging.critical("DDC handler thread is down!")
			ddcMode = ddcHandler()
			ddcMode.start()
		if not manuallyMode.is_alive():
			piScreenUtils.logging.critical("Manually handler thread is down!")
			manuallyMode = manuallyHandler()
			manuallyMode.start()
		if not sH.is_alive():
			piScreenUtils.logging.critical("Socket handler thread is down!")
			sH = socketHandler()
			sH.start()
		if not cronThread.is_alive():
			piScreenUtils.logging.critical("Schedule thread is down!")
			cronThread = cron()
			cronThread.start()
			
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
		status["displayState"] = displayLastValue
		status["display"] = {}
		status["display"]["standbySet"] = (displayAction == 2)
		status["display"]["onSet"] = (displayAction == 1)
		status["modeInfo"] = {}
		status["modeInfo"]["mode"] = mode
		if mode == 1:
			status["modeInfo"]["info"] = firefoxMode.info
		elif mode == 2:
			status["modeInfo"]["info"] = vlcMode.info
		elif mode == 3:
			status["modeInfo"]["info"] = impressMode.info
		xrandr = subprocess.Popen(["xrandr"],stdout=subprocess.PIPE).communicate()[0].decode("utf-8")
		if "HDMI-1 connected" in xrandr:
			if status["hdmi0Connected"] == False: piScreenUtils.logging.info("Display is connected with HDMI0")
			status["hdmi0Connected"] = True
		else:
			if status["hdmi0Connected"] == True: piScreenUtils.logging.critical("Display is not connected with HDMI0!")
			status["hdmi0Connected"] = False
		found = ""
		for line in xrandr.split("\n"):
			if line.startswith("Screen 0:"): found = line
		if found == "":
			status["resulution"] = None
		else:
			try:
				found = found[found.index("current")+8:]
				status["resulution"] = found[:found.index(",")]
			except:
				status["resulution"] = None
				
		#createScreenshot
		try:
			os.system(f"scrot -z -o -t 50 {piScreenUtils.paths.screenshot}.jpg")
			os.system(f"mv {piScreenUtils.paths.screenshot}.jpg {piScreenUtils.paths.screenshot}")
			os.system(f"mv {piScreenUtils.paths.screenshot}-thumb.jpg {piScreenUtils.paths.screenshotThumbnail}")
		except Exception as err:
			piScreenUtils.logging.error("Error while creating screenshot")
			piScreenUtils.logging.debug(err)

		#checkSettings
		checkSettings()

		#checkSchedule
		checkSchedule()

		#checkDisplay orientation
		try:
			if piScreenUtils.isInt(displayOrientation):
				if subprocess.check_output(f"{piScreenUtils.paths.syscall} --get-display-orientation",shell=True).decode("utf-8").replace("\n","") != str(displayOrientation):
					piScreenUtils.logging.info("Change display orientation")
					os.system(f"{piScreenUtils.paths.syscall} --set-display-orientation --no-save {displayOrientation}")
		except Exception as err:
			piScreenUtils.logging.error("Unable to set display orientation")
			piScreenUtils.logging.debug(err)

		#Wait for new cycle
		time.sleep(5)

	piScreenUtils.logging.info("Stop core")
	active = False
	stopAllTrigger()
	killAllSubprocesses()
	os.unlink(piScreenUtils.paths.lockCore)