import os, sys, shutil, json, subprocess

def executeWait(command):
    args = command.split(" ")
#    for arg in args:
#        print(arg)
    process = subprocess.Popen(args)
    process.wait()

def appendToFile(filepath, text):
    file = open(filepath, "a")
    file.write(text)
    file.close()

def readFile(filepath):
    file = open(filepath, "r")
    filestr = file.read()
    file.close()
    return filestr

def createFolder(folderpath):
    if not os.path.exists(folderpath):
        os.mkdir(folderpath)

if os.geteuid() != 0:
    exit("Please run this script with root privileges.")

srvApacheConfig = "<Directory /srv/>\n\tOptions Indexes FollowSymLinks\n\tAllowOverride None\n\tRequire all granted\n</Directory>"

sudoersfilepath = "/etc/sudoers.d/piScreen-nopasswd"
supoweroff =    "www-data        ALL=(ALL:ALL)   NOPASSWD:/usr/sbin/poweroff"
sureboot =      "www-data        ALL=(ALL:ALL)   NOPASSWD:/usr/sbin/reboot"
sukillBrowser = "www-data        ALL=(ALL:ALL)   NOPASSWD:/home/pi/piScreen/killBrowser.sh"
suhostnamectl = "www-data        ALL=(ALL:ALL)   NOPASSWD:/usr/bin/hostnamectl"
suchangePwd =   "www-data        ALL=(ALL:ALL)   NOPASSWD:/home/pi/piScreen/changePwd.sh"

fstabPath = "/etc/fstab"
fstabEntry = "tmpfs    /media/ramdisk  tmpfs   defaults,size=5%        0       0"

oldManifest = json.loads('{"application-name": "piScreen", "version": {"major": "-", "minor": "-"}}')
try:
    oldManifest = json.loads(readFile("/home/pi/piScreen/manifest.json"))
except:
    pass
newManifest = json.loads(readFile(f"{os.getcwd()}/home/pi/piScreen/manifest.json"))

print(f"Starting {oldManifest['application-name']} setup.")
print(f"Old version: {oldManifest['version']['major']}.{oldManifest['version']['minor']}")
print(f"New version: {newManifest['version']['major']}.{newManifest['version']['minor']}")
if oldManifest['version'] == newManifest['version']:
    print("You have already installed the current verion. Do you want to reinstall? [y/N]: ", end="")
    if "y" != input().lower():
        sys.exit()

executeWait("apt install firefox-esr unclutter apache2 php7.4 cec-utils -y")

#Remove files
print("Removing files")
try:
    os.remove("/etc/apache2/sites-available/piScreen.conf")
except:
    pass
try:
    os.remove("/home/pi/.config/autostart/piScreenCore.desktop")
except:
    pass
try:
    executeWait("rm -R /home/pi/piScreen")
except:
    pass
try:
    executeWait("rm -R /srv/piScreen")
except:
    pass


#Copy files
print("Coping files")
shutil.copy(f"{os.getcwd()}/etc/apache2/sites-available/piScreen.conf", "/etc/apache2/sites-available/")
createFolder("/home/pi/.config")
createFolder("/home/pi/.config/autostart")
shutil.copy(f"{os.getcwd()}/home/pi/.config/autostart/piScreenCore.desktop", "/home/pi/.config/autostart/")
executeWait("cp -R home/pi/piScreen/ /home/pi/piScreen")
executeWait("cp -R srv/piScreen/ /srv/piScreen/")


#Configure RAM disk
print("Configuring RAM disk")
createFolder("/media/ramdisk")
if fstabEntry not in readFile(fstabPath):
    appendToFile(fstabPath, "\ntmpfs    /media/ramdisk  tmpfs   defaults,size=5%        0       0")


#Configure Webserver
print("Configuring Webserver")
executeWait("systemctl stop apache2")

try:
    os.remove("/etc/apache2/.htpasswd")
except:
    pass
print("Type your username for weblogin: ", end="")
webusername = input()
executeWait(f"htpasswd -c /etc/apache2/.htpasswd {webusername}")

executeWait("a2dissite 000-default")
executeWait("a2ensite piScreen")
executeWait("a2enmod rewrite")
executeWait("a2enmod ssl")

if srvApacheConfig not in readFile("/etc/apache2/apache2.conf"):
    appendToFile("/etc/apache2/sites-available/piScreen.conf", srvApacheConfig)


#Generate SSL certificates
print("Generating SSL certificates")
createFolder("/home/pi/piScreen/certs")

if not os.path.exists("/home/pi/piScreen/certs/server.key"):
    executeWait("openssl genrsa -out server.key 4096")
if not os.path.exists("/home/pi/piScreen/certs/server.csr"):
    executeWait("openssl req -new -key server.key -out server.csr -sha256 -subj '/C=/ST=/L=/O=PiScreen/OU=/CN='")
    executeWait("openssl req -noout -text -in server.csr")
if not os.path.exists("/home/pi/piScreen/certs/server.crt"):
    executeWait("openssl x509 -req -days 3650 -in server.csr -signkey server.key -out server.crt")


#Set permissions
print("Setting permissions")
executeWait("setfacl -Rm d:u:www-data:rwx /home/pi/piScreen/")
executeWait("setfacl -Rm u:www-data:rwx /home/pi/piScreen/")
executeWait("setfacl -Rm d:u:pi:rwx /home/pi/piScreen/")
executeWait("setfacl -Rm u:pi:rwx /home/pi/piScreen/")

executeWait("setfacl -Rm d:u:www-data:rwx /srv/piScreen/")
executeWait("setfacl -Rm u:www-data:rwx /srv/piScreen/")
executeWait("setfacl -Rm d:u:pi:rwx /srv/piScreen/")
executeWait("setfacl -Rm u:pi:rwx /srv/piScreen/")


#Configure sudoers file
print("Configuring sudoers file")
sudoersfile = readFile(sudoersfilepath)
if supoweroff not in sudoersfile:
    appendToFile(sudoersfilepath, supoweroff + "\n")
if sureboot not in sudoersfile:
    appendToFile(sudoersfilepath, sureboot + "\n")
if sukillBrowser not in sudoersfile:
    appendToFile(sudoersfilepath, sukillBrowser + "\n")
if suhostnamectl not in sudoersfile:
    appendToFile(sudoersfilepath, suhostnamectl + "\n")
if suchangePwd not in sudoersfile:
    appendToFile(sudoersfilepath, suchangePwd + "\n")

executeWait("visudo -cf /etc/sudoers.d/piScreen-nopasswd")


print("Done.")
