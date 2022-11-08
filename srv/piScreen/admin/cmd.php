<?php
	$syscall = '/home/pi/piScreen/piScreenCmd.py';
	if($_GET['id'] == 1) { //Restart Browser
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
	elseif ($_GET['id'] == 4) {
		$hostname = shell_exec('hostname');
		$page = shell_exec("$syscall --get-website");
		if($hostname != $_POST['hostname']) {
			//Hostname hat sich geändert
			shell_exec("sudo hostnamectl set-hostname '{$_POST['hostname']}'");
		}
		if($page != $_POST['page']) {
			//Page hat sich geändert
			shell_exec($syscall . " --set-website " . $_POST['page']);
		}
		if($_POST['user'] && $_POST['pwd']) {
			$file = '/media/ramdisk/piScreenPwd.txt';
			file_put_contents($file,$_POST['pwd']);
			shell_exec("sudo $syscall --set-pw '" . $_POST['user'] . "' -f '$file'");
		}
		header('Location: .');
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
	/*elseif ($_GET['id'] == 7) { //Old test, can Used for other command

	}*/
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
	elseif ($_GET['id'] == 9) { //Set Display Schedule
		file_put_contents('/home/pi/piScreen/cron.json',file_get_contents('php://input'));
		echo 'true';
	}
	elseif ($_GET['id'] == 10) { //Get Display Schedule
		header("Content-Type: application/json; charset=UTF-8");
		echo file_get_contents('/home/pi/piScreen/cron.json');
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
?>
