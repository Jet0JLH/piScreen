#!/usr/bin/python
import os, sys, shutil, json, subprocess, pwd, time
from OpenSSL.crypto import FILETYPE_PEM, load_certificate
from base64 import b64encode

isUpdate = False
isInstall = True
isReinstall = False

userHomePath = "/home/pi/"
certPath = userHomePath + "piScreen/certs/"
certName = "server.crt"
fstabPath = "/etc/fstab"
fstabEntry = "\ntmpfs    /media/ramdisk  tmpfs   defaults,size=5%,mode=0777        0       0"
sudoersFilePath = "/etc/sudoers.d/050_piScreen-nopasswd"
scheduleJsonPath = userHomePath + "piScreen/schedule.json"
settingsJsonPath = userHomePath + "piScreen/settings.json"
htpasswdPath = "/etc/apache2/.piScreen_htpasswd"
lxdePath = "/etc/xdg/lxsession/LXDE-pi/autostart"
lxdeConfig1 = "@lxpanel --profile LXDE-pi"
lxdeConfig2 = "@xset s 0"
lxdeConfig3 = "@xset -dpms"
desktopConfigPath = userHomePath + ".config/pcmanfm/LXDE-pi/desktop-items-0.conf"
desktopConfig1 = "show_trash=1"
desktopConfig2 = "show_mounts=1"
defaultSettingsPath = f"{os.path.dirname(__file__)}/defaults/default_settings.json"
defaultSchedulePath = f"{os.path.dirname(__file__)}/defaults/default_schedule.json"
firefoxConfigPath = "/etc/firefox-esr/piScreen.js"
continuousInstall = False
standardWebUsername = "pi"
standardWebPassword = "piScreen"
skipDependencyUpdate = False
oldManifest = json.loads('{"application-name": "piScreen", "version": { "major": -1,	"minor": -1,	"patch": -1}}') #Set default values
SHA256OID = "OID.2.16.840.1.101.3.4.2.1"
SHA384OID = "OID.2.16.840.1.101.3.4.2.2"
SHA512OID = "OID.2.16.840.1.101.3.4.2.3"
os.environ["DISPLAY"] = ":0"


def executeWait(command):
    args = command.split(" ")
    try:
        process = subprocess.Popen(args)
        process.wait()
        return process.returncode
    except PermissionError:
        exit("No permissions")
    except FileNotFoundError:
        exit("File doesn't exist")
    except:
        exit("Error in executeWait")

def executeWithReturnValue(command):
    try:
        args = command.split(" ")
        result = subprocess.run(args, capture_output=True)
        return result.stdout.decode("utf-8")
    except:
        exit("Error in executeWithReturnValue")


def appendToFile(filepath, text):
    try:
        file = open(filepath, "a")
        file.write(text)
    except PermissionError:
        exit("No permissions on " + filepath)
    except FileNotFoundError:
        exit(filepath + " doesn't exist")
    except:
        exit("Error in appendToFile on " + filepath)
    finally:
        file.close()

def readFile(filepath):
    try:
        file = open(filepath, "r")
        filestr = file.read()
        return filestr
    except PermissionError:
        exit("No read permissions on " + filepath)
    except FileNotFoundError:
        exit(filepath + " doesn't exist")
    except:
        exit("Error in readFile on " + filepath)
    finally:
        file.close()

def removeFile(filePath):
    try:
        if os.path.exists(filePath):
            os.remove(filePath)
    except PermissionError:
        exit("No write and execute permissions on " + filePath + "to delete it.")
    except:
        exit("Error in removeFile")

def copyFile(fromPath, toPath):
    try:
        shutil.copy(fromPath, toPath)
    except PermissionError:
        exit("No read permissions on copy " + fromPath + " to " + toPath)
    except FileNotFoundError:
        exit("File not found error on copy " + fromPath + " to " + toPath)
    except:
        exit("Error in copyFile on " + fromPath + " to " + toPath)
        

def createFolder(folderpath):
    try:
        if not os.path.exists(folderpath):
            os.mkdir(folderpath)
    except PermissionError:
        exit("No write permissions to create " + folderpath)
    except:
        exit("Error in createFolder " + folderpath)

def writeNewFile(filepath, text):
    try:
        file = open(filepath, "w")
        file.write(text)
    except PermissionError:
        exit("No write permissions on " + filepath)
    except:
        exit("Error in writeNewFile on " + filepath)
    finally:
        file.close()

def replaceInFile(toReplace, replacement, filePath):
    try:
        fileText = readFile(filePath)
        fileText = fileText.replace(toReplace, replacement)
        removeFile(filePath)
        writeNewFile(filePath, fileText)
    except PermissionError:
        exit("No permissions")
    except FileNotFoundError:
        exit("File doesn't exist")
    except Exception:
        exit("Error in replaceInFile")

def replaceInFileWriteProtected(toReplace, replacement, filePath):
    try:
        tempFileName = ".temp.txt"
        writeNewFile(tempFileName, "")
        copyFile(filePath, tempFileName)
        replaceInFile(toReplace, replacement, tempFileName)
        copyFile(tempFileName, filePath)
        removeFile(tempFileName)
    except PermissionError:
        exit("No permissions")
    except FileNotFoundError:
        exit("File doesn't exist")
    except:
        exit("Error in replaceInFileWriteProtected")

def isLaterVersion(oMajor, oMinor, oPatch, nMajor, nMinor, nPatch):#Returns 1 if new is newer, 0 if equal, -1 if older
    if oMajor < nMajor:
        return 1
    elif oMajor == nMajor:
        if oMinor < nMinor:
            return 1
        elif oMinor == nMinor:
            if oPatch < nPatch:
                return 1
            elif oPatch == nPatch:
                return 0
            else:
                return -1
        else:
            return -1
    else:
        return -1

def isLaterScheduleStructureVersion(oMajor, oMinor, nMajor, nMinor):#Returns 1 if new is newer, 0 if equal, -1 if older
    if oMajor < nMajor:
        return 1
    elif oMajor == nMajor:
        if oMinor < nMinor:
            return 1
        elif oMinor == nMinor:
            return 0
        else:
            return -1
    else:
        return -1


def checkForRootPrivileges():
    if os.geteuid() != 0:
        exit("Please run this script with root privileges.")

def loadManifests():
    global oldManifest
    newManifest = json.loads(readFile(f"{os.path.dirname(__file__)}{userHomePath}piScreen/manifest.json"))        
    if os.path.exists(userHomePath + "piScreen/manifest.json"):
        oldManifest = json.loads(readFile(userHomePath + "piScreen/manifest.json")) #No piScreen installation yet
        print(f"Old version: {oldManifest['version']['major']}.{oldManifest['version']['minor']}.{oldManifest['version']['patch']}")
    else:
        print("piScreen isn't installed yet.")
    print(f"New version: {newManifest['version']['major']}.{newManifest['version']['minor']}.{newManifest['version']['patch']}")

    res = isLaterVersion(oldManifest['version']['major'], oldManifest['version']['minor'], oldManifest['version']['patch'], newManifest['version']['major'], newManifest['version']['minor'], newManifest['version']['patch'])
    if res == 1:
        if oldManifest['version']['major'] == -1:
            return
        if oldManifest['version']['major'] < 2 and newManifest['version']['major'] >= 2:
            print("An update from version 1 to version 2 will not migrate your settings to the new version due to incompatibility. \nAll data will be lost. You have to set up your schedule and settings again. ")
            print("Do you want to reinstall piScreen? [y/N]: ", end="")
            if "y" != input().lower():
                exit("No reinstall.")
            return
        elif not isUpdate:
            print("Do you want to update? [y/N]: ", end="")
            if "y" != input().lower():
                exit("No update. Exiting.")
    elif res == 0:
        if not isReinstall:
            print("You have already installed the same version. Do you want to reinstall? [y/N]: ", end="")
            if "y" != input().lower():
                exit("No reinstall.")
    elif res == -1:
        exit("You are about to install an old version of piScreen.\nPlease uninstall the current version and install the old version if you want to continue.")


def updateDependencies():
    print("Updating dependencies")
    executeWait("apt update -qq")

def installDependencies():
    print("Installing dependencies")
    executeWait("apt install firefox-esr unclutter apache2 php7.4 cec-utils ddcutil -y -qq")

def removeFiles():
    print("Removing files")
    removeFile(sudoersFilePath)
    if executeWait("a2query -s piScreen -q") == 0:
        executeWait("a2dissite -q piScreen")
    removeFile("/etc/apache2/sites-available/piScreen.conf")
    removeFile(htpasswdPath)
    removeFile(userHomePath + ".config/autostart/piScreenCore.desktop")
    executeWait(f"rm -f -R {userHomePath}piScreen")
    executeWait("rm -f -R /srv/piScreen")
    removeFile(firefoxConfigPath)
    if os.path.exists("/var/spool/cron/crontabs/pi"):
        os.system("crontab -u pi -l | grep -v '/home/pi/piScreen/piScreenCron.py --check-now' | crontab -u pi -")#remove old crontab entry from version 1.x.x
    removeFile(userHomePath + "piScreen/cron.json")

    fstabConf = readFile(fstabPath)
    if fstabEntry in fstabConf:
        fstabConf = fstabConf.replace(fstabEntry, "")
        fstabConf = fstabConf.replace("tmpfs    /media/ramdisk  tmpfs   defaults,size=5%        0       0", "")
        removeFile(fstabPath)
        appendToFile(fstabPath, fstabConf)

def copyFiles():
    print("Copying files")
    copyFile(f"{os.path.dirname(__file__)}/etc/apache2/sites-available/piScreen.conf", "/etc/apache2/sites-available/")
    createFolder(userHomePath + ".config/autostart")
    copyFile(f"{os.path.dirname(__file__)}{userHomePath}.config/autostart/piScreenCore.desktop", userHomePath + ".config/autostart/")
    executeWait(f"cp -R {os.path.dirname(__file__)}{userHomePath}piScreen {userHomePath}piScreen")
    executeWait(f"rm -f -R {certPath}")
    createFolder(certPath)
    executeWait(f"cp -R {os.path.dirname(__file__)}/srv/piScreen/ /srv/piScreen/")
    executeWait(f"ln -s /media/ramdisk/piScreenScreenshot.png /srv/piScreen/admin/")

def setPermissions():
    print("Setting permissions")
    executeWait(f"setfacl -Rm d:u:www-data:rwx {userHomePath}piScreen/")
    executeWait(f"setfacl -Rm u:www-data:rwx {userHomePath}piScreen/")
    executeWait(f"setfacl -Rm d:u:pi:rwx {userHomePath}piScreen/")
    executeWait(f"setfacl -Rm u:pi:rwx {userHomePath}piScreen/")

    executeWait("setfacl -Rm d:u:www-data:rwx /srv/piScreen/")
    executeWait("setfacl -Rm u:www-data:rwx /srv/piScreen/")
    executeWait("setfacl -Rm d:u:pi:rwx /srv/piScreen/")
    executeWait("setfacl -Rm u:pi:rwx /srv/piScreen/")

    executeWait(f"setfacl -Rm d:u:pi:rwx {userHomePath}.config/autostart/")
    executeWait(f"setfacl -Rm u:pi:rwx {userHomePath}.config/autostart/")

def configureRamDisk():
    print("Configuring RAM disk")
    createFolder("/media/ramdisk")
    
    appendToFile(fstabPath, f"\n{fstabEntry}")

def configureWebserver():
    print("Configuring Webserver")
    executeWait("systemctl stop apache2")

    if isInstall:
        if continuousInstall:
            print(f"Webinterface login: Username: '{standardWebUsername}' Password: '{standardWebPassword}'")
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
    executeWithReturnValue(f"openssl genrsa -out {certPath}server.key 4096")
    executeWithReturnValue(f"openssl req -new -key {certPath}server.key -out {certPath}server.csr -sha256 -subj /C=DE/ST=BW/L=/O=PiScreen/OU=/CN=")
    executeWithReturnValue(f"openssl req -noout -text -in {certPath}server.csr")
    executeWithReturnValue(f"openssl x509 -req -days 3650 -in {certPath}server.csr -signkey {certPath}server.key -out {certPath}server.crt")

def configureSudoersFile():
    print("Configuring sudoers file")
    supiscreencmd = f"www-data        ALL=(ALL:ALL)   NOPASSWD:{userHomePath}piScreen/piScreenCmd.py\n"
    suhostnamectl = "www-data        ALL=(ALL:ALL)   NOPASSWD:/usr/bin/hostnamectl\n"
    
    removeFile(sudoersFilePath)
    writeNewFile(sudoersFilePath, supiscreencmd + suhostnamectl)

    executeWait(f"chmod 0440 {sudoersFilePath}")

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
    try:
        os.system(f"export XAUTHORITY={userHomePath}.Xauthority;export XDG_RUNTIME_DIR=/run/user/1000;pcmanfm --wallpaper-mode=color")
    except:
        exit(f"Error while configuring desktop. \nexport XAUTHORITY={userHomePath}.Xauthority;export XDG_RUNTIME_DIR=/run/user/1000;pcmanfm --wallpaper-mode=color")
    desktopConfig = readFile(desktopConfigPath)
    if desktopConfig1 in desktopConfig:
        desktopConfig = desktopConfig.replace(desktopConfig1, "show_trash=0")
        removeFile(desktopConfigPath)
        writeNewFile(desktopConfigPath, desktopConfig)
    else:
        appendToFile(desktopConfigPath, "show_trash=0")

    desktopConfig = readFile(desktopConfigPath)
    if desktopConfig2 in desktopConfig:
        desktopConfig = desktopConfig.replace(desktopConfig2, "show_mounts=0")
        removeFile(desktopConfigPath)
        writeNewFile(desktopConfigPath, desktopConfig)
    else:
        appendToFile(desktopConfigPath, "show_mounts=0")

    try:
        os.system(f"export XAUTHORITY={userHomePath}.Xauthority;export XDG_RUNTIME_DIR=/run/user/1000;pcmanfm --reconfigure")
    except:
        exit(f"Error while configuring desktop. \nexport XAUTHORITY={userHomePath}.Xauthority;export XDG_RUNTIME_DIR=/run/user/1000;pcmanfm --reconfigure")

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
        if "language" in settingsJson["settings"] and settingsJson["settings"]["language"] != "":
            defaultSettingsJson["settings"]["language"] = settingsJson["settings"]["language"]
        if "display" in settingsJson["settings"] and settingsJson["settings"]["display"] != "":
            defaultSettingsJson["settings"]["display"] = settingsJson["settings"]["display"]
    else:
        defaultSettingsJson = json.load(open(defaultSettingsPath))

def postpareUpdate():
    print("Postpare update")
    appendToFile(htpasswdPath, htpasswd + "\n")
    appendToFile(f"{certPath}/server.crt", certcrt)
    appendToFile(f"{certPath}/server.csr", certcsr)
    appendToFile(f"{certPath}/server.key", certkey)

    try:
        settingsFile = open(settingsJsonPath, "w")
        settingsFile.write(json.dumps(defaultSettingsJson, indent = 4))
        settingsFile.close()
    except:
        exit("Error while writing to " + settingsJsonPath)
    
def checkForPiUser():
    print("Checking for pi user")
    try:
        pwd.getpwnam('pi')
    except KeyError:
        exit('User pi does not exist. Script is working only with user pi.')

def getSha():
    output = str(executeWithReturnValue("timeout 1 openssl s_client -showcerts -connect localhost:443")).split("\n")
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
        exit("Hashing of certificate " + hostname + ":" + port + " not correct! Exiting...")
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
    print("Configuring Webbrowser")
    try:
        copyFile(f"{os.path.dirname(__file__)}/defaults/firefoxPiScreen.js", firefoxConfigPath)
    except:
        exit("Error while copying to " + firefoxConfigPath)
    
    try:
        os.system("sudo -u pi firefox-esr -CreateProfile piScreen")
    except:
        exit("Error while creating piScreen Firefox profile.")

    firefoxProfilePath = userHomePath + ".mozilla/firefox/"
    certOverridePath = firefoxProfilePath
    try:
        files = str(executeWithReturnValue(f"ls {firefoxProfilePath}")).split("\n")
    except:
        exit("Error while executing ls " + firefoxProfilePath)
    for item in files:
        if ".piScreen" in item:
            certOverridePath += str(item)
            certOverridePath += "/cert_override.txt"
            break
    if not certOverridePath.endswith("cert_override.txt"): 
        exit("No piScreen profile in " + firefoxProfilePath + " Exiting...")
    entry = getEntry("localhost", 443, certPath + certName)
    if not os.path.exists(certOverridePath):
        writeNewFile(certOverridePath, "")
    if entry not in open(certOverridePath).read():
        appendToFile(certOverridePath, entry)
    else:
        print("Entry already exists in cert_override.")
    
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
        copyFile(defaultSettingsPath, settingsJsonPath)
        copyFile(defaultSchedulePath, scheduleJsonPath)

    configureRamDisk()

    configureWebserver()

    setPermissions()

    configureSudoersFile()
    
    disableScreensaver()

    executeWait("systemctl restart apache2")

    configureDesktop()
    
    configureWebbrowser()

    wannaReboot()

def update():
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
    --reinstall
        Reinstalls {oldManifest['application-name']}
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
try:
    if len(sys.argv) == 0:
        install()

    if "--uninstall" in sys.argv:
        uninstall()

    if "--update" in sys.argv:
        update()

    if "--install" in sys.argv:
        install()

    if "--reinstall" in sys.argv:
        isReinstall = True
        install()
except KeyboardInterrupt:
    exit("\n\nStopped installation! Keyboard interrupt")

print("Done.")
sys.exit(os.EX_OK)