//necessary html elements
darkmodeBtn = document.getElementById("darkmodeBtn");
theme = document.getElementById("theme");
languageSelect = document.getElementById("languageSelect");
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
//language stuff
var currentLanguage = null;
var availableLanguages = [];
var languageStrings = "";

//general functions
function addLeadingZero (input) {
	intInput = parseInt(input);
	if (intInput < 10) {
		return "0" + intInput;
	} else {
		return input;
	}
}
function setToUnknownValues() {
	active.classList = "badge rounded-pill bg-danger";
	active.innerHTML = getLanguageAsText('offline');

	displayState.classList = "badge rounded-pill bg-secondary";
	displayState.innerHTML = getLanguageAsText('unknown');
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
		<option selected value=0 lang-data='day0-short'>${getLanguageAsText('day0-short')}</option>
		<option value=1 lang-data='day1-short'>${getLanguageAsText('day1-short')}</option>
		<option value=2 lang-data='day2-short'>${getLanguageAsText('day2-short')}</option>
		<option value=3 lang-data='day3-short'>${getLanguageAsText('day3-short')}</option>
		<option value=4 lang-data='day4-short'>${getLanguageAsText('day4-short')}</option>
		<option value=5 lang-data='day5-short'>${getLanguageAsText('day5-short')}</option>
		<option value=6 lang-data='day6-short'>${getLanguageAsText('day6-short')}</option>
	</select>
	<input class='form-control mx-1' style='width:auto' type='time'></input>
	<select class='form-select mx-1' style='width:auto'>
		<option selected value=0 lang-data='display-off'>${getLanguageAsText('display-off')}</option>
		<option value=1 lang-data='display-on'>${getLanguageAsText('display-on')}</option>
		<option value=2 lang-data='restart-browser'>${getLanguageAsText('restart-browser')}</option>
		<option value=3 lang-data='restart-device'>${getLanguageAsText('restart-device')}</option>
		<option value=4 lang-data='shutdown-device'>${getLanguageAsText('shutdown-device')}</option>
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

		for (let i = 0; i < jsonScheduleData.schedule.length; i++) {
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
		for (let i = 1; i < schedule.childElementCount; i++) {
			if (schedule.children[i-1].children[1].selectedIndex > schedule.children[i].children[1].selectedIndex || (schedule.children[i-1].children[1].selectedIndex == schedule.children[i].children[1].selectedIndex && parseInt(schedule.children[i-1].children[2].value.replace(":","")) > parseInt(schedule.children[i].children[2].value.replace(":","")))) {
				schedule.insertBefore(schedule.children[i], schedule.children[i-1]);
				found = true;
			}
		}
	}
}
function showModal(title="Titel", body="---", showClose=true, showCancel=true, cancelText=getLanguageAsText('cancel'), actionType=0, actionText=getLanguageAsText('ok'), actionFunction=function(){alert("Kein Befehl gesetzt")}) {
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
	} else {
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
function isInDarkmode() {
	if (theme.href.includes("/bootstrap/css/bootstrap.min.css")) {
		return false;
	}
	else {
		return true;
	}
}
function toggleDarkmode() {
	setDarkMode(!isInDarkmode());
}
function setDarkMode(dark) {
	if (dark) {
		theme.href = "/bootstrap/darkpan-1.0.0/css/bootstrap.min.css";
		darkmodeBtn.classList.replace("btn-outline-secondary", "btn-outline-light");
		languageSelect.classList.replace("border-secondary", "border-light");
	}
	else {
		theme.href = "/bootstrap/css/bootstrap.min.css";
		darkmodeBtn.classList.replace("btn-outline-light", "btn-outline-secondary");
		languageSelect.classList.replace("border-light", "border-secondary");
	}
}

function checkForUpdate() {
	var xmlhttp = new XMLHttpRequest();
	xmlhttp.onload = function() {
		if (xmlhttp.responseText != 'no-update') {
			let nextVersion = xmlhttp.responseText;
			let updateButton = document.createElement('button');
			updateButton.id = 'updateAvaiableBtn';
			updateButton.href = '#';
			updateButton.className = 'btn btn-danger blink';
			updateButton.style = 'float:right;';

			let textSpan = document.createElement('span');
			textSpan.setAttribute('lang-data', 'update-button');
			textSpan.innerText = getLanguageAsText('update-button');
			let versionSpan = document.createElement('span');
			versionSpan.innerText = nextVersion;

			updateButton.appendChild(textSpan);
			updateButton.appendChild(versionSpan);
			updateButton.onclick = function() {
				showModal(getLanguageAsText('update-info-header'), getLanguageAsText('update-info-text'), false, true, getLanguageAsText('ok'));
			}
			document.getElementById('info-footer').appendChild(updateButton);
		}
	}
	xmlhttp.open('GET', 'cmd.php?id=6', true);
    xmlhttp.send();
}

//click events
document.getElementById("reloadBtn").onclick = function() {
	var xmlhttp = new XMLHttpRequest();
	xmlhttp.open('GET', 'cmd.php?id=1', true);
	xmlhttp.send();
}
document.getElementById("restartBtn").onclick = function() {
	showModal(getLanguageAsText('attention'), getLanguageAsText('reboot-really'), undefined, undefined, undefined, 4, getLanguageAsText('reboot-device'), actionFunction=function(){
		var xmlhttp = new XMLHttpRequest();
		xmlhttp.open('GET', 'cmd.php?id=2', true);
		xmlhttp.send();
		modal.hide();
	});
}
document.getElementById("shutdownBtn").onclick = function() {
	showModal(getLanguageAsText('attention'), getLanguageAsText('shutdown-really'), undefined, undefined, undefined, 4, getLanguageAsText('shutdown-device'), actionFunction=function(){
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
		showModal(getLanguageAsText('about-info'), getLanguageAsText('info-text') + ' ' + jsonData.version.major + '.' + jsonData.version.minor + '.' + jsonData.version.patch, false, true, getLanguageAsText('alright'));
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
		} else {
			showModal(getLanguageAsText('error'),`<b>${getLanguageAsText('time-schedule-not-saved')}</b><br>${getLanguageAsText('err-time-missing')}`,false,true,getLanguageAsText('ok'));
			return 1;
		}
	}
	let xmlhttp = new XMLHttpRequest();
	xmlhttp.onload = function() {
		if (xmlhttp.responseText=="true") {
			showModal(getLanguageAsText('saved'),getLanguageAsText('saved-settings'),false,true,getLanguageAsText('ok'));
			loadSchedule();
		}
		else {
			showModal(getLanguageAsText('error'),getLanguageAsText('err-while-saving'),false,true,getLanguageAsText('ok'));
		}
	}
	xmlhttp.open('POST', 'cmd.php?id=9', true);
	xmlhttp.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
	xmlhttp.send(JSON.stringify(scheduleJSON));
}
darkmodeBtn.onclick = function() {
	toggleDarkmode();
}


//main
window.onload = function(){
	if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
		setDarkMode(true);
	}
	else {
		setDarkMode(false);
	}
	getDefaultLanguage();
	var xmlhttp = new XMLHttpRequest();
	xmlhttp.timeout = 1000;
	xmlhttp.open('GET', 'cmd.php?id=5', true);
	//load periodical the current infos about the system
	xmlhttp.onload = function() {
		idleBadge.id = "notIdle";
		setTimeout(function(){idleBadge.id = "idle"},100);
		jsonData = JSON.parse(xmlhttp.responseText);
		active.classList = "badge rounded-pill bg-success";
		active.innerHTML = getLanguageAsText('online');
		switch (jsonData.displayState) {
			case "on":
				displayState.classList = "badge rounded-pill bg-success";
				displayState.innerHTML = getLanguageAsText('on');
				displayOnBtn.parentElement.hidden = true;
				displayStandbyBtn.parentElement.hidden = false; 
				break;
			case "off":
				displayState.classList = "badge rounded-pill bg-danger";
				displayState.innerHTML = getLanguageAsText('off');
				displayOnBtn.parentElement.hidden = false;
				displayStandbyBtn.parentElement.hidden = true; 
				break;
			case "standby":
				displayState.classList = "badge rounded-pill bg-danger";
				displayState.innerHTML = getLanguageAsText('standby');
				displayOnBtn.parentElement.hidden = false;
				displayStandbyBtn.parentElement.hidden = true; 
				break;
			default:
				displayState.classList = "badge rounded-pill bg-secondary";
				displayState.innerHTML = getLanguageAsText('unknown');
				displayOnBtn.parentElement.hidden = false;
				displayStandbyBtn.parentElement.hidden = false; 
				break;
		}
		uptime.innerHTML = jsonData.uptime.days + " " + getLanguageAsText('days') + ", " + jsonData.uptime.hours + " " + getLanguageAsText('hours') + ", " + jsonData.uptime.mins + " " + getLanguageAsText('minutes');
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
	checkForUpdate();
}

// language functions
function fetchLanguage(lang) {
	currentLanguage = lang;
	sendHTTPRequest('GET', 'cmd.php?id=13&lang=' + lang, true);
	document.getElementById(lang).selected = true;
    var xmlhttp = new XMLHttpRequest();
	xmlhttp.onload = function() {
		languageStrings = JSON.parse(xmlhttp.responseText);
		setLanguageOnSite();
	}
    xmlhttp.open('GET', '../languages/' + currentLanguage + '.json', true);
    xmlhttp.send();
}

function setLanguageOnSite() {
	var tags = document.querySelectorAll("[lang-data]"); //Replaces with strings in the right language
	tags.forEach(element => {
		let key = element.getAttribute('lang-data');
		if (key) {
			element.textContent = languageStrings[currentLanguage][key];
		}
	});
}

function getDefaultLanguage() { //gets language from server settings.json
	var xmlhttp = new XMLHttpRequest();
	xmlhttp.onload = function() {
		let settingsJSON = JSON.parse(xmlhttp.responseText);
		currentLanguage = settingsJSON.settings.language;
	}
	xmlhttp.onloadend = function () {
		fetchLanguage(currentLanguage);
		loadSchedule();
	}
    xmlhttp.open('GET', 'cmd.php?id=12', true);
    xmlhttp.send();
}

function sendHTTPRequest(method, url, async) {
	var xmlhttp = new XMLHttpRequest();
	xmlhttp.onload = function() {
		return xmlhttp.responseText;
	}
    xmlhttp.open(method, url, async);
    xmlhttp.send();
}

function getLanguageAsText(langdata) { //Replaces strings in dynamic sections
	try {
		return languageStrings[currentLanguage][langdata];	
	} catch (error) {
		console.log(error);
	}
}

window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', event => {
if (event.matches) {
	setDarkMode(true);
} else {
	setDarkMode(false);
}
});