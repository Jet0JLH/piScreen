#!/usr/bin/python3
import cec, time, os, subprocess, monitorcontrol, piScreenUtils, threading, json

enabled = True

class cecElement:
	device:cec.Device = None
	_isOn:bool = None
	_isActiveSource:bool = None #Bug, value only set when source changed

	@property
	def isOn(self) -> bool:
		return self._isOn

	@isOn.setter
	def isOn(self,value:bool):
		if value != self._isOn:
			self._isOn = value
			try:
				if value:
					piScreenUtils.logging.info("Display status changed to on")
					open(piScreenUtils.paths.displayStatus,"w").write("on")
				else:
					piScreenUtils.logging.info("Display status changed to standby")
					open(piScreenUtils.paths.displayStatus,"w").write("standby")
			except:
				piScreenUtils.logging.error("Unable to update displaystatus in file")

	@property
	def isActiveSource(self):
		return self._isActiveSource
    
	@isActiveSource.setter
	def isActiveSource(self, value:bool):
		if value != self._isActiveSource:
			self._isActiveSource = value

	def __init__(self,deviceID:int) -> None:
		self.device = cec.Device(deviceID)
		cec.add_callback(self.cecEvent,cec.EVENT_COMMAND)
		self.updateStatus()

	def updateStatus(self):
		self.device.transmit(cec.CEC_OPCODE_GIVE_DEVICE_POWER_STATUS)

	def cecEvent(self,event, cmd):
		opcodeName = "Unknown"
		for key, value in cec.__dict__.items():
			if value == cmd["opcode"]: opcodeName = key
		piScreenUtils.logging.debug(f"{opcodeName} -> {cmd}")
		if cmd["opcode"] == cec.CEC_OPCODE_STANDBY:
			self.isOn = False
		elif cmd["opcode"] == cec.CEC_OPCODE_ROUTING_CHANGE: #https://community.openhab.org/t/hdmi-cec-binding/21246/112?page=6
			self.isOn = True
			if cmd["parameters"] == b'\x00\x000\x00': self.isActiveSource = True
			elif cmd["parameters"] == b'0\x00\x00\x00': self.isActiveSource = False
		elif cmd["opcode"] == cec.CEC_OPCODE_REPORT_POWER_STATUS:
			if cmd["parameters"] == b'\x01': self.isOn = False
			if cmd["parameters"] == b'\x00': self.isOn = True
		elif cmd["opcode"] == cec.CEC_OPCODE_ACTIVE_SOURCE:
			if cmd["parameters"] == b'\x00\x00': self.isOn = True ; self.isActiveSource = False
	
	def cmdSelector(self,cmd:str):
		if cmd == "exit":
			pass
		elif cmd == "setOn":
			piScreenUtils.logging.info("Set display on")
			self.device.power_on()
		elif cmd == "setStandby":
			piScreenUtils.logging.info("Set display standby")
			self.device.transmit(cec.CEC_OPCODE_STANDBY)
		elif cmd == "setActiveSource":
			piScreenUtils.logging.info("Set display active source")
			cec.set_active_source()


def doCEC():
	while True:
		for i in range(5):
			if not settings.values.protocol == "cec": return
			if controlFileHandeling(piScreenUtils.paths.displayOff,not cecObj.isOn):
				cecObj.cmdSelector("setStandby")
			elif controlFileHandeling(piScreenUtils.paths.displayOn,cecObj.isOn):
				cecObj.cmdSelector("setOn")
			elif controlFileHandeling(piScreenUtils.paths.displayStandby,not cecObj.isOn):
				cecObj.cmdSelector("setStandby")
			elif os.path.exists(piScreenUtils.paths.displaySwitchChannel):
				cecObj.cmdSelector("setActiveSource")
				try:
					os.remove(piScreenUtils.paths.displaySwitchChannel)
				except: 
					piScreenUtils.logging.error(f"Unable to remove {piScreenUtils.paths.displaySwitchChannel}")
			time.sleep(1)
		cecObj.updateStatus()

def doDDC():
	lastValue = None
	while settings.values.protocol == "ddc":
		monitors = monitorcontrol.get_monitors()
		if len(monitors) > 0:
			with monitors[0]:
				try:
					mode = monitors[0].get_power_mode()
					try:
						if mode == mode.on:
							if lastValue != "on": lastValue = "on" ; piScreenUtils.logging.info("Display status changed to on") ; open(piScreenUtils.paths.displayStatus,"w").write("on")
						elif mode == mode.off_hard or mode == mode.off_soft:
							if lastValue != "off": lastValue = "off" ; piScreenUtils.logging.info("Display status changed to off") ; open(piScreenUtils.paths.displayStatus,"w").write("off")
						elif mode == mode.standby or mode == mode.suspend:
							if lastValue != "standby": lastValue = "standby" ; piScreenUtils.logging.info("Display status changed to standby") ; open(piScreenUtils.paths.displayStatus,"w").write("standby")
					except:
						piScreenUtils.logging.error("Unable to update display ind file")
					if controlFileHandeling(piScreenUtils.paths.displayOff,lastValue=="off" or lastValue=="standby"):
						piScreenUtils.logging.info("Set display off")
						try:
							monitors[0].set_power_mode(mode.off_hard)
						except: 
							piScreenUtils.logging.error("Unable to set mode to off")
					elif controlFileHandeling(piScreenUtils.paths.displayOn,lastValue=="on"):
						piScreenUtils.logging.info("Set display on")
						try:
							monitors[0].set_power_mode(mode.on)
						except: 
							piScreenUtils.logging.error("Unable to set mode to on")
					elif controlFileHandeling(piScreenUtils.paths.displayStandby,lastValue=="off" or lastValue=="standby"):
						piScreenUtils.logging.info("Set display standby")
						try:
							#Code 04 is for standby, but not every system supports it, so we decided to use 05 instead
							monitors[0].set_power_mode(mode.off_hard)
						except: 
							piScreenUtils.logging.error("Unable to set mode to off")
					elif os.path.exists(piScreenUtils.paths.displaySwitchChannel):
							#Not implemented yet
							#monitors[0].set_input_source()
						piScreenUtils.logging.info("Set display input source")
						try:
							os.remove(piScreenUtils.paths.displaySwitchChannel)
						except: 
							piScreenUtils.logging.error(f"Unable to remove {piScreenUtils.paths.displaySwitchChannel}")
				except:
					piScreenUtils.logging.error("Trouble with reading DDC/CI power mode")
		else:
			piScreenUtils.logging.warning("Unable to find display")
		time.sleep(1)


def doMANUALLY():
	lastValue = None
	os.system("xset +dpms")
	os.system("xset s 0")
	os.system("xset dpms 0 0 0")
	while settings.values.protocol == "manually":
		status = str(subprocess.check_output(["xset", "-q"]))
		if "Monitor is Off" in status:
			if lastValue != "off": lastValue = "off" ; piScreenUtils.logging.info("Display status changed to off") ; open(piScreenUtils.paths.displayStatus,"w").write("off")
		elif "Monitor is On" in status:
			if lastValue != "on": lastValue = "on" ; piScreenUtils.logging.info("Display status changed to on") ; open(piScreenUtils.paths.displayStatus,"w").write("on")
		elif "Monitor is in Standby" in status or "Monitor is in Suspend" in status:
			if lastValue != "standby": lastValue = "standby" ; piScreenUtils.logging.info("Display status changed to standby") ; open(piScreenUtils.paths.displayStatus,"w").write("standby")
		
		if controlFileHandeling(piScreenUtils.paths.displayOff,lastValue=="off" or lastValue=="standby"): 
			piScreenUtils.logging.info("Set display off")
			os.system("xset dpms force off")
		elif controlFileHandeling(piScreenUtils.paths.displayOn,lastValue=="on"):
			piScreenUtils.logging.info("Set display on")
			os.system("xset dpms force on")
		elif controlFileHandeling(piScreenUtils.paths.displayStandby,lastValue=="off" or lastValue=="standby"):
			piScreenUtils.logging.info("Set display standby")
			os.system("xset dpms force off")
		elif os.path.exists(piScreenUtils.paths.displaySwitchChannel):
			#Not possible in this mode
			piScreenUtils.logging.info("Can not switch channel in manually mode")
			try:
				os.remove(piScreenUtils.paths.displaySwitchChannel)
			except: 
				piScreenUtils.logging.error(f"Unable to remove {piScreenUtils.paths.displaySwitchChannel}")
		time.sleep(1)
	os.system("xset -dpms")

def controlFileHandeling(file:str,ready:bool) -> bool:
	if os.path.exists(file):
		if ready:
			try:
				if not settings.values.force: os.remove(file)
			except:
				piScreenUtils.logging.error(f"Unable to remove {file}")
			return False
		value = open(file,"r").read().strip()
		if piScreenUtils.isInt(value):
			value = int(value)
		else:
			value = 0
		if value > 60: #Amount of trys
			piScreenUtils.logging.error("Unable to change screen status")
			try:
				os.remove(file)
			except:
				piScreenUtils.logging.error(f"Unable to remove {file}")
			return False
		value = value + 1
		open(file,"w").write(str(value))
		return True
	return False

class settingsWatcher(threading.Thread):
	fileModify = 0
	config = json.dumps({})
	class values:
		protocol = "cec"
		orientation = 0
		force = False
	def __init__(self):
		threading.Thread.__init__(self)
		self.start()

	def run(self):
		while enabled:
			fileModify = os.path.getmtime(piScreenUtils.paths.settings)
			if fileModify == self.fileModify: continue
			try:
				piScreenUtils.logging.info("Config seems to be changed")
				self.config = json.load(open(piScreenUtils.paths.settings))
				self.fileModify = fileModify
				if "settings" in self.config and "display" in self.config["settings"]:
					if "protocol" in self.config["settings"]["display"]: self.values.protocol = self.config["settings"]["display"]["protocol"]
					if "orientation" in self.config["settings"]["display"]: self.values.orientation = self.config["settings"]["display"]["orientation"]
					if "force" in self.config["settings"]["display"]: self.values.force = self.config["settings"]["display"]["force"]
			except:
				piScreenUtils.logging.critical("Settingsfile seems to be demaged and could not be loaded as JSON object")
			time.sleep(5)

if __name__ == "__main__":
	piScreenUtils.logging.info("Startup")
	settings = settingsWatcher()
	cec.init("/dev/cec0") #Can be run only once
	cecObj = cecElement(cec.CECDEVICE_TV)
	os.environ["DISPLAY"] = ":0"
	while enabled:
		if settings.values.protocol == "cec":
			piScreenUtils.logging.info("Switch to CEC mode")	
			doCEC()
		elif settings.values.protocol == "ddc":
			piScreenUtils.logging.info("Switch to DDC mode")
			doDDC()
		elif settings.values.protocol == "manually":
			piScreenUtils.logging.info("Switch to MANUALLY mode")
			doMANUALLY()
		time.sleep(1)