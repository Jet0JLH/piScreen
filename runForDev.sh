#!/bin/bash
# This script is used for hardlink files form dev directory to real paths
# This script will delete the real directories
[ "$UID" -eq 0 ] || exec sudo "$0" "$@"

parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$parent_path"

#Remove original paths
rm -R /opt/piScreen

#Link development paths
ln -s "$parent_path/opt/piScreen/" /opt/piScreen
ln -s "$parent_path/srv/piScreen/" /srv/piScreen
cp "$parent_path/home/pi/.config/labwc/rc.xml" /home/pi/.config/labwc/rc.xml
cp "$parent_path/home/pi/.config/labwc/autostart" /home/pi/.config/labwc/autostart

#Set rights
setfacl -Rm d:u:pi:rwx /opt/piScreen

#Configure Python virtual Environment
python -m venv "$parent_path/opt/piScreen/env"
source "$parent_path/opt/piScreen/env/bin/activate"
pip install -r "$parent_path/opt/piScreen/requirements.txt"