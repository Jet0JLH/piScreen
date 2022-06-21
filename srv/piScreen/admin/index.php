<?php $syscall = '/home/pi/piScreen/piScreenCmd.py';?>
<!doctype html>
<html>
	<head>
		<link id='theme' href='/bootstrap/css/bootstrap.min.css' rel='stylesheet'>
		<link rel='stylesheet' href='/bootstrap/icons/bootstrap-icons.css'>
		<link rel='stylesheet' href='styles.css'>
		<link rel='icon' type='image/x-icon' href='/favicon.ico'>
		<title>piScreen Adminpage</title>
	</head>
	<body>
		<main class='container'>
			<div class='px-4 py-5 my-2 text-center'>
				<button class='btn btn-outline-secondary' id='darkmodeBtn'><i class='bi bi-moon'></i></button>
				<select id='languageSelect' onchange='fetchLanguage(value)' class='form-select border-secondary' aria-label='language'>
					<option id='de' value='de'>🇩🇪 Deutsch</option>
					<option id='en' value='en'>🇬🇧 English</option>
				</select>
				<h1 class='display-5 fw-bold'><img src='/piScreen.svg' alt='Logo' width='128' height='128'> <span lang-data='big-header'>piScreen Adminpage</span></h1>
				<p class='lead mb-4' lang-data='small-header'>Hier lassen sich die wichtigsten piScreen Funktionen bequem administrieren</p>
			</div>
			<div id='masonry' class='row' data-masonry='{&quot;percentPosition&quot;: true }'>
				<div class='col-sm-12 col-lg-6 mb-4'>
					<div class='card p-3 shadow'>
						<div class='pb-3' style='float:left'><h1 style='display:inline'>Status</h1> <span id='idle' class='badge bg-success'>&nbsp;</span></div>
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
						<h1 class='pb-2' lang-data='control-tile-header'>Steuern</h1>
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
						<h1 class='pb-2' lang-data='info-tile-header'>Info</h1>
						<figure class='figure mb-0'>
							<img id='screenshot' src='piScreenScreenshot.png' style='max-width: 100%' class='border figure-img img-fluid'></img>
							<figcaption id='screenshotTime' class='figure-caption'></figcaption>
						</figure>
						<hr>
						<div id='info-footer'>
							<button id='versionInfoBtn' class='btn btn-primary' lang-data='about-info'>piScreen Info</button>
						</div>
					</div>
				</div>
				<div class='col-sm-12 col-lg-6 mb-4'>
					<div class='card p-3 shadow'>
						<h1 class='pb-2' lang-data='settings-tile-header'>Einstellungen</h1>
						<form method='POST' action='cmd.php?id=4'>
							<div class='form-floating mb-3'>
								<input type='text' class='form-control' name='hostname' id='hostname' value='<?php echo shell_exec('hostname'); ?>'>
								<label for='hostname' lang-data='hostname'>Hostname</label>
							</div>
							<div class='form-floating mb-3'>
								<input type='text' class='form-control' name='page' id='page' value='<?php echo shell_exec("$syscall --get-website"); ?>'>
								<label for='page' lang-data='page-shown-url'>Zu öffnende Seite</label>
							</div>
							<div class='form-floating mb-3'>
								<input type='text' class='form-control' name='user' id='user'>
								<label for='user' lang-data='username-web'>Benutzername für Weblogin</label>
							</div>
							<div class='form-floating mb-3'>
								<input type='password' class='form-control' name='pwd' id='pwd'>
								<label for='pwd' lang-data='password-web'>Passwort für Weblogin</label>
							</div>
							<button type='submit' class='btn btn-primary' lang-data='save'><i class='bi bi-save'></i> Speichern</button>
						</form>
					</div>
				</div>
				<div class='col-lg-12 col-xl-6 mb-4'>
					<div class='card p-3 shadow'>
						<h1 class='pb-2' lang-data='timeschedule-tile-header'>Zeitplan</h1>
						<div style='display:flex;flex-flow:row wrap;align-items:center;'>
							<div style='width:auto' class='form-check form-switch'>
							<input id='scheduleExclusionActiv' class='form-check-input' type='checkbox' checked></input>
						</div>
						<span lang-data='ignore-timeschedule'>Zeitplan ignorieren</span> 
						<div class='mx-1' style='display:flex;flex-flow:row wrap;align-items:center;'>
							<span lang-data='from'>Von</span> <input id='scheduleExclusionFrom' style='display:inline;width:auto' type='date' class='form-control mx-2'></input> <span lang-data='to'>bis</span> <input id='scheduleExclusionTo' style='display:inline;width:auto' type='date' class='form-control mx-2'></input></div>
						</div>
						<hr>
						<div id='schedule'>

						</div>
						<div class='btn-group pt-2' role='group' aria-label='Basic mixed styles example'>
							<button id='newScheduleLine' class='btn btn-secondary' lang-data='new-line'>Neue Zeile</button>
							<button id='saveSchedule' class='btn btn-primary' lang-data='save'>Speichern</button>
						</div>
					</div>
				</div>
			</div>
		</main>
		<div id='modal' class='modal fade' tabindex='-1'>
			<div class='modal-dialog modal-dialog-centered'>
				<div class='modal-content'>
					<div class='modal-header'>
						<h5 class='modal-title'></h5>
						<button type='button' class='btn-close' data-bs-dismiss='modal' aria-label='Schließen'></button>
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