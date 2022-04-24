#!/usr/bin/python
import os, sys, shutil, json, subprocess, pwd

isUpdate = False
isInstall = not isUpdate

certPath = "/home/pi/piScreen/certs"
fstabPath = "/etc/fstab"
fstabEntry = "tmpfs    /media/ramdisk  tmpfs   defaults,size=5%        0       0"
sudoersFilePath = "/etc/sudoers.d/050_piScreen-nopasswd"
cronJsonPath = "/home/pi/piScreen/cron.json"
settingsJsonPath = "/home/pi/piScreen/settings.json"
crontabPath = "/var/spool/cron/crontabs/pi"
crontabConfig = "*\t*\t*\t*\t*\t/home/pi/piScreen/piScreenCron.py --check-now"
htpasswdPath = "/etc/apache2/.piScreen_htpasswd"
lxdePath = "/etc/xdg/lxsession/LXDE-pi/autostart"
lxdeConfig1 = "@lxpanel --profile LXDE-pi"
lxdeConfig2 = "@xset s 0"
lxdeConfig3 = "@xset -dpms"
desktopConfigPath = "/home/pi/.config/pcmanfm/LXDE-pi/desktop-items-0.conf"
desktopConfig1 = "show_trash=1"
desktopConfig2 = "show_mounts=1"
oldManifest = json.loads('{"application-name": "piScreen", "version": { "major": "-",	"minor": "-",	"patch": "-"}}')
defaultSettingsPath = f"{os.path.dirname(__file__)}/defaults/default_settings.json"
defaultCronPath = f"{os.path.dirname(__file__)}/defaults/default_cron.json"

def executeWait(command):
    args = command.split(" ")
    process = subprocess.Popen(args)
    process.wait()
    return process.returncode

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

def writeNewFile(filepath, text):
    file = open(filepath, "w")
    file.write(text)
    file.close()

def checkForRootPrivileges():
    if os.geteuid() != 0:
        exit("Please run this script with root privileges.")

def loadManifests():
    global oldManifest
    if os.path.exists("/home/pi/piScreen/manifest.json"):
        oldManifest = json.loads(readFile("/home/pi/piScreen/manifest.json"))
    newManifest = json.loads(readFile(f"{os.path.dirname(__file__)}/home/pi/piScreen/manifest.json"))

    print(f"Starting {oldManifest['application-name']} setup.")
    print(f"Old version: {oldManifest['version']['major']}.{oldManifest['version']['minor']}.{oldManifest['version']['patch']}")
    print(f"New version: {newManifest['version']['major']}.{newManifest['version']['minor']}.{newManifest['version']['patch']}")
    if oldManifest['version'] == newManifest['version']:
        print("You have already installed the current version. Do you want to reinstall? [y/N]: ", end="")
        if "y" != input().lower():
            sys.exit()

def updateDependencies():
    executeWait("apt update")

def installDependencies():
    executeWait("apt install firefox-esr unclutter apache2 php7.4 cec-utils -y")

def removeFiles():
    print("Removing files")
    try: os.remove(sudoersFilePath)
    except: pass
    executeWait("a2dissite piScreen")
    try: os.remove("/etc/apache2/sites-available/piScreen.conf")
    except: pass
    try: os.remove(htpasswdPath)
    except: pass
    try: os.remove("/home/pi/.config/autostart/piScreenCore.desktop")
    except: pass
    try: executeWait("rm -R /home/pi/piScreen")
    except: pass
    try: executeWait("rm -R /srv/piScreen")
    except: pass
    
    fstabConf = readFile(fstabPath)
    if fstabEntry in fstabConf:
        fstabConf = fstabConf.replace(fstabEntry, "")
        try: os.remove(fstabPath)
        except: pass
        appendToFile(fstabPath, fstabConf)

def copyFiles():
    print("Copying files")
    shutil.copy(f"{os.path.dirname(__file__)}/etc/apache2/sites-available/piScreen.conf", "/etc/apache2/sites-available/")
    createFolder("/home/pi/.config/autostart")
    shutil.copy(f"{os.path.dirname(__file__)}/home/pi/.config/autostart/piScreenCore.desktop", "/home/pi/.config/autostart/")
    executeWait(f"cp -R {os.path.dirname(__file__)}/home/pi/piScreen /home/pi/piScreen")
    executeWait(f"rm -R {certPath}")
    createFolder(certPath)
    executeWait(f"cp -R {os.path.dirname(__file__)}/srv/piScreen/ /srv/piScreen/")

def setPermissions():
    print("Setting permissions")
    executeWait("setfacl -Rm d:u:www-data:rwx /home/pi/piScreen/")
    executeWait("setfacl -Rm u:www-data:rwx /home/pi/piScreen/")
    executeWait("setfacl -Rm d:u:pi:rwx /home/pi/piScreen/")
    executeWait("setfacl -Rm u:pi:rwx /home/pi/piScreen/")

    executeWait("setfacl -Rm d:u:www-data:rwx /srv/piScreen/")
    executeWait("setfacl -Rm u:www-data:rwx /srv/piScreen/")
    executeWait("setfacl -Rm d:u:pi:rwx /srv/piScreen/")
    executeWait("setfacl -Rm u:pi:rwx /srv/piScreen/")

    executeWait("setfacl -Rm d:u:pi:rwx /home/pi/.config/autostart/")
    executeWait("setfacl -Rm u:pi:rwx /home/pi/.config/autostart/")

def configureRamDisk():
    print("Configuring RAM disk")
    createFolder("/media/ramdisk")
    
    appendToFile(fstabPath, f"\n{fstabEntry}")

def configureWebserver():
    print("Configuring Webserver")
    executeWait("systemctl stop apache2")

    if isInstall:
        print("Type your username for weblogin: ", end="")
        webusername = input()
        returncode = executeWait(f"htpasswd -c {htpasswdPath} {webusername}")
        while returncode != 0:
            print("Passwords doesn't match!")
            print("Type your username for weblogin: ", end="")
            webusername = input()
            returncode = executeWait(f"htpasswd -c {htpasswdPath} {webusername}")
        os.system(f"chown root:www-data {htpasswdPath}")
        os.system(f"chmod 640 {htpasswdPath}")

    executeWait("a2dissite 000-default")
    executeWait("a2ensite piScreen")
    executeWait("a2enmod rewrite")
    executeWait("a2enmod ssl")
    
    if not isUpdate:
        generateSslCertificates()

    executeWait("systemctl restart apache2")

def generateSslCertificates():
    print("Generating SSL certificates")
    executeWait(f"openssl genrsa -out {certPath}/server.key 4096")
    executeWait(f"openssl req -new -key {certPath}/server.key -out {certPath}/server.csr -sha256 -subj /C=DE/ST=BW/L=/O=PiScreen/OU=/CN=")
    executeWait(f"openssl req -noout -text -in {certPath}/server.csr")
    executeWait(f"openssl x509 -req -days 3650 -in {certPath}/server.csr -signkey {certPath}/server.key -out {certPath}/server.crt")

def configureSudoersFile():
    print("Configuring sudoers file")
    supiscreencmd = "www-data        ALL=(ALL:ALL)   NOPASSWD:/home/pi/piScreen/piScreenCmd.py"
    suhostnamectl = "www-data        ALL=(ALL:ALL)   NOPASSWD:/usr/bin/hostnamectl"
    
    appendToFile(sudoersFilePath, supiscreencmd + "\n")
    appendToFile(sudoersFilePath, suhostnamectl + "\n")

    executeWait(f"chmod 0440 {sudoersFilePath}")

    executeWait(f"visudo -cf {sudoersFilePath}")

def configureCrontab():
    print("Configuring crontab")
    if os.path.isfile(crontabPath):
        if crontabConfig not in readFile(crontabPath):
            os.system(f"(crontab -l -u pi; echo '{crontabConfig}') | crontab -u pi -")
    else:
        os.system(f"echo '' | crontab -u pi -")

def disableScreensaver():
    print("Disabling screensaver")
    lxdeConfig = readFile(lxdePath)
    if lxdeConfig.find(lxdeConfig1) >= 0 and lxdeConfig.find(f"#{lxdeConfig1}") < 0:
        lxdeConfig = lxdeConfig.replace(lxdeConfig1, f"#{lxdeConfig1}")

    if lxdeConfig2 not in lxdeConfig:
        lxdeConfig += f"\n{lxdeConfig2}"
    if lxdeConfig3 not in lxdeConfig:
        lxdeConfig += f"\n{lxdeConfig3}"

    writeNewFile(lxdePath, lxdeConfig)

def configureDesktop():
    print("Configuring desktop")
    os.system("export DISPLAY=:0;export XAUTHORITY=/home/pi/.Xauthority;export XDG_RUNTIME_DIR=/run/user/1000;pcmanfm --wallpaper-mode=color")
    desktopConfig = readFile(desktopConfigPath)
    if desktopConfig1 in desktopConfig:
        desktopConfig = desktopConfig.replace(desktopConfig1, "show_trash=0")
        os.remove(desktopConfigPath)
        writeNewFile(desktopConfigPath, desktopConfig)
    else:
        appendToFile(desktopConfigPath, "show_trash=0")

    desktopConfig = readFile(desktopConfigPath)
    if desktopConfig2 in desktopConfig:
        desktopConfig = desktopConfig.replace(desktopConfig2, "show_mounts=0")
        os.remove(desktopConfigPath)
        writeNewFile(desktopConfigPath, desktopConfig)
    else:
        appendToFile(desktopConfigPath, "show_mounts=0")

    os.system("export DISPLAY=:0;export XAUTHORITY=/home/pi/.Xauthority;export XDG_RUNTIME_DIR=/run/user/1000;pcmanfm --reconfigure")

def wannaReboot():
    print("Please reboot your system to run piScreen properly. Reboot now? [Y/n]: ", end="")
    inp = input()
    if "y" == inp.lower() or "" == inp:
        os.system("reboot now")

def prepareUpdate():
    print("Prepare for update")
    global htpasswd, certcsr, certkey, certcrt
    htpasswd = readFile(htpasswdPath)
    certcsr = readFile(f"{certPath}/server.crt")
    certkey = readFile(f"{certPath}/server.csr")
    certcrt = readFile(f"{certPath}/server.key")

def postpareUpdate():
    print("Postpare update")
    appendToFile(htpasswdPath, htpasswd + "\n")
    appendToFile(f"{certPath}/server.crt", certcsr)
    appendToFile(f"{certPath}/server.csr", certkey)
    appendToFile(f"{certPath}/server.key", certcrt)

def checkForPiUser():
    print("Checking for pi user")
    try:
        pwd.getpwnam('pi')
    except KeyError:
        print('User pi does not exist. Script is working only with username pi.')

def updateJson():
    if os.path.isfile(settingsJsonPath):
        settingsJson = json.load(open(settingsJsonPath))
        defaultSettingsJson = json.load(open(defaultSettingsPath))
        if "website" in settingsJson["settings"] and settingsJson["settings"]["website"] != "":
            defaultSettingsJson["settings"]["website"] = settingsJson["settings"]["website"]
        if "appearence" in settingsJson["settings"] and settingsJson["settings"]["appearence"] != "":
            defaultSettingsJson["settings"]["appearence"] = settingsJson["settings"]["appearence"]
        settingsFile = open(settingsJsonPath, "w")
        settingsFile.write(json.dumps(defaultSettingsJson,indent=4))
        settingsFile.close()
    else:
        shutil.copyfile(defaultSettingsPath,settingsJsonPath)
    if os.path.isfile(cronJsonPath):
        #Do nothing. User has this file allready
        pass
        cronJson = json.load(open(cronJsonPath))
        defaultCronJson = json.load(open(defaultCronPath))
    else:
        shutil.copyfile(defaultCronPath,cronJsonPath)
    
def install():
    checkForRootPrivileges()

    checkForPiUser()

    loadManifests()

    updateDependencies()

    installDependencies()

    if isUpdate:
        prepareUpdate()

    removeFiles()

    copyFiles()

    if isUpdate:
        postpareUpdate()

    configureRamDisk()

    configureWebserver()

    setPermissions()

    configureSudoersFile()

    configureCrontab()
    
    updateJson()

    disableScreensaver()

    executeWait("systemctl restart apache2")

    configureDesktop()

    wannaReboot()


def update():
    global isUpdate
    global isInstall
    isUpdate = True
    isInstall = not isUpdate
    install()

def uninstall():
    checkForRootPrivileges()

    removeFiles()

def printHelp():
    exit(f"""This script installs {oldManifest['application-name']}. 
Parameters:
    --help
        Show this help
    --install
        Installs {oldManifest['application-name']}
    --uninstall
        Uninstalls {oldManifest['application-name']}
    --update
        Updates {oldManifest['application-name']}""")

sys.argv.pop(0)

if len(sys.argv) == 0:
    install()

elif len(sys.argv) == 1 and sys.argv[0].lower() == "--install":
    install()

elif len(sys.argv) == 1 and sys.argv[0].lower() == "--update":
    update()

elif len(sys.argv) == 1 and sys.argv[0].lower() == "--uninstall":
    uninstall()
    
else:
    printHelp()


print("Done.")
