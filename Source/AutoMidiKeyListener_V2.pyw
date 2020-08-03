from pygame import midi as m
from helpers import mObject, getHotkeys, terminateOldListener
from time import sleep
from win32gui import GetForegroundWindow
from win32process import GetWindowThreadProcessId
from psutil import Process
from datetime import datetime
from queue import Queue

import threading
import keyboard


statics = dict()
missed = Queue()


def connectMidi():
    while True:
        try:
            m.init()
            midIn = m.Input(m.get_default_input_id())
            return midIn
        except m.MidiException:
            m.quit()
            sleep(1)


def getActiveHotkeys():
    focused = getFocusedWindow()
    hotkeys = getHotkeys()
    activeDict = dict()

    if focused in hotkeys.keys() and "Universal" in hotkeys.keys():
        for key in hotkeys[focused].keys():
            if key in hotkeys["Universal"].keys():
                activeDict[key] = {**hotkeys["Universal"][key], **hotkeys[focused][key]}
            else:
                activeDict[key] = hotkeys[focused][key]

        for key in (set(hotkeys["Universal"].keys()) - set(activeDict.keys())):
            activeDict[key] = hotkeys["Universal"][key]

    elif "Universal" in hotkeys.keys():
        activeDict = hotkeys["Universal"]
    elif focused in hotkeys.keys():
        activeDict = hotkeys[focused]

    return activeDict


def intercept():
    midIn = connectMidi()
    lastIn = datetime.now()
    while True:
        now = datetime.now()
        if midIn.poll():
            lastIn = datetime.now()
            event = midIn.read(50)

            if len(event) > 10:
                event = event[len(event) - 1]
                missed.put(event)
            else:
                for ev in event:
                    missed.put(ev)

        elif (now - lastIn).seconds > 5:
            try:
                midIn.close()
            except Exception:
                pass
            m.quit()
            midIn = connectMidi()
            lastIn = datetime.now()

        sleep(.05)


def handler(mob):
    activeDict = getActiveHotkeys()

    if mob.eType == 11 and '11' in activeDict.keys():
        if str(mob.ID) in activeDict['11'].keys():
            if mob.ID in statics.keys():
                if mob.val > statics.get(mob.ID) or mob.val == 127:
                    keyboard.press_and_release(activeDict['11'][str(mob.ID)][1])
                elif mob.val < statics.get(mob.ID) or mob.val == 0:
                    keyboard.press_and_release(activeDict['11'][str(mob.ID)][0])
                statics.update({mob.ID: mob.val})

            elif mob.ID not in statics.keys():
                statics.update({mob.ID: mob.val})

    elif mob.eType == 9 and '9' in activeDict.keys():
        if str(mob.ID) in activeDict['9'].keys():
            keyboard.press_and_release(activeDict['9'][str(mob.ID)])

    elif mob.eType == 8 and '8' in activeDict.keys():
        if str(mob.ID) in activeDict['8'].keys():
            keyboard.press_and_release(activeDict['8'][str(mob.ID)])


def processQueue():
    while True:
        while not missed.empty():
            event = missed.get()
            mob = mObject(event[0][0] >> 4, event[0][1], event[0][2])
            handler(mob)
        sleep(0.05)


def getFocusedWindow():
    pid = GetWindowThreadProcessId(GetForegroundWindow())
    return Process(pid[-1]).name()


if __name__ == '__main__':
    terminateOldListener()
    processor = threading.Thread(target=processQueue)
    processor.daemon = True
    processor.start()
    intercept()
