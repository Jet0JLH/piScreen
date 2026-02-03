#!/usr/bin/python3
import piScreenUtils
import socket, json, sys, os, re

def printHelp():
	print(
"""This tool is used to control the piScreenCore service

=== General ===
-h or --help
	Show this information

--get-core-status
	Show if core is reachable

--get-status
	Returns a JSON String with statusinfos.

--stop-core
	Sends to core the command to halt the piScreenCore service

=== Hostcontrol ===
--do-reboot
	Restarts the Device.
--do-shutdown
	Shutdown the Device.
--get-desktop-configuration
	Returns the full desktop configuration.
--set-desktop-configuration [<--mode> <mode>] [<--wallpaper> <path>] [<--background-color> <hexColor>] [<--show-trash><0/1>] [<--show-documents><0/1>] [<--show-mounts><0/1>]
	Configure the desktop wallpaper.
	Possible modes are: color|stretch|fit|crop|center|tile|screen
	Hex colors has 6 characters and starts with a hash. Keep in mind, this character has to be escaped with a backslash!

=== Display ===
--get-display-resolution
	Return the current display resolution of output 1 and 2

--set-display-resolution [<width> <height>] [output]
	Set the display resolution or if no parameter is appended, it will reset resolution to auto.
	You can set the HDMI Output interface optional

--get-display-orientation
	Return the current display orientation of output 1 and 2

--set-display-orientation <orientation> [output]
	Set the display orientation with the value 0 to 7
	You can set the HDMI Output interface optional

--get-display-status
	Return the current display status.
	0 for off
	1 for on

--set-display-status <0/1> [output]
	Set the display status. You can set the HDMI Output interface optional.
	0 for off
	1 for on

=== Modes ===
--stop-modes
	Stops the current running mode and switches back to 'none'.
 == Firefox ==
--start-firefox <url>
	Starts the Browser or navigate it to new location if already open.
--do-firefox-restart
	Restart the Browser when active.
--do-firefox-refresh
	Refresh browser when active.
 == VLC ==
--start-vlc <pathToFile>
	Starts VLC Player.
--do-vlc-restart
	Restarts VLC Player.
--do-vlc-play
	Play the video if mode is VLC.
--do-vlc-pause
	Pause the video if mode is VLC.
--do-vlc-toggle-play-pause
	Pause/Play the video if mode is VLC.
--set-vlc-volume <valueInPercent>
	Set the audio volume to the given value.

=== Settings ===
--get-setting [setting/path]
	Get all settings or an explicit value

--set-setting <setting/path> <value> [type]
	Set value of setting. If a type is declared, the settings will be cast in this type.
	Allowed types are int, float, bool, str and json

=== Schedule ===
--get-schedule [schedule/path]
	Get all schedule entries or an explicit value

--set-schedule <schedule/path> <value> [type]
	Set value of schedule entry. If a type is declared, the schedule entry will be cast in this type.
	Allowed types are int, float, bool, str and json

 == Cron ==
--add-cron-entry [--minute <value>] [--hour <value>] [--day <value>] [--month <value>] [--year <value>] [--weekday <value>] [--enabled <0/1>] [--action <json>] [--commandset <commandsetID>]
	Add a cron entry to schedule and return its ID
	The value for time can be on of the following or a combination of them:
	* = 	Placeholder for every number (Keep in mind, this character has to be escaped with a backslash!)
	1 = 	An explicit number
	1,4,5 = A list of numbers
	1-5 =	A range of numbers
	*/2 =	Every n numbers
	If one of the time parameters is not passed, this value is replaced with *

--delete-cron-entry <--id <id>>
	Delete a cron entry by ID form schedule

--update-cron-entry <--id <id>> [--minute <value>] [--hour <value>] [--day <value>] [--month <value>] [--year <value>] [--weekday <value>] [--enabled <0/1>] [--action <json>] [--commandset <commandsetID>]
	Update an existing cron entrie by id

 == Commandsets ==
--add-commandset <--commands <jsonStructure>> [--name <name>]
	Adds an commandset to schedule and returns its ID

--delete-commandset <--id <id>>
	Delete a commandset by ID from schedule
""")

def sendToCore(data) -> dict:
	returnValue = {"code": -1}
	try:
		client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		client_socket.settimeout(2)
		client_socket.connect(("127.0.0.1", piScreenUtils.Constants.CORE_MGMT_PORT))
		client_socket.sendall(json.dumps(data).encode())
		try:
			returnValue = json.loads(client_socket.recv(16384))
		except:
			piScreenUtils.logging.error("Unable to get valid data from core")
		client_socket.close()
		piScreenUtils.logging.debug(f"Recieved following data: {returnValue}")
	except socket.error as e:
		piScreenUtils.logging.error("Error while sending data to core")
		piScreenUtils.logging.debug(f"Socket error: {e}")
	return returnValue

def evaluateResult(data:dict, results:dict, verbose:bool=False) -> dict:
	#Expect results like [{"code": 0, result: "Success", "log": 0}, {"code": 1, result: "Error", "log": 3}]
	#log=0 (no log), log=1 (debug), log=2 (info), log=3 (warning), log=4 (error)
	if "code" not in data: piScreenUtils.logging.error("There is no code in recieved data") ; return data
	if data["code"] == -1:
		verbose and print("Core dosen't respond")
		piScreenUtils.logging.error("Core dosen't respond") ; return data
	for result in results:
		if result["code"] == data["code"]:
			verbose and print(result["result"])
			if "log" in result:
				if result["log"] == 1: piScreenUtils.logging.debug(result["result"])
				elif result["log"] == 2: piScreenUtils.logging.info(result["result"])
				elif result["log"] == 3: piScreenUtils.logging.warning(result["result"])
				elif result["log"] == 4: piScreenUtils.logging.error(result["result"])
			return data
	verbose and print("Unknown result")
	piScreenUtils.logging.debug("Unknown result")
	return data

def getParameterValue(parameter:str, filter:dict={}) -> dict:
	## filter = {"values": ["true","false"], "regex": r"^[a-z]{3,10}$"}
	result = {"code": 1, "parameter": None}

	if parameter in sys.argv:
		indexOfElement = sys.argv.index(parameter) + 1
		if indexOfElement >= len(sys.argv) or sys.argv[indexOfElement].startswith("--"):
			print(f"No parameter for {parameter} given")
		else:
			found = False
			lowerParameter = sys.argv[indexOfElement].lower()
			if "values" in filter:
				for item in filter["values"]:
					if item == "[BOOL]" and lowerParameter in ["0", "1"]: found = True
					elif item == "[INT]" and piScreenUtils.isInt(lowerParameter): found = True
					elif item == "[FLOAT]" and piScreenUtils.isFloat(lowerParameter): found = True
					elif item == "[STRING]" and isinstance(lowerParameter, str): found = True
					elif item == "[JSON]" and piScreenUtils.isJson(lowerParameter): found = True
					elif lowerParameter == item: found = True
			if "regex" in filter:
				found = bool(re.fullmatch(filter["regex"], lowerParameter))
			if found:
				result["code"] = 0
				result["parameter"] = sys.argv[indexOfElement]
			else:
				print(f"No possible parameter for {parameter} selected")
	return result

if __name__ == "__main__":
	sys.argv.pop(0) #Remove Path

	if "-h" in sys.argv or "--help" in sys.argv:
		printHelp()
		exit()

	for i, origItem in enumerate(sys.argv):
		item = origItem.lower()
		if item == "--stop-core": 
			evaluateResult(sendToCore({"cmd": 1}), [{"code": 0, "result": "Core will be stoped", "log": 0}])
			exit()
		elif (item == "--get-core-status"):
			evaluateResult(sendToCore({"cmd": 2}), [{"code": 0, "result": "Core is reachable"}], True)
			exit()
		elif item == "--get-setting":
			if i + 1 < len(sys.argv): #Load single value
				print(sendToCore({"cmd": 3, "path": sys.argv[i + 1]}))
			else:
				print(sendToCore({"cmd": 3}))
			exit()
		elif item == "--set-setting":
			if i + 3 < len(sys.argv):
				if sys.argv[i + 3].lower() in {"int", "float", "bool", "str", "json"}: evaluateResult(sendToCore({"cmd": 4, "path": sys.argv[i + 1], "value": sys.argv[i + 2], "type": sys.argv[i + 3]}), [{"code": 0, "result": "Change setting successfully"}, {"code": 2, "result": "Missing parameter"}, {"code": 3, "result": "Unknown datatype", "log": 4}, {"code": 4, "result": "Datatype is not bool", "log": 3}, {"code": 5, "result": "Unable to convert datatype", "log": 3}], verbose=True)
				else: print(f"{sys.argv[i + 3]} is no valid var type")
			elif i + 2 < len(sys.argv):
				evaluateResult(sendToCore({"cmd": 4, "path": sys.argv[i + 1], "value": sys.argv[i + 2]}), [{"code": 0, "result": "Change setting successfully"}, {"code": 2, "result": "Missing parameter"}, {"code": 3, "result": "Unknown datatype", "log": 4}, {"code": 4, "result": "Datatype is not bool", "log": 3}, {"code": 5, "result": "Unable to convert datatype", "log": 3}], verbose=True)
			elif i + 1 < len(sys.argv):
				evaluateResult(sendToCore({"cmd": 4, "path": sys.argv[i + 1]}), [{"code": 0, "result": "Change setting successfully"}, {"code": 2, "result": "Missing parameter"}, {"code": 3, "result": "Unknown datatype", "log": 4}, {"code": 4, "result": "Datatype is not bool", "log": 3}, {"code": 5, "result": "Unable to convert datatype", "log": 3}], verbose=True)
			else:
				print("Missing parameter")
			exit()
		elif item == "--get-display-resolution":
			print(sendToCore({"cmd": 5}))
			exit()
		elif item == "--set-display-resolution":
			if i + 3 < len(sys.argv):
				print(sendToCore({"cmd": 6, "width": int(sys.argv[i + 1]), "height": int(sys.argv[i + 2]), "output": sys.argv[i + 3]}))
			elif i + 2 < len(sys.argv):
				if piScreenUtils.isInt(sys.argv[i + 1]) and piScreenUtils.isInt(sys.argv[i + 2]):
					print(sendToCore({"cmd": 6, "width": int(sys.argv[i + 1]), "height": int(sys.argv[i + 2])}))
				else:
					print("Parameter are not int")
			elif i + 1 < len(sys.argv):
				if piScreenUtils.isInt(sys.argv[i + 1]) == False:
					print(sendToCore({"cmd": 6, "output": sys.argv[i + 1]}))
				else:
					print("Two int parameter are requiered for resolution or one string for the name of the output")
			else:
				print(sendToCore({"cmd": 6}))
			exit()
		elif item == "--get-display-orientation":
			print(sendToCore({"cmd": 7}))
			exit()
		elif item == "--set-display-orientation":
			if i + 2 < len(sys.argv):
				if piScreenUtils.isInt(sys.argv[i + 1]):
					print(sendToCore({"cmd": 8, "orientation": int(sys.argv[i + 1]), "output": sys.argv[i + 2]}))
				else:
					print("Orientation is not an integer value")
			elif i + 1 < len(sys.argv):
				if piScreenUtils.isInt(sys.argv[i + 1]):
					print(sendToCore({"cmd": 8, "orientation": int(sys.argv[i + 1])}))
				else:
					print("Orientation is not an integer value")
			else:
				print("Missing parameter")
			exit()
		elif item == "--get-display-status":
			print(sendToCore({"cmd": 9}))
			exit()
		elif item == "--set-display-status":
			if i + 2 < len(sys.argv):
				if piScreenUtils.isInt(sys.argv[i + 1]):
					print(sendToCore({"cmd": 10, "value": int(sys.argv[i + 1]), "output": sys.argv[i + 2]}))
				else:
					print("Status is not an integer value")
			elif i + 1 < len(sys.argv):
				if piScreenUtils.isInt(sys.argv[i + 1]):
					print(sendToCore({"cmd": 10, "value": int(sys.argv[i + 1])}))
				else:
					print("Status is not an integer value")
			else:
				print("Missing parameter")
			exit()
		elif item == "--do-reboot":
			print(sendToCore({"cmd": 11}))
			exit()
		elif item == "--do-shutdown":
			print(sendToCore({"cmd": 12}))
			exit()
		elif item == "--set-desktop-configuration":
			msg = {"cmd": 13, "value":{}}
			if "--mode" in sys.argv:
				indexOfElement = sys.argv.index("--mode") + 1
				if indexOfElement >= len(sys.argv) or sys.argv[indexOfElement].startswith("--"):
					print("No parameter for --mode given")
				else:
					if sys.argv[indexOfElement].lower() in ["color", "stretch", "fit", "crop", "center", "tile", "screen"]:
						msg["value"]["mode"] = sys.argv[indexOfElement]
					else:
						print("No possible mode selected")
			if "--wallpaper" in sys.argv:
				indexOfElement = sys.argv.index("--wallpaper") + 1
				if indexOfElement >= len(sys.argv) or sys.argv[indexOfElement].startswith("--"):
					print("No parameter for --wallpaper given")
				else:
					if os.path.exists(sys.argv[indexOfElement]):
						msg["value"]["wallpaper"] = os.path.abspath(sys.argv[indexOfElement])
					else:
						print("Wallpaper File doesn't exist")
			if "--background-color" in sys.argv:
				indexOfElement = sys.argv.index("--background-color") + 1
				if indexOfElement >= len(sys.argv) or sys.argv[indexOfElement].startswith("--"):
					print("No parameter for --background-color given")
				else:
					import re
					if re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', sys.argv[indexOfElement]):
						msg["value"]["background-color"] = sys.argv[indexOfElement]
					else:
						print("Given color is no valid hex string")
			if "--show-trash" in sys.argv:
				indexOfElement = sys.argv.index("--show-trash") + 1
				if indexOfElement >= len(sys.argv) or sys.argv[indexOfElement].startswith("--"):
					print("No parameter for --show-trash given")
				else:
					if sys.argv[indexOfElement].lower() in ["true", "false", "1", "0"]:
						msg["value"]["show-trash"] = sys.argv[indexOfElement]
					else:
						print("Given value is no bool")
			if "--show-documents" in sys.argv:
				indexOfElement = sys.argv.index("--show-documents") + 1
				if indexOfElement >= len(sys.argv) or sys.argv[indexOfElement].startswith("--"):
					print("No parameter for --show-documents given")
				else:
					if sys.argv[indexOfElement].lower() in ["true", "false", "1", "0"]:
						msg["value"]["show-documents"] = sys.argv[indexOfElement]
					else:
						print("Given value is no bool")
			if "--show-mounts" in sys.argv:
				indexOfElement = sys.argv.index("--show-mounts") + 1
				if indexOfElement >= len(sys.argv) or sys.argv[indexOfElement].startswith("--"):
					print("No parameter for --show-mounts given")
				else:
					if sys.argv[indexOfElement].lower() in ["true", "false", "1", "0"]:
						msg["value"]["show-mounts"] = sys.argv[indexOfElement]
					else:
						print("Given value is no bool")
			if len(msg["value"]) > 0: print(sendToCore(msg))
			else: print("Nothing to do")
			exit()
		elif item == "--get-desktop-configuration":
			print(sendToCore({"cmd": 14}))
			exit()
		elif item == "--get-status":
			print(sendToCore({"cmd": 15}))
			exit()
		elif item == "--get-schedule":
			if i + 1 < len(sys.argv): #Load single value
				print(sendToCore({"cmd": 16, "path": sys.argv[i + 1]}))
			else:
				print(sendToCore({"cmd": 16}))
			exit()
		elif item == "--set-schedule":
			if i + 3 < len(sys.argv):
				if sys.argv[i + 3].lower() in {"int", "float", "bool", "str", "json"}: evaluateResult(sendToCore({"cmd": 17, "path": sys.argv[i + 1], "value": sys.argv[i + 2], "type": sys.argv[i + 3]}), [{"code": 0, "result": "Change schedule successfully"}, {"code": 2, "result": "Missing parameter"}, {"code": 3, "result": "Unknown datatype", "log": 4}, {"code": 4, "result": "Datatype is not bool", "log": 3}, {"code": 5, "result": "Unable to convert datatype", "log": 3}], verbose=True)
				else: print(f"{sys.argv[i + 3]} is no valid var type")
			elif i + 2 < len(sys.argv):
				evaluateResult(sendToCore({"cmd": 17, "path": sys.argv[i + 1], "value": sys.argv[i + 2]}), [{"code": 0, "result": "Change schedule successfully"}, {"code": 2, "result": "Missing parameter"}, {"code": 3, "result": "Unknown datatype", "log": 4}, {"code": 4, "result": "Datatype is not bool", "log": 3}, {"code": 5, "result": "Unable to convert datatype", "log": 3}], verbose=True)
			elif i + 1 < len(sys.argv):
				evaluateResult(sendToCore({"cmd": 17, "path": sys.argv[i + 1]}), [{"code": 0, "result": "Change schedule successfully"}, {"code": 2, "result": "Missing parameter"}, {"code": 3, "result": "Unknown datatype", "log": 4}, {"code": 4, "result": "Datatype is not bool", "log": 3}, {"code": 5, "result": "Unable to convert datatype", "log": 3}], verbose=True)
			else:
				print("Missing parameter")
			exit()
		elif item == "--add-cron-entry":
			msg = {"cmd": 18, "value":{}}
			enabled = getParameterValue("--enabled", {"values": ["[BOOL]"]})
			minute = getParameterValue("--minute", {"regex": piScreenUtils.Regex.cronMinute})
			hour = getParameterValue("--hour", {"regex": piScreenUtils.Regex.cronHour})
			day = getParameterValue("--day", {"regex": piScreenUtils.Regex.cronDay})
			month = getParameterValue("--month", {"regex": piScreenUtils.Regex.cronMonth})
			weekday = getParameterValue("--weekday", {"regex": piScreenUtils.Regex.cronWeekday})
			year = getParameterValue("--year", {"regex": piScreenUtils.Regex.cronYear})
			action = getParameterValue("--action", {"values": ["[JSON]"]})
			commandset = getParameterValue("--commandset", {"values": ["[INT]"]})
			if enabled["code"] == 0: msg["value"]["enabled"] = enabled["parameter"]
			if minute["code"] == 0: msg["value"]["minute"] = minute["parameter"]
			if hour["code"] == 0: msg["value"]["hour"] = hour["parameter"]
			if day["code"] == 0: msg["value"]["day"] = day["parameter"]
			if month["code"] == 0: msg["value"]["month"] = month["parameter"]
			if weekday["code"] == 0: msg["value"]["hour"] = hour["parameter"]
			if year["code"] == 0: msg["value"]["year"] = year["parameter"]
			if action["code"] == 0: msg["value"]["action"] = json.loads(action["parameter"])
			if commandset["code"] == 0: msg["value"]["commandset"] = int(commandset["parameter"])
			if len(msg["value"]) > 0: print(sendToCore(msg))
			else: print("Missing parameter")
			exit()
		elif item == "--delete-cron-entry":
			msg = {"cmd": 19, "value":{}}
			entryID = getParameterValue("--id", {"values": ["[INT]"]})
			if entryID["code"] == 0: msg["value"]["id"] = entryID["parameter"]
			if len(msg["value"]) > 0: print(sendToCore(msg))
			else: print("Missing parameter")
			exit()
		elif item == "--update-cron-entry":
			msg = {"cmd": 20, "value":{}}
			entryID = getParameterValue("--id", {"values": ["[INT]"]})
			if entryID["code"] == 0: msg["value"]["id"] = entryID["parameter"]
			else: print("ID is missing") ; exit()
			enabled = getParameterValue("--enabled", {"values": ["[BOOL]"]})
			minute = getParameterValue("--minute", {"regex": piScreenUtils.Regex.cronMinute})
			hour = getParameterValue("--hour", {"regex": piScreenUtils.Regex.cronHour})
			day = getParameterValue("--day", {"regex": piScreenUtils.Regex.cronDay})
			month = getParameterValue("--month", {"regex": piScreenUtils.Regex.cronMonth})
			weekday = getParameterValue("--weekday", {"regex": piScreenUtils.Regex.cronWeekday})
			year = getParameterValue("--year", {"regex": piScreenUtils.Regex.cronYear})
			action = getParameterValue("--action", {"values": ["[JSON]"]})
			commandset = getParameterValue("--commandset", {"values": ["[INT]"]})
			if enabled["code"] == 0: msg["value"]["enabled"] = enabled["parameter"]
			if minute["code"] == 0: msg["value"]["minute"] = minute["parameter"]
			if hour["code"] == 0: msg["value"]["hour"] = hour["parameter"]
			if day["code"] == 0: msg["value"]["day"] = day["parameter"]
			if month["code"] == 0: msg["value"]["month"] = month["parameter"]
			if weekday["code"] == 0: msg["value"]["hour"] = hour["parameter"]
			if year["code"] == 0: msg["value"]["year"] = year["parameter"]
			if action["code"] == 0: msg["value"]["action"] = json.loads(action["parameter"])
			if commandset["code"] == 0: msg["value"]["commandset"] = int(commandset["parameter"])
			print(sendToCore(msg))
			exit()
		elif item == "--add-commandset":
			msg = {"cmd": 21, "value": {"name": None, "commands": []}}
			commands = getParameterValue("--commands", {"values": ["[JSON]"]})
			name = getParameterValue("--name", {"values": ["[STRING]"]})
			if commands["code"] == 0: 
				msg["value"]["commands"] = json.loads(commands["parameter"])
			else:
				print("No commands in json format given")
				exit()
			if name["code"] == 0:
				msg["value"]["name"] = name["parameter"]
			print(sendToCore(msg))
			exit()
		elif item == "--delete-commandset":
			msg = {"cmd": 22, "value":{}}
			entryID = getParameterValue("--id", {"values": ["[INT]"]})
			if entryID["code"] == 0: msg["value"]["id"] = entryID["parameter"]
			if len(msg["value"]) > 0: print(sendToCore(msg))
			else: print("Missing parameter")
			exit()
		elif item == "--stop-modes":
			print(sendToCore({"cmd": 99}))
			exit()
		elif item == "--start-firefox":
			if i + 1 < len(sys.argv):
				print(sendToCore({"cmd": 100, "value": sys.argv[i + 1]}))
			else:
				print("Missing parameter")
			exit()
		elif item == "--do-firefox-restart":
			print(sendToCore({"cmd": 101}))
			exit()
		elif item == "--do-firefox-refresh":
			print(sendToCore({"cmd": 102}))
			exit()
		elif item == "--start-vlc":
			if i + 1 < len(sys.argv):
				print(sendToCore({"cmd": 200, "value": sys.argv[i + 1]}))
			else:
				print("Missing parameter")
			exit()
		elif item == "--do-vlc-restart":
			print(sendToCore({"cmd": 204}))
			exit()
		elif item == "--do-vlc-play":
			print(sendToCore({"cmd": 201}))
			exit()
		elif item == "--do-vlc-pause":
			print(sendToCore({"cmd": 203}))
			exit()
		elif item == "--do-vlc-toggle-play-pause":
			print(sendToCore({"cmd": 202}))
			exit()
		elif item == "--set-vlc-volume":
			if i + 1 < len(sys.argv):
				if piScreenUtils.isInt(sys.argv[i + 1]) and int(sys.argv[i + 1]) >= 0 and int(sys.argv[i + 1]) <= 100:
					print(sendToCore({"cmd": 205, "value": int(sys.argv[i + 1])}))
				else:
					print("Volume is not an integer value between 0 and 100")
			else:
				print("Missing parameter")
			exit()
	printHelp()