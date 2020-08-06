import threading
import queue as Queue
import tkinter as tk

from mainGUI import mainGUI
from pygame import midi as m
from time import sleep
from helpers import mObject, saveHotkey, capHotkey, updateLabel, terminateOldListener, startListener, parseDropdown


# Client class that spawns a GUI thread and a worker thread for asynchronous IO
########################################################################################
class threadedClient:
    def __init__(self, master):
        self.master = master                # Store tkinter root
        self.taskQueueIn = Queue.Queue()    # Task queue from gui for asynch IO
        self.running = 1    # Flag for thread termination

        terminateOldListener()                                  # Terminate listener if it's running
        m.init()                                                # Initialize midi interface
        mainGUI(master, self.taskQueueIn, self.endApplication)  # Instantiate GUI

        # Start worker thread for asynch IO
        taskThread = threading.Thread(target=self.workerTaskThread)
        taskThread.daemon = True
        taskThread.start()

    # Function for the worker thread that handles asynch IO
    ########################################################################################
    def workerTaskThread(self):
        while self.running:
            try:
                # Get task ID and GUI class that called the task
                ID, gMaster = self.taskQueueIn.get()

                # Handle different tasks by the parsed ID
                if ID == 1:     # Get midi input
                    updateLabel(gMaster.tlabel, gMaster.label_text, "Awaiting Midi input...")

                    # Get midi input and store in GUI class
                    checkMob = self.getMidi()
                    if type(checkMob) is mObject:
                        gMaster.mob = checkMob
                    else:
                        return

                    # Parse type of midi event for display
                    if gMaster.mob.eType == 11:
                        mEvent = "Encoder"
                    elif gMaster.mob.eType == 9:
                        mEvent = "Note ON"
                    elif gMaster.mob.eType == 8:
                        mEvent = "Note OFF"
                    else:
                        mEvent = "Unknown"

                    # Build label message
                    msg = mEvent + " | ID: " + str(gMaster.mob.ID) + " | Value: " + str(gMaster.mob.val)
                    updateLabel(gMaster.tlabel,
                                gMaster.label_text,
                                msg,
                                "Captured: " + msg)
                    gMaster.toggleButtons(tk.NORMAL)

                elif ID == 2:       # Get single hotkey
                    # Update label and get hotkey input from user
                    updateLabel(gMaster.tlabel, gMaster.label_text, "Enter hotkey")
                    hotkey = capHotkey()

                    # If we're in the edit window, get the correct mode, save the hotkey, update the label
                    if gMaster.master.title() == "Edit Hotkeys":
                        mode = parseDropdown(gMaster.modeVar.get(), gMaster.hotkeyVar.get())[0]
                        saveHotkey(hotkey, mode, gMaster.mob)
                        updateLabel(gMaster.tlabel, gMaster.label_text, "Mapped Midi input to: " + hotkey)
                        gMaster.updateMode()

                    # We're in the main window, get the correct mode, save the hotkey, update the label
                    else:
                        mode = gMaster.modeVar.get()
                        saveHotkey(hotkey, mode, gMaster.mob)
                        updateLabel(gMaster.tlabel, gMaster.label_text, "Mapped last Midi input to: " + hotkey, 0)

                    gMaster.toggleButtons(tk.NORMAL)
                    # Update main label after a couple seconds
                    gMaster.master.after(2000, lambda: updateLabel(gMaster.tlabel, gMaster.label_text,
                                                                   "Make a selection below"))

                elif ID == 3:       # Get two hotkeys
                    # Update label and get first hotkey input from user
                    updateLabel(gMaster.tlabel, gMaster.label_text, "Enter hotkey for decrease")
                    dHotkey = capHotkey()
                    # Sleep to allow time for key ups
                    sleep(0.25)

                    # Update label and get second hotkey input from user
                    updateLabel(gMaster.tlabel, gMaster.label_text, "Enter hotkey for increase")
                    iHotkey = capHotkey()

                    # If we're in the edit window, get the correct mode, save the hotkeys, update the label
                    if gMaster.master.title() == "Edit Hotkeys":
                        mode = parseDropdown(gMaster.modeVar.get(), gMaster.hotkeyVar.get())[0]
                        saveHotkey((dHotkey, iHotkey), mode, gMaster.mob)
                        updateLabel(gMaster.tlabel,
                                    gMaster.label_text,
                                    "Mapped Midi input to decrease: " + dHotkey + " and increase: " + iHotkey)
                        gMaster.updateMode()

                    # We're in the main window, get the correct mode, save the hotkey, update the label
                    else:
                        mode = gMaster.modeVar.get()
                        saveHotkey((dHotkey, iHotkey), mode, gMaster.mob)
                        updateLabel(gMaster.tlabel,
                                    gMaster.label_text,
                                    "Mapped last Midi input to decrease: " + dHotkey + " and increase: " + iHotkey,
                                    0)
                    gMaster.toggleButtons(tk.NORMAL)
                    # Update main label after a copule seconds
                    gMaster.master.after(2000, lambda: updateLabel(gMaster.tlabel, gMaster.label_text,
                                                                   "Make a selection below"))

            except Queue.Empty:
                # If queue is empty we wait 100 ms before trying to process again
                sleep(0.1)
        return

    # Function that gets a single midi event input
    ########################################################################################
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

    # Function for gracefully closing the GUI and associated threads
    ########################################################################################
    def endApplication(self):
        self.running = 0
        self.master.destroy()
        startListener()
