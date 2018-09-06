#!/usr/bin/python

import encodings, binascii, codecs


#  value formatters
def PrintTemp(value):
    return ("{0} deg C".format(value))

def PrintPressure(value):
    return ("{0} bar".format(value))

class GATT_service:
    def __init__ (self,
                    characteristics = []
                ):
        self.characteristics = characteristics

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
        self.DefaultVal   = DefaultVal

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
    

def RegisterCharacteristics(characteristics):
    if (type(characteristics) != list):
        return False
    
    for i in characteristics:
        print ("AT+UBTGCHA={0},{1:02X},1,1{2}".format (i.UUID, i.Properties,i.DefaultVal))


characteristiclist = []
characteristiclist.append ( GATT_char(Description="Temperature 1", printfunction=PrintTemp,     UUID="FF00", value = -40) )
characteristiclist.append ( GATT_char(Description="Temperature 2", printfunction=PrintTemp,     UUID="FF01", value =  60) )
characteristiclist.append ( GATT_char(Description="Pressure 1",    printfunction=PrintPressure, UUID="FF02", value =  10) )
characteristiclist.append ( GATT_char(Description="Pressure 2",    printfunction=PrintPressure, UUID="FF03", value =  10) )
characteristiclist.append ( GATT_char(Description="Refrigerant",   printfunction=print,         UUID="FF04", value =  60, DefaultVal="R410A") )


for i in characteristiclist:
    print ("{0:15} {1}".format (i.Description, i.FormattedValue))

# send the characteristics to the u-blox Nina B1 module
#RegisterCharacteristics(characteristiclist)

Refco_service = GATT_service()
Refco_service.append ( GATT_char(Description="Temperature 1", printfunction=PrintTemp,     UUID="FF00", value = -40) )
Refco_service.append ( GATT_char(Description="Temperature 2", printfunction=PrintTemp,     UUID="FF01", value =  60) )
Refco_service.append ( GATT_char(Description="Pressure 1",    printfunction=PrintPressure, UUID="FF02", value =  10) )
Refco_service.append ( GATT_char(Description="Pressure 2",    printfunction=PrintPressure, UUID="FF03", value =  10) )
Refco_service.append ( GATT_char(Description="Refrigerant",   printfunction=print,         UUID="FF04", value =  60, DefaultVal="R410A") )

RegisterCharacteristics (Refco_service.characteristics)
