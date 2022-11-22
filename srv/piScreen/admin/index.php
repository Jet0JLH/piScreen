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
				<button class='btn btn-outline-secondary' id='darkmodeBtn' onclick='toggleDarkmode();'><i class='bi bi-moon'></i></button>
				<select id='languageSelect' onchange='fetchLanguage(value)' class='form-select border-secondary'>
					<option id='de' value='de'>🇩🇪 Deutsch</option>
					<option id='en' value='en'>🇬🇧 English</option>
				</select>
				<h1 class='display-5 fw-bold'><img src='/piScreen.svg' alt='Logo' width='128' height='128'> <span lang-data='big-header'>piScreen Adminpage</span></h1>
				<p class='lead mb-4' lang-data='small-header'>Hier lassen sich die wichtigsten piScreen Funktionen bequem administrieren</p>
			</div>
			<div id='masonry' class='row' data-masonry='{&quot;percentPosition&quot;: true }'>
				<div class='col-sm-12 col-lg-6 mb-4'>
					<div class='card p-3 shadow'>
						<div class='pb-3' style='float:left'><h1 style='display:inline'><i class='bi-lightbulb bigIcon px-2'></i><span lang-data='status-tile-header'>Status</span></h1> <span id='idle' class='badge bg-success'>&nbsp;</span></div>
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
						<h1 class='pb-2'><i class='bi-lightning-charge bigIcon px-2'></i><span lang-data='control-tile-header'>Steuern</span></h1>
						<div class='row'>
							<div class='col-4'>
								<button id='reloadBtn' type='button' class='btn btn-primary w-100 my-1'><i class='bi bi-arrow-clockwise btn-icon-xxl'></i><br><span lang-data='restart-browser'>Browser neu starten</span></button>
							</div>
							<div class='col-4'>
								<button id='restartBtn' type='button' class='btn btn-warning w-100 my-1'><i class='bi bi-bootstrap-reboot btn-icon-xxl'></i><br><span lang-data='restart-device'>Neustarten</span></button>
							</div>
							<div class='col-4'>
								<button id='shutdownBtn' type='button' class='btn btn-danger w-100 my-1'><i class='bi bi-power btn-icon-xxl'></i><br><span lang-data='shutdown-device'>Ausschalten</span></button>
							</div>
						</div>
						<div class='row'>
							<div class='col-4'>
								<button id='displayOnBtn' type='button' class='btn btn-success w-100 my-1'><span id='spinnerDisplayOn' class='spinner-border spinner-border-sm' role='status' hidden=''></span> <i class='bi bi-display btn-icon-xxl'></i><br><span lang-data='display-on'>Display an</span></button>
							</div>
							<div class='col-4'>
								<button id='displayStandbyBtn' type='button' class='btn btn-danger w-100 my-1'><span id='spinnerDisplayStandby' class='spinner-border spinner-border-sm' role='status' hidden=''></span> <i class='bi bi-display btn-icon-xxl'></i><br><span lang-data='display-off'>Display Standby</span></button>
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
						<button id='versionInfoBtn' class='btn btn-primary' lang-data='about-info'>piScreen Info</button>
						</div>
					</div>
				</div>
				<div class='col-sm-12 col-lg-6 mb-4'>
					<div class='card p-3 shadow'>
						<h1 class='pb-2'><i class='bi-gear bigIcon px-2'></i><span lang-data='settings-tile-header'>Einstellungen</span></h1>
						<div class="accordion accordion-flush" id="settingsAccordion">
							<div class="accordion-item" style='background-color: transparent;'>
								<div id="collapseMainSettings" class="accordion-collapse collapse show" data-bs-parent="#settingsAccordion">
									<div class="accordion-body p-0">
										<table style='width: 100%;'>
											<tr>
												<td>
													<div class='form-floating mb-3'>
														<input type='text' class='form-control' id='settingsHostnameInput' value='<?php echo shell_exec('hostname'); ?>' onkeyup='settingNotSaved("settingsButtonSaveHostname");'>
														<label for='settingsHostnameInput' lang-data='hostname'>Hostname</label>
													</div>
												</td>
												<td style='width: 8%;'>
													<button id='settingsButtonSaveHostname' type='button' class='btn btn-success ms-3 mb-3' onclick='setHostname("settingsHostnameInput");'><i class='bi bi-check2'></i></button>
												</td>
											</tr>
											<tr>
												<td>
													<div class='form-floating mb-3'>
														<select id='displayProtocolSelect' onchange='settingNotSaved("settingsButtonSaveDisplayProtocol");' class='form-select border-secondary'>
															<option id='cec' value='cec' lang-data='cec'>CEC</option>
															<option id='ddc' value='ddc' lang-data='ddc'>DDC/CI</option>
														</select>
														<label for="displayProtocolSelect" lang-data="display-protocol">Display Protokoll</label>
													</div>
												</td>
												<td style='width: 8%;'>
													<button id='settingsButtonSaveDisplayProtocol' type='button' class='btn btn-success ms-3 mb-3' onclick='setDisplayProtocol();'><i class='bi bi-check2'></i></button>
												</td>
											</tr>
											<tr>
												<td>
													<div class='form-floating mb-3'>
														<select id='displayOrientationSelect' onchange='settingNotSaved("settingsButtonSaveDisplayOrientation");' class='form-select border-secondary'>
															<option id='horizontal' value='0' lang-data='horizontal'>Horizontal</option>
															<option id='vertical' value='1' lang-data='vertical'>Vertikal</option>
															<option id='horizontalInverted' value='2' lang-data='rotated-horizontally'>Horizontal gedreht</option>
															<option id='verticalInverted' value='3' lang-data='rotated-vertically'>Vertikal gedreht</option>
														</select>
														<label for="displayOrientationSelect" lang-data="display-orientation">Displayausrichtung</label>
													</div>
												</td>
												<td style='width: 8%;'>
													<button id='settingsButtonSaveDisplayOrientation' type='button' class='btn btn-success ms-3 mb-3' onclick='setDisplayOrientation();'><i class='bi bi-check2'></i></button>
												</td>
											</tr>
										</table>
										<button type='button' id='showLoginSettings' class='btn btn-outline-primary' data-bs-toggle="collapse" data-bs-target="#collapseLoginSettings"><i class='bi bi-pencil-square pe-2'></i><span lang-data="edit-weblogin">Weblogindaten bearbeiten</span></button>
									</div>
								</div>
							</div>
							<div class="accordion-item" style='background-color: transparent;'>
								<div id="collapseLoginSettings" class="accordion-collapse collapse" data-bs-parent="#settingsAccordion">
									<div class="accordion-body p-0">
										<div class='form-floating mb-3'>
											<input type='text' class='form-control' id='webUserInput'>
											<label for='webUserInput' lang-data='username-web'>Benutzername für Weblogin</label>
										</div>
										<div class='form-floating mb-3'>
											<input type='password' class='form-control' id='webPasswordInput'>
											<label for='webPasswordInput' lang-data='password-web'>Passwort für Weblogin</label>
										</div>
										<button type='button' id='saveAndShowMainSettings' class='btn btn-outline-success' data-bs-toggle="collapse" data-bs-target="#collapseMainSettings" onclick='setWebLoginAndPassword();'><i class='bi bi-save pe-2'></i><span lang-data="save-weblogin">Weblogindaten speichern</span></button>
										<button type='button' id='cancelAndShowMainSettings' class='btn btn-outline-primary' data-bs-toggle="collapse" data-bs-target="#collapseMainSettings"><i class='bi bi-arrow-left pe-2'></i><span lang-data="back">Zurück</span></button>
									</div>
								</div>
							</div>
						</div>
					</div>
				</div>
				<div class='col-lg-12 col-xl-6 mb-4'>
					<div class='card p-3 shadow'>
					<h1 class='pb-2'><i class='bi bi-calendar2-day bigIcon px-2'></i><span lang-data='timeschedule-tile-header'>Zeitplan</span></h1>
						<div class="accordion" id="scheduleAccordion">
							<div class="accordion-item" style='background-color: transparent;'>
								<div id="collapseTwo" class="accordion-collapse collapse show" data-bs-parent="#scheduleAccordion">
									<div class="accordion-body p-0">
										<!--<div style='display:flex;flex-flow:row wrap;align-items:center;'>
											<div style='width:auto' class='form-check form-switch'>
											<input id='scheduleExclusionActiv' class='form-check-input' type='checkbox' checked></input>
										</div>
										<span lang-data='ignore-timeschedule'>Zeitplan ignorieren</span> 
										<div class='mx-1' style='display:flex;flex-flow:row wrap;align-items:center;'>
											<span lang-data='from'>Von</span> <input id='scheduleExclusionFrom' style='display:inline;width:auto' type='date' class='form-control mx-2'></input> <span lang-data='to'>bis</span> <input id='scheduleExclusionTo' style='display:inline;width:auto' type='date' class='form-control mx-2'></input></div>
										</div>
										<hr>-->
										<!--<div class='form-check form-switch m-3' style='display: flex; flex-flow: row wrap; align-items: center;'>
											<input class="form-check-input" type="checkbox" role="switch" id="startupTriggerSwitch" onchange="" checked></input>
											<label for="startupTriggerSwitch" class="px-2">Startup trigger</label>
											<div class='form-floating mb-3'>
												<select id='startupTriggerSelect' class='form-select border-secondary' onchange=''>

												</select>
												<label for="startupTriggerSelect">Trigger auswählen</label>
											</div>

										</div>-->
										<div class="accordion" id="entryCollectionAccordion">

										</div>
										<button id='newScheduleEntry' class='btn btn-outline-success mt-2' onclick='generateNewScheduleEntry()'><i class='bi bi-plus-lg pe-2'></i><span lang-data='new-entry'>Neuer Eintrag</span></button>
										<button id='firstRunButton' class='btn btn-outline-warning mt-2 px-2' onclick="sendHTTPRequest('GET', 'cmd.php?id=22', true);"><i class='bi bi-play pe-2'></i><span lang-data='first-run'>firstrun</span></button>
										<div class='btn-group pt-2' role='group' style='float: right; display: none;'>
											<button id='importSchedule' class='btn btn-outline-primary' onclick='importSchedule()'><i class='bi bi-upload pe-2'></i><span lang-data='import-schedule'>Import</span></button>
											<button id='exportSchedule' class='btn btn-outline-primary' onclick='download("cmd.php?id=10", "schedule.json")'><i class='bi bi-download pe-2'></i><span lang-data='export-schedule'>Export</span></button>
										</div>
										<button id='showEvents' class='btn btn-outline-primary' data-bs-toggle="collapse" data-bs-target="#collapseOne" hidden>Events bearbeiten</button>
									</div>
								</div>
							</div>

							<div class="accordion-item" style='background-color: transparent;'>
								<div id="collapseOne" class="accordion-collapse collapse" data-bs-parent="#scheduleAccordion">
								<h3 class='pb-2 accordion-header' id="headingOne">Events bearbeiten</h3>
									<div class="accordion-body p-0">
										<div class="accordion accordion-flush" id="eventsAccordion">
											<div class="accordion-item">
												<h2 class="accordion-header" id="headingOne">
													<button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#collapseOneEvents">
													Accordion Item #1
													</button>
												</h2>
												<div id="collapseOneEvents" class="accordion-collapse collapse" data-bs-parent="#eventsAccordion">
													<div class="accordion-body">

													</div>
												</div>
											</div>
											<div class="accordion-item">
												<h2 class="accordion-header" id="headingTwoEvents">
													<button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapseTwoEvents">
													Accordion Item #2
													</button>
												</h2>
												<div id="collapseTwoEvents" class="accordion-collapse collapse" data-bs-parent="#eventsAccordion">
													<div class="accordion-body">

													</div>
												</div>
											</div>
										</div>
										<button id='showSchedule' class='btn btn-outline-primary' data-bs-toggle="collapse" data-bs-target="#collapseTwo">Events speichern</button>
									</div>
								</div>
							</div>
						</div>
					</div>
				</div>
			</div>
		</main>
		<div id='modal' class='modal-lg fade' tabindex='-1'>
			<div class='modal-dialog modal-dialog-centered'>
				<div class='modal-content'>
					<div class='modal-header'>
						<h5 class='modal-title'></h5>
						<button type='button' class='btn-close' data-bs-dismiss='modal'></button>
					</div>
					<div class='modal-body'>

					</div>
					<div class='modal-footer'>
						<button id='modal-cancelBtn' type='button' class='btn btn-secondary' data-bs-dismiss='modal' lang-data='cancel'>Abbruch</button>
						<button id='modal-actionBtn' type='button' class='btn'></button>
					</div>
				</div>
			</div>
		</div>
	</body>
	<script src='/bootstrap/js/bootstrap.bundle.min.js'></script>
	<script src='/masonry.pkgd.min.js'></script>
	<script src='admin.js'></script>
</html>