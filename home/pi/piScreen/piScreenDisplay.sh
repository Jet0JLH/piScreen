ramdisk=/media/ramdisk/
displayStatus=$ramdisk"piScreenDisplay.txt"
displayOff=$ramdisk"piScreenDisplayOff"
displayOn=$ramdisk"piScreenDisplayOn"
displayStandby=$ramdisk"piScreenDisplayStandby"
displaySwitchChannel=$ramdisk"piScreenDisplaySwitch"


(while true ; do sleep 5 ; if [ -f $displayOn ] ; then sudo rm $displayOn ; echo "on 0" ; elif [ -f $displayStandby ] ; then sudo rm $displayStandby ; echo "standby 0" ; elif [ -f $displayOff ] ; then sudo rm $displayOff ; echo "off 0" ; elif [ -f $displaySwitchChannel ] ; then sudo rm $displaySwitchChannel ; echo "as 0" ; fi ; echo "pow 0" ; done) | cec-client -d 8 -p 1 -b 5 -t p | grep power  --line-buffered | while read x ; do
	echo $x | awk '{split($0,a,":");print a[2]}' | sed 's/ //' | tee $displayStatus > /dev/null
done

