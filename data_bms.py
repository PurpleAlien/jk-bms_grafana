# This script reads the data from a JB BMS over RS-485 and formats
# it for use with git@github.com:PurpleAlien/jk-bms_grafana.git

import time
import sys, os, io

# Plain serial... Modbus would have been nice, but oh well. 
import serial

# Yes, we can get this info programatically, but for now just set it here
numCells = 16

sleepTime = 10

try:
    bms = serial.Serial('/dev/ttyUSB0')
    bms.baudrate = 9600
    bms.timeout  = 0.2
except:
    print("BMS not found.")

# The hex string composing the command, including CRC check etc.
# See also: https://diysolarforum.com/resources/rs-485-heltec-jk-bms.140/
def sendBMSCommand(cmd_string):
    cmd_bytes = bytearray.fromhex(cmd_string)
    for cmd_byte in cmd_bytes:
        hex_byte = ("{0:02x}".format(cmd_byte))
        bms.write(bytearray.fromhex(hex_byte))
    return

# This could be much better, but it works.
def readBMS(fileObj):

    # cell voltages
    sendBMSCommand('DD A5 04 00 FF FC 77')
    
    time.sleep(.1)

    while bms.inWaiting() >=3 :
        if bms.read(1).hex() == 'dd' :
            if bms.read(1).hex() == '04' :
                if bms.read(1).hex() == '00' :
                    #next byte is length
                    size = int.from_bytes(bms.read(1),byteorder='big')
                    
                    i = 0
                    while i < numCells :
                        i += 1
                        val = int.from_bytes(bms.read(2),byteorder='big')/1000
                        valName  = "mode=\"cell"+str(i)+"_BMS1\""
                        valName  = "{" + valName + "}"
                        dataStr  = f"JK_BMS{valName} {val}"
                        print(dataStr, file=fileObj)
                    
                 
    time.sleep(.1)
    
    # temperature etc.
    sendBMSCommand('DD A5 03 00 FF FD 77')

    time.sleep(.1)
    
    # We read in all the data even though most are not written to the output file
    # You could expand this easily.
    while bms.inWaiting() >=3 :
        if bms.read(1).hex() == 'dd' :
            if bms.read(1).hex() == '03' :
                if bms.read(1).hex() == '00' :
                    #next byte is length
                    size = int.from_bytes(bms.read(1),byteorder='big')
                    
                    #battery voltage            
                    val = int.from_bytes(bms.read(2),byteorder='big')
                    #print(val/100)  
                    
                    #total current
                    val = int.from_bytes(bms.read(2),byteorder='big')
                    #print(val/100)

                    #remaining capacity
                    val = int.from_bytes(bms.read(2),byteorder='big')
                    #print(val/100)                    

                    #total capcity (as configured)
                    val = int.from_bytes(bms.read(2),byteorder='big')
                    #print(val/100)
                    
                    #cycle number
                    val = int.from_bytes(bms.read(2),byteorder='big')
                    #print(val)
               
                    #production date
                    val = int.from_bytes(bms.read(2),byteorder='big')
                
                    #balance low
                    val = int.from_bytes(bms.read(2),byteorder='big')
        
                    #balance high
                    val = int.from_bytes(bms.read(2),byteorder='big')

                    #protection status
                    val = int.from_bytes(bms.read(2),byteorder='big')

                    #version
                    val = int.from_bytes(bms.read(1),byteorder='big')            

                    #remaning capacity in percentage
                    val = int.from_bytes(bms.read(1),byteorder='big')
                    #print(val)
            
                    #mos status
                    val = int.from_bytes(bms.read(1),byteorder='big')
                    #print(val)

                    #number of cells
                    val = int.from_bytes(bms.read(1),byteorder='big')
                    #print(val)

                    #number of temperature probes
                    val = int.from_bytes(bms.read(1),byteorder='big')
                    #print(val)

                    #temperature 1 (internal)
                    val = int.from_bytes(bms.read(2),byteorder='big')
                    #print((val-2731)/10)

                    #temperature 2 (bat probe 1)
                    val = int.from_bytes(bms.read(2),byteorder='big')
                    val = (val-2731)/10
                    valName  = "mode=\"temp_BMS1\""
                    valName  = "{" + valName + "}"
                    dataStr  = f"JK_BMS{valName} {val}"
                    print(dataStr, file=fileObj)
                     
                    #temperature 3 (bat probe 2)
                    val = int.from_bytes(bms.read(2),byteorder='big')
                    #print((val-2731)/10)

while True:
    file_object = open('/ramdisk/JK_BMS.prom.tmp', mode='w')
    readBMS(file_object)
    file_object.flush()
    file_object.close()
    outLine = os.system('/bin/mv /ramdisk/JK_BMS.prom.tmp /ramdisk/JK_BMS.prom')
    
    time.sleep(sleepTime)

