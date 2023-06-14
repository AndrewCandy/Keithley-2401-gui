'''
-------
Serial
-------
Functions which deal with serial communication between the GUI and microcontroller PCB

Code was built of Jacob Pelton's existing code
'''

import serial
import serial.tools.list_ports
import time

# Sends list of parameters as bytes to PCB and returns output list
def serialExecution(input):
    
    # output arrays read from serial port
    output = []
    dum = 0
    # Find serial COM Port
    port = findPort()
   
    # Baudrate
    rate = 115200

    ser = serial.Serial(port, rate, timeout=0, bytesize=serial.EIGHTBITS) # Define serial device 

    ser.write(bytearray(input)) # Send list of integer values to board as byte array
    
    time.sleep(0.5)

    #TEMP: Remove read code because comms is currently one way
    # # While loop to continuously read data
    # while 1:
        
    #     # read value(s) from board and convert to strings
    #     data = ser.readline().decode("ascii") 
        
    #     # remove unwanted characters
    #     data = data.replace('\r\n', '')
    #     data = data.replace('k', '')
    #     data = data.replace('uA', '')
        
    #     # Possible data read
    #     if data == 'Received Frame Eror': # If error with input list tell user to hit reset switch 
    #         return 'reset switch'
    #         #print("Hit reset switch to resubmit data")
            
    #     elif data == 'Waiting for command': # when data is finished reading or reset switch is pressed -> end loop and wait for user to re-submit input array
    #         break
        
    #     elif data == 'Value is OutOfRange': # (only for script testing) continues reading if bad value
    #         continue
        
    #     elif data != '': # if data read is not empty add to list of output reads
                
    #         output.append(float(data))
                
    #             # if dum == 0: # if 1st read calc R with 1st read voltage
    #             #     data = abs(float(v_read1))/float(data) * 1000 # calculate 
    #             #     #print(round(data, 1))
    #             #     output.append(round(data, 1))
    #             #     dum = 1
    #             # else: # if 2nd read calc R with 2nd read voltage
    #             #     data = abs(float(v_read2))/float(data) * 1000 # calculate resistance
    #             #     #print(round(data, 1))
    #             #     output.append(round(data, 1))
    #             #     dum = 0
            
            
    # return output

# Finds the port the PCB is plugged into
def findPort():
    
    ports = serial.tools.list_ports.comports()
    #print(ports)
    
    comPort = None
    
    for i in ports:
        strPort = str(i)
        if 'Silicon Labs CP210x' in strPort:
            splitPort = strPort.split(' ')
            comPort = splitPort[0]
        
    return comPort

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
