import tkinter as tk
import tkinter.scrolledtext
import logging

from os import remove
from helpers import mObject, getHotkeys, saveHotkeys, capHotkey, updateLabel, getOptions, textHandler,\
                    getHotkeyDisplay, getModeDisplay, parseDropdown, saveHotkey


class mainGUI:
    def __init__(self, master, taskQueueOut, endCommand):
        self.master = master
        self.master.protocol("WM_DELETE_WINDOW", endCommand)

        self.master.configure(bg="white")
        self.taskQueueOut = taskQueueOut
        master.title("AutoMidiKey")

        self.mob = mObject(0, 0, 0)

        self.lframe1 = tk.Frame(bg="white")

        self.label_text = tk.StringVar()
        self.label_text.set("Make a selection below")
        self.tlabel = tk.Label(master=self.lframe1,
                               textvariable=self.label_text,
                               font=("Helvetica", 15),
                               bg="white")
        self.tlabel.pack(side=tk.LEFT)

        self.mode_text = tk.StringVar()
        self.mode_text.set("Universal")
        self.mlabel = tk.Label(master=self.lframe1,
                               textvariable=self.mode_text,
                               font=("Helvetica", 15),
                               bg="white",
                               fg="royalblue2")
        self.mlabel.pack(side=tk.RIGHT)

        self.lframe1.pack(fill=tk.X)

        self.bframe1 = tk.Frame(bg="white")

        self.midi_button = tk.Button(master=self.bframe1,
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
        self.mapThread = None
        self.map_button = tk.Button(master=self.bframe1,
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

        self.del_button = tk.Button(master=self.bframe1,
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

        self.close_button = tk.Button(master=self.bframe1,
                                      text="Close",
                                      command=endCommand,
                                      width=20,
                                      height=5,
                                      bg="red3",
                                      fg="white",
                                      activebackground="red2",
                                      activeforeground="white")

        self.close_button.pack(fill=tk.X, side=tk.LEFT, expand=True)

        self.bframe1.pack(fill=tk.X)

        self.mframe1 = tk.Frame(bg="White")

        self.switchLabel = tk.Label(master=self.mframe1, text="Mode:", bg="white", font=("Helvetica", 12))
        self.switchLabel.pack(side=tk.LEFT)

        self.modeVar = tk.StringVar()
        self.modeVar.trace("w", lambda *args: self.updateMode())
        modeOptions = getOptions()
        self.modeVar.set(modeOptions[0])
        self.modeSwitch = tk.OptionMenu(self.mframe1, self.modeVar, *modeOptions)
        self.modeSwitch.configure(bg="royalblue2",
                                  fg="white",
                                  activebackground="royalblue1",
                                  activeforeground="white",
                                  width=32,
                                  font=("Helvetica", 12))
        self.modeSwitch["menu"].configure(bg="royalblue2", fg="white")
        self.modeSwitch.pack(fill=tk.X, side=tk.LEFT, expand=True)

        self.refresh_button = tk.Button(master=self.mframe1,
                                        text="Refresh Modes",
                                        command=self.refreshMode,
                                        width=10,
                                        height=1,
                                        bg="gray1",
                                        fg="white",
                                        activebackground="gray10",
                                        activeforeground="white")
        self.refresh_button.pack(fill=tk.X, side=tk.LEFT, expand=True)

        self.edit_button = tk.Button(master=self.mframe1,
                                     text="Edit Hotkeys",
                                     command=self.editHotkeys,
                                     width=10,
                                     height=1,
                                     bg="gray40",
                                     fg="white",
                                     activebackground="gray50",
                                     activeforeground="white")
        self.edit_button.pack(fill=tk.X, side=tk.LEFT, expand=True)

        self.mframe1.pack(fill=tk.X)

        self.st = tk.scrolledtext.ScrolledText(master, state="disabled", height=6)
        self.st.pack(fill=tk.X)

        handler = textHandler(self.st)
        logging.root.setLevel(level=logging.INFO)
        logger = logging.getLogger()
        logger.addHandler(handler)

    def editHotkeys(self):
        updateLabel(self.tlabel, self.label_text, "Make a selection in the popup")
        editGUI()

    def updateMode(self):
        updateLabel(self.mlabel, self.mode_text, self.modeVar.get(), "Mode switch: " + self.modeVar.get())

    def refreshMode(self):
        self.modeSwitch["menu"].delete(0, 'end')
        modeOptions = getOptions()
        for option in modeOptions:
            self.modeSwitch["menu"].add_command(label=option, command=lambda o=option: self.modeVar.set(o))
        updateLabel(self.tlabel, self.label_text, "Refreshed available modes", 0)
        self.modeVar.set(modeOptions[0])

    def getMidi(self):
        self.toggleButtons(tk.DISABLED)
        self.taskQueueOut.put(1)

    def mapKey(self):
        self.toggleButtons(tk.DISABLED)
        if self.mob.eType is 154 or self.mob.eType is 138:
            self.taskQueueOut.put(2)

        elif self.mob.eType is 186:
            self.taskQueueOut.put(3)

    def delKey(self):
        hotkeys = getHotkeys()
        if not hotkeys:
            updateLabel(self.tlabel, self.label_text, "No hotkey to delete")
            return

        try:
            mode = self.modeVar.get()
            hotkeys.pop(mode + " " + str(self.mob.eType) + " " + str(self.mob.ID))
            updateLabel(self.tlabel, self.label_text, "Deleted last Midi input hotkey", 0)
        except KeyError:
            updateLabel(self.tlabel, self.label_text, "No hotkey to delete")

        saveHotkeys(hotkeys)

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


class editGUI:
    def __init__(self):
        self.master = tk.Toplevel()
        self.master.protocol("WM_DELETE_WINDOW", self.close)
        self.master.configure(bg="white")
        self.master.grab_set()
        self.master.wm_title("Edit Hotkeys")

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

        self.oframe = tk.Frame(master=self.master, bg="white")

        self.modeOptions = getModeDisplay()
        self.modeVar = tk.StringVar()
        self.modeVar.set(self.modeOptions[0])
        self.modeVar.trace("w", lambda *args: self.updateMode())
        self.modeSwitch = tk.OptionMenu(self.oframe, self.modeVar, *self.modeOptions)
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
        self.hotkeySwitch = tk.OptionMenu(self.oframe, self.hotkeyVar, *self.hotkeyOptions)
        self.hotkeySwitch.configure(bg="gray40",
                                    fg="white",
                                    activebackground="gray50",
                                    activeforeground="white",
                                    width=50,
                                    font=("Helvetica", 12))
        self.hotkeySwitch["menu"].configure(bg="gray40", fg="white")
        self.hotkeySwitch.pack(fill=tk.X, side=tk.LEFT, expand=True)

        self.oframe.pack(fill=tk.X)

        self.bframe1 = tk.Frame(master=self.master, bg="white")

        self.edit_button = tk.Button(master=self.bframe1,
                                     text="Edit",
                                     command=self.edit,
                                     width=20,
                                     height=3,
                                     bg="royalblue2",
                                     fg="white",
                                     activebackground="royalblue1",
                                     activeforeground="white")
        self.edit_button.pack(fill=tk.X, side=tk.LEFT, expand=True)

        self.del_button = tk.Button(master=self.bframe1,
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

        self.remove_button = tk.Button(master=self.bframe1,
                                       text="Close",
                                       command=self.close,
                                       width=20,
                                       height=3,
                                       bg="red3",
                                       fg="white",
                                       activebackground="red2",
                                       activeforeground="white")
        self.remove_button.pack(fill=tk.X, side=tk.LEFT, expand=True)

        self.bframe1.pack(fill=tk.X)

    def updateMode(self):
        oldHotkeyIndex = self.hotkeyOptions.index(self.hotkeyVar.get())
        oldModeIndex = self.modeOptions.index(self.modeVar.get())
        self.hotkeyOptions = getHotkeyDisplay(self.modeVar.get())
        self.hotkeySwitch["menu"].delete(0, 'end')
        for option in self.hotkeyOptions:
            self.hotkeySwitch["menu"].add_command(label=option, command=lambda o=option: self.hotkeyVar.set(o))

        self.modeOptions = getModeDisplay()
        self.modeSwitch["menu"].delete(0, 'end')
        for option in self.modeOptions:
            self.modeSwitch["menu"].add_command(label=option, command=lambda o=option: self.modeVar.set(o))

        try:
            self.hotkeyVar.set(self.hotkeyOptions[oldHotkeyIndex])
        except IndexError:
            self.hotkeyVar.set(self.hotkeyOptions[oldHotkeyIndex - 1])

        try:
            self.modeVar.set(self.modeOptions[oldModeIndex])
        except IndexError:
            self.modeVar.set(self.modeOptions[0])

        if self.hotkeyVar.get() == "None":
            self.del_button.configure(state=tk.DISABLED, bg="burlywood1")
            self.edit_button.configure(state=tk.DISABLED, bg="burlywood1")
        elif self.del_button['state'] == tk.DISABLED:
            self.del_button.configure(state=tk.NORMAL, bg="royalblue2")
            self.edit_button.configure(state=tk.NORMAL, bg="royalblue2")

    def edit(self):
        mode, self.mob = parseDropdown(self.modeVar.get(), self.hotkeyVar.get())
        if self.mob.eType == 186:
            updateLabel(self.tlabel, self.label_text, "Enter a hotkey for decrease")
            dHotkey = capHotkey()
            updateLabel(self.tlabel, self.label_text, "Enter a hotkey for increase")
            iHotkey = capHotkey()
            saveHotkey((dHotkey, iHotkey), mode, self.mob)

        else:
            updateLabel(self.tlabel, self.label_text, "Enter a hotkey")
            hotkey = capHotkey()
            saveHotkey(hotkey, mode, self.mob)

        self.updateMode()
        updateLabel(self.tlabel, self.label_text, "Updated selected hotkey")
        self.master.after(2000, lambda: updateLabel(self.tlabel, self.label_text, "Make a selection below"))

    def delete(self):
        hotkeys = getHotkeys()
        mode, self.mob = parseDropdown(self.modeVar.get(), self.hotkeyVar.get())
        hotkeys[mode][str(self.mob.eType)].pop(str(self.mob.ID))
        if not bool(hotkeys[mode][str(self.mob.eType)]):
            hotkeys[mode].pop(str(self.mob.eType))
            if not bool(hotkeys[mode]):
                hotkeys.pop(mode)
                if not bool(hotkeys):
                    remove("hotkeys.json")

        if bool(hotkeys):
            saveHotkeys(hotkeys)
        self.updateMode()
        updateLabel(self.tlabel, self.label_text, "Deleted selected hotkey")
        self.master.after(2000, lambda: updateLabel(self.tlabel, self.label_text, "Make a selection below"))

    def close(self):
        self.master.grab_release()
        self.master.destroy()
