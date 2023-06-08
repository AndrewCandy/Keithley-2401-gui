import pyvisa
import csv
import matplotlib.pyplot as plt
import os
from datetime import datetime
import time
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

rm = pyvisa.ResourceManager()
print(rm.list_resources())
instrument = rm.open_resource('GPIB0::24::INSTR')  # Name of sourcemeter
with open('values.json', 'r') as openfile:
    saved_vals = functions.json.load(openfile)
column = saved_vals["device_x"]
row = saved_vals["device_y"]

data_stream = [0]*21
# Creates 21 byte long data stream where the first and last values are 0x80 and 0x81 respectively 
# and the second and third to last spots are the  row and columns and the rest are 0
data_stream = functions.create_data_stream()
print(data_stream)
# Uncomment when trying to send information to the PCB
output = microserial.serialExecution(data_stream)
print(output)

# Chooses what test to run and collects data
if (saved_vals["source_sweep_space"] == 'LIN'):
    if ((saved_vals["is_up_down"])):
        measure_up, measure_down = functions.Staircase_Lin()
    else:
        measure_up = functions.Staircase_Lin()
elif (saved_vals["source_sweep_space"] == 'LOG'):
    if ((saved_vals["is_up_down"])):
        measure_up, measure_down = functions.Staircase_Log()
    else:
        measure_up = functions.Staircase_Log()
elif (saved_vals["source_sweep_space"] == 'CUST'):
    measure_up = functions.Staircase_custom()

# Initialize arrays to store the values
voltage = []
current = []
resistance = []
timestamp = []
status_word = []
true_resistance = []

# Function to add values to the arrays
def add_values_to_arrays(data_string):
    values = data_string.split(",")
    for i in range(0, len(values), 5):
        voltage.append(float(values[i].strip()))
        current.append(float(values[i+1].strip()))
        resistance.append(float(values[i+2].strip()))
        timestamp.append(values[i+3].strip())
        status_word.append(values[i+4].strip())


# Chooses what type of test its working with and saves data into respective arrays
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

#Calculates the resitance at every point
true_resistance = np.divide(voltage, current)

#Calculates the time of each data point starting at 0
time = []
first_time = float(timestamp[0])
for element in timestamp:
    current_time = float(element) - float(timestamp[0])
    time.append(current_time)

# Print the values
print("Voltage:", voltage)
print("Current:", current)
print("Resistance:", resistance)
print("Timestamp:", timestamp)
print("Status Word:", status_word)
print('Time: ', time)
print("True_Resistance: ", true_resistance)

# Function that sends pre created arrays to .csv file
def arrays_to_csv(filename):
    # Create a list of headers for each column
    headers = ["Voltage", "Current", "Resistance",
               "Timestamp", "Status Word","Time","Calc Resistance"]
    # Combine the arrays into a list of rows
    rows = zip(voltage, current, resistance, timestamp, status_word, time, true_resistance)
    # Open the CSV file and write the headers
    with open(filename, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        # Write each row to the CSV file
        writer.writerows(rows)

# Grabs information from gui to name file
date = datetime.now().strftime("%m%d%Y")
##Only for my computer if on another computer this becomes irrelevant
folder_path = rf"C:\Users\James\OneDrive\Desktop\SunyPoly\{date}"
timestart = saved_vals["test_start_time"]
chiplet_name = saved_vals["chiplet_name"]
column = saved_vals["device_x"]
row = saved_vals["device_y"]
# Creates name for .csv file
if os.path.exists(folder_path):
    output = os.path.join(folder_path, f'Chip{chiplet_name}_Row{row}_Col{column}_{testType}_{timestart}.csv')
else:
    output = f'Chip{chiplet_name}_Row{row}_Col{column}_{testType}_{timestart}.csv'
print(data_stream)
# Creates .csv file
arrays_to_csv(output)
# Plot Creation
fig, ax = plt.subplots()
ax.plot(voltage, current, color='b')
plt.xlabel('Voltage')
plt.ylabel('Current')
plt.title(f'IV Plot Row:{row} Col:{column} ' + testType)
ax.grid(True, linestyle='--', linewidth=0.5)
ax.legend(['IV Plot'], loc='best')
ax.ticklabel_format(style='sci', axis='both', scilimits=(0, 0))
plt.margins(0.1)
plt.tight_layout()
#Creates name of Graph and saves it to the file of the script
if os.path.exists(folder_path):
    save_path = os.path.join(folder_path, f'Chip{chiplet_name}_Row{row}_Col{column}_{testType}_{timestart}.png')
else:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    save_path = os.path.join(script_dir, f'Chip{chiplet_name}_Row{row}_Col{column}_{testType}_{timestart}.png')
plt.savefig(save_path)
plt.show()
plt.figure()
plt.plot(time,true_resistance)
plt.xlabel('Time')
plt.ylabel('Resistance')
plt.title('Resistance vs. Time')
plt.grid(True)
plt.show()
