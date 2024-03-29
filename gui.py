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


class GUI:
    """
    A class to contain the tkinter GUI
    """

    def __init__(self):
        """
        upon init, creates GUI
        """
        # Create tkinter window
        self._root = Tk()
        self._style = ttk.Style()
        self._root.title("Keithley 2401 GUI")  # Title the window
        self._root.grid_columnconfigure(0, weight=1)  # Config rows and cols
        self._root.grid_rowconfigure(0, weight=1)
        self._style.configure("Red.TSpinbox", foreground="red")
        # Define all exported variables
        self._iv_space = StringVar(self._root)
        self._iv_source_voltage = DoubleVar(self._root)
        self._iv_source_delay = DoubleVar(self._root)
        self._iv_source_voltage_start = DoubleVar(self._root)
        self._iv_source_voltage_stop = DoubleVar(self._root)
        self._iv_source_voltage_neg = DoubleVar(self._root)
        self._iv_num_steps = IntVar(self._root)
        self._iv_neg_steps = IntVar(self._root)
        self._iv_current_compliance = DoubleVar(self._root)
        self._iv_accuracy = DoubleVar(self._root)
        self._iv_cycles = IntVar(self._root)
        self._forming_space = StringVar(self._root)
        self._forming_source_voltage = DoubleVar(self._root)
        self._forming_source_delay = DoubleVar(self._root)
        self._forming_source_voltage_start = DoubleVar(self._root)
        self._forming_source_voltage_stop = DoubleVar(self._root)
        self._forming_num_steps = IntVar(self._root)
        self._forming_current_compliance = DoubleVar(self._root)
        self._forming_accuracy = DoubleVar(self._root)
        self._forming_cycles = IntVar(self._root)
        self._et_set_voltage = DoubleVar(self._root)
        self._et_read_voltage = DoubleVar(self._root)
        self._et_reset_voltage = DoubleVar(self._root)
        self._et_cycles = IntVar(self._root)
        self._et_current_compliance = DoubleVar(self._root)
        self._et_accuracy = DoubleVar(self._root)
        self._et_source_voltage = DoubleVar(self._root)
        self._et_source_delay = DoubleVar(self._root)
        self._rt_read_voltage = DoubleVar(self._root)
        self._rt_cycles = IntVar(self._root)
        self._rt_current_compliance = DoubleVar(self._root)
        self._rt_source_voltage = DoubleVar(self._root)
        self._rt_source_delay = DoubleVar(self._root)
        self._rt_accuracy = DoubleVar(self._root)
        self._chiplet_name = StringVar(self._root)

        self._test_queue = []

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
        self._forming_test_num = 1
        self._et_test_num = 1
        self._rt_test_num = 1
        self._set_num = 1
        self._reset_num = 1

        self.gui_main_window()

    def gui_start(self):
        """
        Starts gui by running the tkinter mainloop
        """
        self._root.mainloop()

    def iv_frame_create(self, window):
        """
        Create IV GUI frame
        This is where you edit max and min values for gui
        """
        # Redefine variables
        source_voltage = self._iv_source_voltage
        source_delay = self._iv_source_delay
        source_voltage_start = self._iv_source_voltage_start
        source_voltage_stop = self._iv_source_voltage_stop
        source_voltage_neg = self._iv_source_voltage_neg
        num_steps = self._iv_num_steps
        neg_steps = self._iv_neg_steps
        current_compliance = self._iv_current_compliance
        accuracy = self._iv_accuracy
        cycles = self._iv_cycles
        spacename = self._iv_space
        accuracy_minmax = [0.01, 10]
        source_delay_minmax = [0.0, 0.25]
        source_voltage_minmax = [0.0, 3.5]
        source_voltage_neg_minmax = [-1.5, 0]
        current_minmax = [0.0, 0.01]
        num_steps_minmax = [1, 100]

        # Create frame structure to place widgets in for IV Test
        frame = ttk.Frame(window, padding=(12, 5, 12, 0))
        frame.grid(column=0, row=0, sticky=(N, W, E, S))
        frame.configure(borderwidth=5, relief="raised")

        # Create option lists for non-numeric inputs
        sweep_space_label = Label(frame, text="Sweep Space:")
        ss_choice_1 = Radiobutton(frame, text="Linear", variable=spacename, value="LIN")
        ss_choice_2 = Radiobutton(
            frame, text="Logarithmic", variable=spacename, value="LOG"
        )

        # Set starting values based on previous set values
        def get_start_values(filepath):
            try:  # Open JSON file if one exists, otherwise tell user no previous data available
                with open(filepath, "r") as openfile:
                    saved_vals = json.load(openfile)
                print(filepath)
                # Take previous values from JSON file and give everything a starting value
                source_voltage.set(saved_vals["iv_source_voltage"])
                source_delay.set(saved_vals["iv_source_delay"])
                source_voltage_start.set(saved_vals["iv_source_voltage_start"])
                source_voltage_stop.set(saved_vals["iv_source_voltage_stop"])
                source_voltage_neg.set(saved_vals["iv_source_voltage_neg"])
                num_steps.set(saved_vals["iv_log_num_steps"])
                neg_steps.set(saved_vals["iv_neg_steps"])
                current_compliance.set(saved_vals["iv_current_compliance"])
                accuracy.set(saved_vals["iv_accuracy"])
                spacename.set(saved_vals["iv_space"])
                cycles.set(saved_vals["iv_cycles"])
            except Exception as _:
                pass
                print("Previous values not available.1")

        get_start_values("values.json")

        # Label the frame
        iv_test_label = Label(frame, text="IV Test Parameters")
        iv_test_label.configure(font=("Arial", 28))

        # Create sliders and text entry points for numeric inputs
        src_voltage_label = Label(frame, text="Source Voltage:")
        src_voltage_scale = ttk.Spinbox(
            frame,
            from_=source_voltage_minmax[0],
            to=source_voltage_minmax[1],
            textvariable=source_voltage,
            increment=0.1,
            wrap=True,
        )

        src_delay_label = Label(frame, text="Source delay:")
        src_delay_scale = ttk.Spinbox(
            frame,
            textvariable=source_delay,
            from_=source_delay_minmax[0],
            to=source_delay_minmax[1],
            increment=0.01,
            wrap=True,
        )
        src_voltage_start_label = Label(frame, text="Source Voltage Start:")
        src_voltage_start_scale = ttk.Spinbox(
            frame,
            textvariable=source_voltage_start,
            from_=source_voltage_minmax[0],
            to=source_voltage_minmax[1],
            increment=0.1,
            wrap=True,
        )

        src_voltage_stop_label = Label(frame, text="Source Voltage Stop:")
        src_voltage_stop_scale = ttk.Spinbox(
            frame,
            textvariable=source_voltage_stop,
            from_=source_voltage_minmax[0],
            to=source_voltage_minmax[1],
            increment=0.1,
            wrap=True,
            style="TSpinbox",
        )

        src_voltage_neg_label = Label(frame, text="Source Voltage Negative")
        src_voltage_neg_scale = ttk.Spinbox(
            frame,
            textvariable=source_voltage_neg,
            from_=source_voltage_neg_minmax[0],
            to=source_voltage_neg_minmax[1],
            increment=0.1,
            wrap=True,
            style="TSpinbox",
        )

        num_steps_label = Label(frame, text="Number of Steps:")
        num_steps_scale = ttk.Spinbox(
            frame,
            textvariable=num_steps,
            from_=num_steps_minmax[0],
            to=num_steps_minmax[1],
            increment=1,
            wrap=True,
        )

        neg_steps_label = Label(frame, text="Negative Steps")
        neg_steps_scale = ttk.Spinbox(
            frame,
            textvariable=neg_steps,
            from_=num_steps_minmax[0],
            to=num_steps_minmax[1],
            increment=1,
            wrap=True,
        )

        accuracy_label = Label(frame, text="Accuracy:")
        accuracy_scale = ttk.Spinbox(
            frame, textvariable=accuracy, from_=0.01, to=10, increment=0.01, wrap=True
        )

        current_compliance_label = Label(frame, text="Current Compliance:")
        current_compliance_scale = ttk.Spinbox(
            frame,
            textvariable=current_compliance,
            from_=current_minmax[0],
            to=current_minmax[1],
            increment=0.001,
            wrap=True,
        )

        cycles_label = Label(frame, text="Cycles")
        cycles_scale = ttk.Spinbox(
            frame, textvariable=cycles, from_=1, to=100, increment=1, wrap=True
        )
        warning_label = Label(frame, text="", wraplength=200, fg="Red")

        def add_test(*args):
            """
            Adds test to test list and closes current window
            """
            window.destroy()
            # Make new IVTest object
            iv_test = tests.IVTest(
                grid=self._devices_grid,
                test_num=self._iv_test_num,
                chiplet_name=self._chiplet_name.get(),
                space=self._iv_space.get(),
                source_voltage=self._iv_source_voltage.get(),
                source_delay=self._iv_source_delay.get(),
                source_voltage_start=self._iv_source_voltage_start.get(),
                source_voltage_stop=self._iv_source_voltage_stop.get(),
                source_voltage_neg=self._iv_source_voltage_neg.get(),
                num_steps=self._iv_num_steps.get(),
                neg_steps=self._iv_neg_steps.get(),
                current_compliance=self._iv_current_compliance.get(),
                cycles=self._iv_cycles.get(),
                accuracy=self._iv_accuracy.get(),
            )
            self._test_queue.append(f"IV Test {self._iv_test_num}")
            self._iv_test_num += 1
            self._tests_requested.append(iv_test)

        button = Button(
            frame,
            text="Add Test",
            command=lambda: add_test(),
            width=25,
            height=3,
            background="white",
            activebackground="light blue",
        )
        # Press Enter to add test
        frame.focus_set()
        frame.bind("<Return>", lambda event: add_test())
        frame.bind_class("TSpinbox", "<Return>", lambda event: add_test())
        frame.bind("<Escape>", lambda event: window.destroy())
        frame.bind_class("TSpinbox", "<Escape>", lambda event: window.destroy())

        def iv_grid_assign():
            """
            Place items in frame
            """
            warning_label.grid(column=4, columnspan=2, row=8, padx=10)
            iv_test_label.grid(column=0, columnspan=5, row=0)

            sweep_space_label.grid(column=0, row=1)
            ss_choice_1.grid(column=0, row=2)
            ss_choice_2.grid(column=0, row=3)

            src_voltage_label.grid(column=3, columnspan=1, row=1, padx=10)
            src_voltage_scale.grid(column=3, columnspan=1, row=2, padx=10, pady=0)

            src_delay_label.grid(column=3, columnspan=1, row=4, padx=10)
            src_delay_scale.grid(column=3, columnspan=1, row=5, padx=10, pady=0)

            src_voltage_start_label.grid(column=1, columnspan=1, row=1, padx=10)
            src_voltage_start_scale.grid(column=1, columnspan=1, row=2, padx=10)

            src_voltage_stop_label.grid(column=1, columnspan=1, row=4, padx=10)
            src_voltage_stop_scale.grid(column=1, columnspan=1, row=5, padx=10)
            source_voltage_stop.trace_add(
                "write", callback=lambda *args: check_stop_voltage()
            )

            src_voltage_neg_label.grid(column=1, columnspan=1, row=7, padx=10)
            src_voltage_neg_scale.grid(column=1, columnspan=1, row=8, padx=10)
            source_voltage_neg.trace_add(
                "write", callback=lambda *args: check_neg_voltage()
            )

            num_steps_label.grid(column=0, columnspan=1, row=4, padx=10)
            num_steps_scale.grid(column=0, columnspan=1, row=5, padx=10)

            neg_steps_label.grid(column=0, columnspan=1, row=7, padx=10)
            neg_steps_scale.grid(column=0, columnspan=1, row=8, padx=10)

            accuracy_label.grid(column=3, columnspan=1, row=7, padx=10)
            accuracy_scale.grid(column=3, columnspan=1, row=8, padx=10)
            accuracy.trace_add("write", callback=lambda *args: check_accuracy())

            current_compliance_label.grid(column=4, columnspan=1, row=1, padx=10)
            current_compliance_scale.grid(
                column=4, columnspan=1, row=2, padx=10, pady=0
            )

            cycles_label.grid(column=4, columnspan=1, row=4, padx=10)
            cycles_scale.grid(column=4, columnspan=1, row=5, padx=10, pady=0)
            cycles.trace_add("write", callback=lambda *args: check_cycles())

            button.grid(column=9, columnspan=2, row=8, rowspan=2, padx=0)

        iv_grid_assign()

        def check_accuracy(*args):
            """
            Uses predetermined range to see if the inputted accuracy will work with the machine
            """
            try:
                value = accuracy.get()
                if value < accuracy_minmax[0]:
                    accuracy_scale["style"] = "Red.TSpinbox"
                    warning_label["text"] = "This value may not give any results."
                    warning_label["fg"] = "Red4"
                else:
                    accuracy_scale["style"] = "TSpinbox"
                    warning_label["text"] = ":)"
                    warning_label["fg"] = "Black"
            except Exception as _:
                pass

        def check_cycles(*args):
            """
            Checks if inputted cycles will work with Sourcemeter
            """
            try:
                value = cycles.get()
                if value == 0:
                    accuracy_scale["style"] = "Red.TSpinbox"
                    warning_label["text"] = "This value may not give any results."
                    warning_label["fg"] = "Red4"
                else:
                    accuracy_scale["style"] = "TSpinbox"
                    warning_label["text"] = ":)"
                    warning_label["fg"] = "Black"
            except Exception as _:
                pass

        def check_stop_voltage(*args):
            """
            Uses max and min values for voltage to warn user when they have inputted something outside the range
            """
            try:
                value = source_voltage_stop.get()
                if value > source_voltage_minmax[1]:
                    src_voltage_stop_scale["style"] = "Red.TSpinbox"
                    warning_label[
                        "text"
                    ] = "One or more values are potentially dangerous for the device."
                    warning_label["fg"] = "Red"
                else:
                    src_voltage_stop_scale["style"] = "TSpinbox"
                    warning_label["text"] = ":)"
                    warning_label["fg"] = "Black"
            except Exception as _:
                pass

        def check_neg_voltage(*args):
            """
            Uses max and min values for voltage to warn user when they have inputted something outside the range
            """
            try:
                value = source_voltage_neg.get()
                if value < source_voltage_neg_minmax[0]:
                    src_voltage_neg_scale["style"] = "Red.TSpinbox"
                    warning_label[
                        "text"
                    ] = "One or more values are potentially dangerous for the device."
                    warning_label["fg"] = "Red"
                elif value > source_voltage_neg_minmax[1]:
                    src_voltage_neg_scale["style"] = "Red.TSpinbox"
                    warning_label[
                        "text"
                    ] = "One or more values are potentially dangerous for the device."
                    warning_label["fg"] = "Red"
                else:
                    src_voltage_neg_scale["style"] = "TSpinbox"
                    warning_label["text"] = ":)"
                    warning_label["fg"] = "Black"
            except Exception as _:
                pass

        # Presets
        def store_preset():
            """
            Runs when save preset button is pushed
            takes current config and saves it to a json
            Prompts user for preset name in popup window
            """

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
                    window,
                    text="Note: You can rewrite an old preset by\n \
                                  assigning a new preset the same name",
                )
                label3.grid(column=0, row=4, pady=15)

            preset_window()
            # Wait to do anything else until popup window is closed
            self._root.wait_window(window)
            preset_name = preset.get()
            if preset_name == "":
                messagebox.showerror(
                    "Preset Warning", "You must provide a name for the preset"
                )
                preset_window()
            else:
                dictionary = {
                    "iv_space": self._iv_space.get(),
                    "iv_source_voltage": self._iv_source_voltage.get(),
                    "iv_source_delay": self._iv_source_delay.get(),
                    "iv_source_voltage_start": self._iv_source_voltage_start.get(),
                    "iv_source_voltage_stop": self._iv_source_voltage_stop.get(),
                    "iv_source_voltage_neg": self._iv_source_voltage_neg.get(),
                    "iv_log_num_steps": self._iv_num_steps.get(),
                    "iv_neg_steps": self._iv_neg_steps.get(),
                    "iv_current_compliance": self._iv_current_compliance.get(),
                    "iv_accuracy": self._iv_accuracy.get(),
                    "iv_cycles": self._iv_cycles.get(),
                }
                with open(f"IVTestPresets/{preset_name}.json", "w") as outfile:
                    json.dump(dictionary, outfile)
            update_preset_list()

        def load_preset():
            """
            Read from json file of selected preset and update current IVTest config to match
            """
            preset_name = selected_preset.get()
            get_start_values(f"IVTestPresets/{preset_name}")

        save_preset_button = Button(frame, text="save preset", command=store_preset)
        save_preset_button.grid(column=9, row=3)

        selected_preset = StringVar()
        presets = ttk.Combobox(frame, width=27, textvariable=selected_preset)
        presets.focus_set()
        frame.bind_class("TCombobox", "l", func=lambda event: load_preset())
        frame.bind_class("TCombobox", "<Return>", func=lambda event: add_test())
        frame.bind_class("TCombobox", "<Escape>", func=lambda event: window.destroy())
        presets.grid(column=9, row=1)

        # Create a list of files in DevicePresets folder

        def update_preset_list():
            preset_list = os.listdir("IVTestPresets/")
            for _, preset_name in enumerate(preset_list):
                preset_name = preset_name[0:-5]
            return preset_list

        # Adding list to presets combobox
        presets["values"] = update_preset_list()

        load_preset_button = Button(frame, text="load preset", command=load_preset)
        load_preset_button.grid(column=9, row=5)

    def forming_frame_create(self, window):
        """
        Create Forming GUI frame
        This is where you edit max and min values for gui
        """
        # Redefine variables
        source_voltage = self._forming_source_voltage
        source_delay = self._forming_source_delay
        source_voltage_start = self._forming_source_voltage_start
        source_voltage_stop = self._forming_source_voltage_stop
        num_steps = self._forming_num_steps
        current_compliance = self._forming_current_compliance
        accuracy = self._forming_accuracy
        cycles = self._forming_cycles
        spacename = self._forming_space
        accuracy_minmax = [0.01, 10]
        source_delay_minmax = [0.0, 0.25]
        source_voltage_minmax = [0.0, 3.5]
        current_minmax = [0.0, 0.01]
        num_steps_minmax = [1, 100]

        # Create frame structure to place widgets in for Forming Test
        frame = ttk.Frame(window, padding=(12, 5, 12, 0))
        frame.grid(column=0, row=0, sticky=(N, W, E, S))
        frame.configure(borderwidth=5, relief="raised")

        # Create option lists for non-numeric inputs
        sweep_space_label = Label(frame, text="Sweep Space:")
        ss_choice_1 = Radiobutton(frame, text="Linear", variable=spacename, value="LIN")
        ss_choice_2 = Radiobutton(
            frame, text="Logarithmic", variable=spacename, value="LOG"
        )

        # Set starting values based on previous set values
        def get_start_values(filepath):
            try:  # Open JSON file if one exists, otherwise tell user no previous data available
                with open(filepath, "r") as openfile:
                    saved_vals = json.load(openfile)
                print(filepath)
                # Take previous values from JSON file and give everything a starting value
                source_voltage.set(saved_vals["forming_source_voltage"])
                source_delay.set(saved_vals["forming_source_delay"])
                source_voltage_start.set(saved_vals["forming_source_voltage_start"])
                source_voltage_stop.set(saved_vals["forming_source_voltage_stop"])
                num_steps.set(saved_vals["forming_log_num_steps"])
                current_compliance.set(saved_vals["forming_current_compliance"])
                accuracy.set(saved_vals["forming_accuracy"])
                spacename.set(saved_vals["forming_space"])
                cycles.set(saved_vals["forming_cycles"])
            except Exception as _:
                pass
                print("Previous values not available.1")

        get_start_values("values.json")

        # Label the frame
        forming_test_label = Label(frame, text="Forming Test Parameters")
        forming_test_label.configure(font=("Arial", 28))

        # Create sliders and text entry points for numeric inputs
        src_voltage_label = Label(frame, text="Source Voltage:")
        src_voltage_scale = ttk.Spinbox(
            frame,
            from_=source_voltage_minmax[0],
            to=source_voltage_minmax[1],
            textvariable=source_voltage,
            increment=0.1,
            wrap=True,
        )

        src_delay_label = Label(frame, text="Source delay:")
        src_delay_scale = ttk.Spinbox(
            frame,
            textvariable=source_delay,
            from_=source_delay_minmax[0],
            to=source_delay_minmax[1],
            increment=0.01,
            wrap=True,
        )
        src_voltage_start_label = Label(frame, text="Source Voltage Start:")
        src_voltage_start_scale = ttk.Spinbox(
            frame,
            textvariable=source_voltage_start,
            from_=source_voltage_minmax[0],
            to=source_voltage_minmax[1],
            increment=0.1,
            wrap=True,
        )

        src_voltage_stop_label = Label(frame, text="Source Voltage Stop:")
        src_voltage_stop_scale = ttk.Spinbox(
            frame,
            textvariable=source_voltage_stop,
            from_=source_voltage_minmax[0],
            to=source_voltage_minmax[1],
            increment=0.1,
            wrap=True,
            style="TSpinbox",
        )

        num_steps_label = Label(frame, text="Number of Steps:")
        num_steps_scale = ttk.Spinbox(
            frame,
            textvariable=num_steps,
            from_=num_steps_minmax[0],
            to=num_steps_minmax[1],
            increment=1,
            wrap=True,
        )

        accuracy_label = Label(frame, text="Accuracy:")
        accuracy_scale = ttk.Spinbox(
            frame, textvariable=accuracy, from_=0.01, to=10, increment=0.01, wrap=True
        )

        current_compliance_label = Label(frame, text="Current Compliance:")
        current_compliance_scale = ttk.Spinbox(
            frame,
            textvariable=current_compliance,
            from_=current_minmax[0],
            to=current_minmax[1],
            increment=0.001,
            wrap=True,
        )

        cycles_label = Label(frame, text="Cycles")
        cycles_scale = ttk.Spinbox(
            frame, textvariable=cycles, from_=1, to=100, increment=1, wrap=True
        )
        warning_label = Label(frame, text="", wraplength=200, fg="Red")

        def add_test(*args):
            """
            Adds test to test list and closes current window
            """
            window.destroy()
            # Make new FormingTest object
            forming_test = tests.FormingTest(
                grid=self._devices_grid,
                test_num=self._forming_test_num,
                chiplet_name=self._chiplet_name.get(),
                space=self._forming_space.get(),
                source_voltage=self._forming_source_voltage.get(),
                source_delay=self._forming_source_delay.get(),
                source_voltage_start=self._forming_source_voltage_start.get(),
                source_voltage_stop=self._forming_source_voltage_stop.get(),
                num_steps=self._forming_num_steps.get(),
                current_compliance=self._forming_current_compliance.get(),
                cycles=self._forming_cycles.get(),
                accuracy=self._forming_accuracy.get(),
            )
            self._test_queue.append(f"Forming Test {self._forming_test_num}")
            self._forming_test_num += 1
            self._tests_requested.append(forming_test)

        button = Button(
            frame,
            text="Add Test",
            command=lambda: add_test(),
            width=25,
            height=3,
            background="white",
            activebackground="light blue",
        )
        # Press Enter to add test
        frame.focus_set()
        frame.bind("<Return>", lambda event: add_test())
        frame.bind_class("TSpinbox", "<Return>", lambda event: add_test())
        frame.bind("<Escape>", lambda event: window.destroy())
        frame.bind_class("TSpinbox", "<Escape>", lambda event: window.destroy())

        def grid_assign():
            """
            Place items in frame
            """
            warning_label.grid(column=4, columnspan=2, row=8, padx=10)
            forming_test_label.grid(column=0, columnspan=5, row=0)

            sweep_space_label.grid(column=0, row=1)
            ss_choice_1.grid(column=0, row=2)
            ss_choice_2.grid(column=0, row=3)

            src_voltage_label.grid(column=3, columnspan=1, row=1, padx=10)
            src_voltage_scale.grid(column=3, columnspan=1, row=2, padx=10, pady=0)

            src_delay_label.grid(column=3, columnspan=1, row=4, padx=10)
            src_delay_scale.grid(column=3, columnspan=1, row=5, padx=10, pady=0)

            src_voltage_start_label.grid(column=1, columnspan=1, row=1, padx=10)
            src_voltage_start_scale.grid(column=1, columnspan=1, row=2, padx=10)

            src_voltage_stop_label.grid(column=1, columnspan=1, row=4, padx=10)
            src_voltage_stop_scale.grid(column=1, columnspan=1, row=5, padx=10)
            source_voltage_stop.trace_add(
                "write", callback=lambda *args: check_stop_voltage()
            )

            num_steps_label.grid(column=0, columnspan=1, row=4, padx=10)
            num_steps_scale.grid(column=0, columnspan=1, row=5, padx=10)

            accuracy_label.grid(column=0, columnspan=1, row=7, padx=10)
            accuracy_scale.grid(column=0, columnspan=1, row=8, padx=10)
            accuracy.trace_add("write", callback=lambda *args: check_accuracy())

            current_compliance_label.grid(column=4, columnspan=1, row=1, padx=10)
            current_compliance_scale.grid(
                column=4, columnspan=1, row=2, padx=10, pady=0
            )

            cycles_label.grid(column=4, columnspan=1, row=4, padx=10)
            cycles_scale.grid(column=4, columnspan=1, row=5, padx=10, pady=0)
            cycles.trace_add("write", callback=lambda *args: check_cycles())

            button.grid(column=9, columnspan=2, row=8, rowspan=2, padx=0)

        grid_assign()

        def check_accuracy(*args):
            """
            Uses predetermined range to see if the inputted accuracy will work with the machine
            """
            try:
                value = accuracy.get()
                if value < accuracy_minmax[0]:
                    accuracy_scale["style"] = "Red.TSpinbox"
                    warning_label["text"] = "This value may not give any results."
                    warning_label["fg"] = "Red4"
                else:
                    accuracy_scale["style"] = "TSpinbox"
                    warning_label["text"] = ":)"
                    warning_label["fg"] = "Black"
            except Exception as _:
                pass

        def check_cycles(*args):
            """
            Checks if inputted cycles will work with Sourcemeter
            """
            try:
                value = cycles.get()
                if value == 0:
                    accuracy_scale["style"] = "Red.TSpinbox"
                    warning_label["text"] = "This value may not give any results."
                    warning_label["fg"] = "Red4"
                else:
                    accuracy_scale["style"] = "TSpinbox"
                    warning_label["text"] = ":)"
                    warning_label["fg"] = "Black"
            except Exception as _:
                pass

        def check_stop_voltage(*args):
            """
            Uses max and min values for voltage to warn user when they have inputted something outside the range
            """
            try:
                value = source_voltage_stop.get()
                if value > source_voltage_minmax[1]:
                    src_voltage_stop_scale["style"] = "Red.TSpinbox"
                    warning_label[
                        "text"
                    ] = "One or more values are potentially dangerous for the device."
                    warning_label["fg"] = "Red"
                else:
                    src_voltage_stop_scale["style"] = "TSpinbox"
                    warning_label["text"] = ":)"
                    warning_label["fg"] = "Black"
            except Exception as _:
                pass

        # Presets
        def store_preset():
            """
            Runs when save preset button is pushed
            takes current config and saves it to a json
            Prompts user for preset name in popup window
            """

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
                    window,
                    text="Note: You can rewrite an old preset by\n \
                                    assigning a new preset the same name",
                )
                label3.grid(column=0, row=4, pady=15)

            preset_window()
            # Wait to do anything else until popup window is closed
            self._root.wait_window(window)
            preset_name = preset.get()
            if preset_name == "":
                messagebox.showerror(
                    "Preset Warning", "You must provide a name for the preset"
                )
                preset_window()
            else:
                dictionary = {
                    "forming_space": self._forming_space.get(),
                    "forming_source_voltage": self._forming_source_voltage.get(),
                    "forming_source_delay": self._forming_source_delay.get(),
                    "forming_source_voltage_start": self._forming_source_voltage_start.get(),
                    "forming_source_voltage_stop": self._forming_source_voltage_stop.get(),
                    "forming_log_num_steps": self._forming_num_steps.get(),
                    "forming_current_compliance": self._forming_current_compliance.get(),
                    "forming_accuracy": self._forming_accuracy.get(),
                    "forming_cycles": self._forming_cycles.get(),
                }
                with open(f"FormingTestPresets/{preset_name}.json", "w") as outfile:
                    json.dump(dictionary, outfile)
            update_preset_list()

        def load_preset():
            """
            Read from json file of selected preset and update current FormingTest config to match
            """
            preset_name = selected_preset.get()
            get_start_values(f"FormingTestPresets/{preset_name}")

        save_preset_button = Button(frame, text="save preset", command=store_preset)
        save_preset_button.grid(column=9, row=3)

        selected_preset = StringVar()
        presets = ttk.Combobox(frame, width=27, textvariable=selected_preset)
        presets.focus_set()
        frame.bind_class("TCombobox", "l", func=lambda event: load_preset())
        frame.bind_class("TCombobox", "<Return>", func=lambda event: add_test())
        frame.bind_class("TCombobox", "<Escape>", func=lambda event: window.destroy())
        presets.grid(column=9, row=1)

        # Create a list of files in DevicePresets folder

        def update_preset_list():
            preset_list = os.listdir("FormingTestPresets/")
            for _, preset_name in enumerate(preset_list):
                preset_name = preset_name[0:-5]
            return preset_list

        # Adding list to presets combobox
        presets["values"] = update_preset_list()

        load_preset_button = Button(frame, text="load preset", command=load_preset)
        load_preset_button.grid(column=9, row=5)

    def et_frame_create(self, window):
        """
        Create and populate endurance test frame of GUI

        """
        # Redeclare variables
        set_voltage = self._et_set_voltage
        read_voltage = self._et_read_voltage
        reset_voltage = self._et_reset_voltage
        cycles = self._et_cycles
        current_compliance = self._et_current_compliance
        source_voltage = self._et_source_voltage
        source_delay = self._et_source_delay
        accuracy = self._et_accuracy
        accuracy_minmax = [0.01, 10]
        source_delay_minmax = [0.0, 0.25]
        source_voltage_minmax = [-1.5, 3.5]
        set_voltage_minmax = [0, 5]
        reset_voltage_minmax = [-5, 0]
        read_voltage_minmax = [-0.3, 0.3]
        current_minmax = [0.0, 0.002]
        cycles_minmax = [5, 500]

        def get_start_values(filename):
            """
            Attempts to collect most recent values to preset gui inputs
            """
            try:  # Open JSON file if one exists, otherwise tell user no previous data available
                with open(filename, "r") as openfile:
                    saved_vals = json.load(openfile)

                # Take previous values from JSON file and give everything a starting value
                set_voltage.set(saved_vals["et_set_voltage"])
                read_voltage.set(saved_vals["et_read_voltage"])
                reset_voltage.set(saved_vals["et_reset_voltage"])
                cycles.set(saved_vals["et_cycles"])
                current_compliance.set(saved_vals["et_current_compliance"])
                source_voltage.set(saved_vals["et_source_voltage"])
                source_delay.set(saved_vals["et_source_delay"])
                accuracy.set(saved_vals["et_accuracy"])
            except Exception as _:
                print("Previous values not available.")

        get_start_values("values.json")

        def check_set_voltage(*args):
            """
            Checks Set Voltage to see if it is out of range and if it could pontentially be dangerous for the device
            """
            try:
                value = set_voltage.get()
                if value > set_voltage_minmax[1]:
                    set_voltage_scale["style"] = "Red.TSpinbox"
                    warning_label[
                        "text"
                    ] = "One or more values are potentially dangerous for the device."
                    warning_label["fg"] = "Red"
                else:
                    set_voltage_scale["style"] = "TSpinbox"
                    warning_label["text"] = ":)"
                    warning_label["fg"] = "Black"
            except Exception as _:
                pass

        def check_accuracy(*args):
            """
            Uses predetermined range to see if the inputted accuracy will work with the machine
            """
            try:
                value = accuracy.get()
                if value < accuracy_minmax[0]:
                    accuracy_scale["style"] = "Red.TSpinbox"
                    warning_label["text"] = "This value may not give any results."
                    warning_label["fg"] = "Red4"
                else:
                    accuracy_scale["style"] = "TSpinbox"
                    warning_label["text"] = ":)"
                    warning_label["fg"] = "Black"
            except Exception as _:
                pass

        def check_reset_voltage(*args):
            """
            Checks Reset Voltage to see if it is out of range and if it could pontentially be dangerous for the device
            """
            try:
                value = reset_voltage.get()
                if value < reset_voltage_minmax[0]:
                    reset_voltage_scale["style"] = "Red.TSpinbox"
                    warning_label[
                        "text"
                    ] = "One or more values are potentially dangerous for the device."
                    warning_label["fg"] = "Red"
                elif value > reset_voltage_minmax[1]:
                    reset_voltage_scale["style"] = "Red.TSpinbox"
                    warning_label[
                        "text"
                    ] = "One or more values are potentially dangerous for the device."
                    warning_label["fg"] = "Red"
                else:
                    reset_voltage_scale["style"] = "TSpinbox"
                    warning_label["text"] = ":)"
                    warning_label["fg"] = "Black"
            except Exception as _:
                pass

        def check_read_voltage(*args):
            """
            Checks Read Voltage to see if it is out of range and if it could pontentially be dangerous for the device
            """
            try:
                value = read_voltage.get()
                if value < read_voltage_minmax[0]:
                    read_voltage_scale["style"] = "Red.TSpinbox"
                    warning_label[
                        "text"
                    ] = "One or more values are potentially dangerous for the device."
                    warning_label["fg"] = "Red"
                elif value > read_voltage_minmax[1]:
                    read_voltage_scale["style"] = "Red.TSpinbox"
                    warning_label[
                        "text"
                    ] = "One or more values are potentially dangerous for the device."
                    warning_label["fg"] = "Red"
                else:
                    read_voltage_scale["style"] = "TSpinbox"
                    warning_label["text"] = ":)"
                    warning_label["fg"] = "Black"
            except Exception as _:
                pass

        def check_cycles(*args):
            """
            Checks if inputted cycles will work with Sourcemeter
            """
            try:
                value = cycles.get()
                if value % 5 != 0:
                    cycles_scale["style"] = "Red.TSpinbox"
                    warning_label["text"] = "Cycles must be divisible by 5."
                    warning_label["fg"] = "Red"
                elif value == 0:
                    cycles_scale["style"] = "Red.TSpinbox"
                    warning_label["text"] = "This value may not give you any results."
                    warning_label["fg"] = "Red4"
                else:
                    cycles_scale["style"] = "TSpinbox"
                    warning_label["text"] = ":)"
                    warning_label["fg"] = "Black"
            except Exception as _:
                pass

        # Created frame for Endurance Test
        frame = ttk.Frame(window, padding=(12, 5, 12, 0))
        frame.grid(column=0, row=0, sticky=(N, W, E, S))
        frame.configure(borderwidth=5, relief="raised")

        # Label the frame
        et_test_label = Label(frame, text="Endurance Test Parameters")
        et_test_label.configure(font=("Arial", 28))
        et_test_label.grid(column=0, columnspan=5, row=0)

        # Create Widgets for inputs
        set_voltage_label = Label(frame, text="Set Voltage:")
        set_voltage_scale = ttk.Spinbox(
            frame,
            textvariable=set_voltage,
            from_=source_voltage_minmax[0],
            to=source_voltage_minmax[1],
            increment=0.1,
            wrap=True,
            style="TSpinbox",
        )
        set_voltage_label.grid(column=0, row=1)
        set_voltage_scale.grid(column=0, row=2)
        set_voltage.trace_add("write", callback=lambda *args: check_set_voltage())

        reset_voltage_label = Label(frame, text="Reset Voltage:")
        reset_voltage_scale = ttk.Spinbox(
            frame,
            textvariable=reset_voltage,
            from_=source_voltage_minmax[0],
            to=source_voltage_minmax[1],
            increment=0.1,
            wrap=True,
            style="TSpinbox",
        )
        reset_voltage_label.grid(column=0, row=4)
        reset_voltage_scale.grid(column=0, row=5)
        reset_voltage.trace_add("write", callback=lambda *args: check_reset_voltage())

        read_voltage_label = Label(frame, text="Read Voltage:")
        read_voltage_scale = ttk.Spinbox(
            frame,
            textvariable=read_voltage,
            from_=source_voltage_minmax[0],
            to=source_voltage_minmax[1],
            increment=0.1,
            wrap=True,
            style="TSpinbox",
        )
        read_voltage_label.grid(column=0, row=7)
        read_voltage_scale.grid(column=0, row=8)
        read_voltage.trace_add("write", callback=lambda *args: check_read_voltage())

        cycles_label = Label(frame, text="Number of Cycles:")
        cycles_scale = ttk.Spinbox(
            frame,
            textvariable=cycles,
            from_=cycles_minmax[0],
            to=cycles_minmax[1],
            increment=5,
            style="TSpinbox",
        )
        cycles_label.grid(column=2, row=1)
        cycles_scale.grid(column=2, row=2)
        cycles.trace_add("write", callback=lambda *args: check_cycles())

        src_voltage_label = Label(frame, text="Source Voltage:")
        src_voltage_scale = ttk.Spinbox(
            frame,
            textvariable=source_voltage,
            from_=source_voltage_minmax[0],
            to=source_voltage_minmax[1],
            increment=0.1,
        )
        src_voltage_label.grid(column=1, row=1)
        src_voltage_scale.grid(column=1, row=2)

        src_delay_label = Label(frame, text="Source delay:")
        src_delay_scale = ttk.Spinbox(
            frame,
            textvariable=source_delay,
            from_=source_delay_minmax[0],
            to=source_delay_minmax[1],
            increment=0.01,
        )
        src_delay_label.grid(column=1, row=4)
        src_delay_scale.grid(column=1, row=5)

        current_compliance_label = Label(frame, text="Current Compliance:")
        current_compliance_scale = ttk.Spinbox(
            frame,
            textvariable=current_compliance,
            from_=current_minmax[0],
            to=current_minmax[1],
            increment=0.001,
        )
        current_compliance_label.grid(column=3, row=1)
        current_compliance_scale.grid(column=3, row=2)

        accuracy_label = Label(frame, text="Accuracy")
        accuracy_scale = ttk.Spinbox(
            frame, textvariable=accuracy, from_=0, to=10, increment=0.01
        )
        accuracy_label.grid(column=2, row=4)
        accuracy_scale.grid(column=2, row=5)
        accuracy.trace_add("write", callback=lambda *args: check_accuracy())

        def add_test(*args):
            window.destroy()
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
                reset_voltage=self._et_reset_voltage.get(),
                accuracy=self._et_accuracy.get(),
            )
            self._test_queue.append(f"Endurance Test {self._et_test_num}")
            self._et_test_num += 1
            self._tests_requested.append(endurance_test)

        warning_label = Label(frame, text="", wraplength=100, fg="Red")
        warning_label.grid(column=2, columnspan=1, row=8, padx=0, pady=0)

        button = Button(
            frame,
            text="Add Test",
            command=lambda: add_test(),
            width=25,
            height=3,
            background="white",
            activebackground="light blue",
        )
        frame.focus_set()
        frame.bind("<Return>", lambda event: add_test())
        frame.bind_class("TSpinbox", "<Return>", lambda event: add_test())
        frame.bind("<Escape>", lambda event: window.destroy())
        frame.bind_class("TSpinbox", "<Escape>", lambda event: window.destroy())
        button.grid(column=9, columnspan=2, row=8, rowspan=2, padx=0)

        # presets
        def store_preset():
            """
            Runs when save preset button is pushed
            takes current config and saves it to a json
            Prompts user for preset name in popup window
            """

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
                    window,
                    text="Note: You can rewrite an old preset by\n \
                                             assigning a new preset the same name",
                )
                label3.grid(column=0, row=4, pady=15)

            preset_window()
            # Wait to do anything else until popup window is closed
            self._root.wait_window(window)
            preset_name = preset.get()
            if preset_name == "":
                messagebox.showerror(
                    "Preset Warning", "You must provide a name for the preset"
                )
                preset_window()
            else:
                dictionary = {
                    "et_set_voltage": self._et_set_voltage.get(),
                    "et_read_voltage": self._et_read_voltage.get(),
                    "et_reset_voltage": self._et_reset_voltage.get(),
                    "et_cycles": self._et_cycles.get(),
                    "et_current_compliance": self._et_current_compliance.get(),
                    "et_source_voltage": self._et_source_voltage.get(),
                    "et_source_delay": self._et_source_delay.get(),
                }
                with open(f"EnduranceTestPresets/{preset_name}.json", "w") as outfile:
                    json.dump(dictionary, outfile)

            update_preset_list()

        def load_preset():
            """
            Read from json file of selected preset and update current IVTest config to match
            """
            preset_name = selected_preset.get()
            get_start_values(f"EnduranceTestPresets/{preset_name}")

        save_preset_button = Button(frame, text="save preset", command=store_preset)
        save_preset_button.grid(column=9, row=3)

        selected_preset = StringVar()
        presets = ttk.Combobox(frame, width=27, textvariable=selected_preset)
        presets.focus_set()
        frame.bind_class("TCombobox", "l", func=lambda event: load_preset())
        frame.bind_class("TCombobox", "<Return>", func=lambda event: add_test())
        frame.bind_class("TCombobox", "<Escape>", func=lambda event: window.destroy())
        presets.grid(column=9, row=1)

        # Create a list of files in DevicePresets folder

        def update_preset_list():
            preset_list = os.listdir("EnduranceTestPresets/")
            for _, preset_name in enumerate(preset_list):
                preset_name = preset_name[0:-5]
            return preset_list

        # Adding list to presets combobox
        presets["values"] = update_preset_list()

        load_preset_button = Button(frame, text="load preset", command=load_preset)
        load_preset_button.grid(column=9, row=5)

    def rt_frame_create(self, window):
        """
        Create and populate endurance test frame of GUI

        """
        # Redeclare variables
        read_voltage = self._rt_read_voltage
        cycles = self._rt_cycles
        current_compliance = self._rt_current_compliance
        source_voltage = self._rt_source_voltage
        source_delay = self._rt_source_delay
        accuracy = self._rt_accuracy
        accuracy_minmax = [0.01, 10]
        source_delay_minmax = [0.0, 0.25]
        source_voltage_minmax = [-1.5, 3.5]
        read_voltage_minmax = [-0.3, 0.3]
        current_minmax = [0.0, 0.01]
        cycles_minmax = [1, 500]

        def get_start_values(filename):
            """
            Attempts to collect most recent values to preset gui inputs
            """
            try:  # Open JSON file if one exists, otherwise tell user no previous data available
                with open(filename, "r") as openfile:
                    saved_vals = json.load(openfile)

                # Take previous values from JSON file and give everything a starting value
                read_voltage.set(saved_vals["rt_read_voltage"])
                cycles.set(saved_vals["rt_cycles"])
                current_compliance.set(saved_vals["rt_current_compliance"])
                source_voltage.set(saved_vals["rt_source_voltage"])
                source_delay.set(saved_vals["rt_source_delay"])
                accuracy.set(saved_vals["rt_accuracy"])
            except Exception as _:
                print("Previous values not available.")

        get_start_values("values.json")

        def check_accuracy(*args):
            """
            Uses predetermined range to see if the inputted accuracy will work with the machine
            """
            try:
                value = accuracy.get()
                if value < accuracy_minmax[0]:
                    accuracy_scale["style"] = "Red.TSpinbox"
                    warning_label["text"] = "This value may not give any results."
                    warning_label["fg"] = "Red4"
                else:
                    accuracy_scale["style"] = "TSpinbox"
                    warning_label["text"] = ":)"
                    warning_label["fg"] = "Black"
            except Exception as _:
                pass

        def check_cycles(*args):
            """
            Checks if inputted cycles will work with Sourcemeter
            """
            try:
                value = cycles.get()
                if value < cycles_minmax[0]:
                    accuracy_scale["style"] = "Red.TSpinbox"
                    warning_label["text"] = "This value may not give any results."
                    warning_label["fg"] = "Red4"
                else:
                    accuracy_scale["style"] = "TSpinbox"
                    warning_label["text"] = ":)"
                    warning_label["fg"] = "Black"
            except Exception as _:
                pass

        def check_read_voltage(*args):
            """
            Checks Read Voltage to see if it is out of range and if it could pontentially be dangerous for the device
            """
            try:
                value = read_voltage.get()
                if value < read_voltage_minmax[0]:
                    read_voltage_scale["style"] = "Red.TSpinbox"
                    warning_label[
                        "text"
                    ] = "One or more values are potentially dangerous for the device."
                    warning_label["fg"] = "Red"
                elif value > read_voltage_minmax[1]:
                    read_voltage_scale["style"] = "Red.TSpinbox"
                    warning_label[
                        "text"
                    ] = "One or more values are potentially dangerous for the device."
                    warning_label["fg"] = "Red"
                else:
                    read_voltage_scale["style"] = "TSpinbox"
                    warning_label["text"] = ":)"
                    warning_label["fg"] = "Black"
            except Exception as _:
                pass

        # Created frame for Endurance Test
        frame = ttk.Frame(window, padding=(12, 5, 12, 0))
        frame.grid(column=0, row=0, sticky=(N, W, E, S))
        frame.configure(borderwidth=5, relief="raised")

        # Label the frame
        rt_test_label = Label(frame, text="Endurance Test Parameters")
        rt_test_label.configure(font=("Arial", 28))
        rt_test_label.grid(column=0, columnspan=5, row=0)

        # Create Widgets for inputs

        read_voltage_label = Label(frame, text="Read Voltage:")
        read_voltage_scale = ttk.Spinbox(
            frame,
            textvariable=read_voltage,
            from_=source_voltage_minmax[0],
            to=source_voltage_minmax[1],
            increment=0.1,
            wrap=True,
            style="TSpinbox",
        )
        read_voltage_label.grid(column=0, row=1)
        read_voltage_scale.grid(column=0, row=2)
        read_voltage.trace_add("write", callback=lambda *args: check_read_voltage())

        cycles_label = Label(frame, text="Number of Cycles:")
        cycles_scale = ttk.Spinbox(
            frame,
            textvariable=cycles,
            from_=cycles_minmax[0],
            to=cycles_minmax[1],
            increment=1,
            style="TSpinbox",
        )
        cycles_label.grid(column=2, row=1)
        cycles_scale.grid(column=2, row=2)
        cycles.trace_add("write", callback=lambda *args: check_cycles())

        src_voltage_label = Label(frame, text="Source Voltage:")
        src_voltage_scale = ttk.Spinbox(
            frame,
            textvariable=source_voltage,
            from_=source_voltage_minmax[0],
            to=source_voltage_minmax[1],
            increment=0.1,
        )
        src_voltage_label.grid(column=1, row=1)
        src_voltage_scale.grid(column=1, row=2)

        src_delay_label = Label(frame, text="Source delay:")
        src_delay_scale = ttk.Spinbox(
            frame,
            textvariable=source_delay,
            from_=source_delay_minmax[0],
            to=source_delay_minmax[1],
            increment=0.01,
        )
        src_delay_label.grid(column=0, row=4)
        src_delay_scale.grid(column=0, row=5)

        current_compliance_label = Label(frame, text="Current Compliance:")
        current_compliance_scale = ttk.Spinbox(
            frame,
            textvariable=current_compliance,
            from_=current_minmax[0],
            to=current_minmax[1],
            increment=0.001,
        )
        current_compliance_label.grid(column=3, row=1)
        current_compliance_scale.grid(column=3, row=2)

        accuracy_label = Label(frame, text="Accuracy")
        accuracy_scale = ttk.Spinbox(
            frame, textvariable=accuracy, from_=0, to=10, increment=0.01
        )

        accuracy_label.grid(column=1, row=4)
        accuracy_scale.grid(column=1, row=5)
        accuracy.trace_add("write", callback=lambda *args: check_accuracy())

        def add_test(*args):
            window.destroy()
            read_test = tests.ReadTest(
                grid=self._devices_grid,
                test_num=self._rt_test_num,
                chiplet_name=self._chiplet_name.get(),
                source_voltage=self._rt_source_voltage.get(),
                source_delay=self._rt_source_delay.get(),
                current_compliance=self._rt_current_compliance.get(),
                cycles=self._rt_cycles.get(),
                accuracy=self._rt_accuracy.get(),
                read_voltage=self._rt_read_voltage.get(),
            )
            self._test_queue.append(f"Read Test {self._rt_test_num}")
            self._rt_test_num += 1
            self._tests_requested.append(read_test)

        warning_label = Label(frame, text="", wraplength=100, fg="Red")
        warning_label.grid(column=2, columnspan=1, row=8, padx=0, pady=0)

        button = Button(
            frame,
            text="Add Test",
            command=lambda: add_test(),
            width=25,
            height=3,
            background="white",
            activebackground="light blue",
        )
        frame.focus_set()
        frame.bind("<Return>", lambda event: add_test())
        frame.bind_class("TSpinbox", "<Return>", lambda event: add_test())
        frame.bind("<Escape>", lambda event: window.destroy())
        frame.bind_class("TSpinbox", "<Escape>", lambda event: window.destroy())
        button.grid(column=9, columnspan=2, row=8, rowspan=2, padx=0)

        # presets
        def store_preset():
            """
            Runs when save preset button is pushed
            takes current config and saves it to a json
            Prompts user for preset name in popup window
            """

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
                    window,
                    text="Note: You can rewrite an old preset by\n \
                                             assigning a new preset the same name",
                )
                label3.grid(column=0, row=4, pady=15)

            preset_window()
            # Wait to do anything else until popup window is closed
            self._root.wait_window(window)
            preset_name = preset.get()
            if preset_name == "":
                messagebox.showerror(
                    "Preset Warning", "You must provide a name for the preset"
                )
                preset_window()
            else:
                dictionary = {
                    "rt_read_voltage": self._rt_read_voltage.get(),
                    "rt_cycles": self._rt_cycles.get(),
                    "rt_current_compliance": self._rt_current_compliance.get(),
                    "rt_source_voltage": self._rt_source_voltage.get(),
                    "rt_source_delay": self._rt_source_delay.get(),
                    "rt_accuracy": self._rt_accuracy.get(),
                }
                with open(f"ReadTestPresets/{preset_name}.json", "w") as outfile:
                    json.dump(dictionary, outfile)

            update_preset_list()

        def load_preset():
            """
            Read from json file of selected preset and update current IVTest config to match
            """
            preset_name = selected_preset.get()
            get_start_values(f"ReadTestPresets/{preset_name}")

        save_preset_button = Button(frame, text="save preset", command=store_preset)
        save_preset_button.grid(column=9, row=3)

        selected_preset = StringVar()
        presets = ttk.Combobox(frame, width=27, textvariable=selected_preset)
        presets.focus_set()
        frame.bind_class("TCombobox", "l", func=lambda event: load_preset())
        frame.bind_class("TCombobox", "<Return>", func=lambda event: add_test())
        frame.bind_class("TCombobox", "<Escape>", func=lambda event: window.destroy())
        presets.grid(column=9, row=1)

        # Create a list of files in DevicePresets folder

        def update_preset_list():
            preset_list = os.listdir("ReadTestPresets/")
            for _, preset_name in enumerate(preset_list):
                preset_name = preset_name[0:-5]
            return preset_list

        # Adding list to presets combobox
        presets["values"] = update_preset_list()

        load_preset_button = Button(frame, text="load preset", command=load_preset)
        load_preset_button.grid(column=9, row=5)

    def device_select_frame_create(self, window, col, row):
        """
        Create and populate device selector frame of GUI

        """
        # Create frame
        frame = ttk.Frame(window, padding=(12, 5, 12, 0))
        frame.grid(column=col, columnspan=2, row=row, rowspan=4, sticky=(N, W, E, S))
        frame.configure(borderwidth=5, relief="raised")

        # Label the frame
        ds_label = Label(frame, text="Endurance Test Parameters")
        ds_label.configure(font=("Arial", 28))
        ds_label.grid(column=0, columnspan=8, row=0)

        # Create and place widgets for device selection
        device_buttons = []
        for col in range(self._grid_size):
            row_list = []
            for row in range(self._grid_size):
                button = Button(
                    frame,
                    text=0,
                    bg="light gray",
                    activebackground="gray90",
                    width=2,
                    height=2,
                )
                button.grid(
                    row=row + 1, column=col, sticky=NW + NE + SW + SE + N + S + E + W
                )
                row_list.append(button)
            device_buttons.append(row_list)

        def change_device_grid_value(row, col):
            if self._devices_grid[row][col] == 1:
                self._devices_grid[row][col] = 0
                device_buttons[row][col].config(
                    text="0", bg="light gray", activebackground="gray90"
                )
                return
            self._devices_grid[row][col] = 1
            device_buttons[row][col].config(
                text="1", bg="deep sky blue", activebackground="light sky blue"
            )

        for row in range(self._grid_size):
            for col in range(self._grid_size):
                device_buttons[row][col].config(
                    command=lambda row=row, col=col: change_device_grid_value(row, col)
                )

        # Select row buttons
        row_buttons = []
        for row in range(self._grid_size):
            button = Button(frame, text="Select Row")
            button.grid(row=row + 1, column=8, sticky=NW + NE + SW + SE + N + S + E + W)
            row_buttons.append(button)

        def select_row(row):
            if row_buttons[row]["text"] == "Select Row":
                row_buttons[row]["text"] = "Deselect Row"
                for col in range(self._grid_size):
                    self._devices_grid[col][row] = 1
                    device_buttons[col][row].config(
                        text="1", bg="deep sky blue", activebackground="light sky blue"
                    )
            else:
                row_buttons[row]["text"] = "Select Row"
                for col in range(self._grid_size):
                    self._devices_grid[col][row] = 0
                    device_buttons[col][row].config(
                        text="0", bg="light gray", activebackground="gray90"
                    )

        for row, button in enumerate(row_buttons):
            button.config(command=lambda row=row: select_row(row))

        # Select column buttons
        col_buttons = []
        for col in range(self._grid_size):
            button = Button(frame, text="Select\nColumn")
            button.grid(row=9, column=col, sticky=NW + NE + SW + SE + N + S + E + W)
            col_buttons.append(button)

        def select_col(col):
            if col_buttons[col]["text"] == "Select\nColumn":
                col_buttons[col]["text"] = "Deselect\nColumn"
                for row in range(self._grid_size):
                    self._devices_grid[col][row] = 1
                    device_buttons[col][row].config(
                        text="1", bg="deep sky blue", activebackground="light sky blue"
                    )
            else:
                col_buttons[col]["text"] = "Select\nColumn"
                for row in range(self._grid_size):
                    self._devices_grid[col][row] = 0
                    device_buttons[col][row].config(
                        text="0", bg="light gray", activebackground="gray90"
                    )

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
                            text="1",
                            bg="deep sky blue",
                            activebackground="light sky blue",
                        )
            else:
                select_all_button["text"] = "Select All"
                for col in range(self._grid_size):
                    for row in range(self._grid_size):
                        self._devices_grid[col][row] = 0
                        device_buttons[col][row].config(
                            text="0", bg="light gray", activebackground="gray90"
                        )

        select_all_button.config(command=select_all)

        def store_preset():
            """
            Runs when save preset button is pushed
            takes current grid config and saves it to csv
            Prompts user for preset name in popup window
            """

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
                    window,
                    text="Note: You can rewrite an old preset by\n \
                                             assigning a new preset the same name",
                )
                label3.grid(column=0, row=4, pady=15)

            preset_window()
            # Wait to do anything else until popup window is closed
            self._root.wait_window(window)
            preset_name = preset.get()
            if preset_name == "":
                preset_window()
                messagebox.showerror(
                    "Preset Warning", "You must provide a name for the preset"
                )
            else:
                # Turn grid config into pandas DataFrame for use of to_csv
                dataframe = pd.DataFrame(self._devices_grid)
                dataframe.to_csv(
                    f"DevicePresets/{preset_name}.csv", header=False, index=False
                )
                # Update list of presets on main window
                update_preset_list()

        def load_preset():
            """
            Read from csv file of selected preset and update current grid config to match
            """
            preset_name = selected_preset.get()
            dataframe = pd.read_csv(
                f"DevicePresets/{preset_name}.csv", header=None, index_col=None
            )
            for col in range(self._grid_size):
                for row in range(self._grid_size):
                    if dataframe[row][col] == 1:
                        self._devices_grid[col][row] = 1
                        device_buttons[col][row].config(
                            text="1",
                            bg="deep sky blue",
                            activebackground="light sky blue",
                        )
                    else:
                        self._devices_grid[col][row] = 0
                        device_buttons[col][row].config(
                            text="0", bg="light gray", activebackground="gray90"
                        )

        save_preset_button = Button(frame, text="save preset", command=store_preset)
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
        presets["values"] = update_preset_list()

        load_preset_button = Button(
            frame, text="load preset", command=lambda: load_preset()
        )
        load_preset_button.grid(column=9, row=5)

        # Try to load most recent grid layout
        try:
            dataframe = pd.read_csv(
                "device_grid_last_vals.csv", header=None, index_col=None
            )
            for col in range(self._grid_size):
                for row in range(self._grid_size):
                    if dataframe[row][col] == 1:
                        self._devices_grid[col][row] = 1
                        device_buttons[col][row].config(
                            text="1",
                            bg="deep sky blue",
                            activebackground="light sky blue",
                        )
                    else:
                        self._devices_grid[col][row] = 0
                        device_buttons[col][row].config(
                            text="0", bg="light gray", activebackground="gray90"
                        )
        except Exception as _:
            print("No previous data available")

    def gui_main_window(self):
        """
        Creates elements of the GUI for inputs common across all three testing functions
        """
        # Define variables
        chiplet_name = self._chiplet_name

        def get_start_values():
            try:  # Open JSON file if one exists, otherwise tell user no previous data available
                with open("values.json", "r") as openfile:
                    saved_vals = json.load(openfile)

                chiplet_name.set(saved_vals["chiplet_name"])
            except Exception as _:
                print("Previous values not available.")

        get_start_values()

        def add_iv(*args):
            """
            Creates IV test window to select parameters and add test to queue
            """
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
            # if(check_vars(self,self._iv_source_voltage_stop,self._iv_source_voltage_neg)):
            #   print('Fix the Values')
            test_lb["listvariable"] = Variable(value=self._test_queue)

        def add_forming(*args):
            """
            Creates forming test window to select parameters and add test to queue
            """
            # Create new window
            window = Toplevel()
            # Ensure window always shows up in the same space
            pos_x = self._root.winfo_x()
            pos_y = self._root.winfo_y()
            window.geometry(f"+{pos_x+50}+{pos_y+50}")

            # Populate window with formingTest options
            self.forming_frame_create(window)

            # Wait to do anything else until popup window is closed
            self._root.wait_window(window)
            # if(check_vars(self,self._forming_source_voltage_stop,self._forming_source_voltage_neg)):
            #   print('Fix the Values')
            test_lb["listvariable"] = Variable(value=self._test_queue)

        def add_et(*args):
            """
            Creates Endurance Test window to set parameters and add test to queue
            """
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
            test_lb["listvariable"] = Variable(value=self._test_queue)

        def add_rt(*args):
            """
            Creates Endurance Test window to set parameters and add test to queue
            """
            # Create new window
            window = Toplevel()
            # Ensure window always shows up in the same space
            pos_x = self._root.winfo_x()
            pos_y = self._root.winfo_y()
            window.geometry(f"+{pos_x+50}+{pos_y+50}")

            # Populate window with IVTest options
            self.rt_frame_create(window)

            # Wait to do anything else until popup window is closed
            self._root.wait_window(window)
            # Make new EnduranceTest object
            test_lb["listvariable"] = Variable(value=self._test_queue)

        def clear_lb(*args):
            """
            Resets the test queue to empty
            """
            test_lb.delete(0, END)
            (
                self._iv_test_num,
                self._forming_test_num,
                self._et_test_num,
                self._set_num,
                self._reset_num,
            ) = (
                0,
                0,
                0,
                0,
                0,
            )
            self._tests_requested = []
            self._test_queue = []

        def delete_selected_test(*args):
            """
            removes currently selected test from the test queue
            """
            index = test_lb.curselection()[0]
            deleted_test = self._tests_requested.pop(index)
            test_indicator = deleted_test.get_test_type()[0]
            del self._test_queue[index]
            # Decrease test num for selected test type
            if test_indicator == "E":
                self._et_test_num -= 1
            else:
                self._iv_test_num -= 1

            # Renumber any later tests of the same type
            for i, test in enumerate(self._tests_requested[index:]):
                if test.get_test_type()[0] == test_indicator:
                    name = self._test_queue[i]
                    trimmed_name = re.findall(r"^\D+\s\D+\s", name)[0]
                    new_test_num = int(re.findall(r"\d+$", name)[0]) - 1
                    test.test_num = new_test_num
                    self._test_queue.insert(i, trimmed_name + str(new_test_num))
            test_lb["listvariable"] = Variable(value=self._test_queue)

        # Chip name box
        name_frame = ttk.Frame(self._root, padding=(12, 5, 12, 0))
        name_frame.grid(column=4, columnspan=2, row=0, rowspan=4, sticky=(N, W, E, S))
        name_frame.configure(borderwidth=5, relief="raised")
        chiplet_name_label = Label(name_frame, text="Chiplet Name/Identifier:")
        chiplet_name_entry = Entry(name_frame, textvariable=chiplet_name)
        chiplet_name_label.grid(column=0, row=0, pady=15)
        chiplet_name_entry.grid(column=0, row=1, pady=15)

        # Device grid box
        self.device_select_frame_create(self._root, col=0, row=0)
        # Test queue box
        frame = ttk.Frame(self._root, padding=(12, 5, 12, 0))
        frame.grid(column=2, columnspan=2, row=0, rowspan=4, sticky=(N, W, E, S))
        frame.configure(borderwidth=5, relief="raised")
        test_lb = Listbox(frame, selectmode="BROWSE")
        test_lb_label = Label(frame, text="Test Queue:")
        keyboard_label = Label(
            frame,
            text="Keyboard Shortcuts: \n I - IV Test, L - Load Preset, \n E - Endurance, Enter - Send Test, Esc - Exit Window",
        )
        add_iv_button = Button(frame, text="Add IV Test", command=add_iv)
        add_forming_button = Button(frame, text="Add Forming Test", command=add_forming)
        add_et_button = Button(frame, text="Add Endurance Test", command=add_et)
        add_rt_button = Button(frame, text="Add Read Test", command=add_rt)
        clear_lb_button = Button(frame, text="Clear Test Queue", command=clear_lb)
        del_test_button = Button(
            frame, text="Delete Selected Test", command=delete_selected_test
        )

        self._root.focus_set()
        self._root.bind("i", func=lambda event: add_iv())
        self._root.bind("f", func=lambda event: add_forming())
        self._root.bind("e", func=lambda event: add_et())
        self._root.bind("r", func=lambda event: add_rt())

        test_lb_label.grid(column=1, columnspan=2, row=0)
        keyboard_label.grid(column=1, columnspan=1, row=8)
        test_lb.grid(column=1, columnspan=2, row=1, rowspan=4)
        clear_lb_button.grid(column=1, columnspan=2, row=5, rowspan=1)
        del_test_button.grid(column=1, columnspan=2, row=6, rowspan=1)
        add_iv_button.grid(column=0, columnspan=1, row=1, rowspan=1)
        add_et_button.grid(column=0, columnspan=1, row=2, rowspan=1)
        add_rt_button.grid(column=0, columnspan=1, row=3, rowspan=1)
        add_forming_button.grid(column=0, columnspan=1, row=4, rowspan=1)

        # Run button
        button = Button(
            self._root,
            text="Run",
            command=self.set_values,
            width=25,
            height=3,
            background="red",
            activebackground="tomato",
        )
        self._root.focus_set()
        self._root.bind("<Return>", lambda event: self.set_values())
        self._root.bind("<Escape>", lambda event: self._root.destroy())
        button.grid(column=4, columnspan=2, row=4, rowspan=2, padx=0)

    def set_values(self):
        """
        Run whenever run button on GUI is pressed
        Reads all values from GUI, saves all values to json file if filled out
        """
        dictionary = {
            # Generics
            "chiplet_name": self._chiplet_name.get(),
            # IV test vals
            "iv_space": self._iv_space.get(),
            "iv_source_voltage": self._iv_source_voltage.get(),
            "iv_source_delay": self._iv_source_delay.get(),
            "iv_source_voltage_start": self._iv_source_voltage_start.get(),
            "iv_source_voltage_stop": self._iv_source_voltage_stop.get(),
            "iv_source_voltage_neg": self._iv_source_voltage_neg.get(),
            "iv_log_num_steps": self._iv_num_steps.get(),
            "iv_neg_steps": self._iv_neg_steps.get(),
            "iv_current_compliance": self._iv_current_compliance.get(),
            "iv_accuracy": self._iv_accuracy.get(),
            "iv_cycles": self._iv_cycles.get(),
            # Forming Vals
            "forming_space": self._forming_space.get(),
            "forming_source_voltage": self._forming_source_voltage.get(),
            "forming_source_delay": self._forming_source_delay.get(),
            "forming_source_voltage_start": self._forming_source_voltage_start.get(),
            "forming_source_voltage_stop": self._forming_source_voltage_stop.get(),
            "forming_log_num_steps": self._forming_num_steps.get(),
            "forming_current_compliance": self._forming_current_compliance.get(),
            "forming_accuracy": self._forming_accuracy.get(),
            "forming_cycles": self._forming_cycles.get(),
            # ET vals
            "et_set_voltage": self._et_set_voltage.get(),
            "et_read_voltage": self._et_read_voltage.get(),
            "et_reset_voltage": self._et_reset_voltage.get(),
            "et_cycles": self._et_cycles.get(),
            "et_current_compliance": self._et_current_compliance.get(),
            "et_source_voltage": self._et_source_voltage.get(),
            "et_source_delay": self._et_source_delay.get(),
            "et_accuracy": self._et_accuracy.get(),
            # Read Vals
            "rt_read_voltage": self._rt_read_voltage.get(),
            "rt_cycles": self._rt_cycles.get(),
            "rt_current_compliance": self._rt_current_compliance.get(),
            "rt_source_voltage": self._rt_source_voltage.get(),
            "rt_source_delay": self._rt_source_delay.get(),
            "rt_accuracy": self._rt_accuracy.get(),
        }
        with open("values.json", "w") as outfile:
            json.dump(dictionary, outfile)

        # Save device grid
        dataframe = pd.DataFrame(self._devices_grid)
        dataframe.to_csv("device_grid_last_vals.csv", header=False, index=False)
        self._root.destroy()

    def get_requested_tests(self):
        """
        Returns a list of tests in order to be conducted
        """
        return self._tests_requested


def check_special_chars(string):
    """
    return:
        1 if string contains special chars, 0 otherwise
    """
    if re.search("[^a-zA-Z0-9s]", string):
        return 1
    return 0

#gui = GUI()
#gui.gui_start()
