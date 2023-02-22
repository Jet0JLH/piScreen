<!doctype html>
<html>
<head>
	<link id='theme' href='/bootstrap/css/bootstrap.min.css' rel='stylesheet'>
	<link rel='stylesheet' href='/bootstrap/icons/bootstrap-icons.css'>
	<link rel='stylesheet' href='styles.css'>
	<link rel='icon' type='image/x-icon' href='/favicon.ico'>

	<title><?php echo shell_exec('hostname');?> piScreen Adminpage</title>
</head>
<body>
	<main class='container'>
		<div class='px-4 py-5 my-2 text-center'>
			<button class='btn btn-outline-secondary' id='darkmodeButton' onclick='toggleDarkmode();'><i class='bi bi-moon'></i></button>
			<select id='languageSelect' onchange='changeLanguage(value)' class='disableOnDisconnect form-select border-secondary'>
				<option id='de' value='de'>🇩🇪 Deutsch</option>
				<option id='en' value='en'>🇬🇧 English</option>
			</select>
			<h1 class='display-5 fw-bold'><img src='/piScreen.svg' alt='Logo' width='128' height='128'> <span lang-data='big-header'>piScreen Adminpage</span></h1>
			<p class='lead mb-4' lang-data='small-header'>Hier lassen sich die wichtigsten piScreen Funktionen bequem administrieren</p>
		</div>
		<div id='masonry' class='row' data-masonry='{&quot;percentPosition&quot;: true }'>
			<div class='col-sm-12 col-lg-6 mb-4'>
				<div class='card p-3 shadow'>
					<div class='pb-3' style='float: left;'><h1 style='display:inline'><i class='bi-lightbulb bigIcon px-2'></i><span lang-data='status-tile-header'>Status</span></h1> <span id='idle' class='badge bg-success'>&nbsp;</span></div>
					<p>
						<i class='bi bi-activity'> </i><span lang-data='activity'>Aktivität</span>: <span id='active' class='badge rounded-pill bg-secondary'>???</span><br>
						<i class='bi bi-display'> </i><span lang-data='display-status'>Display Status</span>: <span id='displayState' class='badge rounded-pill bg-secondary'>???</span><br>
						<i class='bi bi-clock-history'></i> <span lang-data='uptime'>Uptime</span>: <span id='uptime'>???</span><br>
						<i class='bi bi-cpu'></i> <span lang-data='cpu-load'>CPU Last</span>: <span id='cpuLoad'>???</span> %<br>
						<i class='bi bi-thermometer'></i> <span lang-data='cpu-temp'>CPU Temperatur</span>: <span id='cpuTemp'>???</span><br>
						<i class='bi bi-memory'></i> <span lang-data='ram'>RAM</span>: <span id='ramUsed'>???</span> <span lang-data='from'>von</span> <span id='ramTotal'>???</span> <span lang-data='in-use'>belegt</span> (<span id='ramUsage'>???</span> %)<br>
						<i class='bi bi-ethernet'></i> <span lang-data='ip-address'>IP</span>: <?php echo $_SERVER['SERVER_ADDR']; ?>
					</p>
				</div>
			</div>
			<div class='col-sm-12 col-lg-6 mb-4'>
				<div class='card p-3 shadow'>
					<h1 class='pb-2'><i class='bi-layout-wtf bigIcon px-2'></i><span lang-data='control-tile-header'>Steuern</span></h1>
					<div class='row'>
						<div class='col-4'>
							<button id='reloadBrowserButton' class='disableOnDisconnect btn btn-primary w-100 my-1' onclick='reloadBrowser()'><span id='restartBrowserSpinner' class='spinner-border spinner-border-sm' role='status' hidden='true'></span><i class='bi bi-arrow-clockwise btn-icon-xxl'></i><br><span lang-data='restart-browser'>Browser neu starten</span></button>
						</div>
						<div class='col-4'>
							<button id='restartHostButton' class='disableOnDisconnect btn btn-warning w-100 my-1' onclick='restartHost()'><i class='bi bi-bootstrap-reboot btn-icon-xxl'></i><br><span lang-data='restart-device'>Neustarten</span></button>
						</div>
						<div class='col-4'>
							<button id='shutdownHostButton' class='disableOnDisconnect btn btn-danger w-100 my-1' onclick='shutdownHost()'><i class='bi bi-power btn-icon-xxl'></i><br><span lang-data='shutdown-device'>Ausschalten</span></button>
						</div>
					</div>
					<div class='row'>
						<div class='col-4'>
							<button id='displayOnButton' class='disableOnDisconnect btn btn-success w-100 my-1' onclick='setDisplayOn()'><span id='spinnerDisplayOn' class='spinner-border spinner-border-sm' role='status' hidden=''></span> <i class='bi bi-display btn-icon-xxl'></i><br><span lang-data='display-on'>Display an</span></button>
						</div>
						<div class='col-4'>
							<button id='displayStandbyButton' class='disableOnDisconnect btn btn-danger w-100 my-1' onclick='setDisplayStandby()'><span id='spinnerDisplayStandby' class='spinner-border spinner-border-sm' role='status' hidden=''></span> <i class='bi bi-display btn-icon-xxl'></i><br><span lang-data='display-off'>Display Standby</span></button>
						</div>
					</div>
				</div>
			</div>
			<div class='col-sm-12 col-lg-6 mb-4'>
				<div class='card p-3 shadow'>
					<h1 class='pb-2'><i class='bi-info-circle bigIcon px-2'></i><span lang-data='info-tile-header'>Info</span></h1>
					<figure class='figure mb-0'>
						<img id='screenshot' src='piScreenScreenshot.png' style='max-width: 100%;' class='border figure-img img-fluid'></img>
						<figcaption id='screenshotTime' class='figure-caption'></figcaption>
						<figcaption id='screenContent' class='figure-caption text-break'></figcaption>
					</figure>
					<hr>
					<div id='info-footer'>
						<button id='versionInfoButton' class='disableOnDisconnect btn btn-primary' onclick='showPiscreenInfo();' lang-data='about-info'>piScreen Info</button>
					</div>
				</div>
			</div>
			<div class='col-sm-12 col-lg-6 mb-4'>
				<div class='card p-3 shadow'>
					<h1 class='pb-2'><i class='bi-gear bigIcon px-2'></i><span lang-data='settings-tile-header'>Einstellungen</span></h1>
					<div class="accordion accordion-flush" id="settingsAccordion">
						<div class="accordion-item" style='background-color: transparent; border: none !important;'>
							<div id="collapseMainSettings" class="accordion-collapse collapse show" data-bs-parent="#settingsAccordion">
								<div class="accordion-body p-0">
									<table style='width: 100%;'>
										<tr>
											<td colspan="2">
												<div class='form-floating mb-3'>
													<input type='text' class='disableOnDisconnect form-control border-secondary' id='settingsHostnameInput' value='<?php echo shell_exec('hostname'); ?>' onkeyup='settingSaved("settingsButtonSaveHostname", false);'>
													<label for='settingsHostnameInput' lang-data='hostname'>Hostname</label>
												</div>
											</td>
											<td style='width: 8%;'>
												<button id='settingsButtonSaveHostname' class='disableOnDisconnect btn btn-success ms-3 mb-3' onclick='setHostname("settingsHostnameInput");'><i class='bi bi-check2'></i></button>
											</td>
										</tr>
										<tr>
											<td colspan="2">
												<div class='form-floating mb-3'>
													<select id='displayProtocolSelect' onchange='settingSaved("settingsButtonSaveDisplayProtocol", false);' class='disableOnDisconnect form-select border-secondary'>
														<option id='cec' value='cec' lang-data='cec'>CEC</option>
														<option id='ddc' value='ddc' lang-data='ddc'>DDC/CI</option>
														<option id='manually' value='manually' lang-data='manually'>Manuell</option>
													</select>
													<label for="displayProtocolSelect" lang-data="display-protocol">Display Protokoll</label>
												</div>
											</td>
											<td style='width: 8%;'>
												<button id='settingsButtonSaveDisplayProtocol' class='disableOnDisconnect btn btn-success ms-3 mb-3' onclick='setDisplayProtocol();'><i class='bi bi-check2'></i></button>
											</td>
										</tr>
										<tr>
											<td colspan="2">
												<div class='form-floating mb-3'>
													<select id='displayOrientationSelect' onchange='settingSaved("settingsButtonSaveDisplayOrientation", false);' class='disableOnDisconnect form-select border-secondary'>
														<option id='horizontal' value='0' lang-data='horizontal'>Horizontal</option>
														<option id='vertical' value='1' lang-data='vertical'>Vertikal</option>
														<option id='horizontalInverted' value='2' lang-data='rotated-horizontally'>Horizontal gedreht</option>
														<option id='verticalInverted' value='3' lang-data='rotated-vertically'>Vertikal gedreht</option>
													</select>
													<label for="displayOrientationSelect" lang-data="display-orientation">Displayausrichtung</label>
												</div>
											</td>
											<td style='width: 8%;'>
												<button id='settingsButtonSaveDisplayOrientation' class='disableOnDisconnect btn btn-success ms-3 mb-3' onclick='setDisplayOrientation();'><i class='bi bi-check2'></i></button>
											</td>
										</tr>
										<tr>
											<td>
												<div class="mb-3">
													<button id='exportScheduleButton' class='disableOnDisconnect btn btn-outline-primary border-secondary' onclick='download("cmd.php?id=21", "schedule.json")'><i class='bi bi-download pe-2'></i><span lang-data='export'>Export</span></button>
												</div>
											</td>
											<td>
												<div class="input-group mb-3">
													<button id='importScheduleButton' class='disableOnDisconnect btn btn-outline-primary border-secondary border-end-0' ondragover='event.preventDefault();' ondrop='dropScheduleJson(event);' onclick='selectScheduleToImport();'><i class='bi bi-upload pe-2'></i><span lang-data='import'>Import</span></button>
													<input id='importScheduleInputTextfield' type="text" class=" disableOnDisconnect form-control border-secondary border-start-0" style='float: right;' ondragover='event.preventDefault();' ondrop='dropScheduleJson(event);' onclick='this.blur(); selectScheduleToImport();' value=''>
												</div>
											</td>
											<td style='width: 8%;'>
												<button id='settingsButtonSaveImportSchedule' class='disableOnDisconnect btn btn-success ms-3 mb-3' onclick='setSchedule();'><i class='bi bi-check2'></i></button>
											</td>
										</tr>
									</table>
									<button id='showLoginSettings' class='disableOnDisconnect btn btn-outline-primary' data-bs-toggle="collapse" data-bs-target="#collapseLoginSettings"><i class='bi bi-pencil-square pe-2'></i><span lang-data="edit-weblogin">Weblogindaten bearbeiten</span></button>
								</div>
							</div>
						</div>
						<div class="accordion-item" style='background-color: transparent;'>
							<div id="collapseLoginSettings" class="accordion-collapse collapse" data-bs-parent="#settingsAccordion">
								<div class="accordion-body p-0">
									<div class='form-floating mb-3'>
										<input type='text' class='disableOnDisconnect form-control' id='webUserInput'>
										<label for='webUserInput' lang-data='username-web'>Benutzername für Weblogin</label>
									</div>
									<div class='form-floating mb-3'>
										<input type='password' class='disableOnDisconnect form-control' id='webPasswordInput'>
										<label for='webPasswordInput' lang-data='password-web'>Passwort für Weblogin</label>
									</div>
									<button id='saveAndShowMainSettings' class='disableOnDisconnect btn btn-outline-success' data-bs-toggle="collapse" data-bs-target="#collapseMainSettings" onclick='setWebLoginAndPassword();'><i class='bi bi-save pe-2'></i><span lang-data="save-weblogin">Weblogindaten speichern</span></button>
									<button id='cancelAndShowMainSettings' class='disableOnDisconnect btn btn-outline-primary' data-bs-toggle="collapse" data-bs-target="#collapseMainSettings"><i class='bi bi-arrow-left pe-2'></i><span lang-data="back">Zurück</span></button>
								</div>
							</div>
						</div>
					</div>
				</div>
			</div>
			<div class='col-sm-12 col-lg-6 mb-4'>
				<div class='card p-3 shadow'>
					<h1 class='pb-2'><i class='bi bi-lightning-charge bigIcon px-2'></i><span lang-data='startup-trigger'>Startuptrigger</span></h1>
					<div class='form-check form-switch m-1' style='display: flex; flex-flow: row wrap; align-items: center;'>
						<input class="disableOnDisconnect form-check-input" type="checkbox" role="switch" id="trigger0EnabledSwitch" onchange='triggerSaved(false, 0);'></input>
						<label for="trigger0EnabledSwitch" class="px-2" lang-data='active'>Startup trigger</label>
						<i class='bi-question-octagon p-2' style='cursor: pointer;' id='triggerHelp' data-bs-toggle="tooltip" data-bs-placement="top" data-bs-title="??" onclick='showModal(getLanguageAsText("help"), getLanguageAsText("triggerHelpText"), false, true, getLanguageAsText("ok"));'></i>
					</div>
					<div class='form-floating mb-4'>
						<select id='trigger0CommandsetSelect' class='disableOnDisconnect commandsetDropdown form-select border-secondary' onchange='triggerSaved(false, 0);'>
						</select>
						<label for="trigger0CommandsetSelect" lang-data='choose-commandset'>Commandset auswählen</label>
					</div>
					<br>
					<div class='form-floating mb-3'>
						<select id='trigger0CommandSelect' class='disableOnDisconnect form-select border-secondary' onchange='triggerSaved(false, 0); addParameterToTrigger(0, value);'>
						</select>
						<label for="trigger0CommandSelect" lang-data='choose-command'>Command auswählen</label>
					</div>
					<div id="trigger0ParameterCell" style='width: 100%;'>
					</div>
					<div>
						<button id="trigger0SaveButton" class="disableOnDisconnect btn btn-success mt-2" onclick='saveTrigger(0);'><i class='bi bi-check2 pe-2'></i><span lang-data="saved">Speichern</span></button>
						<button id="trigger0ExecuteButton" class="disableOnDisconnect btn btn-outline-warning mt-2" onclick='executeStartupTrigger();'><i class='bi bi-play pe-2'></i><span id='executeStartupTriggerSpinner' class='spinner-border spinner-border-sm' role='status' hidden='true'></span><span lang-data="execute">Ausführen</span></button>
					</div>
				</div>
			</div>
			<div class='col-lg-12 col-xl-6 mb-4'>
				<div class='card p-3 shadow'>
					<h1 class='pb-2'><i class='bi bi-calendar-check bigIcon px-2'></i><span lang-data='planner'>Planer</span></h1>
					<table class="pb-3" style="width: 100%;">
						<tr class="text-center">
							<td style="width: 33%;">
								<button type="radio" id="option1" name="options" class='btn-check' data-bs-target="#timeActionsCarousel" data-bs-slide-to="0" style="cursor: pointer;" checked></button>
								<label id="plannerOption0" class="btn btn-primary w-100 m-2 mb-4" for="option1"><i class='bi bi-calendar2-day bigIcon px-2'></i><span lang-data='timeschedule'>Zeitplan</label>
							</td>
							<td style="width: 33%;">
								<button type="radio" id="option2" name="options" class='btn-check' data-bs-target="#timeActionsCarousel" data-bs-slide-to="1" style="cursor: pointer;"></button>
								<label id="plannerOption1" class="btn btn-secondary w-100 m-2 mb-4" for="option2"><i class='bi bi-terminal bigIcon px-2'></i><span lang-data='commandsets'>Commandsets</label>
							</td>
							<td style="width: 33%;">
								<button type="radio" id="option3" name="options" class='btn-check' data-bs-target="#timeActionsCarousel" data-bs-slide-to="2" style="cursor: pointer;"></button>
								<label id="plannerOption2" class="btn btn-secondary w-100 m-2 mb-4" for="option3"><i class='bi bi-lightning-charge bigIcon px-2'></i><span lang-data='trigger'>Trigger</span></label>
							</td>
						</tr>
					</table>
					<div id="timeActionsCarousel" class="carousel slide">
						<div class="carousel-inner">
							<div class="carousel-item active">
								<div id='scheduleEntryCollectionList' class="list-group">

								</div>
								<div>
									<button id='newScheduleEntry' class='disableOnDisconnect btn btn-outline-success mt-2' onclick='showCronModal(Math.floor(Math.random() * 9999) - 10000 );'><i class='bi bi-plus-lg pe-2'></i><span lang-data='new-entry'>Neuer Eintrag</span></button>
									<button id='lastCronButton' class='disableOnDisconnect btn btn-outline-warning mt-2 px-2' onclick="sendHTTPRequest('GET', 'cmd.php?id=22', true);"><i class='bi bi-play pe-2'></i><span lang-data='lastcron'>Letzter Eintrag ausführen</span></button>
								</div>
							</div>
							<div class="carousel-item">
								<div id="commandsetCollectionList" class="list-group">
								</div>
							<button id='commandsetEntryButtonAdd' class='disableOnDisconnect btn btn-outline-success mt-2' onclick='showCommandsetModal();'><i class='bi bi-plus-lg pe-2'></i><span lang-data='new-commandset'>Neues Commandset</span></button>
							<div class="carousel-item">
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	</main>
	<div id='cronModal' class='modal fade' tabindex='-1'>
		<div class='modal-xl modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-xl-down'>
			<div class='modal-content'>
				<div class='modal-header'>
					<h5 id='cronModalTitle' class='modal-title'></h5>
					<button class='btn-close btn-close-white' data-bs-dismiss='modal'></button>
				</div>
				<div id='cronModalBody' class='modal-body'>

				</div>
				<div class='modal-footer'>
					<table style="width: 100%;">
						<tr>
							<td style="width: 50%;">
								<button id="scheduleEntryButtonDelete" class="disableOnDisconnect btn btn-outline-danger m-1" onclick='deleteScheduleEntry();'><i class='bi bi-trash pe-2'></i><span lang-data='delete-entry'></span></button>
							</td>
							<td>
								<button id='scheduleEntryButtonSave' class='btn btn-outline-success m-1' onclick='saveScheduleEntry();' style='float: right;'><i class='bi bi-save pe-2'></i><span lang-data="save">Speichern</span></button>
								<button id='scheduleEntryButtonCancel' class='btn btn-outline-light m-1' data-bs-dismiss='modal' style='float: right;'><i class='bi bi-x-circle pe-2'></i><span lang-data="cancel">Abbruch</span></button>
							</td>
						</tr>
					</table>
				</div>
			</div>
		</div>
	</div>
	<div id='cronEntryModal' class='modal fade' tabindex='-1'>
		<div class='modal-xl modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-xl-down'>
			<div class='modal-content'>
				<div class='modal-header'>
					<h5 id='cronEntryModalTitle' class='modal-title'>
						<i class="bi bi-pencil-square pe-2"></i><span lang-data="edit-cron-entry">Croneintrag bearbeiten</span>
					</h5>
					<button class='btn-close btn-close-white' data-bs-dismiss='modal'></button>
				</div>
				<div id='cronEntryModalBody' class='modal-body'>
					<div class="form-check m-0 p-0">
						<table class="w-100">
							<tr>
								<td colspan="4" class="border-top border-primary py-3">
									<input type="radio" name="cronRadio" class="btn-check" id="dailyCronRadio" onclick="cronEntryOnChange(value)" value="1" checked>
									<label for="dailyCronRadio" class="btn btn-outline-primary"><h5 class="m-0" lang-data="daily">Täglich</h5></label>
								</td>
							</tr>
							<tr id="cronEntryDailyRow">
								<td style="width: 15%; text-align: center;" class="pb-3">
									<span lang-data="at-this-time">Zu dieser Zeit</span>
								</td>
								<td style="width: 20%; text-align: center;" class="pb-3">
									<input id='cronEntryDailyTime' type="time" class="disableOnDisconnect form-control border border-secondary p-1" style="text-align: center;" value="12:00">
								</td>
								<td style="width: 20%; text-align: center;" class="pb-3">
									<span lang-data="at-these-days">An diesen Tagen</span>
								</td>
								<td style="width: 45%; text-align: center;" class="pb-3">
									<div class="form-check form-check-inline">
										<input class="form-check-input dailyDayCheck" type="checkbox" value="0" id="dailyDayCheck0">
										<label class="form-check-label" for="dailyDayCheck0" lang-data="mon">Mo</label>
									</div>
									<div class="form-check form-check-inline">
										<input class="form-check-input dailyDayCheck" type="checkbox" value="1" id="dailyDayCheck1">
										<label class="form-check-label" for="dailyDayCheck1" lang-data="tue">Di</label>
									</div>
									<div class="form-check form-check-inline">
										<input class="form-check-input dailyDayCheck" type="checkbox" value="2" id="dailyDayCheck2">
										<label class="form-check-label" for="dailyDayCheck2" lang-data="wed">Mi</label>
									</div>
									<div class="form-check form-check-inline">
										<input class="form-check-input dailyDayCheck" type="checkbox" value="3" id="dailyDayCheck3">
										<label class="form-check-label" for="dailyDayCheck3" lang-data="thu">Do</label>
									</div>
									<div class="form-check form-check-inline">
										<input class="form-check-input dailyDayCheck" type="checkbox" value="4" id="dailyDayCheck4">
										<label class="form-check-label" for="dailyDayCheck4" lang-data="fri">Fr</label>
									</div>
									<div class="form-check form-check-inline">
										<input class="form-check-input dailyDayCheck" type="checkbox" value="5" id="dailyDayCheck5">
										<label class="form-check-label" for="dailyDayCheck5" lang-data="sat">Sa</label>
									</div>
									<div class="form-check form-check-inline">
										<input class="form-check-input dailyDayCheck" type="checkbox" value="6" id="dailyDayCheck6">
										<label class="form-check-label" for="dailyDayCheck6" lang-data="sun">So</label>
									</div>
								</td>
							</tr>
							<tr>
								<td colspan="4" class="border-top border-primary py-3">
									<input type="radio" name="cronRadio" class="btn-check" id="monthlyCronRadio" onclick="cronEntryOnChange(value)" value="2">
									<label for="monthlyCronRadio" class="btn btn-outline-primary"><h5 class="m-0" lang-data="mothly">Monatlich</h5></label>
								</td>
							</tr>
							<tr id="cronEntryMonthlyRow" hidden>
								<td style="width: 15%; text-align: center;" class="pb-3">
									<span lang-data="at-this-time">Zu dieser Zeit</span>
								</td>
								<td style="width: 20%; text-align: center;" class="pb-3">
									<input id='cronEntryMonthlyTime' type="time" class="disableOnDisconnect form-control border border-secondary p-1" style="text-align: center;" value="12:00">
								</td>
								<td style="width: 20%; text-align: center;" class="pb-3">
									<span lang-data="at-these-days">An diesen Tagen</span>
								</td>
								<td style="width: 45%; text-align: center;" id="monthlyDayChecks" class="pb-3">
									<table id="cronEntryDayTable">
										<script>
let table = document.getElementById("cronEntryDayTable");
for (let w = 0; w < 5; w++) {
	let row = document.createElement("tr");
	for (let d = 1; d <= 7; d++) {
		let cell = document.createElement("td");
		let i = 7 * w + d;
		if (i > 31) break;
		let div = document.createElement("div");
		div.className = "form-check form-check-inline";
		div.style.float = "left";

		let input = document.createElement("input");
		input.className = "form-check-input monthlyDayCheck";
		input.type = "checkbox";
		input.value = i;
		input.id = "monthlyDayCheck" + i;
		div.appendChild(input);

		let label = document.createElement("label");
		label.className = "form-check-label";
		label.htmlFor = "monthlyDayCheck" + i;
		label.innerText = i;
		div.appendChild(label);
		cell.appendChild(div);
		row.appendChild(cell);
	}
	table.appendChild(row);
}
										</script>
									</table>
								</td>
							</tr>
							<tr>
								<td colspan="4" class="border-top border-primary py-3">
									<input type="radio" name="cronRadio" class="btn-check" id="periodicCronRadio" onclick="cronEntryOnChange(value)" value="3">
									<label for="periodicCronRadio" class="btn btn-outline-primary"><h5 class="m-0" lang-data="periodically">Periodisch</h5></label>
								</td>
							</tr>
							<tr id="cronEntryPeriodicRow" hidden>
								<td style="width: 15%; text-align: center;" class="pb-3">
									<span lang-data="every">Alle</span>
								</td>
								<td style="width: 20%; text-align: center;" class="pb-3">
									<select id='cronEntryPeriodicTimeSelect' class='disableOnDisconnect form-select border-secondary'>
										<option id='periodicTimeOption1' value='1'>1</option>
										<option id='periodicTimeOption2' value='2'>2</option>
										<option id='periodicTimeOption3' value='3'>3</option>
										<option id='periodicTimeOption4' value='4'>4</option>
										<option id='periodicTimeOption5' value='5'>5</option>
										<option id='periodicTimeOption6' value='6'>6</option>
										<option id='periodicTimeOption10' value='10'>10</option>
										<option id='periodicTimeOption15' value='15'>15</option>
										<option id='periodicTimeOption20' value='20'>20</option>
										<option id='periodicTimeOption30' value='30'>30</option>
										<option id='periodicTimeOption45' value='45'>45</option>
										<option id='periodicTimeOption60' value='60'>60</option>
									</select>
								</td>
								<td style="width: 20%; text-align: center;" class="pb-3">
									<select id='cronEntryPeriodicTimeSpanSelect' class='disableOnDisconnect form-select border-secondary'>
										<option id='periodicTimeOptionMinutes' value='1' lang-data="minutes">Minuten</option>
										<option id='periodicTimeOptionHours' value='2' lang-data="hours">Stunden</option>
										<option id='periodicTimeOptionDays' value='3' lang-data="days">Tage</option>
										<option id='periodicTimeOptionMonths' value='4' lang-data="months">Monate</option>
									</select>
								</td>
								<td style="width: 45%; text-align: center;" class="pb-3">
								</td>
							</tr>
							<tr>
								<td colspan="4" class="border-top border-primary pt-3"> </td>
							</tr>
						</table>

					</div>
				</div>
				<div class='modal-footer'>
					<button id='cronEntryButtonCancel' class='btn btn-outline-light m-1' data-bs-dismiss='modal' style='float: right;'><i class='bi bi-x-circle pe-2'></i><span lang-data="cancel">Abbruch</span></button>
					<button id='cronEntryButtonOk' class='disableOnDisconnect btn btn-outline-success m-1' onclick='cronEntryOk();' style='float: right;'><i class='bi bi-save pe-2'></i><span lang-data="ok">Ok</span></button>
				</div>
			</div>
		</div>
	</div>
	<div id='commandsetModal' class='modal fade' tabindex='-1'>
		<div class='modal-xl modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-xl-down'>
			<div class='modal-content'>
				<div class='modal-header'>
					<h5 id='commandsetModalTitle' class='modal-title'></h5>
					<button class='btn-close btn-close-white' data-bs-dismiss='modal'></button>
				</div>
				<div id='commandsetModalBody' class='modal-body'>

				</div>
				<div class='modal-footer'>
					<table style="width: 100%;">
						<tr>
							<td style="width: 50%;">
								<button id="commandsetEntryButtonDelete" class="disableOnDisconnect btn btn-outline-danger m-1" onclick='deleteCommandsetEntry();'><i class='bi bi-trash pe-2'></i><span lang-data='delete-commandset'></span></button>
							</td>
							<td>
								<button id='commandsetEntryButtonSave' class='btn btn-outline-success m-1' onclick='saveCommandsetEntry();' style='float: right;'><i class='bi bi-save pe-2'></i><span lang-data="save">Speichern</span></button>
								<button id='commandsetEntryButtonCancel' class='btn btn-outline-light m-1' data-bs-dismiss='modal' style='float: right;'><i class='bi bi-x-circle pe-2'></i><span lang-data="cancel">Abbruch</span></button>
							</td>
						</tr>
					</table>
				</div>
			</div>
		</div>
	</div>

	<div id='modal' class='modal fade' tabindex='-1'>
		<div class='modal-lg modal-dialog modal-dialog-centered'>
			<div class='modal-content'>
				<div class='modal-header'>
					<h5 class='modal-title'></h5>
					<button class='btn-close btn-close-white' data-bs-dismiss='modal'></button>
				</div>
				<div class='modal-body'>

				</div>
				<hr>
				<div class='modal-footer'>
					<button id='modal-cancelBtn' class='btn btn-secondary' data-bs-dismiss='modal' lang-data='cancel'>Abbruch</button>
					<button id='modal-actionBtn' class='btn'></button>
				</div>
			</div>
		</div>
	</div>
</body>
<script src='/bootstrap/js/bootstrap.bundle.min.js'></script>
<script src='/masonry.pkgd.min.js'></script>
<script src='admin.js'></script>
</html>