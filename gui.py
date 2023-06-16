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
        for i in range(self._grid_size):
            row = [0] * self._grid_size
            self._devices_grid.append(row)

        # Variable to check if new tests were requested or if window was closed another way
        self._tests_requested = []

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
        rangename = self._iv_range
        modename = self._iv_mode
        spacename = self._iv_space
        source_delay_minmax = [0.0, .25]
        source_voltage_minmax = [0.0, 3.5]
        current_minmax = [0.0, 0.01]
        num_steps_minmax = [1, 100]

        # Create frame structure to place widgets in for IV Test
        c = ttk.Frame(window, padding=(12, 5, 12, 0))
        c.grid(column=0, row=0, sticky=(N, W, E, S))
        c.configure(borderwidth=5, relief='raised')

        # Create option lists for non-numeric inputs
        sweep_range_label = Label(c, text='Sweep Range:')
        sr_choice_1 = Radiobutton(c, text="BEST", variable=rangename,
                                  value="BEST")
        voltage_mode_label = Label(c, text='Voltage Mode:')
        vm_choice_1 = Radiobutton(c, text="SWE", variable=modename,
                                  value="SWE")
        sweep_space_label = Label(c, text='Sweep Space:')
        ss_choice_1 = Radiobutton(c, text="Linear", variable=spacename,
                                  value="LIN")
        ss_choice_2 = Radiobutton(c, text="Logarithmic", variable=spacename,
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
            except:
                print("Previous values not available.")

        get_start_values()

        # Label the frame
        iv_test_label = Label(c, text="IV Test Parameters")
        iv_test_label.configure(font=("Arial", 28))

        # Create sliders and text entry points for numeric inputs
        src_voltage_label = Label(c, text='Source Voltage:')
        src_voltage_scale = Scale(c, variable=source_voltage, orient="horizontal",
                                  from_=source_voltage_minmax[0], to=source_voltage_minmax[1], resolution=0.1, showvalue=0,
                                  tickinterval=(source_voltage_minmax[1]-source_voltage_minmax[0]))  # , command=check_source_voltage)
        src_voltage_entry = Entry(c, textvariable=source_voltage)

        src_delay_label = Label(c, text='Source delay:')
        src_delay_scale = Scale(c, variable=source_delay, orient="horizontal",
                                from_=source_delay_minmax[0], to=source_delay_minmax[1], resolution=0.01, showvalue=0,
                                tickinterval=(source_delay_minmax[1]-source_delay_minmax[0]))  # , command=check_source_delay)
        src_delay_entry = Entry(c, textvariable=source_delay)

        src_voltage_start_label = Label(c, text='Source Voltage Start:')
        src_voltage_start_scale = Scale(c, variable=source_voltage_start, orient="horizontal",
                                        from_=source_voltage_minmax[0], to=source_voltage_minmax[1], resolution=0.1, showvalue=0,
                                        tickinterval=(source_voltage_minmax[1]-source_voltage_minmax[0]))  # , command=check_voltage_start)
        src_voltage_start_entry = Entry(c, textvariable=source_voltage_start)

        src_voltage_stop_label = Label(c, text='Source Voltage Stop:')
        src_voltage_stop_scale = Scale(c, variable=source_voltage_stop, orient="horizontal",
                                       from_=source_voltage_minmax[0], to=source_voltage_minmax[1], resolution=0.1, showvalue=0,
                                       tickinterval=(source_voltage_minmax[1]-source_voltage_minmax[0]))  # , command=check_voltage_stop)
        src_voltage_stop_entry = Entry(c, textvariable=source_voltage_stop)

        num_steps_label = Label(c, text='Number of Steps:')
        num_steps_scale = Scale(c, variable=num_steps, orient="horizontal",
                                from_=num_steps_minmax[0], to=num_steps_minmax[1], resolution=1, showvalue=0,
                                tickinterval=(num_steps_minmax[1]-num_steps_minmax[0]))  # , command=check_num_steps)
        num_steps_entry = Entry(c, textvariable=num_steps)

        accuracy_label = Label(c, text='Accuracy:')
        accuracy_scale = Scale(c, variable=accuracy, orient="horizontal",
                               from_=0.01, to=10, resolution=.01, showvalue=0, tickinterval=(10-0.01))
        accuracy_entry = Entry(c, textvariable=accuracy)

        current_compliance_label = Label(c, text='Current Compliance:')
        current_compliance_scale = Scale(c, variable=current_compliance, orient="horizontal",
                                         from_=current_minmax[0], to=current_minmax[1], resolution=0.00001, showvalue=0,
                                         tickinterval=(current_minmax[1]-current_minmax[0]))  # , command=check_current)
        current_compliance_entry = Entry(c, textvariable=current_compliance)

        stairs_button_label = Label(c, text="Stairs up and down?")
        stairs_button = Checkbutton(c, variable=is_up_down, width=20)

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

            stairs_button_label.grid(column=4, row=5)
            stairs_button.grid(column=4, row=6)

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
                x = self._root.winfo_x()
                y = self._root.winfo_y()
                window.geometry("+%d+%d" % (x + 600, y + 400))
                # Populate window
                label1 = Label(window, text="Enter preset name:")
                label1.grid(column=0, row=0)
                preset_entry = Entry(window, textvariable=preset)
                preset_entry.grid(column=0, row=1)
                label2 = Label(window, text="When finished, exit the window.")
                label2.grid(column=0, row=2)
                label3 = Label(
                    window, text="Note: You can rewrite an old preset by\nassigning a new preset the same name")
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
                    "iv_accuracy": self._iv_accuracy.get()
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
            c, text="save preset", command=store_preset)
        save_preset_button.grid(column=9, row=3)

        selected_preset = StringVar()
        presets = ttk.Combobox(c, width=27, textvariable=selected_preset)
        presets.grid(column=9, row=1)

        # Create a list of files in DevicePresets folder

        def update_preset_list():
            preset_list = os.listdir("IVTestPresets/")
            for i in range(len(preset_list)):
                preset_list[i] = preset_list[i][0:-5]
            return preset_list

        # Adding list to presets combobox
        presets['values'] = update_preset_list()

        load_preset_button = Button(
            c, text="load preset", command=load_preset)
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
        source_voltage_minmax = [0.0, 3.5]
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
        f = ttk.Frame(window, padding=(12, 5, 12, 0))
        f.grid(column=0, row=0, sticky=(N, W, E, S))
        f.configure(borderwidth=5, relief='raised')

        # Label the frame
        et_test_label = Label(f, text="Endurance Test Parameters")
        et_test_label.configure(font=("Arial", 28))
        et_test_label.grid(column=0, columnspan=5, row=0)

        # Create Widgets for inputs
        set_voltage_label = Label(f, text='Set Voltage:')
        set_voltage_scale = Scale(f, variable=set_voltage, orient="horizontal",
                                  from_=source_voltage_minmax[0], to=source_voltage_minmax[1], resolution=1, showvalue=0,
                                  tickinterval=(source_voltage_minmax[1]-source_voltage_minmax[0]))  # , command=check_num_steps)
        set_voltage_entry = Entry(f, textvariable=set_voltage)
        set_voltage_label.grid(column=0, row=1)
        set_voltage_entry.grid(column=0, row=2)
        set_voltage_scale.grid(column=0, row=3)

        reset_voltage_label = Label(f, text='Reset Voltage:')
        reset_voltage_scale = Scale(f, variable=reset_voltage, orient="horizontal",
                                    from_=source_voltage_minmax[0], to=source_voltage_minmax[1], resolution=1, showvalue=0,
                                    tickinterval=(source_voltage_minmax[1]-source_voltage_minmax[0]))  # , command=check_num_steps)
        reset_voltage_entry = Entry(f, textvariable=reset_voltage)
        reset_voltage_label.grid(column=0, row=4)
        reset_voltage_entry.grid(column=0, row=5)
        reset_voltage_scale.grid(column=0, row=6)

        read_voltage_label = Label(f, text='Read Voltage:')
        read_voltage_scale = Scale(f, variable=read_voltage, orient="horizontal",
                                   from_=source_voltage_minmax[0], to=source_voltage_minmax[1], resolution=0.1, showvalue=0,
                                   tickinterval=(source_voltage_minmax[1]-source_voltage_minmax[0]))  # , command=check_num_steps)
        read_voltage_entry = Entry(f, textvariable=read_voltage)
        read_voltage_label.grid(column=0, row=7)
        read_voltage_entry.grid(column=0, row=8)
        read_voltage_scale.grid(column=0, row=9)

        cycles_label = Label(f, text='Number of Cycles:')
        cycles_scale = Scale(f, variable=cycles, orient="horizontal",
                             from_=cycles_minmax[0], to=cycles_minmax[1], resolution=5, showvalue=0,
                             tickinterval=(cycles_minmax[1]-cycles_minmax[0]))  # , command=check_num_steps)
        cycles_entry = Entry(f, textvariable=cycles)
        cycles_label.grid(column=2, row=1)
        cycles_entry.grid(column=2, row=2)
        cycles_scale.grid(column=2, row=3)

        src_voltage_label = Label(f, text='Source Voltage:')
        src_voltage_scale = Scale(f, variable=source_voltage, orient="horizontal",
                                  from_=source_voltage_minmax[0], to=source_voltage_minmax[1], resolution=0.1, showvalue=0,
                                  tickinterval=(source_voltage_minmax[1]-source_voltage_minmax[0]))  # , command=check_source_voltage)
        src_voltage_entry = Entry(f, textvariable=source_voltage)
        src_voltage_label.grid(column=1, row=1)
        src_voltage_entry.grid(column=1, row=2)
        src_voltage_scale.grid(column=1, row=3)

        src_delay_label = Label(f, text='Source delay:')
        src_delay_scale = Scale(f, variable=source_delay, orient="horizontal",
                                from_=source_delay_minmax[0], to=source_delay_minmax[1], resolution=0.01, showvalue=0,
                                tickinterval=(source_delay_minmax[1]-source_delay_minmax[0]))  # , command=check_source_delay)
        src_delay_entry = Entry(f, textvariable=source_delay)
        src_delay_label.grid(column=1, row=4)
        src_delay_entry.grid(column=1, row=5)
        src_delay_scale.grid(column=1, row=6)

        current_compliance_label = Label(f, text='Current Compliance:')
        current_compliance_scale = Scale(f, variable=current_compliance, orient="horizontal",
                                         from_=current_minmax[0], to=current_minmax[1], resolution=0.00001, showvalue=0,
                                         tickinterval=(current_minmax[1]-current_minmax[0]))  # , command=check_current)
        current_compliance_entry = Entry(f, textvariable=current_compliance)
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
                x = self._root.winfo_x()
                y = self._root.winfo_y()
                window.geometry("+%d+%d" % (x + 600, y + 400))
                # Populate window
                label1 = Label(window, text="Enter preset name:")
                label1.grid(column=0, row=0)
                preset_entry = Entry(window, textvariable=preset)
                preset_entry.grid(column=0, row=1)
                label2 = Label(window, text="When finished, exit the window.")
                label2.grid(column=0, row=2)
                label3 = Label(
                    window, text="Note: You can rewrite an old preset by\nassigning a new preset the same name")
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
            f, text="save preset", command=store_preset)
        save_preset_button.grid(column=9, row=3)

        selected_preset = StringVar()
        presets = ttk.Combobox(f, width=27, textvariable=selected_preset)
        presets.grid(column=9, row=1)

        # Create a list of files in DevicePresets folder

        def update_preset_list():
            preset_list = os.listdir("EnduranceTestPresets/")
            for i in range(len(preset_list)):
                preset_list[i] = preset_list[i][0:-5]
            return preset_list

        # Adding list to presets combobox
        presets['values'] = update_preset_list()

        load_preset_button = Button(
            f, text="load preset", command=load_preset)
        load_preset_button.grid(column=9, row=5)

    def device_select_frame_create(self, window, col, row):
        '''
        Create and populate device selector frame of GUI

        '''
        # Create frame
        f = ttk.Frame(window, padding=(12, 5, 12, 0))
        f.grid(column=col, columnspan=2, row=row,
               rowspan=4, sticky=(N, W, E, S))
        f.configure(borderwidth=5, relief='raised')

        # Label the frame
        ds_label = Label(f, text="Endurance Test Parameters")
        ds_label.configure(font=("Arial", 28))
        ds_label.grid(column=0, columnspan=8, row=0)

        # Create and place widgets for device selection
        device_buttons = []
        for c in range(self._grid_size):
            row = []
            for r in range(self._grid_size):
                button = Button(f, text=0, bg="light gray",
                                activebackground="gray90", width=2, height=2)
                button.grid(row=r+1, column=c, sticky=NW+NE+SW+SE+N+S+E+W)
                row.append(button)
            device_buttons.append(row)

        def change_device_grid_value(r, c):
            if self._devices_grid[r][c] == 1:
                self._devices_grid[r][c] = 0
                device_buttons[r][c].config(
                    text="0", bg="light gray", activebackground="gray90")
                return
            self._devices_grid[r][c] = 1
            device_buttons[r][c].config(
                text="1", bg="deep sky blue", activebackground="light sky blue")

        for row in range(self._grid_size):
            for col in range(self._grid_size):
                device_buttons[row][col].config(
                    command=lambda row=row, col=col: change_device_grid_value(row, col))

        # Select row buttons
        row_buttons = []
        for r in range(self._grid_size):
            button = Button(f, text="Select Row")
            button.grid(row=r+1, column=8, sticky=NW+NE+SW+SE+N+S+E+W)
            row_buttons.append(button)

        def select_row(r):
            if row_buttons[r]["text"] == "Select Row":
                row_buttons[r]["text"] = "Deselect Row"
                for c in range(self._grid_size):
                    self._devices_grid[c][r] = 1
                    device_buttons[c][r].config(
                        text="1", bg="deep sky blue", activebackground="light sky blue")
            else:
                row_buttons[r]["text"] = "Select Row"
                for c in range(self._grid_size):
                    self._devices_grid[c][r] = 0
                    device_buttons[c][r].config(
                        text="0", bg="light gray", activebackground="gray90")

        for row in range(len(row_buttons)):
            row_buttons[row].config(command=lambda row=row: select_row(row))

        # Select column buttons
        col_buttons = []
        for c in range(self._grid_size):
            button = Button(f, text="Select\nColumn")
            button.grid(row=9, column=c, sticky=NW+NE+SW+SE+N+S+E+W)
            col_buttons.append(button)

        def select_col(c):
            if col_buttons[c]["text"] == "Select\nColumn":
                col_buttons[c]["text"] = "Deselect\nColumn"
                for r in range(self._grid_size):
                    self._devices_grid[c][r] = 1
                    device_buttons[c][r].config(
                        text="1", bg="deep sky blue", activebackground="light sky blue")
            else:
                col_buttons[c]["text"] = "Select\nColumn"
                for r in range(self._grid_size):
                    self._devices_grid[c][r] = 0
                    device_buttons[c][r].config(
                        text="0", bg="light gray", activebackground="gray90")

        for col in range(len(col_buttons)):
            col_buttons[col].config(command=lambda col=col: select_col(col))

        # Select all button
        select_all_button = Button(f, text="Select All")
        select_all_button.grid(column=8, row=9)

        def select_all():
            if select_all_button["text"] == "Select All":
                select_all_button["text"] = "Deselect All"
                for c in range(self._grid_size):
                    for r in range(self._grid_size):
                        self._devices_grid[c][r] = 1
                        device_buttons[c][r].config(
                            text="1", bg="deep sky blue", activebackground="light sky blue")
            else:
                select_all_button["text"] = "Select All"
                for c in range(self._grid_size):
                    for r in range(self._grid_size):
                        self._devices_grid[c][r] = 0
                        device_buttons[c][r].config(
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
                x = self._root.winfo_x()
                y = self._root.winfo_y()
                window.geometry("+%d+%d" % (x + 600, y + 400))
                # Populate window
                label1 = Label(window, text="Enter preset name:")
                label1.grid(column=0, row=0)
                preset_entry = Entry(window, textvariable=preset)
                preset_entry.grid(column=0, row=1)
                label2 = Label(window, text="When finished, exit the window.")
                label2.grid(column=0, row=2)
                label3 = Label(
                    window, text="Note: You can rewrite an old preset by\nassigning a new preset the same name")
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
                df = pd.DataFrame(self._devices_grid)
                df.to_csv(f"DevicePresets/{preset_name}.csv",
                          header=False, index=False)
                # Update list of presets on main window
                update_preset_list()

        def load_preset():
            '''
            Read from csv file of selected preset and update current grid config to match
            '''
            preset_name = selected_preset.get()
            df = pd.read_csv(
                f"DevicePresets/{preset_name}.csv", header=None, index_col=None)
            for c in range(self._grid_size):
                for r in range(self._grid_size):
                    if df[r][c] == 1:
                        self._devices_grid[c][r] = 1
                        device_buttons[c][r].config(
                            text="1", bg="deep sky blue", activebackground="light sky blue")
                    else:
                        self._devices_grid[c][r] = 0
                        device_buttons[c][r].config(
                            text="0", bg="light gray", activebackground="gray90")

        save_preset_button = Button(
            f, text="save preset", command=store_preset)
        save_preset_button.grid(column=9, row=3)

        selected_preset = StringVar()
        presets = ttk.Combobox(f, width=27, textvariable=selected_preset)
        presets.grid(column=9, row=1)

        # Create a list of files in DevicePresets folder

        def update_preset_list():
            preset_list = os.listdir("DevicePresets/")
            for i in range(len(preset_list)):
                preset_list[i] = preset_list[i][0:-4]
            return preset_list

        # Adding list to presets combobox
        presets['values'] = update_preset_list()

        load_preset_button = Button(
            f, text="load preset", command=lambda: load_preset())
        load_preset_button.grid(column=9, row=5)

        # Try to load most recent grid layout
        try:
            df = pd.read_csv(
                f"device_grid_last_vals.csv", header=None, index_col=None)
            for c in range(self._grid_size):
                for r in range(self._grid_size):
                    if df[r][c] == 1:
                        self._devices_grid[c][r] = 1
                        device_buttons[c][r].config(
                            text="1", bg="deep sky blue", activebackground="light sky blue")
                    else:
                        self._devices_grid[c][r] = 0
                        device_buttons[c][r].config(
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
            x = self._root.winfo_x()
            y = self._root.winfo_y()
            window.geometry("+%d+%d" % (x + 50, y + 50))

            # Populate window with IVTest options
            self.iv_frame_create(window)

            # Wait to do anything else until popup window is closed
            self._root.wait_window(window)
            # Make new IVTest object
            iv = tests.IVTest(
                grid=self._devices_grid,
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
                is_up_down=self._iv_is_up_down.get()
            )

            test_lb.insert(END, "IV Test")
            self._tests_requested.append(iv)

        def add_et(*args):
            '''

            '''
            # Create new window
            window = Toplevel()
            # Ensure window always shows up in the same space
            x = self._root.winfo_x()
            y = self._root.winfo_y()
            window.geometry(f"+{x+50}+{y+50}")

            # Populate window with IVTest options
            self.et_frame_create(window)

            # Wait to do anything else until popup window is closed
            self._root.wait_window(window)
            # Make new EnduranceTest object
            et = tests.EnduranceTest(
                grid=self._devices_grid,
                chiplet_name=self._chiplet_name.get(),
                source_voltage=self._et_source_voltage.get(),
                source_delay=self._et_source_delay.get(),
                current_compliance=self._et_current_compliance.get(),
                cycles=self._et_cycles.get(),
                set_voltage=self._et_set_voltage.get(),
                read_voltage=self._et_read_voltage.get(),
                reset_voltage=self._et_reset_voltage.get()
            )

            test_lb.insert(END, "Endurance Test")
            self._tests_requested.append(et)

        def add_set(*args):
            '''
            '''
            test_lb.insert(END, "Set")
            self._tests_requested.append("Set")

        def add_reset(*args):
            '''
            '''
            test_lb.insert(END, "Reset")
            self._tests_requested.append("Reset")

        def clear_lb(*args):
            test_lb.delete(0, END)
            self._tests_requested = []

        # Chip name box
        t = ttk.Frame(self._root, padding=(12, 5, 12, 0))
        t.grid(column=4, columnspan=2, row=0, rowspan=4, sticky=(N, W, E, S))
        t.configure(borderwidth=5, relief='raised')
        chiplet_name_label = Label(t, text="Chiplet Name/Identifier:")
        chiplet_name_entry = Entry(t, textvariable=chiplet_name)
        chiplet_name_label.grid(column=0, row=0, pady=15)
        chiplet_name_entry.grid(column=0, row=1, pady=15)

        # Device grid box
        self.device_select_frame_create(self._root, col=0, row=0)

        # Test queue box
        f = ttk.Frame(self._root, padding=(12, 5, 12, 0))
        f.grid(column=2, columnspan=2, row=0, rowspan=4, sticky=(N, W, E, S))
        f.configure(borderwidth=5, relief='raised')
        test_lb = Listbox(f, selectmode="BROWSE")
        test_lb_label = Label(f, text="Test Queue:")
        add_set_button = Button(f, text="Set", command=add_set)
        add_reset_button = Button(f, text="Reset", command=add_reset)
        add_iv_button = Button(f, text="Add IV Test", command=add_iv)
        add_et_button = Button(f, text="Add Endurance Test", command=add_et)
        clear_lb_button = Button(f, text="Clear Test Queue", command=clear_lb)

        test_lb_label.grid(column=1, columnspan=2, row=0)
        test_lb.grid(column=1, columnspan=2, row=1, rowspan=4)
        clear_lb_button.grid(column=1, columnspan=2, row=5, rowspan=1)
        add_iv_button.grid(column=0, columnspan=1, row=1, rowspan=1)
        add_et_button.grid(column=0, columnspan=1, row=2, rowspan=1)
        add_set_button.grid(column=0, columnspan=1, row=3, rowspan=1)
        add_reset_button.grid(column=0, columnspan=1, row=4, rowspan=1)

        # Run button
        button = Button(self._root, text="Run",
                        command=self.set_values, width=25, height=3, background="red", activebackground="tomato")
        button.grid(column=4, columnspan=2, row=4, rowspan=2, padx=0)

    def define_progress_interval(self):
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
        df = pd.DataFrame(self._devices_grid)
        df.to_csv("device_grid_last_vals.csv", header=False, index=False)

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


gui = GUI()
gui.gui_start()
