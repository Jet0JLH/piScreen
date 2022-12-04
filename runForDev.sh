#!/bin/bash
# This script is used for hardlink files form dev directory to real paths
# This script will delete the real directories
[ "$UID" -eq 0 ] || exec sudo "$0" "$@"

parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$parent_path"

rm -R /home/pi/piScreen
rm -R /srv/piScreen
rm /etc/apache2/sites-available/piScreen.conf
rm /home/pi/.config/autostart/piScreenCore.desktop
rm /etc/firefox-esr/piScreen.js


chmod +x ./home/pi/piScreen/*.sh
chmod +x ./home/pi/piScreen/*.py

ln -s "$parent_path/home/pi/piScreen/" /home/pi/piScreen
ln -s "$parent_path/srv/piScreen/" /srv/piScreen
ln -s "$parent_path/etc/apache2/sites-available/piScreen.conf" /etc/apache2/sites-available/piScreen.conf
mkdir -p /home/pi/.config/autostart/
ln -s "$parent_path/home/pi/.config/autostart/piScreenCore.desktop" /home/pi/.config/autostart/piScreenCore.desktop
chown -R pi:pi /home/pi/.config/autostart/
ln -s "$parent_path/defaults/firefoxPiScreen.js" /etc/firefox-esr/piScreen.js
ln -s /media/ramdisk/piScreenScreenshot.png /srv/piScreen/admin/


setfacl -Rm d:u:www-data:rwx /home/pi/piScreen
setfacl -Rm u:www-data:rwx /home/pi/piScreen
setfacl -Rm d:u:pi:rwx /home/pi/piScreen
setfacl -Rm u:pi:rwx /home/pi/piScreen

setfacl -Rm d:u:www-data:rwx ./home/pi/piScreen/
setfacl -Rm u:www-data:rwx ./home/pi/piScreen/
setfacl -Rm d:u:pi:rwx ./srv/piScreen/
setfacl -Rm u:pi:rwx ./srv/piScreen/

git update-index --skip-worktree home/pi/piScreen/settings.json
git update-index --skip-worktree home/pi/piScreen/schedule.json
git update-index --skip-worktree srv/piScreen/admin/piScreenScreenshot.png

export DISPLAY=:0
sudo -u pi firefox-esr -CreateProfile piScreen

if test -f "./home/pi/piScreen/settings.json"; then
	echo "[Ignore] Settings already exists"
else
	cp ./defaults/default_settings.json ./home/pi/piScreen/settings.json
fi
if test -f "./home/pi/piScreen/schedule.json"; then
	echo "[Ignore] schedule already exists"
else
	cp ./defaults/default_schedule.json ./home/pi/piScreen/schedule.json
fi
if test -f "/etc/apache2/.piScreen_htpasswd"; then
	echo "[Ignore] Weblogin Credentials alrady exists"
else
	echo -e "[INFO] Default Credentials for Weblogin are set!\nuser: pi\npw: piScreen"
	cp ./defaults/.piScreen_htpasswd /etc/apache2/.piScreen_htpasswd
	chown root:www-data /etc/apache2/.piScreen_htpasswd
	chmod 640 /etc/apache2/.piScreen_htpasswd
fi

systemctl restart apache2
