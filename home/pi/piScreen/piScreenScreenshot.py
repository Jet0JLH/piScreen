#!/usr/bin/python
import json, time, os

def loadSettings():
	return json.load(open(f"{os.path.dirname(__file__)}/settings.json"))

while(True):
    os.system("/home/pi/piScreen/piScreenCmd.py --create-screenshot")
    time.sleep(5)