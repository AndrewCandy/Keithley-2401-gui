from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import json
import re
import os
import pandas as pd
import tests

# TODO: create high and low accuracy modes for IV
# TODO: Add multiple device functionality (GUI done)
# TODO: Add test scheduling/cueing
# TODO: Add Endurance test functionality
# TODO: Add output graph select window

# Create a class to contain the tkinter window


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
        # self._fp_voltage = DoubleVar(self._root)
        # self._fp_delay = DoubleVar(self._root)
        # self._fp_num_steps = IntVar(self._root)
        # self._fp_current_compliance = DoubleVar(self._root)
        # self._fp_period = DoubleVar(self._root)
        # self._fp_rise_time = DoubleVar(self._root)
        # self._fp_fall_time = DoubleVar(self._root)
        # self._fp_forming_iv = BooleanVar(self._root)
        # self._gen_device_x = IntVar(self._root)
        # self._gen_device_y = IntVar(self._root)
        self._chiplet_name = StringVar(self._root)
        # self._gen_test_choice = StringVar(self._root)

        # create a grid for storing the positions of selected devices
        self._grid_size = 8
        self._devices_grid = []
        for i in range(self._grid_size):
            row = [0] * self._grid_size
            self._devices_grid.append(row)

        # Variable to check if new tests were requested or if window was closed another way
        self._tests_requested = []

        # Run functions to generate GUI
        # self.iv_frame_create()
        # self.fp_frame_create()
        # self.et_frame_create()
        self.device_select_frame_create(self._root)
        self.gui_common_params()

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
        source_voltage_minmax = [0.0, 3.5]
        source_delay = self._iv_source_delay
        source_delay_minmax = [0.0, .25]
        source_voltage_start = self._iv_source_voltage_start
        source_voltage_stop = self._iv_source_voltage_stop
        # When in LOG sweep space, num steps is used instead of voltage step
        num_steps = self._iv_num_steps
        num_steps_minmax = [1, 100]
        current_compliance = self._iv_current_compliance
        current_minmax = [0.0, 1.0]
        is_up_down = self._iv_is_up_down
        accuracy = self._iv_accuracy
        rangename = self._iv_range
        modename = self._iv_mode
        spacename = self._iv_space

        # Create frame structure to place widgets in for IV Test
        c = ttk.Frame(window, padding=(12, 5, 12, 0))
        c.grid(column=0, row=0, sticky=(N, W, E, S))
        c.configure(borderwidth=5, relief='raised')

        # Create option lists for non-numeric inputs
        sweep_range_label = Label(c, text='Sweep Range:')
        sr_choice_1 = Radiobutton(c, text="BEST", variable=rangename,
                                  value="BEST")
        # sr_choice_2 = Radiobutton(self._root, text="Forming Pulse", variable=test_choice,
        #                            value="Forming Pulse", command=select_test)
        voltage_mode_label = Label(c, text='Voltage Mode:')
        vm_choice_1 = Radiobutton(c, text="SWE", variable=modename,
                                  value="SWE")
        # vm_choice_2 = Radiobutton(self._root, text="Forming Pulse", variable=test_choice,
        #                            value="Forming Pulse", command=select_test)
        sweep_space_label = Label(c, text='Sweep Space:')
        ss_choice_1 = Radiobutton(c, text="Linear", variable=spacename,
                                  value="LIN")
        ss_choice_2 = Radiobutton(c, text="Logarithmic", variable=spacename,
                                  value="LOG")

        # Set starting values based on previous set values
        def ivGetStartValues():
            try:  # Open JSON file if one exists, otherwise tell user no previous data available
                with open('values.json', 'r') as openfile:
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

        ivGetStartValues()

        '''
        Functions to ensure no invalid data is sent from the GUI
        an attempt at minimizing opportunities to fry our chiplets
        '''
        def checkSourceVoltage(*args):
            sv = source_voltage.get()
            if sv > source_voltage_minmax[1]:
                source_voltage.set(source_voltage_minmax[1])
            elif sv < source_voltage_minmax[0]:
                source_voltage.set(source_voltage_minmax[0])
            elif (spacename == 'LOG' and sv == source_voltage_minmax[0]):
                source_voltage.set(source_voltage_minmax[0] + 0.00001)

        def checkSourceDelay(*args):
            sd = source_delay.get()
            if sd > source_delay_minmax[1]:
                source_delay.set(source_delay_minmax[1])
            elif sd <= source_delay_minmax[0]:
                source_delay.set(source_delay_minmax[0])

        def checkVoltageStart(*args):
            svs = source_voltage_start.get()
            if svs > source_voltage_minmax[1]:
                source_voltage_start.set(source_voltage_minmax[1])
            elif svs < source_voltage_minmax[0]:
                source_voltage_start.set(source_voltage_minmax[0])
            elif (spacename == 'LOG' and svs == source_voltage_minmax[0]):
                source_voltage_start.set(source_voltage_minmax[0] + 0.00001)

        def checkVoltageStop(*args):
            svs = source_voltage_stop.get()
            if svs > source_voltage_minmax[1]:
                source_voltage_stop.set(source_voltage_minmax[1])
            elif svs < source_voltage_minmax[0]:
                source_voltage_stop.set(source_voltage_minmax[0])
            elif (spacename == 'LOG' and svs == source_voltage_minmax[0]):
                source_voltage_stop.set(source_voltage_minmax[0] + 0.00001)

        def checkNumSteps(*args):
            ns = num_steps.get()
            if ns > num_steps_minmax[1]:
                num_steps.set(num_steps_minmax[1])
            elif ns < num_steps_minmax[0]:
                num_steps.set(num_steps_minmax[0])

        def checkCurrent(*args):
            cc = current_compliance.get()
            if cc > current_minmax[1]:
                current_compliance.set(current_minmax[1])
            elif cc < current_minmax[0]:
                current_compliance.set(current_minmax[0])
            elif (spacename == 'LOG' and cc == current_minmax[0]):
                current_compliance.set(current_minmax[0] + 0.00001)

        # call value check functions whenever a value in the GUI changes
        # source_voltage.trace_add('write', checkSourceVoltage)
        # source_delay.trace_add('write', checkSourceDelay)
        # source_voltage_start.trace_add('write', checkVoltageStart) # Turns out this is really annoying for entering values into the gui
        # source_voltage_stop.trace_add('write', checkVoltageStop)
        # num_steps.trace_add('write', checkNumSteps)
        # current_compliance.trace_add('write', checkCurrent)

        # Label the frame
        iv_test_label = Label(c, text="IV Test Parameters")
        iv_test_label.configure(font=("Arial", 28))

        # Create sliders and text entry points for numeric inputs
        src_voltage_label = Label(c, text='Source Voltage:')
        src_voltage_scale = Scale(c, variable=source_voltage, orient="horizontal",
                                  from_=source_voltage_minmax[0], to=source_voltage_minmax[1], resolution=0.1, showvalue=0,
                                  tickinterval=(source_voltage_minmax[1]-source_voltage_minmax[0]), command=checkSourceVoltage)
        src_voltage_entry = Entry(c, textvariable=source_voltage)

        src_delay_label = Label(c, text='Source delay:')
        src_delay_scale = Scale(c, variable=source_delay, orient="horizontal",
                                from_=source_delay_minmax[0], to=source_delay_minmax[1], resolution=0.01, showvalue=0,
                                tickinterval=(source_delay_minmax[1]-source_delay_minmax[0]), command=checkSourceDelay)
        src_delay_entry = Entry(c, textvariable=source_delay)

        src_voltage_start_label = Label(c, text='Source Voltage Start:')
        src_voltage_start_scale = Scale(c, variable=source_voltage_start, orient="horizontal",
                                        from_=source_voltage_minmax[0], to=source_voltage_minmax[1], resolution=0.1, showvalue=0,
                                        tickinterval=(source_voltage_minmax[1]-source_voltage_minmax[0]), command=checkVoltageStart)
        src_voltage_start_entry = Entry(c, textvariable=source_voltage_start)

        src_voltage_stop_label = Label(c, text='Source Voltage Stop:')
        src_voltage_stop_scale = Scale(c, variable=source_voltage_stop, orient="horizontal",
                                       from_=source_voltage_minmax[0], to=source_voltage_minmax[1], resolution=0.1, showvalue=0,
                                       tickinterval=(source_voltage_minmax[1]-source_voltage_minmax[0]), command=checkVoltageStop)
        src_voltage_stop_entry = Entry(c, textvariable=source_voltage_stop)

        num_steps_label = Label(c, text='Number of Steps:')
        num_steps_scale = Scale(c, variable=num_steps, orient="horizontal",
                                from_=num_steps_minmax[0], to=num_steps_minmax[1], resolution=1, showvalue=0,
                                tickinterval=(num_steps_minmax[1]-num_steps_minmax[0]), command=checkNumSteps)
        num_steps_entry = Entry(c, textvariable=num_steps)

        accuracy_label = Label(c, text='Number of Steps:')
        accuracy_scale = Scale(c, variable=num_steps, orient="horizontal",
                               from_=0.01, to=10, resolution=.01, showvalue=0, tickinterval=.01)
        accuracy_entry = Entry(c, textvariable=num_steps)

        current_compliance_label = Label(c, text='Current Compliance:')
        current_compliance_scale = Scale(c, variable=current_compliance, orient="horizontal",
                                         from_=current_minmax[0], to=current_minmax[1], resolution=0.00001, showvalue=0,
                                         tickinterval=(current_minmax[1]-current_minmax[0]), command=checkCurrent)
        current_compliance_entry = Entry(c, textvariable=current_compliance)

        stairs_button_label = Label(c, text="Stairs up and down?")
        stairs_button = Checkbutton(c, variable=is_up_down, width=20)

        # Place items in frame for IV test
        def ivGridAssign():
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

        ivGridAssign()

        # def sweepSpaceChange(*args):
        #     if spacename == 'LOG':
        #         src_voltage_step_entry.grid_forget()
        #         src_voltage_step_label.grid_forget()
        #         src_voltage_step_scale.grid_forget()

        #     else:
        #         log_num_steps_entry.grid_forget()
        #         log_num_steps_label.grid_forget()
        #         log_num_steps_scale.grid_forget()
        #         src_voltage_step_label.grid(
        #             column=2, columnspan=1, row=7, padx=10)
        #         src_voltage_step_entry.grid(
        #             column=2, columnspan=1, row=8, padx=10)
        #         src_voltage_step_scale.grid(
        #             column=2, columnspan=1, row=9, padx=10)

        # # Trigger a function every time sweep space choice is changed
        # spacename.trace_add("write", callback=sweepSpaceChange)

        # # Run once to populate blank spaces if possible
        # sweepSpaceChange()

    # def fp_frame_create(self):
    #     # Define variables
    #     voltage = self._fp_voltage
    #     voltage_minmax = [0.0, 5.0]
    #     delay = self._fp_delay
    #     delay_minmax = [0.0, .25]
    #     num_steps = self._fp_num_steps
    #     num_steps_minmax = [1, 1000]
    #     current_compliance = self._fp_current_compliance
    #     current_minmax = [0.0, .01]
    #     period = self._fp_period
    #     period_minmax = [0.0, 1.0]
    #     rise_time = self._fp_rise_time
    #     fall_time = self._fp_fall_time
    #     rise_fall_minmax = [0.0, 1.0]
    #     forming_iv = self._fp_forming_iv

    #     # Set starting values based on previous set values
    #     def fpGetStartValues():
    #         try: # Open JSON file if one exists, otherwise tell user no previous data available
    #             with open('values.json', 'r') as openfile:
    #                 saved_vals = json.load(openfile)

    #             # Take previous values from JSON file and give everything a starting value
    #             voltage.set(saved_vals["fp_voltage"])
    #             delay.set(saved_vals["fp_delay"])
    #             num_steps.set(saved_vals["fp_num_steps"]) # If an IV is wanted, we need to know how much data to collect
    #             period.set(saved_vals["fp_period"])
    #             rise_time.set(saved_vals["fp_rise_time"])
    #             fall_time.set(saved_vals["fp_fall_time"])
    #             forming_iv.set(saved_vals["fp_forming_iv"])
    #             current_compliance.set(saved_vals["fp_current_compliance"])
    #         except:
    #             print("Previous values not available, no JSON file found.")

    #     fpGetStartValues()

    #     # Created frame for Forming pulse
    #     f = ttk.Frame(self._root, padding=(12, 5, 12, 0))
    #     f.grid(column=0, row=2, sticky=(N,W,E,S))
    #     f.configure(borderwidth=5, relief='raised')

    #     #Label the frame
    #     fp_test_label = Label(f, text="Forming Pulse Parameters")
    #     fp_test_label.configure(font =("Arial", 28))

    #     # Create Widgets for inputs

    #     voltage_label = Label(f, text='Voltage:')
    #     voltage_scale = Scale(f, variable=voltage, orient="horizontal",
    #                           from_=voltage_minmax[0], to=voltage_minmax[1], resolution=1, showvalue=0,
    #                           tickinterval=(voltage_minmax[1]-voltage_minmax[0]))
    #     voltage_entry = Entry(f, textvariable=voltage)

    #     num_steps_label = Label(f, text='Number of Steps:')
    #     num_steps_scale = Scale(f, variable=num_steps, orient="horizontal",
    #                           from_=num_steps_minmax[0], to=num_steps_minmax[1], resolution=1, showvalue=0,
    #                           tickinterval=(num_steps_minmax[1]-num_steps_minmax[0]))
    #     num_steps_entry = Entry(f, textvariable=num_steps)

    #     delay_label = Label(f, text='Delay:')
    #     delay_scale = Scale(f, variable=delay, orient="horizontal",
    #                           from_=delay_minmax[0], to=delay_minmax[1], resolution=1, showvalue=0,
    #                           tickinterval=(delay_minmax[1]-delay_minmax[0]))
    #     delay_entry = Entry(f, textvariable=delay)

    #     period_label = Label(f, text='Period:')
    #     period_scale = Scale(f, variable=period, orient="horizontal",
    #                           from_=period_minmax[0], to=period_minmax[1], resolution=1, showvalue=0,
    #                           tickinterval=(period_minmax[1]-period_minmax[0]))
    #     period_entry = Entry(f, textvariable=period)

    #     rise_time_label = Label(f, text='Rise Time:')
    #     rise_time_scale = Scale(f, variable=rise_time, orient="horizontal",
    #                           from_=rise_fall_minmax[0], to=rise_fall_minmax[1], resolution=1, showvalue=0,
    #                           tickinterval=(rise_fall_minmax[1]-rise_fall_minmax[0]))
    #     rise_time_entry = Entry(f, textvariable=rise_time)

    #     fall_time_label = Label(f, text='Fall Time:')
    #     fall_time_scale = Scale(f, variable=fall_time, orient="horizontal",
    #                           from_=rise_fall_minmax[0], to=rise_fall_minmax[1], resolution=1, showvalue=0,
    #                           tickinterval=(rise_fall_minmax[1]-rise_fall_minmax[0]))
    #     fall_time_entry = Entry(f, textvariable=fall_time)

    #     current_label = Label(f, text='Current Compliance:')
    #     current_scale = Scale(f, variable=current_compliance, orient="horizontal",
    #                           from_=current_minmax[0], to=current_minmax[1], resolution=0.001, showvalue=0,
    #                           tickinterval=(current_minmax[1]-current_minmax[0]))
    #     current_entry = Entry(f, textvariable=current_compliance)

    #     #Place items in Frame for Forming pulse
    #     def fpGridAssign():
    #         fp_test_label.grid(column=0,columnspan=5, row=0)

    #         voltage_label.grid(column=0, columnspan=1, row=1)
    #         voltage_entry.grid(column=0, columnspan=1, row=2)
    #         voltage_scale.grid(column=0, columnspan=1, row=3)

    #         num_steps_label.grid(column=1, columnspan=1, row=1)
    #         num_steps_scale.grid(column=1, columnspan=1, row=3)
    #         num_steps_entry.grid(column=1, columnspan=1, row=2)

    #         delay_label.grid(column=0, columnspan=1, row=4)
    #         delay_scale.grid(column=0, columnspan=1, row=6)
    #         delay_entry.grid(column=0, columnspan=1, row=5)

    #         period_label.grid(column=1, columnspan=1, row=4)
    #         period_scale.grid(column=1, columnspan=1, row=6)
    #         period_entry.grid(column=1, columnspan=1, row=5)

    #         rise_time_label.grid(column=2, columnspan=1, row=4)
    #         rise_time_scale.grid(column=2, columnspan=1, row=6)
    #         rise_time_entry.grid(column=2, columnspan=1, row=5)

    #         fall_time_label.grid(column=3, columnspan=1, row=4)
    #         fall_time_scale.grid(column=3, columnspan=1, row=6)
    #         fall_time_entry.grid(column=3, columnspan=1, row=5)

    #         current_label.grid(column=2, columnspan=1, row=1)
    #         current_scale.grid(column=2, columnspan=1, row=3)
    #         current_entry.grid(column=2, columnspan=1, row=2)

    #     fpGridAssign()

    def et_frame_create(self, window):
        '''
        Create and populate endurance test frame of GUI

        '''
        # Created frame for Endurance Test
        t = ttk.Frame(window, padding=(12, 5, 12, 0))
        t.grid(column=0, row=2, sticky=(N, W, E, S))
        t.configure(borderwidth=5, relief='raised')

        # Label the frame
        et_test_label = Label(t, text="Endurance Test Parameters")
        et_test_label.configure(font=("Arial", 28))

        # Create Widgets for inputs

        # Place items in Frame for Forming pulse

        def etGridAssign():
            et_test_label.grid(column=0, columnspan=5, row=0)
        etGridAssign()

    def device_select_frame_create(self, window):
        '''
        Create and populate device selector frame of GUI

        '''
        # Create frame
        f = ttk.Frame(window, padding=(12, 5, 12, 0))
        f.grid(column=0, columnspan=2, row=4, rowspan=4, sticky=(N, W, E, S))
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
                                activebackground="gray90")
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

        for row in range(len(device_buttons)):
            for col in range(len(device_buttons[row])):
                device_buttons[row][col].config(
                    command=lambda row=row, col=col: change_device_grid_value(row, col))

        # Select row buttons
        row_buttons = []
        for r in range(self._grid_size):
            button = Button(f, text="Select Row")
            button.grid(row=r+1, column=8, sticky=NW+NE+SW+SE+N+S+E+W)
            row_buttons.append(button)

        def select_row(r):
            for c in range(self._grid_size):
                self._devices_grid[c][r] = 1
                device_buttons[c][r].config(
                    text="1", bg="deep sky blue", activebackground="light sky blue")

        for row in range(len(row_buttons)):
            row_buttons[row].config(command=lambda row=row: select_row(row))

        # Select column buttons
        col_buttons = []
        for c in range(self._grid_size):
            button = Button(f, text="Select\nColumn")
            button.grid(row=9, column=c, sticky=NW+NE+SW+SE+N+S+E+W)
            col_buttons.append(button)

        def select_col(c):
            for r in range(self._grid_size):
                self._devices_grid[c][r] = 1
                device_buttons[c][r].config(
                    text="1", bg="deep sky blue", activebackground="light sky blue")

        for col in range(len(col_buttons)):
            col_buttons[col].config(command=lambda col=col: select_col(col))

        # Select all button
        def select_all():
            for c in range(self._grid_size):
                for r in range(self._grid_size):
                    self._devices_grid[c][r] = 1
                    device_buttons[c][r].config(
                        text="1", bg="deep sky blue", activebackground="light sky blue")

        select_all_button = Button(f, text="Select All", command=select_all)
        select_all_button.grid(column=8, row=9)

        def store_preset():
            '''
            Runs when save preset button is pushed
            takes current grid config and saves it to csv
            Prompts user for preset name in popup window
            '''
            # Create new window
            window = Toplevel()
            # Ensure window always shows up in the same space
            x = self._root.winfo_x()
            y = self._root.winfo_y()
            window.geometry("230x120+%d+%d" % (x + 600, y + 400))
            # Populate window
            label1 = Label(window, text="Enter preset name:")
            label1.grid(column=0, row=0)
            preset = StringVar()
            preset_entry = Entry(window, textvariable=preset)
            preset_entry.grid(column=0, row=1)
            label2 = Label(window, text="When finished, exit the window.")
            label2.grid(column=0, row=2)
            label3 = Label(
                window, text="Note: You can rewrite an old preset by\nassigning a new preset the same name")
            label3.grid(column=0, row=4, pady=15)

            # Wait to do anything else until popup window is closed
            self._root.wait_window(window)
            preset_name = preset.get()
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

    def gui_common_params(self):
        '''
        Creates elements of the GUI for inputs common across all three testing functions
        '''
        # Define variables
        device_x = self._gen_device_x
        device_y = self._gen_device_y
        device_coord_minmax = [0, 7]  # Could change in the future
        chiplet_name = self._gen_chiplet_name
        test_choice = self._gen_test_choice
        button_text = StringVar(self._root)

        def GetStartValues():
            try:  # Open JSON file if one exists, otherwise tell user no previous data available
                with open('values.json', 'r') as openfile:
                    saved_vals = json.load(openfile)

                # Take previous values from JSON file and give everything a starting value
                device_x.set(saved_vals["gen_device_x"])
                device_y.set(saved_vals["gen_device_y"])
                chiplet_name.set(saved_vals["gen_chiplet_name"])
                test_choice.set(saved_vals["gen_test_choice"])
            except:
                print("Previous values not available, no JSON file found.")

        GetStartValues()

        '''
        Functions to ensure no invalid data is sent from the GUI
        an attempt at minimizing opportunities to fry our chiplets
        '''

        def checkDeviceX(*args):
            x = device_x.get()
            if x > device_coord_minmax[1]:
                device_x.set(device_coord_minmax[1])
            elif x < device_coord_minmax[0]:
                device_x.set(device_coord_minmax[0])

        def checkDeviceY(*args):
            y = device_y.get()
            if y > device_coord_minmax[1]:
                device_y.set(device_coord_minmax[1])
            elif y < device_coord_minmax[0]:
                device_y.set(device_coord_minmax[0])

        def checkChipletName(*args):
            if re.search("[^a-zA-Z0-9s]", chiplet_name.get()):
                messagebox.showwarning(
                    "Warning!", "Chiplet name is invalid, please do not include any special characters")

        # call value check functions whenever a value in the GUI changes
        device_x.trace_add('write', checkDeviceX)
        device_y.trace_add('write', checkDeviceY)
        chiplet_name.trace_add('write', checkChipletName)

        # Universal parameters
        chiplet_name_label = Label(self._root, text="Chiplet Name/Identifier:")
        chiplet_name_entry = Entry(self._root, textvariable=chiplet_name)

        device_xy_label = Label(self._root, text="X and Y device coords:")
        device_x_entry = Entry(self._root, textvariable=device_x)
        device_y_entry = Entry(self._root, textvariable=device_y)

        test_lb = Listbox(self._root, selectmode="BROWSE")

        def add_iv(*args):
            '''

            '''
            # Create new window
            window = Toplevel()
            # Ensure window always shows up in the same space
            x = self._root.winfo_x()
            y = self._root.winfo_y()
            window.geometry("600x400+%d+%d" % (x + 600, y + 400))

            # Populate window with IVTest options
            self.iv_frame_create(window)

            # Wait to do anything else until popup window is closed
            self._root.wait_window(window)
            # Make new IVTest object
            iv = tests.IVTest(
                grid=self._devices_grid.get(),
                chiplet_name=self._gen_chiplet_name.get(),
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

        # def add_fp(*args):
        #     test_lb.insert(END, "Python")
        def add_et(*args):

            test_lb.insert(END, "Endurance Test")
            self._tests_requested.append("Endurance Test")

        def clear_lb(*args):
            test_lb.delete(0, END)
            self._tests_requested = []

        add_iv_button = Button(self._root, text="Add IV Test", command=add_iv)
        # add_fp_button = Button(self._root, text="Add Forming Pulse", command=add_fp)
        add_et_button = Button(
            self._root, text="Add Endurance Test", command=add_et)
        clear_lb_button = Button(
            self._root, text="Clear Test Queue", command=clear_lb)

        # def select_test(*args):
        #     '''
        #     Sets the text on the run button to specify the selected test
        #     '''
        #     button_text.set("Run " + test_choice.get())

        # test_choice_1 = Radiobutton(self._root, text="IV Test", variable=test_choice,
        #                             value="IV Test", command=select_test)
        # # test_choice_2 = Radiobutton(self._root, text="Forming Pulse", variable=test_choice,
        # #                             value="Forming Pulse", command=select_test)
        # test_choice_3 = Radiobutton(self._root, text="Endurance Test", variable=test_choice,
        #                             value="Endurance Test", command=select_test)

        # # Run once to populate blank spaces if possible
        # select_test()

        button = Button(self._root, textvariable=button_text,
                        command=self.set_values)

        # Universal parameters

        test_lb.grid(column=7, columnspan=2, row=0, rowspan=3)
        clear_lb_button.grid(column=7, columnspan=2, row=2, rowspan=1)
        add_iv_button.grid(column=6, columnspan=1, row=0, rowspan=1)
        # add_fp_button.grid(column=6, columnspan=1, row=2, rowspan=1)
        add_et_button.grid(column=6, columnspan=1, row=4, rowspan=1)

        chiplet_name_label.grid(column=7, row=4)
        chiplet_name_entry.grid(column=8, row=4)

        device_xy_label.grid(column=6, row=5)
        device_x_entry.grid(column=7, row=5)
        device_y_entry.grid(column=8, row=5)

        test_choice_1.grid(column=6, row=7)
        # test_choice_2.grid(column=7, row=7)
        test_choice_3.grid(column=8, row=7)

        button.grid(column=6, columnspan=3, row=9)

    def set_values(self):
        '''
        Run whenever run button on GUI is pressed
        Reads all values from GUI, saves all values to json file if filled out
        or informs user information is missing
        '''
        dictionary = {
            # Generics
            # "gen_device_x" : self._gen_device_x.get(),
            # "gen_device_y" : self._gen_device_y.get(),
            "chiplet_name": self._chiplet_name.get(),
            # "gen_test_choice" : self._gen_test_choice.get(),
            # "test_start_time" : datetime.now().strftime("%m-%d-%Y_%H-%M-%S"),
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
            # FP vals
            # "fp_voltage" : self._fp_voltage.get(),
            # "fp_delay" : self._fp_delay.get(),
            # "fp_num_steps" : self._fp_num_steps.get(),
            # "fp_current_compliance" : self._fp_current_compliance.get(),
            # "fp_period" : self._fp_period.get(),
            # "fp_rise_time" : self._fp_rise_time.get(),
            # "fp_fall_time" : self._fp_fall_time.get(),
            # "fp_forming_iv" : self._fp_forming_iv.get(),
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

        self._root.destroy()

    def requested_tests(self):
        '''
        Returns a list of tests in order to be conducted
        '''
        return self._tests_requested


gui = GUI()
gui.gui_start()
