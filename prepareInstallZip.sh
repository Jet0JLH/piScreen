#!/bin/bash
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$parent_path/.."

rm -r install/
rm install.zip

mkdir install
cp -r piScreen/defaults/ install/
cp -r piScreen/home/ install/
cp -r piScreen/srv/ install/
cp -r piScreen/etc/ install/
cp -r piScreen/install.py install/
cp -r piScreen/LICENSE install/
rm -r install/home/pi/piScreen/certs
rm -r install/home/pi/piScreen/settings.json
rm -r install/home/pi/piScreen/schedule.json
rm -r install/srv/piScreen/admin/piScreenScreenshot.jpg
zip -q -r ./install.zip ./install/