#!/bin/bash

[ "$UID" -eq 0 ] || exec sudo "$0" "$@"

#Install dependencies
apt install firefox-esr unclutter apache2 php7.4 cec-utils python3 -y

python3 install.py






