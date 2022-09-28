ramdisk=/media/ramdisk/
displayStatus=$ramdisk"piScreenDisplay.txt"
displayOff=$ramdisk"piScreenDisplayOff"
displayOn=$ramdisk"piScreenDisplayOn"
displayStandby=$ramdisk"piScreenDisplayStandby"
displaySwitchChannel=$ramdisk"piScreenDisplaySwitch"
displayCEC=$ramdisk"piScreenDisplayCEC"
displayDDC=$ramdisk"piScreenDisplayDDC"

#Clear old status
echo "" > $displayStatus

if [ -f $displayCEC ]; then
	(while true ; do sleep 2 ; if [ ! -f $displayCEC ] ; then killall cec-client ; elif [ -f $displayOn ] ; then sudo rm $displayOn ; echo "on 0" ; elif [ -f $displayStandby ] ; then sudo rm $displayStandby ; echo "standby 0" ; elif [ -f $displayOff ] ; then sudo rm $displayOff ; echo "off 0" ; elif [ -f $displaySwitchChannel ] ; then sudo rm $displaySwitchChannel ; echo "as 0" ; fi ; echo "pow 0" ; done) | cec-client -d 8 -p 1 -b 5 -t p | grep power  --line-buffered | while read x ; do
		echo $x | awk '{split($0,a,":");print a[2]}' | sed 's/ //' | tee $displayStatus > /dev/null
	done
elif [ -f $displayDDC ]; then
	while [ -f $displayDDC ] ; do
		if [ -f $displayOn ] ; then
			sudo rm $displayOn
			ddcutil setvcp D6 01
		elif [ -f $displayStandby ] ; then
			sudo rm $displayStandby
			ddcutil setvcp D6 05
			#Code 04 is for stanby, but not every system supports it, so we decided to use 05 instead
		elif [ -f $displayOff ] ; then 
			sudo rm $displayOff
			ddcutil setvcp D6 05
		elif [ -f $displaySwitchChannel ] ; then
			#https://github.com/rockowitz/ddcutil/issues/35
			sudo rm $displaySwitchChannel
			ddcutil setvcp 60 0x0f
		fi
		#https://unix.stackexchange.com/questions/636396/how-to-get-the-status-on-off-lock-of-the-monitor-of-a-remote-host
		status=$(ddcutil -d 1 getvcp d6 |& awk '{ print $NF }')
		if [ $status == "(sl=0x01)" ] ; then
			echo "on" > $displayStatus
		elif [ $status == "(sl=0x05)" ] ; then
			echo "off" > $displayStatus
		else
			echo "unknown" > $displayStatus
		fi
		sleep 2
	done
fi
