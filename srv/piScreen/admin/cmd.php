<?php
	class cronEntry {
		public function importLine($line) {
			$cutting = true;
			while ($cutting) {
				$cutLine = str_replace("\t\t","\t", $line);
				if (strlen($cutLine) != strlen($line)) {
					$line = $cutLine;
				}
				else {
					$cutting = false;
				}
			}
			$segments = explode("\t", $line);
			if (count($segments) == 6) { //Check if the cron entry is correct
				$this->minute = $segments[0];
				$this->hour = $segments[1];
				$this->day = $segments[2];
				$this->month = $segments[3];
				$this->weekday = $segments[4];
				$this->command = $segments[5];
			}
		}
	}

	if($_GET['id'] == 1) { //Restart Browser
		shell_exec("sudo -u pi /home/pi/piScreen/killBrowser.sh");
		header('Location: .');
	}
	elseif ($_GET['id'] == 2) { //reboot
		header('Location: .');
		shell_exec("sudo reboot");
	}
	elseif ($_GET['id'] == 3) { //Poweroff
		header('Location: .');
		shell_exec("sudo poweroff");
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
		$str   = @file_get_contents('/proc/uptime');
		$num   = floatval($str);
		$uptime = new stdClass();
		$uptime->secs = fmod($num, 60); $num = intdiv($num, 60);
		$uptime->mins = $num % 60;      $num = intdiv($num, 60);
		$uptime->hours =$num % 24;      $num = intdiv($num, 24);
		$uptime->days = $num;
		$systemInfo = new stdClass();
		$systemInfo->uptime = $uptime;
		$systemInfo->displayState = trim(file_get_contents('/media/ramdisk/piScreenDisplay.txt'));
		$systemInfo->cpuTemp = (int)file_get_contents('/sys/class/thermal/thermal_zone0/temp');
		$systemInfo->cpuLoad = sys_getloadavg()[0];

		$free = shell_exec('free');
		$free = (string)trim($free);
		$free_arr = explode("\n", $free);
		$mem = explode(" ", $free_arr[1]);
		$mem = array_filter($mem);
		$mem = array_merge($mem);
		$memory_usage = $mem[2]/$mem[1]*100;

		$systemInfo->ramTotal = (int)$mem[1];
		$systemInfo->ramUsed = (int)$mem[2];
		//$systemInfo->ramUsage = $memory_usage;

		$display = new stdClass();
		$display->standbySet = file_exists('/media/ramdisk/piScreenDisplayStandby');
		$display->onSet = file_exists('/media/ramdisk/piScreenDisplayOn');
		$systemInfo->display = $display;
		echo json_encode($systemInfo);
		//echo "$days Tage, $hours Stunden, $mins Minuten";
	}
	elseif ($_GET['id'] == 6) { //Get Crons
		header("Content-Type: application/json; charset=UTF-8");
		$crons = shell_exec("crontab -l");
		$foundIndex = strpos($crons,"#<piScreen>");
		if ($foundIndex === false) {
			//ERROR
			die();
		}
		$crons = substr($crons, $foundIndex);
		$foundIndex = strpos($crons,"#</piScreen>");
		if ($foundIndex === false) {
			//ERROR
			die();
		}
		$crons = substr($crons,0,$foundIndex + strlen("#</piScreen>"));
		$crons = explode("\n", $crons);

		for ($i = 0; $i < count($crons); $i++) { //Find lines for reboot and screenOff Cron
			if ($crons[$i]) {
				if (substr( $crons[$i], 0, strlen('#<reboot>') ) === '#<reboot>') {
					$rebootLine = $i;
				}
				elseif (substr( $crons[$i], 0, strlen('#</reboot>') ) === '#</reboot>') {
					$rebootEndLine = $i;
				}
				elseif (substr( $crons[$i], 0, strlen('#<screenOff>') ) === '#<screenOff>') {
					$screenOffLine = $i;
				}
				elseif (substr( $crons[$i], 0, strlen('#</screenOff>') ) === '#</screenOff>') {
					$screenOffLineEnd = $i;
				}
			}
		}
		$rebootCrons = [];
		$screenOffCrons = [];
		if ($rebootLine < $rebootEndLine) { //Check if reboot lines in correct Order
			for ($i = $rebootLine + 1; $i < $rebootEndLine; $i++) { //Load lines between
				if (substr($crons[$i],0,1) !== '#') { //Check if line starts with #
					$entry = new cronEntry();
					$entry->importLine($crons[$i]);
					if($entry->command) {
						array_push($rebootCrons,$entry);
					}
				}
			}
		}
		if ($screenOffLine < $screenOffLineEnd) { //Check if screenOff lines in correct Order
			for ($i = $screenOffLine + 1; $i < $screenOffLineEnd; $i++) { //Load lines between
				if (substr($crons[$i],0,1) !== '#') { //Check if line starts with #
					$entry = new cronEntry();
					$entry->importLine($crons[$i]);
					if($entry->command) {
						array_push($screenOffCrons,$entry);
					}
				}
			}
		}
		
		echo json_encode(array(rebootCrons => $rebootCrons, screenOffCrons => $screenOffCrons));

	}
	elseif ($_GET['id'] == 7) {
		var_dump($_POST);
	}
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
?>
