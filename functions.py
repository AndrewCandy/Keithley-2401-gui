import itertools
##Linear Staircase 
def Staircase_Lin(instrument, is_up_down, full_cycle, current_compliance, source_voltage,
                  source_delay, source_voltage_start, source_voltage_stop,
                  source_voltage_step, trig_count):
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
    print(measure)
    if is_up_down:
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
        measure = measure +','+ measure_down[:-1]
        print(type(measure))
        if(full_cycle):
            instrument.write(':SENS:VOLT:NPLC 1')
            instrument.write(f':SENS:CURR:PROT {current_compliance}')
            instrument.write(':SOUR:VOLT 0')
            instrument.write(':SOUR:DEL 0')
            instrument.write(':SOUR:SWE:RANG BEST')
            instrument.write(':SOUR:VOLT:MODE LIST')
            instrument.write(':SOUR:LIST:VOLT 0, 0')
            instrument.write(':TRIG:COUN 2')
            
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
            measure = measure +','+ measure_down_again[:-1]
            instrument.write(':SENS:VOLT:NPLC 1')
            instrument.write(f':SENS:CURR:PROT {current_compliance}')
            instrument.write(f':SOUR:VOLT {source_voltage}')
            instrument.write(f':SOUR:DEL {source_delay}')
            instrument.write(':SOUR:SWE:RANG BEST')
            instrument.write(':SOUR:VOLT:MODE SWE')
            instrument.write(':SOUR:SWE:SPAC LIN')
            instrument.write(f':SOUR:VOLT:STAR -1.5')
            instrument.write(f':SOUR:VOLT:STOP 0')
            instrument.write(f':SOUR:VOLT:STEP {source_voltage_step}')
            instrument.write(f':TRIG:COUN 15')
            instrument.write(':OUTP ON')
            measure_up = (instrument.query(':READ?'))
            measure = measure +','+ measure_up[:-1]
    print("Measurements " + str(measure))            
    return measure
    
#Logarithmic Staircase
##When working with log source voltage cannot be 0
def Staircase_Log(instrument, is_up_down, current_compliance, source_voltage,
                  source_delay, source_voltage_start, source_voltage_stop,
                  log_num_steps, trig_count):
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
        measure_down = (instrument.query(':READ?'))
        measure = measure +','+ measure_down[:-1]
        print(type(measure))
    print("Measurements " + str(measure))
    return measure


def endurance_Test_Old(instrument, current_compliance, source_voltage,
                  source_delay):
    instrument.timeout = 100000
    ##SET -- Up
    instrument.write("SYST:REM")
    instrument.write('*RST')
    instrument.write(':SYST:BEEP:STAT 0')
    instrument.write(':SENS:VOLT:NPLC 1')
    instrument.write(f':SENS:CURR:PROT {current_compliance}')
    instrument.write(':SOUR:VOLT 0')
    instrument.write(f':SOUR:DEL {source_delay}')
    instrument.write(':SOUR:SWE:RANG BEST')
    instrument.write(':SOUR:VOLT:MODE SWE')
    instrument.write(':SOUR:SWE:SPAC LIN')
    instrument.write(':SOUR:VOLT:STAR 0')
    instrument.write(':SOUR:VOLT:STOP 2.5')
    instrument.write(':SOUR:VOLT:STEP 0.1')
    instrument.write(':TRIG:COUN 26')
    instrument.write(':OUTP ON')
    measure = []

    #SET -- Down
    instrument.write(':SENS:VOLT:NPLC 1')
    instrument.write(f':SENS:CURR:PROT {current_compliance}')
    instrument.write(':SOUR:VOLT 2.5')
    instrument.write(f':SOUR:DEL {source_delay}')
    instrument.write(':SOUR:SWE:RANG BEST')
    instrument.write(':SOUR:VOLT:MODE SWE')
    instrument.write(':SOUR:SWE:SPAC LIN')
    instrument.write(':SOUR:VOLT:STAR 2.5')
    instrument.write(':SOUR:VOLT:STOP 0')
    instrument.write(':SOUR:VOLT:STEP -0.1')
    instrument.write(':TRIG:COUN 26')
    instrument.write(':OUTP ON')

    ##READ -- Up
  
    instrument.write('*RST')
    instrument.write(':SYST:BEEP:STAT 0')
    instrument.write(':SENS:VOLT:NPLC 1')
    instrument.write(f':SENS:CURR:PROT {current_compliance}')
    instrument.write(':SOUR:VOLT 0')
    instrument.write(f':SOUR:DEL {source_delay}')
    instrument.write(':SOUR:SWE:RANG BEST')
    instrument.write(':SOUR:VOLT:MODE SWE')
    instrument.write(':SOUR:SWE:SPAC LIN')
    instrument.write(':SOUR:VOLT:STAR 0')
    instrument.write(':SOUR:VOLT:STOP 0.2')
    instrument.write(':SOUR:VOLT:STEP 0.1')
    instrument.write(':TRIG:COUN 3')
    instrument.write(':OUTP ON')
    measure = instrument.query(':READ?')[:-1]   
    #READ -- Down
    instrument.write(':SENS:VOLT:NPLC 1')
    instrument.write(f':SENS:CURR:PROT {current_compliance}')
    instrument.write(':SOUR:VOLT 0.2')
    instrument.write(f':SOUR:DEL {source_delay}')
    instrument.write(':SOUR:SWE:RANG BEST')
    instrument.write(':SOUR:VOLT:MODE SWE')
    instrument.write(':SOUR:SWE:SPAC LIN')
    instrument.write(':SOUR:VOLT:STAR 0.2')
    instrument.write(':SOUR:VOLT:STOP 0')
    instrument.write(':SOUR:VOLT:STEP -0.1')
    instrument.write(':TRIG:COUN 3')
    instrument.write(':OUTP ON')
    measure_down = (instrument.query(':READ?'))
    measure = measure +','+ measure_down[:-1]
    
    #RESET -- Down
  
    instrument.write('*RST')
    instrument.write(':SYST:BEEP:STAT 0')
    instrument.write(':SENS:VOLT:NPLC 1')
    instrument.write(f':SENS:CURR:PROT {current_compliance}')
    instrument.write(':SOUR:VOLT 0')
    instrument.write(f':SOUR:DEL {source_delay}')
    instrument.write(':SOUR:SWE:RANG BEST')
    instrument.write(':SOUR:VOLT:MODE SWE')
    instrument.write(':SOUR:SWE:SPAC LIN')
    instrument.write(':SOUR:VOLT:STAR 0')
    instrument.write(':SOUR:VOLT:STOP -1.5')
    instrument.write(':SOUR:VOLT:STEP -0.1')
    instrument.write(':TRIG:COUN 16')
    instrument.write(':OUTP OFF')
    #RESET -- Up
    instrument.write(':SENS:VOLT:NPLC 1')
    instrument.write(f':SENS:CURR:PROT {current_compliance}')
    instrument.write(':SOUR:VOLT -1.5')
    instrument.write(f':SOUR:DEL {source_delay}')
    instrument.write(':SOUR:SWE:RANG BEST')
    instrument.write(':SOUR:VOLT:MODE SWE')
    instrument.write(':SOUR:SWE:SPAC LIN')
    instrument.write(':SOUR:VOLT:STAR -1.5')
    instrument.write(':SOUR:VOLT:STOP 0')
    instrument.write(':SOUR:VOLT:STEP 0.1')
    instrument.write(':TRIG:COUN 16')
    instrument.write(':OUTP OFF')
    
    #READ -- Up
  
    instrument.write('*RST')
    instrument.write(':SYST:BEEP:STAT 0')
    instrument.write(':SENS:VOLT:NPLC 1')
    instrument.write(f':SENS:CURR:PROT {current_compliance}')
    instrument.write(':SOUR:VOLT 0')
    instrument.write(f':SOUR:DEL {source_delay}')
    instrument.write(':SOUR:SWE:RANG BEST')
    instrument.write(':SOUR:VOLT:MODE SWE')
    instrument.write(':SOUR:SWE:SPAC LIN')
    instrument.write(':SOUR:VOLT:STAR 0')
    instrument.write(':SOUR:VOLT:STOP 0.2')
    instrument.write(':SOUR:VOLT:STEP 0.1')
    instrument.write(':TRIG:COUN 3')
    instrument.write(':OUTP ON')
    measure_up = instrument.query(':READ?')[:-1] 
    measure = measure +',' + measure_up
    #READ -- Down
    instrument.write(':SENS:VOLT:NPLC 1')
    instrument.write(f':SENS:CURR:PROT {current_compliance}')
    instrument.write(':SOUR:VOLT 0.2')
    instrument.write(f':SOUR:DEL {source_delay}')
    instrument.write(':SOUR:SWE:RANG BEST')
    instrument.write(':SOUR:VOLT:MODE SWE')
    instrument.write(':SOUR:SWE:SPAC LIN')
    instrument.write(':SOUR:VOLT:STAR 0.2')
    instrument.write(':SOUR:VOLT:STOP 0')
    instrument.write(':SOUR:VOLT:STEP -0.1')
    instrument.write(':TRIG:COUN 3')
    instrument.write(':OUTP ON')
    measure_down_again = (instrument.query(':READ?'))[:-1]
    measure = measure +','+ measure_down_again
    print("Measurements " + str(measure))            
    return measure

def endurance_Test(instrument, current_compliance, source_voltage, source_delay, voltage_list, list_length):
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

def create_voltage_list(set_voltage, read_voltage, reset_voltage, cycles):
    voltage=[] 
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
    #print(voltage)
    volt_string = ', '.join(str(item) for item in voltage)
    #print(volt_string)
    return volt_string
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

def calcTrigCount(source_voltage_stop,source_voltage_start,source_voltage_step,log_num_steps,iv_space):
    if(iv_space == 'LIN'):
        trig_Count = (source_voltage_stop-source_voltage_start)/source_voltage_step
    elif(iv_space == 'LOG'):
        trig_Count = log_num_steps
    return trig_Count
    
