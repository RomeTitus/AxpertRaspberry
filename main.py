import firebase
import time
from firebase_admin import db
import subprocess as commands
import datetime

def getAxpertInfo():
    axpertParam = {}
    #sudo mpp-solar -p /dev/hidraw0 -c QPIRI
    p = commands.Popen(['sudo', 'mpp-solar','-p', '/dev/hidraw0','--getstatus'], stdout=commands.PIPE,
    stderr=commands.PIPE)
    out, err = p.communicate()
    test = out.decode()
    for axperInfo in out.decode().split('\n'):
        axperInfo_NoWhitespace = axperInfo.replace(" ", "")
        if("ac_input_voltage" in axperInfo_NoWhitespace):
            axpertParam["ac_input_voltage"] = axperInfo_NoWhitespace.split('\t')[1] + axperInfo_NoWhitespace.split('\t')[2]
        
        if("pv_input_power" in axperInfo_NoWhitespace):
            axpertParam["pv_input_power"] = axperInfo_NoWhitespace.split('\t')[1] + axperInfo_NoWhitespace.split('\t')[2]

        if("ac_output_voltage" in axperInfo_NoWhitespace):
            axpertParam["ac_output_voltage"] = axperInfo_NoWhitespace.split('\t')[1] + axperInfo_NoWhitespace.split('\t')[2]

        if("ac_output_active_power" in axperInfo_NoWhitespace):
            axpertParam["ac_output_active_power"] = axperInfo_NoWhitespace.split('\t')[1] + axperInfo_NoWhitespace.split('\t')[2]

        if("battery_voltage" in axperInfo_NoWhitespace and "battery_voltage_from_scc" not in axperInfo_NoWhitespace and "is_battery_voltage_to_steady_while_charging" not in axperInfo_NoWhitespace ):
            axpertParam["battery_voltage"] = axperInfo_NoWhitespace.split('\t')[1] + axperInfo_NoWhitespace.split('\t')[2]

    if(len(axpertParam)>0):
        axpertParam["Date_Time"] = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        firebase.updateAxpertDict(axpertParam)

def FirebaseAlive(event):
    try:
        getAxpertInfo()
        pass    
    except:
        pass

def startAllListenerEvents():
    try:
        requestedTimeReferance = db.reference( str(getMacAddress()) + '/Alive/Status/RequestedTime').listen(FirebaseAlive)

        while (True):
            if(requestedTimeReferance._thread.isAlive() == False):
                requestedTimeReferance = db.reference( str(getMacAddress()) + '/Alive/Status/RequestedTime').listen(FirebaseAlive)

            time.sleep(15)
    except Exception as e:
        time.sleep(15)
        startAllListenerEvents()

def getMacAddress():
    cmd = "hciconfig"
    device_id = "hci0"
    status, output = commands.getstatusoutput(cmd)
    bt_mac = output.split("{}:".format(device_id))[1].split(
        "BD Address: ")[1].split(" ")[0].strip()
    return str(bt_mac)


if(__name__ == __name__):
    startAllListenerEvents()