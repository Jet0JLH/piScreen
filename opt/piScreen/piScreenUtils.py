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

class Regex():
	hexColor = r"^#(?:[0-9a-fA-F]{3}){1,2}$"
	cronMinute = r"^(\*|([0-5]?\d))(-([0-5]?\d))?(\/([1-5]?\d))?(,(\*|([0-5]?\d))(-([0-5]?\d))?(\/([1-5]?\d))?)*$"
	cronHour = r"^(\*|([01]?\d|2[0-3]))(-([01]?\d|2[0-3]))?(\/([01]?\d|2[0-3]))?(,(\*|([01]?\d|2[0-3]))(-([01]?\d|2[0-3]))?(\/([01]?\d|2[0-3]))?)*$"
	cronDay = r"^(\*|([1-9]|[12]\d|3[01]))(-([1-9]|[12]\d|3[01]))?(\/([1-9]|[12]\d|3[01]))?(,(\*|([1-9]|[12]\d|3[01]))(-([1-9]|[12]\d|3[01]))?(\/([1-9]|[12]\d|3[01]))?)*$"
	cronMonth = r"^(\*|([1-9]|1[0-2]))(-([1-9]|1[0-2]))?(\/([1-9]|1[0-2]))?(,(\*|([1-9]|1[0-2]))(-([1-9]|1[0-2]))?(\/([1-9]|1[0-2]))?)*$"
	cronWeekday = r"^(\*|[0-7])(-[0-7])?(\/[0-7])?(,(\*|[0-7])(-[0-7])?(\/[0-7])?)*$"
	cronYear = r"^(\*|\d{4})(-\d{4})?(\/\d+)?(,(\*|\d{4})(-\d{4})?(\/\d+)?)*$"

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