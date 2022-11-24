<?php
	$syscall = '/home/pi/piScreen/piScreenCmd.py';
	$error = "EXITCODE1";
	if ($_GET['id'] == 1) { //Restart Browser
		shell_exec("sudo $syscall --restart-browser");
		header('Location: .');
	}
	elseif ($_GET['id'] == 2) { //reboot
		header('Location: .');
		shell_exec("sudo $syscall --reboot");
	}
	elseif ($_GET['id'] == 3) { //Poweroff
		header('Location: .');
		shell_exec("sudo $syscall --shutdown");
	}
	elseif ($_GET['id'] == 4) {//Change hostname
		$hostname = shell_exec('hostname');
		if($hostname != $_POST['hostname']) {
			//Hostname changed
			shell_exec("sudo hostnamectl set-hostname '{$_POST['hostname']}'");
		}
	}
	elseif ($_GET['id'] == 5) { //Get Infos
		header("Content-Type: application/json; charset=UTF-8");
		echo shell_exec("$syscall --get-Status");
	}
	elseif ($_GET['id'] == 6) { //Check for update
		$updateAvailable = shell_exec("$syscall --check-update");
		if ($updateAvailable) {
			echo $updateAvailable;
		} else {
			echo "no-update";
		}
	}
	elseif ($_GET['id'] == 7) { //Set weblogin
		if($_POST['user'] && $_POST['pwd']) {
			echo "true";
			$file = '/media/ramdisk/piScreenPwd.txt';
			file_put_contents($file, $_POST['pwd']);
			shell_exec("sudo $syscall --set-pw '" . $_POST['user'] . "' -f '$file'");
		}
		header('Location: .');
	}
	elseif ($_GET['id'] == 8) { //Display Control
		if ($_GET['cmd'] == 0) {
			shell_exec("$syscall --screen-standby");
		}
		elseif ($_GET['cmd'] == 1) {
			shell_exec("$syscall --screen-on");
		}
		elseif ($_GET['cmd'] == 2) {
			shell_exec("$syscall --screen-off");
		}
		elseif ($_GET['cmd'] == 3) {
			shell_exec("$syscall --screen-switch-input");
		}
	}
	elseif ($_GET['id'] == 9) { //Set Schedule
		if ($_GET['cmd'] == "add"){
			$parameterString = "";
			if ($_GET['enabled'] != NULL) {
				$parameterString .= " --enabled " . $_GET['enabled'];
			}
			if ($_GET['command'] != NULL) {
				$parameterString .= " --command " . $_GET['command'];
			}
			if ($_GET['parameter'] != NULL) {
				$parameterString .= " --parameter " . $_GET['parameter'];
			}
			if ($_GET['start'] != NULL) {
				$parameterString .= " --start \"" . $_GET['start'] . "\"";
			}
			if ($_GET['end'] != NULL) {
				$parameterString .= " --end \"" . $_GET['end'] . "\"";
			}
			if ($_GET['pattern'] != NULL) {
				$parameterString .= " --pattern \"" . $_GET['pattern'] . "\"";
			}
			if ($_GET['commandset'] != NULL) {
				$parameterString .= " --commandset " . $_GET['commandset'];
			}
			//echo "$syscall --add-cron$parameterString";
			echo shell_exec("$syscall --add-cron $parameterString");

		} elseif ($_GET['cmd'] == "update") {
			if ($_GET['index'] == NULL) {
				echo $error;
				return;
			}
			$parameterString = " --index " . $_GET['index'];
			if ($_GET['enabled'] != NULL) {
				$parameterString .= " --enabled " . $_GET['enabled'];
			}
			if ($_GET['command'] != NULL) {
				$parameterString .= " --command " . $_GET['command'];
			}
			if ($_GET['parameter'] != NULL) {
				$parameterString .= " --parameter " . $_GET['parameter'];
			}
			if ($_GET['start'] == " ") {
				$parameterString .= " --start";
			} elseif ($_GET['start'] != NULL) {
				$parameterString .= " --start \"" . $_GET['start'] . "\"";
			}
			if ($_GET['end'] == " ") {
				$parameterString .= " --end";
			} elseif ($_GET['end'] != NULL) {
				$parameterString .= " --end \"" . $_GET['end'] . "\"";
			}
			if ($_GET['pattern'] != NULL) {
				$parameterString .= " --pattern \"" . $_GET['pattern'] . "\"";
			}
			if ($_GET['commandset'] != NULL) {
				$parameterString .= " --commandset " . $_GET['commandset'];
			}
			//echo "$syscall --update-cron$parameterString";
			echo shell_exec("$syscall --update-cron$parameterString");

		} elseif ($_GET['cmd'] == "delete") {
			if ($_GET['index'] == NULL) {
				echo $error;
				return;
			}
			$parameterString = " --index " . $_GET['index'];
			//echo "$syscall --delete-cron$parameterString";
			echo shell_exec("$syscall --delete-cron$parameterString");
		}
	}
	elseif ($_GET['id'] == 10) { //Get Display Schedule
		header("Content-Type: application/json; charset=UTF-8");
		echo file_get_contents('/home/pi/piScreen/schedule.json');
	}
	elseif ($_GET['id'] == 11) { //Get Manifest
		header("Content-Type: application/json; charset=UTF-8");
		echo file_get_contents('/home/pi/piScreen/manifest.json');
	}
	elseif ($_GET['id'] == 12) { //Get settings
		header("Content-Type: application/json; charset=UTF-8");
		echo file_get_contents('/home/pi/piScreen/settings.json');
	}
	elseif ($_GET['id'] == 13) { //Set language
		$data = json_decode(file_get_contents('/home/pi/piScreen/settings.json'), true);
		$data['settings']['language'] = $_GET['lang'];
		file_put_contents('/home/pi/piScreen/settings.json', json_encode($data, JSON_PRETTY_PRINT));
	}
	elseif ($_GET['id'] == 14) { //Set diplay control protocol
		if ($_GET['protocol'] == 'cec') {
			shell_exec("$syscall --set-display-protocol cec");
		}
		elseif ($_GET['protocol'] == 'ddc') {
			shell_exec("$syscall --set-display-protocol ddc");
		}
	}
	elseif ($_GET['id'] == 15) { //Get diplay control protocol
		echo shell_exec("$syscall --get-display-protocol");
	}
	elseif ($_GET['id'] == 16) { //Set diplay orientation
		$orientation = $_GET['orientation'];
		if ($orientation >= 0 && $orientation <= 3) {
			shell_exec("sudo -u pi $syscall --set-display-orientation $orientation");
		}
	}
	elseif ($_GET['id'] == 17) { //Get diplay orientation
		echo shell_exec("$syscall --get-display-orientation-settings");
	}
	elseif ($_GET['id'] == 18) { //cron functions
		/*if ($_GET['cmd'] == "add") {
			$parameter = $_GET['parameter'];
			echo shell_exec("$syscall --add-cron ");
		}
		elseif ($_GET['cmd'] == "update") {
			//shell_exec("$syscall --screen-on");
		}
		elseif ($_GET['cmd'] == "delete") {
			echo shell_exec("$syscall --delete-cron " . $_GET['entryId']);
		}*/
	}
	elseif ($_GET['id'] == 19) { //commandset functions
		//echo shell_exec("$syscall --get-display-orientation-settings");
	}
	elseif ($_GET['id'] == 20) { //Trigger functions
		if ($_GET['cmd'] == "add"){
			$parameterString = "";
			if ($_GET['enabled'] != NULL) {
				$parameterString .= " --enabled " . $_GET['enabled'];
			}
			if ($_GET['trigger'] != NULL) {
				$parameterString .= " --trigger " . $_GET['trigger'];
			}
			if ($_GET['command'] != NULL) {
				$parameterString .= " --command " . $_GET['command'];
			}
			if ($_GET['parameter'] != NULL) {
				$parameterString .= " --parameter " . $_GET['parameter'];
			}
			if ($_GET['commandset'] != NULL) {
				$parameterString .= " --commandset " . $_GET['commandset'];
			}
			//echo "$syscall --add-trigger$parameterString";
			echo shell_exec("$syscall --add-trigger$parameterString");

		} elseif ($_GET['cmd'] == "update") {
			if ($_GET['index'] == NULL) {
				echo $error;
				return;
			}
			$parameterString = " --index " . $_GET['index'];
			if ($_GET['enabled'] != NULL) {
				$parameterString .= " --enabled " . $_GET['enabled'];
			}
			if ($_GET['triggerID'] != NULL) {
				$parameterString .= " --triggerID " . $_GET['triggerID'];
			}
			if ($_GET['command'] != NULL) {
				$parameterString .= " --command " . $_GET['command'];
			}
			if ($_GET['parameter'] != NULL) {
				$parameterString .= " --parameter " . $_GET['parameter'];
			}
			if ($_GET['commandset'] != NULL) {
				$parameterString .= " --commandset " . $_GET['commandset'];
			}
			//echo "$syscall --update-trigger$parameterString";
			echo shell_exec("$syscall --update-trigger$parameterString");

		} elseif ($_GET['cmd'] == "delete") {
			if ($_GET['index'] == NULL) {
				echo $error;
				return;
			}
			$parameterString = " --index " . $_GET['index'];
			//echo "$syscall --delete-trigger$parameterString";
			echo shell_exec("$syscall --delete-trigger$parameterString");
		}
	}
	elseif ($_GET['id'] == 21) { //Get current website
		echo shell_exec("$syscall --get-website");
	}
	elseif ($_GET['id'] == 22) { //Run firstrun
		echo shell_exec("$syscall --schedule-firstrun");
	}

	
?>
