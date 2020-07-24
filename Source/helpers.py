import json
import keyboard
import logging

from win32gui import EnumWindows, IsWindowVisible
from win32process import GetWindowThreadProcessId
from psutil import Process, NoSuchProcess
from tkinter import END
from os import getpid
from subprocess import Popen


class mObject:
    def __init__(self, eType, ID, val):
        self.eType = eType
        self.ID = ID
        self.val = val


class textHandler(logging.Handler):
    # This class allows you to log to a Tkinter Text or ScrolledText widget
    # Adapted from Moshe Kaplan: https://gist.github.com/moshekaplan/c425f861de7bbf28ef06

    def __init__(self, text):
        # run the regular Handler __init__
        logging.Handler.__init__(self)
        # Store a reference to the Text it will log to
        self.text = text

    def emit(self, record):
        msg = self.format(record)

        def append():
            self.text.configure(state='normal')
            self.text.insert(END, msg + '\n')
            self.text.configure(state='disabled')
            # Auto-scroll to the bottom
            self.text.yview(END)

        # This is necessary because we can't modify the Text from other threads
        self.text.after(0, append)


def getHotkeys():
    try:
        readHotkeys = open('Data/hotkeys.json', 'r')
        hotkeys = json.load(readHotkeys)
    except FileNotFoundError:
        hotkeys = dict()
    return hotkeys


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


def getHotkeyDisplay(curMode=None):
    hotkeys = getHotkeys()
    hotkeyOptions = list()
    for mode, keys in hotkeys.items():
        if curMode not in [None, "All"] and mode != curMode:
            continue

        for event, pair in hotkeys[mode].items():
            if event == '186':
                mEvent = "Encoder"
            elif event == '154':
                mEvent = "Note ON"
            elif event == '138':
                mEvent = "Note OFF"
            else:
                mEvent = "Unknown"

            for ID, hotkey in hotkeys[mode][event].items():
                if curMode != "All":
                    key = mEvent + " | " + ID
                else:
                    key = mode + " | " + mEvent + " | " + ID

                if type(hotkey) is list:
                    value = "Decrease: \"" + hotkey[0] + "\" Increase: \"" + hotkey[1] + "\""
                else:
                    value = "\"" + hotkey + "\""

                hotkeyOptions.append(key + ": " + value)

    hotkeyOptions.sort()
    if len(hotkeyOptions) == 0:
        return ["None"]
    return hotkeyOptions


def getModeDisplay():
    hotkeys = getHotkeys()
    modeOptions = ["All"]
    for key in hotkeys.keys():
        if key not in modeOptions:
            modeOptions.append(key)

    modeOptions.sort()
    return modeOptions


def parseDropdown(mode, info):
    toReturn = mObject(0, 0, 0)
    mobInfo = info[0:info.find(":")].split(" | ")

    if mode == "All":
        mode = mobInfo[0]
        if mobInfo[1] == "Encoder":
            toReturn.eType = 186
        elif mobInfo[1] == "Note ON":
            toReturn.eType = 154
        elif mobInfo[1] == "Note OFF":
            toReturn.eType = 138

        toReturn.ID = int(mobInfo[2])

    else:
        if mobInfo[0] == "Encoder":
            toReturn.eType = 186
        elif mobInfo[0] == "Note ON":
            toReturn.eType = 154
        elif mobInfo[0] == "Note OFF":
            toReturn.eType = 138

        toReturn.ID = int(mobInfo[1])

    return mode, toReturn


def saveHotkeys(hotkeys):
    with open('Data/hotkeys.json', 'w') as jfile:
        json.dump(hotkeys, jfile)


def capHotkey():
    keyboard.stash_state()          # This ensures no key sticking and is stupid
    save = keyboard.stash_state()
    hotkey = keyboard.read_hotkey()
    keyboard.restore_state(save)
    return hotkey


def updateLabel(label, labelText, msg, logmsg=None):
    labelText.set(msg)
    label.update()
    if logmsg:
        logging.info(logmsg)
    elif logmsg == 0:
        logging.info(msg)


def getOptions():
    windows = ["Universal"]
    EnumWindows(winEnumHandler, windows)
    return windows


def winEnumHandler(hwnd, windows):
    if IsWindowVisible(hwnd):
        curWindow = getAppName(hwnd)
        if curWindow is not '' and curWindow not in windows:
            windows.append(curWindow)


def getAppName(hwnd):
    pid = GetWindowThreadProcessId(hwnd)
    return Process(pid[-1]).name()


def terminateOldListener():
    terminated = False
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

    with open("Data/run.txt", 'w') as store:
        store.writelines(str(getpid()))

    return terminated


def startListener():
    p = Popen("AutoMidiKeyListener.bat", cwd=r"%cd%/../")
