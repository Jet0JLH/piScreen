import os
from re import sub
import subprocess

"""
#Configure RAM disk
os.mkdir("/media/ramdisk")
fstab = open("/etc/fstab", "a")
fstab.write("\ntmpfs    /media/ramdisk  tmpfs   defaults,size=5%        0       0")
"""

#Configure Webserver
process = subprocess.Popen(["apt", "install", "firefox-esr", "unclutter", "apache2", "php7.4", "cec-utils", "python3", "-y"])
process.wait()
print("fertig")



















"""
#Configure RAM disk
mkdir /media/ramdisk
echo -e "\ntmpfs    /media/ramdisk  tmpfs   defaults,size=5%        0       0" >> /etc/fstab

#Configure Webserver
systemctl stop apache2
htpasswd -c /etc/apache2/.htpasswd pi
a2dissite 000-default
a2ensite piScreen
a2enmod rewrite
a2enmod ssl

if []



#Generate SSL certificates
mkdir /home/pi/piScreen/certs
cd /home/pi/piScreen/certs
rm *
openssl genrsa -out server.key 4096
openssl req -new -key server.key -out server.csr -sha256 -subj "/C=/ST=/L=/O=piScreen/OU=/CN="
openssl req -noout -text -in server.csr
openssl x509 -req -days 3650 -in server.csr -signkey server.key -out server.crt


"""










