from pygame import midi as m
from helpers import mObject, getHotkeys, terminateOldListener, storeListenerPID
from time import sleep
from win32gui import GetForegroundWindow
from win32process import GetWindowThreadProcessId
from psutil import Process
from datetime import datetime
from queue import Queue

import threading
import keyboard


statics = dict()    # Global dict for relative encoder values
process = Queue()   # Processing queue


# Initializes the midi interface with the default midi device if possible
def connectMidi():
    while True:
        try:
            m.init()
            midIn = m.Input(m.get_default_input_id())
            return midIn
        except m.MidiException:
            m.quit()
            sleep(1)


# Builds a list of active hotkeys based on Universal hotkeys and focused window hotkeys
########################################################################################
def getActiveHotkeys():
    focused = getFocusedWindow()    # Get the process name of the focused window
    hotkeys = getHotkeys()          # Get a list of hotkeys from the json
    activeDict = dict()             # Create a dict to store active hotkeys

    # Handle case when universal hotkeys exist and focused window hotkeys exist
    if focused in hotkeys.keys() and "Universal" in hotkeys.keys():
        # Handle focused window hotkeys
        for key in hotkeys[focused].keys():
            # If there's also a universal set then combine the hotkeys with focused priority
            if key in hotkeys["Universal"].keys():
                activeDict[key] = {**hotkeys["Universal"][key], **hotkeys[focused][key]}
            # Otherwise just add the focused hotkeys to the dictionary
            else:
                activeDict[key] = hotkeys[focused][key]

        # Handle leftover hotkeys in the universal set that weren't handled in the focused set if they exist
        for key in (set(hotkeys["Universal"].keys()) - set(activeDict.keys())):
            activeDict[key] = hotkeys["Universal"][key]

    # Handle case when there's just universal hotkeys
    elif "Universal" in hotkeys.keys():
        activeDict = hotkeys["Universal"]
    # Handle the case when there's just focused window hotkeys
    elif focused in hotkeys.keys():
        activeDict = hotkeys[focused]

    return activeDict


# Intercept midi events and add them to a processing queue
########################################################################################
def intercept():
    midIn = connectMidi()       # Initialize midi interface
    lastIn = datetime.now()     # Get current time for reference
    while True:
        now = datetime.now()    # Get current time for reference
        # If a midi event has occurred
        if midIn.poll():
            lastIn = datetime.now()     # Save the current time for reference
            event = midIn.read(50)      # Read up to 50 midi events

            # If there are more than 10 events, a slider is probably being used and we can just use the last event
            if len(event) > 10:
                event = event[len(event) - 1]
                process.put(event)

            # Otherwise put the midi event in the processing queue
            else:
                for ev in event:
                    process.put(ev)

        # Check if it's been 5 seconds since the last midi input (This is used for handling device disconnects)
        elif (now - lastIn).seconds > 5:
            # Attempt to close the midi interface connection
            try:
                midIn.close()
            # General exception because I can't seem to except pygame.midi exceptions
            except Exception:
                pass
            m.quit()                    # Finalize midi interface closure
            midIn = connectMidi()       # Re-initialize the midi interface
            lastIn = datetime.now()     # Save the current time for reference

        # Only handle events every 50 ms
        sleep(.05)


# Handle the midi event that was intercepted
########################################################################################
def handler(mob):
    activeDict = getActiveHotkeys()     # Get a list of the active hotkeys at the time of handling

    # Handle CC type events (encoder / slider)
    if mob.eType == 11 and '11' in activeDict.keys():
        # Check if input ID corresponds to hotkey
        if str(mob.ID) in activeDict['11'].keys():
            # Check if encoder has been used before
            if mob.ID in statics.keys():
                # Handle right rotation
                if mob.val > statics.get(mob.ID) or mob.val == 127:
                    keyboard.press_and_release(activeDict['11'][str(mob.ID)][1])
                # Handle left rotation
                elif mob.val < statics.get(mob.ID) or mob.val == 0:
                    keyboard.press_and_release(activeDict['11'][str(mob.ID)][0])
                statics.update({mob.ID: mob.val})

            # If encoder hasn't been used before then save the value (unfortunately lose first input)
            elif mob.ID not in statics.keys():
                statics.update({mob.ID: mob.val})

    # Handle note down events (button)
    elif mob.eType == 9 and '9' in activeDict.keys():
        if str(mob.ID) in activeDict['9'].keys():
            keyboard.press_and_release(activeDict['9'][str(mob.ID)])

    # Handle note up events (button)
    elif mob.eType == 8 and '8' in activeDict.keys():
        if str(mob.ID) in activeDict['8'].keys():
            keyboard.press_and_release(activeDict['8'][str(mob.ID)])


# Process the midi event queue every 50 ms
########################################################################################
def processQueue():
    while True:
        while not process.empty():
            event = process.get()
            mob = mObject(event[0][0] >> 4, event[0][1], event[0][2])
            handler(mob)
        sleep(.05)


# Get the process name of the focused window
########################################################################################
def getFocusedWindow():
    pid = GetWindowThreadProcessId(GetForegroundWindow())
    return Process(pid[-1]).name()


if __name__ == '__main__':
    terminateOldListener()                                  # Close the old listener (if it exists)
    storeListenerPID()                                      # Store the new listener PID (this process)
    processor = threading.Thread(target=processQueue)       # Create the processing thread
    processor.daemon = True                                 # Set thread as daemon for safe exits
    processor.start()                                       # Start the processing thread
    intercept()                                             # Start midi interceptor
