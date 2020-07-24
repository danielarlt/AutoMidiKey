import threading
import queue as Queue
import tkinter as tk

from gui import mainGUI
from pygame import midi as m
from time import sleep
from helpers import mObject, saveHotkey, capHotkey, updateLabel, terminateOldListener, startListener


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
                ID = self.taskQueueIn.get()

                if ID is 1:
                    updateLabel(self.gui.tlabel, self.gui.label_text, "Awaiting Midi input...")

                    checkMob = self.getMidi()
                    if type(checkMob) is mObject:
                        self.gui.mob = checkMob
                    else:
                        return

                    if self.gui.mob.eType == 186:
                        mEvent = "Encoder"
                    elif self.gui.mob.eType == 154:
                        mEvent = "Note ON"
                    elif self.gui.mob.eType == 138:
                        mEvent = "Note OFF"
                    else:
                        mEvent = "Unknown"

                    msg = mEvent + " | ID: " + str(self.gui.mob.ID) + " | Value: " + str(self.gui.mob.val)
                    updateLabel(self.gui.tlabel,
                                self.gui.label_text,
                                msg,
                                "Captured: " + msg)
                    self.gui.toggleButtons(tk.NORMAL)

                elif ID is 2:
                    updateLabel(self.gui.tlabel, self.gui.label_text, "Enter hotkey")
                    hotkey = capHotkey()

                    mode = self.gui.modeVar.get()
                    saveHotkey(hotkey, mode, self.gui.mob)

                    updateLabel(self.gui.tlabel, self.gui.label_text, "Mapped last Midi input to: " + hotkey, 0)
                    self.gui.toggleButtons(tk.NORMAL)

                elif ID is 3:
                    updateLabel(self.gui.tlabel, self.gui.label_text, "Enter hotkey for decrease")
                    dHotkey = capHotkey()

                    updateLabel(self.gui.tlabel, self.gui.label_text, "Enter hotkey for increase")
                    iHotkey = capHotkey()

                    mode = self.gui.modeVar.get()
                    saveHotkey((dHotkey, iHotkey), mode, self.gui.mob)

                    updateLabel(self.gui.tlabel,
                                self.gui.label_text,
                                "Mapped last Midi input to decrease: " + dHotkey + " and increase: " + iHotkey,
                                0)
                    self.gui.toggleButtons(tk.NORMAL)

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
        mob = mObject(event[0][0][0], event[0][0][1], event[0][0][2])
        midIn.close()
        return mob

    def endApplication(self):
        self.running = 0
        self.master.destroy()
        startListener()




