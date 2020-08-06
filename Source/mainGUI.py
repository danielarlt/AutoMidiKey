import tkinter as tk
import tkinter.scrolledtext
import logging

from os import remove
from helpers import mObject, getHotkeys, saveHotkeys, updateLabel
from editGUI import editGUI
from win32gui import EnumWindows, IsWindowVisible
from win32process import GetWindowThreadProcessId
from psutil import Process


# GUI class that handles the main window
########################################################################################
class mainGUI:
    def __init__(self, master, taskQueueOut, endCommand):
        self.master = master
        # Handle "X" button being clicked instead of close button
        self.master.protocol("WM_DELETE_WINDOW", endCommand)

        self.master.configure(bg="white")
        self.taskQueueOut = taskQueueOut
        master.title("AutoMidiKey")

        self.mob = mObject(0, 0, 0)

        # Label frame
        ####################################################################
        lframe1 = tk.Frame(bg="white")

        self.label_text = tk.StringVar()
        self.label_text.set("Make a selection below")
        self.tlabel = tk.Label(master=lframe1,
                               textvariable=self.label_text,
                               font=("Helvetica", 15),
                               bg="white")
        self.tlabel.pack(side=tk.LEFT)

        self.mode_text = tk.StringVar()
        self.mode_text.set("Universal")
        self.mlabel = tk.Label(master=lframe1,
                               textvariable=self.mode_text,
                               font=("Helvetica", 15),
                               bg="white",
                               fg="royalblue2")
        self.mlabel.pack(side=tk.RIGHT)

        lframe1.pack(fill=tk.X)
        ####################################################################

        # Button frame
        ####################################################################
        bframe1 = tk.Frame(bg="white")

        self.midi_button = tk.Button(master=bframe1,
                                     text="Get Midi",
                                     command=self.getMidi,
                                     width=20,
                                     height=5,
                                     bg="green4",
                                     fg="white",
                                     activebackground="green3",
                                     activeforeground="white",
                                     disabledforeground="gray25")

        self.midi_button.pack(fill=tk.X, side=tk.LEFT, expand=True)
        self.map_button = tk.Button(master=bframe1,
                                    text="Map Last Midi",
                                    command=self.mapKey,
                                    width=20,
                                    height=5,
                                    bg="burlywood1",
                                    fg="white",
                                    activebackground="royalblue2",
                                    activeforeground="white",
                                    disabledforeground="gray25",
                                    state=tk.DISABLED)

        self.map_button.pack(fill=tk.X, side=tk.LEFT, expand=True)

        self.del_button = tk.Button(master=bframe1,
                                    text="Delete Last Midi Hotkey",
                                    command=self.delKey,
                                    width=20,
                                    height=5,
                                    bg="burlywood1",
                                    fg="white",
                                    activebackground="royalblue2",
                                    activeforeground="white",
                                    disabledforeground="gray25",
                                    state=tk.DISABLED)

        self.del_button.pack(fill=tk.X, side=tk.LEFT, expand=True)

        self.close_button = tk.Button(master=bframe1,
                                      text="Close",
                                      command=endCommand,
                                      width=20,
                                      height=5,
                                      bg="red3",
                                      fg="white",
                                      activebackground="red2",
                                      activeforeground="white")

        self.close_button.pack(fill=tk.X, side=tk.LEFT, expand=True)

        bframe1.pack(fill=tk.X)
        ####################################################################

        # Mode frame
        ####################################################################
        mframe1 = tk.Frame(bg="White")

        self.switchLabel = tk.Label(master=mframe1, text="Mode:", bg="white", font=("Helvetica", 12))
        self.switchLabel.pack(side=tk.LEFT)

        self.modeVar = tk.StringVar()
        self.modeVar.trace("w", lambda *args: self.updateMode())
        modeOptions = getModeOptions()
        self.modeVar.set(modeOptions[0])
        self.modeSwitch = tk.OptionMenu(mframe1, self.modeVar, *modeOptions)
        self.modeSwitch.configure(bg="royalblue2",
                                  fg="white",
                                  activebackground="royalblue1",
                                  activeforeground="white",
                                  width=32,
                                  font=("Helvetica", 12))
        self.modeSwitch["menu"].configure(bg="royalblue2", fg="white")
        self.modeSwitch.pack(fill=tk.X, side=tk.LEFT, expand=True)

        self.refresh_button = tk.Button(master=mframe1,
                                        text="Refresh Modes",
                                        command=self.refreshMode,
                                        width=10,
                                        height=1,
                                        bg="gray1",
                                        fg="white",
                                        activebackground="gray10",
                                        activeforeground="white")
        self.refresh_button.pack(fill=tk.X, side=tk.LEFT, expand=True)

        self.edit_button = tk.Button(master=mframe1,
                                     text="Edit Hotkeys",
                                     command=self.editHotkeys,
                                     width=10,
                                     height=1,
                                     bg="gray40",
                                     fg="white",
                                     activebackground="gray50",
                                     activeforeground="white")
        self.edit_button.pack(fill=tk.X, side=tk.LEFT, expand=True)

        mframe1.pack(fill=tk.X)
        ####################################################################

        self.st = tk.scrolledtext.ScrolledText(master, state="disabled", height=6)
        self.st.pack(fill=tk.X)
        # Setup handler for logging events to scrolled text box
        handler = textHandler(self.st)
        logging.root.setLevel(level=logging.INFO)
        logger = logging.getLogger()
        logger.addHandler(handler)

    # Function for handling the edit hotkeys popup
    ########################################################################################
    def editHotkeys(self):
        updateLabel(self.tlabel, self.label_text, "Make a selection in the popup")
        editGUI(self.taskQueueOut)

    # Function for updating the mode label - not sure why I use this honestly
    ########################################################################################
    def updateMode(self):
        updateLabel(self.mlabel, self.mode_text, self.modeVar.get(), "Mode switch: " + self.modeVar.get())

    # Function to get a new list of running windows and update the options
    ########################################################################################
    def refreshMode(self):
        self.modeSwitch["menu"].delete(0, 'end')
        modeOptions = getModeOptions()
        for option in modeOptions:
            self.modeSwitch["menu"].add_command(label=option, command=lambda o=option: self.modeVar.set(o))
        updateLabel(self.tlabel, self.label_text, "Refreshed available modes", 0)
        self.modeVar.set(modeOptions[0])

    # Function to get midi input via asynch IO with the client thread
    ########################################################################################
    def getMidi(self):
        self.toggleButtons(tk.DISABLED)
        self.taskQueueOut.put((1, self))

    # Function to get hotkey input via asynch IO with the client thread
    ########################################################################################
    def mapKey(self):
        self.toggleButtons(tk.DISABLED)
        if self.mob.eType is 9 or self.mob.eType is 8:
            self.taskQueueOut.put((2, self))

        elif self.mob.eType is 11:
            self.taskQueueOut.put((3, self))

    # Function for deleting a hotkey for the currently captured midi input
    ########################################################################################
    def delKey(self):
        hotkeys = getHotkeys()
        # Check if there are hotkeys to delete
        if not hotkeys:
            updateLabel(self.tlabel, self.label_text, "No hotkey to delete")
            return

        # Try to delete the hotkey if it exists, remove the file if there are no more hotkeys
        try:
            mode = self.modeVar.get()       # Get the current mode
            # Attempt to delete the hotkey
            hotkeys[mode][str(self.mob.eType)].pop(str(self.mob.ID))
            # Format the hotkey dict accordingly
            if not bool(hotkeys[mode][str(self.mob.eType)]):
                hotkeys[mode].pop(str(self.mob.eType))
                if not bool(hotkeys[mode]):
                    hotkeys.pop(mode)
                    if not bool(hotkeys):
                        remove("Data/hotkeys.json")

            # If there are still hotkeys to save, save them
            if bool(hotkeys):
                saveHotkeys(hotkeys)
            updateLabel(self.tlabel, self.label_text, "Deleted last Midi input hotkey", 0)
        except KeyError:
            updateLabel(self.tlabel, self.label_text, "No hotkey to delete")

    # Function to easily toggle the state of all buttons
    ########################################################################################
    def toggleButtons(self, state):
        self.midi_button.configure(state=state)
        self.map_button.configure(state=state)
        self.del_button.configure(state=state)

        if state is tk.DISABLED:
            self.midi_button.configure(bg="burlywood1")
            self.map_button.configure(bg="burlywood1")
            self.del_button.configure(bg="burlywood1")
        elif state is tk.NORMAL:
            self.midi_button.configure(bg="green4")
            self.map_button.configure(bg="royalblue3")
            self.del_button.configure(bg="royalblue3")

        self.midi_button.update()
        self.map_button.update()
        self.del_button.update()
        # self.close_button.configure(state=state)
        # self.close_button.update()


# Text handling class used for logging GUI events to the scrolled text object
# Adapted from Moshe Kaplan: https://gist.github.com/moshekaplan/c425f861de7bbf28ef06
########################################################################################
class textHandler(logging.Handler):
    def __init__(self, text):
        # run the regular Handler __init__
        logging.Handler.__init__(self)
        # Store a reference to the Text it will log to
        self.text = text

    def emit(self, record):
        msg = self.format(record)

        def append():
            self.text.configure(state='normal')
            self.text.insert(tk.END, msg + '\n')
            self.text.configure(state='disabled')
            # Auto-scroll to the bottom
            self.text.yview(tk.END)

        # This is necessary because we can't modify the Text from other threads
        self.text.after(0, append)


# Function used to get window mode options for a dropdown
########################################################################################
def getModeOptions():
    windows = ["Universal"]
    EnumWindows(winEnumHandler, windows)
    return windows


# Function used to enumerate the currently visible windows
########################################################################################
def winEnumHandler(hwnd, windows):
    if IsWindowVisible(hwnd):
        curWindow = getAppName(hwnd)
        if curWindow is not '' and curWindow not in windows:
            windows.append(curWindow)


# Function used to get the process name of a visible window
########################################################################################
def getAppName(hwnd):
    pid = GetWindowThreadProcessId(hwnd)
    return Process(pid[-1]).name()
