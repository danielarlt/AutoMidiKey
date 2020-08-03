import threading
import queue as Queue
import tkinter as tk

from gui import mainGUI
from pygame import midi as m
from time import sleep
from helpers import mObject, saveHotkey, capHotkey, updateLabel, terminateOldListener, startListener, parseDropdown


class threadedClient:
    def __init__(self, master):
        self.master = master
        self.taskQueueOut = Queue.Queue()
        self.taskQueueIn = Queue.Queue()

        terminateOldListener()

        self.gui = mainGUI(master,
                           self.taskQueueIn,
                           self.endApplication)

        self.running = 1
        self.taskThread = threading.Thread(target=self.workerTaskThread)
        self.taskThread.daemon = True
        self.taskThread.start()

        m.init()

    def workerTaskThread(self):
        while self.running:
            try:
                ID, gMaster = self.taskQueueIn.get()

                if ID == 1:
                    updateLabel(gMaster.tlabel, gMaster.label_text, "Awaiting Midi input...")

                    checkMob = self.getMidi()
                    if type(checkMob) is mObject:
                        gMaster.mob = checkMob
                    else:
                        return

                    if gMaster.mob.eType == 11:
                        mEvent = "Encoder"
                    elif gMaster.mob.eType == 9:
                        mEvent = "Note ON"
                    elif gMaster.mob.eType == 8:
                        mEvent = "Note OFF"
                    else:
                        mEvent = "Unknown"

                    msg = mEvent + " | ID: " + str(gMaster.mob.ID) + " | Value: " + str(gMaster.mob.val)
                    updateLabel(gMaster.tlabel,
                                gMaster.label_text,
                                msg,
                                "Captured: " + msg)
                    gMaster.toggleButtons(tk.NORMAL)

                elif ID == 2:
                    updateLabel(gMaster.tlabel, gMaster.label_text, "Enter hotkey")
                    hotkey = capHotkey()

                    if gMaster.master.title() == "Edit Hotkeys":
                        mode = parseDropdown(gMaster.modeVar.get(), gMaster.hotkeyVar.get())[0]
                        saveHotkey(hotkey, mode, gMaster.mob)
                        updateLabel(gMaster.tlabel, gMaster.label_text, "Mapped Midi input to: " + hotkey)
                        gMaster.updateMode()

                    else:
                        mode = gMaster.modeVar.get()
                        saveHotkey(hotkey, mode, gMaster.mob)
                        updateLabel(gMaster.tlabel, gMaster.label_text, "Mapped last Midi input to: " + hotkey, 0)

                    gMaster.toggleButtons(tk.NORMAL)
                    gMaster.master.after(2000, lambda: updateLabel(gMaster.tlabel, gMaster.label_text,
                                                                   "Make a selection below"))

                elif ID == 3:
                    updateLabel(gMaster.tlabel, gMaster.label_text, "Enter hotkey for decrease")
                    dHotkey = capHotkey()
                    sleep(0.25)

                    updateLabel(gMaster.tlabel, gMaster.label_text, "Enter hotkey for increase")
                    iHotkey = capHotkey()

                    if gMaster.master.title() == "Edit Hotkeys":
                        mode = parseDropdown(gMaster.modeVar.get(), gMaster.hotkeyVar.get())[0]
                        saveHotkey((dHotkey, iHotkey), mode, gMaster.mob)
                        updateLabel(gMaster.tlabel,
                                    gMaster.label_text,
                                    "Mapped Midi input to decrease: " + dHotkey + " and increase: " + iHotkey)
                        gMaster.updateMode()

                    else:
                        mode = gMaster.modeVar.get()
                        saveHotkey((dHotkey, iHotkey), mode, gMaster.mob)
                        updateLabel(gMaster.tlabel,
                                    gMaster.label_text,
                                    "Mapped last Midi input to decrease: " + dHotkey + " and increase: " + iHotkey,
                                    0)
                    gMaster.toggleButtons(tk.NORMAL)
                    gMaster.master.after(2000, lambda: updateLabel(gMaster.tlabel, gMaster.label_text,
                                                                   "Make a selection below"))

            except Queue.Empty:
                sleep(0.1)
        return

    def getMidi(self):
        midIn = m.Input(m.get_default_input_id())
        while not midIn.poll() and self.running:
            if not m.get_init():
                m.init()
            else:
                pass
        if not self.running:
            return

        event = midIn.read(1)
        mob = mObject(event[0][0][0] >> 4, event[0][0][1], event[0][0][2])
        midIn.close()
        return mob

    def endApplication(self):
        self.running = 0
        self.master.destroy()
        startListener()
