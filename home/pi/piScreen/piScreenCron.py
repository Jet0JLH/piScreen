#!/usr/bin/python
import json
import datetime
import sys
import os

syscall = '/home/pi/piScreen/piScreenCmd.py'

def printHelp():
	print("Run this cron skript with the following parameter\n\n--check-now\n\tThis will check if there is something to do now\n\n--do-last-run\n\tThis will execute the command that should run last\n\tIntended for reboot sequence")

def executeCommand(jsonData):
	if jsonData["mode"] == 0:
		verbose and print("Trigger Standby")
		os.system(f"{syscall} --screen-standby")
	elif jsonData["mode"] == 1:
		verbose and print("Trigger Display On")
		os.system(f"{syscall} --screen-on")
	elif jsonData["mode"] == 2:
		verbose and print("Restart Browser")
		os.system(f"{syscall} --stop-browser")
	elif jsonData["mode"] == 3:
		verbose and print("Reboot")
		os.system(f"sudo {syscall} --reboot")
	elif jsonData["mode"] == 4:
		verbose and print("Shutdown")
		os.system(f"sudo {syscall} --shutdown")

now = datetime.datetime.today()
jsonFile = "/home/pi/piScreen/cron.json"
jsonData = json.load(open(jsonFile))
verbose = False

if len(sys.argv) > 1:
	if len(sys.argv) > 2:
		if sys.argv[2] == "-v":
			verbose = True

	

	if jsonData["scheduleExclude"]["enabled"]:
		scheduleExcludeFromString = str(jsonData["scheduleExclude"]["from"]["year"])+"-"+str(jsonData["scheduleExclude"]["from"]["month"])+"-"+str(jsonData["scheduleExclude"]["from"]["day"])+" "+str(jsonData["scheduleExclude"]["from"]["hour"])+":"+str(jsonData["scheduleExclude"]["from"]["minute"])
		scheduleExcludeToString = str(jsonData["scheduleExclude"]["to"]["year"])+"-"+str(jsonData["scheduleExclude"]["to"]["month"])+"-"+str(jsonData["scheduleExclude"]["to"]["day"])+" "+str(jsonData["scheduleExclude"]["to"]["hour"])+":"+str(jsonData["scheduleExclude"]["to"]["minute"])
		scheduleExcludeFrom = datetime.datetime.strptime(scheduleExcludeFromString, '%Y-%m-%d %H:%M')
		scheduleExcludeTo = datetime.datetime.strptime(scheduleExcludeToString, '%Y-%m-%d %H:%M')
		if scheduleExcludeFrom < now < scheduleExcludeTo:
			verbose and print("We are in exclusion time. Nothing will happen")
			exit()
	if sys.argv[1] == "--do-last-run":
		#Get last entry
		lastEntry = {'enabled': True, 'mode': -1, 'day': -1, 'hour': -1, 'minute': -1}
		lastEntryOfWeek = {'enabled': True, 'mode': -1, 'day': -1, 'hour': -1, 'minute': -1}
		for x in jsonData["schedule"]:
			if x["enabled"]:
				if x["day"] < now.weekday() or (x["day"] == now.weekday() and x["hour"] < now.hour) or (x["day"] == now.weekday() and x["hour"] == now.hour and x["minute"] < now.minute):
					if x["day"] > lastEntry["day"] or (x["day"] == lastEntry["day"] and x["hour"] > lastEntry["hour"]) or (x["day"] == lastEntry["day"] and x["hour"] == lastEntry["hour"] and x["minute"] > lastEntry["minute"]):
						lastEntry = x
				if x["day"] > lastEntryOfWeek["day"] or (x["day"] == lastEntryOfWeek["day"] and x["hour"] > lastEntryOfWeek["hour"]) or (x["day"] == lastEntryOfWeek["day"] and x["hour"] == lastEntryOfWeek["hour"] and x["minute"] > lastEntryOfWeek["minute"]):
					lastEntryOfWeek = x
		if lastEntry["day"] == -1:
			lastEntry = lastEntryOfWeek

		if lastEntry["day"] != -1:
			executeCommand(lastEntry)
	elif sys.argv[1] == "--check-now":
		#Get Entry of now
		jsonData["schedule"][:] = [x for x in jsonData["schedule"] if x["enabled"] and x["day"] == now.weekday() and x["hour"] == now.hour and x["minute"] == now.minute]
		if len(jsonData["schedule"]) > 0:
			executeCommand(jsonData["schedule"][0])
		else:
			verbose and print("Nothing to do")
	else:
		printHelp()
else:
	printHelp()

