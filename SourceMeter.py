import pyvisa
import csv
import matplotlib.pyplot as plt
import gui
import microserial
import functions
import numpy as np
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
        self._instrument = rm.open_resource('GPIB0::24::INSTR')  # Name of sourcemeter

        # Call GUI
        self._gui = gui.GUI()
        self._gui.gui_start()

        # Create place to store collected data
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
            message_micro(vals["gen_device_x"], vals["gen_device_y"])
            match test:
                case "IV Test":
                    # Chooses what test to run and collects data
                    if (vals["iv_space"] == 'LIN'):
                        self._measurements.append(functions.Staircase_Lin(
                            instrument=self._instrument,
                            is_up_down=vals["iv_is_up_down"],
                            current_compliance=vals["iv_current_compliance"],
                            source_voltage=vals["iv_source_voltage"],
                            source_delay=vals["iv_source_delay"],
                            source_voltage_start=vals["iv_source_voltage_start"],
                            source_voltage_stop=vals["iv_source_voltage_stop"],
                            log_num_steps=vals["iv_log_num_steps"],
                            trig_count=vals["iv_trig_count"]
                            )
                        )
                    elif (vals["iv_space"] == 'LOG'):
                        self._measurements.append(functions.Staircase_Log(
                            instrument=self._instrument,
                            is_up_down=vals["iv_is_up_down"],
                            current_compliance=vals["iv_current_compliance"],
                            source_voltage=vals["iv_source_voltage"],
                            source_delay=vals["iv_source_delay"],
                            source_voltage_start=vals["iv_source_voltage_start"],
                            source_voltage_stop=vals["iv_source_voltage_stop"],
                            log_num_steps=vals["iv_log_num_steps"],
                            trig_count=vals["iv_trig_count"]
                            )
                        )
                    # elif (saved_vals["source_sweep_space"] == 'CUST'):
                    #     measure_up = functions.Staircase_custom()
                case "Forming Pulse":
                    print("Test not yet implemented")
                case "Endurance Test":
                    print("Test not yet implemented")
                case _:
                    print("Invalid test type selected, how'd you manage that?")

    def read_values(self):
        '''
        Pull values from json file for tests
        Returns dict of values from GUI
        '''
        with open('values.json', 'r') as openfile:
            saved_vals = functions.json.load(openfile)

        return saved_vals

    def data_breakout(self):
        '''
        Takes data collected from tests and separates the different values for
        easier graphing
        '''
        for data_string in self._measurements:
            values = data_string.split(",")
            temp_voltage = []
            temp_current = []
            temp_resistance = []
            temp_time = []
            temp_status = []
            for i in range(0, len(values), 5):
                temp_voltage.append(float(values[i].strip()))
                temp_current.append(float(values[i+1].strip()))
                temp_resistance.append(float(values[i+2].strip()))
                temp_time.append(float(values[i+3].strip()))
                temp_status.append(values[i+4].strip())
            
            first_time = temp_time[0]
            temp_time = temp_time - first_time

            self._voltage.append(temp_voltage)
            self._current.append(temp_current)
            self._resistance.append(temp_resistance)
            self._timestamp.append(temp_time)
            self._status_word.append(temp_status)
            self._true_resistance.append(np.divide(temp_voltage,temp_current))

    def print_all_vals(self):
        '''
        
        '''
        #TODO: Make do what a normal person would expect
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
                case "Forming Pulse":
                    test_type += "Forming_"
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
            ## For James' computer if on another computer this becomes irrelevant
            # folder_path = rf"C:\Users\James\OneDrive\Desktop\SunyPoly\{date}"
            filename = f'*/SavedData/{vals["gen_chiplet_name"]}_Row{vals["gen_device_y"]}_Col{ \
                        vals["gen_device_x"]}_{test}_{vals["test_start_time"]}'
            filenames.append(filename)
        return filenames

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
                    "Timestamp", "Status Word","Calc Resistance"]
            # Combine the arrays into a list of rows
            rows = zip(self._voltage[i], self._current[i], self._resistance[i],
                    self._timestamp[i], self._status_word[i], self._true_resistance[i])
            # Open the CSV file and write the headers
            with open(filename, "w", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers)
                # Write each row to the CSV file
                writer.writerows(rows)

    def plot_tests(self):
        filenames = self.write_file_names()
        for i in range(len(filenames)):
            vals = self.read_values()
            # Add .png to the filename
            filename = filenames[i] + ".png"
            
            # Create IV graph
            fig, ax = plt.subplots()
            ax.plot(self._voltage[i], self._current[i], color='b')
            plt.xlabel('Voltage')
            plt.ylabel('Current')
            plt.title(f'IV Plot Row:{vals["gen_device_y"]} Col:{vals["gen_device_x"]}')
            ax.grid(True, linestyle='--', linewidth=0.5)
            ax.legend(['IV Plot'], loc='best')
            ax.ticklabel_format(style='sci', axis='both', scilimits=(0, 0))
            plt.margins(0.1)
            plt.tight_layout()
            plt.savefig(filename)

            # Create R over time graph
            plt.show()
            plt.figure()
            plt.plot(self._timestamp[i], self._true_resistance[i])
            plt.xlabel('Time')
            plt.ylabel('Resistance')
            plt.title('Resistance vs. Time')
            plt.grid(True)
            plt.show()

def message_micro(x, y):
    '''
    Sends a 21 byte long datastream to microcontroller containing the xy
    coords of the device we are attempting to work with
    '''
    data_stream = [0]*21
    # Creates 21 byte long data stream where the first and last values are
    # 0x80 and 0x81 respectively and the second and third to last spots are
    # the  row and columns and the rest are 0
    data_stream = functions.create_data_stream(x, y)
    # print(data_stream)
    # Uncomment when trying to send information to the PCB
    microserial.serialExecution(data_stream) #TEMP: removed output because comms is currently one way
    # print(output)

sm = SourceMeter()
sm.run_test()
sm.data_breakout()
sm.save_to_csv()
sm.plot_tests()
