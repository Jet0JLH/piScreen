#!/bin/bash
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$parent_path"
touch /media/ramdisk/piScreenDisplayOn
touch /media/ramdisk/piScreenDisplaySwitch
sleep 10
export DISPLAY=:0
browser=firefox-esr
processID=$(pgrep -x $browser)

unclutter -idle 5 &
/home/pi/piScreen/piScreenDisplay.sh &

while [ true ] ; do
	kill -0 $processID
	if [ $? -gt 0 ] ; then
		echo Kein Browserprozess aktiv
		./piScreenCmd.py --start-browser
		sleep 5
		processID=$(pgrep -x $browser)
	fi
	sleep 1
done
