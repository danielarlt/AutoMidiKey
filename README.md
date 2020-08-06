# AutoMidiKey
*As a disclaimer I don't know anything about the best practices for GUI programming, and this program is only built to work with Windows.*
## Introduction
Welcome to AutoMidiKey! This project was created with the purpose of being able to easily map midi controller inputs to hotkeys.
The project utilizes Python 3 with Tkinter in order to create a simple GUI that can be used to map midi inputs to hotkeys.
The program allows the user to bind "Universal" hotkeys that work anywhere, as well as application specific hotkeys that work exclusively when 
the specified application is focused, and overwrite "Universal" hotkeys bound to the same input.
Also included in the project is a simple listener that uses the pygame.midi interface to listen for midi inputs and execute the bound hotkeys.
Currently, only midi controller buttons and encoders are supported for mapping.

## Installation
Installation is very simple and all install files are self contained in the AutoMidiKey directory wherever it's been cloned.
In the ``AutoMidiKey\Install`` folder there's a simple ``install.bat`` script that will create a Python virtual environment with the required dependencies where the scripts will be run.
The only requirement for this installation script to work correctly is a valid installation of Python 3 added to the user PATH under "python".

## Usage
In order to easily run the program files in the Python virtual environment, batch files are used for controlling them.
They can be found under the home ``AutoMidiKey`` directory as ``AutoMidiKeyConfig.bat`` which is used for mapping hotkeys, ``AutoMidiKeyListener.bat`` which is used for manually
starting the midi listener, and ``TerminateListner.bat`` which will terminate the midi listener and report true/false if it was able to do so.

The listener is automatically terminated when the configuration program is run as to avoid midi interface conflicts, and automatically restarted once the configuration program is 
closed. If the listener is run through the batch file when it's already running, it will simply shut down the old listener and start a new one to avoid repeat processes.

The configuration program should be pretty straightforward to use, but the basic instructions are as follows:
- Use the "Get Midi" button to listen for midi input, and provide a midi input in order to see it captured with the program.
- Once a midi event is captured, it can be mapped with the "Map Last Midi" button which will prompt for hotkey(s) to bind to the event.
- The mode dropdown allows you to select a program (from a list of running programs) to bind hotkeys to work specifically when the selected application is focused.
- As this mode dropdown shows currently open programs, the "Refresh Modes" button can be used to refresh the list if a new application is opened or an old one is closed.
- The "Edit Hotkeys" button opens a popup that shows all the currently bound hotkeys and the modes to which they're bound. These can be selected, edited, and/or deleted from this popup.
- In the "Edit Hotkeys" popup, the left dropdown allows you to select a mode to see only the hotkeys bound to that mode, or "All" to see all hotkeys and which mode they're bound to from 
the dropdown on the right.

## Bugs
If anybody actually uses this code and runs into issues, feel free to post them here, or email me at danielarlt99@gmail.com
