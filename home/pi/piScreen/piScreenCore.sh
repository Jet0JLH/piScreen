#!/bin/bash
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
		cat /home/pi/piScreen/page.txt | xargs firefox -kiosk -private-window &
		sleep 5
		processID=$(pgrep -x $browser)
	fi
	sleep 1
	#echo 'pow 0' | cec-client -s -d 1 | grep 'power status:' | sed 's/^.*: //' > /media/ramdisk/piScreenDisplay.txt
done
