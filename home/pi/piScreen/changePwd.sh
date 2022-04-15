#!/bin/bash
cat /media/ramdisk/piScreenPwd.txt | sudo xargs -0 htpasswd -b /etc/apache2/.htpasswd pi
cat /media/ramdisk/piScreenPwd.txt | sudo xargs -0 -I {} echo pi:{} | sudo chpasswd