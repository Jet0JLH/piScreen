////////////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////   general variables   ///////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////

var timeoutTime = 5000;
//schedule
let commandsetCommandCount = 0;
var commandsetEntryCount = 0;
const commandCollection = [//text, parameter
		["---", false], ["sleep", "text"], ["lastcron", false], ["", false], ["", false], ["", false], ["", false], ["", false], ["", false], ["", false],
		["universal", "text"], ["restart-device", false], ["shutdown-device", false], ["", false], ["", false], ["", false], ["", false], ["", false], ["", false], ["", false],
		["", false], ["", false], ["", false], ["", false], ["", false], ["", false], ["", false], ["", false], ["", false], ["", false],
		["display-state", [[0, "display-off"], [1, "display-on"]]], ["switch-display-input", false], ["change-display-protocol", [[0, "cec"], [1, "ddc"], [2, "manually"]]], ["", false], ["", false], ["", false], ["", false], ["", false], ["", false], ["", false],
		["start-browser", "text"], ["restart-browser", false], ["refresh-browser-page", false], ["stop-browser", false], ["", false], ["", false], ["", false], ["", false], ["", false], ["", false],
		["start-vlc-video", "filemanager", 2], ["restart-vlc-video", false], ["stop-vlc", false], ["play-pause-vlc-video", false], ["play-vlc-video", false], ["pause-vlc-video", false], ["set-volume-vlc", "text"], ["", false], ["", false], ["", false],
		["start-impress", "filemanager", 3], ["restart-impress", false], ["stop-impress", false], ["", false], ["", false], ["", false], ["", false], ["", false], ["", false], ["", false],
		["", false], ["", false], ["", false], ["", false], ["", false], ["", false], ["", false], ["", false], ["", false], ["", false],
		["", false], ["", false], ["", false], ["", false], ["", false], ["", false], ["", false], ["", false], ["", false], ["", false],
		["", false], ["", false], ["", false], ["", false], ["", false], ["", false], ["", false], ["", false], ["", false], ["", false],
	];
var scheduleObj;
//import
var scheduleToImport = null;
//trigger
var startupTriggerIndex = -1;
var triggerCollection = [//[]name, []list cases, []parameters
	["", false], ["", false], ["", false], ["", false], ["", false], ["", false], ["", false], ["", false], ["", false], ["", false],
	["file-exists", ["true", "false", "change"], ["file"]], ["file-changed", ["true"], ["file"]], ["", false], ["", false], ["", false], ["", false], ["", false], ["", false], ["", false], ["", false],
	["tcp-connection-changed", ["true", "false", "change"], ["host", "port", "tries", "timeout"]], ["", false], ["", false], ["", false], ["", false], ["", false], ["", false], ["", false], ["", false], ["", false],
	["display-state-on", ["true", "false", "change"], []], ["cec-key-pressed", ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "accept", "up", "down", "left", "right", "exit", "play", "pause", "stop", "forward", "rewind", "record", "red", "green", "yellow", "blue"], []], ["", false], ["", false], ["", false], ["", false], ["", false], ["", false], ["", false], ["", false],
	["mode-changed", ["true", "firefox", "vlc", "impress", "none"], []], ["", false], ["", false], ["", false], ["", false], ["", false], ["", false], ["", false], ["", false], ["", false]
];
var triggerEntryCount = 0;
//general modal
var modal = new bootstrap.Modal(getElement("modal"));
var modalCloseBtn = modal._element.getElementsByClassName('btn-close')[0];
var modalTitle = modal._element.getElementsByClassName('modal-title')[0];
var modalBody = modal._element.getElementsByClassName('modal-body')[0];
var modalCancelBtn = getElement("modal-cancelBtn");
var modalActionBtn = getElement("modal-actionBtn");
//modals
var scheduleModal = new bootstrap.Modal(getElement("scheduleModal"));
var commandsetModal = new bootstrap.Modal(getElement("commandsetModal"));
var triggerModal = new bootstrap.Modal(getElement("triggerModal"));
var cronEditorModal = new bootstrap.Modal(getElement("cronEditorModal"));
var fileExplorerModal = new bootstrap.Modal(getElement("fileExplorerModal"));
var renameModal = new bootstrap.Modal(getElement("renameModal"));
var screenshotModal = new bootstrap.Modal(getElement("screenshotModal"));
//language
var currentLanguage = null;
var languageStrings = null;
var prevItemsEnabled = null;
//cron entry limitations
const minuteLowerLimit = 0, minuteUpperLimit = 59;
const hourLowerLimit = 0, hourUpperLimit = 23;
const dayOfMonthLowerLimit = 1, dayOfMonthUpperLimit = 31;
const monthLowerLimit = 1, monthUpperLimit = 12;
const dayOfWeekLowerLimit = 0, dayOfWeekUpperLimit = 6;
//file explorer
const modeGeneral = 0;
const modeFirefox = 1;
const modeVLC = 2;
const modeImpress = 3;
var currentFileExplorerMode = 2;
const modes = ["general", "firefox", "vlc", "impress"]; //there is no mode 0 
var currentMode = 0;
var currentRenameFile;
var fileExplorerReturnElement = null;
var prevVlcVideoState = "";
var modifiedVlcVolume = false;
//screenshot modal
var screenshotModalShown = false;
//color picker
var colorPickerElement = document.createElement("input");
colorPickerElement.type = "color";
colorPickerElement.onchange = () => {getElement("setBackgroundInputTextfield").value = colorPickerElement.value.substring(1);};
//splashscreen
var splashscreenActive = true;

////////////////////////////////////////////////////////////////////////////////////////////////////
/////////////////////////////////   general schedule functions   ///////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////

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

	if (getElement("ignoreTimeScheduleStartDateTime").value != undefined) getElement("ignoreTimeScheduleStartDateTime").value = scheduleObj.ignoreCronFrom;
	if (getElement("ignoreTimeScheduleEndDateTime").value != undefined) getElement("ignoreTimeScheduleEndDateTime").value = scheduleObj.ignoreCronTo;

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

	addCommandsToDropdown("startupTriggerCommandSelect");//trigger
	addCommandsetsToDropdown("startupTriggerCommandsetSelect");//trigger
	for (let i = 0; i < scheduleObj.trigger.length; i++) {//trigger parameter
		let triggerObj = scheduleObj.trigger[i];
		if (triggerObj.trigger == 1) {
			startupTriggerIndex = i;
			if (triggerObj.enabled != undefined) getElement("startupTriggerEnabledSwitch").checked = triggerObj.enabled;
			else getElement("startupTriggerEnabledSwitch").checked = false;
			
			if (triggerObj.cases.true.command != undefined) {
				getElement("startupTriggerCommandSelect").value = triggerObj.cases.true.command;
				addParameterToStartupTrigger(triggerObj.cases.true.command, triggerObj.cases.true.parameter);
			} else getElement("startupTriggerCommandSelect").value = 0;

			if (triggerObj.cases.true.commandset != undefined) {
				getElement("startupTriggerCommandsetSelect").value = triggerObj.cases.true.commandset;
			} else getElement("startupTriggerCommandsetSelect").value = 0;
			break;
		}
	}

	getElement("triggerCollectionList").innerHTML = "";
	triggerEntryCount = 0;
	for (let i = 0; i < scheduleObj.trigger.length; i++) {//trigger
		if (scheduleObj.trigger[i].trigger != 1) //skip the startup trigger
			generateTriggerEntry(scheduleObj.trigger[i]);
		triggerEntryCount += 1;
	}
}

////////////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////   schedule entry functions   ////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////

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
	newScheduleEntryObj.onclick = () => {showScheduleModal(scheduleEntryId);};
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

function showScheduleModal(scheduleEntryId) {
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

	getElement("scheduleModalTitle").innerHTML = `<i class="bi bi-asterisk bigIcon pe-2"></i><span lang-data="cron-entry">${getLanguageAsText("cron-entry")}</span><span id='currentScheduleEntryId' hidden>${scheduleEntryId}</span>`;
	getElement("scheduleModalBody").innerHTML = `<table class="table-sm" style='width: 100%;'>
	<div id='scheduleEntry'>
		<tr>
			<td style='width: 50%;'>
				<div class="form-check form-switch">
					<input class="disableOnDisconnect form-check-input" type="checkbox" role="switch" id="scheduleEntryEnabledSwitchCheck" onchange="scheduleEntrySaved(false);" ${enabled ? "checked" : ""}>
					<label class="form-check-label" for="scheduleEntryEnabledSwitchCheck" lang-data="active">${getLanguageAsText("active")}</label>
				</div>
			</td>
			<td style='width: 50%;'>
				<button id="scheduleEntryButtonExecute" class="disableOnDisconnect btn btn-outline-warning mt-2" onclick='executeScheduleEntry(${scheduleEntryId});' style='float: right;'><i class='bi bi-play pe-2'></i><span id='scheduleEntryButtonExecuteSpinner' class='spinner-border spinner-border-sm' role='status' hidden='true'></span><span lang-data="execute">${getLanguageAsText("execute")}</span></button>
			</td>
		</tr>
		<tr>
			<td>
				<div class="input-group mb-3">
					<button class='disableOnDisconnect btn btn-outline-primary border-secondary border-end-0' onclick='showCronEditorModal(); scheduleModal.hide();'><i class='bi bi-pencil-square pe-2'></i><span lang-data='edit-cron-entry'>${getLanguageAsText("edit-cron-entry")}</span></button>
					<input id='cronentry' type="text" class="disableOnDisconnect form-control border-secondary border-start-0" value='${pattern}' onkeyup='scheduleEntrySaved(false); cronEntryError(this);'>
				</div>
			</td>
			<td>
				<i class='bi-question-octagon p-2' style='cursor: pointer;' id='cronEntryHelp' onclick='showModal(getLanguageAsText("help"), getLanguageAsText("cronHelpText"), false, true, getLanguageAsText("ok"));'></i>
			</td>
		</tr>
		<tr>
			<td>
				<div class='form-floating'>
					<select id='scheduleEntryCommandSelect' class='disableOnDisconnect form-select border border-secondary' onchange='scheduleEntrySaved(false); addParameterToScheduleEntry(value);'>
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
					<select id='scheduleEntryCommandsetSelect' class='disableOnDisconnect commandsetDropdown form-select border border-secondary' onchange="scheduleEntrySaved(false);" value='${commandset}'>
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
								<input class="disableOnDisconnect form-check-input" type="checkbox" role="switch" id="scheduleEntryValiditySwitchCheckFrom" onchange='scheduleEntrySaved(false); toggleValidityFrom(checked);' ${start != undefined ? "checked" : ""}>
								<label class="form-check-label" for="scheduleEntryValiditySwitchCheckFrom" lang-data="valid-from">${getLanguageAsText("valid-from")}</label>
							</div>
						</td>
						<td colspan='2' class='p-2'>
							<div class="form-check form-switch">
								<input class="disableOnDisconnect form-check-input" type="checkbox" role="switch" id="scheduleEntryValiditySwitchCheckTo" onchange='scheduleEntrySaved(false); toggleValidityTo(checked);' ${end != undefined ? "checked" : ""}>
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
								<input id='scheduleEntryStartTime' name='scheduleEntryStartDateTime' type="time" class="disableOnDisconnect form-control border border-secondary p-1" style="text-align: center; width: 40%;" onchange='scheduleEntrySaved(false);' value="${startTime}">
								<input id='scheduleEntryStartDate' type="date" class="disableOnDisconnect form-control border border-secondary p-1" style="text-align: center; width: 60%;" onchange='scheduleEntrySaved(false);' value="${startDate}">
							</div>
						</td>
						<td id='scheduleEntryValidityTimeSpanTo1' class='px-2' lang-data='to'>
						${getLanguageAsText("to")}
						</td>
						<td id='scheduleEntryValidityTimeSpanTo2'>
							<div class='input-group'>
								<input id='scheduleEntryEndTime' name='scheduleEntryEndDateTime' type="time" class="disableOnDisconnect form-control border border-secondary p-1" style="text-align: center; width: 40%;" onchange='scheduleEntrySaved(false);' value="${endTime}">
								<input id='scheduleEntryEndDate' type="date" class="disableOnDisconnect form-control border border-secondary p-1" style="text-align: center; width: 60%;" onchange='scheduleEntrySaved(false);' value="${endDate}">
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
	scheduleModal.show();
	enableElements(prevItemsEnabled);
	scheduleEntrySaved(scheduleEntryId >= 0);
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
		div.innerHTML = `<input id='scheduleEntryParameterInput' type='text' class='disableOnDisconnect form-control border border-secondary' onkeyup='scheduleEntrySaved(false);' value='${parameter}' lang-data='parameter'>`;
		if (parameter == undefined) parameter = "";
	} else if (commandCollection[commandId][1] == "filemanager") {
		div.className += " w-75";
		div.innerHTML = `<input id='scheduleEntryParameterInput' type='text' class='disableOnDisconnect form-control border border-secondary' onkeyup='scheduleEntrySaved(false);' value='${parameter}' lang-data='parameter'>`;
		let btn = document.createElement("button");
		btn.id = "scheduleEntryFileManagerButtonOpen";
		btn.onclick = () => showFileExplorerModal(commandCollection[commandId][2], false, getElement("scheduleEntryParameterInput"));
		btn.className = "disableOnDisconnect btn btn-outline-success mt-2";
		btn.style.float = "right";
		btn.innerHTML = `<i class="bi bi-folder"></i>`;
		cell.appendChild(btn);
		if (parameter == undefined) parameter = "";
	} else if (Array.isArray(commandCollection[commandId][1])) {
		let htmlSelect = `<select id='scheduleEntryParameterInput' class='disableOnDisconnect form-select border border-secondary' onchange='scheduleEntrySaved(false);'>\n`;
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

function executeLastCron() {
	getElement("executeLastCronSpinner").hidden = false;
	sendHTTPRequest('GET', 'cmd.php?id=22', true, () => getElement("executeLastCronSpinner").hidden = true);
}

function scheduleEntrySaved(saved) {
	let scheduleEntryButtonElement = getElement("scheduleEntryButtonExecute");
	if (saved) {
		scheduleEntryButtonElement.className = "disableOnDisconnect btn btn-outline-warning mt-2";
		if (prevItemsEnabled) scheduleEntryButtonElement.disabled = false;
	} else {
		scheduleEntryButtonElement.className = "btn btn-outline-warning mt-2";
		scheduleEntryButtonElement.disabled = true;
	}
}

function saveScheduleEntry() {
	//send to server
	if (getElement("currentScheduleEntryId").innerText < 0) {//add
		sendHTTPRequest('GET', 'cmd.php?id=9&cmd=add&' + prepareScheduleString(), true, () => {scheduleModal.hide(); getScheduleFromServer();});
	} else {//update
		sendHTTPRequest('GET', 'cmd.php?id=9&cmd=update&' + prepareScheduleString() + '&index=' + getElement("currentScheduleEntryId").innerText, true, () => {scheduleModal.hide(); getScheduleFromServer();});
	}
}

function deleteScheduleEntry() {
	if (getElement("currentScheduleEntryId").innerText >= 0) {
		sendHTTPRequest('GET', 'cmd.php?id=9&cmd=delete&index=' + getElement("currentScheduleEntryId").innerText, true, () => {scheduleModal.hide(); getScheduleFromServer();});
	} else {
		scheduleModal.hide();
	}
}

function executeScheduleEntry() {
	getElement("scheduleEntryButtonExecuteSpinner").hidden = false;
	sendHTTPRequest('GET', 'cmd.php?id=9&cmd=execute&index=' + getElement("currentScheduleEntryId").innerText, true, () => getElement("scheduleEntryButtonExecuteSpinner").hidden = true);
}

////////////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////   schedule entry helper functions   ////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////

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
	} else {
		msg += "parameter=\"\"&"
	}
	msg = msg.substring(0, msg.length - 1);
	
	return msg;
}

function cronEntryError(scheduleCronEntry) {
	let saveButton = getElement("scheduleEntryButtonSave");
	if (checkCronEntryValidity(scheduleCronEntry.value)) {
		saveButton.className = "disableOnDisconnect btn btn-outline-success m-1"
		if(prevItemsEnabled) saveButton.disabled = false;
		scheduleCronEntry.className = "disableOnDisconnect form-control border border-secondary text-body"
	} else {
		saveButton.className = "btn btn-outline-success m-1"
		saveButton.disabled = true;
		scheduleCronEntry.className = "disableOnDisconnect form-control border border-danger text-danger"
	}

}

function checkCronEntryValidity(cronEntryString) {
	let acceptedChars = "0123456789,/-* "
	cronEntryString = cronEntryString.trim();
	while (cronEntryString.includes("  ")) cronEntryString = cronEntryString.replaceAll("  ", " ");//removes whitespace
	if (cronEntryString.split(" ").length != 5) return false;

	for (let i = 0; i < cronEntryString.length; i++) { // check if all used chars are valid
		if (!acceptedChars.includes(cronEntryString[i])) {
			return false;
		}
	}

	for (let i = 0; i < ",/- ".length; i++) {//checks if starts or ends with operator
		if (cronEntryString.startsWith(",/- "[i]) || cronEntryString.endsWith(",/- "[i])) {
			return false;
		}
	}

	for (let i = 1; i < cronEntryString.length - 1; i++) {//checks that operators are surrounded by values
		if (",/-".includes(cronEntryString[i])) {
			if (!"0123456789*".includes(cronEntryString[i-1]) || !"0123456789".includes(cronEntryString[i+1])) {
				return false;
			}
		}
	}

	let varArray = cronEntryString.split(" ");
	for (let i = 0; i < varArray.length; i++) {
		switch (i) {
			case 0://minutes
				if (!checkCronEntrySubsequenceValidity(varArray[i], minuteLowerLimit, minuteUpperLimit)) return false;
				break;
			case 1://hours
				if (!checkCronEntrySubsequenceValidity(varArray[i], hourLowerLimit, hourUpperLimit)) return false;
				break;
			case 2://days in month
				if (!checkCronEntrySubsequenceValidity(varArray[i], dayOfMonthLowerLimit, dayOfMonthUpperLimit)) return false;
				break;
			case 3://months
				if (!checkCronEntrySubsequenceValidity(varArray[i], monthLowerLimit, monthUpperLimit)) return false;
				break;
			case 4://days in week
				if (!checkCronEntrySubsequenceValidity(varArray[i], dayOfWeekLowerLimit, dayOfWeekUpperLimit)) return false;
				break;
		}
	}
	return true;
}

function checkCronEntrySubsequenceValidity(subsequence, lowerLimit, upperLimit) {
	let validNumbersArray = getArrayFromTo(lowerLimit, upperLimit);
	try {//check if subsequence is only a number and if it is in valid limits
		if (parseInt(subsequence) < lowerLimit || parseInt(subsequence) > upperLimit) return false;
	} catch (error) {}
	if (subsequence.includes("*")) {
		if (subsequence != "*") {
			if (!subsequence.includes("*/")) return false;
		}
	}
	if (subsequence.includes(",")) {
		if (hasDuplicates(subsequence, ",")) return false;
		const subArray = subsequence.split(",");
		for (let j = 0; j < subArray.length; j++) {//check if number is in valid range
			if (subArray[j] < lowerLimit || subArray[j] > upperLimit) return false;
		}
		for (let j = 1; j < subArray.length - 2; j++) {//checks if invalid char is directly in front or behind ,
			if (!validNumbersArray.includes(subArray[j-1]) || !validNumbersArray.includes(subArray[j+1])) return false;	
		}
	}
	if (subsequence.includes("-")) {
		if (hasDuplicates(subsequence, "-")) return false;
		const subArray = subsequence.split("-");
		for (let j = 0; j < subArray.length; j++) {//check if number is in valid range
			if (subArray[j] < lowerLimit || subArray[j] > upperLimit) return false;
		}
		for (let j = 1; j < subArray.length - 2; j++) {//checks if invalid char is directly in front or behind -
			if (!validNumbersArray.includes(subArray[j-1]) || !validNumbersArray.includes(subArray[j+1])) return false;	
		}
	}
	if (subsequence.includes("/")) {
		if (hasDuplicates(subsequence, "/")) return false;
		const subArray = subsequence.split("/");
		if (subArray.length > 2) return false;//only one / allowed
		for (let j = 0; j < "*-,0".length; j++) {//check for valid character behind /
			if (subArray[1].includes("*-,0"[j])) return false;
		}
		for (let j = 0; j < subArray.length; j++) {//check if number is in valid range
			if (subArray[j] < lowerLimit || subArray[j] > upperLimit) return false;
			if (",/- ".includes(subArray[j])) return false;
		}
		for (let j = 1; j < subArray.length - 2; j++) {//checks if invalid char is directly in front or behind /
			let tempArr = validNumbersArray + "*";
			if (!tempArr.includes(subsequence[j-1]) || !validNumbersArray.includes(subsequence[j+1])) return false;
		}
	}
	return true;
}

function getArrayFromTo(start, end) {
	let arr = [];
	for (let i = 0; i <= end-start; i++) arr[i] = (i + start).toString();
	return arr;
}

function hasDuplicates(str, separator) {
	const arr = str.split(separator);
	let singleArr = [];
	for (let i = 0; i < arr.length; i++) {
		if (singleArr.includes(arr[i])) return true;
		singleArr.push(arr[i]);
	}
	return false;
}

function cronEditorCarouselSwitchRadio(id) {
	for (let i = 0; i < 3; i++) getElement("cronEditorCarouselOptionLabel" + i).className = "btn btn-secondary w-100 mb-4";
	getElement("cronEditorCarouselOptionLabel" + id).className = "btn btn-primary w-100 mb-4";
}

////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////   cron editor functions   /////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////

function showCronEditorModal() {
	updateSelectableValues(0);
	cronEditorModal.show();
}

function cronEditorOnChange(activeValue) {
	switch (activeValue) {
		case "1":
			getElement("cronEditorDailyRow").hidden = false;
			getElement("cronEditorMonthlyRow").hidden = true;
			getElement("cronEditorPeriodicRow").hidden = true;
			break;
		case "2":
			getElement("cronEditorDailyRow").hidden = true;
			getElement("cronEditorMonthlyRow").hidden = false;
			getElement("cronEditorPeriodicRow").hidden = true;
			break;
		case "3":
			getElement("cronEditorDailyRow").hidden = true;
			getElement("cronEditorMonthlyRow").hidden = true;
			getElement("cronEditorPeriodicRow").hidden = false;
			break;
	}
}

function cronEditorOk() {
	let cronString = parseCronEntry();
	if (cronString) {
		getElement("cronentry").value = cronString;
		cronEditorModal.hide();
		scheduleEntrySaved(false);
	} else showModal(getLanguageAsText("error"), "Invalid input.<br>" + cronString, true, true, getLanguageAsText("ok"));
}

function parseCronEntry() {
	let result = "";
	if (getElement("cronEditorCarouselOptionLabel0").className.includes("btn-primary")) {
		if (getElement("cronEditorDailyTime").value.split(":")[1] == undefined) return false;//no valid time
		else result += parseInt(getElement("cronEditorDailyTime").value.split(":")[1]);//parse to int to remove leading zeros
		result += " ";

		if (getElement("cronEditorDailyTime").value.split(":")[0] == undefined) return false;
		else result += parseInt(getElement("cronEditorDailyTime").value.split(":")[0]);
		result += " * * ";

		for (let i = 0; i < document.getElementsByClassName("dailyDayCheck").length; i++) {
			if (document.getElementsByClassName("dailyDayCheck")[i].checked) {
				result += document.getElementsByClassName("dailyDayCheck")[i].value + ",";
			}
		}
		if (result.endsWith(",")) result = result.substring(0, result.length - 1);
		else return false;//no days checked

	} else if (getElement("cronEditorCarouselOptionLabel1").className.includes("btn-primary")) {
		if (getElement("cronEditorMonthlyTime").value.split(":")[1] == undefined) return false;//no valid time
		else result += parseInt(getElement("cronEditorMonthlyTime").value.split(":")[1]);//parse to int to remove leading zeros
		result += " ";

		if (getElement("cronEditorMonthlyTime").value.split(":")[0] == undefined) return false;
		else result += parseInt(getElement("cronEditorMonthlyTime").value.split(":")[0]);
		result += " ";

		for (let i = 0; i < document.getElementsByClassName("monthlyDayCheck").length; i++) {
			if (document.getElementsByClassName("monthlyDayCheck")[i].checked) {
				result += document.getElementsByClassName("monthlyDayCheck")[i].value + ",";
			}
		}
		if (result.endsWith(",")) result = result.substring(0, result.length - 1);
		else return false;//no days checked

		result += " * *";

	} else if (getElement("cronEditorCarouselOptionLabel2").className.includes("btn-primary")) {
		let val = getElement("cronEditorPeriodicTimeSelect").value;
		switch (getElement("cronEditorPeriodicTimeSpanSelect").value) {
			case "0"://minutes
			if (val == 1) result += "*"; 
			else result += "*/" + val;
			result += " * * * *";
			break;

			case "1"://hours
			if (val == 1) result += "0 *"; 
			else result += "0 */" + val;
			result += " * * *";
			break;

			case "2"://months
			if (val == 1) result += "0 0 1 *"; 
			else result += "0 0 1 */" + val;
			result += " *";
			break;
		}
	}
	return result;
}

function updateSelectableValues(value) {
	let values = [[1, 2, 3, 4, 5, 6, 10, 15, 20, 30], [1, 2, 4, 6, 8, 12], [1, 2, 3, 4, 6]];
	let dropdown = getElement("cronEditorPeriodicTimeSelect");
	dropdown.innerHTML = "";
	for (let i = 0; i < values[value].length; i++) {
		let opt = document.createElement("option");
		opt.id = "periodicTimeOption" + values[value][i];
		opt.value = values[value][i];
		opt.innerText = values[value][i];
		dropdown.appendChild(opt);
	}
}

function cronEditorDaysSelectAll() {
	for (let i = 0; i < document.getElementsByClassName("dailyDayCheck").length; i++) {
		document.getElementsByClassName("dailyDayCheck")[i].checked = true;
	}
}

function cronEditorDaysInvert() {
	for (let i = 0; i < document.getElementsByClassName("dailyDayCheck").length; i++) {
		document.getElementsByClassName("dailyDayCheck")[i].checked = !document.getElementsByClassName("dailyDayCheck")[i].checked;
	}
}

function cronEditorDaysUnselectAll() {
	for (let i = 0; i < document.getElementsByClassName("dailyDayCheck").length; i++) {
		document.getElementsByClassName("dailyDayCheck")[i].checked = false;
	}
}

function cronEditorMonthsSelectAll() {
	for (let i = 0; i < document.getElementsByClassName("monthlyDayCheck").length; i++) {
		document.getElementsByClassName("monthlyDayCheck")[i].checked = true;
	}
}

function cronEditorMonthsInvert() {
	for (let i = 0; i < document.getElementsByClassName("monthlyDayCheck").length; i++) {
		document.getElementsByClassName("monthlyDayCheck")[i].checked = !document.getElementsByClassName("monthlyDayCheck")[i].checked;
	}
}

function cronEditorMonthsUnselectAll() {
	for (let i = 0; i < document.getElementsByClassName("monthlyDayCheck").length; i++) {
		document.getElementsByClassName("monthlyDayCheck")[i].checked = false;
	}
}

////////////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////   trigger functions   ///////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////

function generateTriggerEntry(triggerObj) {
	let tempTriggerCount = triggerEntryCount;
	let triggerEntryObj = document.createElement('div');
	triggerEntryObj.id = "triggerEntry" + triggerObj.trigger;
	triggerEntryObj.className = "disableOnDisconnect list-group-item list-group-item-action border border-primary p-3";
	triggerEntryObj.style.backgroundColor = "transparent";
	triggerEntryObj.onclick = () => {showTriggerModal(tempTriggerCount);};
	triggerEntryObj.style.cursor = "pointer";
	triggerEntryObj.innerHTML = `<div class="d-flex w-100 justify-content-between">
	<p><i class='bi bi-lightning bigIcon pe-2'></i>${getLanguageAsText(triggerCollection[triggerObj.trigger][0])}</p>
	<p><span lang-data="active">${getLanguageAsText("active")}</span>: ${triggerObj.enabled ? "<i class='bi bi-check-lg bigIcon pe-2' style='color: green;'></i>" : "<i class='bi bi-x-lg bigIcon pe-2' style='color: red;'></i>"}</p>
</div>
<i class='bi bi-chat-left-quote bigIcon pe-2'></i><span lang-data="description">${getLanguageAsText("description")}</span>: ${triggerObj.comment == undefined ? "-" : triggerObj.comment}`;
	getElement("triggerCollectionList").appendChild(triggerEntryObj);
}

function addParameterToStartupTrigger(commandId, parameter) {
	let cell = getElement("startupTriggerParameterCell");
	cell.innerHTML = "";
	//add element
	let div = document.createElement("div");
	div.id = "startupTriggerParameterInputDiv";
	div.className = "form-floating mb-3";

	if (commandCollection[commandId][1] == false) {
		return;
	} else if (commandCollection[commandId][1] == "text") {
		div.innerHTML = `<input id='startupTriggerParameterInput' type='text' class='disableOnDisconnect form-control border border-secondary' onkeyup='startupTriggerSaved(false);' lang-data='parameter'>`;
		if (parameter == undefined) parameter = "";
	} else if (commandCollection[commandId][1] == "filemanager") {
		div.className += " w-75";
		div.innerHTML = `<input id='startupTriggerParameterInput' type='text' class='disableOnDisconnect form-control border border-secondary' onkeyup='startupTriggerSaved(false);' value='${parameter}' lang-data='parameter'>`;
		let btn = document.createElement("button");
		btn.id = "startupTriggerFileManagerButtonOpen";
		btn.onclick = () => showFileExplorerModal(commandCollection[commandId][2], false, getElement("startupTriggerParameterInput"));
		btn.className = "disableOnDisconnect btn btn-outline-success mt-2";
		btn.style.float = "right";
		btn.innerHTML = `<i class="bi bi-folder"></i>`;
		cell.appendChild(btn);
		if (parameter == undefined) parameter = "";
	} else if (Array.isArray(commandCollection[commandId][1])) {
		let htmlSelect = `<select id='startupTriggerParameterInput' class='disableOnDisconnect form-select border border-secondary' style='width: 100%;' onchange='startupTriggerSaved(false);'>\n`;
		for (let i = 0; i < commandCollection[commandId][1].length; i++) {
			htmlSelect += `<option value='${commandCollection[commandId][1][i][0]}' lang-data='${commandCollection[commandId][1][i][1]}'>${getLanguageAsText(commandCollection[commandId][1][i][1])}</option>\n`;
		}
		htmlSelect += "</select>";
		div.innerHTML = htmlSelect;
		if (parameter == undefined) parameter = 0;
	}

	cell.appendChild(div);
	getElement("startupTriggerParameterInput").value = parameter;

	//add label
	let label = document.createElement("label");
	label.htmlFor = "startupTriggerParameterInput";
	label.setAttribute('lang-data', 'parameter');
	label.innerHTML = getLanguageAsText('parameter');
	div.appendChild(label);
}

function showTriggerModal(triggerEntryId=-1, newTrigger=false) {
	let obj;
	if (triggerEntryId == -1) {//default new entry
		obj = {
			"enabled": true,
			"trigger": 10,
			"cases": {}
		};
	} else {
		obj = scheduleObj.trigger[triggerEntryId];
	}

	getElement("triggerModalTitle").setAttribute("newtrigger", newTrigger);
	getElement("triggerModalTitle").innerHTML = `<i class="bi bi-terminal bigIcon pe-2"></i><span lang-data="trigger">${getLanguageAsText("trigger")}</span>: <span lang-data="trigger">${getLanguageAsText(triggerCollection[obj.trigger][0])}</span>`;
	getElement("triggerModalBody").innerHTML = `<table id="triggerEntryCaseCollection" style='width: 100%;'>
	<tr>
		<td>
			<div class="form-check form-switch m-2" style='width: 50%;'>
				<input class="disableOnDisconnect form-check-input" type="checkbox" role="switch" id="triggerEntryEnabledSwitchCheck" onchange="triggerSaved(false);" ${obj.enabled ? "checked" : ""}>
				<label class="form-check-label" for="triggerEntryEnabledSwitchCheck" lang-data="active">${getLanguageAsText("active")}</label>
			</div>
		</td>
		<td colspan="2" style='width: 50%;'>
			<span class='ms-2'>ID: </span><span id='triggerId'>${triggerEntryId}</span>
			<button id="triggerEntryButtonExecute" class="btn btn-outline-warning mb-3" onclick='' style='float: right;' hidden><i class='bi bi-play pe-2'></i><span id='triggerEntryButtonExecuteSpinner' class='spinner-border spinner-border-sm' role='status' hidden='true'></span><span lang-data="execute">${getLanguageAsText("execute")}</span></button>
		</td>
	</tr>
	<tr>
		<td colspan="2" style='width: 50%;'>
			<div class='form-floating mb-3'>
				<select id='triggerSelect' class='disableOnDisconnect form-select border border-secondary' onchange='triggerSaved(false); removeAllCaseAddButtons(); addAllCaseAddButton(value); addTriggerParameter(value)' value='${obj.trigger}'>
				</select>
				<label for="triggerSelect" lang-data="choose-trigger">${getLanguageAsText("choose-trigger")}</label>
			</div>
		</td>
		<td style='width: 50%;'>
			<div class='form-floating mb-3'>
				<input id='triggerEntryDescription' type='text' class='disableOnDisconnect form-control border border-secondary' value='${obj.comment == undefined ? "" : obj.comment}' onkeyup='triggerSaved(false);'>
				<label for='triggerEntryDescription' lang-data='description'>${getLanguageAsText("description")}</label>
			</div>
		</td>
	</tr>
	<tr>
		<td colspan="3" class="w-100 pb-3">
			<table id="triggerParameterCollection" class="w-100">
			</table>
		</td>
	</tr>
</table>
<div id="triggerEntryButtonNewCaseDiv" class="btn-group dropend">
	<button id='triggerEntryButtonNewCase' class="disableOnDisconnect btn btn-outline-success mt-2 dropdown-toggle" data-bs-toggle="dropdown"><i class='bi bi-plus-lg pe-2'></i><span lang-data='add-trigger-case'>${getLanguageAsText("add-trigger-case")}</span></button>
	<ul id="triggerButtonAddCaseList" class="dropdown-menu dropdown-menu-dark">
	</ul>
</div>`;

	for (let i = 0; i < triggerCollection.length; i++) {
		if (triggerCollection[i][0] + "+" != "+") {
			let opt = document.createElement("option");
			opt.value = i;
			opt.innerHTML = getLanguageAsText(triggerCollection[i][0]);
			opt.selected = i == obj.trigger ? true : false;

			getElement("triggerSelect").appendChild(opt);
		}
	}

	addTriggerParameter(obj.trigger, obj);

	triggerModal.show();

	let triggerCases = Object.keys(obj.cases);
	for (let i = 0; i < Object.keys(obj.cases).length; i++) {
		addCaseRow(triggerCases[i], obj.cases[triggerCases[i]].commandset, obj.cases[triggerCases[i]].command, obj.cases[triggerCases[i]].parameter);
	}
	for (let i = 0; i < triggerCollection[obj.trigger][1].length; i++) {
		if (!triggerCases.includes(triggerCollection[obj.trigger][1][i])) {
			addCaseAddButton(triggerCollection[obj.trigger][1][i]);
		}
	}

	enableElements(prevItemsEnabled);
}

function addTriggerParameter(trigger, triggerObj) {
	getElement("triggerParameterCollection").innerHTML = "";
	for (let i = 0; i < triggerCollection[trigger][2].length; i++) {
		let row = document.createElement("tr");
		row.innerHTML = `<td>
	<div class="form-floating">
		<input id='triggerParameter${triggerCollection[trigger][2][i]}' type='text' class='disableOnDisconnect form-control border border-secondary triggerParameter' onkeyup='triggerSaved(false);' value="${triggerObj == undefined || triggerObj[triggerCollection[trigger][2][i]] == undefined ? '' : triggerObj[triggerCollection[trigger][2][i]]}">
		<label for="triggerParameter${triggerCollection[trigger][2][i]}" lang-data="${triggerCollection[trigger][2][i]}">${getLanguageAsText(triggerCollection[trigger][2][i])} *</label>
	</div>
</td>`;
		getElement("triggerParameterCollection").appendChild(row);
	}
}

function addCaseAddButton(triggerCase) {
	let newCase = document.createElement("li");
	newCase.id = "caseListItem" + triggerCase;
	newCase.innerHTML = `<button class="dropdown-item" onclick='triggerSaved(false); addCaseRow(this.innerHTML); removeCaseAddButton("${triggerCase}");'>${triggerCase}</button>`;
	getElement("triggerButtonAddCaseList").appendChild(newCase);
}

function removeCaseAddButton(triggerCase) {
	getElement("caseListItem" + triggerCase).remove();
}

function removeCaseRow(triggerCase) {
	getElement("caseRow" + triggerCase).remove();
}

function addCaseRow(triggerCase, commandset=0, command=0, parameter="") {
	let newTriggerEntryObj = document.createElement('tr');
	newTriggerEntryObj.id = "caseRow" + triggerCase;
	newTriggerEntryObj.setAttribute("case", triggerCase);
	newTriggerEntryObj.className = "border-top border-bottom border-primary caseRow";
	newTriggerEntryObj.innerHTML = `<td colspan="3" class='p-2' style='width: 50%;'>
	<table class="w-100">
		<tr>
			<td colspan="2">
				<h5><span lang-data="case">${getLanguageAsText("case")}</span>: <span id="triggerCase" class="triggerCase">${triggerCase}</span></h5>
			</td>
			<td>
			</td>
		</tr>
		<tr>
			<td style='width: 45%;'>
				<div class='form-floating p-1'>
					<select id='triggerEntryCommandSelect${triggerCase}' class='disableOnDisconnect form-select border border-secondary commandSelect' onchange='triggerSaved(false); addParameterToTriggerCaseCommand("${triggerCase}", value);'>
					</select>
					<label for="triggerEntryCommandSelect${triggerCase}" lang-data="choose-command">${getLanguageAsText("choose-command")}</label>
				</div>
			</td>
			<td id='triggerCaseCommand${triggerCase}ParameterCell' class='p-1' style='width: 45%;'>
			</td>
			<td class='p-2' style='width: 10%;'>
				<button id="triggerCaseButtonDelete${triggerCase}" class="disableOnDisconnect btn btn-danger" onclick='triggerSaved(false); removeCaseRow("${triggerCase}"); addCaseAddButton("${triggerCase}");' style='float: right;'><i class='bi bi-trash'></i></button>
			</td>
		</tr>
		<tr>
			<td colspan="2">
				<div class='form-floating p-1'>
					<select id='triggerEntryCommandsetSelect${triggerCase}' class='disableOnDisconnect form-select border border-secondary commandsetSelect' onchange="triggerSaved(false);" value='${commandset}'>
					</select>
					<label for="triggerEntryCommandsetSelect${triggerCase}" lang-data="choose-commandset">${getLanguageAsText("choose-commandset")}</label>
				</div>
			</td>
			<td>
			</td>
		</tr>
	</table>
</td>`;
	//Adding element to document
	getElement("triggerEntryCaseCollection").appendChild(newTriggerEntryObj);

	//Adding dropdown options
	addCommandsToDropdown("triggerEntryCommandSelect" + triggerCase);
	getElement("triggerEntryCommandSelect" + triggerCase).value = command;

	addParameterToTriggerCaseCommand(triggerCase, command, parameter);

	addCommandsetsToDropdown("triggerEntryCommandsetSelect" + triggerCase, commandset);
}

function addParameterToTriggerCaseCommand(triggerCase, commandId, parameter) {
	let cell = getElement("triggerCaseCommand" + triggerCase + "ParameterCell");
	cell.innerHTML = "";
	//add element
	let div = document.createElement("div");
	div.id = "triggerEntryParameterInputDiv";
	div.className = "form-floating";

	if (commandId < 0 || commandId > commandCollection.length - 1) {
		return;
	} else if (commandCollection[commandId][1] == false) {
		return;
	} else if (commandCollection[commandId][1] == "text") {
		if (parameter == undefined) parameter = "";
		div.innerHTML = `<input id='triggerEntryCommand${triggerCase}ParameterInput' type='text' class='disableOnDisconnect form-control border border-secondary commandParameter' onkeyup='triggerSaved(false);' value='${parameter}' lang-data='parameter'>`;
	} else if (commandCollection[commandId][1] == "filemanager") {
		div.className += " w-75";
		div.innerHTML = `<input id='triggerEntryCommand${triggerCase}ParameterInput' type='text' class='disableOnDisconnect form-control border border-secondary commandParameter' onkeyup='triggerSaved(false);' value='${parameter}' lang-data='parameter'>`;
		let btn = document.createElement("button");
		btn.id = "triggerEntryCommandFileManagerButtonOpen";
		btn.onclick = () => showFileExplorerModal(commandCollection[commandId][2], false, getElement(`triggerEntryCommand${triggerCase}ParameterInput`));
		btn.className = "disableOnDisconnect btn btn-outline-success mt-2";
		btn.style.float = "right";
		btn.innerHTML = `<i class="bi bi-folder"></i>`;
		cell.appendChild(btn);
		if (parameter == undefined) parameter = "";
	} else if (Array.isArray(commandCollection[commandId][1])) {
		let htmlSelect = `<select id='triggerEntryCommand${triggerCase}ParameterInput' onchange='triggerSaved(false);' class='disableOnDisconnect form-select border border-secondary commandParameter' value='${commandCollection[commandId][1][0][1]}'>\n`;
		for (let i = 0; i < commandCollection[commandId][1].length; i++) {
			htmlSelect += `<option value='${commandCollection[commandId][1][i][0]}' lang-data='${commandCollection[commandId][1][i][1]}'>${getLanguageAsText(commandCollection[commandId][1][i][1])}</option>\n`;
		}
		htmlSelect += "</select>";
		div.innerHTML = htmlSelect;
		if (parameter == undefined) parameter = 0;
	}

	cell.appendChild(div);
	getElement("triggerEntryCommand" + triggerCase + "ParameterInput").value = parameter;

	//add label
	let label = document.createElement("label");
	label.htmlFor = "triggerEntryCommand" + triggerCase + "ParameterInput";
	label.setAttribute('lang-data', 'parameter');
	label.innerHTML = getLanguageAsText('parameter');
	div.appendChild(label);
}

function removeAllCaseAddButtons() {
	let caseList = document.getElementsByClassName("caseRow");
	for (let i = caseList.length - 1; i >= 0; i--) caseList[i].remove();
	getElement("triggerButtonAddCaseList").innerHTML = "";
}

function addAllCaseAddButton(triggerNumber) {
	for (let i = 0; i < triggerCollection[triggerNumber][1].length; i++) {
		addCaseAddButton(triggerCollection[triggerNumber][1][i]);
	}
}

function startupTriggerSaved(saved) {
	let saveButtonElement = getElement("startupTriggerSaveButton");
	let executeButtonElement = getElement("startupTriggerExecuteButton");
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

function triggerSaved(saved) {
	let saveButtonElement = getElement("triggerButtonSave");
	//let executeButtonElement = getElement("triggerExecuteButton");
	if (saved) {
		saveButtonElement.className = "disableOnDisconnect btn btn-success m-1";
		saveButtonElement.innerHTML = "<i class='bi bi-check2 pe-2'></i><span lang-data='saved'>" + getLanguageAsText("saved") + "</span>";
		//executeButtonElement.className = "disableOnDisconnect btn btn-outline-warning mt-2";
		//executeButtonElement.disabled = false;
	} else {
		saveButtonElement.className = "disableOnDisconnect btn btn-outline-success m-1";
		saveButtonElement.innerHTML = "<i class='bi bi-save pe-2'></i><span lang-data='save'>" + getLanguageAsText("save") + "</span>";
		//executeButtonElement.className = "btn btn-outline-warning mt-2";
		//executeButtonElement.disabled = true;
	}
}

function executeStartupTrigger() {
	getElement("executestartupTriggerSpinner").hidden = false;
	sendHTTPRequest('GET', 'cmd.php?id=23', true, () => getElement("executestartupTriggerSpinner").hidden = true);
}

function saveStartupTrigger() {
	if (startupTriggerIndex > -1) {
		if (getElement("startupTriggerCommandSelect").value == 0 && getElement("startupTriggerCommandsetSelect").value == 0) {//if no command or commandset selected, delete
			sendHTTPRequest('GET', 'cmd.php?id=20&cmd=delete&index=' + startupTriggerIndex, true, () => {startupTriggerSaved(true, 0);});
			startupTriggerIndex--;
			return;
		}
		sendHTTPRequest('GET', 'cmd.php?id=20&cmd=update&index=' + startupTriggerIndex + '&' + prepareStartupTriggerString(), true, () => {startupTriggerSaved(true, 0);});
		return;
	}
	sendHTTPRequest('GET', 'cmd.php?id=20&cmd=add&' + prepareStartupTriggerString(triggerId), true, () => {startupTriggerSaved(true, 0);});
	startupTriggerIndex++;
}

function saveTrigger() {
	let commandSelects = document.getElementsByClassName("commandSelect");
	let commandsetSelects = document.getElementsByClassName("commandsetSelect");
	let triggerParameter = document.getElementsByClassName("triggerParameter");
	let allCasesEmpty = true;
	let anyTriggerParameterEmpty = false;
	for (let i = 0; i < commandSelects.length; i++) {
		if (commandSelects[i].value != 0 || commandsetSelects[i].value != 0) allCasesEmpty = false;
	}
	for (let i = 0; i < triggerParameter.length; i++) {
		if (triggerParameter[i].value + "+" == "+") anyTriggerParameterEmpty = true;
	}
	if (getElement("triggerModalTitle").getAttribute("newtrigger") == "false") {//update
		if (anyTriggerParameterEmpty) {//if trigger paramter is missing
			showModal(getLanguageAsText("ups"), getLanguageAsText("fill-required-fields"), true, true, getLanguageAsText("ok"));
			return;
		}
		if (allCasesEmpty) {//if case is empty
			showModal(getLanguageAsText("allready-done"), getLanguageAsText("save-trigger-anyway"), true, true, getLanguageAsText("cancel"), 3, getLanguageAsText("save"), () => {sendHTTPRequest('GET', 'cmd.php?id=20&cmd=update&index=' + getElement("triggerId").innerText + '&' + prepareTriggerString(true), true, () => {modal.hide(); triggerModal.hide(); getScheduleFromServer();});});
			return;
		}
		sendHTTPRequest('GET', 'cmd.php?id=20&cmd=update&index=' + getElement("triggerId").innerText + '&' + prepareTriggerString(true), true, () => {triggerModal.hide(); getScheduleFromServer();});
		return;
	} else {//add
		if (anyTriggerParameterEmpty) {//if trigger paramter is missing
			showModal(getLanguageAsText("ups"), getLanguageAsText("fill-required-fields"), true, true, getLanguageAsText("ok"));
			return;
		}
		if (allCasesEmpty) {//if case is empty
			showModal(getLanguageAsText("allready-done"), getLanguageAsText("save-trigger-anyway"), true, true, getLanguageAsText("cancel"), 3, getLanguageAsText("save"), () => {sendHTTPRequest('GET', 'cmd.php?id=20&cmd=add&' + prepareTriggerString(), true, () => {modal.hide(); triggerModal.hide(); getScheduleFromServer();});});
			return;
		}
		sendHTTPRequest('GET', 'cmd.php?id=20&cmd=add&' + prepareTriggerString(), true, () => {triggerModal.hide(); getScheduleFromServer();});
	}
}

function prepareTriggerString(update=false) {//add or update
	let enabled = getElement("triggerEntryEnabledSwitchCheck").checked;
	let comment = getElement("triggerEntryDescription").value;
	let parameter = "";

	let msg = "enabled=" + enabled.toString().trim() + "&";
	let triggerCases = [];
	for (let i = 0; i < triggerCollection[getElement("triggerSelect").value][1].length; i++) triggerCases[i] = triggerCollection[getElement("triggerSelect").value][1][i];
	for (let i = 0; i < triggerCases.length; i++) {
		msg += "cases[" + i + "]=" + triggerCases[i] + "&";
		let command = getElement("triggerEntryCommandSelect" + triggerCases[i]) == null ? "" : getElement("triggerEntryCommandSelect" + triggerCases[i]).value;
		let commandset = getElement("triggerEntryCommandsetSelect" + triggerCases[i]) == null ? "" : getElement("triggerEntryCommandsetSelect" + triggerCases[i]).value;
		if (command != 0) msg += "command" + triggerCases[i] + "=" + triggerCases[i] + " " + command + "&";
		else {
			if (update) msg += "command" + triggerCases[i] + "=" + triggerCases[i] + " &";
		}
		if (getElement("triggerEntryCommand" + triggerCases[i] + "ParameterInput") != null) {
			parameter = getElement("triggerEntryCommand" + triggerCases[i] + "ParameterInput").value;
			parameter = parameter.replaceAll("%20", " ");
			parameter = parameter.replaceAll("\"", "\\\"");
			msg += "parameter" + triggerCases[i] + "=" + triggerCases[i] + " \"" + encodeURIComponent(parameter) + "\"&";
		} else {
			if (update) msg += "parameter" + triggerCases[i] + "=" + triggerCases[i] + " &";
		}
		if (commandset != 0) msg += "commandset" + triggerCases[i] + "=" + triggerCases[i] + " " + commandset + "&";
		else {
			if (update) msg += "commandset" + triggerCases[i] + "=" + triggerCases[i] + " &";
		}
	}
	let triggerParameters = document.getElementsByClassName("triggerParameter");
	for (let i = 0; i < triggerParameters.length; i++) msg += "triggerParameter[" + i + "]=" + triggerParameters[i].id.substring("triggerParameter".length) + " " + encodeURIComponent(triggerParameters[i].value) + "&";
	msg += "comment=\"" + encodeURIComponent(comment) + "\"&";
	msg += "trigger=" + getElement("triggerSelect").value;

	return msg;
}

function prepareStartupTriggerString(triggerCases=["true"]) {
	let enabled = getElement("startupTriggerEnabledSwitch").checked;
	let command = getElement("startupTriggerCommandSelect").value;
	let commandset = getElement("startupTriggerCommandsetSelect").value;
	let parameter = "";

	let msg = "enabled=" + enabled.toString().trim() + "&";

	for (let i = 0; i < triggerCases.length; i++) {
		msg += "cases[" + i + "]=" + triggerCases[i] + "&";
		if (command != 0) msg += "command" + triggerCases[i] + "=" + triggerCases[i] + " " + command + "&";
		else msg += "command" + triggerCases[i] + "=" + triggerCases[i] + " &";
		if (getElement("startupTriggerParameterInput") != null) {
			let parameterElement = getElement("startupTriggerParameterInput");
			parameter = parameterElement.value;
			parameter = parameter.replaceAll("%20", " ");
			parameter = parameter.replaceAll("\"", "\\\"");
			msg += "parameter" + triggerCases[i] + "=" + triggerCases[i] + " \"" + encodeURIComponent(parameter) + "\"&";
		} else msg += "parameter" + triggerCases[i] + "=" + triggerCases[i] + " &";
		if (commandset != 0) msg += "commandset" + triggerCases[i] + "=" + triggerCases[i] + " " + commandset + "&";
		else msg += "commandset" + triggerCases[i] + "=" + triggerCases[i] + " &";
	}

	msg += "trigger=1";

	return msg;
}

function deleteTrigger(triggerEntryId) {
	sendHTTPRequest('GET', 'cmd.php?id=20&cmd=delete&index=' + getElement("triggerId").innerText, true, () => {triggerModal.hide(); getScheduleFromServer();});
}

////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////   commandset functions   //////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////

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
	getElement("commandsetModalTitle").innerHTML = `<i class="bi bi-terminal bigIcon pe-2"></i><span lang-data="commandset">${getLanguageAsText("commandset")}</span>: <span id='currentScheduleEntryId'>${obj.name}</span>`;
	getElement("commandsetModalBody").innerHTML = `<table id="commandsetEntryCommandCollection" style='width: 100%;'>
		<tr>
			<td style='width: 50%;'>
				<div class='form-floating mb-3'>
					<input id='commandsetEntryName' type='text' class='disableOnDisconnect form-control border border-secondary' value='${obj.name}' onkeyup='commandsetEntrySaved(false); showCommandsetEntryTitle();'>
					<label for='commandsetEntryName' lang-data='description'>${getLanguageAsText("description")}</label>
				</div>
			</td>
			<td colspan="2" style='width: 50%;'>
				<span class='ms-2'>ID: </span><span id='commandsetId'>${commandsetId}</span>
				<button id="commandsetEntryButtonExecute" class="disableOnDisconnect btn btn-outline-warning mb-3" onclick='executeCommandsetEntry(${commandsetId});' style='float: right;'><i class='bi bi-play pe-2'></i><span id='commandsetEntryButtonExecuteSpinner' class='spinner-border spinner-border-sm' role='status' hidden='true'></span><span lang-data="execute">${getLanguageAsText("execute")}</span></button>
			</td>
		</tr>
	</table>
<button id='commandEntryButtonNew' class='disableOnDisconnect btn btn-outline-success mt-2' onclick='commandsetEntrySaved(false); addCommandToCommandset();'><i class='bi bi-plus-lg pe-2'></i><span lang-data='new-command'>${getLanguageAsText("new-command")}</span></button>`;
	
	for (let i = 0; i < obj.commands.length; i++) {
		addCommandToCommandset(obj.commands[i].command, obj.commands[i].parameter == undefined ? "" : obj.commands[i].parameter);
	}
	commandsetModal.show();
	enableElements(prevItemsEnabled);
	commandsetEntrySaved(commandsetId >= 0);
}

function executeCommandsetEntry() {
	getElement("commandsetEntryButtonExecuteSpinner").hidden = false;
	sendHTTPRequest('GET', 'cmd.php?id=19&cmd=execute&commandsetid=' + getCommandsetId(), true, () => getElement("commandsetEntryButtonExecuteSpinner").hidden = true);
}

function commandsetEntrySaved(saved) {
	let commandsetEntryButtonElement = getElement("commandsetEntryButtonExecute");
	if (saved) {
		commandsetEntryButtonElement.className = "disableOnDisconnect btn btn-outline-warning mt-2";
		if (prevItemsEnabled) commandsetEntryButtonElement.disabled = false;
	} else {
		commandsetEntryButtonElement.className = "btn btn-outline-warning mt-2";
		commandsetEntryButtonElement.disabled = true;
	}
}

function addCommandToCommandset(command=0, parameter="") {
	let commandId = commandsetCommandCount;
	let newCommandEntryObj = document.createElement('tr');
	newCommandEntryObj.className = "border-top border-bottom border-primary commandrow";
	newCommandEntryObj.innerHTML = `<td class='p-2' style='width: 50%;'>
	<div class='form-floating'>
		<select id='commandsetEntryCommandSelect${commandId}' class='disableOnDisconnect form-select border border-secondary commandSelect' onchange='commandsetEntrySaved(false); addParameterToCommandsetEntryCommand(${commandId}, value);'>
		</select>
		<label for="commandsetEntryCommandSelect${commandId}" lang-data="choose-command">${getLanguageAsText("choose-command")}</label>
	</div>
</td>
<td id='commandsetEntryCommand${commandId}ParameterCell' class='p-2' style='width: 40%;'>
</td>
<td class='p-2' style='width: 10%;'>
	<button id="commandsetEntryCommandButtonDelete" class="disableOnDisconnect btn btn-danger" onclick='commandsetEntrySaved(false); deleteCommandFromCommandset(this);' style='float: right;'><i class='bi bi-trash'></i></button>
</td>
`;
	//Adding element to document
	getElement("commandsetEntryCommandCollection").appendChild(newCommandEntryObj);

	//Adding dropdown options
	addCommandsToDropdown("commandsetEntryCommandSelect" + commandId);
	getElement("commandsetEntryCommandSelect" + commandId).value = command;

	addParameterToCommandsetEntryCommand(commandId, command, parameter);

	commandsetCommandCount++;
}

function addParameterToCommandsetEntryCommand(commandEntryId, commandId, parameter) {
	let cell = getElement("commandsetEntryCommand" + commandEntryId + "ParameterCell");
	cell.innerHTML = "";
	//add element
	let div = document.createElement("div");
	div.id = "commandsetEntryParameterInputDiv";
	div.className = "form-floating";

	if (commandId < 0 || commandId > commandCollection.length - 1) {
		return;
	} else if (commandCollection[commandId][1] == false) {
		return;
	} else if (commandCollection[commandId][1] == "text") {
		if (parameter == undefined) parameter = "";
		div.innerHTML = `<input id='commandsetEntryCommand${commandEntryId}ParameterInput' type='text' class='disableOnDisconnect form-control border border-secondary commandParameter' onkeyup='commandsetEntrySaved(false);' value='${parameter}' lang-data='parameter'>`;
	} else if (commandCollection[commandId][1] == "filemanager") {
		div.className += " w-75";
		div.innerHTML = `<input id='commandsetEntryCommand${commandEntryId}ParameterInput' type='text' class='disableOnDisconnect form-control border border-secondary commandParameter' onkeyup='startupTriggerSaved(false);' value='${parameter}' lang-data='parameter'>`;
		let btn = document.createElement("button");
		btn.id = "commandsetEntryCommandFileManagerButtonOpen";
		btn.onclick = () => showFileExplorerModal(commandCollection[commandId][2], false, getElement(`commandsetEntryCommand${commandEntryId}ParameterInput`));
		btn.className = "disableOnDisconnect btn btn-outline-success mt-2";
		btn.style.float = "right";
		btn.innerHTML = `<i class="bi bi-folder"></i>`;
		cell.appendChild(btn);
		if (parameter == undefined) parameter = "";
	} else if (Array.isArray(commandCollection[commandId][1])) {
		let htmlSelect = `<select id='commandsetEntryCommand${commandEntryId}ParameterInput' onchange='commandsetEntrySaved(false);' class='disableOnDisconnect form-select border border-secondary commandParameter' value='${commandCollection[commandId][1][0][1]}'>\n`;
		for (let i = 0; i < commandCollection[commandId][1].length; i++) {
			htmlSelect += `<option value='${commandCollection[commandId][1][i][0]}' lang-data='${commandCollection[commandId][1][i][1]}'>${getLanguageAsText(commandCollection[commandId][1][i][1])}</option>\n`;
		}
		htmlSelect += "</select>";
		div.innerHTML = htmlSelect;
		if (parameter == undefined) parameter = 0;
	}

	cell.appendChild(div);
	getElement("commandsetEntryCommand" + commandEntryId + "ParameterInput").value = parameter;

	//add label
	let label = document.createElement("label");
	label.htmlFor = "commandsetEntryCommand" + commandEntryId + "ParameterInput";
	label.setAttribute('lang-data', 'parameter');
	label.innerHTML = getLanguageAsText('parameter');
	div.appendChild(label);
}

function saveCommandsetEntry() {
	let commandsetEntryNameElement = getElement("commandsetEntryName");
	if (commandsetEntryNameElement.value == "") {
		commandsetEntryNameElement.className = "disableOnDisconnect form-control border border-danger";
		return;
	}

	let sendString = prepareCommandsetString(commandsetEntryNameElement.value);
	if (getCommandsetId() < 0) {//add
		sendHTTPRequest('GET', 'cmd.php?id=19&cmd=add&' + sendString, true, () => {commandsetModal.hide(); getScheduleFromServer();});
	} else {//update
		sendHTTPRequest('GET', 'cmd.php?id=19&cmd=update&commandsetid=' + getCommandsetId() + '&' + sendString, true, () => {commandsetModal.hide(); getScheduleFromServer();});
	}
}

function deleteCommandFromCommandset(commandEntry) {
	getElement(commandEntry.parentElement.parentElement.remove());
}

function deleteCommandsetEntry() {
	if (getCommandsetId() < 0) {// < 0 is unsaved, > 0 is saved
		commandsetModal.hide();
	} else {
		sendHTTPRequest('GET', 'cmd.php?id=19&cmd=delete&commandsetid=' + getCommandsetId(), true, () => {commandsetModal.hide(); getScheduleFromServer();});
	}
}

function prepareCommandsetString(commandsetName) {
	let msg = "name=\"" + commandsetName + "\"&";
	let commandEntries = getElement("commandsetEntryCommandCollection").getElementsByClassName("commandrow");
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

////////////////////////////////////////////////////////////////////////////////////////////////////
/////////////////////////////////   commandset helper functions   //////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////

function commandsetExists(commandsetId) {
	return undefined != getCommandsetName(commandsetId);
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

////////////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////   update functions   ////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////

function checkForUpdate() {
	let requestedUrl = "cmd.php?id=6";
	let xmlhttp = new XMLHttpRequest();
	xmlhttp.timeout = 5000;//longer timeout as usual
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

////////////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////   import / export functions   ///////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////

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

////////////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////   file explorer functions   ////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////

function showFileExplorerModal(selectedMode=modeVLC, multiselect=true, returnElement=null, forceMode=true) {
	let modeButtons = document.getElementsByClassName("fileExplorerModeButton");
	for (let i = 0; i < modeButtons.length; i++) modeButtons[i].disabled = false; //enable all elements, to select the correct one
	getElement("fileExplorerMode" + selectedMode).click(); //select the correct mode
	if (forceMode) { //disable all elements, except the correct one
		for (let i = 0; i < modeButtons.length; i++) modeButtons[i].disabled = true;
	}
	getElement("fileExplorerModal").setAttribute("multiselect", multiselect.toString());
	if (returnElement == null) {
		getElement("fileExplorerFooter").innerHTML = `<button class='btn btn-secondary' data-bs-dismiss='modal' lang-data='ok'>${getLanguageAsText("ok")}</button>`;
	} else {
		getElement("fileExplorerFooter").innerHTML = `<button class='btn btn-outline-light' data-bs-dismiss='modal' lang-data='cancel'>${getLanguageAsText("cancel")}</button>
<button class='btn btn-outline-success' onclick="applySelectedFile();" data-bs-dismiss='modal' lang-data='apply'>${getLanguageAsText("apply")}</button>`;
	}
	fileExplorerReturnElement = returnElement;
	getElement("fileExplorerExecuteFile").disabled = true;
	fileExplorerModal.show();
}

function changeFileExplorerMode(mode) {
	currentFileExplorerMode = mode;
	let modeButtons = document.getElementsByClassName("fileExplorerModeButton");
	for (let i = 0; i < modeButtons.length; i++) modeButtons[i].classList.remove("active");
	getElement("fileExplorerMode" + mode).classList.add("active");
	getElement("fileExplorerRootFolder").innerText = modes[mode];

	getFilesInFolder();
}

function getFilesInFolder() {
	let requestedUrl = "cmd.php?id=24&mode=" + currentFileExplorerMode;
	let xmlhttp = new XMLHttpRequest();
	xmlhttp.timeout = timeoutTime;
	xmlhttp.ontimeout = () => {showServerError("Timeout error", requestedUrl);};
	xmlhttp.onloadend = function() {
		if (!serverExecutedSuccessfully(xmlhttp.responseText)) {
			showServerError("Error while getting display protocol", requestedUrl);
			return;
		}
		getElement("fileExplorerFileCollection").innerHTML = "";
		let files = parseReturnValuesFromServer(xmlhttp.responseText);
		if (files + "+" == "+") return;
		for (let i = 0; i < files.length; i++) {
			let icon = "";
			switch (files[i].split(".")[files[i].split(".").length - 1]) {
				case "jpg":
				case "jpeg":
				case "png":
				case "svg":
				case "gif":
				case "bmp":
					icon = "file-earmark-image";
					break;
				case "mp4":
				case "mov":
				case "wmv":
					icon = "file-earmark-play";
					break;
				case "mp3":
				case "wav":
				case "wma":
					icon = "file-earmark-music";
					break;
				case "ppt":
				case "pptx":
					icon = "file-earmark-easel";
					break;
				case "pdf":
					icon = "file-earmark-pdf";
					break;
				case "json":
					icon = "file-earmark-code";
					break;
				default:
					icon = "file-earmark";
					break;
			}
			let fileItem = document.createElement("div");
			fileItem.className = "col";
			fileItem.innerHTML = `<div class='card border-0 mode${currentFileExplorerMode}' fileexplorerfileselected='false' onclick='selectFileItem(this)' ondblclick="showRenameModal(this);" onmouseover='this.style.opacity = 0.7;' onmouseleave='this.style.opacity = 1;'>
	<svg class="bi ${isInDarkmode() ? "text-white" : "text-dark"}" role="img" width="100%" height="100%" fill="currentColor"><use xlink:href="/bootstrap/icons/bootstrap-icons.svg#${icon}"/></svg>
	<figcaption class='text-center mt-1 card-text' style='cursor: default;'>
		${files[i]}
	</figcaption>
</div>`;
			getElement("fileExplorerFileCollection").appendChild(fileItem);
		}
	}
	xmlhttp.open('GET', requestedUrl, true);
	xmlhttp.send();
}

function selectFileItem(element) {
	if (getElement("fileExplorerModal").getAttribute("multiselect") == "true") {
		fileExplorerSelectSingleFile(element, element.getAttribute("fileexplorerfileselected") == "false");
	} else if (getElement("fileExplorerModal").getAttribute("multiselect") == "false") {
		let elementsInCurrentMode = document.getElementsByClassName("mode" + currentFileExplorerMode);
		for (let i = 0; i < elementsInCurrentMode.length; i++) {
			fileExplorerSelectSingleFile(elementsInCurrentMode[i], false);
		}
		fileExplorerSelectSingleFile(element, true);
	}
	disableExecuteFileExplorerFile();
}

function fileExplorerSelectSingleFile(element, select=true) {//when false, unselect
	if (select) {
		element.classList.remove("border-0");
		element.classList.add("border");
		element.classList.add("border-primary");
		element.setAttribute("fileexplorerfileselected", "true");
	} else {
		element.classList.add("border-0");
		element.classList.remove("border");
		element.classList.remove("border-primary");
		element.setAttribute("fileexplorerfileselected", "false");
	}
}

function applySelectedFile() {
	let elementsInCurrentMode = document.getElementsByClassName("mode" + currentFileExplorerMode);
	for (let i = 0; i < elementsInCurrentMode.length; i++) {
		if (elementsInCurrentMode[i].getAttribute("fileexplorerfileselected") == "true") {
			fileExplorerReturnElement.value = "/srv/piScreen/admin/data/" + modes[currentFileExplorerMode] + "/" + elementsInCurrentMode[i].children[1].innerText;
		}
	}
}

function selectFileToUpload() {
	let input = document.createElement('input');
	input.type = 'file';
	input.onchange = e => {
		let file = e.target.files[0];
		var formData = new FormData();
		formData.append("file", file);
		var xmlhttp = new XMLHttpRequest();
		xmlhttp.onloadend = () => {getFilesInFolder(currentFileExplorerMode)};
		xmlhttp.open("POST", 'cmd.php?id=25&mode=' + currentFileExplorerMode, true);
		xmlhttp.send(formData);
	}
	input.click();
}

function deleteSelectedFiles() {
	let fileElements = document.querySelectorAll("[fileexplorerfileselected='true']");
	for (let i = 0; i < fileElements.length; i++) deleteFile(fileElements[i].children[1].innerText);
}

function deleteFile(filename) {
	sendHTTPRequest("GET", 'cmd.php?id=26&mode=' + currentFileExplorerMode + '&filename=' + filename, true, () => {getFilesInFolder(currentFileExplorerMode)});
}

function showRenameModal(element) {
	currentRenameFile = element;
	let filename = element.children[1].innerText;
	getElement("renameTextfield").value = filename;
	getElement("renameOldName").innerText = filename;
	renameModal.show();
	//getElement("renameTextfield").focus();
}

function saveFileRename() {
	let oldName = getElement("renameOldName").innerText;
	if (oldName == getElement("renameTextfield").value) {
		renameModal.hide();
		return;
	}

	let requestedUrl = 'cmd.php?id=27&mode=' + currentFileExplorerMode + '&oldfilename=' + oldName + '&newfilename=' + getElement("renameTextfield").value;
	let xmlhttp = new XMLHttpRequest();
	xmlhttp.timeout = timeoutTime;
	xmlhttp.ontimeout = () => {showServerError("Timeout error", requestedUrl);};
	xmlhttp.onloadend = () => {
		if (serverExecutedSuccessfully(xmlhttp.responseText)) {
			currentRenameFile.children[1].innerText = getElement("renameTextfield").value;
			renameModal.hide();
		}
		else showServerError(parseReturnValuesFromServer(xmlhttp.responseText), requestedUrl);
	}
	xmlhttp.open('GET', requestedUrl, true);
	xmlhttp.send();

}

function dropFileIntoFileExplorer(ev) {
	ev.preventDefault();
	let file = ev.dataTransfer.files[0];
	var formData = new FormData();
	formData.append("file", file);
	var xmlhttp = new XMLHttpRequest();
	xmlhttp.onloadend = () => {getFilesInFolder(currentFileExplorerMode)};
	xmlhttp.open("POST", 'cmd.php?id=25&mode=' + currentFileExplorerMode, true);
	xmlhttp.send(formData);
}

function disableExecuteFileExplorerFile() {
	let selectedElements = document.querySelectorAll("[fileexplorerfileselected='true']");
	if (selectedElements.length > 1 || selectedElements.length == 0) {
		getElement("fileExplorerExecuteFile").disabled = true;
		return;
	}
	getElement("fileExplorerExecuteFile").disabled = false;
}

function executeFileExplorerFile() {
	let selectedElement = document.querySelector("[fileexplorerfileselected='true']");
	let commandId = 0;
	if (currentFileExplorerMode == modeFirefox) commandId = 40;
	else if (currentFileExplorerMode == modeVLC) commandId = 50;
	else if (currentFileExplorerMode == modeImpress) commandId = 60;
	else {
		showModal(getLanguageAsText("error"), getLanguageAsText("execute-mode-general-disabled"), true, true, getLanguageAsText("ok"));
		return;
	}
	getElement("fileExplorerExecuteFileSpinner").hidden = false;
	sendHTTPRequest("GET", 'cmd.php?id=35&commandid=' + commandId + '&parameter=\"/srv/piScreen/admin/data/' + modes[currentFileExplorerMode] + "/" + selectedElement.children[1].innerText + "\"", true, () => {getElement("fileExplorerExecuteFileSpinner").hidden = true;});
}

////////////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////   screenshot modal functions   //////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////

function showScreenshotModal() {
	getElement("screenshotFull").src = "piScreenScreenshot.jpg?t=" + new Date().getTime();
	screenshotModal.show();
}

////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////   click events   //////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////

function restartBrowser() {
	getElement("restartBrowserSpinner").hidden = false;
	sendHTTPRequest('GET', 'cmd.php?id=1&cmd=restart', true, () => {getElement("restartBrowserSpinner").hidden = true;});
}

function refreshBrowserPage() {
	getElement("refreshBrowserPageSpinner").hidden = false;
	sendHTTPRequest('GET', 'cmd.php?id=1&cmd=refresh', true, () => {getElement("refreshBrowserPageSpinner").hidden = true;});
}

function restartVlcVideo() {
	getElement("restartVlcSpinner").hidden = false;
	sendHTTPRequest('GET', 'cmd.php?id=28&cmd=restart', true, () => {getElement("restartVlcSpinner").hidden = true;});
}

function playVlcVideo() {
	getElement("playVlcSpinner").hidden = false;
	sendHTTPRequest('GET', 'cmd.php?id=28&cmd=play', true, () => {getElement("playVlcSpinner").hidden = true;});
}

function pauseVlcVideo() {
	getElement("pauseVlcSpinner").hidden = false;
	sendHTTPRequest('GET', 'cmd.php?id=28&cmd=pause', true, () => {getElement("pauseVlcSpinner").hidden = true;});
}

function setVlcVolume(volume) {
	sendHTTPRequest('GET', 'cmd.php?id=28&cmd=volume&value=' + volume, true, () => {volumeSaved(true);});
}

function restartImpress() {
	getElement("restartImpressSpinner").hidden = false;
	sendHTTPRequest('GET', 'cmd.php?id=29', true, () => {getElement("restartImpressSpinner").hidden = true;});
}

function restartHost() {
	showModal(getLanguageAsText('attention'), getLanguageAsText('reboot-really'), undefined, undefined, undefined, 4, getLanguageAsText('restart-device'), () => {sendHTTPRequest('GET', 'cmd.php?id=2', false, () => {}); modal.hide();});
}

function shutdownHost() {
	showModal(getLanguageAsText('attention'), getLanguageAsText('shutdown-really'), undefined, undefined, undefined, 4, getLanguageAsText('shutdown-device'), () => {sendHTTPRequest('GET', 'cmd.php?id=3', false, () => {}); modal.hide();});
}

function setDisplayOn() {
	sendHTTPRequest('GET', 'cmd.php?id=8&cmd=1', true, () => {getElement("spinnerDisplayOn").hidden = false;});
}

function setDisplayOff() {
	sendHTTPRequest('GET', 'cmd.php?id=8&cmd=0', true, () => {getElement("spinnerDisplayOff").hidden = false;});
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

function showColorPicker(colorCode) {
	colorPickerElement.value = "#" + colorCode;
	colorPickerElement.click();
}

////////////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////   event listener   /////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////

getElement("collapseMainSettings").addEventListener("shown.bs.collapse", event => {
	rearrangeGui();
});

getElement("collapseLoginSettings").addEventListener("shown.bs.collapse", event => {
	rearrangeGui();
});

getElement("timeActionsCarousel").addEventListener("slide.bs.carousel", event => {
	organizerSwitchRadio(event.to);
});

getElement("cronEditorCarousel").addEventListener("slide.bs.carousel", event => {
	cronEditorCarouselSwitchRadio(event.to);
});

getElement("cronEditorModal").addEventListener("hidden.bs.modal", event => {
	scheduleModal.show();
});

getElement("scheduleModal").addEventListener("shown.bs.modal", event => {
	cronEntryError(getElement("cronentry"));
});

getElement("screenshotModal").addEventListener("hidden.bs.modal", event => {
	screenshotModalShown = false;
});

getElement("screenshotModal").addEventListener("shown.bs.modal", event => {
	screenshotModalShown = true;
});

////////////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////   functionallity functions   ///////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////

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

function showDesktopSettings() {
	let requestedUrl = "cmd.php?id=30";
	let xmlhttp = new XMLHttpRequest();
	xmlhttp.timeout = timeoutTime;
	xmlhttp.ontimeout = () => {showServerError("Timeout error", requestedUrl);};
	xmlhttp.onloadend = function() {
		if (!serverExecutedSuccessfully(xmlhttp.responseText)) {
			console.log(xmlhttp.responseText);
			showServerError("Error while setting display orientation select", requestedUrl);
			return;
		}
		desktopConfig = JSON.parse(parseReturnValuesFromServer(xmlhttp.responseText)[0]);
		getElement("backgroundSelect").value = desktopConfig.wallpaper_mode;
		showSettingsFileExplorerButton();
	}
	xmlhttp.open('GET', requestedUrl, true);
	xmlhttp.send();
}

function showSettingsFileExplorerButton() {
	if (getElement("backgroundSelect").value == "color") {
		getElement("fileExplorerBackgroundButton").hidden = true;
		getElement("backgroundColorPickerButton").hidden = false;
		getElement("setBackgroundInputTextfield").value = desktopConfig.desktop_bg.toString().substring(1);
	} else {
		getElement("fileExplorerBackgroundButton").hidden = false;
		getElement("backgroundColorPickerButton").hidden = true;
		getElement("setBackgroundInputTextfield").value = desktopConfig.wallpaper;
	}
}

function deleteBackground() {
	getElement("backgroundSelect").value = "color";
	getElement("setBackgroundInputTextfield").value = "";
	settingSaved("settingsButtonSaveBackground", false);
}

function saveBackground() {
	let mode = getElement("backgroundSelect").value;
	let val = getElement("setBackgroundInputTextfield").value;
	if (val + "+" == "+") val = "000000";
	if (desktopConfig.wallpaper_mode != mode) sendHTTPRequest('GET', 'cmd.php?id=31&mode=' + mode, true, () => {settingSaved("settingsButtonSaveBackground", true); showDesktopSettings();});
	if (mode == "color") {
		if (desktopConfig.desktop_bg.toString().substring(1) != val) sendHTTPRequest('GET', 'cmd.php?id=32&color=' + val, true, () => {settingSaved("settingsButtonSaveBackground", true); showDesktopSettings();});
	} else {
		if (desktopConfig.wallpaper != val) sendHTTPRequest('GET', 'cmd.php?id=33&path=' + val, true, () => {settingSaved("settingsButtonSaveBackground", true); showDesktopSettings();});
	}
}

function volumeSaved(saved) {
	modifiedVlcVolume = !saved;
	let element = getElement("vlcVolumeSetButton");
	if (saved) {
		element.className = "disableOnDisconnect btn btn-primary w-100";
		element.innerHTML = "<i class='bi bi-check2 pe-2'></i><span lang-data='set-volume-vlc'>" + getLanguageAsText("set-volume-vlc") + "</span>";
	} else {
		element.className = "disableOnDisconnect btn btn-outline-primary w-100";
		element.innerHTML = "<i class='bi bi-save pe-2'></i><span lang-data='set-volume-vlc'>" + getLanguageAsText("set-volume-vlc") + "</span>";
	}
}

function ignoreCronDateDelete() {
	getElement("ignoreTimeScheduleStartDateTime").value = "";
	getElement("ignoreTimeScheduleEndDateTime").value = "";
}

function ignoreCronDateChanged() {
	getElement("ignoreTimeScheduleSave").className = "disableOnDisconnect btn btn-outline-success ms-3 mb-3";
	getElement("ignoreTimeScheduleSave").innerHTML = "<i class='bi bi-save'></i>"
}

function setIgnoreCron() {
	let startDateTime = getElement("ignoreTimeScheduleStartDateTime").value;
	let endDateTime = getElement("ignoreTimeScheduleEndDateTime").value;
	if (startDateTime + "+" == "+" && endDateTime + "+" == "+") {
		sendHTTPRequest('GET', 'cmd.php?id=34&fromto=\" \"', true, () => {getElement("ignoreTimeScheduleSave").className = "disableOnDisconnect btn btn-success ms-3 mb-3"; getElement("ignoreTimeScheduleSave").innerHTML = "<i class='bi bi-check2'></i>"}, true);
		return;
	}
	if (startDateTime > endDateTime) {
		showModal(getLanguageAsText("error"), getLanguageAsText("ignore-timeschedule-wrong-sequence"), true, true, getLanguageAsText("ok"));
		return;
	}
	if (startDateTime + "+" == "+" || endDateTime + "+" == "+") {
		showModal(getLanguageAsText("error"), getLanguageAsText("ignore-timeschedule-data-missing"), true, true, getLanguageAsText("ok"));
		return;
	}
	let fromTo = startDateTime.replace("T", " ") + " " + endDateTime.replace("T", " ");
	sendHTTPRequest('GET', 'cmd.php?id=34&fromto=\"' + fromTo + "\"", true, () => {getElement("ignoreTimeScheduleSave").className = "disableOnDisconnect btn btn-success ms-3 mb-3"; getElement("ignoreTimeScheduleSave").innerHTML = "<i class='bi bi-check2'></i>"}, true);
}

////////////////////////////////////////////////////////////////////////////////////////////////////
/////////////////////////////////////   organizer functions   //////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////

function organizerSwitchRadio(id) {
	for (let i = 0; i < 3; i++) getElement("plannerOption" + i).className = "btn btn-secondary w-100 mb-4";
	getElement("plannerOption" + id).className = "btn btn-primary w-100 mb-4";
}

////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////   on window load   ////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////

window.onload = function() {
	setDarkMode(window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches);
	getDefaultLanguage();
	setDisplayProtocolSelect();
	setDisplayOrientationSelect();
	showDesktopSettings();

	let st = null; //screenshotTime
	let idleBadge = getElement("idle");
	let active = getElement("active");
	let displayState = getElement("displayState");
	let displayOnBtn = getElement("displayOnButton");
	let displayOffBtn = getElement("displayOffBtn");

	let requestedUrl = 'cmd.php?id=5';
	let xmlhttp = new XMLHttpRequest();
	xmlhttp.open('GET', requestedUrl, true);
	xmlhttp.timeout = 1900; //has to be shorter than the interval time
	xmlhttp.ontimeout = () => {showServerError("Timeout error", requestedUrl);};
	//load periodical the current infos about the system
	xmlhttp.onload = () => {
		if (splashscreenActive) {
			showSplashscreen(false);
			splashscreenActive = false;
		}
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
		getElement("modeBadge").innerHTML = modes[jsonData.modeInfo.mode];
		getElement("displayResolution").innerHTML = jsonData.resolution;
		switch (jsonData.displayState) {
			case "on":
				displayState.classList = "badge rounded-pill bg-success";
				displayState.innerHTML = getLanguageAsText('on');
				displayOnBtn.parentElement.hidden = true;
				displayOffBtn.parentElement.hidden = false; 
				break;
			case "off":
				displayState.classList = "badge rounded-pill bg-danger";
				displayState.innerHTML = getLanguageAsText('off');
				displayOnBtn.parentElement.hidden = false;
				displayOffBtn.parentElement.hidden = true; 
				break;
			default:
				displayState.classList = "badge rounded-pill bg-secondary";
				displayState.innerHTML = getLanguageAsText('unknown');
				displayOnBtn.parentElement.hidden = false;
				displayOffBtn.parentElement.hidden = false; 
				break;
		}
		getElement("uptime").innerHTML = jsonData.uptime.days + " " + getLanguageAsText('days') + ", " + jsonData.uptime.hours + " " + getLanguageAsText('hours') + ", " + jsonData.uptime.mins + " " + getLanguageAsText('minutes');
		getElement("cpuLoad").innerHTML = jsonData.cpuLoad;
		getElement("cpuTemp").innerHTML = Math.round(jsonData.cpuTemp / 1000) + " °C";
		getElement("ramUsed").innerHTML = Number(jsonData.ramUsed / 1000 / 1000).toFixed(2) + " GiB";
		getElement("ramTotal").innerHTML = Number(jsonData.ramTotal / 1000 / 1000).toFixed(2) + " GiB";
		getElement("ramUsage").innerHTML = Number(jsonData.ramUsed / jsonData.ramTotal * 100).toFixed(2);
		getElement("spinnerDisplayOn").hidden = !jsonData.display.onSet;
		getElement("spinnerDisplayOff").hidden = !jsonData.display.standbySet;
		if (new Date(jsonData.screenshotTime * 1000) != st) {
			st = new Date(jsonData.screenshotTime * 1000);
			getElement("screenshotTime").innerHTML = `${addLeadingZero(st.getDate())}.${addLeadingZero(st.getMonth() + 1)}.${1900 + st.getYear()} - ${addLeadingZero(st.getHours())}:${addLeadingZero(st.getMinutes())}:${addLeadingZero(st.getSeconds())}`;
			getElement("screenshot").src = "piScreenScreenshot-thumb.jpg?t=" + new Date().getTime();
			
			if (currentMode != jsonData.modeInfo.mode) changeMode(jsonData.modeInfo);

			switch (jsonData.modeInfo.mode) {
				case modeFirefox:
					getElement("screenContent").innerHTML = jsonData.modeInfo.info.url;
					getElement("currentVideoTimeTable").hidden = true;
					getElement("screenVlcAudioInfo").hidden = true;
					break;
				case modeVLC:
					getElement("screenContent").innerHTML = jsonData.modeInfo.info.source.split("/")[jsonData.modeInfo.info.source.split("/").length - 1];
					getElement("currentVideoTimeTable").hidden = false;
					getElement("screenVlcAudioInfo").hidden = false;
					getElement("currentVideoTime").innerHTML = msToTime(jsonData.modeInfo.info.time);
					getElement("totalVideoTime").innerHTML = msToTime(jsonData.modeInfo.info.length);
					getElement("infoVideoProgressbar").style.width = (jsonData.modeInfo.info.time / jsonData.modeInfo.info.length * 100).toFixed() + "%";
					if (!modifiedVlcVolume) {
						getElement("vlcVolumeRange").value = jsonData.modeInfo.info.volume;
						getElement('vlcVolumeNumber').innerHTML = getElement("vlcVolumeRange").value + '%';
					}

					if (prevVlcVideoState != jsonData.modeInfo.info.state) {
						if (jsonData.modeInfo.info.state == "State.Paused") {
							getElement("infoVideoProgressbar").classList.remove("progress-bar-animated");
							getElement("videoControlDiv").innerHTML = `<button class='disableOnDisconnect btn btn-success w-100' onclick='playVlcVideo();'><span id='playVlcSpinner' class='spinner-border spinner-border-sm' role='status' hidden=''></span> <i class='bi bi-play btn-icon-xxl'></i><br><span lang-data='play-vlc-video'>${getLanguageAsText("play-vlc-video")}</span></button>`;
						} else if (jsonData.modeInfo.info.state == "State.Playing") {
							getElement("infoVideoProgressbar").classList.add("progress-bar-animated");
							getElement("videoControlDiv").innerHTML = `<button class='disableOnDisconnect btn btn-danger w-100' onclick='pauseVlcVideo();'><span id='pauseVlcSpinner' class='spinner-border spinner-border-sm' role='status' hidden=''></span> <i class='bi bi-pause btn-icon-xxl'></i><br><span lang-data='pause-vlc-video'>${getLanguageAsText("pause-vlc-video")}</span></button>`;
						}
					}

					prevVlcVideoState = jsonData.modeInfo.info.state;
					break;
				case modeImpress:
					getElement("screenContent").innerHTML = jsonData.modeInfo.info.file.split("/")[jsonData.modeInfo.info.file.split("/").length - 1];
					getElement("currentVideoTimeTable").hidden = true;
					getElement("screenVlcAudioInfo").hidden = true;
					break;
			}
			
			if (screenshotModalShown) {
				getElement("screenshotFull").src = "piScreenScreenshot.jpg?t=" + new Date().getTime();
				getElement("screenshotFullTime").innerHTML = `${addLeadingZero(st.getDate())}.${addLeadingZero(st.getMonth() + 1)}.${1900 + st.getYear()} - ${addLeadingZero(st.getHours())}:${addLeadingZero(st.getMinutes())}:${addLeadingZero(st.getSeconds())}`;
				switch (jsonData.modeInfo.mode) {
					case modeFirefox:
						getElement("screenFullContent").innerHTML = jsonData.modeInfo.info.url;
						break;
					case modeVLC:
						getElement("screenFullContent").innerHTML = jsonData.modeInfo.info.source.split("/")[jsonData.modeInfo.info.source.split("/").length - 1];
						break;
					case modeImpress:
						getElement("screenFullContent").innerHTML = jsonData.modeInfo.info.file.split("/")[jsonData.modeInfo.info.file.split("/").length - 1];
						break;
				}
				getElement("screenFullContent").innerHTML = getElement("screenFullContent").innerHTML.replaceAll("%20", " ");1
			}
		}

		currentMode = jsonData.modeInfo.mode;

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

window.onbeforeunload = function () {
	showSplashscreen(true);
	window.scrollTo({top: 0, left: 0, behavior: 'instant'});
}

////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////   mode change functions   /////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////

function changeMode(modeInfo) {
	switch (modeInfo.mode) {
		case modeFirefox:
			getElement("modeControl").innerHTML = `<h5 class="my-2">Firefox</h5>
<div class='col-6'>
	<button class='disableOnDisconnect btn btn-danger w-100' onclick='restartBrowser();'><span id='restartBrowserSpinner' class='spinner-border spinner-border-sm' role='status' hidden='true'></span><i class='bi bi-arrow-repeat btn-icon-xxl'></i><br><span lang-data='restart-browser'>${getLanguageAsText("restart-browser")}</span></button>
</div>
<div class='col-6'>
	<button class='disableOnDisconnect btn btn-primary w-100' onclick='refreshBrowserPage();'><span id='refreshBrowserPageSpinner' class='spinner-border spinner-border-sm' role='status' hidden=''></span> <i class='bi bi-arrow-clockwise btn-icon-xxl'></i><br><span lang-data='refresh-browser-page'>${getLanguageAsText("refresh-browser-page")}</span></button>
</div>`;
			if (getElement("videoVolumeControlDiv") != null) getElement("videoVolumeControlDiv").outerHTML = "";
			getElement("infoVideoProgressbarWrapper").hidden = true;
			rearrangeGui();
			break;
		case modeVLC:
			getElement("modeControl").innerHTML = `<h5 class="my-2">VLC</h5>
<div class='col-6'>
	<button class='disableOnDisconnect btn btn-danger w-100' onclick='restartVlcVideo();'><span id='restartVlcSpinner' class='spinner-border spinner-border-sm' role='status' hidden='true'></span><i class='bi bi-skip-backward btn-icon-xxl'></i><br><span lang-data='restart-vlc-video'>${getLanguageAsText("restart-vlc-video")}</span></button>
</div>
<div id="videoControlDiv" class='col-6'></div>
<div id="videoVolumeControlDiv" class='col-6 mt-3'>
	<div id="videoVolumeControl" class="border border-primary rounded p-2">
		<table class="w-100"><tr><td><input id="vlcVolumeRange" type="range" class="form-range" min="0" max="100" step="1" value="${modeInfo.info.volume}" onchange="volumeSaved(false); getElement('vlcVolumeNumber').innerHTML = value + '%';"></td><td id="vlcVolumeNumber" class="ps-2 pb-2"></td></tr></table>
		<button id="vlcVolumeSetButton" class='disableOnDisconnect btn btn-primary w-100' onclick="setVlcVolume(getElement('vlcVolumeRange').value);"><i class='bi bi-check2 pe-2'></i><span lang-data="set-volume-vlc">${getLanguageAsText("set-volume-vlc")}</span></button>
	</div>
</div>`;
			if (jsonData.modeInfo.info.state == "State.Paused") {
				getElement("videoControlDiv").innerHTML = `<button class='disableOnDisconnect btn btn-success w-100' onclick='playVlcVideo();'><span id='playVlcSpinner' class='spinner-border spinner-border-sm' role='status' hidden=''></span> <i class='bi bi-play btn-icon-xxl'></i><br><span lang-data='play-vlc-video'>${getLanguageAsText("play-vlc-video")}</span></button>`;
			} else if (jsonData.modeInfo.info.state == "State.Playing") {
				getElement("videoControlDiv").innerHTML = `<button class='disableOnDisconnect btn btn-danger w-100' onclick='pauseVlcVideo();'><span id='pauseVlcSpinner' class='spinner-border spinner-border-sm' role='status' hidden=''></span> <i class='bi bi-pause btn-icon-xxl'></i><br><span lang-data='pause-vlc-video'>${getLanguageAsText("pause-vlc-video")}</span></button>`;
			}

			getElement("infoVideoProgressbarWrapper").hidden = false;
			rearrangeGui();
			break;
		case modeImpress:
			if (getElement("videoVolumeControlDiv") != null) getElement("videoVolumeControlDiv").outerHTML = "";
			getElement("modeControl").innerHTML = `<h5 class="my-2">Impress</h5>
<div class='col-6'>
	<button class='disableOnDisconnect btn btn-danger w-100' onclick='restartImpress();'><span id='restartImpressSpinner' class='spinner-border spinner-border-sm' role='status' hidden='true'></span><i class='bi bi-arrow-repeat btn-icon-xxl'></i><br><span lang-data='restart-impress'>${getLanguageAsText("restart-impress")}</span></button>
</div>`;
			if (getElement("videoVolumeControlDiv") != null) getElement("videoVolumeControlDiv").outerHTML = "";
			getElement("infoVideoProgressbarWrapper").hidden = true;
			rearrangeGui();
			break;
		default:
			getElement("screenContent").innerHTML = "";
			getElement("modeControl").innerHTML = "";
			getElement("infoVideoProgressbarWrapper").hidden = true;
			break;
	}
	getElement("screenContent").innerHTML = getElement("screenContent").innerHTML.replaceAll("%20", " ");
}

////////////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////   language functions   //////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////

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
			try {
				element.textContent = languageStrings[currentLanguage][key];
			} catch (error) {
				console.log(error);
				console.log(key);
			}
		}
	});
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

////////////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////   server communication functions   /////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////

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

function serverExecutedSuccessfully(received) {//returns false if error occurs
	let returncode = received.split(":-:")[1];
	return (returncode == 0);
}

function parseReturnValuesFromServer(received) {
	let returnvals = received.split(":-:")[0].split(":;:");
	for (let i = 0; i < returnvals.length; i++) returnvals[i] = returnvals[i].trim(); // removes whitespace from every output line
	return returnvals;
}

////////////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////   darkmode functions   //////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////

window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', event => {
	setDarkMode(event.matches);
});

function isInDarkmode() {
	return !getElement("theme").href.includes("/bootstrap/css/bootstrap.min.css");
}

function toggleDarkmode() {
	setDarkMode(!isInDarkmode());
}

function setDarkMode(dark) {
	let theme = getElement("theme");
	let languageSelect = getElement("languageSelect");
	let buttonsToToggle = document.getElementsByClassName("toggleDarkLight");
	let closeButtons = document.getElementsByClassName("btn-close");
	if (dark) {
		theme.href = "/bootstrap/darkpan-1.0.0/css/bootstrap.min.css";
		languageSelect.classList.replace("border-dark", "border-light");
		for (let i = 0; i < buttonsToToggle.length; i++) {
			buttonsToToggle[i].classList.replace("btn-outline-dark", "btn-outline-light");
			buttonsToToggle[i].classList.replace("text-dark", "text-light");
		}
		for (let i = 0; i < closeButtons.length; i++) {
			closeButtons[i].classList.replace("btn-close-dark", "btn-close-white");
		}
		getElement("infoVideoProgressbarWrapper").style.backgroundColor = "#373737cf";
	} else {
		theme.href = "/bootstrap/css/bootstrap.min.css";
		languageSelect.classList.replace("border-light", "border-dark");
		for (let i = 0; i < buttonsToToggle.length; i++) {
			buttonsToToggle[i].classList.replace("btn-outline-light", "btn-outline-dark");
			buttonsToToggle[i].classList.replace("text-light", "text-dark");
		}
		for (let i = 0; i < closeButtons.length; i++) {
			closeButtons[i].classList.replace("btn-close-white", "btn-close-dark");
		}
		getElement("infoVideoProgressbarWrapper").style.backgroundColor = "#cecece82";
	}
}

////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////   splashscreen functions   ////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////

function showSplashscreen(show) {
	let splashscreen = getElement("splashscreen");
	if (show) {
		document.getElementsByTagName("body")[0].classList.add("prevent-scrolling");
		splashscreen.style.opacity = 0;
		splashscreen.style.display = "block";
	} else {
		splashscreen.style.opacity = 0;
		document.getElementsByTagName("body")[0].classList.remove("prevent-scrolling");
		setTimeout(() => {
			splashscreen.style.display = "none";
		}, 500);
	}
}

////////////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////   general helper functions   ///////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////

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
	getElement("displayResolution").innerHTML = getLanguageAsText('unknown');

	getElement("displayOnButton").hidden = false;
	getElement("displayOffBtn").hidden = false;
	getElement("spinnerDisplayOn").hidden = true;
	getElement("spinnerDisplayOff").hidden = true;

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

function rearrangeGui() {
	new Masonry(getElement("masonry"));
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

function msToTime(milliseconds) {
	let seconds = (milliseconds / 1000).toFixed();
	let minutes = (seconds / 60).toFixed();
	let hours = (minutes / 60).toFixed();
	return addLeadingZero(hours) + ":" + addLeadingZero(minutes % 60) + ":" + addLeadingZero(seconds % 60);
}
