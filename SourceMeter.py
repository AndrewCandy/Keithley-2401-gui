import pyvisa
import csv
import matplotlib.pyplot as plt
import gui
import json
import os
from datetime import datetime
import time
import itertools


## Test and features to add: 
# Forming Pulse
# Limits to each variable are as follows: When in Lin Voltage: 0-3.5V, Current:0-1A, 
# trig_count:should be very large, step: should be very small,delay should be very small micro or nano seconds
# When working with Log: Voltage:Cant start at 0 and same stopping point, Current same thing, 
# Points: very large number, same with trig_count. 
# When working with custom: a list of values is needed to tell what amplitude pulse to send out. 
# Forming pulse ~3.3-3.5V for a very short time (delay should be very small). 
# Trig_count is dependent on how many pulses u want. =numofpulses*2
#### More limits: For log function trig count and points need to be the same number but for linear 
# trig count-2 = stop_voltage/step. or Step = stop_voltage/trig_count. Need larger scale for trig count 100 not enough
##Creating device and accepting inputs from the GUI
rm = pyvisa.ResourceManager()
print(rm.list_resources())
instrument = rm.open_resource('GPIB0::24::INSTR')  # Name of sourcemeter
with open('values.json', 'r') as openfile:
    saved_vals = json.load(openfile)
column = saved_vals["device_x"]
row = saved_vals["device_y"]
data_stream = [0]*20
def create_data_stream():
    for i in range(1,20):
        if(i == 18):
            data_stream[i] = column
        elif(i==19):
            data_stream[i] = row
    return data_stream
##Test types
def Staircase_Lin():
    instrument.timeout = 10000
    instrument.write("SYST:REM")
    instrument.write('*RST')
    instrument.write(f':SENS:CURR:PROT {saved_vals["current_compliance"]}')
    instrument.write(f':SOUR:VOLT {saved_vals["source_voltage"]}')
    instrument.write(f':SOUR:DEL {saved_vals["source_delay"]}')
    instrument.write(':SOUR:SWE:RANG BEST')
    instrument.write(':SOUR:VOLT:MODE SWE')
    instrument.write(':SOUR:SWE:SPAC LIN')
    instrument.write(f':SOUR:VOLT:STAR {saved_vals["source_voltage_start"]}')
    instrument.write(f':SOUR:VOLT:STOP {saved_vals["source_voltage_stop"]}')
    instrument.write(f':SOUR:VOLT:STEP {saved_vals["source_voltage_step"]}')
    instrument.write(f':TRIG:COUN {saved_vals["trig_count"]}')
    instrument.write(':OUTP ON')
    measure_up = instrument.query(':READ?')
    print("Measure_up"+measure_up)
    if ((saved_vals["is_up_down"])):
        instrument.write('*RST')
        instrument.write(f':SENS:CURR:PROT {saved_vals["current_compliance"]}')
        instrument.write(f':SOUR:VOLT {saved_vals["source_voltage_stop"]}')
        instrument.write(f':SOUR:DEL {saved_vals["source_delay"]}')
        instrument.write(':SOUR:SWE:RANG BEST')
        instrument.write(':SOUR:VOLT:MODE SWE')
        instrument.write(':SOUR:SWE:SPAC LIN')
        instrument.write(f':SOUR:VOLT:STAR {saved_vals["source_voltage_stop"]}')
        instrument.write(f':SOUR:VOLT:STOP {saved_vals["source_voltage_start"]}')
        instrument.write(f':SOUR:VOLT:STEP {saved_vals["source_voltage_step"]*-1}')
        instrument.write(f':TRIG:COUN {saved_vals["trig_count"]}')
        instrument.write(':OUTP ON')
        measure_down = instrument.query(':READ?')
        print("Measure_down" + measure_down)
        return measure_up, measure_down
    else:
        return measure_up
##When working with log source voltage cannot be 0
def Staircase_Log():
    instrument.timeout = 10000
    instrument.write("SYST:REM")
    instrument.write('*RST')
    instrument.write(f':SENS:CURR:PROT {saved_vals["current_compliance"]}')
    instrument.write(f':SOUR:VOLT {saved_vals["source_voltage"]}')
    instrument.write(f':SOUR:DEL {saved_vals["source_delay"]}')
    instrument.write(':SOUR:SWE:RANG BEST')
    instrument.write(':SOUR:VOLT:MODE SWE')
    instrument.write(':SOUR:SWE:SPAC LOG')
    instrument.write(f':SOUR:VOLT:STAR {saved_vals["source_voltage_start"]}')
    instrument.write(f':SOUR:VOLT:STOP {saved_vals["source_voltage_stop"]}')
    instrument.write(f':SOUR:SWE:POIN {saved_vals["log_num_steps"]}')
    instrument.write(f':TRIG:COUN {saved_vals["trig_count"]}')
    instrument.write(':OUTP ON')
    measure_up = instrument.query(':READ?')
    print(measure_up)
    if ((saved_vals["is_up_down"])):
        instrument.write('*RST')
        instrument.write(f':SENS:CURR:PROT {saved_vals["current_compliance"]}')
        instrument.write(f':SOUR:VOLT {saved_vals["source_voltage_stop"]}')
        instrument.write(f':SOUR:DEL {saved_vals["source_delay"]}')
        instrument.write(':SOUR:SWE:RANG BEST')
        instrument.write(':SOUR:VOLT:MODE SWE')
        instrument.write(':SOUR:SWE:SPAC LOG')
        instrument.write(f':SOUR:VOLT:STAR {saved_vals["source_voltage_stop"]}')
        instrument.write(f':SOUR:VOLT:STOP {saved_vals["source_voltage_start"]}')
        instrument.write(f':SOUR:SWE:POIN {saved_vals["log_num_steps"]}')
        instrument.write(f':TRIG:COUN {saved_vals["trig_count"]}')
        instrument.write(':OUTP ON')
        measure_down = instrument.query(':READ?')
        print(measure_down)
        return measure_up, measure_down
    else:
        return measure_up
## variables to grab from GUI: list of voltages
def Staircase_custom():
    # Define the voltage values for the staircase pattern
    voltage_values = [3.5, 0]  # Enter the two voltage values here

    # Define the number of repetitions
    num_repetitions = 5  # Specify the desired number of repetitions

    # Generate the repeated staircase pattern
    voltage = list(itertools.islice(itertools.cycle(voltage_values), num_repetitions))

    # Print the generated voltage values
    print(voltage)
    instrument.timeout = 10000
    instrument.write("SYST:REM")
    instrument.write('*RST')
    instrument.write(f':SENS:CURR:PROT {saved_vals["current_compliance"]}')
    instrument.write(f':SOUR:VOLT {saved_vals["source_voltage"]}')
    instrument.write('SOUR:SWE:RANG BEST')
    instrument.write('SOUR:VOLT:MODE LIST')
    instrument.write('SOUR:LIST:VOLT 3.5,0')
    instrument.write(f':TRIG:COUN {saved_vals["trig_count"]}')
    instrument.write('OUTP ON')
    instrument.query(':READ?')

data_stream = create_data_stream()
print(data_stream)

#Chooses what test to run and collects data
if (saved_vals["source_sweep_space"] == 'LIN'):
    if ((saved_vals["is_up_down"])):
        measure_up, measure_down = Staircase_Lin()
    else:
        measure_up = Staircase_Lin()
elif (saved_vals["source_sweep_space"] == 'LOG'):
    if ((saved_vals["is_up_down"])):
        measure_up, measure_down = Staircase_Log()
    else:
        measure_up = Staircase_Log()
elif (saved_vals["source_sweep_space"]=='CUST'):
    #When custom need to decide how many times the pulse will be active and what values they will be going to 
    measure_up = Staircase_custom()
# Initialize arrays to store the values
voltage = []
current = []
resistance = []
timestamp = []
status_word = []
# Function to add values to the arrays
def add_values_to_arrays(data_string):
    values = data_string.split(",")
    for i in range(0, len(values),5):
        voltage.append(float(values[i].strip()))
        current.append(float(values[i+1].strip()))
        resistance.append(float(values[i+2].strip()))
        timestamp.append(values[i+3].strip())
        status_word.append(values[i+4].strip())
# Chooses what type of staircase its working with and saves data into respective arrays
if (saved_vals["source_sweep_space"] == 'LIN'):
    if (saved_vals["is_up_down"]):
        add_values_to_arrays(measure_up)
        add_values_to_arrays(measure_down)
        testType = 'Linear Double Staircase'
    else:
        add_values_to_arrays(measure_up)
        testType = 'Linear Single Staircase'
elif (saved_vals["source_sweep_space"] == 'LOG'):
    if (saved_vals["is_up_down"]):
        add_values_to_arrays(measure_up)
        add_values_to_arrays(measure_down)
        testType = 'Logarithmic Double Staircase'
    else:
        add_values_to_arrays(measure_up)
        testType = 'Logarithmic Single Staircase'
# Print the values
print("Voltage:", voltage)
print("Current:", current)
print("Resistance:", resistance)
print("Timestamp:", timestamp)
print("Status Word:", status_word)


def arrays_to_csv(filename):
    # Create a list of headers for each column
    headers = ["Voltage", "Current", "Resistance",
               "Timestamp", "Status Word"]

    # Combine the arrays into a list of rows
    rows = zip(voltage, current, resistance, timestamp, status_word)

    # Open the CSV file and write the headers
    with open(filename, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        # Write each row to the CSV file
        writer.writerows(rows)
##Need to collect which columns and rows were selected

date = datetime.now().strftime("%m%d%Y")
folder_path = rf"C:\Users\James\OneDrive\Desktop\SunyPoly\{date}"
timestart = saved_vals["test_start_time"]
chiplet_name = saved_vals["chiplet_name"]
column = saved_vals["device_x"]
row = saved_vals["device_y"]
if os.path.exists(folder_path):
    output = os.path.join(folder_path, f'Chip{chiplet_name}_Row{row}_Col{column}_{testType}_{timestart}.csv')
    
else:
    output = f'Chip{chiplet_name}_Row{row}_Col{column}_{testType}_{timestart}.csv'
# Call the function to write the arrays to a CSV file
print(data_stream)
arrays_to_csv(output)
fig, ax = plt.subplots()
ax.plot(voltage, current, color='b')
# Set x-axis and y-axis labels
plt.xlabel('Voltage')
plt.ylabel('Current')
# Set plot title
plt.title(f'IV Plot Row:{row} Col:{column} ' + testType)
# Set grid lines
ax.grid(True, linestyle='--', linewidth=0.5)
# Add legend
ax.legend(['IV Plot'], loc='best')
# Set the tick label format to scientific notation for both x-axis and y-axis
ax.ticklabel_format(style='sci', axis='both', scilimits=(0, 0))
# Set plot margins
plt.margins(0.1)
# Display the plot
plt.tight_layout()
plt.show()