import tkinter as tk

from helpers import parseDropdown, mObject, getHotkeys, saveHotkeys, updateLabel
from os import remove


# GUI class that handles the edit hotkeys popup window
########################################################################################
class editGUI:
    def __init__(self, taskQueueOut):
        self.master = tk.Toplevel()
        # Handle "X" button being clicked instead of close button
        self.master.protocol("WM_DELETE_WINDOW", self.close)
        self.master.configure(bg="white")
        self.master.grab_set()      # This lil number disables the main window and forces focus on this popup
        self.master.wm_title("Edit Hotkeys")
        self.taskQueueOut = taskQueueOut

        self.mob = mObject(0, 0, 0)

        self.label_text = tk.StringVar()
        self.label_text.set("Make a selection below")
        self.tlabel = tk.Label(master=self.master,
                               textvariable=self.label_text,
                               font=("Helvetica", 18),
                               bg="white")
        self.tlabel.pack()

        self.flabel = tk.Label(master=self.master,
                               text="Format is: Mode | Type | ID: Hotkey(s)",
                               font=("Helvetica", 11),
                               bg="white")
        self.flabel.pack()

        # Option frame
        ####################################################################
        oframe = tk.Frame(master=self.master, bg="white")

        self.modeOptions = getModeDisplay()
        self.modeVar = tk.StringVar()
        self.modeVar.set(self.modeOptions[0])
        self.modeVar.trace("w", lambda *args: self.updateMode())
        self.modeSwitch = tk.OptionMenu(oframe, self.modeVar, *self.modeOptions)
        self.modeSwitch.configure(bg="gray40",
                                  fg="white",
                                  activebackground="gray50",
                                  activeforeground="white",
                                  width=15,
                                  font=("Helvetica", 12))
        self.modeSwitch["menu"].configure(bg="gray40", fg="white")
        self.modeSwitch.pack(fill=tk.X, side=tk.LEFT, expand=True)

        self.hotkeyOptions = getHotkeyDisplay(self.modeVar.get())
        self.hotkeyVar = tk.StringVar()
        self.hotkeyVar.set(self.hotkeyOptions[0])
        self.hotkeySwitch = tk.OptionMenu(oframe, self.hotkeyVar, *self.hotkeyOptions)
        self.hotkeySwitch.configure(bg="gray40",
                                    fg="white",
                                    activebackground="gray50",
                                    activeforeground="white",
                                    width=50,
                                    font=("Helvetica", 12))
        self.hotkeySwitch["menu"].configure(bg="gray40", fg="white")
        self.hotkeySwitch.pack(fill=tk.X, side=tk.LEFT, expand=True)

        oframe.pack(fill=tk.X)
        ####################################################################

        # Button frame
        ####################################################################
        bframe1 = tk.Frame(master=self.master, bg="white")

        self.edit_button = tk.Button(master=bframe1,
                                     text="Edit",
                                     command=self.edit,
                                     width=20,
                                     height=3,
                                     bg="royalblue2",
                                     fg="white",
                                     activebackground="royalblue1",
                                     activeforeground="white")
        self.edit_button.pack(fill=tk.X, side=tk.LEFT, expand=True)

        self.del_button = tk.Button(master=bframe1,
                                    text="Delete",
                                    command=self.delete,
                                    width=20,
                                    height=3,
                                    bg="royalblue2",
                                    fg="white",
                                    activebackground="royalblue1",
                                    activeforeground="white")
        self.del_button.pack(fill=tk.X, side=tk.LEFT, expand=True)

        if self.hotkeyVar.get() == "None":
            self.del_button.configure(state=tk.DISABLED, bg="burlywood1")
            self.edit_button.configure(state=tk.DISABLED, bg="burlywood1")

        self.remove_button = tk.Button(master=bframe1,
                                       text="Close",
                                       command=self.close,
                                       width=20,
                                       height=3,
                                       bg="red3",
                                       fg="white",
                                       activebackground="red2",
                                       activeforeground="white")
        self.remove_button.pack(fill=tk.X, side=tk.LEFT, expand=True)

        bframe1.pack(fill=tk.X)
        ####################################################################

    # Function for updating the mode dropdown
    ########################################################################################
    def updateMode(self):
        # Get indices of old locations to restore when list has been rebuilt
        oldHotkeyIndex = self.hotkeyOptions.index(self.hotkeyVar.get())
        oldModeIndex = self.modeOptions.index(self.modeVar.get())

        # Get new hotkey options
        self.hotkeyOptions = getHotkeyDisplay(self.modeVar.get())
        # Clear the dropdown of the old choices
        self.hotkeySwitch["menu"].delete(0, 'end')
        # Add the new choices to the dropdown
        for option in self.hotkeyOptions:
            self.hotkeySwitch["menu"].add_command(label=option, command=lambda o=option: self.hotkeyVar.set(o))

        # Get new mode options
        self.modeOptions = getModeDisplay()
        # Clear the dropdown of the old choices
        self.modeSwitch["menu"].delete(0, 'end')
        # Add the new choices to the dropdown
        for option in self.modeOptions:
            self.modeSwitch["menu"].add_command(label=option, command=lambda o=option: self.modeVar.set(o))

        # Try restoring hotkey index
        try:
            self.hotkeyVar.set(self.hotkeyOptions[oldHotkeyIndex])
        except IndexError:
            self.hotkeyVar.set(self.hotkeyOptions[oldHotkeyIndex - 1])

        # Try restoring mode index
        try:
            self.modeVar.set(self.modeOptions[oldModeIndex])
        except IndexError:
            self.modeVar.set(self.modeOptions[0])

        # Handle case when no options are available on rebuild
        if self.hotkeyVar.get() == "None":
            self.del_button.configure(state=tk.DISABLED, bg="burlywood1")
            self.edit_button.configure(state=tk.DISABLED, bg="burlywood1")
        elif self.del_button['state'] == tk.DISABLED:
            self.del_button.configure(state=tk.NORMAL, bg="royalblue2")
            self.edit_button.configure(state=tk.NORMAL, bg="royalblue2")

    # Function for editing a selected hotkey
    ########################################################################################
    def edit(self):
        # Get the current mode and midi object
        mode, self.mob = parseDropdown(self.modeVar.get(), self.hotkeyVar.get())
        self.toggleButtons(tk.DISABLED)
        # Handle the required hotkey inputs
        if self.mob.eType == 9 or self.mob.eType == 8:
            self.taskQueueOut.put((2, self))

        elif self.mob.eType == 11:
            self.taskQueueOut.put((3, self))

    # Function for deleting a selected hotkey
    ########################################################################################
    def delete(self):
        hotkeys = getHotkeys()      # Get the current list of hotkeys
        # Get the current mode and midi object
        mode, self.mob = parseDropdown(self.modeVar.get(), self.hotkeyVar.get())
        # Delete the hotkey
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
        # Update the mode dropdown
        self.updateMode()
        updateLabel(self.tlabel, self.label_text, "Deleted selected hotkey")
        # Update the main label after a couple seconds
        self.master.after(2000, lambda: updateLabel(self.tlabel, self.label_text, "Make a selection below"))

    # Function to easily toggle the state of all buttons
    ########################################################################################
    def toggleButtons(self, state):
        self.edit_button.configure(state=state)
        self.del_button.configure(state=state)
        self.remove_button.configure(state=state)

        if state is tk.DISABLED:
            self.edit_button.configure(bg="burlywood1")
            self.del_button.configure(bg="burlywood1")
            self.remove_button.configure(bg="burlywood1")
        elif state is tk.NORMAL:
            self.edit_button.configure(bg="royalblue3")
            self.del_button.configure(bg="royalblue3")
            self.remove_button.configure(bg="red3")

        self.edit_button.update()
        self.del_button.update()
        self.remove_button.update()

    # Function for gracefully closing the popup GUI
    ########################################################################################
    def close(self):
        self.master.grab_release()
        self.master.destroy()


# Function that returns the displayable list of modes for a dropdown
########################################################################################
def getModeDisplay():
    hotkeys = getHotkeys()
    modeOptions = ["All"]
    for key in hotkeys.keys():
        if key not in modeOptions:
            modeOptions.append(key)

    modeOptions.sort()
    return modeOptions


# Function that returns the displayable list of hotkeys for a dropdown
########################################################################################
def getHotkeyDisplay(curMode=None):
    hotkeys = getHotkeys()
    hotkeyOptions = list()
    for mode, keys in hotkeys.items():
        if curMode not in [None, "All"] and mode != curMode:
            continue

        for event, pair in hotkeys[mode].items():
            if event == '11':
                mEvent = "Encoder"
            elif event == '9':
                mEvent = "Note ON"
            elif event == '8':
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
