import firebase
import time
from firebase_admin import db
import subprocess as commands
import datetime
import os

def getAxpertInfo(hasRun = False):
    axpertParam = {}
    #sudo mpp-solar -p /dev/hidraw0 -c QPIRI
    p = commands.Popen(['sudo', 'mpp-solar','-p', '/dev/hidraw0','--getstatus'], stdout=commands.PIPE,
    stderr=commands.PIPE)
    out, err = p.communicate()
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
        print("Saving...")
        firebase.saveAxpertDictLocal("AxpertInfo", axpertParam)
    else:
        if(hasRun == False):
            print("Failed, trying agian")
            getAxpertInfo(True)
    #    axpertParam["ac_input_voltage"] = "Error While Reading"
    #    axpertParam["pv_input_power"] = "Error While Reading"
    #    axpertParam["ac_output_voltage"] = "Error While Reading"
    #    axpertParam["ac_output_active_power"] = "Error While Reading"
    #    axpertParam["battery_voltage"] = "Error While Reading"
    #    axpertParam["Date_Time"] = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    #    firebase.updateAxpertDict(axpertParam)


def FirebaseAlive(event):
    try:
        print("getAxpertInfo")
        if(int(event.data) == 0):
             print("Restart Command Sent...")
             os.system('sudo reboot')
        print(str(event.data))
        axpertDict = firebase.downloadeAxpertDict("AxpertInfo")
        if(len(axpertDict)>0):
            firebase.updateAxpertDict(axpertDict)
    except Exception as e:
        print(e)

def startAllListenerEvents():
    try:
        requestedTimeReferance = db.reference( str(getMacAddress()) + '/Alive/Status/RequestedTime').listen(FirebaseAlive)

        while (True):
            if(requestedTimeReferance._thread.isAlive() == False):
                requestedTimeReferance = db.reference( str(getMacAddress()) + '/Alive/Status/RequestedTime').listen(FirebaseAlive)
            getAxpertInfo()
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
