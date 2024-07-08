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

def evaluateResult(data:dict, results:dict, verbose:bool=False):
	#Expect results like [{"code": 0, result: "Success", "log": 0}, {"code": 1, result: "Error", "log": 3}]
	if "code" not in data: piScreenUtils.logging.error("There is no code in recieved data") ; return
	if data["code"] == -1:
		verbose and print("Core dosen't respond")
		piScreenUtils.logging.error("Core dosen't respond") ; return
	for result in results:
		if result["code"] == data["code"]:
			verbose and print(result["result"])
			if "log" in result:
				if result["log"] == 1: piScreenUtils.logging.debug(result["result"])
				elif result["log"] == 2: piScreenUtils.logging.warning(result["result"])
				elif result["log"] == 1: piScreenUtils.logging.error(result["result"])
			return
	verbose and print("Unknown result")
	piScreenUtils.logging.debug("Unknown result")


if __name__ == "__main__":
	sys.argv.pop(0) #Remove Path

	if "-h" in sys.argv or "--help" in sys.argv:
		printHelp()
		exit()

	for i, origItem in enumerate(sys.argv):
		item = origItem.lower()
		if (item == "--stop-core"): 
			evaluateResult(sendToCore({"cmd": 1}), [{"code": 0, "result": "Core will be stoped", "log": 0}])
			exit()
		elif (item == "--get-core-status"):
			evaluateResult(sendToCore({"cmd": 2}), [{"code": 0, "result": "Core is reachable"}], True)
			exit()
		elif(item == "--get-setting"):
			if i + 1 < len(sys.argv): #Load single value
				print(sendToCore({"cmd": 3, "path": sys.argv[i + 1]}))
			else:
				print(sendToCore({"cmd": 3}))
			exit()
		elif(item == "--set-setting"):
			if i + 3 < len(sys.argv):
				if sys.argv[i + 3].lower() in {"int", "float", "bool", "str", "json"}: print(sendToCore({"cmd": 4, "path": sys.argv[i + 1], "value": sys.argv[i + 2], "type": sys.argv[i + 3]}))
				else: print(f"{sys.argv[i + 3]} is no valid var type")
			elif i + 2 < len(sys.argv):
				print(sendToCore({"cmd": 4, "path": sys.argv[i + 1], "value": sys.argv[i + 2]}))
			elif i + 1 < len(sys.argv):
				print(sendToCore({"cmd": 4, "path": sys.argv[i + 1]}))
			else:
				print("Missing parameter")
			exit()
	
	printHelp()