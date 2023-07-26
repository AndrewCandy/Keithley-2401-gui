"""
Module for creating the post test gui
"""
from tkinter import *
from tkinter import ttk
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import functions


class ResultsGUI():
    """
    A class to contain the tkinter GUI for displaying test results
    """

    def __init__(self, test_list, master_file):
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
        self._master_file = master_file
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


        def create_devices_list(*args):
            """
            Create list of devices based on the selected test
            """
            selected_test = self._test_dict[self._selected_test_name.get()]

            self._device_dict = {}
            for _, point in enumerate(selected_test.selected_devices):
                self._device_dict[f"({point.x}, {point.y})"] = point

            # Get error if this isn't set to some default value
            self._selected_device_name.set(list(self._device_dict.keys())[0])
            devices["values"] = list(self._device_dict.keys())

            # Change graph button command for endurance/iv tests
            if self._selected_test_name.get()[0] == "E":
                graph_button["command"] = self.create_endurance_graph
            elif self._selected_test_name.get()[0] == "F":
                graph_button["command"] = self.create_forming_graph
            elif self._selected_test_name.get()[0] == "R":
                graph_button["command"] = self.create_read_graph
            else:
                graph_button["command"] = self.create_iv_graph

        devices = ttk.Combobox(self._root, width=27, values=list(self._device_dict.keys()),
                               textvariable=self._selected_device_name)
        devices.grid(column=1, row=1)

        device_select_label = Label(text="Select Device:")
        device_select_label.grid(column=1, row=0)

        self._selected_test_name.trace_add(
            "write", callback=create_devices_list)


        def device_name_call(*args):
            if self._selected_test_name.get()[0] == "E":
                self.create_endurance_device_stats(self._root, col=2, row=1)
            elif self._selected_device_name.get()[0] == "F":
                self.create_forming_device_stats(self._root, col=2, row=1)
            else:
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
        filename = f'{folder_path}\Col{device.x}_Row{device.y}.xlsx'
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
        Create a frame containing statistical data about the selected test
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

        filename = self.get_filename()
        dataframe = pd.read_excel(filename)
        stats_df = dataframe[["Voltage", "Current",
                              "Real Resistance"]].describe()

        stats_info = Label(frame, text=stats_df.to_string())
        stats_info.grid(column=0, row=1)

    def create_iv_graph(self):
        '''
        Creates a new window containing an IV graph for the selected device
        '''
        filename = self.get_filename()
        dataframe = pd.read_excel(filename)

        plt.plot(dataframe["Voltage"], dataframe["Current"])
        plt.xlabel("Voltage")
        plt.ylabel("Current")
        plt.title(f"IV for device {self._selected_device_name.get()}")
        plt.show()

    def create_forming_device_stats(self, window, col, row):
        '''
        Create a frame containing statistical data about the selected test
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

        filename = self.get_filename()
        dataframe = pd.read_excel(filename)
        stats_df = dataframe[["Voltage", "Current",
                              "Real Resistance"]].describe()

        stats_info = Label(frame, text=stats_df.to_string())
        stats_info.grid(column=0, row=1)

    def create_forming_graph(self):
        '''
        Creates a new window containing an Forming graph for the selected device
        '''
        filename = self.get_filename()
        dataframe = pd.read_excel(filename)

        plt.plot(dataframe["Voltage"], dataframe["Current"])
        plt.xlabel("Voltage")
        plt.ylabel("Current")
        plt.title(f"Forming for device {self._selected_device_name.get()}")
        plt.show()


    def create_endurance_device_stats(self, window, col, row):
        '''
        Create a frame containing statistical data about the selected test
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

        filename = self.get_filename()
        dataframe = pd.read_excel(filename)
        hrs = functions.find_hrs_et(dataframe)
        lrs = functions.find_lrs_et(dataframe)
        dataframe = pd.DataFrame(columns=['HRS', 'LRS'])
        dataframe['HRS'] = hrs
        dataframe['LRS'] = lrs

        stats_df = dataframe.describe()

        stats_info = Label(frame, text=stats_df.to_string())
        stats_info.grid(column=0, row=1)

    def create_endurance_graph(self):
        '''
        Creates a new window containing a scatter of hrs and lrs resistances for the selected device
        '''
        filename = self.get_filename()
        dataframe = pd.read_excel(filename)

        hrs = functions.find_hrs_et(dataframe)
        lrs = functions.find_lrs_et(dataframe)

        plt.scatter(range(len(hrs)), hrs)
        plt.scatter(range(len(lrs)), lrs)
        plt.xlabel("Cycle #")
        plt.ylabel("Resistance")
        plt.title(f"HRS vs LRS for device {self._selected_device_name.get()}")
        plt.legend(["HRS", "LRS"])
        plt.show()

    def create_read_device_stats(self, window, col, row):
        '''
        Create a frame containing statistical data about the selected test
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

        filename = self.get_filename()
        dataframe = pd.read_excel(filename)
        stats_df = dataframe[["Voltage", "Current",
                              "Real Resistance"]].describe()

        stats_info = Label(frame, text=stats_df.to_string())
        stats_info.grid(column=0, row=1)


    def create_read_graph(self):
        '''
        Creates a new window containing a scatter of hrs and lrs resistances for the selected device
        '''
        summary = pd.read_excel(self._master_file)
        col_list = summary["Col"].to_list()
        row_list = summary["Row"].to_list()

        # Initialize DataFrame to store resistance values
        resistance_array = np.full((8, 8), np.nan)

        for col, row in zip(col_list, row_list):
            if summary["TestType"][row][0] == "R":
                resistance_values = summary.loc[(summary["Col"] == col) & (summary["Row"] == row), "Avg. HRS"]
                resistance_array[row - 1, col - 1] = abs(resistance_values.values[0])

        # Create a DataFrame from the resistance array
        df = pd.DataFrame(resistance_array, columns=np.arange(1, 9), index=np.arange(1, 9))

        cmap = sns.color_palette("coolwarm", as_cmap=True)
        fig, ax = plt.subplots(figsize=(10, 8))

        # Create the heatmap using Seaborn
        sns.heatmap(df, cmap=cmap, annot=True, fmt=".4e", cbar=True, cbar_kws={'label': 'Resistance'}, 
                    mask=df.isnull(), square=True, annot_kws={'color': 'black', 'fontsize': 8}, linewidths=0.5, linecolor='lightgray',
                    robust=False)

        # Set the title and labels
        plt.title('Resistance Heatmap')
        plt.xlabel('Column')
        plt.ylabel('Row')

        # Show the heatmap
        plt.show()
