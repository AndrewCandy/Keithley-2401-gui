import os
# Linear Staircase


def staircase_lin(instrument, current_compliance, source_voltage,
                  source_delay, source_voltage_start, source_voltage_stop,
                  source_voltage_step, trig_count):
    '''
    Set of instructions for the sourcemeter to run a linear iv test
    '''
    # UP
    instrument.timeout = 100000
    instrument.write("SYST:REM")
    instrument.write('*RST')
    instrument.write(':SYST:BEEP:STAT 0')
    instrument.write(':SENS:VOLT:NPLC 1')
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
    instrument.write(':OUTP ON')
    measure = instrument.query(':READ?')[:-1]
    # DOWN
    instrument.write(':SENS:VOLT:NPLC 1')
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
    instrument.write(':OUTP ON')
    measure_down = (instrument.query(':READ?'))
    measure = measure + ',' + measure_down[:-1]
    # ZERO
    instrument.write(':SENS:VOLT:NPLC 1')
    instrument.write(f':SENS:CURR:PROT {current_compliance}')
    instrument.write(':SOUR:VOLT 0')
    instrument.write(':SOUR:DEL 0')
    instrument.write(':SOUR:SWE:RANG BEST')
    instrument.write(':SOUR:VOLT:MODE LIST')
    instrument.write(':SOUR:LIST:VOLT 0, 0')
    instrument.write(':TRIG:COUN 2')
    # UP
    instrument.write('*RST')
    instrument.write(':SYST:BEEP:STAT 0')
    instrument.write(':SENS:VOLT:NPLC 1')
    instrument.write(f':SENS:CURR:PROT {current_compliance}')
    instrument.write(f':SOUR:VOLT {source_voltage}')
    instrument.write(f':SOUR:DEL {source_delay}')
    instrument.write(':SOUR:SWE:RANG BEST')
    instrument.write(':SOUR:VOLT:MODE SWE')
    instrument.write(':SOUR:SWE:SPAC LIN')
    instrument.write(':SOUR:VOLT:STAR 0')
    instrument.write(':SOUR:VOLT:STOP -1.5')
    instrument.write(f':SOUR:VOLT:STEP {source_voltage_step*-1}')
    instrument.write(':TRIG:COUN 16')
    instrument.write(':OUTP ON')
    measure_down_again = (instrument.query(':READ?'))
    measure = measure + ',' + measure_down_again[:-1]

    instrument.write(':SENS:VOLT:NPLC 1')
    instrument.write(f':SENS:CURR:PROT {current_compliance}')
    instrument.write(f':SOUR:VOLT {source_voltage}')
    instrument.write(f':SOUR:DEL {source_delay}')
    instrument.write(':SOUR:SWE:RANG BEST')
    instrument.write(':SOUR:VOLT:MODE SWE')
    instrument.write(':SOUR:SWE:SPAC LIN')
    instrument.write(':SOUR:VOLT:STAR -1.5')
    instrument.write(':SOUR:VOLT:STOP 0')
    instrument.write(f':SOUR:VOLT:STEP {source_voltage_step}')
    instrument.write(':TRIG:COUN 16')
    instrument.write(':OUTP ON')
    measure_up = instrument.query(':READ?')
    measure = measure + ',' + measure_up[:-1]
    print("Measurements " + str(measure))
    return measure

# Logarithmic Staircase
# When working with log source voltage cannot be 0


def staircase_log(instrument, is_up_down, current_compliance, source_voltage,
                  source_delay, source_voltage_start, source_voltage_stop,
                  log_num_steps, trig_count):
    '''
    Set of instructions for the sourcemeter to run a logarithmic iv test
    '''
    instrument.timeout = 10000
    instrument.write("SYST:REM")
    instrument.write('*RST')
    instrument.write(':SENS:VOLT:NPLC 10')
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
    instrument.write(':OUTP ON')
    measure = instrument.query(':READ?')[:-1]
    print(measure)

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
        instrument.write(':OUTP ON')
        measure_down = instrument.query(':READ?')
        measure = measure + ',' + measure_down[:-1]
        print(type(measure))
    print("Measurements " + str(measure))
    return measure


def endurance_test(instrument, current_compliance, source_voltage,
                   source_delay, voltage_list, list_length):
    '''
    Set of instructions for the sourcemeter to run an endurance test
    '''
    instrument.timeout = 10000
    instrument.write("SYST:REM")
    instrument.write('*RST')
    instrument.write(':SYST:BEEP:STAT 0')
    instrument.write(':SENS:VOLT:NPLC 0.01')
    instrument.write(f':SENS:CURR:PROT {current_compliance}')
    instrument.write(f':SOUR:VOLT {source_voltage}')
    instrument.write(f':SOUR:DEL {source_delay}')
    instrument.write(':SOUR:SWE:RANG BEST')
    instrument.write(':SOUR:VOLT:MODE LIST')
    instrument.write(f':SOUR:LIST:VOLT {voltage_list}')
    instrument.write(f':TRIG:COUN {list_length}')
    instrument.write(':OUTP ON')
    measure = (instrument.query(':READ?'))[:-1]
    return measure


def create_voltage_list(set_voltage, read_voltage, reset_voltage):
    '''
    Assembles a list of voltages to set the source meter to for endurance testing
    '''
    voltage = []
    i = 0
    for j in range(1, 6):
        cycle_number = i + j
        print("Running cycle", cycle_number)
        voltage.append(set_voltage)
        voltage.append(0)
        voltage.append(read_voltage)
        voltage.append(0)
        voltage.append(reset_voltage)
        voltage.append(0)
        voltage.append(read_voltage)
        voltage.append(0)
    # print(voltage)
    volt_string = ', '.join(str(item) for item in voltage)
    # print(volt_string)
    return volt_string


def create_test_folder(test):
    '''
    Creates folder for all device test files of a test
    return:
        folder path
    '''
    test_type = test.get_test_type()
    str_time = test.start_time.strftime("%m-%d-%Y_%H-%M-%S")
    # Get current directory
    home_dir = os.path.abspath(__file__)
    current_directory = os.path.dirname(home_dir)
    # Make new folder for test if doesn't exist
    folder_path = os.path.join(
        current_directory, f"SavedData/{test_type}_{str_time}")
    os.makedirs(folder_path, exist_ok=True)
    return folder_path


def calc_trig_count(source_voltage_stop, source_voltage_start,
                    source_voltage_step, log_num_steps, iv_space):
    '''
    Finds the correct trigger count for an iv test given parameters about the sweep
    '''
    if iv_space == 'LIN':
        trig_count = (source_voltage_stop-source_voltage_start) / \
            source_voltage_step
    elif iv_space == 'LOG':
        trig_count = log_num_steps
    return trig_count


def find_hrs(dataframe):
    '''
    Input dataframe must be data from endurance test
    returns list of HRS readings from endurance test
    '''
    resistance = dataframe['Real Resistance']
    hrs = []
    for i in range(2, len(resistance), 8):
        hrs.append(resistance[i])
    return hrs


def find_lrs(dataframe):
    '''
    Input dataframe must be data from endurance test
    returns list of LRS readings from endurance test
    '''
    resistance = dataframe['Real Resistance']
    lrs = []
    for i in range(6, len(resistance), 8):
        lrs.append(resistance[i])
    return lrs
