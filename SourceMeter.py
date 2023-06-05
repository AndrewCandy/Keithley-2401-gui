import pyvisa
rm = pyvisa.ResourceManager()
print(rm.list_resources())
instrument = rm.open_resource('GPIB0::24::INSTR')
""" Type of Tests to be complete
    1. IV Inputs either current or voltage then finds the other after going through device then ploting on IV graph
    2. Staircase up to set voltage then back down and graph triangle
"""
#print(input('Choose what test you would like to complete: \n 1. IV \n 2. Linearity\n'))
# Find instrument name from earlier 
instrument.timeout = 10000
instrument.write("SYST:REM")
instrument.write('*RST')
instrument.write(':SOUR:VOLT 0')
instrument.write(':SOUR:DEL 0.00001')
instrument.write(':SOUR:SWE:RANG BEST')
instrument.write(':SOUR:VOLT:MODE SWE')
instrument.write(':SOUR:SWE:SPAC LIN')
instrument.write(':SOUR:VOLT:STAR 0')
instrument.write(':SOUR:VOLT:STOP 3.3')
instrument.write(':SOUR:VOLT:STEP 0.1')
instrument.write(':TRIG:COUN 34')
instrument.write(':OUTP ON')
measure_up = instrument.query(':READ?')
print(measure_up)
instrument.write('*RST')
instrument.write(':SOUR:VOLT 3.3')
instrument.write(':SOUR:DEL 0.00001')
instrument.write(':SOUR:SWE:RANG BEST')
instrument.write(':SOUR:VOLT:MODE SWE')
instrument.write(':SOUR:SWE:SPAC LIN')
instrument.write(':SOUR:VOLT:STAR 3.2')
instrument.write(':SOUR:VOLT:STOP 0')
instrument.write(':SOUR:VOLT:STEP -0.1')
instrument.write(':TRIG:COUN 33')
instrument.write(':OUTP ON')
measure_down = instrument.query(':READ?')
print(measure_down)