#!/usr/bin/python3
import cec, time, os, subprocess, monitorcontrol

ramdisk="/media/ramdisk/"
displayStatus=f"{ramdisk}piScreenDisplay.txt"
displayOff=f"{ramdisk}piScreenDisplayOff"
displayOn=f"{ramdisk}piScreenDisplayOn"
displayStandby=f"{ramdisk}piScreenDisplayStandby"
displaySwitchChannel=f"{ramdisk}piScreenDisplaySwitch"
displayCEC=f"{ramdisk}piScreenDisplayCEC"
displayDDC=f"{ramdisk}piScreenDisplayDDC"
displayMANUALLY=f"{ramdisk}piScreenDisplayMANUALLY"

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
					open(displayStatus,"w").write("on")
				else:
					open(displayStatus,"w").write("standby")
			except:
				pass

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
			self.device.power_on()
		elif cmd == "setStandby":
			self.device.transmit(cec.CEC_OPCODE_STANDBY)
		elif cmd == "setActiveSource":
			cec.set_active_source()


def doCEC():
	cecObj = cecElement(cec.CECDEVICE_TV)
	while os.path.exists(displayCEC):
		for i in range(60) and os.path.exists(displayCEC):
			if os.path.exists(displayOff):
				cecObj.cmdSelector("setStandby")
				try:
					os.remove(displayOff)
				except: 
					pass
			elif os.path.exists(displayOn):
				cecObj.cmdSelector("setOn")
				try:
					os.remove(displayOn)
				except: 
					pass
			elif os.path.exists(displayStandby):
				cecObj.cmdSelector("setStandby")
				try:
					os.remove(displayStandby)
				except: 
					pass
			elif os.path.exists(displaySwitchChannel):
				cecObj.cmdSelector("setActiveSource")
				try:
					os.remove(displaySwitchChannel)
				except: 
					pass
			time.sleep(1)
		cecObj.updateStatus()

def doDDC():
	lastValue = None
	while os.path.exists(displayDDC):
		monitors = monitorcontrol.get_monitors()
		if len(monitors) > 0:
			with monitors[0]:
				mode = monitors[0].get_power_mode()
				if os.path.exists(displayOff):
					try:
						monitors[0].set_power_mode(mode.off_soft)
						os.remove(displayOff)
					except: 
						pass
				elif os.path.exists(displayOn):
					try:
						monitors[0].set_power_mode(mode.on)
						os.remove(displayOn)
					except: 
						pass
				elif os.path.exists(displayStandby):
					try:
						monitors[0].set_power_mode(mode.standby)
						os.remove(displayStandby)
					except: 
						pass
				elif os.path.exists(displaySwitchChannel):
						#Not implemented yet
						#monitors[0].set_input_source()
					try:
						os.remove(displaySwitchChannel)
					except: 
						pass

			if mode == mode.on:
				if lastValue != "on": lastValue = "on" ; open(displayStatus,"w").write("on")
			elif mode == mode.off_hard or mode == mode.off_soft:
				if lastValue != "off": lastValue = "off" ; open(displayStatus,"w").write("off")
			elif mode == mode.standby or mode == mode.suspend:
				if lastValue != "standby": lastValue = "standby" ; open(displayStatus,"w").write("standby")
		time.sleep(1)


def doMANUALLY():
	lastValue = None
	os.system("xset +dpms")
	os.system("xset s 0")
	os.system("xset dpms 0 0 0")
	while os.path.exists(displayMANUALLY):
		status = str(subprocess.check_output(["xset", "-q"]))
		if "Monitor is Off" in status:
			if lastValue != "off": lastValue = "off" ; open(displayStatus,"w").write("off")
		elif "Monitor is On" in status:
			if lastValue != "on": lastValue = "on" ; open(displayStatus,"w").write("on")
		elif "Monitor is in Standby" in status or "Monitor is in Suspend" in status:
			if lastValue != "standby": lastValue = "standby" ; open(displayStatus,"w").write("standby")
		
		if os.path.exists(displayOff):
			os.system("xset dpms force off")
			try:
				os.remove(displayOff)
			except: 
				pass
		elif os.path.exists(displayOn):
			os.system("xset dpms force on")
			try:
				os.remove(displayOn)
			except: 
				pass
		elif os.path.exists(displayStandby):
			os.system("xset dpms force off")
			try:
				os.remove(displayStandby)
			except: 
				pass
		elif os.path.exists(displaySwitchChannel):
			#Not possible in this mode
			try:
				os.remove(displaySwitchChannel)
			except: 
				pass
		time.sleep(1)
	os.system("xset -dpms")

		

if __name__ == "__main__":
	cec.init("/dev/cec0") #Can be run only once
	os.environ["DISPLAY"] = ":0"
	while True:
		if os.path.exists(displayCEC):	
			doCEC()
		elif os.path.exists(displayDDC):
			doDDC()
		elif os.path.exists(displayMANUALLY):
			doMANUALLY()
		time.sleep(1)