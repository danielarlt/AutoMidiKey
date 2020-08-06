import json
import keyboard
import logging

from psutil import Process, NoSuchProcess
from os import getpid
from subprocess import Popen


# Midi object class used to store data from midi events
########################################################################################
class mObject:
    def __init__(self, eType, ID, val):
        self.eType = eType
        self.ID = ID
        self.val = val


# Function for getting the current list of hotkeys from the json
########################################################################################
def getHotkeys():
    try:
        readHotkeys = open('Data/hotkeys.json', 'r')
        hotkeys = json.load(readHotkeys)
    except FileNotFoundError:
        hotkeys = dict()
    return hotkeys


# Function for saving the list of hotkeys to the json
########################################################################################
def saveHotkeys(hotkeys):
    with open('Data/hotkeys.json', 'w') as jfile:
        json.dump(hotkeys, jfile)


# Function for saving a hotkey given the key, mode, and midi object
########################################################################################
def saveHotkey(hotkey, mode, mob):
    hotkeys = getHotkeys()
    if mode in hotkeys.keys():
        if str(mob.eType) in hotkeys[mode].keys():
            hotkeys[mode][str(mob.eType)].update({str(mob.ID): hotkey})
        else:
            hotkeys[mode].update({str(mob.eType): {str(mob.ID): hotkey}})
    else:
        hotkeys.update({mode: {str(mob.eType): {str(mob.ID): hotkey}}})
    saveHotkeys(hotkeys)


# Function that parses dropdown objects to extract the midi object
########################################################################################
def capHotkey():
    keyboard.stash_state()              # This ensures no key sticking and is stupid
    save = keyboard.stash_state()       # Save the keyboard state prior to hotkey intake
    hotkey = keyboard.read_hotkey()     # Read the hotkey
    keyboard.restore_state(save)        # Restore the keyboard state after hotkey intake
    return hotkey


# Function that parses dropdown objects to extract the midi object
########################################################################################
def parseDropdown(mode, info):
    toReturn = mObject(0, 0, 0)
    mobInfo = info[0:info.find(":")].split(" | ")

    if mode == "All":
        mode = mobInfo[0]
        if mobInfo[1] == "Encoder":
            toReturn.eType = 11
        elif mobInfo[1] == "Note ON":
            toReturn.eType = 9
        elif mobInfo[1] == "Note OFF":
            toReturn.eType = 8

        toReturn.ID = int(mobInfo[2])

    else:
        if mobInfo[0] == "Encoder":
            toReturn.eType = 11
        elif mobInfo[0] == "Note ON":
            toReturn.eType = 9
        elif mobInfo[0] == "Note OFF":
            toReturn.eType = 8

        toReturn.ID = int(mobInfo[1])

    return mode, toReturn


# Function used to update a GUI label and optionally log a message
########################################################################################
def updateLabel(label, labelText, msg, logmsg=None):
    labelText.set(msg)
    label.update()
    if logmsg:
        logging.info(logmsg)
    elif logmsg == 0:
        logging.info(msg)


# Function used to terminate the midi listener if it's running
########################################################################################
def terminateOldListener():
    # Assume the listener hasn't been terminated
    terminated = False
    # Check the PID in the run.txt file to see if it's an active python process and if so shut it down
    with open("Data/run.txt", 'r') as check:
        strpid = check.readline()
        if strpid != "":
            try:
                process = Process(int(strpid))
                if process.name() == "python.exe" or process.name() == "pythonw.exe":
                    process.terminate()
                    terminated = True

            except NoSuchProcess:
                pass

    return terminated


# Function used to store the pid of the new listener
########################################################################################
def storeListenerPID():
    with open("Data/run.txt", 'w') as store:
        store.writelines(str(getpid()))


# Function used to start a listener
########################################################################################
def startListener():
    Popen("AutoMidiKeyListener.bat", cwd=r"%cd%/../")
