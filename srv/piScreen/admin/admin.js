//genereal variables
var timeoutTime = 1994;
//schedule
let commandsetCommandCount = 0;
var commandsetEntryCount = 0;
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
var scheduleObj;
//import
var scheduleToImport = null;
//trigger
var startupTriggerIndex = -1;
//modal
var modal = new bootstrap.Modal(getElement("modal"));
var modalCloseBtn = modal._element.getElementsByClassName('btn-close')[0];
var modalTitle = modal._element.getElementsByClassName('modal-title')[0];
var modalBody = modal._element.getElementsByClassName('modal-body')[0];
var modalCancelBtn = getElement("modal-cancelBtn");
var modalActionBtn = getElement("modal-actionBtn");
//modals
var cronModal = new bootstrap.Modal(getElement("cronModal"));
var commandsetModal = new bootstrap.Modal(getElement("commandsetModal"));
//tooltip
var tooltipTriggerList;
var tooltipList;
//language
var currentLanguage = null;
var languageStrings = null;
var prevItemsEnabled = null;
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
	getElement("active").classList = "badge rounded-pill bg-danger";
	getElement("active").innerHTML = getLanguageAsText('offline');

	getElement("displayState").classList = "badge rounded-pill bg-secondary";
	getElement("displayState").innerHTML = getLanguageAsText('unknown');

	getElement("displayOnButton").hidden = false;
	getElement("displayStandbyButton").hidden = false;
	getElement("spinnerDisplayOn").hidden = true;
	getElement("spinnerDisplayStandby").hidden = true;

	getElement("uptime").innerHTML = "???";
	getElement("cpuLoad").innerHTML = "???";
	getElement("cpuTemp").innerHTML = "???";
	getElement("ramUsed").innerHTML = "???";
	getElement("ramTotal").innerHTML = "???";
	getElement("ramUsage").innerHTML = "???";
}

function connectionStatusChanged(status) {
	return prevItemsEnabled != status;
}

function enableElements(enable) {
	let disable = !enable;
	let elementsToDisable = document.getElementsByClassName("disableOnDisconnect");
	for (let i = 0; i < elementsToDisable.length; i++) {
		elementsToDisable[i].disabled = disable;
	}
	prevItemsEnabled = enable;
}

function getElement(id) {
	return document.getElementById(id);
}

function commandsetExists(commandsetId) {
	return undefined != getCommandsetName(commandsetId);
}

function generateNewScheduleEntry(scheduleEntryId=-1, scheduleEntryObject) {//enabled=true, pattern="* * * * *", start="", end="", command=0, commandset=0, parameter="") {
	if (scheduleEntryObject.command == undefined) scheduleEntryObject.command = 0;
	if (scheduleEntryObject.parameter == undefined) scheduleEntryObject.parameter = "";
	if (scheduleEntryObject.commandset == undefined) scheduleEntryObject.commandset = 0;
	
	if (scheduleEntryObject.command < 0 || scheduleEntryObject.command > commandCollection.length - 1) {
		console.error("Command " + scheduleEntryObject.command + " not known! CronID: " + scheduleEntryId);
		scheduleEntryObject.command = 0;
	} else if (commandCollection[scheduleEntryObject.command][0] == "") {
		scheduleEntryObject.command = 0;
	}
	
	let start, end;
	if (scheduleEntryObject.start == undefined) start = "";
	else {
		let startDateTime = new Date(scheduleEntryObject.start);
		start = "<td>" + addLeadingZero(startDateTime.getHours()) + ":" + addLeadingZero(startDateTime.getMinutes()) + " Uhr " + addLeadingZero(startDateTime.getDay()) + "." + addLeadingZero(startDateTime.getMonth() + 1) + "." + addLeadingZero(startDateTime.getFullYear()) + "</td>";
	}
	if (scheduleEntryObject.end == undefined) end = "";
	else {
		let endDateTime = new Date(scheduleEntryObject.end);
		end = "<td>" + addLeadingZero(endDateTime.getHours()) + ":" + addLeadingZero(endDateTime.getMinutes()) + " Uhr " + addLeadingZero(endDateTime.getDay()) + "." + addLeadingZero(endDateTime.getMonth() + 1) + "." + addLeadingZero(endDateTime.getFullYear()) + "</td>";
	}

	let newScheduleEntryObj = document.createElement('div');
	newScheduleEntryObj.id = "scheduleEntry" + scheduleEntryId;
	newScheduleEntryObj.className = "disableOnDisconnect scheduleEntryListItem list-group-item list-group-item-action border border-primary p-3";
	newScheduleEntryObj.style.backgroundColor = "transparent";
	newScheduleEntryObj.onclick = () => {showCronModal(scheduleEntryId);};
	newScheduleEntryObj.style.cursor = "pointer";
	newScheduleEntryObj.innerHTML = `<div class="d-flex w-100 justify-content-between">
	<p><i class='bi bi-asterisk bigIcon pe-2'></i><span lang-data="cron-entry">${getLanguageAsText("cron-entry")}</span>: ${scheduleEntryObject.pattern}</p>
	<p><span lang-data="active">${getLanguageAsText("active")}</span>: ${scheduleEntryObject.enabled ? "<i class='bi bi-check-lg bigIcon pe-2' style='color: green;'></i>" : "<i class='bi bi-x-lg bigIcon pe-2' style='color: red;'></i>"}</p>
</div>
<i class='bi bi-terminal bigIcon pe-2'></i><span lang-data="command">${getLanguageAsText("command")}</span>: ${getLanguageAsText(commandCollection[scheduleEntryObject.command][0])}<br>
<i class='bi bi-node-plus bigIcon pe-2'></i><span lang-data="parameter">${getLanguageAsText("parameter")}</span>: ${scheduleEntryObject.parameter.length > 50 ? scheduleEntryObject.parameter.substring(0, 40) + "..." : scheduleEntryObject.parameter}<br><br>
<i class='bi bi-file-ruled bigIcon pe-2'></i><span lang-data="commandset">${getLanguageAsText("commandset")}</span>: ${commandsetExists(scheduleEntryObject.commandset) ? getCommandsetName(scheduleEntryObject.commandset) : "---"}<br><br>
<table style='width: 100%;'>
	<tr>
		${scheduleEntryObject.start == undefined ? "" : "<td style='width: 50%;'><i class='bi bi-stopwatch bigIcon pe-2'></i><span lang-data='valid-from'>" + getLanguageAsText('valid-from') + "</span>: </td>"}
		${scheduleEntryObject.end == undefined ? "" : "<td style='width: 50%;'><i class='bi bi-stopwatch bigIcon pe-2'></i><span lang-data='valid-from'>" + getLanguageAsText('valid-to') + "</span>: </td>"}
	</tr>
	<tr>
		${start}
		${end}
	</tr>
</table>`;

	getElement("scheduleEntryCollectionList").appendChild(newScheduleEntryObj);
	if (scheduleEntryId < 0) getElement("scheduleEntry" + scheduleEntryId).click();

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

function addParameterToScheduleEntry(commandId, parameter) {
	let cell = getElement("scheduleEntryParameterCell");
	cell.innerHTML = "";
	//add element
	let div = document.createElement("div");
	div.id = "scheduleEntryParameterInputDiv";
	div.className = "form-floating";

	if (commandCollection[commandId][1] == false) {
		return;
	} else if (commandCollection[commandId][1] == "text") {
		div.innerHTML = `<input id='scheduleEntryParameterInput' type='text' class='disableOnDisconnect form-control border border-secondary' value='${parameter}' lang-data='parameter'>`;
		if (parameter == undefined) parameter = "";
	} else if (Array.isArray(commandCollection[commandId][1])) {
		let htmlSelect = `<select id='scheduleEntryParameterInput' class='disableOnDisconnect form-select border border-secondary'>\n`;
		for (let i = 0; i < commandCollection[commandId][1].length; i++) {
			htmlSelect += `<option value='${commandCollection[commandId][1][i][0]}' lang-data='${commandCollection[commandId][1][i][1]}'>${getLanguageAsText(commandCollection[commandId][1][i][1])}</option>\n`;
		}
		htmlSelect += "</select>";
		div.innerHTML = htmlSelect;
		if (parameter == undefined) parameter = 0;
	}

	cell.appendChild(div);
	getElement("scheduleEntryParameterInput").value = parameter;

	//add label
	let label = document.createElement("label");
	label.htmlFor = "scheduleEntryParameterInput";
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
	let requestedUrl = "cmd.php?id=10";
	let xmlhttp = new XMLHttpRequest();
	xmlhttp.timeout = timeoutTime;
	xmlhttp.ontimeout = () => {showServerError("Timeout error", requestedUrl);};
	xmlhttp.onloadend = () => {
		if (!serverExecutedSuccessfully(xmlhttp.responseText)) {
			console.log(xmlhttp.responseText);
			showServerError("Server error while requesting time schedule", requestedUrl);
			return;
		}
		loadScheduleJson(parseReturnValuesFromServer(xmlhttp.responseText)[0]);
	}
	xmlhttp.open('GET', requestedUrl, true);
	xmlhttp.send();
}

function loadScheduleJson(jsonString) {
	try {
		scheduleObj = JSON.parse(jsonString);
	} catch (error) {
		showServerError("Failed to load time schedule", "schedule.json", error);
		return;
	}
	getElement("commandsetCollectionList").innerHTML = "";
	for (let i = 0; i < scheduleObj.commandsets.length; i++) {//commandsets
		let commandsetCommandsArray = [];
		let commandsetObj = scheduleObj.commandsets[i];
		for (let j = 0; j < commandsetObj.commands.length; j++) {//commands
			commandsetCommandsArray.push([commandsetObj.commands[j].command, commandsetObj.commands[j].parameter]);
		}
		generateCommandsetEntry(commandsetObj.name, commandsetCommandsArray, commandsetObj.id, true);
	}
	
	getElement("scheduleEntryCollectionList").innerHTML = "";
	for (let i = 0; i < scheduleObj.cron.length; i++) {//crons
		let cronObj = scheduleObj.cron[i];
		generateNewScheduleEntry(i, cronObj);
	}

	addCommandsToDropdown("trigger0CommandSelect");//trigger
	addCommandsetsToDropdown("trigger0CommandsetSelect");//trigger
	for (let i = 0; i < scheduleObj.trigger.length; i++) {//trigger parameter
		let triggerObj = scheduleObj.trigger[i];
		if (triggerObj.trigger == 1) {
			startupTriggerIndex = i;
			if (triggerObj.enabled != undefined) getElement("trigger0EnabledSwitch").checked = triggerObj.enabled;
			else getElement("trigger0EnabledSwitch").checked = false;
			
			if (triggerObj.cases.true.command != undefined) {
				getElement("trigger0CommandSelect").value = triggerObj.cases.true.command;
				addParameterToTrigger(0, triggerObj.cases.true.command, triggerObj.cases.true.parameter);
			} else getElement("trigger0CommandSelect").value = 0;

			if (triggerObj.cases.true.commandset != undefined) {
				getElement("trigger0CommandsetSelect").value = triggerObj.cases.true.commandset;
			} else getElement("trigger0CommandsetSelect").value = 0;
			break;
		}
	}
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
			case 1: modalActionBtn.className = "btn btn-primary"; break;
			case 2: modalActionBtn.className = "btn btn-secondary"; break;
			case 3: modalActionBtn.className = "btn btn-success"; break;
			case 4: modalActionBtn.className = "btn btn-danger"; break;
			case 5: modalActionBtn.className = "btn btn-warning"; break;
			case 6: modalActionBtn.className = "btn btn-info"; break;
			case 7: modalActionBtn.className = "btn btn-light"; break;
			case 8: modalActionBtn.className = "btn btn-dark"; break;
		}
		modalActionBtn.onclick = actionFunction;
	} else {
		modalActionBtn.hidden = true;
	}
	modal.show();
}

function showCronModal(scheduleEntryId) {
	//default new entry
	let obj = {
		"enabled": true,
		"pattern": "* * * * *"
	};
	if (scheduleObj.cron[scheduleEntryId] != undefined) { // load already existing schedule entry
		obj = scheduleObj.cron[scheduleEntryId];
	}
	let enabled = obj.enabled;
	let pattern = obj.pattern;
	let command = obj.command == undefined ? 0 : obj.command;
	let commandset = obj.commandset == undefined ? 0 : obj.commandset;
	let parameter = obj.parameter;
	let start = obj.start;
	let end = obj.end;
	let startDate = "";
	if (obj.start) {
		startDate = start.split(" ")[0];
	}
	let startTime = "";
	if (obj.start) {
		startTime = start.split(" ")[1];
	}
	let endDate = "";
	if (obj.end) {
		endDate = end.split(" ")[0];
	}
	let endTime = "";
	if (obj.end) {
		endTime = end.split(" ")[1];
	}

	getElement("cronModalTitle").innerHTML = `<span lang-data="cron-entry">${getLanguageAsText("cron-entry")}</span>: <span id='currentScheduleEntryId'>${scheduleEntryId}</span>`;
	getElement("cronModalBody").innerHTML = `<table class="table-sm" style='width: 100%;'>
	<div id='scheduleEntry'>
		<tr>
			<td style='width: 50%;'>
				<div class="form-check form-switch">
					<input class="disableOnDisconnect form-check-input" type="checkbox" role="switch" id="scheduleEntryEnabledSwitchCheck" ${enabled ? "checked" : ""}>
					<label class="form-check-label" for="scheduleEntryEnabledSwitchCheck" lang-data="active">${getLanguageAsText("active")}</label>
				</div>
			</td>
			<td style='width: 50%;'>
				<button id="scheduleEntryButtonExecute" class="disableOnDisconnect btn btn-outline-warning mt-2" onclick='executeCurrentScheduleEntry(${scheduleEntryId});' style='float: right;'><i class='bi bi-play pe-2'></i><span id='scheduleEntryButtonExecuteSpinner' class='spinner-border spinner-border-sm' role='status' hidden='true'></span><span lang-data="execute">${getLanguageAsText("execute")}</span></button>
			</td>
		</tr>
		<tr>
			<td>
				<div class='form-floating'>
					<input type='text' class='disableOnDisconnect form-control border border-secondary' name='cronentry' id='cronentry' value='${pattern}' onkeyup='checkCronEntryValidity(this);'>
					<label for='cronentry' lang-data="cron-entry">${getLanguageAsText("cron-entry")}</label>
				</div>
			</td>
			<td>
				<i class='bi-question-octagon p-2' style='cursor: pointer;' id='cronEntryHelp' data-bs-toggle="tooltip" data-bs-placement="top" data-bs-title="${getLanguageAsText('help')}" onclick='showModal(getLanguageAsText("help"), getLanguageAsText("cronHelpText"), false, true, getLanguageAsText("ok"));'></i>
			</td>
		</tr>
		<tr>
			<td>
				<div class='form-floating'>
					<select id='scheduleEntryCommandSelect' class='disableOnDisconnect form-select border border-secondary' onchange='addParameterToScheduleEntry(value);'>
					</select>
					<label for="scheduleEntryCommandSelect" lang-data="choose-command">${getLanguageAsText("choose-command")}</label>
				</div>
			</td>
			<td id="scheduleEntryParameterCell">
			</td>
		</tr>
		<tr>
			<td colspan="2">
				<div class='form-floating'>
					<select id='scheduleEntryCommandsetSelect' class='disableOnDisconnect commandsetDropdown form-select border border-secondary' value='${commandset}'>
					</select>
					<label for="scheduleEntryCommandsetSelect" lang-data="choose-commandset">${getLanguageAsText("choose-commandset")}</label>
				</div>
			</td>
		</tr>
		<tr>
			<td colspan='3' class='p-0'>
				<table class='p-0' style="width: 100%;">
					<tr>
						<td colspan='2' class='p-2'>
							<div class="form-check form-switch">
								<input class="disableOnDisconnect form-check-input" type="checkbox" role="switch" id="scheduleEntryValiditySwitchCheckFrom" onchange='toggleValidityFrom(checked);' ${start != undefined ? "checked" : ""}>
								<label class="form-check-label" for="scheduleEntryValiditySwitchCheckFrom" lang-data="valid-from">${getLanguageAsText("valid-from")}</label>
							</div>
						</td>
						<td colspan='2' class='p-2'>
							<div class="form-check form-switch">
								<input class="disableOnDisconnect form-check-input" type="checkbox" role="switch" id="scheduleEntryValiditySwitchCheckTo" onchange='toggleValidityTo(checked);' ${end != undefined ? "checked" : ""}>
								<label class="form-check-label" for="scheduleEntryValiditySwitchCheckTo" lang-data="valid-to">${getLanguageAsText("valid-to")}</label>
							</div>
						</td>
					</tr>
					<tr>
						<td id='scheduleEntryValidityTimeSpanFrom1' class='px-2' lang-data='from'>
						${getLanguageAsText("from")}
						</td>
						<td id='scheduleEntryValidityTimeSpanFrom2'>
							<div class='input-group'>
								<input id='scheduleEntryStartTime' name='scheduleEntryStartDateTime' type="time" class="disableOnDisconnect form-control border border-secondary p-1" style="text-align: center; width: 40%;" value="${startTime}">
								<input id='scheduleEntryStartDate' type="date" class="disableOnDisconnect form-control border border-secondary p-1" style="text-align: center; width: 60%;" value="${startDate}">
							</div>
						</td>
						<td id='scheduleEntryValidityTimeSpanTo1' class='px-2' lang-data='to'>
						${getLanguageAsText("to")}
						</td>
						<td id='scheduleEntryValidityTimeSpanTo2'>
							<div class='input-group'>
								<input id='scheduleEntryEndTime' name='scheduleEntryEndDateTime' type="time" class="disableOnDisconnect form-control border border-secondary p-1" style="text-align: center; width: 40%;" value="${endTime}">
								<input id='scheduleEntryEndDate' type="date" class="disableOnDisconnect form-control border border-secondary p-1" style="text-align: center; width: 60%;" value="${endDate}">
							</div>
						</td>
					</tr>
				</table>
			</td>
		</tr>
	</div>
</table>`;
	
	addCommandsetsToDropdown("scheduleEntryCommandsetSelect", commandset);

	toggleValidityFrom(getElement("scheduleEntryValiditySwitchCheckFrom").checked);
	toggleValidityTo(getElement("scheduleEntryValiditySwitchCheckTo").checked);

	addCommandsToDropdown("scheduleEntryCommandSelect");
	getElement("scheduleEntryCommandSelect").value = command;
	addParameterToScheduleEntry(command, parameter);	

	getElement("scheduleEntryButtonSave").onclick = () => saveScheduleEntry(scheduleEntryId);
	getElement("scheduleEntryButtonDelete").onclick = () => deleteScheduleEntry(scheduleEntryId);
	cronModal.show();
	enableElements(prevItemsEnabled);
}

function isInDarkmode() {
	return !getElement("theme").href.includes("/bootstrap/css/bootstrap.min.css");
}

function toggleDarkmode() {
	setDarkMode(!isInDarkmode());
}

function setDarkMode(dark) {
	let darkmodeButton = getElement("darkmodeButton");
	let theme = getElement("theme");
	let languageSelect = getElement("languageSelect");
	let scheduleEntryButtonCancel = getElement("scheduleEntryButtonCancel");
	let commandsetEntryButtonCancel = getElement("commandsetEntryButtonCancel");
		if (dark) {
		theme.href = "/bootstrap/darkpan-1.0.0/css/bootstrap.min.css";
		darkmodeButton.classList.replace("btn-outline-secondary", "btn-outline-light");
		languageSelect.classList.replace("border-secondary", "border-light");
		scheduleEntryButtonCancel.classList.replace("btn-outline-dark", "btn-outline-light");
		commandsetEntryButtonCancel.classList.replace("btn-outline-dark", "btn-outline-light");
		for (let i = 0; i < document.getElementsByClassName("btn-close-dark").length; i++) {
			document.getElementsByClassName("btn-close-dark")[i].classList.replace("btn-close-dark", "btn-close-white");
		}
	} else {
		theme.href = "/bootstrap/css/bootstrap.min.css";
		darkmodeButton.classList.replace("btn-outline-light", "btn-outline-secondary");
		languageSelect.classList.replace("border-light", "border-secondary");
		scheduleEntryButtonCancel.classList.replace("btn-outline-light", "btn-outline-dark");
		commandsetEntryButtonCancel.classList.replace("btn-outline-light", "btn-outline-dark");
		for (let i = 0; i < document.getElementsByClassName("btn-close-white").length; i++) {
			document.getElementsByClassName("btn-close-white")[i].classList.replace("btn-close-white", "btn-close-dark");
		}
	}
}

function checkForUpdate() {
	let requestedUrl = "cmd.php?id=6";
	let xmlhttp = new XMLHttpRequest();
	xmlhttp.timeout = timeoutTime;
	xmlhttp.ontimeout = () => {showServerError("Timeout error", requestedUrl);};
	xmlhttp.onload = () => {
		if (!serverExecutedSuccessfully(xmlhttp.responseText)) {
			console.log(xmlhttp.responseText);
			showServerError("Error while requesting if update is available", requestedUrl);
			return;
		}
		if (parseReturnValuesFromServer(xmlhttp.responseText)[0] != "") {
			let nextVersion = parseReturnValuesFromServer(xmlhttp.responseText);
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
			getElement('info-footer').appendChild(updateButton);
		}
	}
	xmlhttp.open('GET', requestedUrl, true);
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
	let requestedUrl = "cmd.php?id=18";
	let xmlhttp = new XMLHttpRequest();
	xmlhttp.timeout = timeoutTime;
	xmlhttp.ontimeout = () => {showServerError("Timeout error", requestedUrl);};
	xmlhttp.onloadend = () => {
		console.log(xmlhttp.responseText);
		if (!serverExecutedSuccessfully(xmlhttp.responseText)) {
			showServerError("Error while importing time schedule", requestedUrl);
			return;
		}
	}
	xmlhttp.open('POST', requestedUrl, true);
	xmlhttp.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
	xmlhttp.send(jsonString);
}

//click events
function reloadBrowser() {
	getElement("restartBrowserSpinner").hidden = false;
	sendHTTPRequest('GET', 'cmd.php?id=1', true, () => {getElement("restartBrowserSpinner").hidden = true;});
}

function restartHost() {
	showModal(getLanguageAsText('attention'), getLanguageAsText('reboot-really'), undefined, undefined, undefined, 4, getLanguageAsText('restart-device'), () => {sendHTTPRequest('GET', 'cmd.php?id=2', false, () => {}); modal.hide();});
}

function shutdownHost() {
	showModal(getLanguageAsText('attention'), getLanguageAsText('shutdown-really'), undefined, undefined, undefined, 4, getLanguageAsText('shutdown-device'), () => {sendHTTPRequest('GET', 'cmd.php?id=3', false, () => {}); modal.hide();});
}

function setDisplayOn() {
	sendHTTPRequest('GET', 'cmd.php?id=8&cmd=1', true, () => {spinnerDisplayOn.hidden = false;});
}

function setDisplayStandby() {
	sendHTTPRequest('GET', 'cmd.php?id=8&cmd=0', true, () => {spinnerDisplayStandby.hidden = false;});
}

function showPiscreenInfo() {
	let requestedUrl = "cmd.php?id=11";
	let xmlhttp = new XMLHttpRequest();
	xmlhttp.timeout = timeoutTime;
	xmlhttp.ontimeout = () => {showServerError("Timeout error", requestedUrl);};
	xmlhttp.onload = () => {
		if (!serverExecutedSuccessfully(xmlhttp.responseText)) {
			showServerError("Error while getting display protocol");
			return;
		}
		try {
			let jsonData = JSON.parse(parseReturnValuesFromServer(xmlhttp.responseText));
			showModal(getLanguageAsText('about-info'), getLanguageAsText('info-text') + ' ' + jsonData.version.major + '.' + jsonData.version.minor + '.' + jsonData.version.patch, false, true, getLanguageAsText('alright'));
		} catch (error) {
			showServerError("Failed to load piScreen info", "manifest.json", error);
		}
	}
	xmlhttp.open('GET', requestedUrl, true);
	xmlhttp.send();
}

function rearrangeGui() {
	new Masonry(getElement("masonry"));
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
//slide.bs.carousel
getElement("timeActionsCarousel").addEventListener("slide.bs.carousel", event => {
	plannerSwitchRadio(event.to);
});

function showServerError(text, request, details=null) {
	if (details == null || details == undefined) {
		details = "";
	} else {
		details = `<br><br><a data-bs-toggle="collapse" href="#collapseDetails" role="button">
Details
</a>
<div class="collapse" id="collapseDetails">
	<div class="card card-body">
		${details}
	</div>
</div>`
	}
	showModal(getLanguageAsText("error"), text + "<br><br><code>" + request + "</code>" + details, true, true, getLanguageAsText("ok"), 4, "Reload adminsite", () => location.reload());
}

function serverExecutedSuccessfully(received) {//returns false if error occurs
	let returncode = received.split(":-:")[1];
	return (returncode == 0);
}

function parseReturnValuesFromServer(received) {
	let returnvals = received.split(":-:")[0].split(":;:");
	for (let i = 0; i < returnvals.length; i++) returnvals[i] = returnvals[i].trim(); // removes whitespace from every output line
	return returnvals;
}

function setDisplayProtocol() {
	let protocol = getElement('displayProtocolSelect').value;
	sendHTTPRequest('GET', 'cmd.php?id=14&protocol=' + protocol, true, () => settingSaved("settingsButtonSaveDisplayProtocol", true));
}

function setDisplayProtocolSelect() {
	let requestedUrl = "cmd.php?id=15";
	let xmlhttp = new XMLHttpRequest();
	xmlhttp.timeout = timeoutTime;
	xmlhttp.ontimeout = () => {showServerError("Timeout error", requestedUrl);};
	xmlhttp.onloadend = function() {
		if (!serverExecutedSuccessfully(xmlhttp.responseText)) {
			showServerError("Error while getting display protocol", requestedUrl);
			return;
		}
		getElement("displayProtocolSelect").value = parseReturnValuesFromServer(xmlhttp.responseText)[0];
	}
	xmlhttp.open('GET', requestedUrl, true);
	xmlhttp.send();
}

function setDisplayOrientation() {
	// 0 - horizontal, 1 - vertical, 2 - horizontal inverted, 3 - vertical inverted
	let orientation = getElement('displayOrientationSelect').value;
	sendHTTPRequest('GET', 'cmd.php?id=16&orientation=' + orientation, true, () => settingSaved("settingsButtonSaveDisplayOrientation", true));
}

function setDisplayOrientationSelect() {
	let requestedUrl = "cmd.php?id=17";
	let xmlhttp = new XMLHttpRequest();
	xmlhttp.timeout = timeoutTime;
	xmlhttp.ontimeout = () => {showServerError("Timeout error", requestedUrl);};
	xmlhttp.onloadend = function() {
		if (!serverExecutedSuccessfully(xmlhttp.responseText)) {
			console.log(xmlhttp.responseText);
			showServerError("Error while setting display orientation select", requestedUrl);
			return;
		}
		getElement("displayOrientationSelect").value = parseReturnValuesFromServer(xmlhttp.responseText)[0];
	}
	xmlhttp.open('GET', requestedUrl, true);
	xmlhttp.send();
}

function setHostname(elementId) {
	let requestedUrl = "cmd.php?id=4";
	let hostname = getElement(elementId).value;
	let xmlhttp = new XMLHttpRequest();
	xmlhttp.timeout = timeoutTime;
	xmlhttp.ontimeout = () => {showServerError("Timeout error", requestedUrl);};
	xmlhttp.onloadend = () => {
		if (serverExecutedSuccessfully(xmlhttp.responseText)) {
			settingSaved("settingsButtonSaveHostname", true);
		} else {
			showServerError("An error occured on the server while setting hostname.", requestedUrl);
			return;
		}
	};
	xmlhttp.open('POST', requestedUrl, true);
	xmlhttp.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
	xmlhttp.send("hostname=" + hostname);
}

function setWebLoginAndPassword() {
	let requestedUrl = "cmd.php?id=7";
	let xmlhttp = new XMLHttpRequest();
	xmlhttp.timeout = timeoutTime;
	xmlhttp.ontimeout = () => {showServerError("Timeout error", requestedUrl);};
	xmlhttp.onloadend = () => {
		if (serverExecutedSuccessfully(xmlhttp.responseText)) {
			showModal(getLanguageAsText("success"), "Updated weblogin successfully", true, true, getLanguageAsText("ok"));
			location.reload();
		} else {
			showServerError("An error occured on the server while setting weblogin user and password.", requestedUrl);
		}
	};
	xmlhttp.open('POST', requestedUrl, true);
	xmlhttp.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
	xmlhttp.send("user=" + getElement("webUserInput").value + "&pwd=" + getElement("webPasswordInput").value);
}

function settingSaved(elementId, saved) {
	let element = getElement(elementId);
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
		executeButtonElement.className = "disableOnDisconnect btn btn-outline-warning mt-2";
		executeButtonElement.disabled = false;
	} else {
		saveButtonElement.className = "disableOnDisconnect btn btn-outline-success mt-2";
		saveButtonElement.innerHTML = "<i class='bi bi-save pe-2'></i><span lang-data='save'>" + getLanguageAsText("save") + "</span>";
		executeButtonElement.className = "btn btn-outline-warning mt-2";
		executeButtonElement.disabled = true;
	}
}

function executeStartupTrigger() {
	getElement("executeStartupTriggerSpinner").hidden = false;
	sendHTTPRequest('GET', 'cmd.php?id=23', true, () => getElement("executeStartupTriggerSpinner").hidden = true);
}

function executeLastCron() {
	getElement("executeLastCronSpinner").hidden = false;
	sendHTTPRequest('GET', 'cmd.php?id=22', true, () => getElement("executeLastCronSpinner").hidden = true);
}

function showScheduleEntryHeader(scheduleEntryId) {
	let commandSelect = getElement("scheduleEntry" + scheduleEntryId + "CommandSelect");
	getElement("scheduleEntry" + scheduleEntryId + "HeaderCommand").innerText = commandSelect.options[commandSelect.selectedIndex].text;
	getElement("scheduleEntry" + scheduleEntryId + "HeaderCommand").setAttribute("lang-data", commandCollection[commandSelect.value][0]);
	let commandsetSelect = getElement("scheduleEntry" + scheduleEntryId + "CommandsetSelect");
	getElement("scheduleEntry" + scheduleEntryId + "HeaderCommandset").innerText = commandsetSelect.options[commandsetSelect.selectedIndex].text;
	getElement("scheduleEntry" + scheduleEntryId + "HeaderCron").innerText = getElement("cronentry" + scheduleEntryId).value;
}

function toggleValidityFrom(checked){
	let scheduleEntry1 = getElement('scheduleEntryValidityTimeSpanFrom1');
	let scheduleEntry2 = getElement('scheduleEntryValidityTimeSpanFrom2');
	if (checked) {
		scheduleEntry1.style.visibility = "";
		scheduleEntry2.style.visibility = "";
	} else {
		scheduleEntry1.style.visibility = "hidden";
		scheduleEntry2.style.visibility = "hidden";
	}
}

function toggleValidityTo(checked){
	let scheduleEntry1 = getElement('scheduleEntryValidityTimeSpanTo1');
	let scheduleEntry2 = getElement('scheduleEntryValidityTimeSpanTo2');
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
			sendHTTPRequest('GET', 'cmd.php?id=20&cmd=delete&index=' + startupTriggerIndex, true, () => {triggerSaved(true, 0);});
			startupTriggerIndex--;
			return;
		}
		sendHTTPRequest('GET', 'cmd.php?id=20&cmd=update&index=' + startupTriggerIndex + '&' + prepareTriggerString(triggerId), true, () => {triggerSaved(true, 0);});
		return;
	}
	sendHTTPRequest('GET', 'cmd.php?id=20&cmd=add&' + prepareTriggerString(triggerId), true, () => {triggerSaved(true, 0);});
	startupTriggerIndex++;
}

function prepareTriggerString(triggerId, triggerCase=["true"]) {
	let enabled = getElement("trigger" + triggerId + "EnabledSwitch").checked;
	let command = getElement("trigger" + triggerId + "CommandSelect").value;
	let commandset = getElement("trigger" + triggerId + "CommandsetSelect").value;
	let parameter = "";

	let msg = "enabled=" + enabled.toString().trim() + "&";

	for (let i = 0; i < triggerCase.length; i++) {
		if (command != 0) msg += "command=" + triggerCase[i] + " " + command + "&";
		else msg += "command=" + triggerCase[i] + " &";
		if (getElement("trigger" + triggerId + "ParameterInput") != null) {
			let parameterElement = getElement("trigger" + triggerId + "ParameterInput");
			parameter = parameterElement.value;
			parameter = parameter.replaceAll("%20", " ");
			parameter = parameter.replaceAll("\"", "\\\"");
			msg += "parameter=" + triggerCase[i] + " \"" + encodeURIComponent(parameter) + "\"&";
		} else msg += "parameter=" + triggerCase[i] + " &";
		if (commandset != 0) msg += "commandset=" + triggerCase[i] + " " + commandset + "&";
		else msg += "commandset=" + triggerCase[i] + " &";
	}

	if (triggerId == 0) msg += "trigger=1&";
	msg = msg.substring(0, msg.length - 1);

	return msg;
}

function saveScheduleEntry() {
	//send to server
	if (getElement("currentScheduleEntryId").innerText < 0) {//add
		sendHTTPRequest('GET', 'cmd.php?id=9&cmd=add&' + prepareScheduleString(), true, () => {cronModal.hide(); getScheduleFromServer();});
	} else {//update
		sendHTTPRequest('GET', 'cmd.php?id=9&cmd=update&' + prepareScheduleString() + '&index=' + getElement("currentScheduleEntryId").innerText, true, () => {cronModal.hide(); getScheduleFromServer();});
	}
}

function deleteScheduleEntry() {
	if (getElement("currentScheduleEntryId").innerText >= 0) {
		sendHTTPRequest('GET', 'cmd.php?id=9&cmd=delete&index=' + getElement("currentScheduleEntryId").innerText, true, () => {cronModal.hide(); getScheduleFromServer();});
	} else {
		cronModal.hide();
	}
}

function prepareScheduleString() {
	//get elements
	let enabled = getElement("scheduleEntryEnabledSwitchCheck").checked;
	let cronentry = getElement("cronentry").value;
	let command = getElement("scheduleEntryCommandSelect").value;
	let commandset = getElement("scheduleEntryCommandsetSelect").value;
	let parameterElement = getElement("scheduleEntryParameterInput");
	let parameter = parameterElement != null ? parameterElement.value : null;
	let startTime = getElement("scheduleEntryStartTime").value;
	let endTime = getElement("scheduleEntryEndTime").value;
	let startDate = getElement("scheduleEntryStartDate").value;
	let endDate = getElement("scheduleEntryEndDate").value;
	let startDateTime = getElement("scheduleEntryValiditySwitchCheckFrom").checked;
	let endDateTime = getElement("scheduleEntryValiditySwitchCheckTo").checked;

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

function checkCronEntryValidity(scheduleCronEntry) {
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

	let saveButton = getElement("scheduleEntryButtonSave");
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

function executeCurrentScheduleEntry() {
	getElement("scheduleEntryButtonExecuteSpinner").hidden = false;
	sendHTTPRequest('GET', 'cmd.php?id=9&cmd=execute&index=' + getElement("currentScheduleEntryId").innerText, true, () => getElement("scheduleEntryButtonExecuteSpinner").hidden = true);
}

function executeCommandsetEntry(commandsetEntryId) {
	getElement("commandsetEntry" + commandsetEntryId + "ButtonExecuteSpinner").hidden = false;
	sendHTTPRequest('GET', 'cmd.php?id=19&cmd=execute&commandsetid=' + getCommandsetId(commandsetEntryId), true, () => getElement("commandsetEntry" + commandsetEntryId + "ButtonExecuteSpinner").hidden = true);
}

function generateCommandsetEntry(name=getLanguageAsText("new-commandset"), commands=[], commandsetId=0, saved=false) {
	let cId = commandsetEntryCount;
	let newCommandsetEntryObj = document.createElement('div');
	newCommandsetEntryObj.id = "commandsetEntry" + cId;
	newCommandsetEntryObj.className = "disableOnDisconnect list-group-item list-group-item-action border border-primary p-3";
	newCommandsetEntryObj.onclick = () => {showCommandsetModal(commandsetId);};
	newCommandsetEntryObj.style.backgroundColor = "transparent";
	newCommandsetEntryObj.style.cursor = "pointer";
	newCommandsetEntryObj.innerHTML = `<div class="d-flex w-100 justify-content-between">
	<p class='m-2'><i class='bi bi-terminal bigIcon pe-2'></i>${name}</p>
	<p id='commandset${cId}Id' class='m-2'>${commandsetId}</p>
</div>`;
	//Adding element to document
	getElement("commandsetCollectionList").appendChild(newCommandsetEntryObj);
	
	commandsetEntryCount += 1;
}

function showCommandsetModal(commandsetId=0) {
	if (commandsetId == 0) {
		commandsetId = Math.floor(Math.random() * 9999) + 1;
		commandsetId -= commandsetId * 2;
	}
	//default new entry
	let obj = {
		"id": commandsetId,
		"name": getLanguageAsText("new-commandset"),
		"commands": []
	};
	for (let i = 0; i < scheduleObj.commandsets.length; i++) {
		if (scheduleObj.commandsets[i].id == commandsetId) { // load already existing schedule entry
			obj = scheduleObj.commandsets[i];
		}
	}
	commandsetCommandCount = 0;
	getElement("commandsetModalTitle").innerHTML = `<span lang-data="commandset">${getLanguageAsText("commandset")}</span>: <span id='currentScheduleEntryId'>${obj.name}</span>`;
	getElement("commandsetModalBody").innerHTML = `<table id="commandsetEntry${commandsetId}CommandCollection" style='width: 100%;'>
		<tr>
			<td style='width: 50%;'>
				<div class='form-floating mb-3'>
					<input id='commandsetEntryName' type='text' class='disableOnDisconnect form-control border border-secondary' value='${obj.name}' onkeyup='showCommandsetEntryTitle();'>
					<label for='commandsetEntryName' lang-data='description'>${getLanguageAsText("description")}</label>
				</div>
			</td>
			<td colspan="2" style='width: 50%;'>
				<span class='ms-2'>ID: </span><span id='commandsetId'>${commandsetId}</span>
				<button id="commandsetEntry${commandsetId}ButtonExecute" class="disableOnDisconnect btn btn-outline-warning mb-3" onclick='executeCommandsetEntry(${commandsetId});' style='float: right;'><i class='bi bi-play pe-2'></i><span id='commandsetEntry${commandsetId}ButtonExecuteSpinner' class='spinner-border spinner-border-sm' role='status' hidden='true'></span><span lang-data="execute">${getLanguageAsText("execute")}</span></button>
			</td>
		</tr>
	</table>
<button id='commandEntry${commandsetId}ButtonNew' class='disableOnDisconnect btn btn-outline-success mt-2' onclick='addCommandToCommandset(${commandsetId});'><i class='bi bi-plus-lg pe-2'></i><span lang-data='new-command'>${getLanguageAsText("new-command")}</span></button>`;
	
	for (let i = 0; i < obj.commands.length; i++) {
		addCommandToCommandset(commandsetId, obj.commands[i].command, obj.commands[i].parameter == undefined ? "" : obj.commands[i].parameter);
	}
	commandsetModal.show();
	enableElements(prevItemsEnabled);
}

function plannerSwitchRadio(id) {
	for (let i = 0; i < 3; i++) getElement("plannerOption" + i).className = "btn btn-secondary w-100 m-2 mb-4";
	getElement("plannerOption" + id).className = "btn btn-primary w-100 m-2 mb-4";
}

function addCommandToCommandset(commandsetEntryId, command=0, parameter="") {
	let commandId = commandsetCommandCount;
	let newCommandEntryObj = document.createElement('tr');
	newCommandEntryObj.className = "border-top border-bottom border-primary commandrow";
	newCommandEntryObj.innerHTML = `<td class='p-2' style='width: 50%;'>
	<div class='form-floating'>
		<select id='commandsetEntry${commandsetEntryId}CommandSelect${commandId}' class='disableOnDisconnect form-select border border-secondary commandSelect' onchange='addParameterToCommandsetEntryCommand(${commandsetEntryId}, ${commandId}, value);'>
		</select>
		<label for="commandsetEntry${commandsetEntryId}CommandSelect${commandId}" lang-data="choose-command">${getLanguageAsText("choose-command")}</label>
	</div>
</td>
<td id='commandsetEntry${commandsetEntryId}Command${commandId}ParameterCell' class='p-2' style='width: 40%;'>
</td>
<td class='p-2' style='width: 10%;'>
	<button id="commandsetEntry${commandsetEntryId}CommandButtonDelete" class="disableOnDisconnect btn btn-danger" onclick='deleteCommandFromCommandset(this);' style='float: right;'><i class='bi bi-trash'></i></button>
</td>
`;
	//Adding element to document
	getElement("commandsetEntry" + commandsetEntryId + "CommandCollection").appendChild(newCommandEntryObj);

	//Adding dropdown options
	addCommandsToDropdown("commandsetEntry" + commandsetEntryId + "CommandSelect" + commandId);
	getElement("commandsetEntry" + commandsetEntryId + "CommandSelect" + commandId).value = command;

	addParameterToCommandsetEntryCommand(commandsetEntryId, commandId, command, parameter);

	commandsetCommandCount++;
}

function addParameterToCommandsetEntryCommand(commandsetEntryId, commandEntryId, commandId, parameter) {
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
		div.innerHTML = `<input id='commandsetEntry${commandsetEntryId}Command${commandEntryId}ParameterInput' type='text' class='disableOnDisconnect form-control border border-secondary commandParameter' onkeyup='' value='${parameter}' lang-data='parameter'>`;
	} else if (Array.isArray(commandCollection[commandId][1])) {
		let htmlSelect = `<select id='commandsetEntry${commandsetEntryId}Command${commandEntryId}ParameterInput' onchange='' class='disableOnDisconnect form-select border border-secondary commandParameter' value='${commandCollection[commandId][1][0][1]}'>\n`;
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

function deleteCommandsetEntry() {
	if (getCommandsetId(getCommandsetId()) < 0) {// < 0 is unsaved, > 0 is saved
		commandsetModal.hide();
	} else {
		sendHTTPRequest('GET', 'cmd.php?id=19&cmd=delete&commandsetid=' + getCommandsetId(), true, () => {commandsetModal.hide(); getScheduleFromServer();});
	}
}

function getCommandsetId() {
	return getElement("commandsetId").textContent;
}

function getCommandsetName(commandsetId) {
	for (let i = 0; i < scheduleObj.commandsets.length; i++) {
		if (scheduleObj.commandsets[i].id == commandsetId) {
			return scheduleObj.commandsets[i].name;
		}
	}
}

function showCommandsetEntryTitle() {
	getElement("commandsetModalTitle").innerText = getLanguageAsText("commandset") + ": " + getElement("commandsetEntryName").value;
}

function saveCommandsetEntry() {
	let commandsetEntryId = getCommandsetId();
	let commandsetEntryNameElement = getElement("commandsetEntryName");
	if (commandsetEntryNameElement.value == "") {
		commandsetEntryNameElement.className = "disableOnDisconnect form-control border border-danger";
		return;
	}

	let sendString = prepareCommandsetString(commandsetEntryId, commandsetEntryNameElement.value);
	if (getCommandsetId(commandsetEntryId) < 0) {//add
		sendHTTPRequest('GET', 'cmd.php?id=19&cmd=add&' + sendString, true, () => {commandsetModal.hide(); getScheduleFromServer();});
	} else {//update
		sendHTTPRequest('GET', 'cmd.php?id=19&cmd=update&commandsetid=' + getCommandsetId(commandsetEntryId) + '&' + sendString, true, () => {commandsetModal.hide(); getScheduleFromServer();});
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
	for (let i = 0; i < scheduleObj.commandsets.length; i++) {
		let optionTag = document.createElement("option");
		optionTag.value = scheduleObj.commandsets[i].id;
		optionTag.innerText = scheduleObj.commandsets[i].name;
		getElement(dropdownId).appendChild(optionTag);
		if (selectedId == scheduleObj.commandsets[i].id) {
			getElement(dropdownId).value = selectedId;
		}
	}
}

//main
window.onload = function() {
	setDarkMode(window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches);
	getDefaultLanguage();
	setDisplayProtocolSelect();
	setDisplayOrientationSelect();

	let st = null; //screenshotTime
	let idleBadge = getElement("idle");
	let active = getElement("active");
	let displayState = getElement("displayState");
	let uptime = getElement("uptime");
	let cpuLoad = getElement("cpuLoad");
	let cpuTemp = getElement("cpuTemp");
	let ramUsed = getElement("ramUsed");
	let ramTotal = getElement("ramTotal");
	let ramUsage = getElement("ramUsage");
	let displayOnBtn = getElement("displayOnButton");
	let displayStandbyBtn = getElement("displayStandbyButton");
	let spinnerDisplayOn = getElement("spinnerDisplayOn");
	let spinnerDisplayStandby = getElement("spinnerDisplayStandby");
	let screenshot = getElement("screenshot");
	let screenshotTime = getElement("screenshotTime");
	
	let requestedUrl = 'cmd.php?id=5';
	let xmlhttp = new XMLHttpRequest();
	xmlhttp.open('GET', requestedUrl, true);
	xmlhttp.timeout = timeoutTime;
	xmlhttp.ontimeout = () => {showServerError("Timeout error", requestedUrl);};
	//load periodical the current infos about the system
	xmlhttp.onload = () => {
		idleBadge.id = "notIdle";
		setTimeout(() => {
			idleBadge.id = "idle"
		}, 100);
		try {
			jsonData = JSON.parse(parseReturnValuesFromServer(xmlhttp.responseText));
		} catch (error) {
			showServerError("Failed to parse piScreen status", "", error);
		}
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
		switch (jsonData.modeInfo.mode) {
			case "firefox":
				getElement("screenContent").innerHTML = jsonData.modeInfo.url;
				rearrangeGui();
				break;
			case "vlc":
				
				break;
			case "impress":
				
				break;
		}
		if (connectionStatusChanged(true)) enableElements(true);

		rearrangeGui();
	}
	xmlhttp.onerror = () => {
		if (connectionStatusChanged(false)) {
			setToUnknownValues();
			enableElements(false);
			prevItemsEnabled = false;
		}
	}
	xmlhttp.ontimeout = () => {
		if (connectionStatusChanged(false)) {
			setToUnknownValues();
			enableElements(false);
			prevItemsEnabled = false;
		}
	}
	xmlhttp.send();

	//reload infos every 2 seconds
	setInterval(() => {
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
	let requestedUrl = "cmd.php?id=12";
	let xmlhttp = new XMLHttpRequest();
	xmlhttp.timeout = timeoutTime;
	xmlhttp.ontimeout = () => {showServerError("Timeout error", requestedUrl);};
	xmlhttp.onloadend = function () {
		if (!serverExecutedSuccessfully(xmlhttp.responseText)) {
			showServerError("Error while getting default language", requestedUrl);
			return;
		}
		try {
			let settingsJSON = JSON.parse(parseReturnValuesFromServer(xmlhttp.responseText));
			currentLanguage = settingsJSON.settings.language;
			fetchLanguage(currentLanguage);
		} catch (error) {
			showServerError("Failed to parse piScreen default language", xmlhttp.responseText, error);
		}
	}
	xmlhttp.open('GET', requestedUrl, true);
	xmlhttp.send();
}

function fetchLanguage(lang) { //Sets language to server and gets language.json
	currentLanguage = lang;
	getElement(lang).selected = true;
	let requestedUrl = '../languages/' + currentLanguage + '.json';
	let xmlhttp = new XMLHttpRequest();
	xmlhttp.timeout = timeoutTime;
	xmlhttp.ontimeout = () => {showServerError("Timeout error", requestedUrl);};
	xmlhttp.onloadend = function() {
		try {
			languageStrings = JSON.parse(xmlhttp.responseText);
		} catch (error) {
			showServerError("Failed to parse piScreen language json", requestedUrl, error);
			return;
		}
		getScheduleFromServer();
		setLanguageOnSite();
	}
	xmlhttp.open('GET', requestedUrl, true);
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

function sendHTTPRequest(method, url, wantResponse, loadend=() => {}) {
	let xmlhttp = new XMLHttpRequest();
	if (wantResponse) {
		xmlhttp.onloadend = () => {
			if (!serverExecutedSuccessfully(xmlhttp.responseText)) {
				console.log(xmlhttp.responseText);
				showServerError("Error from server", url, parseReturnValuesFromServer(xmlhttp.responseText));
				return;
			}
			loadend();
		};
	}
	xmlhttp.onerror = (e) => {showServerError(e, url);};
	xmlhttp.timeout = timeoutTime;
	xmlhttp.ontimeout = () => {showServerError("Timeout error", url);};
	xmlhttp.open(method, url, true);
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