from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import matplotlib.pyplot as plt
import pandas as pd
import functions


class ResultsGUI():
    """
    A class to contain the tkinter GUI for displaying test results
    """

    def __init__(self, test_list):
        '''
        upon init, creates GUI
        '''
        # Create tkinter window
        self._root = Tk()
        self._root.title("Keithley 2401 GUI")  # Title the window
        self._root.grid_columnconfigure(0, weight=1)  # Config rows and cols
        self._root.grid_rowconfigure(0, weight=1)
        self._test_list = test_list
        self._selected_test_name = StringVar()
        self._selected_device_name = StringVar()
        self._test_dict = {}
        self._device_dict = {}

    def gui_start(self):
        '''
        Runs the tkinter mainloop for the gui
        '''
        self.create_main_window()
        self._root.mainloop()

    def create_main_window(self):
        '''
        Creates the primary window where you can select which test results you
        would like to view
        '''
        # Create list of tests to select from
        self._test_dict = {}
        for _, ele in enumerate(self._test_list):
            self._test_dict[ele.get_test_type()] = ele

        # Get error if this isn't set to some default value
        self._selected_test_name.set(list(self._test_dict.keys())[0])
        tests = ttk.Combobox(self._root, width=27, values=list(self._test_dict.keys()),
                             textvariable=self._selected_test_name)
        tests.grid(column=0, row=1)

        test_select_label = Label(text="Select Test:")
        test_select_label.grid(column=0, row=0)

        # Create list of devices based on the selected test
        def create_devices_list(*args):
            selected_test = self._test_dict[self._selected_test_name.get()]

            self._device_dict = {}
            for _, point in enumerate(selected_test.selected_devices):
                self._device_dict[f"({point.x}, {point.y})"] = point

            # Get error if this isn't set to some default value
            self._selected_device_name.set(list(self._device_dict.keys())[0])
            devices["values"] = list(self._device_dict.keys())

        devices = ttk.Combobox(self._root, width=27, values=list(self._device_dict.keys()),
                               textvariable=self._selected_device_name)
        devices.grid(column=1, row=1)

        device_select_label = Label(text="Select Device:")
        device_select_label.grid(column=1, row=0)

        self._selected_test_name.trace_add(
            "write", callback=create_devices_list)

        def device_name_call(*args):
            self.create_iv_device_stats(self._root, col=2, row=1)

        self._selected_device_name.trace_add(
            "write", callback=device_name_call)

        # button for making a graph
        graph_button = Button(
            self._root, text="Generate Graph", command=self.create_iv_graph)
        graph_button.grid(column=1, row=2)

    def get_filename(self):
        '''
        Return the filename for the specific chosen device test
        '''
        test = self.get_current_test()
        folder_path = functions.create_test_folder(test)
        device = self.get_current_device()
        filename = f'{folder_path}/{test.chiplet_name}_Col{device.x}_Row{device.y}'
        return filename

    def get_current_test(self):
        '''
        Return the currently selected test object
        '''
        return self._test_dict[self._selected_test_name.get()]

    def get_current_device(self):
        '''
        return the currently selected device namedtuple
        '''
        return self._device_dict[self._selected_device_name.get()]

    def create_iv_device_stats(self, window, col, row):
        '''
        Create a fram containing statistical data about the selected test
        '''
        # Create frame
        frame = ttk.Frame(window, padding=(12, 5, 12, 0))
        frame.grid(column=col, columnspan=2, row=row,
                   rowspan=4, sticky=(N, W, E, S))
        frame.configure(borderwidth=5, relief='raised')

        # Label the frame
        ds_label = Label(frame, text=f"{self._selected_test_name.get()}")
        ds_label.configure(font=("Arial", 28))
        ds_label.grid(column=0, columnspan=8, row=0)

        # filename = self.get_filename()

        df = pd.read_excel("_Col5_Row3.xlsx")  # filename) #changed for testing
        stats_df = df[["Voltage", "Current", "Real Resistance"]].describe()

        stats_info = Label(frame, text=stats_df.to_string())
        stats_info.grid(column=0, row=1)

    def create_iv_graph(self):
        '''

        '''
        # filename = self.get_filename()
        df = pd.read_excel("_Col5_Row3.xlsx")

        plt.plot(df["Voltage"], df["Current"])
        plt.show()

    def create_endurance_device_stats(self):
        '''
        '''

    def create_iv_cumulative_stats(self):
        '''
        '''

    def create_endurance_cumulative_stats(self):
        '''
        '''


# gui = ResultsGUI()
# gui.gui_start()
