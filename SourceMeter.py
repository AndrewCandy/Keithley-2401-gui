from openpyxl import load_workbook
from openpyxl import Workbook
from openpyxl.cell import WriteOnlyCell
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.utils import FORMULAE
from collections import namedtuple
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xlwings as xw
import pyvisa
import gui
import microserial
import functions
import tests
import post_test_gui
# Test and features to add:
# Forming Pulse, Endurance Test
# Limits to each variable are as follows: When in Lin Voltage: 0-3.5V, Current:0-1A,
# trig_count:should be very large, step: should be very small,delay should be very small micro or nano seconds
# When working with Log: Voltage:Cant start at 0 and same stopping point, Current same thing,
# Points: very large number, same with trig_count.
# When working with custom: a list of values is needed to tell what amplitude pulse to send out.
# Forming pulse ~3.3-3.5V for a very short time (delay should be very small).
# Trig_count is dependent on how many pulses u want. =numofpulses*2
# More limits: For log function trig count and points need to be the same number but for linear
# trig count= (stop_voltage/step)-2. or Step = stop_voltage/trig_count. Need larger scale for trig count 100 not enough
# Creating device and accepting inputs from the GUI


class SourceMeter():
    """
    Class containing all code used to interact with source meter, microcontroller, and GUI
    """

    def __init__(self):
        '''

        '''
        # # Connect to source Meter
        # rm = pyvisa.ResourceManager()
        # # print(rm.list_resources())
        # self._instrument = rm.open_resource(
        #     'GPIB0::24::INSTR')  # Name of sourcemeter

        # Call GUI
        self._gui = gui.GUI()
        self._gui.gui_start()

        # Create place to store collected data
        self._ran_tests = []

    def run_test(self):
        '''
        Run all tests requested by the GUI
        Updates _run_tests:
            A list of namedtuples containing the test class and a list of
            device test namedtuples for each device the test was executed on
        '''
        # TODO: add progressbar progression here
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
        '''
        Create an excel sheet containing relevant statistics and all test data
        for each test
        '''
        sheet_name = "Sheet1"

        for ran_test in self._ran_tests:
            test = ran_test.test
            device_test_list = ran_test.device_test_list
            folder_path = functions.create_test_folder(test)
            for device_test in device_test_list:
                col = device_test.x
                row = device_test.y
                data = device_test.data
                dataframe = create_dataframe(data)
                filename = f'{folder_path}\{test.get_chip_name()}_Col{col}_Row{row}.xlsx'
                print('hi')
                save_to_excel(dataframe, filename)
                print('hey')
                if isinstance(test, tests.IVTest):
                    set_voltage, reset_voltage = find_set_reset(dataframe)
                    add_integer_to_excel(
                        filename, sheet_name, 'I11', 'Largest_Current_Diff_Set', set_voltage)
                    add_integer_to_excel(
                        filename, sheet_name, 'J11', 'Largest_Current_Diff_Reset', reset_voltage)
                elif isinstance(test, tests.EnduranceTest):
                    # These functions now return a list not a 1 column dataframe
                    hrs = functions.find_hrs(dataframe)
                    lrs = functions.find_lrs(dataframe)

    def run_post_test_gui(self):
        '''
        Run the post test gui after the tests have been run
        '''
        results_gui = post_test_gui.ResultsGUI(self._gui.get_requested_tests())
        results_gui.gui_start()


def create_dataframe(data_string):
    '''
    Takes sourcemeter data string and converts to dataframe
    input:
        data_string: the output from the sourcemeter
    return:
        a pandas dataframe object containing the data from a sourcemeter test
    '''
    measurements = data_string.split(',')
    # Reshape the measurements into a 2D array with 5 columns
    reshaped_values = np.reshape(measurements, (-1, 5))
    # Create a DataFrame with the reshaped values and column names
    dataframe = pd.DataFrame(reshaped_values, columns=[
        'Voltage', 'Current', 'Resistance', 'TimeStamp', 'Status'])
    # print(df_new.head())
    dataframe = manipulate_df(dataframe)
    return dataframe


def manipulate_df(dataframe):
    '''
    cleans and converts sourcemeter dataframe to numeric values
    input:
        dataframe with non-numeric data and special characters
    return:
        clean dataframe with numeric values
    '''
    dataframe['Voltage'] = dataframe['Voltage'].str.strip(
    ).str.strip("['").str.rstrip("'")
    dataframe['Status'] = dataframe['Status'].str.rstrip("']")
    dataframe['Voltage'] = pd.to_numeric(dataframe['Voltage'])
    dataframe['Current'] = pd.to_numeric(dataframe['Current'])
    dataframe['Resistance'] = pd.to_numeric(dataframe['Resistance'])
    dataframe['TimeStamp'] = pd.to_numeric(dataframe['TimeStamp'])
    dataframe['Status'] = pd.to_numeric(dataframe['Status'])

    # Add new column containing true resistance data
    dataframe["Real Resistance"] = dataframe['Voltage'] / dataframe['Current']
    dataframe["Real Resistance"].apply(lambda x: f"{x:.2e}")
    return dataframe


def save_to_excel(dataframe, name):
    '''
    Take dataframe, save values to excel file
    Find statistics of data and and add analysis to data file
    '''
    dataframe.to_excel(name, index=False)
    sheet_name = "Sheet1"
    '''df_mapping = {"A1": dataframe, "H1": dataframe.describe()}
    with xw.App(visible=False) as app:
        workbook = app.books.open(name)
        # Add sheet if it does not exist
        current_sheets = [sheet.name for sheet in workbook.sheets]
        if sheet_name not in current_sheets:
            workbook.sheets.add(sheet_name)
        # Write dataframe to cell range
        for cell_target, dataframe in df_mapping.items():
            workbook.sheets(sheet_name).range(cell_target).options(
                pd.DataFrame, index=True).value = dataframe
        workbook.save()
    '''


def add_integer_to_excel(filename, sheet_name, cell_target, header, value):
    '''
    '''
    with xw.App(visible=False) as app:
        workbook = app.books.open(filename)
        sheet = workbook.sheets[sheet_name]
        # Write the header
        sheet.range(cell_target).value = header
        # Write the value below the header
        sheet.range(cell_target).offset(row_offset=1).value = value
        # Save and close the workbook
        workbook.save()


def add_list_to_excel(filename, sheet_name, target, df, header_value):
    df_mapping = {target: df}
    with xw.App(visible=False) as app:
        workbook = app.books.open(filename)
        # Add sheet if it does not exist
        current_sheets = [sheet.name for sheet in workbook.sheets]
        if sheet_name not in current_sheets:
            workbook.sheets.add(sheet_name)
        # Write dataframe to cell range
        for cell_target, dataframe in df_mapping.items():
            sheet = workbook.sheets(sheet_name)
            header_range = sheet.range(cell_target)
            header_range.value = header_value
            data_range = header_range.offset(row_offset=1)
            data_range.options(index=False).value = dataframe
        workbook.save()


'''def insert_data(file,listdata,row, col):
    wb = xlsxwriter.Workbook(file)
    ws = wb.add_worksheet()
    for item in listdata:
        ws.write(row, col, item)
        row += 1
    wb.close()'''


def find_set_reset(dataframe):
    '''
    return:
        set, reset voltages
    '''
    set_df = dataframe[dataframe['Voltage'] > 0]
    slopes_set = np.diff(set_df["Current"])  # / np.diff(set_df["Voltage"])
    slopes_max_index = np.argmax(slopes_set)

    reset_df = dataframe[dataframe['Voltage'] < 0]
    # / np.diff(reset_df["Voltage"])
    slopes_reset = np.diff(reset_df["Current"])
    slopes_min_index = np.argmax(slopes_reset)
    print(slopes_max_index)
    print(slopes_min_index)
    set_volt = set_df.iloc[slopes_max_index, 0]
    reset_volt = reset_df.iloc[slopes_min_index, 0]
    print(set_volt, ' ', reset_volt)
    return set_volt, reset_volt


def create_blank_excel(filename):
    dataframe = pd.DataFrame()
    dataframe.to_excel(filename)


sm = SourceMeter()
# sm.run_test()
# sm.create_excel_sheets()
sm.run_post_test_gui()
