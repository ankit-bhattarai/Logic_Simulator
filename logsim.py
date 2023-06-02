#!/usr/bin/env python3
"""Parse command line options and arguments for the Logic Simulator.

This script parses options and arguments specified on the command line, and
runs either the command line user interface or the graphical user interface.

Usage
-----
Show help: logsim.py -h
Command line user interface: logsim.py -c <file path>
Graphical user interface: logsim.py <file path>
Graphical user interface (load definition file from GUI): logsim.py -g
"""
import getopt
import sys
import os

import wx

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser
from userint import UserInterface
from gui import Gui

other_locale = {"es_ES.utf8": "Spanish",
                "fr_FR.utf8": "French", "zh_CN.utf8": "Chinese"}
if os.environ.get('LANG') in other_locale:
    print("Hello world in", other_locale[os.environ.get('LANG')])
    lang = wx.LANGUAGE_SPANISH if os.environ.get(
        'LANG') == "es_ES.utf8" else wx.LANGUAGE_CHINESE
    print(wx.Locale.IsAvailable(lang))
else:
    print("Hello world")
    lang = None


def main(arg_list):
    """Parse the command line options and arguments specified in arg_list.

    Run either the command line user interface, the graphical user interface,
    or display the usage message.
    """
    usage_message = ("Usage:\n"
                     "Show help: logsim.py -h\n"
                     "Command line user interface: logsim.py -c <file path>\n"
                     "Graphical user interface: logsim.py <file path>\n"
                     "Graphical user interface (load definition file from GUI): logsim.py -g\n")
    try:
        options, arguments = getopt.getopt(arg_list, "ghc:")
    except getopt.GetoptError:
        print("Error: invalid command line arguments\n")
        print(usage_message)
        sys.exit()

    # Initialise instances of the four inner simulator classes
    names = Names()
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)

    for option, path in options:
        if option == "-h":  # print the usage message
            print(usage_message)
            sys.exit()
        elif option == "-c":  # use the command line user interface
            scanner = Scanner(path, names)
            parser = Parser(names, devices, network, monitors, scanner)
            if parser.parse_network():
                # Initialise an instance of the userint.UserInterface() class
                userint = UserInterface(names, devices, network, monitors)
                userint.command_interface()
        elif option == "-g":  # Load the definition file from the GUI itself
            app = wx.App()
            gui = Gui("Logic Simulator", None, None, None,
                      None, None, None, load_graphically=True, locale=lang)
            gui.Show(True)
            app.MainLoop()

    if not options:  # no option given, use the graphical user interface

        if len(arguments) != 1:  # wrong number of arguments
            print("Error: one file path required\n")
            print(usage_message)
            sys.exit()

        [path] = arguments
        scanner = Scanner(path, names)
        parser = Parser(names, devices, network, monitors, scanner)
        if parser.parse_network():
            # Initialise an instance of the gui.Gui() class
            app = wx.App()
            gui = Gui("Logic Simulator", path, names, devices, network,
                      monitors, scanner, locale=lang)
            gui.Show(True)
            app.MainLoop()


if __name__ == "__main__":
    main(sys.argv[1:])
