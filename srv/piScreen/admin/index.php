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
			<button class='toggleDarkLight btn btn-outline-dark' id='darkmodeButton' onclick='toggleDarkmode();'><i class='bi bi-moon'></i></button>
			<select id='languageSelect' onchange='changeLanguage(value)' class='disableOnDisconnect form-select border-dark'>
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
					<div class='row my-2'>
						<h5 class="m-0 mb-2" lang-data="host">Host</h5>
						<div class='col-6'>
							<button id='restartHostButton' class='disableOnDisconnect btn btn-warning w-100' onclick='restartHost()'><i class='bi bi-bootstrap-reboot btn-icon-xxl'></i><br><span lang-data='restart-device'>Neustarten</span></button>
						</div>
						<div class='col-6'>
							<button id='shutdownHostButton' class='disableOnDisconnect btn btn-danger w-100' onclick='shutdownHost()'><i class='bi bi-power btn-icon-xxl'></i><br><span lang-data='shutdown-device'>Ausschalten</span></button>
						</div>
					</div>
					<div class='row my-2'>
						<h5 class="my-2" lang-data="display">Display</h5>
						<div class='col-6'>
							<button id='displayOnButton' class='disableOnDisconnect btn btn-success w-100' onclick='setDisplayOn()'><span id='spinnerDisplayOn' class='spinner-border spinner-border-sm' role='status' hidden=''></span> <i class='bi bi-display btn-icon-xxl'></i><br><span lang-data='display-on'>Display an</span></button>
						</div>
						<div class='col-6'>
							<button id='displayStandbyButton' class='disableOnDisconnect btn btn-danger w-100' onclick='setDisplayStandby()'><span id='spinnerDisplayStandby' class='spinner-border spinner-border-sm' role='status' hidden=''></span> <i class='bi bi-display btn-icon-xxl'></i><br><span lang-data='display-off'>Display Standby</span></button>
						</div>
					</div>
					<div id="modeControl" class='row my-2'>
					</div>
				</div>
			</div>
			<div class='col-sm-12 col-lg-6 mb-4'>
				<div class='card p-3 shadow'>
					<h1 class='pb-2'><i class='bi-info-circle bigIcon px-2'></i><span lang-data='info-tile-header'>Info</span></h1>
					<figure class='figure mb-0'>
						<img id='screenshot' src='piScreenScreenshot-thumb.jpg' style='max-width: 100%; cursor: pointer;' class='border figure-img img-fluid' onclick="showScreenshotModal();"></img>
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
											<td colspan="2">
												<div class="input-group mb-3">
													<button id='exportScheduleButton' class='disableOnDisconnect btn btn-outline-primary border-secondary' onclick='download("cmd.php?id=21", "schedule.json")'><i class='bi bi-download pe-2'></i><span lang-data='export'>Export</span></button>
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
			<div class='col-sm-12 col-lg-6 mb-4'>
				<div class='card p-3 shadow'>
					<h1 class='pb-2'><i class='bi bi-folder bigIcon px-2'></i><span lang-data='file-explorer'>file explorer</span></h1>
					<button class='disableOnDisconnect btn btn-outline-success mt-2' onclick='showFileExplorerModal(0, true, null, false);'><i class='bi bi-folder pe-2'></i><span lang-data='file-explorer'></span></button>
				</div>
			</div>
			<div class='col-lg-12 col-xl-6 mb-4'>
				<div class='card p-3 shadow'>
					<h1 class='pb-2'><i class='bi bi-calendar-check bigIcon px-2'></i><span lang-data='planner'>Planer</span></h1>
					<table class="pb-3" style="width: 100%;">
						<tr class="text-center">
							<td style="width: 33%;">
								<button type="radio" id="option1" name="options" class='btn-check' data-bs-target="#timeActionsCarousel" data-bs-slide-to="0" style="cursor: pointer;" checked></button>
								<label id="plannerOption0" class="btn btn-primary w-100 mb-4" for="option1"><i class='bi bi-calendar2-day bigIcon px-2'></i><span lang-data='timeschedule'>Zeitplan</label>
							</td>
							<td style="width: 33%;">
								<button type="radio" id="option2" name="options" class='btn-check' data-bs-target="#timeActionsCarousel" data-bs-slide-to="1" style="cursor: pointer;"></button>
								<label id="plannerOption1" class="btn btn-secondary w-100 mb-4" for="option2"><i class='bi bi-terminal bigIcon px-2'></i><span lang-data='commandsets'>Commandsets</label>
							</td>
							<td style="width: 33%;">
								<button type="radio" id="option3" name="options" class='btn-check' data-bs-target="#timeActionsCarousel" data-bs-slide-to="2" style="cursor: pointer;"></button>
								<label id="plannerOption2" class="btn btn-secondary w-100 mb-4" for="option3"><i class='bi bi-lightning-charge bigIcon px-2'></i><span lang-data='trigger'>Trigger</span></label>
							</td>
						</tr>
					</table>
					<div id="timeActionsCarousel" class="carousel slide">
						<div class="carousel-inner">
							<div class="carousel-item active">
								<div id='scheduleEntryCollectionList' class="list-group">

								</div>
								<div>
									<button id='newScheduleEntry' class='disableOnDisconnect btn btn-outline-success mt-2' onclick='showScheduleModal(Math.floor(Math.random() * 9999) - 10000 );'><i class='bi bi-plus-lg pe-2'></i><span lang-data='new-entry'>Neuer Eintrag</span></button>
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
	<div id='scheduleModal' class='modal fade' tabindex='-1'>
		<div class='modal-xl modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-xl-down'>
			<div class='modal-content'>
				<div class='modal-header'>
					<h5 id='scheduleModalTitle' class='modal-title'></h5>
					<button class='btn-close btn-close-white' data-bs-dismiss='modal'></button>
				</div>
				<div id='scheduleModalBody' class='modal-body'>

				</div>
				<div class='modal-footer'>
					<table style="width: 100%;">
						<tr>
							<td style="width: 50%;">
								<button id="scheduleEntryButtonDelete" class="disableOnDisconnect btn btn-outline-danger m-1" onclick='deleteScheduleEntry();'><i class='bi bi-trash pe-2'></i><span lang-data='delete-entry'></span></button>
							</td>
							<td>
								<button id='scheduleEntryButtonSave' class='disableOnDisconnect btn btn-outline-success m-1' onclick='saveScheduleEntry();' style='float: right;'><i class='bi bi-save pe-2'></i><span lang-data="save">Speichern</span></button>
								<button id='scheduleEntryButtonCancel' class='toggleDarkLight btn btn-outline-light m-1' data-bs-dismiss='modal' style='float: right;'><i class='bi bi-x-circle pe-2'></i><span lang-data="cancel">Abbruch</span></button>
							</td>
						</tr>
					</table>
				</div>
			</div>
		</div>
	</div>
	<div id='cronEditorModal' class='modal fade' tabindex='-1'>
		<div class='modal-xl modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-xl-down'>
			<div class='modal-content'>
				<div class='modal-header'>
					<h5 id='cronEditorModalTitle' class='modal-title'>
						<i class="bi bi-pencil-square pe-2"></i><span lang-data="edit-cron-entry">Croneintrag bearbeiten</span>
					</h5>
					<button class='btn-close btn-close-white' data-bs-dismiss='modal'></button>
				</div>
				<div id='cronEditorModalBody' class='modal-body'>
					<table class="pb-3 m-1" style="width: 100%;">
						<tr class="text-center">
							<td style="width: 33%;">
								<button type="radio" id="cronEditorCarouselOption0" name="cronEditorCarouselOptions" class='btn-check' data-bs-target="#cronEditorCarousel" data-bs-slide-to="0" style="cursor: pointer;" checked></button>
								<label class="btn btn-primary w-100 mb-4" id="cronEditorCarouselOptionLabel0" for="cronEditorCarouselOption0"><span lang-data='daily'>Täglich</label>
							</td>
							<td style="width: 33%;">
								<button type="radio" id="cronEditorCarouselOption1" name="cronEditorCarouselOptions" class='btn-check' data-bs-target="#cronEditorCarousel" data-bs-slide-to="1" style="cursor: pointer;"></button>
								<label class="btn btn-secondary w-100 mb-4" id="cronEditorCarouselOptionLabel1" for="cronEditorCarouselOption1"><span lang-data='monthly'>Monatlich</label>
							</td>
							<td style="width: 33%;">
								<button type="radio" id="cronEditorCarouselOption2" name="cronEditorCarouselOptions" class='btn-check' data-bs-target="#cronEditorCarousel" data-bs-slide-to="2" style="cursor: pointer;"></button>
								<label class="btn btn-secondary w-100 mb-4" id="cronEditorCarouselOptionLabel2" for="cronEditorCarouselOption2"><span lang-data='periodically'>Periodisch</span></label>
							</td>
						</tr>
					</table>
					<div class="w-100 p-3">
						<div id="cronEditorCarousel" class="carousel slide">
							<div class="carousel-inner">
								<div class="carousel-item active">
									<table class="w-100">
										<tr id="cronEditorDailyRow">
											<td style="width: 15%; text-align: center;" class="pb-3">
												<span lang-data="at-this-time">Zu dieser Zeit</span>
											</td>
											<td style="width: 20%; text-align: center;" class="pb-3">
												<input id='cronEditorDailyTime' type="time" class="disableOnDisconnect form-control border border-secondary p-1" style="text-align: center;" value="12:00">
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
											<td colspan="3"></td>
											<td>
												<button class='toggleDarkLight btn btn-sm btn-outline-light m-1' onclick='cronEditorDaysSelectAll();'><i class='bi bi-check-square-fill pe-2'></i><span lang-data="select-all">Alle auswählen</span></button>
												<button class='toggleDarkLight btn btn-sm btn-outline-light m-1' onclick='cronEditorDaysInvert();'><i class='bi bi-slash-square-fill pe-2'></i><span lang-data="invert-selection">Auswahl invertieren</span></button>
												<button class='toggleDarkLight btn btn-sm btn-outline-light m-1' onclick='cronEditorDaysUnselectAll();'><i class='bi bi-square pe-2'></i><span lang-data="select-nothing">Keines auswählen</span></button>
											</td>
										</tr>
									</table>	
								</div>
								<div class="carousel-item">
									<table class="w-100">
										<tr id="cronEditorMonthlyRow">
											<td style="width: 15%; text-align: center;" class="pb-3">
												<span lang-data="at-this-time">Zu dieser Zeit</span>
											</td>
											<td style="width: 20%; text-align: center;" class="pb-3">
												<input id='cronEditorMonthlyTime' type="time" class="disableOnDisconnect form-control border border-secondary p-1" style="text-align: center;" value="12:00">
											</td>
											<td style="width: 20%; text-align: center;" class="pb-3">
												<span lang-data="at-these-days">An diesen Tagen</span>
											</td>
											<td style="width: 45%; text-align: center;" id="monthlyDayChecks" class="pb-3">
												<table id="cronEditorDayTable">
													<script>
let table = document.getElementById("cronEditorDayTable");
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
											<td colspan="3"></td>
											<td>
												<button class='toggleDarkLight btn btn-sm btn-outline-light m-1' onclick='cronEditorMonthsSelectAll();'><i class='bi bi-check-square-fill pe-2'></i><span lang-data="select-all">Alle auswählen</span></button>
												<button class='toggleDarkLight btn btn-sm btn-outline-light m-1' onclick='cronEditorMonthsInvert();'><i class='bi bi-slash-square-fill pe-2'></i><span lang-data="invert-selection">Auswahl invertieren</span></button>
												<button class='toggleDarkLight btn btn-sm btn-outline-light m-1' onclick='cronEditorMonthsUnselectAll();'><i class='bi bi-square pe-2'></i><span lang-data="select-nothing">Keines auswählen</span></button>
											</td>
										</tr>
									</table>
								</div>
								<div class="carousel-item">
									<table class="w-100">
										<tr id="cronEditorPeriodicRow">
											<td style="width: 15%; text-align: center;" class="pb-3">
												<span lang-data="every">Alle</span>
											</td>
											<td style="width: 20%; text-align: center;" class="pb-3">
												<select id='cronEditorPeriodicTimeSelect' class='disableOnDisconnect form-select border-secondary'>

												</select>
											</td>
											<td style="width: 20%; text-align: center;" class="pb-3">
												<select id='cronEditorPeriodicTimeSpanSelect' class='disableOnDisconnect form-select border-secondary' onchange="updateSelectableValues(value);">
													<option id='periodicTimeOptionMinutes' value='0' lang-data="minutes">Minuten</option>
													<option id='periodicTimeOptionHours' value='1' lang-data="hours">Stunden</option>
													<option id='periodicTimeOptionMonths' value='2' lang-data="months">Monate</option>
												</select>
											</td>
											<td style="width: 45%; text-align: center;" class="pb-3">
											</td>
										</tr>
									</table>
								</div>
							</div>
						</div>
					</div>
				</div>
				<div class='modal-footer'>
					<button id='cronEditorButtonCancel' class='toggleDarkLight btn btn-outline-light m-1' data-bs-dismiss='modal' style='float: right;'><i class='bi bi-x-circle pe-2'></i><span lang-data="cancel">Abbruch</span></button>
					<button id='cronEditorButtonOk' class='disableOnDisconnect btn btn-outline-success m-1' onclick='cronEditorOk();' style='float: right;'><i class='bi bi-save pe-2'></i><span lang-data="ok">Ok</span></button>
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
								<button id='commandsetEntryButtonSave' class='disableOnDisconnect btn btn-outline-success m-1' onclick='saveCommandsetEntry();' style='float: right;'><i class='bi bi-save pe-2'></i><span lang-data="save">Speichern</span></button>
								<button id='commandsetEntryButtonCancel' class='toggleDarkLight btn btn-outline-light m-1' data-bs-dismiss='modal' style='float: right;'><i class='bi bi-x-circle pe-2'></i><span lang-data="cancel">Abbruch</span></button>
							</td>
						</tr>
					</table>
				</div>
			</div>
		</div>
	</div>
	<div id='fileExplorerModal' class='modal fade' tabindex='-1'>
		<div class='modal-xl modal-dialog modal-dialog-centered modal-fullscreen-xl-down'>
			<div class='modal-content'>
				<div class='modal-header'>
					<h5 class='modal-title'>
						<i class="bi bi-folder pe-2"></i><span lang-data="file-explorer">fileexplorer</span>
					</h5>
					<button class='btn-close btn-close-white' data-bs-dismiss='modal'></button>
				</div>
				<div class='modal-body'>
					<table class="w-100">
						<tr>
							<td rowspan="2" style="width: 30%;" class="border border-primary p-2">
								<div class="list-group">
									<button type="button" id="fileExplorerMode0" value="0" class="fileExplorerModeButton toggleDarkLight text-dark bg-transparent list-group-item list-group-item-action active" onclick="changeFileExplorerMode(value);">Allgemein</button>
									<button type="button" id="fileExplorerMode1" value="1" class="fileExplorerModeButton toggleDarkLight text-dark bg-transparent list-group-item list-group-item-action" onclick="changeFileExplorerMode(value);">Firefox</button>
									<button type="button" id="fileExplorerMode2" value="2" class="fileExplorerModeButton toggleDarkLight text-dark bg-transparent list-group-item list-group-item-action" onclick="changeFileExplorerMode(value);">VLC</button>
									<button type="button" id="fileExplorerMode3" value="3" class="fileExplorerModeButton toggleDarkLight text-dark bg-transparent list-group-item list-group-item-action" onclick="changeFileExplorerMode(value);">Impress</button>
								</div>
							</td>
							<td style="width: 70%;" class="border border-primary p-3">
								<div class="d-inline">
									<h5 class="d-inline"><span id="fileExplorerRootFolder" class="badge rounded-pill bg-secondary">Ordner</span></h5>
								</div>
								<div class="d-inline" style="float: right;">
									<button class='disableOnDisconnect btn btn-sm btn-outline-danger m-1' onclick='deleteSelectedFiles();'><i class='bi bi-trash pe-2'></i><span lang-data="delete">Löschen</span></button>
									<button class='disableOnDisconnect btn btn-sm btn-outline-success m-1' onclick='selectFileToUpload();'><i class='bi bi-upload pe-2'></i><span lang-data="upload">Hochladen</span></button>
								</div>
							</td>
						</tr>
						<tr>
							<td class="border border-primary p-3">
								<div id="fileExplorerFileCollection" class="row row-cols-1 row-cols-md-6 g-2" style="overflow-x:hidden; overflow-y:auto; height: 30rem;" ondragover='event.preventDefault();' ondrop='dropFileIntoFileExplorer(event);'>

								</div>
							</td>
						</tr>
					</table>
				</div>
				<div id="fileExplorerFooter" class='modal-footer'>
					<button class='btn btn-outline-light' data-bs-dismiss='modal' lang-data='cancel'>Abbruch</button>
					<button class='btn btn-outline-success' onclick="applySelectedFile();" data-bs-dismiss='modal' lang-data='apply'>Anwenden</button>
				</div>
			</div>
		</div>
	</div>
	<div id='renameModal' class='modal fade' tabindex='-1'>
		<div class='modal-lg modal-dialog modal-dialog-centered'>
			<div class='modal-content'>
				<div class='modal-header'>
					<h5 class='modal-title'><span lang-data="rename">Umbenennen</span>: <span id="renameOldName">alter name</span></h5>
					<button class='btn-close btn-close-white' data-bs-dismiss='modal'></button>
				</div>
				<div class='modal-body'>
					<div class='form-floating mb-3'>
						<input type='text' id='renameTextfield' class='form-control border-secondary'>
						<label for='renameTextfield' lang-data='rename'>Umbenennen</label>
					</div>
				</div>
				<hr>
				<div class='modal-footer'>
					<button id='renameButtonCancel' class='toggleDarkLight btn btn-outline-light m-1' data-bs-dismiss='modal' style='float: right;'><i class='bi bi-x-circle pe-2'></i><span lang-data="cancel">Abbruch</span></button>
					<button id='renameButtonSave' class='btn btn-outline-success m-1' onclick='saveFileRename();' style='float: right;'><i class='bi bi-save pe-2'></i><span lang-data="save">Speichern</span></button>
				</div>
			</div>
		</div>
	</div>
	<div id='screenshotModal' class='modal fade' tabindex='-1'>
		<div class='modal-xl modal-dialog modal-dialog-centered modal-fullscreen-xl-down'>
			<div class='modal-content'>
				<div class='modal-header'>
					<h5 class='modal-title'><i class='bi bi-tv bigIcon pe-2'></i><span lang-data="displayed-content">angezeigter Inhalt</span></h5>
					<button class='btn-close btn-close-white' data-bs-dismiss='modal'></button>
				</div>
				<div class='modal-body'>
					<figure class='figure mb-0'>
						<img id='screenshotFull' src='piScreenScreenshot.jpg' style='max-width: 100%;' class='w-100 border figure-img img-fluid'></img>
						<figcaption id='screenshotFullTime' class='figure-caption'></figcaption>
						<figcaption id='screenFullContent' class='figure-caption text-break'></figcaption>
					</figure>
				</div>
				<hr>
				<div class='modal-footer'>
					<button id='screenshotButtonCancel' class='btn btn-secondary' data-bs-dismiss='modal' lang-data='ok'>OK</button>
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