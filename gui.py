"""
Module to run the pre test gui where tests are selected and queued
"""
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import json
import re
import os
import pandas as pd
import tests


class GUI():
    """
    A class to contain the tkinter GUI
    """

    def __init__(self):
        '''
        upon init, creates GUI
        '''
        # Create tkinter window
        self._root = Tk()
        self._root.title("Keithley 2401 GUI")  # Title the window
        self._root.grid_columnconfigure(0, weight=1)  # Config rows and cols
        self._root.grid_rowconfigure(0, weight=1)
        # Define all exported variables
        self._iv_range = StringVar(self._root)
        self._iv_mode = StringVar(self._root)
        self._iv_space = StringVar(self._root)
        self._iv_source_voltage = DoubleVar(self._root)
        self._iv_source_delay = DoubleVar(self._root)
        self._iv_source_voltage_start = DoubleVar(self._root)
        self._iv_source_voltage_stop = DoubleVar(self._root)
        self._iv_num_steps = IntVar(self._root)
        self._iv_current_compliance = DoubleVar(self._root)
        self._iv_is_up_down = BooleanVar(self._root)
        self._iv_accuracy = DoubleVar(self._root)
        self._iv_cycles = IntVar(self._root)
        self._et_set_voltage = DoubleVar(self._root)
        self._et_read_voltage = DoubleVar(self._root)
        self._et_reset_voltage = DoubleVar(self._root)
        self._et_cycles = IntVar(self._root)
        self._et_current_compliance = DoubleVar(self._root)
        self._et_source_voltage = DoubleVar(self._root)
        self._et_source_delay = DoubleVar(self._root)
        self._chiplet_name = StringVar(self._root)

        # create a grid for storing the positions of selected devices
        self._grid_size = 8
        self._devices_grid = []
        for _ in range(self._grid_size):
            row = [0] * self._grid_size
            self._devices_grid.append(row)

        # Variable to check if new tests were requested or if window was closed another way
        self._tests_requested = []

        # count to label tests better
        self._iv_test_num = 1
        self._et_test_num = 1
        self._set_num = 1
        self._reset_num = 1

        self.gui_main_window()

    def gui_start(self):
        '''
        Starts gui by running the tkinter mainloop
        '''
        self._root.mainloop()

    def iv_frame_create(self, window):
        '''
        Create IV GUI frame
        '''
        # Redefine variables
        source_voltage = self._iv_source_voltage
        source_delay = self._iv_source_delay
        source_voltage_start = self._iv_source_voltage_start
        source_voltage_stop = self._iv_source_voltage_stop
        num_steps = self._iv_num_steps
        current_compliance = self._iv_current_compliance
        is_up_down = self._iv_is_up_down
        accuracy = self._iv_accuracy
        cycles = self._iv_cycles
        rangename = self._iv_range
        modename = self._iv_mode
        spacename = self._iv_space
        source_delay_minmax = [0.0, .25]
        source_voltage_minmax = [0.0, 3.5]
        current_minmax = [0.0, 0.01]
        num_steps_minmax = [1, 100]

        # Create frame structure to place widgets in for IV Test
        frame = ttk.Frame(window, padding=(12, 5, 12, 0))
        frame.grid(column=0, row=0, sticky=(N, W, E, S))
        frame.configure(borderwidth=5, relief='raised')

        # Create option lists for non-numeric inputs
        sweep_range_label = Label(frame, text='Sweep Range:')
        sr_choice_1 = Radiobutton(frame, text="BEST", variable=rangename,
                                  value="BEST")
        voltage_mode_label = Label(frame, text='Voltage Mode:')
        vm_choice_1 = Radiobutton(frame, text="SWE", variable=modename,
                                  value="SWE")
        sweep_space_label = Label(frame, text='Sweep Space:')
        ss_choice_1 = Radiobutton(frame, text="Linear", variable=spacename,
                                  value="LIN")
        ss_choice_2 = Radiobutton(frame, text="Logarithmic", variable=spacename,
                                  value="LOG")

        # Set starting values based on previous set values
        def get_start_values(filepath="values.json"):
            try:  # Open JSON file if one exists, otherwise tell user no previous data available
                with open(filepath, 'r') as openfile:
                    saved_vals = json.load(openfile)

                # Take previous values from JSON file and give everything a starting value
                source_voltage.set(saved_vals["iv_source_voltage"])
                source_delay.set(saved_vals["iv_source_delay"])
                source_voltage_start.set(saved_vals["iv_source_voltage_start"])
                source_voltage_stop.set(saved_vals["iv_source_voltage_stop"])
                num_steps.set(saved_vals["iv_log_num_steps"])
                current_compliance.set(saved_vals["iv_current_compliance"])
                is_up_down.set(saved_vals["iv_is_up_down"])
                accuracy.set(saved_vals["iv_accuracy"])
                rangename.set(saved_vals["iv_range"])
                modename.set(saved_vals["iv_mode"])
                spacename.set(saved_vals["iv_space"])
                cycles.set(saved_vals("iv_cycles"))
            except:
                print("Previous values not available.")

        get_start_values()

        # Label the frame
        iv_test_label = Label(frame, text="IV Test Parameters")
        iv_test_label.configure(font=("Arial", 28))

        # Create sliders and text entry points for numeric inputs
        src_voltage_label = Label(frame, text='Source Voltage:')
        src_voltage_scale = Scale(
            frame, variable=source_voltage, orient="horizontal",
            from_=source_voltage_minmax[0], to=source_voltage_minmax[1],
            resolution=0.1, showvalue=0,
            tickinterval=source_voltage_minmax[1]-source_voltage_minmax[0]
        )
        src_voltage_entry = Entry(frame, textvariable=source_voltage)

        src_delay_label = Label(frame, text='Source delay:')
        src_delay_scale = Scale(
            frame, variable=source_delay, orient="horizontal",
            from_=source_delay_minmax[0], to=source_delay_minmax[1],
            resolution=0.01, showvalue=0,
            tickinterval=source_delay_minmax[1]-source_delay_minmax[0]
        )
        src_delay_entry = Entry(frame, textvariable=source_delay)

        src_voltage_start_label = Label(frame, text='Source Voltage Start:')
        src_voltage_start_scale = Scale(
            frame, variable=source_voltage_start, orient="horizontal",
            from_=source_voltage_minmax[0], to=source_voltage_minmax[1],
            resolution=0.1, showvalue=0,
            tickinterval=source_voltage_minmax[1]-source_voltage_minmax[0]
        )
        src_voltage_start_entry = Entry(
            frame, textvariable=source_voltage_start)

        src_voltage_stop_label = Label(frame, text='Source Voltage Stop:')
        src_voltage_stop_scale = Scale(
            frame, variable=source_voltage_stop, orient="horizontal",
            from_=source_voltage_minmax[0], to=source_voltage_minmax[1],
            resolution=0.1, showvalue=0,
            tickinterval=source_voltage_minmax[1]-source_voltage_minmax[0]
        )
        src_voltage_stop_entry = Entry(frame, textvariable=source_voltage_stop)

        num_steps_label = Label(frame, text='Number of Steps:')
        num_steps_scale = Scale(
            frame, variable=num_steps, orient="horizontal",
            from_=num_steps_minmax[0], to=num_steps_minmax[1],
            resolution=1, showvalue=0,
            tickinterval=num_steps_minmax[1]-num_steps_minmax[0]
        )
        num_steps_entry = Entry(frame, textvariable=num_steps)

        accuracy_label = Label(frame, text='Accuracy:')
        accuracy_scale = Scale(
            frame, variable=accuracy, orient="horizontal",
            from_=0.01, to=10, resolution=.01, showvalue=0,
            tickinterval=10-0.01
        )
        accuracy_entry = Entry(frame, textvariable=accuracy)

        current_compliance_label = Label(frame, text='Current Compliance:')
        current_compliance_scale = Scale(
            frame, variable=current_compliance, orient="horizontal",
            from_=current_minmax[0], to=current_minmax[1],
            resolution=0.00001, showvalue=0,
            tickinterval=current_minmax[1]-current_minmax[0]
        )
        current_compliance_entry = Entry(
            frame, textvariable=current_compliance)
       
        cycles_label = Label(frame, text='Cycles')
        cycles_scale = Scale(frame, variable=cycles, orient="horizontal",from_=0, to=100, resolution=1, showvalue=0,tickinterval=100-0)
        cycles_entry = Entry(frame,textvariable=cycles)

        stairs_button_label = Label(frame, text="Stairs up and down?")
        stairs_button = Checkbutton(frame, variable=is_up_down, width=20)

        # Place items in frame
        def grid_assign():
            iv_test_label.grid(column=0, columnspan=5, row=0)

            sweep_range_label.grid(column=0, row=2)
            sr_choice_1.grid(column=0, row=3)
            voltage_mode_label.grid(column=1, row=2)
            vm_choice_1.grid(column=1, row=3)
            sweep_space_label.grid(column=2, row=2)
            ss_choice_1.grid(column=2, row=3)
            ss_choice_2.grid(column=2, row=4)

            src_voltage_label.grid(column=3, columnspan=1, row=1, padx=10)
            src_voltage_entry.grid(
                column=3, columnspan=1, row=2, padx=10, pady=5)
            src_voltage_scale.grid(
                column=3, columnspan=1, row=3, padx=10, pady=0)

            src_delay_label.grid(column=3, columnspan=1, row=4, padx=10)
            src_delay_entry.grid(column=3, columnspan=1,
                                 row=5, padx=10, pady=5)
            src_delay_scale.grid(column=3, columnspan=1,
                                 row=6, padx=10, pady=0)

            src_voltage_start_label.grid(
                column=0, columnspan=1, row=7, padx=10)
            src_voltage_start_entry.grid(
                column=0, columnspan=1, row=8, padx=10)
            src_voltage_start_scale.grid(
                column=0, columnspan=1, row=9, padx=10)

            src_voltage_stop_label.grid(column=1, columnspan=1, row=7, padx=10)
            src_voltage_stop_entry.grid(column=1, columnspan=1, row=8, padx=10)
            src_voltage_stop_scale.grid(column=1, columnspan=1, row=9, padx=10)

            num_steps_label.grid(column=2, columnspan=1, row=7, padx=10)
            num_steps_entry.grid(column=2, columnspan=1, row=8, padx=10)
            num_steps_scale.grid(column=2, columnspan=1, row=9, padx=10)

            accuracy_label.grid(column=3, columnspan=1, row=7, padx=10)
            accuracy_entry.grid(column=3, columnspan=1, row=8, padx=10)
            accuracy_scale.grid(column=3, columnspan=1, row=9, padx=10)

            current_compliance_label.grid(
                column=4, columnspan=1, row=1, padx=10)
            current_compliance_entry.grid(
                column=4, columnspan=1, row=2, padx=10, pady=5)
            current_compliance_scale.grid(
                column=4, columnspan=1, row=3, padx=10, pady=0)

            cycles_label.grid(column=4,columnspan=1,row=4, padx=10)
            cycles_entry.grid(column=4,columnspan=1,row=5,padx=10,pady=5)
            cycles_scale.grid(column=4,columnspan=1,row=6, padx=10, pady=0)
            stairs_button_label.grid(column=4, row=7)
            stairs_button.grid(column=4, row=8)

        grid_assign()

        # Presets
        def store_preset():
            '''
            Runs when save preset button is pushed
            takes current config and saves it to a json
            Prompts user for preset name in popup window
            '''

            preset = StringVar()

            def preset_window():
                # Create new window
                window = Toplevel()
                # Ensure window always shows up in the same space
                pos_x = self._root.winfo_x()
                pos_y = self._root.winfo_y()
                window.geometry(f"+{pos_x+600}+{pos_y+400}")
                # Populate window
                label1 = Label(window, text="Enter preset name:")
                label1.grid(column=0, row=0)
                preset_entry = Entry(window, textvariable=preset)
                preset_entry.grid(column=0, row=1)
                label2 = Label(window, text="When finished, exit the window.")
                label2.grid(column=0, row=2)
                label3 = Label(
                    window, text="Note: You can rewrite an old preset by\n \
                                  assigning a new preset the same name")
                label3.grid(column=0, row=4, pady=15)

            preset_window()
            # Wait to do anything else until popup window is closed
            self._root.wait_window(window)
            preset_name = preset.get()
            if preset_name == "":
                messagebox.showerror(
                    "Preset Warning", "You must provide a name for the preset")
                preset_window()
            else:
                dictionary = {
                    "iv_range": self._iv_range.get(),
                    "iv_mode": self._iv_mode.get(),
                    "iv_space": self._iv_space.get(),
                    "iv_source_voltage": self._iv_source_voltage.get(),
                    "iv_source_delay": self._iv_source_delay.get(),
                    "iv_source_voltage_start": self._iv_source_voltage_start.get(),
                    "iv_source_voltage_stop": self._iv_source_voltage_stop.get(),
                    "iv_log_num_steps": self._iv_num_steps.get(),
                    "iv_current_compliance": self._iv_current_compliance.get(),
                    "iv_is_up_down": self._iv_is_up_down.get(),
                    "iv_accuracy": self._iv_accuracy.get(),
                    "iv_cycles": self._iv_cycles.get()
                }
                with open(f"IVTestPresets/{preset_name}.json", "w") as outfile:
                    json.dump(dictionary, outfile)

            update_preset_list()

        def load_preset():
            '''
            Read from json file of selected preset and update current IVTest config to match
            '''
            preset_name = selected_preset.get()
            get_start_values(f"IVTestPresets/{preset_name}.json")

        save_preset_button = Button(
            frame, text="save preset", command=store_preset)
        save_preset_button.grid(column=9, row=3)

        selected_preset = StringVar()
        presets = ttk.Combobox(frame, width=27, textvariable=selected_preset)
        presets.grid(column=9, row=1)

        # Create a list of files in DevicePresets folder

        def update_preset_list():
            preset_list = os.listdir("IVTestPresets/")
            for _, preset_name in enumerate(preset_list):
                preset_name = preset_name[0:-5]
            return preset_list

        # Adding list to presets combobox
        presets['values'] = update_preset_list()

        load_preset_button = Button(
            frame, text="load preset", command=load_preset)
        load_preset_button.grid(column=9, row=5)

    def et_frame_create(self, window):
        '''
        Create and populate endurance test frame of GUI

        '''
        # Redeclare variables
        set_voltage = self._et_set_voltage
        read_voltage = self._et_read_voltage
        reset_voltage = self._et_reset_voltage
        cycles = self._et_cycles
        current_compliance = self._et_current_compliance
        source_voltage = self._et_source_voltage
        source_delay = self._et_source_delay
        source_delay_minmax = [0.0, .25]
        source_voltage_minmax = [-1.5, 3.5]
        current_minmax = [0.0, 0.01]
        cycles_minmax = [5, 500]

        def get_start_values(filename="values.json"):
            '''
            Attempts to collect most recent values to preset gui inputs
            '''
            try:  # Open JSON file if one exists, otherwise tell user no previous data available
                with open(filename, 'r') as openfile:
                    saved_vals = json.load(openfile)

                # Take previous values from JSON file and give everything a starting value
                set_voltage.set(saved_vals["et_set_voltage"])
                read_voltage.set(saved_vals["et_read_voltage"])
                reset_voltage.set(saved_vals["et_reset_voltage"])
                cycles.set(saved_vals["et_cycles"])
                current_compliance.set(saved_vals["et_current_compliance"])
                source_voltage.set(saved_vals["et_source_voltage"])
                source_delay.set(saved_vals["et_source_delay"])
            except:
                print("Previous values not available.")

        get_start_values()

        # Created frame for Endurance Test
        frame = ttk.Frame(window, padding=(12, 5, 12, 0))
        frame.grid(column=0, row=0, sticky=(N, W, E, S))
        frame.configure(borderwidth=5, relief='raised')

        # Label the frame
        et_test_label = Label(frame, text="Endurance Test Parameters")
        et_test_label.configure(font=("Arial", 28))
        et_test_label.grid(column=0, columnspan=5, row=0)

        # Create Widgets for inputs
        set_voltage_label = Label(frame, text='Set Voltage:')
        set_voltage_scale = Scale(frame, variable=set_voltage, orient="horizontal",
                                  from_=source_voltage_minmax[0], to=source_voltage_minmax[1],
                                  resolution=1, showvalue=0,
                                  tickinterval=source_voltage_minmax[1]-source_voltage_minmax[0])
        set_voltage_entry = Entry(frame, textvariable=set_voltage)
        set_voltage_label.grid(column=0, row=1)
        set_voltage_entry.grid(column=0, row=2)
        set_voltage_scale.grid(column=0, row=3)

        reset_voltage_label = Label(frame, text='Reset Voltage:')
        reset_voltage_scale = Scale(frame, variable=reset_voltage, orient="horizontal",
                                    from_=source_voltage_minmax[0], to=source_voltage_minmax[1],
                                    resolution=1, showvalue=0,
                                    tickinterval=source_voltage_minmax[1]-source_voltage_minmax[0])
        reset_voltage_entry = Entry(frame, textvariable=reset_voltage)
        reset_voltage_label.grid(column=0, row=4)
        reset_voltage_entry.grid(column=0, row=5)
        reset_voltage_scale.grid(column=0, row=6)

        read_voltage_label = Label(frame, text='Read Voltage:')
        read_voltage_scale = Scale(frame, variable=read_voltage, orient="horizontal",
                                   from_=source_voltage_minmax[0], to=source_voltage_minmax[1],
                                   resolution=0.1, showvalue=0,
                                   tickinterval=source_voltage_minmax[1]-source_voltage_minmax[0])
        read_voltage_entry = Entry(frame, textvariable=read_voltage)
        read_voltage_label.grid(column=0, row=7)
        read_voltage_entry.grid(column=0, row=8)
        read_voltage_scale.grid(column=0, row=9)

        cycles_label = Label(frame, text='Number of Cycles:')
        cycles_scale = Scale(frame, variable=cycles, orient="horizontal",
                             from_=cycles_minmax[0], to=cycles_minmax[1],
                             resolution=5, showvalue=0,
                             tickinterval=cycles_minmax[1]-cycles_minmax[0])
        cycles_entry = Entry(frame, textvariable=cycles)
        cycles_label.grid(column=2, row=1)
        cycles_entry.grid(column=2, row=2)
        cycles_scale.grid(column=2, row=3)

        src_voltage_label = Label(frame, text='Source Voltage:')
        src_voltage_scale = Scale(frame, variable=source_voltage, orient="horizontal",
                                  from_=source_voltage_minmax[0], to=source_voltage_minmax[1],
                                  resolution=0.1, showvalue=0,
                                  tickinterval=source_voltage_minmax[1]-source_voltage_minmax[0])
        src_voltage_entry = Entry(frame, textvariable=source_voltage)
        src_voltage_label.grid(column=1, row=1)
        src_voltage_entry.grid(column=1, row=2)
        src_voltage_scale.grid(column=1, row=3)

        src_delay_label = Label(frame, text='Source delay:')
        src_delay_scale = Scale(frame, variable=source_delay, orient="horizontal",
                                from_=source_delay_minmax[0], to=source_delay_minmax[1],
                                resolution=0.01, showvalue=0,
                                tickinterval=source_delay_minmax[1]-source_delay_minmax[0])
        src_delay_entry = Entry(frame, textvariable=source_delay)
        src_delay_label.grid(column=1, row=4)
        src_delay_entry.grid(column=1, row=5)
        src_delay_scale.grid(column=1, row=6)

        current_compliance_label = Label(frame, text='Current Compliance:')
        current_compliance_scale = Scale(frame, variable=current_compliance, orient="horizontal",
                                         from_=current_minmax[0], to=current_minmax[1],
                                         resolution=0.00001, showvalue=0,
                                         tickinterval=current_minmax[1]-current_minmax[0])
        current_compliance_entry = Entry(
            frame, textvariable=current_compliance)
        current_compliance_label.grid(column=3, row=1)
        current_compliance_entry.grid(column=3, row=2)
        current_compliance_scale.grid(column=3, row=3)

        # presets
        def store_preset():
            '''
            Runs when save preset button is pushed
            takes current config and saves it to a json
            Prompts user for preset name in popup window
            '''

            preset = StringVar()

            def preset_window():
                # Create new window
                window = Toplevel()
                # Ensure window always shows up in the same space
                pos_x = self._root.winfo_x()
                pos_y = self._root.winfo_y()
                window.geometry(f"+{pos_x+600}+{pos_y+400}")
                # Populate window
                label1 = Label(window, text="Enter preset name:")
                label1.grid(column=0, row=0)
                preset_entry = Entry(window, textvariable=preset)
                preset_entry.grid(column=0, row=1)
                label2 = Label(window, text="When finished, exit the window.")
                label2.grid(column=0, row=2)
                label3 = Label(
                    window, text="Note: You can rewrite an old preset by\n \
                                  assigning a new preset the same name")
                label3.grid(column=0, row=4, pady=15)

            preset_window()
            # Wait to do anything else until popup window is closed
            self._root.wait_window(window)
            preset_name = preset.get()
            if preset_name == "":
                messagebox.showerror(
                    "Preset Warning", "You must provide a name for the preset")
                preset_window()
            else:
                dictionary = {
                    "et_set_voltage": self._et_set_voltage.get(),
                    "et_read_voltage": self._et_read_voltage.get(),
                    "et_reset_voltage": self._et_reset_voltage.get(),
                    "et_cycles": self._et_cycles.get(),
                    "et_current_compliance": self._et_current_compliance.get(),
                    "et_source_voltage": self._et_source_voltage.get(),
                    "et_source_delay": self._et_source_delay.get()
                }
                with open(f"EnduranceTestPresets/{preset_name}.json", "w") as outfile:
                    json.dump(dictionary, outfile)

            update_preset_list()

        def load_preset():
            '''
            Read from json file of selected preset and update current IVTest config to match
            '''
            preset_name = selected_preset.get()
            get_start_values(f"EnduranceTestPresets/{preset_name}.json")

        save_preset_button = Button(
            frame, text="save preset", command=store_preset)
        save_preset_button.grid(column=9, row=3)

        selected_preset = StringVar()
        presets = ttk.Combobox(frame, width=27, textvariable=selected_preset)
        presets.grid(column=9, row=1)

        # Create a list of files in DevicePresets folder

        def update_preset_list():
            preset_list = os.listdir("EnduranceTestPresets/")
            for _, preset_name in enumerate(preset_list):
                preset_name = preset_name[0:-5]
            return preset_list

        # Adding list to presets combobox
        presets['values'] = update_preset_list()

        load_preset_button = Button(
            frame, text="load preset", command=load_preset)
        load_preset_button.grid(column=9, row=5)

    def device_select_frame_create(self, window, col, row):
        '''
        Create and populate device selector frame of GUI

        '''
        # Create frame
        frame = ttk.Frame(window, padding=(12, 5, 12, 0))
        frame.grid(column=col, columnspan=2, row=row,
                   rowspan=4, sticky=(N, W, E, S))
        frame.configure(borderwidth=5, relief='raised')

        # Label the frame
        ds_label = Label(frame, text="Endurance Test Parameters")
        ds_label.configure(font=("Arial", 28))
        ds_label.grid(column=0, columnspan=8, row=0)

        # Create and place widgets for device selection
        device_buttons = []
        for col in range(self._grid_size):
            row_list = []
            for row in range(self._grid_size):
                button = Button(frame, text=0, bg="light gray",
                                activebackground="gray90", width=2, height=2)
                button.grid(row=row+1, column=col, sticky=NW+NE+SW+SE+N+S+E+W)
                row_list.append(button)
            device_buttons.append(row_list)

        def change_device_grid_value(row, col):
            if self._devices_grid[row][col] == 1:
                self._devices_grid[row][col] = 0
                device_buttons[row][col].config(
                    text="0", bg="light gray", activebackground="gray90")
                return
            self._devices_grid[row][col] = 1
            device_buttons[row][col].config(
                text="1", bg="deep sky blue", activebackground="light sky blue")

        for row in range(self._grid_size):
            for col in range(self._grid_size):
                device_buttons[row][col].config(
                    command=lambda row=row, col=col: change_device_grid_value(row, col))

        # Select row buttons
        row_buttons = []
        for row in range(self._grid_size):
            button = Button(frame, text="Select Row")
            button.grid(row=row+1, column=8, sticky=NW+NE+SW+SE+N+S+E+W)
            row_buttons.append(button)

        def select_row(row):
            if row_buttons[row]["text"] == "Select Row":
                row_buttons[row]["text"] = "Deselect Row"
                for col in range(self._grid_size):
                    self._devices_grid[col][row] = 1
                    device_buttons[col][row].config(
                        text="1", bg="deep sky blue", activebackground="light sky blue")
            else:
                row_buttons[row]["text"] = "Select Row"
                for col in range(self._grid_size):
                    self._devices_grid[col][row] = 0
                    device_buttons[col][row].config(
                        text="0", bg="light gray", activebackground="gray90")

        for row, button in enumerate(row_buttons):
            button.config(command=lambda row=row: select_row(row))

        # Select column buttons
        col_buttons = []
        for col in range(self._grid_size):
            button = Button(frame, text="Select\nColumn")
            button.grid(row=9, column=col, sticky=NW+NE+SW+SE+N+S+E+W)
            col_buttons.append(button)

        def select_col(col):
            if col_buttons[col]["text"] == "Select\nColumn":
                col_buttons[col]["text"] = "Deselect\nColumn"
                for row in range(self._grid_size):
                    self._devices_grid[col][row] = 1
                    device_buttons[col][row].config(
                        text="1", bg="deep sky blue", activebackground="light sky blue")
            else:
                col_buttons[col]["text"] = "Select\nColumn"
                for row in range(self._grid_size):
                    self._devices_grid[col][row] = 0
                    device_buttons[col][row].config(
                        text="0", bg="light gray", activebackground="gray90")

        for col, button in enumerate(col_buttons):
            button.config(command=lambda col=col: select_col(col))

        # Select all button
        select_all_button = Button(frame, text="Select All")
        select_all_button.grid(column=8, row=9)

        def select_all():
            if select_all_button["text"] == "Select All":
                select_all_button["text"] = "Deselect All"
                for col in range(self._grid_size):
                    for row in range(self._grid_size):
                        self._devices_grid[col][row] = 1
                        device_buttons[col][row].config(
                            text="1", bg="deep sky blue", activebackground="light sky blue")
            else:
                select_all_button["text"] = "Select All"
                for col in range(self._grid_size):
                    for row in range(self._grid_size):
                        self._devices_grid[col][row] = 0
                        device_buttons[col][row].config(
                            text="0", bg="light gray", activebackground="gray90")

        select_all_button.config(command=select_all)

        def store_preset():
            '''
            Runs when save preset button is pushed
            takes current grid config and saves it to csv
            Prompts user for preset name in popup window
            '''

            preset = StringVar()

            def preset_window():
                # Create new window
                window = Toplevel()
                # Ensure window always shows up in the same space
                pos_x = self._root.winfo_x()
                pos_y = self._root.winfo_y()
                window.geometry(f"+{pos_x+600}+{pos_y+400}")
                # Populate window
                label1 = Label(window, text="Enter preset name:")
                label1.grid(column=0, row=0)
                preset_entry = Entry(window, textvariable=preset)
                preset_entry.grid(column=0, row=1)
                label2 = Label(window, text="When finished, exit the window.")
                label2.grid(column=0, row=2)
                label3 = Label(
                    window, text="Note: You can rewrite an old preset by\n \
                                  assigning a new preset the same name")
                label3.grid(column=0, row=4, pady=15)

            preset_window()
            # Wait to do anything else until popup window is closed
            self._root.wait_window(window)
            preset_name = preset.get()
            if preset_name == "":
                preset_window()
                messagebox.showerror(
                    "Preset Warning", "You must provide a name for the preset")
            else:
                # Turn grid config into pandas DataFrame for use of to_csv
                dataframe = pd.DataFrame(self._devices_grid)
                dataframe.to_csv(f"DevicePresets/{preset_name}.csv",
                                 header=False, index=False)
                # Update list of presets on main window
                update_preset_list()

        def load_preset():
            '''
            Read from csv file of selected preset and update current grid config to match
            '''
            preset_name = selected_preset.get()
            dataframe = pd.read_csv(
                f"DevicePresets/{preset_name}.csv", header=None, index_col=None)
            for col in range(self._grid_size):
                for row in range(self._grid_size):
                    if dataframe[row][col] == 1:
                        self._devices_grid[col][row] = 1
                        device_buttons[col][row].config(
                            text="1", bg="deep sky blue", activebackground="light sky blue")
                    else:
                        self._devices_grid[col][row] = 0
                        device_buttons[col][row].config(
                            text="0", bg="light gray", activebackground="gray90")

        save_preset_button = Button(
            frame, text="save preset", command=store_preset)
        save_preset_button.grid(column=9, row=3)

        selected_preset = StringVar()
        presets = ttk.Combobox(frame, width=27, textvariable=selected_preset)
        presets.grid(column=9, row=1)

        # Create a list of files in DevicePresets folder

        def update_preset_list():
            preset_list = os.listdir("DevicePresets/")
            for _, preset_name in enumerate(preset_list):
                preset_name = preset_name[0:-4]
            return preset_list

        # Adding list to presets combobox
        presets['values'] = update_preset_list()

        load_preset_button = Button(
            frame, text="load preset", command=lambda: load_preset())
        load_preset_button.grid(column=9, row=5)

        # Try to load most recent grid layout
        try:
            dataframe = pd.read_csv(
                "device_grid_last_vals.csv", header=None, index_col=None)
            for col in range(self._grid_size):
                for row in range(self._grid_size):
                    if dataframe[row][col] == 1:
                        self._devices_grid[col][row] = 1
                        device_buttons[col][row].config(
                            text="1", bg="deep sky blue", activebackground="light sky blue")
                    else:
                        self._devices_grid[col][row] = 0
                        device_buttons[col][row].config(
                            text="0", bg="light gray", activebackground="gray90")
        except:
            print("No previous data available")

    def gui_main_window(self):
        '''
        Creates elements of the GUI for inputs common across all three testing functions
        '''
        # Define variables
        chiplet_name = self._chiplet_name

        def get_start_values():
            try:  # Open JSON file if one exists, otherwise tell user no previous data available
                with open('values.json', 'r') as openfile:
                    saved_vals = json.load(openfile)

                chiplet_name.set(saved_vals["chiplet_name"])
            except:
                print("Previous values not available.")

        get_start_values()

        def add_iv(*args):
            '''

            '''
            # Create new window
            window = Toplevel()
            # Ensure window always shows up in the same space
            pos_x = self._root.winfo_x()
            pos_y = self._root.winfo_y()
            window.geometry(f"+{pos_x+50}+{pos_y+50}")

            # Populate window with IVTest options
            self.iv_frame_create(window)

            # Wait to do anything else until popup window is closed
            self._root.wait_window(window)
            # Make new IVTest object
            iv_test = tests.IVTest(
                grid=self._devices_grid,
                test_num=self._iv_test_num,
                chiplet_name=self._chiplet_name.get(),
                voltage_range=self._iv_range.get(),
                mode=self._iv_mode.get(),
                space=self._iv_space.get(),
                source_voltage=self._iv_source_voltage.get(),
                source_delay=self._iv_source_delay.get(),
                source_voltage_start=self._iv_source_voltage_start.get(),
                source_voltage_stop=self._iv_source_voltage_stop.get(),
                num_steps=self._iv_num_steps.get(),
                current_compliance=self._iv_current_compliance.get(),
                is_up_down=self._iv_is_up_down.get(),
                cycles= self._iv_cycles.get()
                            
                                        )

            test_lb.insert(END, f"IV Test {self._iv_test_num}")
            self._iv_test_num += 1
            self._tests_requested.append(iv_test)

        def add_et(*args):
            '''

            '''
            # Create new window
            window = Toplevel()
            # Ensure window always shows up in the same space
            pos_x = self._root.winfo_x()
            pos_y = self._root.winfo_y()
            window.geometry(f"+{pos_x+50}+{pos_y+50}")

            # Populate window with IVTest options
            self.et_frame_create(window)

            # Wait to do anything else until popup window is closed
            self._root.wait_window(window)
            # Make new EnduranceTest object
            endurance_test = tests.EnduranceTest(
                grid=self._devices_grid,
                test_num=self._et_test_num,
                chiplet_name=self._chiplet_name.get(),
                source_voltage=self._et_source_voltage.get(),
                source_delay=self._et_source_delay.get(),
                current_compliance=self._et_current_compliance.get(),
                cycles=self._et_cycles.get(),
                set_voltage=self._et_set_voltage.get(),
                read_voltage=self._et_read_voltage.get(),
                reset_voltage=self._et_reset_voltage.get()
            )

            test_lb.insert(END, f"Endurance Test {self._et_test_num}")
            self._et_test_num += 1
            self._tests_requested.append(endurance_test)

        def add_set(*args):
            '''
            '''
            test_lb.insert(END, f"Set {self._set_num}")
            self._set_num += 1
            self._tests_requested.append("Set")

        def add_reset(*args):
            '''
            '''
            test_lb.insert(END, f"Reset {self._reset_num}")
            self._reset_num += 1
            self._tests_requested.append("Reset")

        def clear_lb(*args):
            test_lb.delete(0, END)
            self._iv_test_num, self._et_test_num, self._set_num, self._reset_num = 0, 0, 0, 0
            self._tests_requested = []

        # Chip name box
        name_frame = ttk.Frame(self._root, padding=(12, 5, 12, 0))
        name_frame.grid(column=4, columnspan=2, row=0,
                        rowspan=4, sticky=(N, W, E, S))
        name_frame.configure(borderwidth=5, relief='raised')
        chiplet_name_label = Label(name_frame, text="Chiplet Name/Identifier:")
        chiplet_name_entry = Entry(name_frame, textvariable=chiplet_name)
        chiplet_name_label.grid(column=0, row=0, pady=15)
        chiplet_name_entry.grid(column=0, row=1, pady=15)

        # Device grid box
        self.device_select_frame_create(self._root, col=0, row=0)

        # Test queue box
        frame = ttk.Frame(self._root, padding=(12, 5, 12, 0))
        frame.grid(column=2, columnspan=2, row=0,
                   rowspan=4, sticky=(N, W, E, S))
        frame.configure(borderwidth=5, relief='raised')
        test_lb = Listbox(frame, selectmode="BROWSE")
        test_lb_label = Label(frame, text="Test Queue:")
        add_set_button = Button(frame, text="Set", command=add_set)
        add_reset_button = Button(frame, text="Reset", command=add_reset)
        add_iv_button = Button(frame, text="Add IV Test", command=add_iv)
        add_et_button = Button(
            frame, text="Add Endurance Test", command=add_et)
        clear_lb_button = Button(
            frame, text="Clear Test Queue", command=clear_lb)

        test_lb_label.grid(column=1, columnspan=2, row=0)
        test_lb.grid(column=1, columnspan=2, row=1, rowspan=4)
        clear_lb_button.grid(column=1, columnspan=2, row=5, rowspan=1)
        add_iv_button.grid(column=0, columnspan=1, row=1, rowspan=1)
        add_et_button.grid(column=0, columnspan=1, row=2, rowspan=1)
        add_set_button.grid(column=0, columnspan=1, row=3, rowspan=1)
        add_reset_button.grid(column=0, columnspan=1, row=4, rowspan=1)

        # Run button
        button = Button(self._root, text="Run",
                        command=self.set_values, width=25, height=3, background="red",
                        activebackground="tomato")
        button.grid(column=4, columnspan=2, row=4, rowspan=2, padx=0)

    def define_progress_interval(self):
        '''
        Returns a double from 0 to 100 that is the size a single progressbar step should be
        '''
        num_intervals = 0.0
        try:
            for test in self._tests_requested:
                num_intervals += len(test.selected_devices)
            return 100.0/num_intervals
        except:
            print("No tests requested")
            return 100.0

    def set_values(self):
        '''
        Run whenever run button on GUI is pressed
        Reads all values from GUI, saves all values to json file if filled out
        '''
        dictionary = {
            # Generics
            "chiplet_name": self._chiplet_name.get(),
            "progress_interval": self.define_progress_interval(),
            # IV test vals
            "iv_range": self._iv_range.get(),
            "iv_mode": self._iv_mode.get(),
            "iv_space": self._iv_space.get(),
            "iv_source_voltage": self._iv_source_voltage.get(),
            "iv_source_delay": self._iv_source_delay.get(),
            "iv_source_voltage_start": self._iv_source_voltage_start.get(),
            "iv_source_voltage_stop": self._iv_source_voltage_stop.get(),
            "iv_log_num_steps": self._iv_num_steps.get(),
            "iv_current_compliance": self._iv_current_compliance.get(),
            "iv_is_up_down": self._iv_is_up_down.get(),
            "iv_accuracy": self._iv_accuracy.get(),
            "iv_cycles": self._iv_cycles.get(),
            # ET vals
            "et_set_voltage": self._et_set_voltage.get(),
            "et_read_voltage": self._et_read_voltage.get(),
            "et_reset_voltage": self._et_reset_voltage.get(),
            "et_cycles": self._et_cycles.get(),
            "et_current_compliance": self._et_current_compliance.get(),
            "et_source_voltage": self._et_source_voltage.get(),
            "et_source_delay": self._et_source_delay.get()
        }
        with open("values.json", "w") as outfile:
            json.dump(dictionary, outfile)

        # Save device grid
        dataframe = pd.DataFrame(self._devices_grid)
        dataframe.to_csv("device_grid_last_vals.csv",
                         header=False, index=False)

        self._root.destroy()

    def get_requested_tests(self):
        '''
        Returns a list of tests in order to be conducted
        '''
        return self._tests_requested


def check_special_chars(string):
    '''
    return:
        1 if string contains special chars, 0 otherwise
    '''
    if re.search("[^a-zA-Z0-9s]", string):
        return 1
    return 0


#gui = GUI()
#gui.gui_start()
