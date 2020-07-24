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

    if focused in hotkeys.keys() and "Universal" in hotkeys.keys():
        activeDict = {**hotkeys["Universal"], **hotkeys[focused]}
    elif "Universal" in hotkeys.keys():
        activeDict = hotkeys["Universal"]
    elif focused in hotkeys.keys():
        activeDict = hotkeys[focused]
    else:
        activeDict = dict()

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

    if mob.eType is 186 and '186' in activeDict.keys():
        if str(mob.ID) in activeDict['186'].keys():
            if mob.ID in statics.keys():
                if mob.val > statics.get(mob.ID) or mob.val is 127:
                    keyboard.press_and_release(activeDict['186'][str(mob.ID)][1])
                elif mob.val < statics.get(mob.ID) or mob.val is 0:
                    keyboard.press_and_release(activeDict['186'][str(mob.ID)][0])
                statics.update({mob.ID: mob.val})

            elif mob.ID not in statics.keys():
                statics.update({mob.ID: mob.val})

    elif mob.eType is 154 and '154' in activeDict.keys():
        if str(mob.ID) in activeDict['154'].keys():
            keyboard.press_and_release(activeDict['154'][str(mob.ID)])

    elif mob.eType is 138 and '138' in activeDict.keys():
        if str(mob.ID) in activeDict['138'].keys():
            keyboard.press_and_release(activeDict['138'][str(mob.ID)])


def processQueue():
    while True:
        while not missed.empty():
            event = missed.get()
            mob = mObject(event[0][0], event[0][1], event[0][2])
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
