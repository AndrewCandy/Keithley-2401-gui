import itertools
##Linear Staircase 
def Staircase_Lin(instrument, is_up_down, current_compliance, source_voltage,
                  source_delay, source_voltage_start, source_voltage_stop,
                  source_voltage_step, trig_count):
    instrument.timeout = 100000
    instrument.write("SYST:REM")
    instrument.write('*RST')
    instrument.write(':SYST:BEEP:STAT 0')
    instrument.write(':SENS:VOLT:NPLC 0.01')
    instrument.write(f':SENS:CURR:PROT {current_compliance}')
    instrument.write(f':SOUR:VOLT {source_voltage}')
    instrument.write(f':SOUR:DEL {source_delay}')
    instrument.write(':SOUR:SWE:RANG BEST')
    instrument.write(':SOUR:VOLT:MODE SWE')
    instrument.write(':SOUR:SWE:SPAC LIN')
    instrument.write(f':SOUR:VOLT:STAR {source_voltage_start}')
    instrument.write(f':SOUR:VOLT:STOP {source_voltage_stop}')
    instrument.write(f':SOUR:VOLT:STEP {source_voltage_step}')
    instrument.write(f':TRIG:COUN {trig_count}')
    # instrument.write(':OUTP ON')
    # measure_up = instrument.query(':READ?')
    # print("Measure_up"+measure_up)
    if (is_up_down):
        instrument.write(':SENS:VOLT:NPLC 0.01')
        instrument.write(f':SENS:CURR:PROT {current_compliance}')
        instrument.write(f':SOUR:VOLT {source_voltage_stop}')
        instrument.write(f':SOUR:DEL {source_delay}')
        instrument.write(':SOUR:SWE:RANG BEST')
        instrument.write(':SOUR:VOLT:MODE SWE')
        instrument.write(':SOUR:SWE:SPAC LIN')
        instrument.write(f':SOUR:VOLT:STAR {source_voltage_stop}')
        instrument.write(f':SOUR:VOLT:STOP {source_voltage_start}')
        instrument.write(f':SOUR:VOLT:STEP {source_voltage_step*-1}')
        instrument.write(f':TRIG:COUN {trig_count}')
    #     instrument.write(':OUTP ON')
    #     measure_down = instrument.query(':READ?')
    #     print("Measure_down" + measure_down)
    #     return measure_up, measure_down
    # else:
    #     return measure_up
    instrument.write(':OUTP ON')
    measure = instrument.query(':READ?')
    print("Measurements" + measure)
    return measure
    
#Logarithmic Staircase
##When working with log source voltage cannot be 0
def Staircase_Log(instrument, is_up_down, current_compliance, source_voltage,
                  source_delay, source_voltage_start, source_voltage_stop,
                  log_num_steps, trig_count):
    instrument.timeout = 10000
    instrument.write("SYST:REM")
    instrument.write('*RST')
    instrument.write(':SENS:VOLT:NPLC 0.1')
    instrument.write(f':SENS:CURR:PROT {current_compliance}')
    instrument.write(f':SOUR:VOLT {source_voltage}')
    instrument.write(f':SOUR:DEL {source_delay}')
    instrument.write(':SOUR:SWE:RANG BEST')
    instrument.write(':SOUR:VOLT:MODE SWE')
    instrument.write(':SOUR:SWE:SPAC LOG')
    instrument.write(f':SOUR:VOLT:STAR {source_voltage_start}')
    instrument.write(f':SOUR:VOLT:STOP {source_voltage_stop}')
    instrument.write(f':SOUR:SWE:POIN {log_num_steps}')
    instrument.write(f':TRIG:COUN {trig_count}')
    # instrument.write(':OUTP ON')
    # measure_up = instrument.query(':READ?')
    # print(measure_up)
    if (is_up_down):
        instrument.write(':SENS:VOLT:NPLC 0.1')
        instrument.write(f':SENS:CURR:PROT {current_compliance}')
        instrument.write(f':SOUR:VOLT {source_voltage_stop}')
        instrument.write(f':SOUR:DEL {source_delay}')
        instrument.write(':SOUR:SWE:RANG BEST')
        instrument.write(':SOUR:VOLT:MODE SWE')
        instrument.write(':SOUR:SWE:SPAC LOG')
        instrument.write(f':SOUR:VOLT:STAR {source_voltage_stop}')
        instrument.write(f':SOUR:VOLT:STOP {source_voltage_start}')
        instrument.write(f':SOUR:SWE:POIN {log_num_steps}')
        instrument.write(f':TRIG:COUN {trig_count}')
    #     instrument.write(':OUTP ON')
    #     measure_down = instrument.query(':READ?')
    #     print(measure_down)
    #     return measure_up, measure_down
    # return measure_up, ""
    instrument.write(':OUTP ON')
    measure = instrument.query(':READ?')
    print("Measurements" + measure)
    return measure

##Custom Stair
## variables to grab from GUI: list of voltages
def Staircase_custom(instrument, current_compliance, source_voltage, trig_count):
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
    instrument.write(f':SENS:CURR:PROT {current_compliance}')
    instrument.write(f':SOUR:VOLT {source_voltage}')
    instrument.write('SOUR:SWE:RANG BEST')
    instrument.write('SOUR:VOLT:MODE LIST')
    instrument.write('SOUR:LIST:VOLT 3.5,0')
    instrument.write(f':TRIG:COUN {trig_count}')
    instrument.write('OUTP ON')
    instrument.query(':READ?')

def create_data_stream(column, row):
    data_stream = [0]*21
    for i in range(0,21):
        if(i==0):
            data_stream[i] = 0x80
        if(i == 18):
            data_stream[i] = column
        elif(i==19):
            data_stream[i] = row
        elif(i==20):
            data_stream[i] = 0x81
        
    return data_stream
