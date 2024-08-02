# This script reads the data from a JB BMS over RS-485 and formats
# it for use with https://github.com/BarkinSpider/SolarShed/

import time
import sys, os, io
import struct

# Plain serial... Modbus would have been nice, but oh well. 
import serial

sleepTime = 10

try:
    bms1 = serial.Serial('/dev/bms1')
    bms1.baudrate = 115200
    bms1.timeout  = 0.2
except:
    print("BMS 1 not found.")

try:
    bms2 = serial.Serial('/dev/bms2')
    bms2.baudrate = 115200
    bms2.timeout  = 0.2
except:
    print("BMS 2 not found.")

try:
    bms3 = serial.Serial('/dev/bms3')
    bms3.baudrate = 115200
    bms3.timeout  = 0.2
except:
    print("BMS 3 not found.")

try:
    bms4 = serial.Serial('/dev/bms4')
    bms4.baudrate = 115200
    bms4.timeout  = 0.2
except:
    print("BMS 4 not found.")

# The hex string composing the command, including CRC check etc.
# See also:  
# - https://github.com/syssi/esphome-jk-bms
# - https://github.com/NEEY-electronic/JK/tree/JK-BMS
# - https://github.com/Louisvdw/dbus-serialbattery

def sendBMSCommand(bms,cmd_string):
    cmd_bytes = bytearray.fromhex(cmd_string)
    for cmd_byte in cmd_bytes:
        hex_byte = ("{0:02x}".format(cmd_byte))
        bms.write(bytearray.fromhex(hex_byte))
    return

# This could be much better, but it works.
def readBMS(fileObj,bms,ident):

    # BMS 
    try :
        # cell voltages
        sendBMSCommand(bms, '4E 57 00 13 00 00 00 00 06 03 00 00 00 00 00 00 68 00 00 01 29')
    
        time.sleep(.1)
        if bms.inWaiting() >= 4 :
            if bms.read(1).hex() == '4e' : # header byte 1
                if bms.read(1).hex() == '57' : # header byte 2
                    # next two bytes is the length of the data package, including the two length bytes
                    length = int.from_bytes(bms.read(2),byteorder='big')
                    length -= 2 # Remaining after length bytes

                    # Lets wait until all the data that should be there, really is present.
                    # If not, something went wrong. Flush and exit
                    available = bms.inWaiting()
                    if available != length :
                        time.sleep(0.1)
                        available = bms.inWaiting()
                        #if it's not here by now, exit
                        if available != length :
                            bms.reset_input_buffer()
                            raise Exception("Something went wrong reading the data...")

                    # Reconstruct the header and length field
                    b = bytearray.fromhex("4e57")
                    b += (length+2).to_bytes(2, byteorder='big')

                    # Read all the data
                    data = bytearray(bms.read(available))
                    # And re-attach the header (needed for CRC calculation)
                    data = b + data

                    # Calculate the CRC sum
                    crc_calc = sum(data[0:-4])
                    # Extract the CRC value from the data
                    crc_lo = struct.unpack_from('>H', data[-2:])[0]

                    # Exit if CRC doesn't match
                    if crc_calc != crc_lo :
                        bms.reset_input_buffer()
                        raise Exception("CRC Wrong")

                    # The actual data we need
                    data = data[11:length-19] # at location 0 we have 0x79

                    # The byte at location 1 is the length count for the cell data bytes
                    # Each cell has 3 bytes representing the voltage per cell in mV
                    bytecount = data[1]

                    # We can use this number to determine the total amount of cells we have
                    cellcount = int(bytecount/3)

                    voltages = []
                    # Voltages start at index 2, in groups of 3
                    for i in range(cellcount) :
                        voltage = struct.unpack_from('>xH', data, i * 3 + 2)[0]/1000
                        voltages.append(voltage)
                        valName  = "mode=\"cell"+str(i+1)+"_BMS"+ident+"\""
                        valName  = "{" + valName + "}"
                        dataStr  = f"JK_BMS{valName} {voltage}"
                        print(dataStr, file=fileObj)
                
                    delta = max(voltages) - min(voltages)
                    valName  = "mode=\"delta_BMS"+ident+"_V"+"\""
                    valName  = "{" + valName + "}"
                    dataStr  = f"JK_BMS{valName} {delta}"
                    print(dataStr, file=fileObj)
                
                    # Temperatures are in the next nine bytes (MOSFET, Probe 1 and Probe 2), register id + two bytes each for data
                    # Anything over 100 is negative, so 110 == -10                    
                    temp_fet = struct.unpack_from('>H', data, bytecount + 3)[0]
                    if temp_fet > 100 :
                        temp_fet = -(temp_fet - 100)
                    temp_1 = struct.unpack_from('>H', data, bytecount + 6)[0]   
                    if temp_1 > 100 :
                        temp_1 = -(temp_1 - 100)
                    temp_2 = struct.unpack_from('>H', data, bytecount + 9)[0]
                    if temp_2 > 100 :
                        temp_2 = -(temp_2 - 100)
                    
                    # FET + both probes
                    valName  = "mode=\"temp_BMS"+ident+"_FET"+"\""
                    valName  = "{" + valName + "}"
                    dataStr  = f"JK_BMS{valName} {temp_fet}"
                    print(dataStr, file=fileObj)
    
                    valName  = "mode=\"temp_BMS"+ident+"_probe_1"+"\""
                    valName  = "{" + valName + "}"
                    dataStr  = f"JK_BMS{valName} {temp_1}"
                    print(dataStr, file=fileObj)
    
                    valName  = "mode=\"temp_BMS"+ident+"_probe_2"+"\""
                    valName  = "{" + valName + "}" 
                    dataStr  = f"JK_BMS{valName} {temp_2}"
                    print(dataStr, file=fileObj)
            
                    # Battery voltage
                    voltage = struct.unpack_from('>H', data, bytecount + 12)[0]/100
                    valName  = "mode=\"global_BMS"+ident+"_voltage"+"\""
                    valName  = "{" + valName + "}"
                    dataStr  = f"JK_BMS{valName} {voltage}"
                    print(dataStr, file=fileObj)

                    # Current
                    # There are two different versions of the protocol that encode the current differently.
                    # We distinguish by the lenngth of the data sent. This is likely not going to be correct on non-16s packs. 
                    value = struct.unpack_from('>H', data, bytecount + 15)[0]
                    current = 0
                    if length < 260 : 
                        current = (10000 - value)*0.01
                    else:
                        if (value & 0x8000) == 0x8000 :
                            current = (value & 0x7FFF)/100
                        else :
                            current = ((value & 0x7FFF)/100) * -1

                    valName  = "mode=\"global_BMS"+ident+"_current"+"\""
                    valName  = "{" + valName + "}"
                    dataStr  = f"JK_BMS{valName} {current}"
                    print(dataStr, file=fileObj)
                    
                    # Remaining capacity, %
                    capacity = struct.unpack_from('>B', data, bytecount + 18)[0]   
                    valName  = "mode=\"global_BMS"+ident+"_capacity"+"\""
                    valName  = "{" + valName + "}"
                    dataStr  = f"JK_BMS{valName} {capacity}"
                    print(dataStr, file=fileObj)

        bms.reset_input_buffer()

    except Exception as e : 
        print(e)

while True:
    file_object = open('/ramdisk/JK_BMS.prom.tmp', mode='w')

    if 'bms1' in globals() : 
        readBMS(file_object,bms1,"1")

    if 'bms2' in globals() :
        readBMS(file_object,bms2,"2")

    if 'bms3' in globals() : 
        readBMS(file_object,bms3,"3")

    if 'bms4' in globals() :
        readBMS(file_object,bms4,"4")

    file_object.flush()
    file_object.close()
    outLine = os.system('/bin/mv /ramdisk/JK_BMS.prom.tmp /ramdisk/JK_BMS.prom')
    
    time.sleep(sleepTime)
