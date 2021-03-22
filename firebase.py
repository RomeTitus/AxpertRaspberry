from firebase_admin import db
from firebase_admin import credentials
import firebase_admin
import subprocess as commands

cred = credentials.Certificate("/home/pi/Irrigation-controller/Database/firebaseSDK.json")
firebase_admin.initialize_app(cred,
{
    'httpTimeout': 120,
    'databaseURL': 'https://pump-25eee.firebaseio.com/'
})

def updateAxpertDict(readingDic):
    try:
        readingRef = db.reference(getMacAddress() + '/Reading/Current')
        readingRef.set(readingDic)
    except Exception as e:
        pass

def getMacAddress():
    cmd = "hciconfig"
    device_id = "hci0"
    status, output = commands.getstatusoutput(cmd)
    bt_mac = output.split("{}:".format(device_id))[1].split(
        "BD Address: ")[1].split(" ")[0].strip()
    return str(bt_mac)