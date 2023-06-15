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

    # Define serial device
    ser = serial.Serial(port, rate, timeout=0, bytesize=serial.EIGHTBITS)

    # Send list of integer values to board as byte array
    ser.write(bytearray(input))

    time.sleep(0.5)

    # TEMP: Remove read code because comms is currently one way
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
    # print(ports)

    comPort = None

    for i in ports:
        strPort = str(i)
        if 'Silicon Labs CP210x' in strPort:
            splitPort = strPort.split(' ')
            comPort = splitPort[0]

    return comPort


def create_data_stream(column, row):
    data_stream = [0x80, 0x02, 0x64, 0x19, 0x64, 0x04, 0x64, 0xFE, 0x64,
                   0x03, 0x64, 0xE7, 0x64, 0x04, 0x64, 0xFE, 0x64, 0x01, column, row, 0x81]
    return data_stream


def message_micro(x, y):
    '''
    Sends a 21 byte long datastream to microcontroller containing the xy
    coords of the device we are attempting to work with
    '''
    data_stream = [0]*21
    # Creates 21 byte long data stream where the first and last values are
    # 0x80 and 0x81 respectively and the second and third to last spots are
    # the  row and columns and the rest are 0
    data_stream = create_data_stream(x, y)
    print(data_stream)
    # Uncomment when trying to send information to the PCB
    output = serialExecution(data_stream)
    print(output)
