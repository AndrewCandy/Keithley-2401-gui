from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import json
import re
import os
import pandas as pd
import tests


class ResultsGUI():
    """
    A class to contain the tkinter GUI for displaying test results
    """

    def __init__(self, ran_tests):
        '''
        upon init, creates GUI
        '''
        # Create tkinter window
        self._root = Tk()
        self._root.title("Keithley 2401 GUI")  # Title the window
        self._root.grid_columnconfigure(0, weight=1)  # Config rows and cols
        self._root.grid_rowconfigure(0, weight=1)
        self._ran_tests = ran_tests

    def gui_start(self):
        '''
        Runs the tkinter mainloop for the gui
        '''
        self._root.mainloop()

    def create_main_window(self):
        '''
        '''
        # Create list of tests to select from

        # Create list of devices based on the selected test

        # Create frame for device test statistics

        # Create graph for selected device test

        # Create frame for cumulative test statistics

        # Create graph for cumulative test data


gui = ResultsGUI()
gui.gui_start()
