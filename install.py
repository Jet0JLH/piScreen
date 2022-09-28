#!/usr/bin/python
import os, sys, shutil, json, subprocess, pwd, time
from OpenSSL.crypto import FILETYPE_PEM, load_certificate
from base64 import b64encode

isUpdate = False
isInstall = not isUpdate

certPath = "/home/pi/piScreen/certs/"
certName = "server.crt"
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
firefoxConfigPath = "/etc/firefox-esr/piScreen.js"
continuousInstall = False
standardWebPassword = "piScreen"
standardWebUsername = "pi"
skipDependencyUpdate = False
SHA256OID = "OID.2.16.840.1.101.3.4.2.1"
SHA384OID = "OID.2.16.840.1.101.3.4.2.2"
SHA512OID = "OID.2.16.840.1.101.3.4.2.3"


def executeWait(command):
    args = command.split(" ")
    process = subprocess.Popen(args)
    process.wait()
    return process.returncode

def executeWithReturnValue(command):
    args = command.split(" ")
    result = subprocess.run(args, capture_output=True)
    return result.stdout.decode("utf-8")

def appendToFile(filepath, text):
    try:
        file = open(filepath, "a")
        file.write(text)
    finally:
        file.close()

def readFile(filepath):
    try:
        file = open(filepath, "r")
        filestr = file.read()
    finally:
        file.close()
    return filestr

def removeFile(filePath):
    if os.path.exists(filePath):
        os.remove(filePath)

def createFolder(folderpath):
    if not os.path.exists(folderpath):
        os.mkdir(folderpath)

def writeNewFile(filepath, text):
    try:
        file = open(filepath, "w")
        file.write(text)
    finally:
        file.close()

def replaceInFile(toReplace, replacement, filePath):
    fileText = readFile(filePath)
    fileText = fileText.replace(toReplace, replacement)
    removeFile(filePath)
    writeNewFile(filePath, fileText)

def replaceInfileWriteProtected(toReplace, replacement, filePath):
    tempFileName = ".temp.txt"
    writeNewFile(tempFileName, "")
    shutil.copy(filePath, tempFileName)
    replaceInFile(toReplace, replacement, tempFileName)
    shutil.copy(tempFileName, filePath)
    removeFile(tempFileName)

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
        if not continuousInstall:
            print("You have already installed the current version. Do you want to reinstall? [y/N]: ", end="")
            if "y" != input().lower():
                exit("No need to reinstall.")

def updateDependencies():
    print("Updating dependencies")
    executeWait("apt update -qq")

def installDependencies():
    print("Installing dependencies")
    executeWait("apt install firefox-esr unclutter apache2 php7.4 cec-utils ddcutil -y -qq")

def removeFiles():
    print("Removing files")
    try: os.remove(sudoersFilePath)
    except: pass
    executeWait("a2dissite -q piScreen")
    try: os.remove("/etc/apache2/sites-available/piScreen.conf")
    except: pass
    try: os.remove(htpasswdPath)
    except: pass
    try: os.remove("/home/pi/.config/autostart/piScreenCore.desktop")
    except: pass
    try: executeWait("rm -f -R /home/pi/piScreen")
    except: pass
    try: executeWait("rm -f -R /srv/piScreen")
    except: pass
    try: os.remove(firefoxConfigPath)
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
    executeWait(f"rm -f -R {certPath}")
    createFolder(certPath)
    executeWait(f"cp -R {os.path.dirname(__file__)}/srv/piScreen/ /srv/piScreen/")
    executeWait(f"ln -s /media/ramdisk/piScreenScreenshot.png /srv/piScreen/admin/")

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
        if continuousInstall:
            print("Webinterface login: Username: 'pi' Password: 'piScreen'")
            executeWait(f"htpasswd -c -b {htpasswdPath} {standardWebUsername} {standardWebPassword}")
        else:
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

    executeWait("a2dissite -q 000-default")
    executeWait("a2ensite -q piScreen")
    executeWait("a2enmod -q rewrite")
    executeWait("a2enmod -q ssl")
    
    if not isUpdate:
        generateSslCertificates()

    executeWait("systemctl restart apache2")

def generateSslCertificates():
    print("Generating SSL certificates")
    executeWait(f"openssl genrsa -out {certPath}server.key 4096")
    executeWait(f"openssl req -new -key {certPath}server.key -out {certPath}server.csr -sha256 -subj /C=DE/ST=BW/L=/O=PiScreen/OU=/CN=")
    executeWait(f"openssl req -noout -text -in {certPath}server.csr")
    executeWait(f"openssl x509 -req -days 3650 -in {certPath}server.csr -signkey {certPath}server.key -out {certPath}server.crt")

def configureSudoersFile():
    print("Configuring sudoers file")
    supiscreencmd = "www-data        ALL=(ALL:ALL)   NOPASSWD:/home/pi/piScreen/piScreenCmd.py"
    suhostnamectl = "www-data        ALL=(ALL:ALL)   NOPASSWD:/usr/bin/hostnamectl"
    
    appendToFile(sudoersFilePath, supiscreencmd + "\n")
    appendToFile(sudoersFilePath, suhostnamectl + "\n")

    executeWait(f"chmod 0440 {sudoersFilePath}")

    #executeWait(f"visudo -cf {sudoersFilePath}")

def configureCrontab():
    print("Configuring crontab")
    if os.path.isfile(crontabPath):
        if crontabConfig not in readFile(crontabPath):
            os.system(f"(crontab -l -u pi; echo '{crontabConfig}') | crontab -u pi -")
    else:
        os.system(f"echo '' | crontab -u pi -")
        os.system(f"(crontab -l -u pi; echo '{crontabConfig}') | crontab -u pi -")

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
    if continuousInstall:
        print("Rebooting in 5 seconds...")
        os.system("sleep 5 && reboot &")
    else:
        print("Please reboot your system to run piScreen properly. Reboot now? [Y/n]: ", end="")
        inp = input()
        if "y" == inp.lower() or "" == inp:
            print("Rebooting in 5 seconds...")
            os.system("sleep 5 && reboot &")

def prepareUpdate():
    print("Prepare for update")
    global htpasswd, certcsr, certkey, certcrt
    htpasswd = readFile(htpasswdPath)
    certcrt = readFile(f"{certPath}/server.crt")
    certcsr = readFile(f"{certPath}/server.csr")
    certkey = readFile(f"{certPath}/server.key")

    global defaultSettingsJson
    if os.path.isfile(settingsJsonPath):
        settingsJson = json.load(open(settingsJsonPath))
        defaultSettingsJson = json.load(open(defaultSettingsPath))
        if "website" in settingsJson["settings"] and settingsJson["settings"]["website"] != "":
            defaultSettingsJson["settings"]["website"] = settingsJson["settings"]["website"]
        if "language" in settingsJson["settings"] and settingsJson["settings"]["language"] != "":
            defaultSettingsJson["settings"]["language"] = settingsJson["settings"]["language"]
    else:
        defaultSettingsJson = json.load(open(defaultSettingsPath))

    global defaultCronJson
    if os.path.isfile(cronJsonPath):
        defaultCronJson = json.load(open(cronJsonPath))
    else:
        defaultCronJson = json.load(open(defaultCronPath))

def postpareUpdate():
    print("Postpare update")
    appendToFile(htpasswdPath, htpasswd + "\n")
    appendToFile(f"{certPath}/server.crt", certcrt)
    appendToFile(f"{certPath}/server.csr", certcsr)
    appendToFile(f"{certPath}/server.key", certkey)

    settingsFile = open(settingsJsonPath, "w")
    settingsFile.write(json.dumps(defaultSettingsJson, indent = 4))
    settingsFile.close()
    
    cronFile = open(cronJsonPath, "w")
    cronFile.write(json.dumps(defaultCronJson, indent = 4))
    cronFile.close()
    
def checkForPiUser():
    print("Checking for pi user")
    try:
        pwd.getpwnam('pi')
    except KeyError:
        exit('User pi does not exist. Script is working only with username pi.')

def getSha():
    output = str(executeWithReturnValue("timeout 1 openssl s_client -showcerts -connect piscreen:443")).split("\n")
    for item in output:
        if "Peer signing digest" in item:
            return item.split(": ")[1].upper()
    return "SHA256"

def base64Append(data):
    missing = len(data) % 4
    if missing:
        data += b'=' * (4 - missing)
    return data

def getEntry(hostname, port, certPath):
    cert = load_certificate(FILETYPE_PEM, open(certPath).read())
    sha = getSha()

    returnVal = hostname
    returnVal += ":"
    returnVal += str(port)
    returnVal += ":"
    returnVal += "\t"
    if sha == "SHA256":
        returnVal += SHA256OID
    elif sha == "SHA384":
        returnVal += SHA384OID
    elif sha == "SHA512":
        returnVal += SHA512OID
    else:
        exit("Hashing not correct! Exiting...")
    returnVal += "\t"

    fingerprint = cert.digest(sha).decode('utf-8')
    returnVal += fingerprint
    returnVal += "\t"
    returnVal += "MUT"
    returnVal += "\t"

    serialNumber = cert.get_serial_number()
    serialNumber = serialNumber.to_bytes((serialNumber.bit_length() // 8) + 1, 'big')
    issuer = cert.get_issuer().der()
    cryptKey = b''.join([
        (0).to_bytes(4, 'big'),
        (0).to_bytes(4, 'big'),
        len(serialNumber).to_bytes(4, 'big'),
        len(issuer).to_bytes(4, 'big'),
        serialNumber,
        issuer
    ])

    cryptKey = base64Append(b64encode(cryptKey)).decode('utf-8')
    returnVal += cryptKey
    returnVal += "\n"

    return returnVal

def configureWebbrowser():
    shutil.copyfile(f"{os.path.dirname(__file__)}/defaults/firefoxPiScreen.js", firefoxConfigPath)
    firefoxProfilePath = "/home/pi/.mozilla/firefox/"
    certOverridePath = firefoxProfilePath
    files = str(executeWithReturnValue(f"ls {firefoxProfilePath}")).split("\n")
    for item in files:
        if ".default-esr" in item:
            certOverridePath += str(item)
            certOverridePath += "/cert_override.txt"
            break

    entry = getEntry("localhost", 443, certPath + certName)
    if entry not in open(certOverridePath).read():
        appendToFile(certOverridePath, entry)
    else:
        print("Entry is already in cert_override.")
    
def install():
    checkForRootPrivileges()

    checkForPiUser()

    loadManifests()

    if not skipDependencyUpdate:
        updateDependencies()

        installDependencies()

    if isUpdate:
        prepareUpdate()

    removeFiles()

    copyFiles()

    if isUpdate:
        postpareUpdate()
    else:
        shutil.copyfile(defaultSettingsPath, settingsJsonPath)
        shutil.copyfile(defaultCronPath, cronJsonPath)

    configureRamDisk()

    configureWebserver()

    setPermissions()

    configureSudoersFile()

    configureCrontab()
    
    disableScreensaver()

    executeWait("systemctl restart apache2")

    configureDesktop()
    
    configureWebbrowser()

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
        Shows this help
    -y or --skip-user-input
        Skips the user input, or fills it with standard values
    -s
        Skips update and installation of dependencies
    --install
        Installs {oldManifest['application-name']}
    --uninstall
        Uninstalls {oldManifest['application-name']}
    --update
        Updates {oldManifest['application-name']}""")

sys.argv.pop(0)

if "-y" in sys.argv or "--skip-user-input" in sys.argv:
    continuousInstall = True
    try: sys.argv.remove("-y")
    except ValueError: pass 
    try: sys.argv.remove("--skip-user-input")
    except ValueError: pass

if "-s" in sys.argv:
    skipDependencyUpdate = True
    try: sys.argv.remove("-s")
    except ValueError: pass 

if "--help" in sys.argv:
    printHelp()

if len(sys.argv) == 0:
    install()

if "--uninstall" in sys.argv:
    uninstall()

if "--update" in sys.argv:
    update()

if "--install" in sys.argv:
    install()


print("Done.")
sys.exit(os.EX_OK)