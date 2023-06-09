from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime
import json
import re

#TODO: create high and low accuracy modes for IV 
#TODO: Automate trigger count calculation
#TODO: Add multiple device functionality
#TODO: Add test scheduling/cueing
#TODO: Add Forming pulse functionality
#TODO: Add Endurance test functionality

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
        self._root.title("Keithley 2401 GUI") # Title the window
        self._root.grid_columnconfigure(0, weight=1) # Config rows and cols
        self._root.grid_rowconfigure(0,weight=1)
        # Define all exported variables
        self._iv_range = StringVar(self._root)
        self._iv_mode = StringVar(self._root)
        self._iv_space = StringVar(self._root)
        self._iv_source_voltage = DoubleVar(self._root)
        self._iv_source_delay = DoubleVar(self._root)
        self._iv_source_voltage_start = DoubleVar(self._root)
        self._iv_source_voltage_stop = DoubleVar(self._root)
        self._iv_source_voltage_step = DoubleVar(self._root)
        self._iv_log_num_steps = IntVar(self._root)
        self._iv_trig_count = IntVar(self._root)
        self._iv_current_compliance = DoubleVar(self._root)
        self._iv_is_up_down = BooleanVar(self._root)
        self._fp_voltage = DoubleVar(self._root)
        self._fp_delay = DoubleVar(self._root)
        self._fp_voltage_step = DoubleVar(self._root)
        self._fp_current_compliance = DoubleVar(self._root)
        self._fp_period = DoubleVar(self._root)
        self._fp_rise_time = DoubleVar(self._root)
        self._fp_fall_time = DoubleVar(self._root)
        self._fp_forming_iv = BooleanVar(self._root)
        self._gen_device_x = IntVar(self._root)
        self._gen_device_y = IntVar(self._root)
        self._gen_chiplet_name = StringVar(self._root)
        self._gen_test_choice = StringVar(self._root)

        # Variable to check if new tests were requested or if window was closed another way
        self._testRequested = []

        # Run functions to generate GUI
        self.iv_frame_create()
        self.fp_frame_create()
        self.et_frame_create()
        self.gui_common_params()
    
    def gui_start(self):
        self._root.mainloop()
        
    def iv_frame_create(self):
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
        source_voltage_step = self._iv_source_voltage_step # When in LIN sweep space, step size is used
        voltage_step_minmax = [0.0, 1.0]
        log_num_steps = self._iv_log_num_steps # When in LOG sweep space, num steps is used instead of voltage step
        num_steps_minmax = [1, 100]
        trig_count = self._iv_trig_count # Trigger count (must be set based on other values)
        trig_count_minmax = [1, 100]
        current_compliance = self._iv_current_compliance
        current_minmax = [0.0, 1.0]
        is_up_down = self._iv_is_up_down

        # Define lists of accepted inputs for string variables
        rangename = self._iv_range
        modename = self._iv_mode
        spacename = self._iv_space

        # Create frame structure to place widgets in for IV Test
        c = ttk.Frame(self._root, padding=(12, 5, 12, 0))
        c.grid(column=0, row=0, sticky=(N,W,E,S))
        c.configure(borderwidth=5, relief='raised')

        # Create option lists for non-numeric inputs
        sweep_range_label = Label(c, text='Sweep Range:')
        sr_choice_1 = Radiobutton(c, text="BEST", variable=rangename,
                                    value="BEST")
        #sr_choice_2 = Radiobutton(self._root, text="Forming Pulse", variable=test_choice,
        #                            value="Forming Pulse", command=select_test)
        voltage_mode_label = Label(c, text='Voltage Mode:')
        vm_choice_1 = Radiobutton(c, text="SWE", variable=modename,
                                    value="SWE")
        #vm_choice_2 = Radiobutton(self._root, text="Forming Pulse", variable=test_choice,
        #                            value="Forming Pulse", command=select_test)
        sweep_space_label = Label(c, text='Sweep Space:')
        ss_choice_1 = Radiobutton(c, text="Linear", variable=spacename,
                                    value="LIN")
        ss_choice_2 = Radiobutton(c, text="Logarithmic", variable=spacename,
                                    value="LOG")

        # Set starting values based on previous set values
        def ivGetStartValues():
            try: # Open JSON file if one exists, otherwise tell user no previous data available
                with open('values.json', 'r') as openfile:
                    saved_vals = json.load(openfile)

                # Take previous values from JSON file and give everything a starting value
                source_voltage.set(saved_vals["iv_source_voltage"])
                source_delay.set(saved_vals["iv_source_delay"])
                source_voltage_start.set(saved_vals["iv_source_voltage_start"])
                source_voltage_stop.set(saved_vals["iv_source_voltage_stop"])
                source_voltage_step.set(saved_vals["iv_source_voltage_step"])
                log_num_steps.set(saved_vals["iv_log_num_steps"])
                trig_count.set(saved_vals["iv_trig_count"])
                current_compliance.set(saved_vals["iv_current_compliance"])
                is_up_down.set(saved_vals["iv_is_up_down"])
                rangename.set(saved_vals["iv_range"])
                modename.set(saved_vals["iv_mode"])
                spacename.set(saved_vals["iv_space"])
            except:
                print("Previous values not available, no JSON file found.")

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

        def checkVoltageStep(*args):
            svs = source_voltage_step.get()
            if svs > voltage_step_minmax[1]:
                source_voltage_step.set(voltage_step_minmax[1])
            elif svs <= voltage_step_minmax[0]:
                source_voltage_step.set(voltage_step_minmax[0] + 0.00001)

        def checkNumSteps(*args):
            ns = log_num_steps.get()
            if ns > num_steps_minmax[1]:
                log_num_steps.set(num_steps_minmax[1])
            elif ns < num_steps_minmax[0]:
                log_num_steps.set(num_steps_minmax[0])

        def checkTrigCount(*args):
            tc = trig_count.get()
            if tc > trig_count_minmax[1]:
                trig_count.set(trig_count_minmax[1])
            elif tc < trig_count_minmax[0]:
                trig_count.set(trig_count_minmax[0])

        def checkCurrent(*args):
            cc = current_compliance.get()
            if cc > current_minmax[1]:
                current_compliance.set(current_minmax[1])
            elif cc < current_minmax[0]:
                current_compliance.set(current_minmax[0])
            elif (spacename == 'LOG' and cc == current_minmax[0]):
                current_compliance.set(current_minmax[0] + 0.00001)

        # call value check functions whenever a value in the GUI changes
        source_voltage.trace_add('write', checkSourceVoltage)
        source_delay.trace_add('write', checkSourceDelay)
        source_voltage_start.trace_add('write', checkVoltageStart)
        source_voltage_stop.trace_add('write', checkVoltageStop)
        source_voltage_step.trace_add('write', checkVoltageStep)
        log_num_steps.trace_add('write', checkNumSteps)
        trig_count.trace_add('write', checkTrigCount)
        current_compliance.trace_add('write', checkCurrent)

        #Label the frame
        iv_test_label = Label(c, text="IV Test Parameters")
        iv_test_label.configure(font =("Arial", 28))

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

        src_voltage_step_label = Label(c, text='Source Voltage Step:')
        src_voltage_step_scale = Scale(c, variable=source_voltage_step, orient="horizontal",
                                    from_=voltage_step_minmax[0], to=voltage_step_minmax[1], resolution=0.00001, showvalue=0, 
                                    tickinterval=(voltage_step_minmax[1]-voltage_step_minmax[0]), command=checkVoltageStep)
        src_voltage_step_entry = Entry(c, textvariable=source_voltage_step)

        log_num_steps_label = Label(c, text='Number of Steps:')
        log_num_steps_scale = Scale(c, variable=log_num_steps, orient="horizontal",
                                    from_=num_steps_minmax[0], to=num_steps_minmax[1], resolution=1, showvalue=0, 
                                    tickinterval=(num_steps_minmax[1]-num_steps_minmax[0]), command=checkNumSteps)
        log_num_steps_entry = Entry(c, textvariable=log_num_steps)

        trig_count_label = Label(c, text='Trig Count:')
        trig_count_scale = Scale(c, variable=trig_count, orient="horizontal",
                                    from_=trig_count_minmax[0], to=trig_count_minmax[1], resolution=1, showvalue=0, 
                                    tickinterval=(trig_count_minmax[1]-trig_count_minmax[0]), command=checkTrigCount)
        trig_count_entry = Entry(c, textvariable=trig_count)

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
            src_voltage_entry.grid(column=3, columnspan=1, row=2, padx=10, pady=5)
            src_voltage_scale.grid(column=3, columnspan=1, row=3, padx=10, pady=0)

            src_delay_label.grid(column=3, columnspan=1, row=4, padx=10)
            src_delay_entry.grid(column=3, columnspan=1, row=5, padx=10, pady=5)
            src_delay_scale.grid(column=3, columnspan=1, row=6, padx=10, pady=0)

            src_voltage_start_label.grid(column=0, columnspan=1, row=7, padx=10)
            src_voltage_start_entry.grid(column=0, columnspan=1, row=8, padx=10)
            src_voltage_start_scale.grid(column=0, columnspan=1, row=9, padx=10)

            src_voltage_stop_label.grid(column=1, columnspan=1, row=7, padx=10)
            src_voltage_stop_entry.grid(column=1, columnspan=1, row=8, padx=10)
            src_voltage_stop_scale.grid(column=1, columnspan=1, row=9, padx=10)

            trig_count_label.grid(column=3, columnspan=1, row=7, padx=10)
            trig_count_entry.grid(column=3, columnspan=1, row=8, padx=10, pady=5)
            trig_count_scale.grid(column=3, columnspan=1, row=9, padx=10, pady=0)

            current_compliance_label.grid(column=4, columnspan=1, row=1, padx=10)
            current_compliance_entry.grid(column=4, columnspan=1, row=2, padx=10, pady=5)
            current_compliance_scale.grid(column=4, columnspan=1, row=3, padx=10, pady=0)

            stairs_button_label.grid(column=4, row=5)
            stairs_button.grid(column=4, row=6)

        ivGridAssign()

        def sweepSpaceChange(*args):
            if spacename == 'LOG':
                src_voltage_step_entry.grid_forget()
                src_voltage_step_label.grid_forget()
                src_voltage_step_scale.grid_forget()
                log_num_steps_label.grid(column=2, columnspan=1, row=7, padx=10)
                log_num_steps_entry.grid(column=2, columnspan=1, row=8, padx=10)
                log_num_steps_scale.grid(column=2, columnspan=1, row=9, padx=10)

            else:
                log_num_steps_entry.grid_forget()
                log_num_steps_label.grid_forget()
                log_num_steps_scale.grid_forget()
                src_voltage_step_label.grid(column=2, columnspan=1, row=7, padx=10)
                src_voltage_step_entry.grid(column=2, columnspan=1, row=8, padx=10)
                src_voltage_step_scale.grid(column=2, columnspan=1, row=9, padx=10)

        # Trigger a function every time sweep space choice is changed
        spacename.trace_add("write",callback=sweepSpaceChange)

        # Run once to populate blank spaces if possible
        sweepSpaceChange()

    def fp_frame_create(self):
        # Define variables
        voltage = self._fp_voltage
        #fp_voltage_minmax = [0.0, 5.0]
        delay = self._fp_delay
        #fp_delay_minmax = [0.0, .25]
        voltage_step = self._fp_voltage_step
        #fp_voltage_step_minmax = [0.0, 1.0]
        current_compliance = self._fp_current_compliance
        #current_minmax = [0.0, 1.0]
        period = self._fp_period
        rise_time = self._fp_rise_time
        fall_time = self._fp_fall_time
        #fp_rise_fall_minmax = [0.0, 1.0]
        forming_iv = self._fp_forming_iv

        # Set starting values based on previous set values
        def fpGetStartValues():
            try: # Open JSON file if one exists, otherwise tell user no previous data available
                with open('values.json', 'r') as openfile:
                    saved_vals = json.load(openfile)

                # Take previous values from JSON file and give everything a starting value
                voltage.set(saved_vals["fp_voltage"])
                delay.set(saved_vals["fp_delay"])
                voltage_step.set(saved_vals["fp_voltage_step"])
                period.set(saved_vals["fp_period"])
                rise_time.set(saved_vals["fp_rise_time"])
                fall_time.set(saved_vals["fp_fall_time"])
                forming_iv.set(saved_vals["fp_forming_iv"])
                current_compliance.set(saved_vals["fp_current_compliance"])
            except:
                print("Previous values not available, no JSON file found.")

        fpGetStartValues()

        # Created frame for Forming pulse
        f = ttk.Frame(self._root, padding=(12, 5, 12, 0))
        f.grid(column=0, row=2, sticky=(N,W,E,S))
        f.configure(borderwidth=5, relief='raised')

        #Label the frame
        fp_test_label = Label(f, text="Forming Pulse Parameters")
        fp_test_label.configure(font =("Arial", 28))

        # Create Widgets for inputs


        #Place items in Frame for Forming pulse
        def fpGridAssign():
            fp_test_label.grid(column=0,columnspan=5, row=0)
        fpGridAssign()

    def et_frame_create(self):
        '''
        Create and populate endurance test frame of GUI
        
        '''
        # Created frame for Endurance Test
        t = ttk.Frame(self._root, padding=(12, 5, 12, 0))
        t.grid(column=0, row=4, sticky=(N,W,E,S))
        t.configure(borderwidth=5, relief='raised')

        #Label the frame
        et_test_label = Label(t, text="Endurance Test Parameters")
        et_test_label.configure(font =("Arial", 28))

        # Create Widgets for inputs


        #Place items in Frame for Forming pulse
        def etGridAssign():
            et_test_label.grid(column=0, columnspan=5, row=0)
        etGridAssign()

    def gui_common_params(self):
        '''
        Creates elements of the GUI for inputs common across all three testing functions
        '''        
        # Define variables     
        device_x = self._gen_device_x
        device_y = self._gen_device_y
        device_coord_minmax = [0, 7] # Could change in the future
        chiplet_name = self._gen_chiplet_name
        test_choice = self._gen_test_choice
        button_text = StringVar(self._root)

        def GetStartValues():
            try: # Open JSON file if one exists, otherwise tell user no previous data available
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
                messagebox.showwarning("Warning!", "Chiplet name is invalid, please do not include any special characters")

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

        def select_test(*args):
            '''
            Sets the text on the run button to specify the selected test
            '''
            button_text.set("Run " + test_choice.get())

        test_choice_1 = Radiobutton(self._root, text="IV Test", variable=test_choice,
                                    value="IV Test", command=select_test)
        test_choice_2 = Radiobutton(self._root, text="Forming Pulse", variable=test_choice,
                                    value="Forming Pulse", command=select_test)
        test_choice_3 = Radiobutton(self._root, text="Endurance Test", variable=test_choice,
                                    value="Endurance Test", command=select_test)

        # Run once to populate blank spaces if possible
        select_test()

        button = Button(self._root, textvariable=button_text, command=self.set_values)

        # Universal parameters
        chiplet_name_label.grid(column=7, row=1)
        chiplet_name_entry.grid(column=8, row=1)

        device_xy_label.grid(column=6, row=3)
        device_x_entry.grid(column=7, row=3)
        device_y_entry.grid(column=8, row=3)

        test_choice_1.grid(column=6, row=7)
        test_choice_2.grid(column=7, row=7)
        test_choice_3.grid(column=8, row=7)

        button.grid(column=6, columnspan=3, row=9)
    
    def set_values(self):
        '''
        Run whenever run button on GUI is pressed
        Reads all values from GUI, saves all values to json file if filled out
        or informs user information is missing
        '''
        # When the run button is hit, show that a test was requested
        self._testRequested.append(self._gen_test_choice.get())

        dictionary = {
            # Generics
            "gen_device_x" : self._gen_device_x.get(),
            "gen_device_y" : self._gen_device_y.get(),
            "gen_chiplet_name" : self._gen_chiplet_name.get(),
            "gen_test_choice" : self._gen_test_choice.get(),
            "test_start_time" : datetime.now().strftime("%m-%d-%Y_%H-%M-%S"),
            # IV test vals
            "iv_range" : self._iv_range.get(),
            "iv_mode" : self._iv_mode.get(),
            "iv_space" : self._iv_space.get(),
            "iv_source_voltage" : self._iv_source_voltage.get(),
            "iv_source_delay" : self._iv_source_delay.get(),
            "iv_source_voltage_start" : self._iv_source_voltage_start.get(),
            "iv_source_voltage_stop" : self._iv_source_voltage_stop.get(),
            "iv_source_voltage_step" : self._iv_source_voltage_step.get(),
            "iv_log_num_steps" : self._iv_log_num_steps.get(),
            "iv_trig_count" : self._iv_trig_count.get(),
            "iv_current_compliance" : self._iv_current_compliance.get(),
            "iv_is_up_down" : self._iv_is_up_down.get(),
            # FP vals
            "fp_voltage" : self._fp_voltage.get(),
            "fp_delay" : self._fp_delay.get(),
            "fp_voltage_step" : self._fp_voltage_step.get(),
            "fp_current_compliance" : self._fp_current_compliance.get(),
            "fp_period" : self._fp_period.get(),
            "fp_rise_time" : self._fp_rise_time.get(),
            "fp_fall_time" : self._fp_fall_time.get(),
            "fp_forming_iv" : self._fp_forming_iv.get(),
        }
        with open("values.json", "w") as outfile:
            json.dump(dictionary, outfile)

        self._root.destroy()

    def requested_tests(self):
        '''
        Returns a list of tests in order to be conducted
        '''
        return self._testRequested 

# gui = GUI()
# gui.gui_start()