import pyvisa
import csv
import matplotlib.pyplot as plt
import gui
import json
rm = pyvisa.ResourceManager()
print(rm.list_resources())
instrument = rm.open_resource('GPIB0::24::INSTR')  # Name of sourcemeter
with open('values.json', 'r') as openfile:
    saved_vals = json.load(openfile)


def singleStaircase_Lin():
    instrument.timeout = 10000
    instrument.write("SYST:REM")
    instrument.write('*RST')
    instrument.write(':SENS:CURR:PROT 1')
    instrument.write(':SOUR:VOLT 0')
    instrument.write(':SOUR:DEL 0.00001')
    instrument.write(':SOUR:SWE:RANG BEST')
    instrument.write(':SOUR:VOLT:MODE SWE')
    instrument.write(':SOUR:SWE:SPAC LIN')
    instrument.write(f':SOUR:VOLT:STAR {saved_vals["source_voltage_start"]}')
    instrument.write(f':SOUR:VOLT:STOP {saved_vals["source_voltage_stop"]}')
    instrument.write(f':SOUR:VOLT:STEP {saved_vals["source_voltage_step"]}')
    instrument.write(f':TRIG:COUN {saved_vals["trig_count"]}')
    instrument.write(':OUTP ON')
    measure_up = instrument.query(':READ?')
    print(measure_up)
    return measure_up


def doubleStaircase_Lin():
    instrument.timeout = 10000
    instrument.write("SYST:REM")
    instrument.write('*RST')
    instrument.write(':SENS:CURR:PROT 1')
    instrument.write(':SOUR:VOLT 0')
    instrument.write(':SOUR:DEL 0.00001')
    instrument.write(':SOUR:SWE:RANG BEST')
    instrument.write(':SOUR:VOLT:MODE SWE')
    instrument.write(':SOUR:SWE:SPAC LIN')
    instrument.write(f':SOUR:VOLT:STAR {saved_vals["source_voltage_start"]}')
    instrument.write(f':SOUR:VOLT:STOP {saved_vals["source_voltage_stop"]}')
    instrument.write(f':SOUR:VOLT:STEP {saved_vals["source_voltage_step"]}')
    instrument.write(f':TRIG:COUN {saved_vals["trig_count"]}')
    instrument.write(':OUTP ON')
    measure_up = instrument.query(':READ?')
    print(measure_up)
    instrument.write('*RST')
    instrument.write(':SENS:CURR:PROT 1')
    instrument.write(':SOUR:VOLT 3.3')
    instrument.write(':SOUR:DEL 0.00001')
    instrument.write(':SOUR:SWE:RANG BEST')
    instrument.write(':SOUR:VOLT:MODE SWE')
    instrument.write(':SOUR:SWE:SPAC LIN')
    instrument.write(f':SOUR:VOLT:STAR {saved_vals["source_voltage_stop"]}')
    instrument.write(f':SOUR:VOLT:STOP {saved_vals["source_voltage_start"]}')
    instrument.write(f':SOUR:VOLT:STEP {saved_vals["source_voltage_step"]*-1}')
    instrument.write(f':TRIG:COUN {saved_vals["trig_count"]}')
    instrument.write(':OUTP ON')
    measure_down = instrument.query(':READ?')
    print(measure_down)
    return measure_up, measure_down


def singleStaircase_Log():
    instrument.timeout = 10000
    instrument.write("SYST:REM")
    instrument.write('*RST')
    instrument.write(':SENS:CURR:PROT 1')
    instrument.write(':SOUR:VOLT 0.1')
    instrument.write(':SOUR:DEL 0.00001')
    instrument.write(':SOUR:SWE:RANG BEST')
    instrument.write(':SOUR:VOLT:MODE SWE')
    instrument.write(':SOUR:SWE:SPAC LOG')
    instrument.write(':SOUR:VOLT:STAR 0.1')
    instrument.write(':SOUR:VOLT:STOP 3.3')
    instrument.write(':SOUR:SWE:POIN 20')
    instrument.write(':TRIG:COUN 20')
    instrument.write(':OUTP ON')
    measure_up = instrument.query(':READ?')
    print(measure_up)
    return measure_up


def doubleStaircase_Log():
    instrument.timeout = 10000
    instrument.write("SYST:REM")
    instrument.write('*RST')
    instrument.write(':SENS:CURR:PROT 1')
    instrument.write(':SOUR:VOLT 0.1')
    instrument.write(':SOUR:DEL 0.00001')
    instrument.write(':SOUR:SWE:RANG BEST')
    instrument.write(':SOUR:VOLT:MODE SWE')
    instrument.write(':SOUR:SWE:SPAC LOG')
    instrument.write(':SOUR:VOLT:STAR 0.1')
    instrument.write(':SOUR:VOLT:STOP 3.3')
    instrument.write(':SOUR:SWE:POIN 20')
    instrument.write(':TRIG:COUN 20')
    instrument.write(':OUTP ON')
    measure_up = instrument.query(':READ?')
    print(measure_up)
    instrument.write('*RST')
    instrument.write(':SENS:CURR:PROT 1')
    instrument.write(':SOUR:VOLT 3.3')
    instrument.write(':SOUR:DEL 0.00001')
    instrument.write(':SOUR:SWE:RANG BEST')
    instrument.write(':SOUR:VOLT:MODE SWE')
    instrument.write(':SOUR:SWE:SPAC LOG')
    instrument.write(':SOUR:VOLT:STAR 3.2')
    instrument.write(':SOUR:VOLT:STOP 0.1')
    instrument.write(':SOUR:SWE:POIN 20')
    instrument.write(':TRIG:COUN 20')
    instrument.write(':OUTP ON')
    measure_down = instrument.query(':READ?')
    print(measure_down)
    return measure_up, measure_down

#Chooses what test to run

if (saved_vals["source_sweep_space"] == 'LIN'):
    if ((saved_vals["is_up_down"])):
        measure_up, measure_down = doubleStaircase_Lin()
    else:
        measure_up = singleStaircase_Lin()
elif (saved_vals["source_sweep_space"] == 'LOG'):
    if ((saved_vals["is_up_down"])):
        measure_up, measure_down = doubleStaircase_Log()
    else:
        measure_up = singleStaircase_Log()

# Initialize arrays to store the values
voltage = []
current = []
resistance = []
timestamp = []
status_word = []

# Function to add values to the arrays
def add_values_to_arrays(data_string):
    values = data_string.split(",")
    for i in range(0, len(values), 5):
        voltage.append(float(values[i].strip()))
        current.append(float(values[i+1].strip()))
        resistance.append(float(values[i+2].strip()))
        timestamp.append(values[i+3].strip())
        status_word.append(values[i+4].strip())

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
               "Timestamp", "Status Word",testType]

    # Combine the arrays into a list of rows
    rows = zip(voltage, current, resistance, timestamp, status_word)

    # Open the CSV file and write the headers
    with open(filename, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)

        # Write each row to the CSV file
        writer.writerows(rows)


output = input('Please enter the name of your excel file with .csv: ')
# Call the function to write the arrays to a CSV file
arrays_to_csv(output)

# Create a line plot
plt.plot(current, voltage)

# Add labels and title
plt.xlabel('Current')
plt.ylabel('Voltage')
plt.title('IV Plot '+testType)

# Display the plot
plt.show()
