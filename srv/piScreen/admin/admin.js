uptime = document.getElementById("uptime");
active = document.getElementById("active");
displayState = document.getElementById("displayState");
cpuTemp = document.getElementById("cpuTemp");
modal = new bootstrap.Modal(document.getElementById("modal"));
modalTitle = document.getElementById("modal-title");
modalBody = document.getElementById("modal-body");
modalCancelBtn = document.getElementById("modal-cancelBtn");
modalAcceptBtn = document.getElementById("modal-acceptBtn");
rebootTimes = [];
rebootTimes[0] = document.getElementById("reboot-0-time");
rebootTimes[1] = document.getElementById("reboot-1-time");
rebootTimes[2] = document.getElementById("reboot-2-time");
rebootTimes[3] = document.getElementById("reboot-3-time");
rebootTimes[4] = document.getElementById("reboot-4-time");
rebootTimes[5] = document.getElementById("reboot-5-time");
rebootTimes[6] = document.getElementById("reboot-6-time");

displayOnBtn = document.getElementById("displayOnBtn");
displayStandbyBtn = document.getElementById("displayStandbyBtn");
spinnerDisplayOn = document.getElementById("spinnerDisplayOn");
spinnerDisplayStandby = document.getElementById("spinnerDisplayStandby");

idleBadge = document.getElementById("idle");

cpuLoad = document.getElementById("cpuLoad");
ramUsed = document.getElementById("ramUsed");
ramTotal = document.getElementById("ramTotal");
ramUsage = document.getElementById("ramUsage");

newScheduleLine = document.getElementById("newScheduleLine");
schedule = document.getElementById("schedule");
saveSchedule = document.getElementById("saveSchedule");
scheduleExclusionActiv = document.getElementById("scheduleExclusionActiv");
scheduleExclusionFrom = document.getElementById("scheduleExclusionFrom");
scheduleExclusionTo = document.getElementById("scheduleExclusionTo");

versionInfoBtn = document.getElementById("versionInfoBtn");

screenshot = document.getElementById("screenshot");
screenshotTime = document.getElementById("screenshotTime");

modal._element.addEventListener('hidden.bs.modal', function (event) {
    modalAcceptBtn.hidden = false;
	modalCancelBtn.hidden = false;
});

function generateScheduleLine() {
	newLine = document.createElement("div");
	newLine.className = "scheduleLine my-1";
	newLine.style = "display:flex;flex-flow:row wrap;align-items:center;";

	scheduleActiv = document.createElement("div");
	scheduleActiv.className = "form-check form-switch mx-1";
	scheduleActiv.innerHTML = "<input class='form-check-input' type='checkbox' checked></input>";
		
	scheduleDay = document.createElement("select");
	scheduleDay.className = "form-select mx-1";
	scheduleDay.innerHTML = "<option selected value=0 label='Mo'>Montag</option><option value=1 label='Di'>Dienstag</option><option value=2 label='Mi'>Mittwoch</option><option value=3 label='Do'>Donnerstag</option><option value=4 label='Fr'>Freitag</option><option value=5 label='Sa'>Samstag</option><option value=6 label='So'>Sonntag</option>";
	scheduleDay.style = "width:auto";

	scheduleTime = document.createElement("input");
	scheduleTime.className = "form-control mx-1";
	scheduleTime.setAttribute("type","time");
	scheduleTime.style = "width:auto";

	scheduleAction = document.createElement("select");
	scheduleAction.className = "form-select mx-1";
	scheduleAction.innerHTML = "<option selected value=0>Bildschirm ausschalten</option><option value=1>Bildschirm einschalten</option><option value=2>Browser neustarten</option><option value=3>Gerät neustarten</option><option value=4>Gerät ausschalten</option>";
	scheduleAction.style = "width:auto";

	scheduleDelete = document.createElement("button");
	scheduleDelete.className = "btn btn-danger mx-1";
	scheduleDelete.innerHTML = "<i class='bi bi-trash'></i>";
	scheduleDelete.onclick = function() {
		this.parentElement.remove();
	}

	newLine.appendChild(scheduleActiv);
	newLine.appendChild(scheduleDay);
	newLine.appendChild(scheduleTime);
	newLine.appendChild(scheduleAction);
	newLine.appendChild(scheduleDelete);

	return newLine;
}

function addLeadingZero (input) {
	intInput = parseInt(input);
	if (intInput < 10) {
		return "0"+intInput;
	}
	else {
		return input;
	}
}

function setToUnknownValues() {
	active.classList = "badge rounded-pill bg-danger";
	active.innerHTML = "Offline";

	displayState.classList = "badge rounded-pill bg-secondary";
	displayState.innerHTML = "Unbekannt";
	displayOnBtn.hidden = false;
	displayStandbyBtn.hidden = false;
	spinnerDisplayOn.hidden = true;
	spinnerDisplayStandby.hidden = true;

	uptime.innerHTML = "???";

	cpuTemp.innerHTML = "???";
	cpuLoad.innerHTML = "???";
	ramUsed.innerHTML = "???";
	ramTotal.innerHTML = "???";
	ramUsage.innerHTML = "???";
}

document.getElementById("reloadBtn").onclick = function() {
	var xmlhttp = new XMLHttpRequest();
	xmlhttp.open('GET', 'cmd.php?id=1', true);
	xmlhttp.send();
}
document.getElementById("restartBtn").onclick = function() {
	modalTitle.innerHTML = "Achtung";
	modalBody.innerHTML = "Gerät wirklich neustarten?";
	modalAcceptBtn.innerHTML = "Neustart";
	modalAcceptBtn.onclick = function() {
		var xmlhttp = new XMLHttpRequest();
		xmlhttp.open('GET', 'cmd.php?id=2', true);
		xmlhttp.send();
		modal.hide(1);
	}
	modal.toggle(1);
}
document.getElementById("shutdownBtn").onclick = function() {

	modalTitle.innerHTML = "Achtung";
	modalBody.innerHTML = "Gerät wirklich herunterfahren?<br>Das Gerät ist danach nicht mehr erreichbar und muss vom Strom getrennt werden, um wieder starten zu können!";
	modalAcceptBtn.innerHTML = "Herunterfahren";
	modalAcceptBtn.onclick = function() {
		var xmlhttp = new XMLHttpRequest();
		xmlhttp.open('GET', 'cmd.php?id=3', true);
		xmlhttp.send();
		modal.hide(1);
	}
	modal.toggle(1);
}
displayOnBtn.onclick = function() {
	spinnerDisplayOn.hidden = false;
	var xmlhttp = new XMLHttpRequest();
	xmlhttp.open('GET', 'cmd.php?id=8&cmd=1', true);
	xmlhttp.send();
}
displayStandbyBtn.onclick = function() {
	spinnerDisplayStandby.hidden = false;
	var xmlhttp = new XMLHttpRequest();
	xmlhttp.open('GET', 'cmd.php?id=8&cmd=0', true);
	xmlhttp.send();
}
newScheduleLine.onclick = function() {
	schedule.appendChild(generateScheduleLine());
}

versionInfoBtn.onclick = function() {
	modalAcceptBtn.hidden = true;
	modalCancelBtn.hidden = true;
	let xmlhttp = new XMLHttpRequest();
	xmlhttp.onload = function() {
		let jsonData = JSON.parse(xmlhttp.responseText);
		modalTitle.innerHTML = "piScreen Info";
		modalBody.innerHTML = `<h4><i class='bi bi-file-earmark-code'></i> piScreen Versionsinfo</h4>piScreen befindet sich auf Version ${jsonData.version.major}.${jsonData.version.minor}.${jsonData.version.patch}<br><br>piScreen ist ein kleines Bastelprojekt von zwei befreundeten Hobbyentwicklern und ist <a href='https://github.com/Jet0JLH/piScreen' target='popup'>hier</a> zu finden.`;
		modalAcceptBtn.innerHTML = "X";
		modalAcceptBtn.onclick = function() {
			modal.toggle(1);
		}
		modal.toggle(1);
	}
	xmlhttp.open('GET', 'cmd.php?id=11', true);
	xmlhttp.send();
}

function updateAvaiable() {
	let xmlhttp = new XMLHttpRequest();
	xmlhttp.onload = function() {
		modalAcceptBtn.hidden = true;
		modalCancelBtn.hidden = true;
		let jsonData = JSON.parse(xmlhttp.responseText);
		modalTitle.innerHTML = "Update verfügbar";
		modalBody.innerHTML = `Aktuelle Version: ${jsonData.version.major}.${jsonData.version.minor}.${jsonData.version.patch}<br>Verfügbare Version: ${updateAvaiableBtn.innerText}<br><br><code>sudo /home/pi/piScreen/piScreenCmd.py --do-upgrade -v</code>`;
		modalAcceptBtn.innerHTML = "OK";
		modalAcceptBtn.onclick = function() {
			window.location.href = "update.php";
		}
		modal.toggle(1);
	}
	xmlhttp.open('GET', 'cmd.php?id=11', true);
	xmlhttp.send();
}

function createScheduleEntryJSON(htmlElement) {
	if (htmlElement.children[2].value == "") {
		return null;
	}
	return {
		"enabled":htmlElement.children[0].children[0].checked,
		"day":parseInt(htmlElement.children[1].value),
		"hour":parseInt(htmlElement.children[2].value.split(":")[0]),
		"minute":parseInt(htmlElement.children[2].value.split(":")[1]),
		"mode":parseInt(htmlElement.children[3].value)
	}
}

saveSchedule.onclick = function() {
	let scheduleJSON = {
		"scheduleExclude":{
			"enabled":scheduleExclusionActiv.checked,
			"from":{
				"year":0,
				"month":0,
				"day":0,
				"hour":0,
				"minute":0
			},
			"to":{
				"year":0,
				"month":0,
				"day":0,
				"hour":0,
				"minute":0
			}
		},
		"schedule": []
	}
	if (scheduleExclusionFrom.value != "" && scheduleExclusionTo.value != "") {
		if (new Date(scheduleExclusionFrom.value) > new Date(scheduleExclusionTo.value)) {
			let tempDate = scheduleExclusionFrom.value;
			scheduleExclusionFrom.value = scheduleExclusionTo.value;
			scheduleExclusionTo.value = tempDate;
		}
		let scheduleExclusionSplit = scheduleExclusionFrom.value.split("-");
		scheduleJSON.scheduleExclude.from.year = parseInt(scheduleExclusionSplit[0]);
		scheduleJSON.scheduleExclude.from.month = parseInt(scheduleExclusionSplit[1]);
		scheduleJSON.scheduleExclude.from.day = parseInt(scheduleExclusionSplit[2]);
		scheduleExclusionSplit = scheduleExclusionTo.value.split("-");
		scheduleJSON.scheduleExclude.to.year = parseInt(scheduleExclusionSplit[0]);
		scheduleJSON.scheduleExclude.to.month = parseInt(scheduleExclusionSplit[1]);
		scheduleJSON.scheduleExclude.to.day = parseInt(scheduleExclusionSplit[2]);
	}
	for (let i=0;i < schedule.childElementCount;i++) {
		let jsonEntry = createScheduleEntryJSON(schedule.children[i]);
		if (jsonEntry != null) {
			scheduleJSON.schedule.push(jsonEntry);
		}
		else {
			alert("Wurde nicht gespeichert!\nBei mindestens einem Eintrag fehlt die Uhrzeit!");
			return 1;
		}
	}
	let xmlhttp = new XMLHttpRequest();
	xmlhttp.onload = function() {
		if (xmlhttp.responseText=="true") {
			alert("Einstellungen gespeichert");
			loadSchedule();
		}
		else {
			alert("Fehler beim Speichern");
		}
	}
	xmlhttp.open('POST', 'cmd.php?id=9', true);
	xmlhttp.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
	xmlhttp.send(JSON.stringify(scheduleJSON));
}

window.onload = function(){
	var xmlhttp = new XMLHttpRequest();
	xmlhttp.timeout = 1000;
	xmlhttp.onload = function() {
		idleBadge.id = "notIdle";
		setTimeout(function(){idleBadge.id = "idle"},100);
		jsonData = JSON.parse(xmlhttp.responseText);
		uptime.innerHTML = jsonData.uptime.days + " Tage, " + jsonData.uptime.hours + " Stunden, " + jsonData.uptime.mins + " Minuten";
		cpuTemp.innerHTML = Math.round(jsonData.cpuTemp / 1000) + " °C";
		active.classList = "badge rounded-pill bg-success";
		active.innerHTML = "Online";
		switch (jsonData.displayState) {
			case "on":
				displayState.classList = "badge rounded-pill bg-success";
				displayState.innerHTML = "An";
				displayOnBtn.hidden = true;
				displayStandbyBtn.hidden = false; 
				break;
			case "off":
				displayState.classList = "badge rounded-pill bg-danger";
				displayState.innerHTML = "Aus";
				displayOnBtn.hidden = false;
				displayStandbyBtn.hidden = true; 
				break;
			case "standby":
				displayState.classList = "badge rounded-pill bg-danger";
				displayState.innerHTML = "Standby";
				displayOnBtn.hidden = false;
				displayStandbyBtn.hidden = true; 
				break;
			default:
				displayState.classList = "badge rounded-pill bg-secondary";
				displayState.innerHTML = "Unbekannt";
				displayOnBtn.hidden = false;
				displayStandbyBtn.hidden = false; 
				break;
		}
		spinnerDisplayOn.hidden = !jsonData.display.onSet;
		spinnerDisplayStandby.hidden = !jsonData.display.standbySet;
		cpuLoad.innerHTML = jsonData.cpuLoad;
		ramUsed.innerHTML = Number(jsonData.ramUsed / 1000 / 1000).toFixed(2) + " GiB";
		ramTotal.innerHTML = Number(jsonData.ramTotal / 1000 / 1000).toFixed(2) + " GiB";
		ramUsage.innerHTML = Number(jsonData.ramUsed/jsonData.ramTotal*100).toFixed(2);
		screenshot.src = "piScreenScreenshot.png?t=" + new Date().getTime();
		st = new Date(jsonData.screenshotTime*1000);
		screenshotTime.innerHTML = `${addLeadingZero(st.getDate())}.${addLeadingZero(st.getMonth()+1)}.${1900+st.getYear()} - ${addLeadingZero(st.getHours())}:${addLeadingZero(st.getMinutes())}:${addLeadingZero(st.getSeconds())}`;
	}
	xmlhttp.onerror = function() {
		setToUnknownValues();
	}
	xmlhttp.ontimeout = function() {
		setToUnknownValues();
	}
	xmlhttp.open('GET', 'cmd.php?id=5', true);
	xmlhttp.send();
	 setInterval(function() {
		xmlhttp.open('GET', 'cmd.php?id=5', true);
		xmlhttp.send();
	},5000);

	loadSchedule();
};

function loadSchedule() {
	let xmlhttp1 = new XMLHttpRequest();
	xmlhttp1.onload = function() {
		for (let i=schedule.childElementCount;i>0;i--) {
			schedule.children[i-1].remove();
		}
		let jsonScheduleData = JSON.parse(xmlhttp1.responseText);
		scheduleExclusionActiv.checked = jsonScheduleData.scheduleExclude.enabled;
		scheduleExclusionFrom.value = addLeadingZero(jsonScheduleData.scheduleExclude.from.year) + "-" + addLeadingZero(jsonScheduleData.scheduleExclude.from.month) + "-" + addLeadingZero(jsonScheduleData.scheduleExclude.from.day);
		scheduleExclusionTo.value = addLeadingZero(jsonScheduleData.scheduleExclude.to.year) + "-" + addLeadingZero(jsonScheduleData.scheduleExclude.to.month) + "-" + addLeadingZero(jsonScheduleData.scheduleExclude.to.day);

		for (let i=0;i<jsonScheduleData.schedule.length;i++) {
			let scheduleEntry = generateScheduleLine();
			scheduleEntry.children[0].children[0].checked = jsonScheduleData.schedule[i].enabled;
			scheduleEntry.children[1].selectedIndex = jsonScheduleData.schedule[i].day;
			scheduleEntry.children[2].value = addLeadingZero(jsonScheduleData.schedule[i].hour) + ":" + addLeadingZero(jsonScheduleData.schedule[i].minute);
			scheduleEntry.children[3].selectedIndex = jsonScheduleData.schedule[i].mode;
			schedule.appendChild(scheduleEntry);
		}
		sortSchedule();
	}
	xmlhttp1.open('GET', 'cmd.php?id=10', true);
	xmlhttp1.send();
}

function sortSchedule() {
	let found = true;
	while (found) {
		found = false;
		for (let i=1;i < schedule.childElementCount;i++) {
			if (schedule.children[i-1].children[1].selectedIndex > schedule.children[i].children[1].selectedIndex || (schedule.children[i-1].children[1].selectedIndex == schedule.children[i].children[1].selectedIndex && parseInt(schedule.children[i-1].children[2].value.replace(":","")) > parseInt(schedule.children[i].children[2].value.replace(":","")))) {
				schedule.insertBefore(schedule.children[i], schedule.children[i-1]);
				found = true;
			}
		}
	}
}