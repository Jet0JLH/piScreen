<?php
	$syscall = '/home/pi/piScreen/piScreenCmd.py';
	if($_GET['id'] == 1) { //Restart Browser
		shell_exec("sudo $syscall --stop-browser");
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
		$page = shell_exec("cat /home/pi/piScreen/page.txt");
		if($hostname != $_POST['hostname']) {
			//Hostname hat sich geändert
			shell_exec("sudo hostnamectl set-hostname '{$_POST['hostname']}'");
		}
		if($page != $_POST['page']) {
			//Page hat sich geändert
			file_put_contents('/home/pi/piScreen/page.txt',$_POST['page']);
		}
		if($_POST['pwd']) {
			$file = '/media/ramdisk/piScreenPwd.txt';
			file_put_contents($file,$_POST['pwd']);
			shell_exec("sudo /home/pi/piScreen/changePwd.sh");
			unlink($file);
		}
		header('Location: .');
	}
	elseif ($_GET['id'] == 5) { //Get Infos
		header("Content-Type: application/json; charset=UTF-8");
		echo shell_exec("$syscall --get-Status");
	}
	/*elseif ($_GET['id'] == 6) { //Old get Crons, ID can used for other command
		
	}*/
	/*elseif ($_GET['id'] == 7) { //Old test, can Used for other command

	}*/
	elseif ($_GET['id'] == 8) { //Display Control
		if ($_GET['cmd'] == 0) {
			shell_exec("touch /media/ramdisk/piScreenDisplayStandby");
		}
		elseif ($_GET['cmd'] == 1) {
			shell_exec("touch /media/ramdisk/piScreenDisplayOn");
		}
		elseif ($_GET['cmd'] == 2) {
			shell_exec("touch /media/ramdisk/piScreenDisplayOff");
		}
		elseif ($_GET['cmd'] == 3) {
			shell_exec("touch /media/ramdisk/piScreenDisplaySwitch");
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
	elseif ($_GET['id'] == 11) { //Get Mainifest
		header("Content-Type: application/json; charset=UTF-8");
		echo file_get_contents('/home/pi/piScreen/manifest.json');
	}
	elseif ($_GET['id'] == 12) { //Get settings
		header("Content-Type: application/json; charset=UTF-8");
		echo file_get_contents('/home/pi/piScreen/settings.json');
	}
?>
