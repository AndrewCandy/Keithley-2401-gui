import pyvisa
import csv
import matplotlib.pyplot as plt
from collections import namedtuple
import gui
import post_test_gui
import time
import microserial
import functions
import numpy as np
import pandas as pd
import statistics
import tests
import os
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
        # Connect to source Meter
        rm = pyvisa.ResourceManager()
        # print(rm.list_resources())
        self._instrument = rm.open_resource(
            'GPIB0::24::INSTR')  # Name of sourcemeter

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
        folder_path = functions.create_test_folder(self._gui.get_requested_tests()[0])
        master_file = os.path.join(folder_path, 'Summary.xlsx')
        for ran_test in self._ran_tests:
            test = ran_test.test
            device_test_list = ran_test.device_test_list
            test_type = test.get_test_type()
            for device_test in device_test_list:
                col = device_test.x
                row = device_test.y
                data = device_test.data
                dataframe = create_dataframe(data)
                filename = f'{folder_path}\{test.chiplet_name}_{test_type}_Col{col}_Row{row}.xlsx'
                save_to_excel(dataframe, filename)
            create_master_excel(master_file,ran_test,folder_path)
        # merge_excel_sheets(folder_path,test)
    

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


'''def write_test_type(test):
    
    Returns:
        a string describing conducted test to be used in making file name
    
    # Create test name for file naming
    test_type = ""
    if isinstance(test, tests.IVTest):
        # Lin or log
        if test.get_voltage_space == 'LIN':
            test_type += "Linear_"
        elif test.get_voltage_space == 'LOG':
            test_type += "Logarithmic_"
        # Show it was an IV
        test_type += "IV"
    elif isinstance(test, tests.EnduranceTest):
        test_type += "Endurance"
    return test_type


def create_test_folder(test):
    
    Creates folder for all device test files of a test
    return:
        folder path
    
    test_type = write_test_type(test)
    str_time = test.start_time.strftime("%m-%d-%Y_%H-%M-%S")
    # Get current directory
    home_dir = os.path.abspath(__file__)
    current_directory = os.path.dirname(home_dir)
    # Make new folder for test if doesn't exist
    folder_path = os.path.join(
        current_directory, f"SavedData\{test_type}_{str_time}")
    os.makedirs(folder_path, exist_ok=True)
    return folder_path
'''

def find_HRS(dataframe):
    resistance = dataframe['Real Resistance']
    HRS = []
    for i in range(2, len(resistance), 8):
        HRS.append(resistance[i])
    return HRS


def find_LRS(dataframe):
    resistance = dataframe['Real Resistance']
    LRS = []
    for i in range(6, len(resistance), 8):
        LRS.append(resistance[i])
    return LRS


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
    set_volt = set_df.iloc[slopes_max_index, 0]
    reset_volt = reset_df.iloc[slopes_min_index, 0]
    print(set_volt, ' ', reset_volt)
    return set_volt, reset_volt


def create_master_excel(filename, ran_test,folder_path):
    '''
        #TODO: Data to grab: TestType, Column, Row, Chip, VSet, VReset (Stats with those), HRS and LRS
        TestParameter Length = 12
        Name Value Length = 1
        DataValue = 1
        All multiplied by number of tests
    '''
    print(filename)
    col_names = ['ChipName','Row', 'Col','TestType','Vset','Vreset','Avg. Vset','Std_Dev_Vset','Med. Vset','Vset 1.5IQR Upper','Vset 1.5IQR Lower','Avg. Vreset','Std_Dev_Vreset','Med. Vreset','Vreset 1.5IQR Upper','Vreset 1.5IQR Lower','Avg. HRS', 'Std_Dev_HRS','Med. HRS','HRS 1.5IQR Upper','HRS 1.5IQR Lower','Avg. LRS', 'Std_Dev_LRS','Med. LRS', 'LRS 1.5IQR Upper','LRS 1.5IQR Lower']
    df = pd.DataFrame(columns=col_names)
    test = ran_test.test
    device_test_list = ran_test.device_test_list
    Chipname =  [test.chiplet_name]*len(device_test_list)
    test_type = [test.get_test_type()]*len(device_test_list)
    col = []
    row = []
    setV = []
    resetV = []
    avg_LRS = []
    avg_HRS = []
    std_HRS = []
    std_LRS = []
    med_HRS = []
    med_LRS = []
    Percent_75_HRS = []
    Percent_75_LRS = []
    Percent_25_HRS = []
    Percent_25_LRS = []
    Upper_Range_HRS = []
    Upper_Range_LRS = []
    Lower_Range_HRS = []
    Lower_Range_LRS = []
    avg_resetVolt = []
    avg_setVolt = []
    std_setVolt = []
    std_resetVolt = []
    med_setVolt = []
    med_resetVolt = []
    Percent_75_setVolt = []
    Percent_75_resetVolt = []
    Percent_25_setVolt = []
    Percent_25_resetVolt = []
    Upper_Range_setVolt = []
    Upper_Range_resetVolt = []
    Lower_Range_setVolt = []
    Lower_Range_resetVolt = []
    for device_test in device_test_list:
        col.append(device_test.x)
        row.append(device_test.y)
        file_path = os.path.join(folder_path,f'{test.chiplet_name}_{test.get_test_type()}_Col{col[0]}_Row{row[0]}.xlsx')
        data = pd.read_excel(os.path.normpath(file_path))
        HRS = find_HRS(data)
        LRS = find_LRS(data)
        avg_HRS.append(np.mean(HRS))
        avg_LRS.append(np.mean(LRS))
        std_HRS.append(np.std(HRS))
        std_LRS.append(np.std(LRS))
        med_HRS.append(np.median(HRS))
        med_LRS.append(np.median(LRS))
        Percent_75_HRS.append(np.percentile(HRS,75))
        Percent_75_LRS.append(np.percentile(LRS,75))
        Percent_25_HRS.append(np.percentile(HRS,25))
        Percent_25_LRS.append(np.percentile(LRS,25))
        Upper_Range_HRS.append(np.percentile(HRS,25)-1.5*(np.percentile(HRS,75)-np.percentile(HRS,25)))
        Lower_Range_HRS.append(np.percentile(HRS,75)+1.5*(np.percentile(HRS,75)-np.percentile(HRS,25)))
        Upper_Range_LRS.append(np.percentile(LRS,25)-1.5*(np.percentile(LRS,75)-np.percentile(LRS,25)))
        Lower_Range_LRS.append(np.percentile(LRS,75)+1.5*(np.percentile(LRS,75)-np.percentile(LRS,25)))
        if(isinstance(test,tests.IVTest)):
            setVolt, resetVolt = find_set_reset(data)
            setV.append(setVolt)
            resetV.append(resetVolt)
            avg_setVolt.append(np.mean(setVolt))
            avg_resetVolt.append(np.mean(resetVolt))
            std_setVolt.append(np.std(setVolt))
            std_resetVolt.append(np.std(resetVolt))
            med_setVolt.append(np.median(setVolt))
            med_resetVolt.append(np.median(resetVolt))
            Percent_75_setVolt.append(np.percentile(setVolt,75))
            Percent_75_resetVolt.append(np.percentile(resetVolt,75))
            Percent_25_setVolt.append(np.percentile(setVolt,25))
            Percent_25_resetVolt.append(np.percentile(resetVolt,25))
            Upper_Range_setVolt.append(np.percentile(setVolt,25)-1.5*(np.percentile(setVolt,75)-np.percentile(setVolt,25)))
            Lower_Range_setVolt.append(np.percentile(setVolt,75)+1.5*(np.percentile(setVolt,75)-np.percentile(setVolt,25)))
            Upper_Range_resetVolt.append(np.percentile(resetVolt,25)-1.5*(np.percentile(resetVolt,75)-np.percentile(resetVolt,25)))
            Lower_Range_resetVolt.append(np.percentile(resetVolt,75)+1.5*(np.percentile(resetVolt,75)-np.percentile(resetVolt,25)))
        elif(isinstance(test,tests.EnduranceTest)):
            setV.append(None)
            resetV.append(None)
            avg_setVolt.append(None)
            avg_resetVolt.append(None)
            std_setVolt.append(None)
            std_resetVolt.append(None)
            med_setVolt.append(None)
            med_resetVolt.append(None)
            Percent_75_setVolt.append(None)
            Percent_75_resetVolt.append(None)
            Percent_25_setVolt.append(None)
            Percent_25_resetVolt.append(None)
            Upper_Range_setVolt.append(None)
            Lower_Range_setVolt.append(None)
            Upper_Range_resetVolt.append(None)
            Lower_Range_resetVolt.append(None)
    df['ChipName']=Chipname
    df['Row'] = row
    df['Col'] = col 
    df['TestType'] = test_type
    df['Vset'] = setV
    df['Vreset'] = resetV
    df['Avg. HRS'] = avg_HRS
    df['Avg. LRS'] = avg_LRS
    df['Std_Dev_HRS'] = std_HRS
    df['Std_Dev_LRS'] = std_LRS
    df['Med. HRS'] = med_HRS
    df['Med. LRS'] = med_LRS
    df['HRS 1.5IQR Upper'] = Upper_Range_HRS
    df['LRS 1.5IQR Upper'] = Upper_Range_LRS
    df['HRS 1.5IQR Lower'] = Lower_Range_HRS
    df['LRS 1.5IQR Lower'] = Lower_Range_LRS
    df['Avg. Vset'] = avg_setVolt
    df['Avg. Vreset'] = avg_resetVolt
    df['Std_Dev_Vset'] = std_setVolt
    df['Std_Dev_Vreset'] = std_resetVolt
    df['Med. Vset'] = med_setVolt
    df['Med. Vreset'] = med_resetVolt
    df['Vset 1.5IQR Upper'] = Upper_Range_setVolt
    df['Vreset 1.5IQR Upper'] = Upper_Range_resetVolt
    df['Vset 1.5IQR Lower'] = Lower_Range_setVolt
    df['Vreset 1.5IQR Lower'] = Lower_Range_resetVolt
    if(os.path.exists(filename)):
        df = pd.concat([pd.read_excel(filename),df])
        df.to_excel(filename,index=False)
        print(df)
    else:
        df.to_excel(filename,index=False)
def calc_IQR(data):
    IQR = np.percentile(data,75)-np.percentile(data,25)
    return IQR
sm = SourceMeter()
sm.run_test()
sm.create_excel_sheets()
sm.run_post_test_gui()
