<?php $syscall = '/home/pi/piScreen/piScreenCmd.py';?>
<!doctype html>
<html>
	<head>
		<link href='/bootstrap/css/bootstrap.min.css' rel='stylesheet'>
		<link rel='stylesheet' href='/bootstrap/icons/bootstrap-icons.css'>
		<link rel='stylesheet' href='styles.css'>
		<link rel='icon' type='image/x-icon' href='/favicon.ico'>
		<title>piScreen Adminpage</title>
	</head>
	<body class='d-flex flex-column min-vh-100'>
		<div class='px-4 py-5 my-2 text-center'>
			<h1 class='display-5 fw-bold'><img src='/piScreen.svg' alt='Logo' width='128' height='128'> piScreen Adminpage</h1>
			<p class='lead mb-4'>Hier lassen sich die wichtigsten PiScreen Funktionen bequem administrieren</p>
		</div>
		<div class='container px-4'>
			<div class='row gx-5'>
				<div class='col col-sm-12 col-lg-6 p-2'>
					<div class='p-3 rounded-3 border shadow'>
						<h1 style='display:inline'>Status</h1> <span id='idle' class='badge bg-success' style='transform: translateY(-50%);'>•</span>
						<p>
							<i class='bi bi-activity'> </i>Aktivität: <span id='active' class='badge rounded-pill bg-secondary'>???</span><br>
							<i class='bi bi-display'> </i>Display Status: <span id='displayState' class='badge rounded-pill bg-secondary'>???</span><br>
							<i class='bi bi-clock-history'></i> Uptime: <span id='uptime'>???</span><br>
							<i class='bi bi-cpu'></i> CPU Last: <span id='cpuLoad'>???</span> %<br>
							<i class='bi bi-thermometer'></i> CPU Temperatur: <span id='cpuTemp'>???</span><br>
							<i class='bi bi-memory'></i> RAM: <span id='ramUsed'>???</span> von <span id='ramTotal'>???</span> belegt (<span id='ramUsage'>???</span> %)
						</p>
					</div>
				</div>
				<div class='col col-sm-12 col-lg-6 p-2'>
					<div class='p-3 rounded-3 border shadow'>
						<h1>Steuern</h1>
						<button id='reloadBtn' type='button' class='btn btn-primary'><i class='bi bi-arrow-clockwise'></i> Browser neu starten</button>
						<button id='restartBtn' type='button' class='btn btn-warning'><i class='bi bi-bootstrap-reboot'></i> Neustarten</button>
						<button id='shutdownBtn' type='button' class='btn btn-danger'><i class='bi bi-power'></i> Herunterfahren</button>
						<br><br>
						<button id='displayOnBtn' type='button' class='btn btn-success'><span id='spinnerDisplayOn' class='spinner-border spinner-border-sm' role='status' hidden=''></span> <i class='bi bi-display'></i> Display an</button>
						<button id='displayStandbyBtn' type='button' class='btn btn-danger'><span id='spinnerDisplayStandby' class='spinner-border spinner-border-sm' role='status' hidden=''></span> <i class='bi bi-display'></i> Display Standby</button>
						<br>
					</div>
				</div>
				<div class='col col-sm-12 col-lg-6 p-2'>
					<div class='p-3 rounded-3 border shadow'>
						<form method='POST' action='cmd.php?id=4'>
							<h1>Einstellungen</h1>
							<div class='form-floating mb-3'>
								<input type='text' class='form-control' name='hostname' id='hostname' value='<?php echo shell_exec('hostname'); ?>'>
								<label for='hostname'>Hostname</label>
							</div>
							<div class='form-floating mb-3'>
								<input type='text' class='form-control' name='page' id='page' value='<?php echo shell_exec("$syscall --get-website"); ?>'>
								<label for='page'>Zu öffnende Seite</label>
							</div>
							<div class='form-floating mb-3'>
								<input type='password' class='form-control' name='pwd' id='pwd'>
								<label for='pwd'>Neues Passwort für den Pi Benutzer</label>
							</div>
							<button type='submit' class='btn btn-primary'><i class='bi bi-save'></i> Speichern</button>
						</form>
					</div>
				</div>
				<div class='col col-sm-12 col-lg-6 p-2'>
					<div class='p-3 rounded-3 border shadow'>
						<h1>Zeitplan</h1>
						<div>
							<div style='float:left;width:auto' class='form-check form-switch'>
							<input id='scheduleExclusionActiv' class='form-check-input' type='checkbox' checked></input>
						</div>
						Unten stehenden Zeitplan ignorieren.
						<div style='display:flex;flex-flow:row wrap;align-items:center;'>
							
							Von <input id='scheduleExclusionFrom' style='display:inline;width:auto' type='date' class='form-control mx-2'></input> bis <input id='scheduleExclusionTo' style='display:inline;width:auto' type='date' class='form-control mx-2'></input></div>
						</div>
						<hr>
						<div id='schedule'>

						</div>
						<br>
						<button id='newScheduleLine' class='btn btn-secondary'>Neue Zeile</button>
						<button id='saveSchedule' class='btn btn-primary'>Speichern</button>
					</div>
				</div>
			</div>
		</div>
		<div id='modal' class='modal fade' tabindex='-1'>
			<div class='modal-dialog modal-dialog-centered'>
				<div class='modal-content'>
					<div class='modal-header'>
						<h5 id='modal-title' class='modal-title'></h5>
						<button type='button' class='btn-close' data-bs-dismiss='modal' aria-label='Schließen'></button>
					</div>
					<div class='modal-body'>
						<p id='modal-body'></p>
					</div>
					<div class='modal-footer'>
						<button id='modal-cancelBtn' type='button' class='btn btn-secondary' data-bs-dismiss='modal'>Abbruch</button>
						<button id='modal-acceptBtn' type='button' class='btn btn-danger'></button>
					</div>
				</div>
			</div>
		</div>
	</body>
	<footer class='bg-dark text-center text-white mt-auto'>
		<div class='text-center p-3'>
			<a id='versionInfoBtn' class='text-white' href='#'>piScreen Info</a>
		</div>
	</footer>
	<script src='/bootstrap/js/bootstrap.bundle.min.js'></script>
	<script src='admin.js'></script>
</html>
