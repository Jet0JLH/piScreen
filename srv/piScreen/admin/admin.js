//necessary html elements
darkmodeButton = document.getElementById("darkmodeButton");
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
displayOnBtn = document.getElementById("displayOnButton");
displayStandbyBtn = document.getElementById("displayStandbyButton");
spinnerDisplayOn = document.getElementById("spinnerDisplayOn");
spinnerDisplayStandby = document.getElementById("spinnerDisplayStandby");
//info
screenshot = document.getElementById("screenshot");
screenshotTime = document.getElementById("screenshotTime");
//schedule
var scheduleEntryCount = 0;
var commandsetEntryCount = 0;
var commandEntryCounts = {};
var unsavedCommandsets = 0;
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
var scheduleEntryShown = false;
//import
var scheduleToImport = null;
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
var languageStrings = null;

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

function generateNewScheduleEntry(enabled=true, pattern="* * * * *", start="", end="", command=0, commandset=0, parameter="", saved=false, newScheduleEntry=true) {
	let eId = scheduleEntryCount;
	if (command < 0 || command > commandCollection.length - 1) {
		console.error("Command " + command + " not known! CronID: " + eId);
		command = 0;
	} else if (commandCollection[command][0] == "") {
		console.error("Command " + command + " not assigned! CronID: " + eId);
		command = 0;
	}

	let startDate = start.split(" ")[0];
	let startTime = start.split(" ")[1];
	let endDate = end.split(" ")[0];
	let endTime = end.split(" ")[1];
	let newScheduleEntryObj = document.createElement('div');
	newScheduleEntryObj.id = "scheduleEntry" + eId;
	newScheduleEntryObj.className = "accordion-item border border-primary";
	newScheduleEntryObj.style.backgroundColor = "transparent";
	newScheduleEntryObj.innerHTML = `	<h2 class="accordion-header">
			<label id='scheduleEntry${eId}Label' class="accordion-button collapsed" data-bs-toggle="collapse" data-bs-target="#collapseScheduleEntry${eId}Collection" style='width: 100%; cursor: pointer;'>
				<span id='scheduleEntry${eId}HeaderEnabled' style='width: 10%;'>${enabled ? "<i class='bi bi-check-lg bigIcon pe-2' style='color: green;'></i>" : "<i class='bi bi-x-lg bigIcon pe-2' style='color: red;'></i>"}</span>
				<span id='scheduleEntry${eId}HeaderCommandset' class='px-2' style='width: 30%;'>${commandset}</span>
				<span id='scheduleEntry${eId}HeaderCommand' class='px-2' style='width: 30%;' lang-data='${commandCollection[command][0]}'>${commandCollection[command][0]}</span>
				<span id='scheduleEntry${eId}HeaderCron' class='px-2' style='width: 20%;'>${pattern}</span>
				<span id='scheduleEntry${eId}HeaderSaved' class='px-2 text-end' style='width: 10%;'></span>
			</label>
		</h2>
		<div id="collapseScheduleEntry${eId}Collection" class="accordion-collapse collapse" data-bs-parent="#scheduleEntryCollectionAccordion">
			<div class="accordion-body">
				<table class="table-sm" style='width: 100%;'>
					<div id='scheduleEntry${eId}'>
						<tr>
							<td style='width: 50%;'>
								<div class="form-check form-switch">
									<input class="disableOnDisconnect form-check-input" type="checkbox" role="switch" id="scheduleEntry${eId}EnabledSwitchCheck" onchange="enabledChanged(this, ${eId}); displayScheduleEntrySaved(false, ${eId});" ${enabled ? "checked" : ""}>
									<label class="form-check-label" for="scheduleEntry${eId}EnabledSwitchCheck" lang-data="active">Aktiviert</label>
								</div>
							</td>
							<td style='width: 50%;'>
								<button id="scheduleEntry${eId}ButtonExecute" class="disableOnDisconnect btn btn-outline-warning mt-2" onclick='executeScheduleEntry();' style='float: right;'><i class='bi bi-play pe-2'></i><span lang-data="execute">Ausführen</span></button>
							</td>
						</tr>
						<tr>
							<td>
								<div class='form-floating'>
									<input type='text' class='disableOnDisconnect form-control border border-secondary' name='cronentry' id='cronentry${eId}' value='${pattern}' onkeyup='checkCronEntryValidity(this, ${eId}); showScheduleEntryHeader(${eId}); displayScheduleEntrySaved(false, ${eId});'>
									<label for='cronentry${eId}'lang-data="cron-entry">Croneintrag</label>
								</div>
							</td>
							<td>
								<i class='bi-question-octagon p-2' style='cursor: pointer;' id='cronEntry${eId}Help' data-bs-toggle="tooltip" data-bs-placement="top" data-bs-title="${getLanguageAsText('help')}" onclick='showModal(getLanguageAsText("help"), getLanguageAsText("cronHelpText"), false, true, getLanguageAsText("ok"));'></i>
							</td>
						</tr>
						<tr>
							<td colspan="2">
								<div class='form-floating'>
									<select id='scheduleEntry${eId}CommandsetSelect' class='disableOnDisconnect form-select border border-secondary' onchange='showScheduleEntryHeader(${eId}); displayScheduleEntrySaved(false, ${eId});' value='${commandset}'>
									</select>
									<label for="scheduleEntry${eId}CommandsetSelect" lang-data="choose-commandset">Befehlssatz auswählen</label>
								</div>
							</td>
						</tr>
						<tr>
							<td>
								<div class='form-floating'>
									<select id='scheduleEntry${eId}CommandSelect' class='disableOnDisconnect form-select border border-secondary' onchange='showScheduleEntryHeader(${eId}); displayScheduleEntrySaved(false, ${eId}); addParameterToScheduleEntry(${eId}, value);'>
									</select>
									<label for="scheduleEntry${eId}CommandSelect" lang-data="choose-command">Befehl auswählen</label>
								</div>
							</td>
							<td id="scheduleEntry${eId}ParameterCell">
							</td>
						</tr>
						<tr>
							<td colspan='3' class='p-0'>
								<table class='p-0' style="width: 100%;">
									<tr>
										<td colspan='2' class='p-2'>
											<div class="form-check form-switch">
												<input class="disableOnDisconnect form-check-input" type="checkbox" role="switch" id="scheduleEntry${eId}ValiditySwitchCheckFrom" onchange='toggleValidityFrom(${eId}, checked); displayScheduleEntrySaved(false, ${eId});' ${start != "" ? "checked" : ""}>
												<label class="form-check-label" for="scheduleEntry${eId}ValiditySwitchCheckFrom" lang-data="valid-from">Gültig von</label>
											</div>
										</td>
										<td colspan='2' class='p-2'>
											<div class="form-check form-switch">
												<input class="disableOnDisconnect form-check-input" type="checkbox" role="switch" id="scheduleEntry${eId}ValiditySwitchCheckTo" onchange='toggleValidityTo(${eId}, checked); displayScheduleEntrySaved(false, ${eId});' ${end != "" ? "checked" : ""}>
												<label class="form-check-label" for="scheduleEntry${eId}ValiditySwitchCheckTo" lang-data="valid-to">Gültig bis</label>
											</div>
										</td>
									</tr>
									<tr>
										<td id='scheduleEntry${eId}ValidityTimeSpanFrom1' class='px-2' lang-data='from'>
											von
										</td>
										<td id='scheduleEntry${eId}ValidityTimeSpanFrom2'>
											<div class='input-group'>
												<input id='scheduleEntry${eId}StartTime' name='scheduleEntry${eId}StartDateTime' type="time" class="disableOnDisconnect form-control border border-secondary p-1" onchange="displayScheduleEntrySaved(false, ${eId});" style="text-align: center; width: 40%;" value="${startTime}">
												<input id='scheduleEntry${eId}StartDate' type="date" class="disableOnDisconnect form-control border border-secondary p-1" style="text-align: center; width: 60%;" value="${startDate}">
											</div>
										</td>
										<td id='scheduleEntry${eId}ValidityTimeSpanTo1' class='px-2' lang-data='to'>
											bis
										</td>
										<td id='scheduleEntry${eId}ValidityTimeSpanTo2'>
											<div class='input-group'>
												<input id='scheduleEntry${eId}EndTime' name='scheduleEntry${eId}EndDateTime' type="time" class="disableOnDisconnect form-control border border-secondary p-1" onchange="displayScheduleEntrySaved(false, ${eId});" style="text-align: center; width: 40%;" value="${endTime}">
												<input id='scheduleEntry${eId}EndDate' type="date" class="disableOnDisconnect form-control border border-secondary p-1" style="text-align: center; width: 60%;" value="${endDate}">
											</div>
										</td>
									</tr>
								</table>
							</td>
						</tr>
					</div>
				</table>
				<button id="scheduleEntry${eId}SaveButton" class="disableOnDisconnect btn btn-outline-success mt-2" onclick='saveScheduleEntry(${eId})' data-bs-toggle="collapse" data-bs-target="#collapseScheduleEntry${eId}Collection"><i class='bi bi-save pe-2'></i><span lang-data="save">Speichern</span></button>
				<button id="scheduleEntry${eId}ButtonDelete" class="disableOnDisconnect btn btn-danger mt-2" onclick='deleteScheduleEntry(${eId})' style='float: right;'><i class='bi bi-trash pe-2'></i><span lang-data='delete-commandset'>${getLanguageAsText("delete-entry")}</span></button>
				<i id='scheduleEntryInfo${eId}' data='${newScheduleEntry}' class='bi bi-info-circle mt-3' style="float: right;" data-bs-toggle="tooltip" data-bs-placement="right" data-bs-title="CronID: ${eId}" hidden></i>
			</div>
		</div>
	</div>`;

	//Adding element to document
	getElement("scheduleEntryCollectionAccordion").appendChild(newScheduleEntryObj);
	if (newScheduleEntry) getElement("scheduleEntry" + eId + "Label").click();

	displayScheduleEntrySaved(saved, eId);

	toggleValidityFrom(eId, document.getElementById("scheduleEntry" + eId + "ValiditySwitchCheckFrom").checked);
	toggleValidityTo(eId, document.getElementById("scheduleEntry" + eId + "ValiditySwitchCheckTo").checked);

	addCommandsetsToDropdown("scheduleEntry" + eId + "CommandsetSelect", commandset);

	addCommandsToDropdown("scheduleEntry" + eId + "CommandSelect");
	getElement("scheduleEntry" + eId + "CommandSelect").value = command;
	addParameterToScheduleEntry(eId, command, parameter);

	showScheduleEntryHeader(eId);
	tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
	tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
	scheduleEntryCount += 1;
}

function addCommandsToDropdown(dropdownId) {
	//Add commands dropdown options
	getElement(dropdownId).innerHTML = "";
	for (let i = 0; i < commandCollection.length; i++) {
		if (commandCollection[i][0] != "") {
			let optionTag = document.createElement("option");
			optionTag.value = i;
			optionTag.setAttribute('lang-data', commandCollection[i][0]);
			optionTag.innerHTML = getLanguageAsText(commandCollection[i][0]);
			getElement(dropdownId).appendChild(optionTag);
		}
	}
}

function addParameterToScheduleEntry(scheduleEntryId, commandId, parameter) {
	let cell = getElement("scheduleEntry" + scheduleEntryId + "ParameterCell");
	cell.innerHTML = "";
	//add element
	let div = document.createElement("div");
	div.id = "scheduleEntry" + scheduleEntryId + "ParameterInputDiv";
	div.className = "form-floating";

	if (commandCollection[commandId][1] == false) {
		return;
	} else if (commandCollection[commandId][1] == "text") {
		div.innerHTML = `<input id='scheduleEntry${scheduleEntryId}ParameterInput' type='text' class='disableOnDisconnect form-control border border-secondary' onkeyup='displayScheduleEntrySaved(false, ${scheduleEntryId});' value='${parameter}' lang-data='parameter'>`;
		if (parameter == undefined) parameter = "";
	} else if (Array.isArray(commandCollection[commandId][1])) {
		let htmlSelect = `<select id='scheduleEntry${scheduleEntryId}ParameterInput' onchange='displayScheduleEntrySaved(false, ${scheduleEntryId});' class='disableOnDisconnect form-select border border-secondary'>\n`;
		for (let i = 0; i < commandCollection[commandId][1].length; i++) {
			htmlSelect += `<option value='${commandCollection[commandId][1][i][0]}' lang-data='${commandCollection[commandId][1][i][1]}'>${getLanguageAsText(commandCollection[commandId][1][i][1])}</option>\n`;
		}
		htmlSelect += "</select>";
		div.innerHTML = htmlSelect;
		if (parameter == undefined) parameter = 0;
	}

	cell.appendChild(div);
	getElement("scheduleEntry" + scheduleEntryId + "ParameterInput").value = parameter;

	//add label
	let label = document.createElement("label");
	label.htmlFor = "scheduleEntry" + scheduleEntryId + "ParameterInput";
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
		div.innerHTML = `<input id='trigger${triggerId}ParameterInput' type='text' class='disableOnDisconnect form-control border border-secondary' onkeyup='triggerSaved(false, 0);' lang-data='parameter'>`;
		if (parameter == undefined) parameter = "";
	} else if (Array.isArray(commandCollection[commandId][1])) {
		let htmlSelect = `<select id='trigger${triggerId}ParameterInput' class='disableOnDisconnect form-select border border-secondary' style='width: 100%;' onchange='triggerSaved(false, 0);'>\n`;
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
		loadScheduleJson(xmlhttp.responseText)
	}
	xmlhttp.open('GET', 'cmd.php?id=10', true);
	xmlhttp.send();
}

function loadScheduleJson(jsonString) {
	scheduleEntryCount = 0;
	commandsetEntryCount = 0;
	commandEntryCounts = {};
	let scheduleObj = JSON.parse(jsonString);
	for (let i = 0; i < scheduleObj.commandsets.length; i++) {
		commandEntryCounts[scheduleObj.commandsets[i].id] = 0;
	}
	getElement("commandsetCollectionAccordion").innerHTML = "";
	for (let i = 0; i < scheduleObj.commandsets.length; i++) {//commandsets
		let commandsetCommandsArray = [];
		let commandsetObj = scheduleObj.commandsets[i];
		for (let j = 0; j < commandsetObj.commands.length; j++) {//commands
			commandsetCommandsArray.push([commandsetObj.commands[j].command, commandsetObj.commands[j].parameter]);
		}
		generateCommandsetEntry(commandsetObj.name, commandsetCommandsArray, commandsetObj.id, true);
	}
	getElement("scheduleEntryCollectionAccordion").innerHTML = "";
	for (let i = 0; i < scheduleObj.cron.length; i++) {//crons
		let cronObj = scheduleObj.cron[i];
		generateNewScheduleEntry(cronObj.enabled, cronObj.pattern, cronObj.start, cronObj.end, cronObj.command, cronObj.commandset, cronObj.parameter, true, false);
	}
	addCommandsToDropdown("trigger0CommandSelect");//trigger
	addCommandsetsToDropdown("trigger0CommandsetSelect");//trigger
	for (let i = 0; i < scheduleObj.trigger.length; i++) {//trigger parameter
		let triggerObj = scheduleObj.trigger[i];
		if (triggerObj.trigger == 1) {
			startupTriggerIndex = i;
			getElement("trigger0EnabledSwitch").checked = triggerObj.enabled;
			getElement("trigger0CommandSelect").value = triggerObj.command;
			getElement("trigger0CommandsetSelect").value = triggerObj.commandset;
			addParameterToTrigger(0, triggerObj.command, triggerObj.parameter);
			break;
		}
	}}

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
		darkmodeButton.classList.replace("btn-outline-secondary", "btn-outline-light");
		languageSelect.classList.replace("border-secondary", "border-light");
	} else {
		theme.href = "/bootstrap/css/bootstrap.min.css";
		darkmodeButton.classList.replace("btn-outline-light", "btn-outline-secondary");
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

function setSchedule() {
	if (importSchedule(scheduleToImport)) {
		getElement("importScheduleInputTextfield").value = "";
		settingSaved("settingsButtonSaveImportSchedule", true);
		showModal(getLanguageAsText('info'), getLanguageAsText('import-success'), true, true, getLanguageAsText('ok'), 0);
	}
}

function selectScheduleToImport() {
	let input = document.createElement('input');
	input.type = 'file';
	input.accept = 'application/JSON';
	input.onchange = e => {
		let file = e.target.files[0];
		getElement("importScheduleInputTextfield").value = file.name;
		let reader = new FileReader();
		reader.readAsText(file, 'UTF-8');
		reader.onload = readerEvent => {
			scheduleToImport = readerEvent.target.result;
			settingSaved("settingsButtonSaveImportSchedule", false);
		}
	}
	input.click();
}

function dropScheduleJson(ev) {
	ev.preventDefault();
	let file = ev.dataTransfer.files[0];
	getElement("importScheduleInputTextfield").value = file.name;
	let reader = new FileReader();
	reader.readAsText(file, 'UTF-8');
	reader.onload = readerEvent => {
		scheduleToImport = readerEvent.target.result;
		settingSaved("settingsButtonSaveImportSchedule", false);
	}
}

function importSchedule(scheduleAsJson) {
	if (scheduleToImport == null) {
		showModal(getLanguageAsText('import-failed'), getLanguageAsText('file-empty'), true, true, getLanguageAsText('ok'), 0);
		return false;
	}
	try {
		loadScheduleJson(scheduleAsJson);
	} catch (error) {
		showModal(getLanguageAsText('import-failed'), getLanguageAsText('file-wrong-format'), true, true, getLanguageAsText('ok'), 0);
		return false;
	}
	try {
		saveEntireSchedule(scheduleAsJson);	
	} catch (error) {
		showModal(getLanguageAsText('import-failed'), getLanguageAsText('schedule-save-failed'), true, true, getLanguageAsText('ok'), 0);
		return false;
	}
	scheduleToImport = null;
	return true;
}

function saveEntireSchedule(jsonString) {
	let xmlhttp = new XMLHttpRequest();
	xmlhttp.open('POST', 'cmd.php?id=18', true);
	xmlhttp.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
	xmlhttp.send(jsonString);
}

//click events
function reloadBrowser() {
	sendHTTPRequest('GET', 'cmd.php?id=1', true, () => {});
}

function restartHost() {
	showModal(getLanguageAsText('attention'), getLanguageAsText('reboot-really'), undefined, undefined, undefined, 4, getLanguageAsText('restart-device'), () => {sendHTTPRequest('GET', 'cmd.php?id=2', true, () => {}); modal.hide();});
}

function shutdownHost() {
	showModal(getLanguageAsText('attention'), getLanguageAsText('shutdown-really'), undefined, undefined, undefined, 4, getLanguageAsText('shutdown-device'), () => {sendHTTPRequest('GET', 'cmd.php?id=3', true, () => {}); modal.hide();});
}

function setDisplayOn() {
	sendHTTPRequest('GET', 'cmd.php?id=8&cmd=1', true, () => {spinnerDisplayOn.hidden = false;});
}

function setDisplayStandby() {
	sendHTTPRequest('GET', 'cmd.php?id=8&cmd=0', true, () => {spinnerDisplayStandby.hidden = false;});
}

function showPiscreenInfo() {
	let xmlhttp = new XMLHttpRequest();
	xmlhttp.onload = function() {
		let jsonData = JSON.parse(xmlhttp.responseText);
		showModal(getLanguageAsText('about-info'), getLanguageAsText('info-text') + ' ' + jsonData.version.major + '.' + jsonData.version.minor + '.' + jsonData.version.patch, false, true, getLanguageAsText('alright'));
	}
	xmlhttp.open('GET', 'cmd.php?id=11', true);
	xmlhttp.send();
}

function rearrangeGui() {
	new Masonry(document.getElementById("masonry"));
}
function showTimeSchedule() {
	rearrangeGui();
}

getElement("collapseMainSettings").addEventListener("shown.bs.collapse", event => {
	rearrangeGui();
});

getElement("collapseLoginSettings").addEventListener("shown.bs.collapse", event => {
	rearrangeGui();
});

getElement("showCommandsets").addEventListener("shown.bs.collapse", event => {
	rearrangeGui();
});

getElement("showTimeschedule").addEventListener("shown.bs.collapse", event => {
	rearrangeGui();
});

function setDisplayProtocol() {
	let protocol = document.getElementById('displayProtocolSelect').value;
	sendHTTPRequest('GET', 'cmd.php?id=14&protocol=' + protocol, true, () => settingSaved("settingsButtonSaveDisplayProtocol", true));
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
	sendHTTPRequest('GET', 'cmd.php?id=16&orientation=' + orientation, true, () => settingSaved("settingsButtonSaveDisplayOrientation", true));
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
	settingSaved("settingsButtonSaveHostname", true);
}

function setWebLoginAndPassword() {
	var xmlhttp = new XMLHttpRequest();
	xmlhttp.open('POST', 'cmd.php?id=7', true);
	xmlhttp.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
	xmlhttp.send("user=" + document.getElementById("webUserInput").value + "&pwd=" + document.getElementById("webPasswordInput").value);
}

function settingSaved(elementId, saved) {
	let element = document.getElementById(elementId);
	if (saved) {
		element.className = "disableOnDisconnect btn btn-success ms-3 mb-3";
		element.innerHTML = "<i class='bi bi-check2'></i>";
	} else {
		element.className = "disableOnDisconnect btn btn-outline-success ms-3 mb-3";
		element.innerHTML = "<i class='bi bi-save'></i>";
	}
}

function triggerSaved(saved, triggerId) {
	let saveButtonElement = getElement("trigger" + triggerId + "SaveButton");
	let executeButtonElement = getElement("trigger" + triggerId + "ExecuteButton");
	if (saved) {
		saveButtonElement.className = "disableOnDisconnect btn btn-success mt-2";
		saveButtonElement.innerHTML = "<i class='bi bi-check2 pe-2'></i><span lang-data='saved'>" + getLanguageAsText("saved") + "</span>";
		executeButtonElement.className = "disableOnDisconnect btn btn-outline-warning mt-2"
		executeButtonElement.disabled = false;
	} else {
		saveButtonElement.className = "disableOnDisconnect btn btn-outline-success mt-2";
		saveButtonElement.innerHTML = "<i class='bi bi-save pe-2'></i><span lang-data='save'>" + getLanguageAsText("save") + "</span>";
		executeButtonElement.className = "btn btn-outline-warning mt-2"
		executeButtonElement.disabled = true;
	}
}

function executeStartupTrigger() {
	sendHTTPRequest('GET', 'cmd.php?id=20&cmd=execute&index=' + startupTriggerIndex, true, () => {});
}

function showScheduleEntryHeader(scheduleEntryId) {
	let commandSelect = getElement("scheduleEntry" + scheduleEntryId + "CommandSelect");
	getElement("scheduleEntry" + scheduleEntryId + "HeaderCommand").innerText = commandSelect.options[commandSelect.selectedIndex].text;
	getElement("scheduleEntry" + scheduleEntryId + "HeaderCommand").setAttribute("lang-data", commandCollection[commandSelect.value][0]);
	let commandsetSelect = getElement("scheduleEntry" + scheduleEntryId + "CommandsetSelect");
	getElement("scheduleEntry" + scheduleEntryId + "HeaderCommandset").innerText = commandsetSelect.options[commandsetSelect.selectedIndex].text;
	getElement("scheduleEntry" + scheduleEntryId + "HeaderCron").innerText = getElement("cronentry" + scheduleEntryId).value;
}

function toggleValidityFrom(scheduleEntryId, checked){
	scheduleEntry1 = document.getElementById('scheduleEntry' + scheduleEntryId + 'ValidityTimeSpanFrom1');
	scheduleEntry2 = document.getElementById('scheduleEntry' + scheduleEntryId + 'ValidityTimeSpanFrom2');
	if (checked) {
		scheduleEntry1.style.visibility = "";
		scheduleEntry2.style.visibility = "";
	} else {
		scheduleEntry1.style.visibility = "hidden";
		scheduleEntry2.style.visibility = "hidden";
	}
}

function toggleValidityTo(scheduleEntryId, checked){
	scheduleEntry1 = document.getElementById('scheduleEntry' + scheduleEntryId + 'ValidityTimeSpanTo1');
	scheduleEntry2 = document.getElementById('scheduleEntry' + scheduleEntryId + 'ValidityTimeSpanTo2');
	if (checked) {
		scheduleEntry1.style.visibility = "";
		scheduleEntry2.style.visibility = "";
	} else {
		scheduleEntry1.style.visibility = "hidden";
		scheduleEntry2.style.visibility = "hidden";
	}
}

function saveTrigger(triggerId) {
	if (triggerId != 0) return;//only startup trigger
	if (startupTriggerIndex > -1) {
		if (getElement("trigger" + triggerId + "CommandSelect").value == 0 && getElement("trigger" + triggerId + "CommandsetSelect").value == 0) {//if no command or commandset selected, delete
			sendHTTPRequest('GET', 'cmd.php?id=20&cmd=delete&index=' + startupTriggerIndex, true, () => {});
			startupTriggerIndex--;
			return;
		}
		sendHTTPRequest('GET', 'cmd.php?id=20&cmd=update&index=' + startupTriggerIndex + '&' + prepareTriggerString(triggerId), true, () => {});
		return;
	}
	sendHTTPRequest('GET', 'cmd.php?id=20&cmd=add&' + prepareTriggerString(triggerId), true, () => {});
	startupTriggerIndex++;
}

function prepareTriggerString(triggerId) {
	let enabled = getElement("trigger" + triggerId + "EnabledSwitch").checked;
	let command = getElement("trigger" + triggerId + "CommandSelect").value;
	let commandset = getElement("trigger" + triggerId + "CommandsetSelect").value;
	let parameterElement = getElement("trigger" + triggerId + "ParameterInput");
	let parameter = parameterElement != null ? parameterElement.value : null;

	let msg = "enabled=" + enabled.toString().trim() + "&";
	msg += "command=" + command + "&";
	msg += "commandset=" + commandset + "&";
	if (parameter != null) {
		parameter = parameter.replaceAll("%20", " ");
		parameter = parameter.replaceAll("\"", "\\\"");
		msg += "parameter=\"" + encodeURIComponent(parameter) + "\"&";
	}
	if (triggerId == 0) msg += "trigger=1&";
	msg = msg.substring(0, msg.length - 1);

	return msg;
}

function saveScheduleEntry(scheduleEntryId) {
	//send to server
	if (document.getElementById("scheduleEntryInfo" + scheduleEntryId).getAttribute("data") == "true") {//add
		sendHTTPRequest('GET', 'cmd.php?id=9&cmd=add&' + prepareScheduleString(scheduleEntryId), true, () => displayScheduleEntrySaved(true, scheduleEntryId));
		getElement("scheduleEntryInfo" + scheduleEntryId).setAttribute("data", "false");
	} else {//update
		sendHTTPRequest('GET', 'cmd.php?id=9&cmd=update&' + prepareScheduleString(scheduleEntryId) + '&index=' + scheduleEntryId, true, () => displayScheduleEntrySaved(true, scheduleEntryId));
	}
}

function deleteScheduleEntry(scheduleEntryId) {
	if (getElement("scheduleEntry" + scheduleEntryId + "HeaderSaved").children[0].className.includes("bi-file-earmark-x-fill")) {
		getElement('scheduleEntry' + scheduleEntryId).remove();
	} else {
		sendHTTPRequest('GET', 'cmd.php?id=9&cmd=delete&index=' + scheduleEntryId, true, () => getElement('scheduleEntry' + scheduleEntryId).remove());
	}
}

function prepareScheduleString(scheduleEntryId) {
	//get elements
	let enabled = document.getElementById("scheduleEntry" + scheduleEntryId + "EnabledSwitchCheck").checked;
	let cronentry = document.getElementById("cronentry" + scheduleEntryId).value;
	let command = document.getElementById("scheduleEntry" + scheduleEntryId + "CommandSelect").value;
	let commandset = document.getElementById("scheduleEntry" + scheduleEntryId + "CommandsetSelect").value;
	let parameterElement = document.getElementById("scheduleEntry" + scheduleEntryId + "ParameterInput");
	let parameter = parameterElement != null ? parameterElement.value : null;
	let startTime = document.getElementById("scheduleEntry" + scheduleEntryId + "StartTime").value;
	let endTime = document.getElementById("scheduleEntry" + scheduleEntryId + "EndTime").value;
	let startDate = document.getElementById("scheduleEntry" + scheduleEntryId + "StartDate").value;
	let endDate = document.getElementById("scheduleEntry" + scheduleEntryId + "EndDate").value;
	let startDateTime = document.getElementById("scheduleEntry" + scheduleEntryId + "ValiditySwitchCheckFrom").checked;
	let endDateTime = document.getElementById("scheduleEntry" + scheduleEntryId + "ValiditySwitchCheckTo").checked;

	let msg = "enabled=" + enabled.toString().trim() + "&";
	while (cronentry.includes("  ")) cronentry = cronentry.replaceAll("  ", " ");
	msg += "pattern=" + cronentry.trim() + "&";
	if (startDateTime) msg += "start=" + startDate + " " + startTime + "&";
	else msg += "start= &";
	if (endDateTime) msg += "end=" + endDate + " " + endTime + "&";
	else msg += "end= &";
	if (command != 0) msg += "command=" + command + "&";
	else msg += "command= &";
	if (commandset != 0) msg += "commandset=" + commandset + "&";
	else msg += "commandset= &";
	if (parameter != null) {
		parameter = parameter.replaceAll("%20", " ");
		parameter = parameter.replaceAll("\"", "\\\"");
		msg += "parameter=\"" + encodeURIComponent(parameter) + "\"&";
	}
	msg = msg.substring(0, msg.length - 1);
	
	return msg;
}

function checkCronEntryValidity(scheduleCronEntry, scheduleEntryId) {
	let acceptetChars = "0123456789,/-* "
	let validity = true;
	let tempString = scheduleCronEntry.value;
	tempString = tempString.trim();
	while (tempString.includes("  ")) tempString = tempString.replaceAll("  ", " ");
	if (tempString.split(" ").length != 5) validity = false;

	for (let i = 0; i < scheduleCronEntry.value.length; i++) {
		let hasChar = false;
		for (let chars = 0; chars < acceptetChars.length; chars++) {
			if (scheduleCronEntry.value[i] == acceptetChars[chars]) {
				hasChar = true;
			}
		}
		if (!hasChar) {
			validity = false;
		}
	}

	let saveButton = getElement("scheduleEntry" + scheduleEntryId + "SaveButton");
	if (validity) {
		saveButton.className = "disableOnDisconnect btn btn-outline-success mt-2"
		saveButton.disabled = false;
		scheduleCronEntry.className = "disableOnDisconnect form-control border border-secondary text-body"
	} else {
		saveButton.className = "btn btn-outline-success mt-2"
		saveButton.disabled = true;
		scheduleCronEntry.className = "disableOnDisconnect form-control border border-danger text-danger"
	}

	return validity;
}

function displayScheduleEntrySaved(saved, scheduleEntryId) {
	if (saved) {
		document.getElementById("scheduleEntry" + scheduleEntryId + "HeaderSaved").innerHTML = "<i class='bi bi-file-earmark-check-fill bigIcon px-2' style='color: green;'></i>";
	} else {
		document.getElementById("scheduleEntry" + scheduleEntryId + "HeaderSaved").innerHTML = "<i class='bi bi-file-earmark-x-fill bigIcon px-2' style='color: red;'></i>";
	}
}

function enabledChanged(check, scheduleEntryId) {
	if (check.checked) {
		document.getElementById("scheduleEntry" + scheduleEntryId + "HeaderEnabled").innerHTML = "<i class='bi bi-check-lg bigIcon pe-2' style='color: green;'></i>";
	} else {
		document.getElementById("scheduleEntry" + scheduleEntryId + "HeaderEnabled").innerHTML = "<i class='bi bi-x-lg bigIcon pe-2' style='color: red;'></i>";
	}
}

function executeScheduleEntry(scheduleEntryId) {
	console.log("not implemented yet");
	//sendHTTPRequest('GET', 'cmd.php?id=19&cmd=delete&commandsetid=' + getCommandsetId(commandsetEntryId), true, () => getElement("commandsetEntry" + commandsetEntryId).remove());
}

function generateCommandsetEntry(name=getLanguageAsText("new-commandset"), commands=[], commandsetId=0, saved=false) {
	let cId = commandsetEntryCount;
	if (commandsetId == 0) {
		commandsetId = Math.floor(Math.random() * 9999) + 1;
		commandsetId -= commandsetId * 2;
	}
	let newCommandsetEntryObj = document.createElement('div');
	newCommandsetEntryObj.id = "commandsetEntry" + cId;
	newCommandsetEntryObj.className = "accordion-item border border-primary";
	newCommandsetEntryObj.style.backgroundColor = "transparent";
	newCommandsetEntryObj.innerHTML = `<h2 class="accordion-header">
	<label id='commandsetEntry${cId}Label' class="accordion-button collapsed" style='cursor: pointer;' data-bs-toggle="collapse" data-bs-target="#collapseCommandset${cId}" onclick='getElement("commandsetEntry${cId}Name").setSelectionRange(0, getElement("commandsetEntry${cId}Name").value.length); getElement("commandsetEntry${cId}Name").focus();'>
		<span id='commandsetEntry${cId}Header' class='px-2' style='width: 80%;'>${name}</span>
		<span id='commandsetEntry${cId}HeaderSaved' class='px-2 text-end' style='width: 20%;'></span>
	</label>
</h2>
<div id="collapseCommandset${cId}" class="accordion-collapse collapse" data-bs-parent="#commandsetCollectionAccordion">
	<div class="accordion-body">
		<table id="commandsetEntry${cId}CommandCollection" style='width: 100%;'>
			<tr>
				<td style='width: 50%;'>
					<div class='form-floating mb-3'>
						<input id='commandsetEntry${cId}Name' type='text' class='disableOnDisconnect form-control border border-secondary' value='${name}' onkeyup='showCommandsetEntryHeader(${cId}); commandsetEntrySaved(false, ${cId});'>
						<label for='commandsetEntry${cId}Name' lang-data='description'>${getLanguageAsText("description")}</label>
					</div>
				</td>
				<td colspan="2" style='width: 50%; text-align: right;'>
					<label id='commandset${cId}Id'>${commandsetId}</label>
				</td>
			</tr>
		</table>
		<button id='commandEntry${cId}ButtonNew' class='disableOnDisconnect btn btn-outline-success mt-2' onclick='addCommandToCommandset(${cId}); commandsetEntrySaved(false, ${cId});'><i class='bi bi-plus-lg pe-2'></i><span lang-data='new-command'>${getLanguageAsText("new-command")}</span></button>
		<hr>
		<button id="commandsetEntry${cId}ButtonSave" class="disableOnDisconnect btn btn-outline-success mt-2" onclick='saveCommandsetEntry(${cId})' data-bs-toggle="collapse" data-bs-target="#collapseCommandset${cId}"><i class='bi bi-save pe-2'></i><span lang-data="save">${getLanguageAsText("save")}</span></button>
		<button id='commandsetEntry${cId}ButtonDelete' class='disableOnDisconnect btn btn-danger mt-2' onclick='deleteCommandsetEntry(${cId});' style='float: right;'><i class='bi bi-trash pe-2'></i><span lang-data='delete-commandset'>${getLanguageAsText("delete-commandset")}</span></button>
	</div>
</div>
`;

	//Adding element to document
	getElement("commandsetCollectionAccordion").appendChild(newCommandsetEntryObj);
	
	if (commandsetId < 0) getElement("commandsetEntry" + cId + "Label").click();

	commandsetEntrySaved(saved, cId);

	for (let i = 0; i < commands.length; i++) {
		addCommandToCommandset(cId, commands[i][0], commands[i][1] == undefined ? "" : commands[i][1]);
	}
	commandsetEntryCount += 1;
}

function addCommandToCommandset(commandsetEntryId, command=0, parameter="") {
	let commandId = commandEntryCounts[getCommandsetId(commandsetEntryId)];
	let newCommandEntryObj = document.createElement('tr');
	newCommandEntryObj.className = "border-top border-bottom border-primary commandrow";
	newCommandEntryObj.innerHTML = `<td class='p-1' style='width: 50%;'>
	<div class='form-floating'>
		<select id='commandsetEntry${commandsetEntryId}CommandSelect${commandId}' class='disableOnDisconnect form-select border border-secondary commandSelect' onchange='addParameterToCommandsetEntryCommand(${commandsetEntryId}, ${commandId}, value); commandsetEntrySaved(false, ${commandsetEntryId});'>
		</select>
		<label for="commandsetEntry${commandsetEntryId}CommandSelect${commandId}" lang-data="choose-command">${getLanguageAsText("choose-command")}</label>
	</div>
</td>
<td id='commandsetEntry${commandsetEntryId}Command${commandId}ParameterCell' class='p-1' style='width: 40%;'>
</td>
<td class='p-1' style='width: 10%;'>
	<button id="commandsetEntry${commandsetEntryId}CommandButtonDelete" class="disableOnDisconnect btn btn-danger" onclick='deleteCommandFromCommandset(this); commandsetEntrySaved(false, ${commandsetEntryId});' style='float: right;'><i class='bi bi-trash'></i></button>
</td>
`;
	//Adding element to document
	getElement("commandsetEntry" + commandsetEntryId + "CommandCollection").appendChild(newCommandEntryObj);

	//Adding dropdown options
	addCommandsToDropdown("commandsetEntry" + commandsetEntryId + "CommandSelect" + commandId);
	getElement("commandsetEntry" + commandsetEntryId + "CommandSelect" + commandId).value = command;

	addParameterToCommandsetEntryCommand(commandsetEntryId, commandId, command, parameter);

	commandEntryCounts[getCommandsetId(commandsetEntryId)]++;
}

function addParameterToCommandsetEntryCommand(commandsetEntryId, commandEntryId, commandId, parameter="") {
	let cell = getElement("commandsetEntry" + commandsetEntryId + "Command" + commandEntryId + "ParameterCell");
	cell.innerHTML = "";
	//add element
	let div = document.createElement("div");
	div.id = "commandsetEntry" + commandsetEntryId + "ParameterInputDiv";
	div.className = "form-floating";

	if (commandId < 0 || commandId > commandCollection.length - 1) {
		return;
	} else if (commandCollection[commandId][1] == false) {
		return;
	} else if (commandCollection[commandId][1] == "text") {
		if (parameter == undefined) parameter = "";
		div.innerHTML = `<input id='commandsetEntry${commandsetEntryId}Command${commandEntryId}ParameterInput' type='text' class='disableOnDisconnect form-control border border-secondary commandParameter' onkeyup='commandsetEntrySaved(false, ${commandsetEntryId});' value='${parameter}' lang-data='parameter'>`;
	} else if (Array.isArray(commandCollection[commandId][1])) {
		let htmlSelect = `<select id='commandsetEntry${commandsetEntryId}Command${commandEntryId}ParameterInput' onchange='commandsetEntrySaved(false, ${commandsetEntryId});' class='disableOnDisconnect form-select border border-secondary commandParameter' value='${commandCollection[commandId][1][0][1]}'>\n`;
		for (let i = 0; i < commandCollection[commandId][1].length; i++) {
			htmlSelect += `<option value='${commandCollection[commandId][1][i][0]}' lang-data='${commandCollection[commandId][1][i][1]}'>${getLanguageAsText(commandCollection[commandId][1][i][1])}</option>\n`;
		}
		htmlSelect += "</select>";
		div.innerHTML = htmlSelect;
		if (parameter == undefined) parameter = 0;
	}

	cell.appendChild(div);
	getElement("commandsetEntry" + commandsetEntryId + "Command" + commandEntryId + "ParameterInput").value = parameter;

	//add label
	let label = document.createElement("label");
	label.htmlFor = "commandsetEntry" + commandsetEntryId + "Command" + commandEntryId + "ParameterInput";
	label.setAttribute('lang-data', 'parameter');
	label.innerHTML = getLanguageAsText('parameter');
	div.appendChild(label);
}

function deleteCommandFromCommandset(commandEntry) {
	getElement(commandEntry.parentElement.parentElement.remove());
}

function deleteCommandsetEntry(commandsetEntryId) {
	if (getCommandsetId(commandsetEntryId) < 0) {// < 0 is unsaved, > 0 is saved
		getElement("commandsetEntry" + commandsetEntryId).remove();
	} else {
		sendHTTPRequest('GET', 'cmd.php?id=19&cmd=delete&commandsetid=' + getCommandsetId(commandsetEntryId), true, () => getElement("commandsetEntry" + commandsetEntryId).remove());
	}
}

function getCommandsetId(entryIndex) {
	return getElement("commandset" + entryIndex + "Id").textContent;
}

function getCommandsetName(commandsetEntryId) {
	return getElement("commandsetEntry" + commandsetEntryId + "Name").value;
}

function showCommandsetEntryHeader(commandsetEntryId) {
	getElement("commandsetEntry" + commandsetEntryId + "Header").innerText =  getElement("commandsetEntry" + commandsetEntryId + "Name").value;
}

function commandsetEntrySaved(saved, commandsetEntryId) {
	if (saved) {
		getElement("commandsetEntry" + commandsetEntryId + "HeaderSaved").innerHTML = "<i class='bi bi-file-earmark-check-fill bigIcon px-2' style='color: green;'></i>";
	} else {
		getElement("commandsetEntry" + commandsetEntryId + "HeaderSaved").innerHTML = "<i class='bi bi-file-earmark-x-fill bigIcon px-2' style='color: red;'></i>";
	}
}

function saveCommandsetEntry(commandsetEntryId) {
	let commandsetEntryNameElement = getElement("commandsetEntry" + commandsetEntryId + "Name");
	if (commandsetEntryNameElement.value == "") {
		commandsetEntryNameElement.className = "disableOnDisconnect form-control border border-danger";
		return;
	}

	let sendString = prepareCommandsetString(commandsetEntryId, commandsetEntryNameElement.value);
	if (getCommandsetId(commandsetEntryId) < 0) {//add
		let xmlhttp = new XMLHttpRequest();
		xmlhttp.onloadend = function () {
			commandsetEntrySaved(true, commandsetEntryId);
			getElement("commandset" + commandsetEntryId + "Id").textContent = xmlhttp.responseText;
		}
		xmlhttp.open('GET', 'cmd.php?id=19&cmd=add&' + sendString, true);
		xmlhttp.send();
	} else {//update
		sendHTTPRequest('GET', 'cmd.php?id=19&cmd=update&commandsetid=' + getCommandsetId(commandsetEntryId) + '&' + sendString, true, () => commandsetEntrySaved(true, commandsetEntryId));
	}
}

function prepareCommandsetString(commandsetEntryId, commandsetName) {
	let msg = "name=\"" + commandsetName + "\"&";
	let commandEntries = getElement("commandsetEntry" + commandsetEntryId + "CommandCollection").getElementsByClassName("commandrow");
	for (let i = 0; i < commandEntries.length; i++) {
		let commandSelect = commandEntries[i].getElementsByClassName("commandSelect")[0];
		msg += "command" + i + "=" + commandSelect.value + "&"
		let parameter = "";
		try {
			parameter = commandEntries[i].getElementsByClassName("commandParameter")[0].value;
			if (parameter != null) {
				parameter = parameter.replaceAll("%20", " ");
				parameter = parameter.replaceAll("\"", "\\\"");
				msg += "parameter" + i + "=\"" + encodeURIComponent(parameter) + "\"&"
			}
		} catch (error) {
			//no parameter on this command
		}
	}
	msg = msg.substring(0, msg.length - 1);
	return msg;
}

function addCommandsetsToDropdown(dropdownId, selectedId=0) {
	//Add commandsets dropdown options
	getElement(dropdownId).innerHTML = "";
	let firstoptionTag = document.createElement("option"); //---
	firstoptionTag.value = 0;
	firstoptionTag.innerText = "---";
	getElement(dropdownId).appendChild(firstoptionTag);
	let savedEntries = getSavedCommandsetEntryIds();
	for (let i = 0; i < savedEntries.length; i++) {
		let optionTag = document.createElement("option");
		optionTag.value = savedEntries[i][0];
		optionTag.innerText = savedEntries[i][1];
		getElement(dropdownId).appendChild(optionTag);
		if (selectedId == savedEntries[i][0]) {
			getElement(dropdownId).value = selectedId;
		}
	}
}

function getSavedCommandsetEntryIds() {
	let ids = [];
	let htmlItems = getElement("commandsetCollectionAccordion").getElementsByClassName("accordion-item");
	for (let i = 0; i < htmlItems.length; i++) {
		let commandsetEntryId = htmlItems[i].id.substring("commandsetEntry".length);
		if (getCommandsetId(commandsetEntryId) != 0) {
			ids.push([getElement("commandset" + commandsetEntryId + "Id").textContent, getElement("commandsetEntry" + commandsetEntryId + "Name").value]);
		}
	}
	return ids;
}

//main
window.onload = function() {
	setDarkMode(window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches);
	getDefaultLanguage();
	setDisplayProtocolSelect();
	setDisplayOrientationSelect();
	let st = null; //screenshotTime
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
			rearrangeGui();
		}
		x.open('GET', 'cmd.php?id=21', true);
		x.send();

		enableElements(true);

		rearrangeGui();
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
function changeLanguage(lang) {
	sendHTTPRequest('GET', 'cmd.php?id=13&lang=' + lang, true, () => {});//sets lang in settings.json on server
	fetchLanguage(lang);
}

function getDefaultLanguage() { //gets language from server settings.json
	var xmlhttp = new XMLHttpRequest();
	xmlhttp.onload = function() {
		let settingsJSON = JSON.parse(xmlhttp.responseText);
		currentLanguage = settingsJSON.settings.language;
	}
	xmlhttp.onloadend = function () {
		fetchLanguage(currentLanguage);
	}
	xmlhttp.open('GET', 'cmd.php?id=12', true);
	xmlhttp.send();
}

function fetchLanguage(lang) { //Sets language to server and gets language.json
	currentLanguage = lang;
	document.getElementById(lang).selected = true;
	var xmlhttp = new XMLHttpRequest();
	xmlhttp.onloadend = function() {
		languageStrings = JSON.parse(xmlhttp.responseText);
		getScheduleFromServer();
		setLanguageOnSite();
	}
	xmlhttp.open('GET', '../languages/' + currentLanguage + '.json', true);
    xmlhttp.setRequestHeader('Cache-Control', 'no-cache');
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

function sendHTTPRequest(method, url, async, loadend) {
	var xmlhttp = new XMLHttpRequest();
	xmlhttp.onloadend = loadend;
	xmlhttp.open(method, url, async);
	xmlhttp.send();
}

function getLanguageAsText(langdata) { //Replaces strings in dynamic sections
	try {
		if (languageStrings == null) {
			setLanguageOnSite();
		}
		return languageStrings[currentLanguage][langdata];	
	} catch (error) {
		console.log(error);
	}
}

window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', event => {
	setDarkMode(event.matches);
});