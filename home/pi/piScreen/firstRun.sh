#!/bin/bash

#Skripte ausführbar machen

sudo apt install firefox-esr-l10n-de unclutter apache2 php7.4 cec-utils

echo Erstelle notwendige Verzeichnisse
sudo mkdir /media/ramdisk
sudo mkdir /home/pi/piScreen/certs

echo Setze Berechtigungen
setfacl -Rm d:u:www-data:rwx /home/pi/piScreen/
setfacl -Rm u:www-data:rwx /home/pi/piScreen/
setfacl -Rm d:u:pi:rwx /home/pi/piScreen/
setfacl -Rm u:pi:rwx /home/pi/piScreen/

setfacl -Rm d:u:www-data:rwx /srv/piScreen/
setfacl -Rm u:www-data:rwx /srv/piScreen/
setfacl -Rm d:u:pi:rwx /srv/piScreen/
setfacl -Rm u:pi:rwx /srv/piScreen/

echo Erstelle notwendige ramdisk
sudo su -c 'echo -e "\ntmpfs    /media/ramdisk  tmpfs   defaults,size=5%        0       0" >> /etc/fstab'

sudo systemctl stop apache2
htpasswd -c /etc/apache2/.htpasswd pi
setfacl -Rm u:www-data:rwx /etc/apache2/.htpasswd

sudo a2dissite 000-default
sudo a2ensite piScreen
sudo a2enmod rewrite
sudo a2enmod ssl
#Pfad /srv für Apache erlauben /etc/apache2/apache2.conf
echo Generiere Zertifikate für Apache
cd /home/pi/piScreen/certs
rm ./*
openssl genrsa -out server.key 4096
openssl req -new -key server.key -out server.csr -sha256 -subj "/C=DE/ST=BW/L=/O=PiScreen/OU=/CN="
openssl req -noout -text -in server.csr
openssl x509 -req -days 3650 -in server.csr -signkey server.key -out server.crt

#Apache kann nun in Betrieb genommen werden
echo Starte Apache
sudo systemctl enable apache2
sudo systemctl start apache2


#visudo
#www-data        ALL=(ALL:ALL)   NOPASSWD:/usr/sbin/poweroff
#www-data        ALL=(ALL:ALL)   NOPASSWD:/usr/sbin/reboot
#www-data        ALL=(ALL:ALL)   NOPASSWD:/home/pi/piScreen/killBrowser.sh
#www-data        ALL=(ALL:ALL)   NOPASSWD:/usr/bin/hostnamectl
#www-data        ALL=(ALL:ALL)   NOPASSWD:/home/pi/piScreen/changePwd.sh

#PythonCron in Crontab von www-data eintragen
#raspi-config display blanking disable
#/etc/xdg/lxsession/LXDE-pi/autostart #@lxpanel --profile LXDE-pi
#Hintergrundbid auf no-image ändern
#Wastebin & external Disk ausblenden
#Firefox auf deutsch stellen
#about:config toolkit.startup.max_resumed_crashes = -1 (steht auf 3)
