#!/usr/bin/python
import cec
import socket
import time

class cecTvStates: 
    def __init__(self):
        self._isOn = cecTv.is_on()
        self._isActiveSource = cec.is_active_source(1)
    @property
    def isOn(self):
        return self._isOn
    
    @isOn.setter
    def isOn(self, value):
        self._isOn = value
        
    @property
    def isActiveSource(self):
        return self._isActiveSource
    
    @isActiveSource.setter
    def isActiveSource(self, value):
        self._isActiveSource = value

def cecEvent(event, cmd):
    if cmd["opcode"] == cec.CEC_OPCODE_STANDBY:
        cecStates.isOn = False
    elif cmd["opcode"] == cec.CEC_OPCODE_ROUTING_CHANGE and cmd["parameters"] == b'\x00\x00@\x00': #https://community.openhab.org/t/hdmi-cec-binding/21246/112?page=6
        cecStates.isOn = True

def cmdSelector(data):
    if data == "exit":
        global enabled
        enabled = False
    elif data == "isOn":
        return cecStates.isOn
    elif data == "isActiveSource":
        cecStates.isActiveSource = cec.is_active_source(1) #Noch keine bessere Lösung gefunden dies Eventbasiert zu lösen.
        return cecStates.isActiveSource
    elif data == "setOn":
        cecTv.power_on()
        return None
    elif data == "setStandby":
        cecTv.standby()
        return None
    elif data == "setActiveSource":
        cec.set_active_source()
        return None

print("Loading...")
enabled = True
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #https://stackoverflow.com/questions/6380057/python-binding-socket-address-already-in-use
serversocket.bind(("127.0.0.1", 28888))
serversocket.listen()

cec.init("/dev/cec0")
cecTv = cec.Device(0)
cecStates = cecTvStates()

while enabled:
    try:
        if cecTv.transmit(cec.CEC_OPCODE_NONE):
            cecTv.transmit(cec.CEC_OPCODE_GIVE_DEVICE_POWER_STATUS) #Library is buggy! If you don't send this, the TV is marked as on until you change the state while this skript is running or waiting for a time.
            cec.add_callback(cecEvent,cec.EVENT_COMMAND)
            time.sleep(10) #Need a little time to take effect
            cecStates.isOn = cecTv.is_on()
            cecStates.isActiveSource = cec.is_active_source(1)
            print("Ready")
            while enabled:
                conn, addr = serversocket.accept()
                with conn:
                    returnValue = cmdSelector(conn.recv(1024).decode("utf-8"))
                    if returnValue != None:
                        conn.sendall(str(returnValue).encode("utf-8"))
        else:
            print("ERROR: HDMI seems not connected. Retry in 10 seconds")
            time.sleep(10)
    except:
        print("ERROR: Unexcpected Error. Will try again in 10 seconds")
        time.sleep(10)

serversocket.close()