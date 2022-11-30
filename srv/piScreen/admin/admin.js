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
var scheduleEntryCount = 0;
const commandCollection = [//text, parameter
		["---", false], ["sleep", "text"], ["", false], ["", false], ["", false], ["", false], ["", false], ["", false], ["", false], ["", false],
		["universal", "text"], ["restart-device", false], ["shutdown-device", false], ["", false], ["", false], ["", false], ["", false], ["", false], ["", false], ["", false],
		["", false], ["", false], ["", false], ["", false], ["", false], ["", false], ["", false], ["", false], ["", false], ["", false],
		["display-state", [[0, "display-off"], [1, "display-on"]]], ["switch-display-input", false], ["change-display-protocol", [[0, "cec"], [1, "ddc"]]], ["", false], ["", false], ["", false], ["", false], ["", false], ["", false], ["", false],
		["start-browser", "text"], ["", false], ["", false], ["stop-browser", false], ["", false], ["", false], ["", false], ["", false], ["", false], ["", false],
		["", false], ["", false], ["", false], ["", false], ["", false], ["", false], ["", false], ["", false], ["", false], ["", false],
		["", false], ["", false], ["", false], ["", false], ["", false], ["", false], ["", false], ["", false], ["", false], ["", false],
		["", false], ["", false], ["", false], ["", false], ["", false], ["", false], ["", false], ["", false], ["", false], ["", false],
		["", false], ["", false], ["", false], ["", false], ["", false], ["", false], ["", false], ["", false], ["", false], ["", false],
		["", false], ["", false], ["", false], ["", false], ["", false], ["", false], ["", false], ["", false], ["", false], ["", false],
	];
var entryShown = false;

//trigger
var startupTriggerIndex = -1;
//modal
modal = new bootstrap.Modal(document.getElementById("modal"));
modalCloseBtn = modal._element.getElementsByClassName('btn-close')[0];
modalTitle = modal._element.getElementsByClassName('modal-title')[0];
modalBody = modal._element.getElementsByClassName('modal-body')[0];
modalCancelBtn = document.getElementById("modal-cancelBtn");
modalActionBtn = document.getElementById("modal-actionBtn");
//tooltip
var tooltipTriggerList;
var tooltipList;
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

function enableElements(enable) {
	let disable = !enable;
	let elementsToDisable = document.getElementsByClassName("disableOnDisconnect");

	for (let i = 0; i < elementsToDisable.length; i++) {
		elementsToDisable[i].disabled = disable;
	}
}

function getElement(id) {
	return document.getElementById(id);
}

function generateNewScheduleEntry(enabled=true, pattern="* * * * *", start="", end="", command=0, parameter="", saved=false, newEntry=true) {
	eId = scheduleEntryCount;
	if (commandCollection[command][0] == "") {
		console.error("Command " + command + " not found! CronID: " + eId);
		command = 0;
	}

	let startDate = start.split(" ")[0];
	let startTime = start.split(" ")[1];
	let endDate = end.split(" ")[0];
	let endTime = end.split(" ")[1];
	newEntryObj = document.createElement('div');
	newEntryObj.id = "entry" + eId;
	newEntryObj.className = "accordion-item border border-primary";
	newEntryObj.style.backgroundColor = "transparent";
	newEntryObj.innerHTML = `	<h2 class="accordion-header">
			<label class="accordion-button collapsed" data-bs-toggle="collapse" data-bs-target="#collapseEntry${eId}Collection" style='width: 100%; cursor: pointer;'>
				<span id='scheduleEntry${eId}HeaderEnabled' style='width: 10%;'>${enabled ? "<i class='bi bi-check-lg bigIcon pe-2' style='color: green;'></i>" : "<i class='bi bi-x-lg bigIcon pe-2' style='color: red;'></i>"}</span>
				<span id='scheduleEntry${eId}HeaderCommand' class='px-2' style='width: 30%;' lang-data='${commandCollection[command][0]}'>${commandCollection[command][0]}</span>
				<span id='scheduleEntry${eId}HeaderCron' class='px-2' style='width: 30%;'>${pattern}</span>
				<span id='scheduleEntry${eId}HeaderSaved' class='px-2 text-end' style='width: 30%;'></span>
			</label>
		</h2>
		<div id="collapseEntry${eId}Collection" class="accordion-collapse collapse" data-bs-parent="#entryCollectionAccordion">
			<div class="accordion-body">
				<table class="table-sm" style='width: 100%;'>
					<div id='scheduleEntry${eId}'>
						<tr>
							<td style='width: 50%;'>
								<div class="form-check form-switch">
									<input class="disableOnDisconnect form-check-input" type="checkbox" role="switch" id="entry${eId}EnabledSwitchCheck" onchange="enabledChanged(this, ${eId}); displayEntrySaved(false, ${eId});" ${enabled ? "checked" : ""}>
									<label class="form-check-label" for="entry${eId}EnabledSwitchCheck" lang-data="active">Aktiviert</label>
								</div>
							</td>
							<td style='width: 50%;'>
								<button id="entry${eId}ButtonDelete" type="button" class="disableOnDisconnect btn btn-danger" onclick='deleteEntry(${eId})' style='float: right;'><i class='bi bi-trash'></i></button>
							</td>
						</tr>
						<tr>
							<td>
								<div class='form-floating mb-3'>
									<input type='text' class='disableOnDisconnect form-control' name='cronentry' id='cronentry${eId}' value='${pattern}' onkeyup='showEntryHeader(${eId}); displayEntrySaved(false, ${eId});'>
									<label for='cronentry${eId}'lang-data="cron-entry">Croneintrag</label>
								</div>
							</td>
							<td>
								<i class='bi-question-octagon p-2' style='cursor: pointer;' id='cronEntry${eId}Help' data-bs-toggle="tooltip" data-bs-placement="top" data-bs-title="${getLanguageAsText('help')}" onclick='showModal(getLanguageAsText("help"), getLanguageAsText("cronHelpText"), false, true, getLanguageAsText("ok"));'></i>
							</td>
						</tr>
						<tr>
							<td>
								<div class='form-floating mb-3'>
									<select id='commandSelect${eId}' class='disableOnDisconnect form-select border-secondary' onchange='showEntryHeader(${eId}); displayEntrySaved(false, ${eId}); addParameter(${eId}, value);'>
									</select>
									<label for="commandSelect${eId}" lang-data="choose-command">Befehl auswählen</label>
								</div>
							</td>
							<td id="entry${eId}ParameterCell">
							</td>
						</tr>
						<tr>
							<td colspan='3' class=' border-top border-light p-0'>
								<table class='p-0' style="width: 100%;">
									<tr>
										<td colspan='2' class='p-2'>
											<div class="form-check form-switch">
												<input class="disableOnDisconnect form-check-input" type="checkbox" role="switch" id="entry${eId}ValiditySwitchCheckFrom" onchange='toggleValidityFrom(${eId}, checked); displayEntrySaved(false, ${eId});' ${start != "" ? "checked" : ""}>
												<label class="form-check-label" for="entry${eId}ValiditySwitchCheckFrom" lang-data="valid-from">Gültig von</label>
											</div>
										</td>
										<td colspan='2' class='p-2'>
											<div class="form-check form-switch">
												<input class="disableOnDisconnect form-check-input" type="checkbox" role="switch" id="entry${eId}ValiditySwitchCheckTo" onchange='toggleValidityTo(${eId}, checked); displayEntrySaved(false, ${eId});' ${end != "" ? "checked" : ""}>
												<label class="form-check-label" for="entry${eId}ValiditySwitchCheckTo" lang-data="valid-to">Gültig bis</label>
											</div>
										</td>
									</tr>
									<tr>
										<td id='entry${eId}ValidityTimeSpanFrom1' class='px-2' lang-data='from'>
											von
										</td>
										<td id='entry${eId}ValidityTimeSpanFrom2'>
											<div class='input-group'>
												<input id='scheduleEntry${eId}StartTime' name='scheduleEntry${eId}StartDateTime' type="time" class="disableOnDisconnect form-control p-1" onchange="displayEntrySaved(false, ${eId});" style="text-align: center; width: 40%;" value="${startTime}">
												<input id='scheduleEntry${eId}StartDate' type="date" class="disableOnDisconnect form-control p-1" style="text-align: center; width: 60%;" value="${startDate}">
											</div>
										</td>
										<td id='entry${eId}ValidityTimeSpanTo1' class='px-2' lang-data='to'>
											bis
										</td>
										<td id='entry${eId}ValidityTimeSpanTo2'>
											<div class='input-group'>
												<input id='scheduleEntry${eId}EndTime' name='scheduleEntry${eId}EndDateTime' type="time" class="disableOnDisconnect form-control p-1" onchange="displayEntrySaved(false, ${eId});" style="text-align: center; width: 40%;" value="${endTime}">
												<input id='scheduleEntry${eId}EndDate' type="date" class="disableOnDisconnect form-control p-1" style="text-align: center; width: 60%;" value="${endDate}">
											</div>
										</td>
									</tr>
								</table>
							</td>
						</tr>
					</div>
				</table>
				<button id="entry${eId}SaveButton" type="button" class="disableOnDisconnect btn btn-outline-success mt-2" onclick='saveEntry(${eId})' data-bs-toggle="collapse" data-bs-target="#collapseEntry${eId}Collection"><i class='bi bi-save pe-2'></i><span lang-data="save">Speichern</span></button>
				<i id='entryInfo${eId}' data='${newEntry}' class='bi bi-info-circle mt-3' style="float: right;" data-bs-toggle="tooltip" data-bs-placement="right" data-bs-title="CronID: ${eId}"></i>
			</div>
		</div>
	</div>`;

	//Adding element to document
	document.getElementById("entryCollectionAccordion").appendChild(newEntryObj);

	displayEntrySaved(saved, eId);

	toggleValidityFrom(eId, document.getElementById("entry" + eId + "ValiditySwitchCheckFrom").checked);
	toggleValidityTo(eId, document.getElementById("entry" + eId + "ValiditySwitchCheckTo").checked);

	addCommandsToDropdown("commandSelect" + eId);
	document.getElementById("commandSelect" + eId).value = command;
	addParameter(eId, command, parameter);

	showEntryHeader(eId);
	tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
	tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
	scheduleEntryCount += 1;
}

function addCommandsToDropdown(dropdownId) {
	//Add commands dropdown options
	for (let i = 0; i < commandCollection.length; i++) {
		if (commandCollection[i][0] != "") {
			let optionTag = document.createElement("option");
			optionTag.value = i;
			optionTag.setAttribute('lang-data', commandCollection[i][0]);
			optionTag.innerHTML = getLanguageAsText(commandCollection[i][0]);
			document.getElementById(dropdownId).appendChild(optionTag);
		}
	}
}

function addParameter(entryId, commandId, parameter) {
	let cell = getElement("entry" + entryId + "ParameterCell");
	cell.innerHTML = "";
	//add element
	let div = document.createElement("div");
	div.id = "scheduleEntry" + entryId + "ParameterInputDiv";
	div.className = "form-floating mb-3";

	if (commandCollection[commandId][1] == false) {
		return;
	} else if (commandCollection[commandId][1] == "text") {
		div.innerHTML = `<input id='scheduleEntry${entryId}ParameterInput' type='text' class='disableOnDisconnect form-control' onkeyup='displayEntrySaved(false, ${entryId});' maxlength='50' value='${parameter}' lang-data='parameter'>`;
		if (parameter == undefined) parameter = "";
	} else if (Array.isArray(commandCollection[commandId][1])) {
		let htmlSelect = `<select id='scheduleEntry${entryId}ParameterInput' onchange='displayEntrySaved(false, ${entryId});' class='disableOnDisconnect form-select border-secondary'>\n`;
		for (let i = 0; i < commandCollection[commandId][1].length; i++) {
			htmlSelect += `<option value='${commandCollection[commandId][1][i][0]}' lang-data='${commandCollection[commandId][1][i][1]}'>${getLanguageAsText(commandCollection[commandId][1][i][1])}</option>\n`;
		}
		htmlSelect += "</select>";
		div.innerHTML = htmlSelect;
		if (parameter == undefined) parameter = 0;
	}

	cell.appendChild(div);
	document.getElementById("scheduleEntry" + entryId + "ParameterInput").value = parameter;

	//add label
	let label = document.createElement("label");
	label.htmlFor = `scheduleEntry${entryId}ParameterInput`;
	label.setAttribute('lang-data', 'parameter');
	label.innerHTML = getLanguageAsText('parameter');
	div.appendChild(label);
}

function addParameterToTrigger(triggerId, commandId, parameter) {
	let cell = getElement("trigger" + triggerId + "ParameterCell");
	cell.innerHTML = "";
	//add element
	let div = document.createElement("div");
	div.id = "trigger" + triggerId + "ParameterInputDiv";
	div.className = "form-floating mb-3";

	if (commandCollection[commandId][1] == false) {
		return;
	} else if (commandCollection[commandId][1] == "text") {
		div.innerHTML = `<input id='trigger${triggerId}ParameterInput' type='text' class='disableOnDisconnect form-control' maxlength='50' onkeyup='triggerSaved(false, 0);' lang-data='parameter'>`;
		if (parameter == undefined) parameter = "";
	} else if (Array.isArray(commandCollection[commandId][1])) {
		let htmlSelect = `<select id='trigger${triggerId}ParameterInput' class='disableOnDisconnect form-select border-secondary' style='width: 100%;' onchange='triggerSaved(false, 0);'>\n`;
		for (let i = 0; i < commandCollection[commandId][1].length; i++) {
			htmlSelect += `<option value='${commandCollection[commandId][1][i][0]}' lang-data='${commandCollection[commandId][1][i][1]}'>${getLanguageAsText(commandCollection[commandId][1][i][1])}</option>\n`;
		}
		htmlSelect += "</select>";
		div.innerHTML = htmlSelect;
		if (parameter == undefined) parameter = 0;
	}

	cell.appendChild(div);
	getElement("trigger" + triggerId + "ParameterInput").value = parameter;

	//add label
	let label = document.createElement("label");
	label.htmlFor = "trigger" + triggerId + "ParameterInput";
	label.setAttribute('lang-data', 'parameter');
	label.innerHTML = getLanguageAsText('parameter');
	div.appendChild(label);
}


function getScheduleFromServer() {
	let xmlhttp = new XMLHttpRequest();
	xmlhttp.onloadend = function() {
		let scheduleObj = JSON.parse(xmlhttp.responseText);
		for (let i = 0; i < scheduleObj.cron.length; i++) {//crons
			let cronObj = scheduleObj.cron[i];
			generateNewScheduleEntry(cronObj.enabled, cronObj.pattern, cronObj.start, cronObj.end, cronObj.command, cronObj.parameter, true, false);
		}
		addCommandsToDropdown("trigger0CommandSelect");//trigger
		for (let i = 0; i < scheduleObj.trigger.length; i++) {//trigger parameter
			let triggerObj = scheduleObj.trigger[i];
			if (triggerObj.trigger == 1) {
				startupTriggerIndex = i;
				getElement("trigger0EnabledSwitch").checked = triggerObj.enabled;
				getElement("trigger0CommandSelect").value = triggerObj.command;
				addParameterToTrigger(0, triggerObj.command, triggerObj.parameter);
				return;
			}
		}
	}
	xmlhttp.open('GET', 'cmd.php?id=10', true);
	xmlhttp.send();

}

function showModal(title="Titel", body="---", showClose=true, showCancel=true, cancelText=getLanguageAsText('cancel'), actionType=0, actionText=getLanguageAsText('ok'), actionFunction=function(){alert("Kein Befehl gesetzt")}) {
	modalTitle.innerText = title;
	modalBody.innerHTML = body;
	modalCloseBtn.hidden = !showClose;
	modalCancelBtn.hidden = !showCancel;
	modalCancelBtn.innerText = cancelText;
	if (actionType != 0) {
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

function isInDarkmode() {
	return !theme.href.includes("/bootstrap/css/bootstrap.min.css");
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
			updateButton.className = 'disableOnDisconnect btn btn-danger blink';
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

function download(path, filename) {
	let anchor = document.createElement('a');
	anchor.href = path;
	anchor.download = filename;
	anchor.click();
}

function importSchedule() {
	let input = document.createElement('input');
	input.type = 'file';
	input.accept = 'application/JSON';
	input.onchange = e => {
		let file = e.target.files[0];
		let reader = new FileReader();
		reader.readAsText(file,'UTF-8');
		reader.onload = readerEvent => {
			//loadScheduleJson(readerEvent.target.result);
		}
	}
	input.click();
}

//click events
document.getElementById("reloadBtn").onclick = function() {
	var xmlhttp = new XMLHttpRequest();
	xmlhttp.open('GET', 'cmd.php?id=1', true);
	xmlhttp.send();
}
document.getElementById("restartBtn").onclick = function() {
	showModal(getLanguageAsText('attention'), getLanguageAsText('reboot-really'), undefined, undefined, undefined, 4, getLanguageAsText('restart-device'), actionFunction=function(){
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

getElement("collapseMainSettings").addEventListener("shown.bs.collapse", event => {
	new Masonry(document.getElementById("masonry"));
});

getElement("collapseLoginSettings").addEventListener("shown.bs.collapse", event => {
	new Masonry(document.getElementById("masonry"));
});

function setDisplayProtocol() {
	let protocol = document.getElementById('displayProtocolSelect').value;
	sendHTTPRequest('GET', 'cmd.php?id=14&protocol=' + protocol, true);
	settingSaved("settingsButtonSaveDisplayProtocol");
}

function setDisplayProtocolSelect() {
	var xmlhttp = new XMLHttpRequest();
	xmlhttp.onloadend = function() {
		document.getElementById("displayProtocolSelect").value = xmlhttp.responseText.trim();
	}
	xmlhttp.open('GET', 'cmd.php?id=15', true);
	xmlhttp.send();
}

function setDisplayOrientation() {
	// 0 - horizontal, 1 - vertical, 2 - horizontal inverted, 3 - vertical inverted
	let orientation = document.getElementById('displayOrientationSelect').value;
	sendHTTPRequest('GET', 'cmd.php?id=16&orientation=' + orientation, true);
	settingSaved("settingsButtonSaveDisplayOrientation");
}

function setDisplayOrientationSelect() {
	var xmlhttp = new XMLHttpRequest();
	xmlhttp.onloadend = function() {
		document.getElementById("displayOrientationSelect").value = xmlhttp.responseText.trim();
	}
	xmlhttp.open('GET', 'cmd.php?id=17', true);
	xmlhttp.send();
}

function setHostname(elementId) {
	let hostname = document.getElementById(elementId).value;
	let xmlhttp = new XMLHttpRequest();
	xmlhttp.open('POST', 'cmd.php?id=4', true);
	xmlhttp.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
	xmlhttp.send("hostname=" + hostname);
	settingSaved("settingsButtonSaveHostname");
}

function setWebLoginAndPassword() {
	var xmlhttp = new XMLHttpRequest();
	xmlhttp.open('POST', 'cmd.php?id=7', true);
	xmlhttp.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
	xmlhttp.send("user=" + document.getElementById("webUserInput").value + "&pwd=" + document.getElementById("webPasswordInput").value);
}

function settingSaved(elementId) {
	let element = document.getElementById(elementId);
	element.className = "disableOnDisconnect btn btn-success ms-3 mb-3";
	element.innerHTML = "<i class='bi bi-check2'></i>";
}

function settingNotSaved(elementId) {
	let element = document.getElementById(elementId);
	element.className = "disableOnDisconnect btn btn-outline-success ms-3 mb-3";
	element.innerHTML = "<i class='bi bi-save'></i>";
}

function triggerSaved(saved, triggerId) {
	let element = getElement("trigger" + triggerId + "SaveButton");
	if (saved) {
		element.className = "disableOnDisconnect btn btn-success mt-2";
		element.innerHTML = "<i class='bi bi-check2 pe-2'></i><span lang-data='saved'>" + getLanguageAsText("saved") + "</span>";
	} else {
		element.className = "disableOnDisconnect btn btn-outline-success mt-2";
		element.innerHTML = "<i class='bi bi-save pe-2'></i><span lang-data='save'>" + getLanguageAsText("save") + "</span>";
	}
}


function showEntryHeader(entryId) {
	let sel = getElement("commandSelect" + entryId);
	getElement("scheduleEntry" + entryId + "HeaderCommand").innerText = sel.options[sel.selectedIndex].text;
	getElement("scheduleEntry" + entryId + "HeaderCommand").setAttribute("lang-data", commandCollection[sel.value][0]);
	getElement("scheduleEntry" + entryId + "HeaderCron").innerText = document.getElementById("cronentry" + entryId).value;
}

function toggleValidityFrom(entryId, checked){
	entry1 = document.getElementById('entry' + entryId + 'ValidityTimeSpanFrom1');
	entry2 = document.getElementById('entry' + entryId + 'ValidityTimeSpanFrom2');
	if (checked) {
		entry1.style.visibility = "";
		entry2.style.visibility = "";	
	} else {
		entry1.style.visibility = "hidden";
		entry2.style.visibility = "hidden";
	}
}

function toggleValidityTo(entryId, checked){
	entry1 = document.getElementById('entry' + entryId + 'ValidityTimeSpanTo1');
	entry2 = document.getElementById('entry' + entryId + 'ValidityTimeSpanTo2');
	if (checked) {
		entry1.style.visibility = "";
		entry2.style.visibility = "";
	} else {
		entry1.style.visibility = "hidden";
		entry2.style.visibility = "hidden";
	}
}

function saveTrigger(triggerId) {
	if (triggerId != 0) return;//only startup trigger
	if (startupTriggerIndex > -1) {
		if (getElement("trigger" + triggerId + "CommandSelect").value == 0) {//if no command selected, delete
			sendHTTPRequest('GET', 'cmd.php?id=20&cmd=delete&index=' + startupTriggerIndex, true);
			return;
		}
		sendHTTPRequest('GET', 'cmd.php?id=20&cmd=update&index=' + startupTriggerIndex + '&' + prepareTriggerString(triggerId), true);
		return;
	}
	sendHTTPRequest('GET', 'cmd.php?id=20&cmd=add&' + prepareTriggerString(triggerId), true);
	startupTriggerIndex++;
}

function prepareTriggerString(triggerId) {
	//get elements
	let enabled = document.getElementById("trigger" + triggerId + "EnabledSwitch").checked;
	let command = document.getElementById("trigger" + triggerId + "CommandSelect").value;
	let parameterElement = document.getElementById("trigger" + triggerId + "ParameterInput");
	let parameter = parameterElement != null ? parameterElement.value : null;

	let msg = "enabled=" + enabled.toString().trim() + "&";
	if (command != 0) msg += "command=" + command + "&";
	if (parameter != null) msg += "parameter=" + parameter + "&";
	if (triggerId == 0) msg += "trigger=1&";
	msg = msg.substring(0, msg.length - 1);

	return msg;
}

function saveEntry(entryId) {
	//send to server
	let command = document.getElementById("commandSelect" + entryId).value;
	if (document.getElementById("entryInfo" + entryId).getAttribute("data") == "true") {//add
		if (commandCollection[command][0] == "" || command == 0) {
			showModal(getLanguageAsText("error"), getLanguageAsText("fill-required-fields"), false, true, getLanguageAsText("ok"));
			document.getElementById("collapseEntry" + entryId + "Collection").className += " show";
			return;
		}

		sendHTTPRequest('GET', 'cmd.php?id=9&cmd=add&' + prepareCronString(entryId), true);
		displayEntrySaved(true, entryId);
		document.getElementById("entryInfo" + entryId).setAttribute("data", "false");

	} else {//update
		if (commandCollection[command][0] == "" || command == 0) {
			showModal(getLanguageAsText("error"), getLanguageAsText("fill-required-fields"), false, true, getLanguageAsText("ok"));
			document.getElementById("collapseEntry" + entryId + "Collection").className += " show";
			return;
		}

		sendHTTPRequest('GET', 'cmd.php?id=9&cmd=update&' + prepareCronString(entryId) + '&index=' + entryId, true);
		displayEntrySaved(true, entryId);
	}
}

function deleteEntry(entryId) {
	scheduleEntryCount -= 1;
	sendHTTPRequest('GET', 'cmd.php?id=9&cmd=delete&index=' + entryId, true);

	document.getElementById('entry' + entryId).remove();
}

function prepareCronString(entryId) {
	//get elements
	let enabled = document.getElementById("entry" + entryId + "EnabledSwitchCheck").checked;
	let cronentry = document.getElementById("cronentry" + entryId).value;
	let command = document.getElementById("commandSelect" + entryId).value;
	let parameterElement = document.getElementById("scheduleEntry" + entryId + "ParameterInput");
	let parameter = parameterElement != null ? parameterElement.value : null;
	let startTime = document.getElementById("scheduleEntry" + entryId + "StartTime").value;
	let endTime = document.getElementById("scheduleEntry" + entryId + "EndTime").value;
	let startDate = document.getElementById("scheduleEntry" + entryId + "StartDate").value;
	let endDate = document.getElementById("scheduleEntry" + entryId + "EndDate").value;
	let startDateTime = document.getElementById("entry" + entryId + "ValiditySwitchCheckFrom").checked;
	let endDateTime = document.getElementById("entry" + entryId + "ValiditySwitchCheckTo").checked;

	let msg = "enabled=" + enabled.toString().trim() + "&";
	msg += "pattern=" + cronentry + "&";
	if (startDateTime) msg += "start=" + startDate + " " + startTime + "&";
	else msg += "start= &";
	if (endDateTime) msg += "end=" + endDate + " " + endTime + "&";
	else msg += "end= &";
	if (command != 0) msg += "command=" + command + "&";
	if (parameter != null) msg += "parameter=" + parameter + "&";
	msg = msg.substring(0, msg.length - 1);

	return msg;
}

function displayEntrySaved(saved, entryId) {
	if (saved) {
		document.getElementById("scheduleEntry" + entryId + "HeaderSaved").innerHTML = "<i class='bi bi-file-earmark-check-fill bigIcon px-2' style='color: green;'></i>";
	} else {
		document.getElementById("scheduleEntry" + entryId + "HeaderSaved").innerHTML = "<i class='bi bi-file-earmark-x-fill bigIcon px-2' style='color: red;'></i>";
	}
}

function enabledChanged(check, entryId) {
	if (check.checked) {
		document.getElementById("scheduleEntry" + entryId + "HeaderEnabled").innerHTML = "<i class='bi bi-check-lg bigIcon pe-2' style='color: green;'></i>";
	} else {
		document.getElementById("scheduleEntry" + entryId + "HeaderEnabled").innerHTML = "<i class='bi bi-x-lg bigIcon pe-2' style='color: red;'></i>";
	}
}

//main
window.onload = function() {
	setDarkMode(window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches);
	getDefaultLanguage();
	setDisplayProtocolSelect();
	setDisplayOrientationSelect();
	st = null;
	var xmlhttp = new XMLHttpRequest();
	xmlhttp.timeout = 1000;
	xmlhttp.open('GET', 'cmd.php?id=5', true);
	//load periodical the current infos about the system
	xmlhttp.onload = function() {
		idleBadge.id = "notIdle";
		setTimeout(function(){idleBadge.id = "idle"}, 100);
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
		ramUsage.innerHTML = Number(jsonData.ramUsed / jsonData.ramTotal * 100).toFixed(2);
		spinnerDisplayOn.hidden = !jsonData.display.onSet;
		spinnerDisplayStandby.hidden = !jsonData.display.standbySet;
		if (new Date(jsonData.screenshotTime * 1000) != st) {
			st = new Date(jsonData.screenshotTime * 1000);
			screenshotTime.innerHTML = `${addLeadingZero(st.getDate())}.${addLeadingZero(st.getMonth() + 1)}.${1900 + st.getYear()} - ${addLeadingZero(st.getHours())}:${addLeadingZero(st.getMinutes())}:${addLeadingZero(st.getSeconds())}`;
			screenshot.src = "piScreenScreenshot.png?t=" + new Date().getTime();
		}
		var x = new XMLHttpRequest();
		x.onloadend = function() {
			getElement("screenContent").innerHTML = x.responseText.trim();
		}
		x.open('GET', 'cmd.php?id=21', true);
		x.send();

		enableElements(true);

		new Masonry(document.getElementById("masonry"));
	}
	xmlhttp.onerror = function() {
		setToUnknownValues();
		enableElements(false);
	}
	xmlhttp.ontimeout = function() {
		setToUnknownValues();
		enableElements(false);
		//var today = new Date();
		//showModal(getLanguageAsText("error"), getLanguageAsText("connection-lost") + "<br>" + today.getFullYear() + '-' + (today.getMonth() + 1) + '-' + today.getDate() + "<br>" + today.getHours() + ":" + today.getMinutes() + ":" + today.getSeconds(), false, true, getLanguageAsText("ok"));
	}
	xmlhttp.send();

	//reload infos every 2 seconds
	setInterval(function() {
		xmlhttp.open('GET', 'cmd.php?id=5', true);
		xmlhttp.send();
	}, 2000);
	checkForUpdate();
}

// language functions
function fetchLanguage(lang) {
	currentLanguage = lang;
	sendHTTPRequest('GET', 'cmd.php?id=13&lang=' + lang, true);
	document.getElementById(lang).selected = true;
	var xmlhttp = new XMLHttpRequest();
	xmlhttp.onloadend = function() {
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
		getScheduleFromServer();
	}
	xmlhttp.open('GET', 'cmd.php?id=12', true);
	xmlhttp.send();
}

function sendHTTPRequest(method, url, async) {
	var xmlhttp = new XMLHttpRequest();
	xmlhttp.onloadend = function() {
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
	setDarkMode(event.matches);
});