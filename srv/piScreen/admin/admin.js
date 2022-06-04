//necessary html elements
idleBadge = document.getElementById("idle");
//status
active = document.getElementById("active");
displayState = document.getElementById("displayState");
uptime = document.getElementById("uptime");
cpuLoad = document.getElementById("cpuLoad");
cpuTemp = document.getElementById("cpuTemp");
ramUsed = document.getElementById("ramUsed");
ramTotal = document.getElementById("ramTotal");
ramUsage = document.getElementById("ramUsage");
//control
displayOnBtn = document.getElementById("displayOnBtn");
displayStandbyBtn = document.getElementById("displayStandbyBtn");
spinnerDisplayOn = document.getElementById("spinnerDisplayOn");
spinnerDisplayStandby = document.getElementById("spinnerDisplayStandby");
//info
screenshot = document.getElementById("screenshot");
screenshotTime = document.getElementById("screenshotTime");
versionInfoBtn = document.getElementById("versionInfoBtn");
//schedule
schedule = document.getElementById("schedule");
newScheduleLine = document.getElementById("newScheduleLine");
saveSchedule = document.getElementById("saveSchedule");
//modal
modal = new bootstrap.Modal(document.getElementById("modal"));
modalCloseBtn = modal._element.getElementsByClassName('btn-close')[0]
modalTitle = modal._element.getElementsByClassName('modal-title')[0]
modalBody = modal._element.getElementsByClassName('modal-body')[0]
modalCancelBtn = document.getElementById("modal-cancelBtn");
modalActionBtn = document.getElementById("modal-actionBtn");

//general functions
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
function generateScheduleLine() {
	newLine = document.createElement("div");
	newLine.className = "scheduleLine my-2";
	newLine.style = "display:flex;flex-flow:row wrap;align-items:center;";
	newLine.innerHTML = `
	<div class='form-check form-switch mx-1'>
		<input class='form-check-input' type='checkbox' checked></input>
	</div>
	<select class='form-select mx-1' style='width:auto'>
		<option selected value=0 label='Mo'>Montag</option>
		<option value=1 label='Di'>Dienstag</option>
		<option value=2 label='Mi'>Mittwoch</option>
		<option value=3 label='Do'>Donnerstag</option>
		<option value=4 label='Fr'>Freitag</option>
		<option value=5 label='Sa'>Samstag</option>
		<option value=6 label='So'>Sonntag</option>
	</select>
	<input class='form-control mx-1' style='width:auto' type='time'></input>
	<select class='form-select mx-1' style='width:auto'>
		<option selected value=0>Bildschirm ausschalten</option>
		<option value=1>Bildschirm einschalten</option>
		<option value=2>Browser neustarten</option>
		<option value=3>Gerät neustarten</option>
		<option value=4>Gerät ausschalten</option>
	</select>
	<button class='btn btn-danger mx-1' onclick="this.parentElement.remove();">
		<i class='bi bi-trash'></i>
	</button>
	`;
	return newLine;
}
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
function showModal(title="Titel",body="---",showClose=true,showCancel=true,cancelText="Abbruch",actionType=0,actionText="OK",actionFunction=function(){alert("Kein Befehl gesetzt")}) {
	modalTitle.innerText = title;
	modalBody.innerHTML = body;
	modalCloseBtn.hidden = !showClose;
	modalCancelBtn.hidden = !showCancel;
	modalCancelBtn.innerText = cancelText;
	if (actionType!=0) {
		modalActionBtn.innerText = actionText;
		modalActionBtn.hidden = false;
		switch (actionType) {
			case 1:
				modalActionBtn.className = "btn btn-primary";
				break;
			case 2:
				modalActionBtn.className = "btn btn-secondary";
				break;
			case 3:
				modalActionBtn.className = "btn btn-success";
				break;
			case 4:
				modalActionBtn.className = "btn btn-danger";
				break;
			case 5:
				modalActionBtn.className = "btn btn-warning";
				break;
			case 6:
				modalActionBtn.className = "btn btn-info";
				break;
			case 7:
				modalActionBtn.className = "btn btn-light";
				break;
			case 8:
				modalActionBtn.className = "btn btn-dark";
				break;
		}
		modalActionBtn.onclick = actionFunction;
	}
	else {
		modalActionBtn.hidden = true;
	}
	modal.show();
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

//click events
document.getElementById("reloadBtn").onclick = function() {
	var xmlhttp = new XMLHttpRequest();
	xmlhttp.open('GET', 'cmd.php?id=1', true);
	xmlhttp.send();
}
document.getElementById("restartBtn").onclick = function() {
	showModal("Achtung","Gerät wirklich neustarten?",undefined,undefined,undefined,4,"Neustart",actionFunction=function(){
		var xmlhttp = new XMLHttpRequest();
		xmlhttp.open('GET', 'cmd.php?id=2', true);
		xmlhttp.send();
		modal.hide();
	});
}
document.getElementById("shutdownBtn").onclick = function() {
	showModal("Achtung","Gerät wirklich herunterfahren?<br>Das Gerät ist danach nicht mehr erreichbar und muss vom Strom getrennt werden, um wieder starten zu können!",undefined,undefined,undefined,4,"Herunterfahren",actionFunction=function(){
		var xmlhttp = new XMLHttpRequest();
		xmlhttp.open('GET', 'cmd.php?id=3', true);
		xmlhttp.send();
		modal.hide();
	});
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
versionInfoBtn.onclick = function() {
	let xmlhttp = new XMLHttpRequest();
	xmlhttp.onload = function() {
		let jsonData = JSON.parse(xmlhttp.responseText);
		showModal("piScreen Info",`
		<h4>
			<i class='bi bi-file-earmark-code'></i> piScreen Versionsinfo
		</h4>
		piScreen befindet sich auf Version ${jsonData.version.major}.${jsonData.version.minor}.${jsonData.version.patch}<br><br>
		piScreen ist ein kleines Bastelprojekt von zwei befreundeten Hobbyentwicklern und ist <a href='https://github.com/Jet0JLH/piScreen' target='popup'>hier</a> zu finden.
		`,false,true,"Danke für die Info 😊");
	}
	xmlhttp.open('GET', 'cmd.php?id=11', true);
	xmlhttp.send();
}
newScheduleLine.onclick = function() {
	schedule.appendChild(generateScheduleLine());
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
			showModal("Fehler","<b>Wurde nicht gespeichert!</b><br>Bei mindestens einem Eintrag fehlt die Uhrzeit!",false,true,"OK");
			return 1;
		}
	}
	let xmlhttp = new XMLHttpRequest();
	xmlhttp.onload = function() {
		if (xmlhttp.responseText=="true") {
			showModal("Gespeichert","Einstellungen gespeichert",false,true,"OK");
			loadSchedule();
		}
		else {
			showModal("Fehler","<b>Fehler beim Speichern</b>",false,true,"OK");
		}
	}
	xmlhttp.open('POST', 'cmd.php?id=9', true);
	xmlhttp.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
	xmlhttp.send(JSON.stringify(scheduleJSON));
}


//main
window.onload = function(){
	var xmlhttp = new XMLHttpRequest();
	xmlhttp.timeout = 1000;
	xmlhttp.open('GET', 'cmd.php?id=5', true);
	//load periodical the current infos about the system
	xmlhttp.onload = function() {
		idleBadge.id = "notIdle";
		setTimeout(function(){idleBadge.id = "idle"},100);
		jsonData = JSON.parse(xmlhttp.responseText);
		active.classList = "badge rounded-pill bg-success";
		active.innerHTML = "Online";
		switch (jsonData.displayState) {
			case "on":
				displayState.classList = "badge rounded-pill bg-success";
				displayState.innerHTML = "An";
				displayOnBtn.parentElement.hidden = true;
				displayStandbyBtn.parentElement.hidden = false; 
				break;
			case "off":
				displayState.classList = "badge rounded-pill bg-danger";
				displayState.innerHTML = "Aus";
				displayOnBtn.parentElement.hidden = false;
				displayStandbyBtn.parentElement.hidden = true; 
				break;
			case "standby":
				displayState.classList = "badge rounded-pill bg-danger";
				displayState.innerHTML = "Standby";
				displayOnBtn.parentElement.hidden = false;
				displayStandbyBtn.parentElement.hidden = true; 
				break;
			default:
				displayState.classList = "badge rounded-pill bg-secondary";
				displayState.innerHTML = "Unbekannt";
				displayOnBtn.parentElement.hidden = false;
				displayStandbyBtn.parentElement.hidden = false; 
				break;
		}
		uptime.innerHTML = jsonData.uptime.days + " Tage, " + jsonData.uptime.hours + " Stunden, " + jsonData.uptime.mins + " Minuten";
		cpuLoad.innerHTML = jsonData.cpuLoad;
		cpuTemp.innerHTML = Math.round(jsonData.cpuTemp / 1000) + " °C";
		ramUsed.innerHTML = Number(jsonData.ramUsed / 1000 / 1000).toFixed(2) + " GiB";
		ramTotal.innerHTML = Number(jsonData.ramTotal / 1000 / 1000).toFixed(2) + " GiB";
		ramUsage.innerHTML = Number(jsonData.ramUsed/jsonData.ramTotal*100).toFixed(2);
		spinnerDisplayOn.hidden = !jsonData.display.onSet;
		spinnerDisplayStandby.hidden = !jsonData.display.standbySet;
		screenshot.src = "piScreenScreenshot.png?t=" + new Date().getTime();
		st = new Date(jsonData.screenshotTime*1000);
		screenshotTime.innerHTML = `${addLeadingZero(st.getDate())}.${addLeadingZero(st.getMonth()+1)}.${1900+st.getYear()} - ${addLeadingZero(st.getHours())}:${addLeadingZero(st.getMinutes())}:${addLeadingZero(st.getSeconds())}`;

		new Masonry(document.getElementById("masonry"))
	}
	xmlhttp.onerror = function() {
		setToUnknownValues();
	}
	xmlhttp.ontimeout = function() {
		setToUnknownValues();
	}
	xmlhttp.send();

	//reload infos every 5 seconds
	setInterval(function() {
		xmlhttp.open('GET', 'cmd.php?id=5', true);
		xmlhttp.send();
	},5000);

	loadSchedule();
}