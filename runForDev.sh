#!/bin/bash
# This script is used for hardlink files form dev directory to real paths
# This script will delete the real directories
[ "$UID" -eq 0 ] || exec sudo "$0" "$@"

rm -R /home/pi/piScreen
rm -R /srv/piScreen
rm /etc/apache2/sites-available/piScreen.conf

chmod +x /home/pi/piScreenDev/piScreen/home/pi/piScreen/*.sh
chmod +x /home/pi/piScreenDev/piScreen/home/pi/piScreen/*.py

ln -s /home/pi/piScreenDev/piScreen/home/pi/piScreen/ /home/pi/piScreen
ln -s /home/pi/piScreenDev/piScreen/srv/piScreen/ /srv/piScreen
ln -s /home/pi/piScreenDev/piScreen/etc/apache2/sites-available/piScreen.conf /etc/apache2/sites-available/piScreen.conf

setfacl -Rm d:u:www-data:rwx /home/pi/piScreen
setfacl -Rm u:www-data:rwx /home/pi/piScreen
setfacl -Rm d:u:pi:rwx /home/pi/piScreen
setfacl -Rm u:pi:rwx /home/pi/piScreen

setfacl -Rm d:u:www-data:rwx /home/pi/piScreenDev/piScreen/home/pi/piScreen/
setfacl -Rm u:www-data:rwx /home/pi/piScreenDev/piScreen/home/pi/piScreen/
setfacl -Rm d:u:pi:rwx /home/pi/piScreenDev/piScreen/srv/piScreen/
setfacl -Rm u:pi:rwx /home/pi/piScreenDev/piScreen/srv/piScreen/



systemctl restart apache2