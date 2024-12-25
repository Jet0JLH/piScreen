#!/usr/bin/python3
import piScreenUtils
import socket, json, sys

def printHelp():
	print(
"""This tool is used to control the piScreenCore service

=== General ===
-h or --help
	Show this information

--get-core-status
	Show if core is reachable

--stop-core
	Sends to core the command to halt the piScreenCore service

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
--stop-mode
	Stops the current running mode and switches back to 'none'.
 == Firefox ==
--start-firefox <url>
	Starts the Browser or navigate it to new location if already open.

=== Settings ===
--get-setting [setting/path]
	Get all settings or an explicit value

--set-setting <setting/path> <value> [type]
	Set value of setting. If a type is declared, the settings will be cast in this type.
	Allowed types are int, float, bool, str and json

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
		elif item == "--stop-modes":
			print(sendToCore({"cmd": 99}))
			exit()
		elif item == "--start-firefox":
			if i + 1 < len(sys.argv):
				print(sendToCore({"cmd": 100, "value": sys.argv[i + 1]}))
			else:
				print("Missing parameter")
			exit()
	
	printHelp()