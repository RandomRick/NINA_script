#!/usr/bin/python

import encodings, binascii, codecs, logging
import os
import sys
import serial

COMPORT = 9
theport = None  # serial port


def main():
    global theport
    # test for operating system name
    try:
        portname = "COM" + str(COMPORT) if (os.name == "nt") else "/dev/ttyS"+str(COMPORT-1)
        theport = SP(portname=portname)

        theport.WriteRead ("AT+UBTCM=2",                            ["OK", "ERROR"], "GAP connectable mode")
        theport.WriteRead ("AT+UBTDM=3",                            ["OK", "ERROR"], "GAP general discoverable mode")
        theport.WriteRead ("AT+UBTPM=2",                            ["OK", "ERROR"], "GAP pairing mode")
        theport.WriteRead ("AT+UBTLE=2",                            ["OK", "ERROR"], "BLE peripheral")                       # 2 is peripheral
        theport.WriteRead ("AT+UDSC=0,0",                           ["OK", "ERROR"], "server config: disable SPS server")   # turn off SPS server to increase GATT characteristics capability
        theport.WriteRead ("AT+UBTLECFG=26,2",                      ["OK", "ERROR"], "u-blox advice MTU size")         # fiddle with MTU size - as above.
        theport.WriteRead ("AT+UBTLN=\"REFCOperipheralserver\"",    ["OK", "ERROR"], "Local Name")
        theport.WriteRead ("AT+UBTLEDIS=REFCO_Ltd,CLA,6.12,1",      ["OK", "ERROR"], "Device Information Service")
        theport.WriteRead ("AT&W",                                  ["OK", "ERROR"])                                               # reset 1
        theport.WriteRead ("AT+CPWROFF",                            ["+STARTUP"])                                            # reset 2: note terminator different ("STARTUP")


        # define the custom service
        Refco_service = GATT_service(UUID="b0897c037fdd42a499abef47e3fe574f".upper(), characteristics=[])
        # and add its characteristics
        Refco_service.append ( GATT_char(Description="Temperature 1", printfunction=PrintTemp,     UUID="FF00", value = -40) )
        Refco_service.append ( GATT_char(Description="Temperature 2", printfunction=PrintTemp,     UUID="FF01", value =  60) )
        Refco_service.append ( GATT_char(Description="Pressure 1",    printfunction=PrintPressure, UUID="FF02", value =  10) )
        Refco_service.append ( GATT_char(Description="Pressure 2",    printfunction=PrintPressure, UUID="FF03", value =  10) )
        Refco_service.append ( GATT_char(Description="Refrigerant",   printfunction=PrintVanilla,  UUID="FF04", value =  60, DefaultVal="R410A") )

        # Now send the service to the u-blox NINA B1 module:
        theport.IntelliWriteSerial(Refco_service)


        for c in Refco_service.characteristics:
            print ("it's ", c.Description, c.handle)


        theport.MessageLoop()

        # # send the service's characteristics to the u-blox NINA B1 module
        # for i in Refco_service.characteristics:
        #     IntelliWriteSerial(i)

    except Exception as ee:
        print ("An error occurred")
        print ("Error message:", ee)





class SP:
    # class vars - not per-instance vars
    __theport = None
    __transactionCount = 1

    # ctor
    def __init__(self, portname):
        self.portname = portname
        SP.__theport = serial.Serial()
        SP.__theport.port = portname
        SP.__theport.baudrate = 115200
        SP.__theport.timeout = 1
        try:
            SP.__theport.open()
        except Exception as ee:
            raise ee

    def WriteRead (self, stringIn, terminators, comment=None):
        print ("Transaction " + str(SP.__transactionCount))
        if (not comment == None):
            print (comment)
        SP.__transactionCount = SP.__transactionCount+1
        print ("OUT: " + stringIn)
        #stringIn = stringIn + "\r"
        SP.__theport.write(stringIn.encode() + b'\r')
        # read output from NINA until OK or ERROR

        answers = []
        answer = None
        terminators = list(map(str.upper, terminators))
        while not answer in terminators:
            answer = SP.__theport.readline().rstrip().decode().upper()
            if not answer == None:
                answers.append (answer)
            print ("IN:  " + answer)

            if (False):
                if (answer.upper() == "ERROR"):
                    exit()
        print()
        return answers

    def IntelliWriteSerial(self, i):
        if type(i) == GATT_service:
            answer = self.WriteRead ("AT+UBTGSER={0}".format (i.UUID), ["OK", "ERROR"])
            if answer[1][:9] == "+UBTGSER:" :
                i.handle = int (answer[1].split(":")[1])

            for c in i.characteristics:
                answer = \
                self.WriteRead ("AT+UBTGCHA={0},{1:02X},1,1{2}".format (c.UUID, c.Properties,c.DefaultVal), ["OK", "ERROR"])
                if answer[1][:9] == "+UBTGCHA:" :
                    c.handle = int (answer[1].split(":")[1].split(",")[0])



    def MessageLoop (self):
        timeout = False
        message = None
        print ("setting serial time-out to 1 second")
        SP.__theport.timeout = 1
        while (1):
            message = SP.__theport.readline().rstrip().decode()
            # print dots whilst timing out
            if ( len (message) == 0):
                #if (not timeout):
                    #print()
                timeout = True
                sys.stdout.write ('.')
                sys.stdout.flush()
                continue

            # newline if we've been printing dots
            if (timeout):
                print()
                timeout = False

            print ('IN:  ' + message)
 




#  value formatters
def PrintTemp(value):
    return ("{0} deg C".format(value))

def PrintPressure(value):
    return ("{0} bar".format(value))
    
def PrintVanilla (value):
    return str(value)

class GATT_service:
    def __init__ (self,
                    UUID            = None,
                    characteristics = [],
                    handle          = None
                ):
        self.UUID               = UUID
        self.characteristics    = characteristics
        self.handle             = handle

    def append(self, appendage=None):
        self.characteristics.append (appendage)


class GATT_char:
    def __init__(self,
                    printfunction   = None,
                    value           = None,
                    UUID            = None,
                    Description     = None,
                    handle          = None,
                    Properties      = 0x10 + 0x02,
                    DefaultVal      = None
                    ):
        self.printfunction  = printfunction
        self.value          = value
        self.UUID           = UUID
        self.Description    = Description
        self.handle         = handle
        self.Properties     = Properties
        self.DefaultVal     = DefaultVal

    @property
    def UUID(self):
        return "{0}".format(self.__UUID)
    @UUID.setter
    def UUID (self, UUID):
        if (not UUID == None):
            if (not type(UUID) == str):
                print ("The UUID must be a string!")
        self.__UUID = UUID


    @property
    def FormattedValue(self):
        return self.printfunction(self.value)

    @property
    def CheckClassFullyDefined(self):
        if (self.printfunction == None):
            return False
        if (self.value == None):
            return False
        if (self.UUID == None):
            return False
        return True

    @property
    def DefaultVal(self):
        if (self.__DefaultVal == None):
            return ""
        return "," + str(codecs.encode(bytearray(self.__DefaultVal, "ascii"), "hex"), "ascii")
        #return "," + self.__DefaultVal
    @DefaultVal.setter
    def DefaultVal(self, DefaultVal):
        self.__DefaultVal = DefaultVal
    

# def RegisterCharacteristics(characteristics):
#     if (type(characteristics) != list):
#         return False
    
#     for i in characteristics:
#         print ("AT+UBTGCHA={0},{1:02X},1,1{2}".format (i.UUID, i.Properties,i.DefaultVal))



# # writes a string to the serial port, and waits for the
# # specified response.  All good.
# def WriteReadSerial(out, termination):
#     # turn a single string terminator into a list, albeit with one element:
#     if  type(termination) == str:
#         termination = [termination]

#     print ("OUT: ", out)
#     print ("Now waiting for any of " , termination)





# Refco_service = GATT_service()
# Refco_service.append ( GATT_char(Description="Temperature 1", printfunction=PrintTemp,     UUID="FF00", value = -40) )
# Refco_service.append ( GATT_char(Description="Temperature 2", printfunction=PrintTemp,     UUID="FF01", value =  60) )
# Refco_service.append ( GATT_char(Description="Pressure 1",    printfunction=PrintPressure, UUID="FF02", value =  10) )
# Refco_service.append ( GATT_char(Description="Pressure 2",    printfunction=PrintPressure, UUID="FF03", value =  10) )
# Refco_service.append ( GATT_char(Description="Refrigerant",   printfunction=print,         UUID="FF04", value =  60, DefaultVal="R410A") )

# #RegisterCharacteristics (Refco_service.characteristics)
# print ("I got here, didn't I?")
# for i in Refco_service.characteristics:
#     IntelliWriteSerial(i)
# IntelliWriteSerial(Refco_service)


main()