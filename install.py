import os, sys, shutil, json, subprocess
from venv import create

srvApacheConfig = "<Directory /srv/>\n\tOptions Indexes FollowSymLinks\n\tAllowOverride None\n\tRequire all granted\n</Directory>"
apache2ConfPath = "/etc/apache2/apache2.conf"
sslCertDirectory = "/home/pi/piScreen/certs"
fstabPath = "/etc/fstab"
fstabEntry = "tmpfs    /media/ramdisk  tmpfs   defaults,size=5%        0       0"
sudoersFilePath = "/etc/sudoers.d/piScreen-nopasswd"

oldManifest = json.loads('{"application-name": "piScreen", "version": {"major": "-", "minor": "-"}}')

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

def checkForRootPrivileges():
    if os.geteuid() != 0:
        exit("Please run this script with root privileges.")

def loadManifests():
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

def installDependencies():
    executeWait("apt install firefox-esr unclutter apache2 php7.4 cec-utils -y")

def removeFiles():
    print("Removing files")
    try: os.remove(sudoersFilePath)
    except: pass
    try: os.remove("/etc/apache2/sites-available/piScreen.conf")
    except: pass
    try: os.remove("/etc/apache2/.htpasswd")
    except: pass
    try: os.remove("/home/pi/.config/autostart/piScreenCore.desktop")
    except: pass
    try: executeWait("rm -R /home/pi/piScreen")
    except: pass
    try: executeWait("rm -R /srv/piScreen")
    except: pass

    apache2conf = readFile(apache2ConfPath)
    if srvApacheConfig in apache2conf:
        apache2conf = apache2conf.replace(srvApacheConfig, "")
        try: os.remove(apache2ConfPath)
        except: pass
        appendToFile(apache2ConfPath, apache2conf)
    
    fstabConf = readFile(fstabPath)
    if fstabEntry in fstabConf:
        fstabConf = fstabConf.replace(fstabEntry, "")
        try: os.remove(fstabPath)
        except: pass
        appendToFile(fstabPath, fstabConf)

def copyFiles():
    print("Coping files")
    shutil.copy(f"{os.getcwd()}/etc/apache2/sites-available/piScreen.conf", "/etc/apache2/sites-available/")
    createFolder("/home/pi/.config")
    createFolder("/home/pi/.config/autostart")
    shutil.copy(f"{os.getcwd()}/home/pi/.config/autostart/piScreenCore.desktop", "/home/pi/.config/autostart/")
    executeWait("cp -R home/pi/piScreen /home/pi/piScreen")
    executeWait(f"rm -R {sslCertDirectory}")
    createFolder(sslCertDirectory)
    executeWait("cp -R srv/piScreen/ /srv/piScreen/")

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

def configureRamDisk():
    print("Configuring RAM disk")
    createFolder("/media/ramdisk")
    
    appendToFile(fstabPath, f"\n{fstabEntry}")

def configureWebserver():
    print("Configuring Webserver")
    executeWait("systemctl stop apache2")

    print("Type your username for weblogin: ", end="")
    webusername = input()
    executeWait(f"htpasswd -c /etc/apache2/.htpasswd {webusername}")

    executeWait("a2dissite 000-default")
    executeWait("a2ensite piScreen")
    executeWait("a2enmod rewrite")
    executeWait("a2enmod ssl")
    
    if srvApacheConfig not in readFile(apache2ConfPath):
        print(True)
        print(srvApacheConfig)
        appendToFile(apache2ConfPath, f"\n{srvApacheConfig}")

    generateSslCertificates()

    executeWait("systemctl start apache2")

def generateSslCertificates():
    print("Generating SSL certificates")
    executeWait(f"openssl genrsa -out {sslCertDirectory}/server.key 4096")
    executeWait(f"openssl req -new -key {sslCertDirectory}/server.key -out {sslCertDirectory}/server.csr -sha256 -subj /C=DE/ST=BW/L=/O=PiScreen/OU=/CN=")
    executeWait(f"openssl req -noout -text -in {sslCertDirectory}/server.csr")
    executeWait(f"openssl x509 -req -days 3650 -in {sslCertDirectory}/server.csr -signkey {sslCertDirectory}/server.key -out {sslCertDirectory}/server.crt")

def configureSudoersFile():
    print("Configuring sudoers file")
    supiscreencmd = "www-data        ALL=(ALL:ALL)   NOPASSWD:/home/pi/piScreen/piScreenCmd.py"
    suhostnamectl = "www-data        ALL=(ALL:ALL)   NOPASSWD:/usr/bin/hostnamectl"
    suchangePwd =   "www-data        ALL=(ALL:ALL)   NOPASSWD:/home/pi/piScreen/changePwd.sh"
    
    appendToFile(sudoersFilePath, supiscreencmd + "\n")
    appendToFile(sudoersFilePath, suhostnamectl + "\n")
    appendToFile(sudoersFilePath, suchangePwd + "\n")

    executeWait(f"visudo -cf {sudoersFilePath}")

def install():
    checkForRootPrivileges()

    loadManifests()

    installDependencies()

    removeFiles()

    copyFiles()

    configureRamDisk()

    configureWebserver()

    setPermissions()

    configureSudoersFile()

def uninstall():
    removeFiles()

def printHelp():
    exit(f"""
This script installs {oldManifest['application-name']}. 
Parameters:
    --help
        Show this help
    --install
        Installs {oldManifest['application-name']}
    --uninstall
        Uninstalls {oldManifest['application-name']}
    """)

sys.argv.pop(0)

if len(sys.argv) == 0:
    install()

elif len(sys.argv) == 1 and sys.argv[0].lower() == "--install":
    install()

elif len(sys.argv) == 1 and sys.argv[0].lower() == "--uninstall":
    uninstall()
    
else:
    printHelp()


print("Done.")
