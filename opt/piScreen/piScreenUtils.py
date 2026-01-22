import logging, logging.handlers, __main__, os

class Paths():
	SOFTWARE_DIR = "/opt/piScreen/"
	SETTINGS = f"{SOFTWARE_DIR}settings.json"
	SCHEDULE = f"{SOFTWARE_DIR}schedule.json"
	LOG = "/tmp/piScreen.log"
	SCREENSHOT = "/tmp/piScreenScreenshot.png"
	MANIFEST = f"{SOFTWARE_DIR}manifest.json"

class Constants():
	CORE_MGMT_PORT = 28888
	DATE_FORMATE = "%Y-%m-%d %H:%M"
	DEFAULT_DISPLAY_OUTPUT = "HDMI-A-1"

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

def setLogForRoot():
	if os.geteuid() == 0 and os.path.exists(Paths.LOG):
		os.chmod(Paths.LOG, 0o777)
		os.chown(Paths.LOG, 0, 0)

if "__file__" in __main__.__dir__():
	mainFileName = __main__.__file__[-(len(__main__.__file__)-__main__.__file__.rindex("/"))+1:]
	if mainFileName == "install.py": setLogForRoot()
else:
	mainFileName = "NoScript"

logging.basicConfig(
format=f"%(asctime)s [%(levelname)s] ({mainFileName}) %(funcName)s(%(lineno)d) | %(message)s",
level="INFO",
encoding="utf-8",
handlers=[logging.handlers.RotatingFileHandler(filename=Paths.LOG,mode="a",maxBytes=5242880,backupCount=2,encoding="utf-8",delay=0)])