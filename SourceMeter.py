import pyvisa
import csv
import matplotlib.pyplot as plt
import math
import gui
import microserial
import functions
import numpy as np
import pandas as pd
import xlwings as xw
import os
from openpyxl import load_workbook
from openpyxl import Workbook
from openpyxl.cell import WriteOnlyCell
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.utils import FORMULAE
# Test and features to add:
# Forming Pulse, Endurance Test
# Limits to each variable are as follows: When in Lin Voltage: 0-3.5V, Current:0-1A,
# trig_count:should be very large, step: should be very small,delay should be very small micro or nano seconds
# When working with Log: Voltage:Cant start at 0 and same stopping point, Current same thing,
# Points: very large number, same with trig_count.
# When working with custom: a list of values is needed to tell what amplitude pulse to send out.
# Forming pulse ~3.3-3.5V for a very short time (delay should be very small).
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
        self._repitions = 2
        self._measurements = []
        self._voltage = []
        self._current = []
        self._resistance = []
        self._timestamp = []
        self._status_word = []
        self._true_resistance = []

    def run_test(self):
        '''
        Run all tests requested by the GUI
        Commands to be sent to the source meter are written out in functions.py
        values are passed through from GUI to source meter commands
        '''
        testList = self._gui.requested_tests()
        # Check to make sure at least one test has been requested
        if len(testList) == 0:
            return

        # if test(s) have been requested, execute them
        vals = self.read_values()
        for test in testList:
            # Tell microcontroller what device we are targeting
            # microserial.message_micro(vals["gen_device_x"], vals["gen_device_y"])
            match test:
                case "IV Test":
                    # Chooses what test to run and collects data
                    if (vals["iv_space"] == 'LIN'):
                        vals['iv_log_num_steps'] = ''
                        trig_Count = functions.calcTrigCount(vals['iv_source_voltage_stop'],
                                                             vals['iv_source_voltage_start'],
                                                             vals['iv_source_voltage_step'],
                                                             vals['iv_log_num_steps'],
                                                             vals['iv_space'])
                        self._measurements.append(functions.Staircase_Lin(
                            instrument=self._instrument,
                            is_up_down=vals["iv_is_up_down"],
                            full_cycle=vals["iv_full_cycle"],
                            current_compliance=vals["iv_current_compliance"],
                            source_voltage=vals["iv_source_voltage"],
                            source_delay=vals["iv_source_delay"],
                            source_voltage_start=vals["iv_source_voltage_start"],
                            source_voltage_stop=vals["iv_source_voltage_stop"],
                            source_voltage_step=vals["iv_source_voltage_step"],
                            trig_count=math.floor(trig_Count)
                        )
                        )
                    elif (vals["iv_space"] == 'LOG'):
                        vals['iv_source_voltage_step'] = ''
                        trig_Count = functions.calcTrigCount(vals['iv_source_voltage_stop'],
                                                             vals['iv_source_voltage_start'],
                                                             vals['iv_source_voltage_step'],
                                                             vals['iv_log_num_steps'],
                                                             vals['iv_space'])
                        self._measurements.append(functions.Staircase_Log(
                            instrument=self._instrument,
                            is_up_down=vals["iv_is_up_down"],
                            current_compliance=vals["iv_current_compliance"],
                            source_voltage=vals["iv_source_voltage"],
                            source_delay=vals["iv_source_delay"],
                            source_voltage_start=vals["iv_source_voltage_start"],
                            source_voltage_stop=vals["iv_source_voltage_stop"],
                            log_num_steps=vals["iv_log_num_steps"],
                            trig_count=math.floor(trig_Count)
                        )
                        )
                case "Endurance Test":
                    self._voltage_list = functions.create_voltage_list(
                        set_voltage=vals["set_voltage"],
                        read_voltage=vals["read_voltage"],
                        reset_voltage=vals["reset_voltage"],
                        cycles=vals["et_cycles"]
                    )
                    for i in range(0, vals["et_cycles"], 5):
                        self._measurements.append(functions.endurance_Test(
                            instrument=self._instrument,
                            current_compliance=vals["iv_current_compliance"],
                            source_voltage=vals["iv_source_voltage"],
                            source_delay=vals["iv_source_delay"],
                            voltage_list=self._voltage_list,
                            list_length=vals["et_cycles"]*8
                        )
                        )
                        print(i)
                case _:
                    print("Invalid test type selected, how'd you manage that?")

    def read_values(self):
        '''
        Pull values from json file for tests
        Returns dict of values from GUI
        '''
        with open('values.json', 'r') as openfile:
            saved_vals = gui.json.load(openfile)

        return saved_vals

    def create_dataframe(self, run_num):
        measurements = self._measurements[run_num].split(',')
        # Reshape the measurements into a 2D array with 5 columns
        reshaped_values = np.reshape(measurements, (-1, 5))
        # Create a DataFrame with the reshaped values and column names
        df_new = pd.DataFrame(reshaped_values, columns=[
                              'Voltage', 'Current', 'Resistance', 'TimeStamp', 'Status'])
        print(df_new.head())
        return df_new

    def manipulateDf(self, name, run_num):
        df = self.create_dataframe(run_num)
        print(df.shape)
        print(df.info())
        df['Voltage'] = df['Voltage'].str.strip().str.strip("['").str.rstrip("'")
        df['Status'] = df['Status'].str.rstrip("']")
        df['Voltage'] = pd.to_numeric(df['Voltage'])
        df['Current'] = pd.to_numeric(df['Current'])
        df['Resistance'] = pd.to_numeric(df['Resistance'])
        df['TimeStamp'] = pd.to_numeric(df['TimeStamp'])
        df['Status'] = pd.to_numeric(df['Status'])
        self._voltage = df['Voltage']
        self._current = df['Current']
        self._resistance = df['Resistance']
        self._timestamp = df['TimeStamp']
        self._status = df['Status']
        print(df.info())

        df.to_excel(name,index=False)
        sheet_name = "xlwings_option"
        df_mapping = {"A1": df, "H1": df.describe()}
        with xw.App(visible=False) as app:
            wb = app.books.open(name)

            # Add sheet if it does not exist
            current_sheets = [sheet.name for sheet in wb.sheets]
            if sheet_name not in current_sheets:
                wb.sheets.add(sheet_name)

            # Write dataframe to cell range
            for cell_target, df in df_mapping.items():
                wb.sheets(sheet_name).range(cell_target).options(
                    pd.DataFrame, index=True).value = df

            wb.save()

    def excelCalculations(self):
        run_num = 0
        wb_names = self.write_file_names()
        test_types = self._gui.requested_tests()
        for name in wb_names:
            print(name)
            self.manipulateDf(name, run_num)
            sheet_name = "xlwings_option"
            df = pd.read_excel(name)
            df_new = df['Voltage'] / df['Current']
            df_new = df_new.apply(lambda x: f"{x:.2e}")
            header = ["Real Resistance"]
            df_new = pd.DataFrame({header[0]: df_new})
            df_mapping = {"G1": df_new}
            with xw.App(visible=False) as app:
                wb = app.books.open(name)

                # Add sheet if it does not exist
                current_sheets = [sheet.name for sheet in wb.sheets]
                if sheet_name not in current_sheets:
                    wb.sheets.add(sheet_name)

                # Write dataframe to cell range
                for cell_target, df in df_mapping.items():
                    wb.sheets(sheet_name).range(cell_target).options(
                        pd.DataFrame, index=False).value = pd.DataFrame(df_new)
                wb.save()
            print(test_types[run_num])
            df_full = pd.read_excel(name)
            print(df_full.columns)
            vals = self.read_values()
            match test_types[run_num]:
                
                case "IV Test":
                    #We need to find set and reset voltages
                    column_name = 'Current'
                    reset=False
                    largest_diff_set = self.find_largest_difference(df_full,column_name,reset)
                    print(largest_diff_set)
                    self.add_integer_to_excel(name, sheet_name,'I11','Largest_Current_Diff_Set',largest_diff_set)
                    reset=True
                    largest_diff_reset = self.find_largest_difference(df_full,column_name,reset)
                    print(largest_diff_reset)
                    self.add_integer_to_excel(name, sheet_name,'J11','Largest_Current_Diff_Reset',largest_diff_reset)
                case "Endurance Test":
                    #we need to find avg HRS and LRS
                    print('hi')
                    HRS = self.find_HRS(df_full,reset_voltage=vals["reset_voltage"])
                    print(HRS)
                    LRS = self.find_LRS(df_full, set_voltage=vals['set_voltage'])
                    print(LRS)
                case _:
                    #You done goofed
                    print('hey')
            run_num += 1
    def find_HRS(self,df,reset_voltage):
        voltage = df['Voltage']
        resistance = df['Real Resistance']
        print(reset_voltage)
        HRS = []
        for i in range(1,len(voltage)):
            if(voltage[i]==reset_voltage):
                print(len(resistance))
                print(i+2)
                HRS.append(resistance[i+2])
        return HRS
    def find_LRS(self,df,set_voltage):
        voltage = df['Voltage']
        resistance = df['Real Resistance']
        print(set_voltage)
        LRS = []
        for i in range(0,len(voltage)):
            if(voltage[i]==set_voltage):
                print(len(resistance))
                print(i+2)
                LRS.append(resistance[i+2])
        return LRS
    def find_largest_difference(self, df, column_name,reset):
        # Get the column as a Series
        column = df[column_name]
        largest_difference_set = None
        largest_difference_reset = None
        # Iterate through the column values
        if(reset==False):
            for voltages in self._voltage:
                if(voltages>=0):
                    print(voltages)
                    for i in range(1, len(column)):
                        difference = abs(column[i] - column[i-1])
                        # Update the largest difference if necessary
                        if largest_difference_set is None or difference > largest_difference_set:
                            largest_difference_set = difference
            return largest_difference_set
        else:
            for voltages in self._voltage:
                if(voltages<0):
                    print(voltages)
                    for i in range(1, len(column)):
                        difference = abs(column[i] - column[i-1])
                        # Update the largest difference if necessary
                        if largest_difference_reset is None or difference > largest_difference_reset:
                            largest_difference_reset = difference
            return largest_difference_reset
         
    def add_integer_to_excel(self,file_name, sheet_name, cell_target, header, value):
        with xw.App(visible=False) as app:
            wb = app.books.open(file_name)
            sheet = wb.sheets[sheet_name]
            
            # Write the header
            sheet.range(cell_target).value = header
            
            # Write the value below the header
            sheet.range(cell_target).offset(row_offset=1).value = value
            
            # Save and close the workbook
            wb.save()    
        """def data_breakout(self):
        '''
        Takes data collected from tests and separates the different values for
        easier graphing
        '''
        for data_string in self._measurements:
            for i in range(len(data_string)):
                values = data_string.split(",")
                temp_voltage = []
                temp_current = []
                temp_resistance = []
                time_stamp = []
                temp_status = []
                temp_time = []
                for i in range(0, len(values), 5):
                    temp_voltage.append(float(values[i].strip()))
                    temp_current.append(float(values[i+1].strip()))
                    temp_resistance.append(float(values[i+2].strip()))
                    time_stamp.append(float(values[i+3].strip()))
                    temp_status.append(values[i+4].strip())

        first_time = float(time_stamp[0])
        for element in time_stamp:
            current_time = float(element) - first_time
            temp_time.append(current_time)

            self._voltage.append(temp_voltage)
            self._current.append(temp_current)
            self._resistance.append(temp_resistance)
            self._timestamp.append(temp_time)
            self._status_word.append(temp_status)
            self._true_resistance.append(np.divide(temp_voltage,temp_current))
"""

    def print_all_vals(self):
        '''

        '''
        # TODO: Make do what a normal person would expect
        print("Voltage:", self._voltage)
        print("Current:", self._current)
        print("Resistance:", self._resistance)
        print("Timestamp:", self._timestamp)
        print("Status Word:", self._status_word)
        print("True_Resistance: ", self._true_resistance)

    def write_test_types(self):
        '''
        Returns:
            a list of strings describing conducted tests to be used in making file names
        '''
        test_types = []
        testList = self._gui.requested_tests()
        for test in testList:
            # Create test name for file naming
            test_type = ""
            vals = self.read_values()
            match test:
                case "IV Test":
                    # Lin or log
                    if vals["iv_space"] == 'LIN':
                        test_type += "Linear_"
                    elif vals["iv_space"] == 'LOG':
                        test_type += "Logarithmic_"
                    # Single or double staircase
                    if vals["iv_is_up_down"]:
                        test_type += "Double_"
                    else:
                        test_type += "Single_"
                    # Show it was an IV
                    test_type += "Staircase_IV_"
                case "Endurance Test":
                    test_type += "Endurance_"
                case _:
                    test_type += "Unknown_Test_"
            test_types.append(test_type)
        return test_types

    def write_file_names(self):
        '''
        Returns:
            A list of full filenames for saving files
        '''
        filenames = []
        test_types = self.write_test_types()
        for test in test_types:
            vals = self.read_values()
            # Create the filename
            home_dir = os.path.abspath(__file__)
            current_directory = os.path.dirname(home_dir)
            folder_path = os.path.join(current_directory,"SavedData\Runs")
            print(folder_path)
            os.makedirs(folder_path, exist_ok=True)
            file_path = f'{folder_path}\{vals["gen_chiplet_name"]}_Row{vals["gen_device_y"]}_Col{vals["gen_device_x"]}_{test}_{vals["test_start_time"]}.xlsx'
            print(file_path)
            filenames.append(file_path)
        return filenames
    """
    def save_to_csv(self):
        '''
        Saves data from each test in a csv file
        '''
        filenames = self.write_file_names()
        for i in range(len(filenames)):
            vals = self.read_values()
            # Add .csv to the filename
            filename = filenames[i] + ".csv"

            # Create a list of headers for each column
            headers = ["Voltage", "Current", "Resistance",
                       "Timestamp", "Status Word", "Calc Resistance"]
            # Combine the arrays into a list of rows
            rows = zip(self._voltage[i], self._current[i], self._resistance[i],
                       self._timestamp[i], self._status_word[i], self._true_resistance[i])
            # Open the CSV file and write the headers
            with open(filename, "w", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers)
                # Write each row to the CSV file
                writer.writerows(rows)"""

    def plot_tests(self):
        filenames = self.write_file_names()
        for i in range(len(filenames)):
            vals = self.read_values()
            # Add .png to the filename
            voltage = self._voltage.to_list()
            current = self._current.to_list()
            # Create IV graph
            fig, ax = plt.subplots()
            ax.plot(voltage, current, color='b')
            plt.xlabel('Voltage')
            plt.ylabel('Current')
            plt.title(
                f'IV Plot Row:{vals["gen_device_y"]} Col:{vals["gen_device_x"]}')
            ax.grid(True, linestyle='--', linewidth=0.5)
            ax.legend(['IV Plot'], loc='best')
            ax.ticklabel_format(style='sci', axis='both', scilimits=(0, 0))
            plt.margins(0.1)
            plt.tight_layout()
            plt.show()
            # Create I over time graph
            """plt.show()
            plt.figure()
            plt.plot(self._timestamp[i], self._current[i])
            plt.xlabel('Time')
            plt.ylabel('Current')
            plt.title('Current vs. Time')
            plt.grid(True)
            plt.show()"""


'''def message_micro(x, y):
    
    #Sends a 21 byte long datastream to microcontroller containing the xy
    #coords of the device we are attempting to work with
    
    data_stream = [0]*21
    # Creates 21 byte long data stream where the first and last values are
    # 0x80 and 0x81 respectively and the second and third to last spots are
    # the  row and columns and the rest are 0
    data_stream = functions.create_data_stream(x, y)
    # print(data_stream)
    # Uncomment when trying to send information to the PCB
    output = microserial.serialExecution(data_stream)
    # print(output)
'''
sm = SourceMeter()
sm.run_test()
# sm.data_breakout()
# sm.manipulateDf()
sm.excelCalculations()
sm.plot_tests()
