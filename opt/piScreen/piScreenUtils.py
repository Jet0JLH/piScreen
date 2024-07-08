import logging, logging.handlers, __main__, os

class Paths():
	SOFTWARE_DIR = "/opt/piScreen/"
	SETTINGS = f"{SOFTWARE_DIR}settings.json"
	LOG = "/tmp/piScreen.log"

class Constants():
	CORE_MGMT_PORT = 28888
	DATE_FORMATE = "%Y-%m-%d %H:%M"

def isInt(s):
	if s == None: return False
	try: 
		int(s)
		return True
	except ValueError:
		return False

def isFloat(s):
	if s == None: return False
	try:
		float(s)
		return True
	except ValueError:
		return False

if "__file__" in __main__.__dir__():
	mainFileName = __main__.__file__[-(len(__main__.__file__)-__main__.__file__.rindex("/"))+1:]
else:
	mainFileName = "NoScript"

logging.basicConfig(
format=f"%(asctime)s [%(levelname)s] ({mainFileName}) %(funcName)s(%(lineno)d) | %(message)s",
level="DEBUG",
encoding="utf-8",
handlers=[logging.handlers.RotatingFileHandler(filename=Paths.LOG,mode="a",maxBytes=5242880,backupCount=2,encoding="utf-8",delay=0)])