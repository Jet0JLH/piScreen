<!doctype html>
<?php
	$syscall = '/home/pi/piScreen/piScreenCmd.py';
	$updateStatusFile = '/media/ramdisk/piScreenUpdateStatus.txt';
	if (isset($_GET['reload'])) {
		echo nl2br(htmlentities(file_get_contents($updateStatusFile)));
		if (file_exists($updateStatusFile)) {
			if (isset($_GET['count'])) {
				$count = $_GET['count'] + 1;
			}
			else {
				$count = 1;
			}
			if ($count > 150) {
				header("Refresh:0; url=update.php?error&count=$count");		
			}
			else {
				header("Refresh:2; url=update.php?reload&count=$count");
			}
		}
		else {
			header('Refresh:0; url=update.php?ready');
		}
	}
	else if (isset($_GET['ready'])) {
		header('Refresh:120; url=.');
		echo nl2br(htmlentities(file_get_contents($updateStatusFile)));
		echo("<h1>Bitte warten, das Update ist abgeschlossen und das Gerät wird neugestartet.</h1>Diese Seite ladet sich in 2 Minuten selber neu");
	}
	else if (isset($_GET['error'])) {
		echo nl2br(htmlentities(file_get_contents($updateStatusFile)));
		echo("<h1>Das Update hat zu lange gebraucht. Etwas scheint schief gelaufen zu sein!</h1>");
	}
	else {
		#header('Refresh:1; url=update.php?reload&count=0');
		#shell_exec("sudo $syscall -v --do-upgrade > $updateStatusFile 2>&1 &");
		#Not operational. Function may be added later
	}
?>
<script>window.scrollTo(0, document.body.scrollHeight);</script>
