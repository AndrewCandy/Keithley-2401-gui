"""
Controller module for sourcemeter gui
"""
from collections import namedtuple
import os
import time
import pyvisa
import numpy as np
import pandas as pd
import gui
import tests
import functions
import microserial
import post_test_gui
import progress_gui


class SourceMeter:
    """
    Class containing all code used to interact with source meter, microcontroller, and GUI
    """

    def __init__(self):
        """
        Runs when an instance of SourceMeter is created
        """
        # Connect to source Meter
        resource_manager = pyvisa.ResourceManager()
        print(resource_manager.list_resources())
        self._instrument = resource_manager.open_resource(
            "GPIB0::24::INSTR"
        )  # Name of sourcemeter

        # Call GUI
        self._gui = gui.GUI()
        self._gui.gui_start()

        # Create place to store collected data
        self._ran_tests = []

    def run_test(self):
        """
        Run all tests requested by the GUI
        Updates _run_tests:
            A list of namedtuples containing the test class and a list of
            device test namedtuples for each device the test was executed on
        """
        test_list = self._gui.get_requested_tests()
        # Check to make sure at least one test has been requested
        if len(test_list) == 0:
            return

        # Create new namedtuple to store each devices test data along with its coords
        DeviceTest = namedtuple("DeviceTest", "x y data")
        RanTest = namedtuple("RanTest", "test device_test_list")
        # Loop through requested tests
        for test in test_list:
            # Loop through each device the test should run on
            device_test_list = []
            for coords in test.selected_devices:
                # Tell microcontroller what device we are targeting
                # microserial.message_micro(coords.x, coords.y)
                # Run the test
                data = test.run_sourcemeter(self._instrument)
                # Save the test data linked to the device coords
                device_test = DeviceTest(coords.x, coords.y, data)
                device_test_list.append(device_test)
            ran_test = RanTest(test, device_test_list)
            self._ran_tests.append(ran_test)

    # The function that loops though everything

    def create_excel_sheets(self):
        """
        Create an excel sheet containing relevant statistics and all test data
        for each test
        """
        local_time = time.localtime()
        current_time = time.strftime("%H_%M_%S", local_time)
        main_folder = functions.create_chip_folder(self._gui.get_requested_tests()[0])
        master_file = os.path.join(main_folder, f"Summary_{current_time}.xlsx")
        for ran_test in self._ran_tests:
            test = ran_test.test
            device_test_list = ran_test.device_test_list
            folder_path = functions.create_test_folder(test)
            for device_test in device_test_list:
                col = device_test.x
                row = device_test.y
                data = device_test.data
                dataframe = create_dataframe(data)
                filename = f"{folder_path}\Col{col}_Row{row}.xlsx"
                dataframe.to_excel(filename, index=False)
            create_master_excel(master_file, ran_test, folder_path)
    def run_post_test_gui(self):
        """
        Run the post test gui after the tests have been run
        """
        results_gui = post_test_gui.ResultsGUI(self._gui.get_requested_tests())
        results_gui.gui_start()


def create_dataframe(data_string):
    """
    Takes sourcemeter data string and converts to dataframe
    input:
        data_string: the output from the sourcemeter
    return:
        a pandas dataframe object containing the data from a sourcemeter test
    """

    measurements = data_string.split(",")
    # Reshape the measurements into a 2D array with 5 columns
    reshaped_values = np.reshape(measurements, (-1, 5))
    # Create a DataFrame with the reshaped values and column names
    dataframe = pd.DataFrame(
        reshaped_values,
        columns=["Voltage", "Current", "Resistance", "TimeStamp", "Status"],
    )
    dataframe = manipulate_df(dataframe)
    return dataframe


def manipulate_df(dataframe):
    """
    cleans and converts sourcemeter dataframe to numeric values
    input:
        dataframe with non-numeric data and special characters
    return:
        clean dataframe with numeric values
    """
    dataframe["Voltage"] = (
        dataframe["Voltage"].str.strip().str.strip("['").str.rstrip("'")
    )
    dataframe["Status"] = dataframe["Status"].str.rstrip("']")
    dataframe["Voltage"] = pd.to_numeric(dataframe["Voltage"])
    dataframe["Current"] = pd.to_numeric(dataframe["Current"])
    dataframe["Resistance"] = pd.to_numeric(dataframe["Resistance"])
    dataframe["TimeStamp"] = pd.to_numeric(dataframe["TimeStamp"])
    dataframe["Status"] = pd.to_numeric(dataframe["Status"])
    dataframe["TimeStamp"] = dataframe["TimeStamp"] - dataframe["TimeStamp"][0]
    # Add new column containing true resistance data
    dataframe["Real Resistance"] = dataframe["Voltage"] / dataframe["Current"]
    dataframe["Real Resistance"].apply(lambda x: f"{x:.2e}")
    return dataframe


def create_master_excel(filename, ran_test, folder_path):
    """
    Input: Filename for Summary of data, Test information, Path of the folder the data is stored in
    Return: Creates an excel sheet with all of the statistical information from the multiple tests.
    """
    # Create Variables
    col = []
    row = []
    set_v = []
    reset_v = []
    hrs = []
    lrs = []
    avg_lrs = []
    avg_hrs = []
    std_hrs = []
    std_lrs = []
    med_hrs = []
    med_lrs = []
    percent_75_hrs = []
    percent_75_lrs = []
    percent_25_hrs = []
    percent_25_lrs = []
    upper_range_hrs = []
    upper_range_lrs = []
    lower_range_hrs = []
    lower_range_lrs = []
    avg_reset_volt = []
    avg_set_volt = []
    std_set_volt = []
    std_reset_volt = []
    med_set_volt = []
    med_reset_volt = []
    percent_75_set_volt = []
    percent_75_reset_volt = []
    percent_25_set_volt = []
    percent_25_reset_volt = []
    upper_range_set_volt = []
    upper_range_reset_volt = []
    lower_range_set_volt = []
    lower_range_reset_volt = []
    i_max_pos = []
    i_max_neg = []
    avg_i_max_set = []
    std_i_max_set = []
    med_i_max_set = []
    percent_75_i_max_set = []
    percent_25_i_max_set = []
    upper_range_i_max_set = []
    lower_range_i_max_set = []
    avg_i_max_reset = []
    std_i_max_reset = []
    med_i_max_reset = []
    percent_75_i_max_reset = []
    percent_25_i_max_reset = []
    upper_range_i_max_reset = []
    lower_range_i_max_reset = []
    # Create Columns to send Variables
    col_names = [
        "ChipName",
        "Row",
        "Col",
        "TestType",
        "Avg. Vset",
        "Avg. Vreset",
        "Avg. i_max_set",
        "Avg. i_max_reset",
        "Avg. HRS",
        "Avg. LRS",
        "Std_Dev_Vset",
        "Med. Vset",
        "Vset 1.5IQR Upper",
        "Vset 1.5IQR Lower",
        "Std_Dev_Vreset",
        "Med. Vreset",
        "Vreset 1.5IQR Upper",
        "Vreset 1.5IQR Lower",
        "Std_Dev_i_max_set",
        "Med. i_max_set",
        "i_max_set 1.5IQR Upper",
        "i_max_set 1.5IQR Lower",
        "Std_Dev_i_max_reset",
        "Med. i_max_reset",
        "i_max_reset 1.5IQR Upper",
        "i_max_reset 1.5IQR Lower",
        "Std_Dev_HRS",
        "Med. HRS",
        "HRS 1.5IQR Upper",
        "HRS 1.5IQR Lower",
        "Std_Dev_LRS",
        "Med. LRS",
        "LRS 1.5IQR Upper",
        "LRS 1.5IQR Lower",
    ]
    # Access the data and calculate the values
    dataframe = pd.DataFrame(columns=col_names)
    test = ran_test.test
    device_test_list = ran_test.device_test_list
    chip_name = [test.chiplet_name] * len(device_test_list)
    test_type = [test.get_test_type()] * len(device_test_list)
    for device_test in device_test_list:
        set_v = []
        reset_v = []
        i_max_pos = []
        i_max_neg = []
        hrs = []
        lrs = []
        device_x = device_test.x
        device_y = device_test.y
        col.append(device_x)
        row.append(device_y)
        file_path = os.path.join(folder_path, f"Col{device_x}_Row{device_y}.xlsx")
        data = pd.read_excel(os.path.normpath(file_path))
        split_data = split_dataframe(data)
        # If there are multiple cycles in one test this breaks them down and splits into individual cycles
        for data in split_data:
            hrs.append(functions.find_hrs(data))
            lrs.append(functions.find_lrs(data))
        avg_hrs.append(np.mean(hrs))
        avg_lrs.append(np.mean(lrs))
        std_hrs.append(np.std(hrs))
        std_lrs.append(np.std(lrs))
        med_hrs.append(np.median(hrs))
        med_lrs.append(np.median(lrs))
        percent_75_hrs.append(np.percentile(hrs, 75))
        percent_75_lrs.append(np.percentile(lrs, 75))
        percent_25_hrs.append(np.percentile(hrs, 25))
        percent_25_lrs.append(np.percentile(lrs, 25))
        upper_range_hrs.append(
            np.percentile(hrs, 25)
            - 1.5 * (np.percentile(hrs, 75) - np.percentile(hrs, 25))
        )
        lower_range_hrs.append(
            np.percentile(hrs, 75)
            + 1.5 * (np.percentile(hrs, 75) - np.percentile(hrs, 25))
        )
        upper_range_lrs.append(
            np.percentile(lrs, 25)
            - 1.5 * (np.percentile(lrs, 75) - np.percentile(lrs, 25))
        )
        lower_range_lrs.append(
            np.percentile(lrs, 75)
            + 1.5 * (np.percentile(lrs, 75) - np.percentile(lrs, 25))
        )
        # Check if IV or Endurance
        if isinstance(test, tests.IVTest):
            split_data = split_dataframe(data)
            for data in split_data:
                i_max_set, i_max_reset = get_i_max(data)
                i_max_pos.append(i_max_set)
                i_max_neg.append(i_max_reset)
                set_volt, reset_volt = find_set_reset(data)
                set_v.append(set_volt)
                reset_v.append(reset_volt)
            avg_set_volt.append(np.mean(set_v))
            avg_reset_volt.append(np.mean(reset_v))
            std_set_volt.append(np.std(set_v))
            std_reset_volt.append(np.std(reset_v))
            med_set_volt.append(np.median(set_v))
            med_reset_volt.append(np.median(reset_v))
            percent_75_set_volt.append(np.percentile(set_v, 75))
            percent_75_reset_volt.append(np.percentile(reset_v, 75))
            percent_25_set_volt.append(np.percentile(set_v, 25))
            percent_25_reset_volt.append(np.percentile(reset_v, 25))
            upper_range_set_volt.append(
                np.percentile(set_v, 25)
                - 1.5 * (np.percentile(set_v, 75) - np.percentile(set_v, 25))
            )
            lower_range_set_volt.append(
                np.percentile(set_v, 75)
                + 1.5 * (np.percentile(set_v, 75) - np.percentile(set_v, 25))
            )
            upper_range_reset_volt.append(
                np.percentile(reset_v, 25)
                - 1.5 * (np.percentile(reset_v, 75) - np.percentile(reset_v, 25))
            )
            lower_range_reset_volt.append(
                np.percentile(reset_v, 75)
                + 1.5 * (np.percentile(reset_v, 75) - np.percentile(reset_v, 25))
            )
            avg_i_max_set.append(np.mean(i_max_pos))
            std_i_max_set.append(np.std(i_max_pos))
            med_i_max_set.append(np.median(i_max_pos))
            percent_75_i_max_set.append(np.percentile(i_max_pos, 75))
            percent_25_i_max_set.append(np.percentile(i_max_pos, 25))
            upper_range_i_max_set.append(
                np.percentile(i_max_pos, 25)
                - 1.5 * (np.percentile(i_max_pos, 75) - np.percentile(i_max_pos, 25))
            )
            lower_range_i_max_set.append(
                np.percentile(i_max_pos, 75)
                + 1.5 * (np.percentile(i_max_pos, 75) - np.percentile(i_max_pos, 25))
            )
            avg_i_max_reset.append(np.mean(i_max_neg))
            std_i_max_reset.append(np.std(i_max_neg))
            med_i_max_reset.append(np.median(i_max_neg))
            percent_75_i_max_reset.append(np.percentile(i_max_neg, 75))
            percent_25_i_max_reset.append(np.percentile(i_max_neg, 25))
            upper_range_i_max_reset.append(
                np.percentile(i_max_neg, 25)
                - 1.5 * (np.percentile(i_max_neg, 75) - np.percentile(i_max_neg, 25))
            )
            lower_range_i_max_reset.append(
                np.percentile(i_max_neg, 75)
                + 1.5 * (np.percentile(i_max_neg, 75) - np.percentile(i_max_neg, 25))
            )
        elif isinstance(test, tests.EnduranceTest):
            # Not calculated in ET, but cols must be equal lengths so fill them with None
            set_v.append(None)
            reset_v.append(None)
            avg_set_volt.append(None)
            avg_reset_volt.append(None)
            std_set_volt.append(None)
            std_reset_volt.append(None)
            med_set_volt.append(None)
            med_reset_volt.append(None)
            percent_75_set_volt.append(None)
            percent_75_reset_volt.append(None)
            percent_25_set_volt.append(None)
            percent_25_reset_volt.append(None)
            upper_range_set_volt.append(None)
            lower_range_set_volt.append(None)
            upper_range_reset_volt.append(None)
            lower_range_reset_volt.append(None)
            avg_i_max_set.append(None)
            std_i_max_set.append(None)
            med_i_max_set.append(None)
            percent_75_i_max_set.append(None)
            percent_25_i_max_set.append(None)
            upper_range_i_max_set.append(None)
            lower_range_i_max_set.append(None)
            avg_i_max_reset.append(None)
            std_i_max_reset.append(None)
            med_i_max_reset.append(None)
            percent_75_i_max_reset.append(None)
            percent_25_i_max_reset.append(None)
            upper_range_i_max_reset.append(None)
            lower_range_i_max_reset.append(None)

    # Send to Dataframe
    dataframe["ChipName"] = chip_name
    dataframe["Row"] = row
    dataframe["Col"] = col
    dataframe["TestType"] = test_type
    dataframe["Avg. HRS"] = avg_hrs
    dataframe["Avg. LRS"] = avg_lrs
    dataframe["Std_Dev_HRS"] = std_hrs
    dataframe["Std_Dev_LRS"] = std_lrs
    dataframe["Med. HRS"] = med_hrs
    dataframe["Med. LRS"] = med_lrs
    dataframe["HRS 1.5IQR Upper"] = upper_range_hrs
    dataframe["LRS 1.5IQR Upper"] = upper_range_lrs
    dataframe["HRS 1.5IQR Lower"] = lower_range_hrs
    dataframe["LRS 1.5IQR Lower"] = lower_range_lrs
    dataframe["Avg. Vset"] = avg_set_volt
    dataframe["Avg. Vreset"] = avg_reset_volt
    dataframe["Std_Dev_Vset"] = std_set_volt
    dataframe["Std_Dev_Vreset"] = std_reset_volt
    dataframe["Med. Vset"] = med_set_volt
    dataframe["Med. Vreset"] = med_reset_volt
    dataframe["Vset 1.5IQR Upper"] = upper_range_set_volt
    dataframe["Vreset 1.5IQR Upper"] = upper_range_reset_volt
    dataframe["Vset 1.5IQR Lower"] = lower_range_set_volt
    dataframe["Vreset 1.5IQR Lower"] = lower_range_reset_volt
    dataframe["Avg. i_max_set"] = avg_i_max_set
    dataframe["Std_Dev_i_max_set"] = std_i_max_set
    dataframe["Med. i_max_set"] = med_i_max_set
    dataframe["i_max_set 1.5IQR Upper"] = upper_range_i_max_set
    dataframe["i_max_set 1.5IQR Lower"] = lower_range_i_max_set
    dataframe["Avg. i_max_reset"] = avg_i_max_reset
    dataframe["Std_Dev_i_max_reset"] = std_i_max_reset
    dataframe["Med. i_max_reset"] = med_i_max_reset
    dataframe["i_max_reset 1.5IQR Upper"] = upper_range_i_max_reset
    dataframe["i_max_reset 1.5IQR Lower"] = lower_range_i_max_reset

    # Create File or Add to it
    if os.path.exists(filename):
        dataframe = pd.concat([pd.read_excel(filename), dataframe])
        dataframe.to_excel(filename, index=False)
    else:
        dataframe.to_excel(filename, index=False)


def find_set_reset(dataframe):
    """
    return:
        set, reset voltages in a list that is used to create a statiscal analysis
    """
    set_df = dataframe[dataframe["Voltage"] > 0]
    slopes_set = np.diff(set_df["Current"])
    slopes_max_index = np.argmax(slopes_set)

    reset_df = dataframe[dataframe["Voltage"] < 0]
    slopes_reset = np.diff(reset_df["Current"])
    slopes_min_index = np.argmax(slopes_reset)
    set_volt = set_df.iloc[slopes_max_index, 0]
    reset_volt = reset_df.iloc[slopes_min_index, 0]
    return set_volt, reset_volt


def get_i_max(dataframe):
    """
    Grabs the two largest currents in the dataframe,
    one when voltage postitive and other when its negative
    """
    set_df = dataframe[dataframe["Voltage"] > 0]
    i_max_set = max(set_df["Current"])
    reset_df = dataframe[dataframe["Voltage"] < 0]
    i_max_reset = max(reset_df["Current"])
    return i_max_set, i_max_reset


def split_dataframe(dataframe):
    """
    Takes the large dataframe from multiple IV's and breaks it up into smalled
    dataframes that can be analyzed
    Return: BrokenUp dataframe
    """
    split_dataframes = []
    start_index = 0
    prev_voltage = None

    for index, row in dataframe.iterrows():
        voltage = row["Voltage"]

        if voltage == 0 and prev_voltage == 0:
            split_dataframes.append(dataframe.iloc[start_index:index])
            start_index = index

        prev_voltage = voltage

    # Append the last section of the DataFrame (If only one loop then just send the dataframe)
    split_dataframes.append(dataframe.iloc[start_index:])

    return split_dataframes


def calc_iqr(data):
    """
    Find the interquartile range of a dataset
    """
    iqr = np.percentile(data, 75) - np.percentile(data, 25)
    return iqr


sm = SourceMeter()
sm.run_test()
sm.create_excel_sheets()
sm.run_post_test_gui()
