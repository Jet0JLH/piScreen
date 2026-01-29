import piScreenUtils, json, datetime, os, copy
class JsonData:
	def loadFile(self):
		if not os.path.exists(self.path): piScreenUtils.logging.error(f"Unable to find {self.path}") ; return
		try:
			piScreenUtils.logging.debug(f"Load JSON from {self.path}")
			self.file = json.load(open(self.path))
			self.origFile = copy.deepcopy(self.file)
			self.whenChanged = os.path.getmtime(self.path)
			self.whenSaved = os.path.getmtime(self.path)
		except: piScreenUtils.logging.error(f"Unable to load {self.path}") ; return

	def saveFile(self, orig:bool=False):
		if not os.path.exists(self.path): piScreenUtils.logging.error(f"Unable to find {self.path}") ; return
		try:
			with open(self.path, "w") as f:
				if orig:
					piScreenUtils.logging.debug(f"Save original JSON to {self.path}")
					json.dump(self.origFile, f, indent=4)
				else:
					piScreenUtils.logging.debug(f"Save JSON to {self.path}")
					json.dump(self.file, f, indent=4)
					self.origFile = copy.deepcopy(self.file)
			self.whenSaved = os.path.getmtime(self.path)
		except:
			piScreenUtils.logging.error(f"Unable to save {self.path}")

	def __init__(self, path:str, autosave:bool=False):
		self.path = path
		self.file = {}
		self.origFile = {}
		self.autosave = autosave
		self.whenChanged = datetime.datetime.strptime("1900-01-01 00:00", piScreenUtils.Constants.DATE_FORMATE)
		self.whenSaved = datetime.datetime.strptime("1900-01-01 00:00",piScreenUtils.Constants.DATE_FORMATE)
		if path != "": self.loadFile()

	def getValue(self, keyPath:str, orig:bool=False):
		keys = keyPath.split('/')
		if orig: value = self.origFile 
		else: value = self.file
		try:
			for key in keys:
				value = value[key]
			return value
		except KeyError:
			return None

	def getAllValues(self, orig:bool=False):
		if orig: return self.origFile
		else: return self.file

	def setValue(self, keyPath:str, value, convert:bool=True, orig:bool=False):
		oldValue = self.getValue(keyPath,orig)
		if oldValue == value: piScreenUtils.logging.debug(f"Value {value} for key {keyPath} is already set") ; return
		keys = keyPath.split('/')
		if orig: currentDict = self.origFile
		else: currentDict = self.file
		for key in keys[:-1]:
			if key not in currentDict:
				currentDict[key] = {}
			currentDict = currentDict[key]
		if value is None:
			currentDict.pop(keys[-1], None)
		else:
			try: #Try to convert value to old datatype
				if convert:
					if type(oldValue) == int: value = int(value)
					if type(oldValue) == float: value = float(value)
					if type(oldValue) == bool:
						if value.lower() == "true": value = True
						elif value.lower() == "false": value = False
			except:
				piScreenUtils.logging.info(f"Changed setting seems to change datatype from {type(oldValue)} to String")
			currentDict[keys[-1]] = value
		self.whenChanged = datetime.datetime.now()
		if self.autosave: self.saveFile()

	def hasChanged(self): return self.origFile != self.file

	def hasExternalChanged(self): return os.path.getmtime(self.path) != self.whenSaved