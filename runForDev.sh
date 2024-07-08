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

#Set rights
setfacl -Rm d:u:pi:rwx /opt/piScreen