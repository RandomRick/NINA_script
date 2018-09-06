#!/usr/bin/python
import sys,os, serial, os, time, io, re
#import _thread as thread
#import threading
import binascii, codecs
import calendar # for creating timestamps, etc.

#globals
COMPORT=9
transactionglobal = 1
theport = serial.Serial()
regex = re.compile (r'.*CHA:\d\d,\d+')
RunBGthread : True
conn_handle = -1 # connection handle dished out by +UUBTACLC and needed by SN
mfg_name_handle = -1
Temp1Handle = None
Temp2Handle = None
RefrigerantHandle = None
Pressure1Handle = None
Pressure2Handle = None
VacuumHandle = None
HaltOnError = True

def main():
    # test for operating system name
    if (os.name == "nt"):
        comport = "COM" + str(COMPORT)
    else:
        comport = "/dev/ttyS" + str(COMPORT-1)


    # get the serial port open
    theport.port = comport
    theport.baudrate = 115200
    theport.timeout = 3
    theport.open()
    # wait a bit otherwise the buffer won't be accurate
    time.sleep (0.25)
    theport.flush()

    #WriteRead ("AT+UFACTORY")
    WriteRead ("AT+UBTCM=2")
    WriteRead ("AT+UBTDM=3")
    WriteRead ("AT+UBTPM=2")
    WriteRead ("AT+UBTLE=2")                    # 2 is peripheral
    WriteRead ("AT+UDSC=0,0")                   # turn off SPS server to increase GATT characteristics capability
    WriteRead ("AT+UBTLECFG=26,2")              # fiddle with MTU size - as above.
    WriteRead ("AT+UBTLN=""REFCOperipheralserver""")
    WriteRead ("AT+UBTLEDIS=REFCO_Ltd,CLA,6.12,1")
    WriteRead ("AT&W")                          # reset 1
    WriteRead ("AT+CPWROFF")                    # reset 2
    #
    # Most of the following few lines can be set with the UBTLEDIS command,
    # and doing so below seems to create a duplicate service, at least on BLE Scanner on Android...
    #
    # # set up device information service
    # WriteRead ("AT+UBTGSER=180A")               # service (180A = Device Info)
    # WriteRead ("AT+UBTGCHA=2A23,10,1,1")        # characteristic System ID
    # WriteRead ("AT+UBTGCHA=2A24,10,1,1")        # characteristic Model Number String
    # WriteRead ("AT+UBTGCHA=2A25,10,1,1")        # characteristic Serial Number String
    # #WriteRead ("AT+UBTGCHA=2A26,10,1,1")        # characteristic Firmware Revision String
    # #WriteRead ("AT+UBTGCHA=2A27,10,1,1")        # characteristic Hardware Revision String
    # mfg_name_handle  = \
    # WriteRead ("AT+UBTGCHA=2A29,10,1,1")        # characteristic Manufacturer Name String
    # print ("handle of manufacturer name string is  : " + str(mfg_name_handle))

    

    RefcoService()

    #BatteryService()

    #Here we want to connect with a smartphone or an other ble device
    print ('Please connect smart-phone to REFCOperipheralserver')
    MessageLoop()
   





def WriteRead(stringIn):
    global transactionglobal, Temp1Handle, Temp2Handle
    returnvalue=""
    answer =""
    print()
    print ("Transaction " + str(transactionglobal))
    transactionglobal = transactionglobal+1
    print ("OUT: " + stringIn)
    #stringIn = stringIn + "\r"
    theport.write(stringIn.encode() + b'\r')
    # read output from NINA until OK or ERROR
    while ((answer != "OK") and (answer != "ERROR")):
        answer = theport.readline().rstrip().decode()
        print ("IN:  " + answer)

        if (HaltOnError):
            if (answer.upper() == "ERROR"):
                exit()

        # if this is defining a characteristic, grab the handle for later use
        if (regex.match (answer)):
            returnvalue = int(answer.split(':')[1].split(',')[0])
    
    # special case: wait for "+STARTUP" afterwards if the command was CPWROFF
    if (stringIn.upper() == "AT+CPWROFF"):
        while (answer.upper() != "+STARTUP"):
            try:
                answer = theport.readline().rstrip().decode()
                print ("IN: " + answer)
            finally:
                pass

    return returnvalue






def MessageLoop():
    timeout = False
    global theport
    SendNotifications = False
    message=""
    ConnectionCounter = 1

    theport.timeout = 1
    while (1):
        # if connected, send notifications to show something changing
        if (SendNotifications):
            print ("Send notifications {0}".format(ConnectionCounter))
            ConnectionCounter = ConnectionCounter + 1
            # refrigerant name
            dastring = "AT+UBTGSN=0,{0},{1}".format(RefrigerantHandle,  str(codecs.encode(bytearray("R410A", "ascii"), "hex"), "ascii"))
            WriteRead (dastring)
            # temperature 1
            TemperatureString = "{0} deg C".format (-40 + ConnectionCounter % 100)
            dastring = "AT+UBTGSN=0,{0},{1}".format(Temp1Handle,  str(codecs.encode(bytearray(TemperatureString, "ascii"), "hex"), "ascii"))
            WriteRead (dastring)
            print ("")

        message = theport.readline().rstrip().decode()
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

        # Connection notification event
        if (message[0:9] == '+UUBTACLC'):
            print ('ACL connection completed')
            if (not SendNotifications):
                SendNotifications = True
                time.sleep(1)
            continue

        # Write request
        if (message[0:8] == '+UUBTGRW'):
            print ('request to write')
            # if (not SendNotifications):
            #     SendNotifications = True
            #     time.sleep(1)
            continue

        # Read request
        if (message[0:8] == '+UUBTGRR'):
            print ('request to read')
            ReadRequest(message)
            if (not SendNotifications):
                SendNotifications = True
                time.sleep(1)
            continue

        # Disconenction notification event
        if (message[0:9] == '+UUBTACLD'):
            print ('ACL disconnected')
            # don't send notifications when not connected!
            SendNotifications = False
            continue






def BatteryService():
    # setup  battery service
    print ("Battery Service set-up: BEGIN")
    WriteRead ("AT+UBTGSER=180F")                                           # Battery Service
    WriteRead ("AT+UBTGCHA=2A19,10,1,1")                                    # Battery Level
    print ("Battery Service set-up: END")




def RefcoService():
    global Temp1Handle, Temp2Handle, Pressure1Handle, Pressure2Handle, RefrigerantHandle, VacuumHandle
    #setup device data service  # use UUID without connecting line
    WriteRead ("AT+UBTGSER=b0897c037fdd42a499abef47e3fe574f")
    #WriteRead ("AT+UBTGCHA=34832c10687d4eedb17f8b14f5ce70ea,12,1,1")        # Device State
    #WriteRead ("AT+UBTGCHA=854abe1146474a598fd2062278a6b691,12,1,1")        # Device Alarms
    #WriteRead ("AT+UBTGCHA=efa28478f59f431b832c89df618f4de2,12,1,1")        # Reader Time Period
    #WriteRead ("AT+UBTGCHA=5136a9ae032d4f16a9462a062abf6b85,12,1,1")        # Number of Connected Devices
    #WriteRead ("AT+UBTGCHA=7e6613f156fe46719c01f6605d5643f5,12,1,1")        # Transmitter Power (error in GATT definition confusing TX Power with RSSI)
    #WriteRead ("AT+UBTGCHA=775bf19859854a7596e32001ca1eba83,12,1,1")        # URL
    RefrigerantHandle = \
    WriteRead ("AT+UBTGCHA=a76f5dc0ba6648a5b5db193f77bf9cdb,12,1,1,{0}".format(StrToByteArray("R410A")))        # Refrigerant Name
    WriteRead ("AT+UBTGDES=ABCD,1,1,{0}".format(StrToByteArray("Refrigerant")))
    #WriteRead ("AT+UBTGCHA=2a840c865ad742d6b0d0733ff134c215,12,1,1")        # Device Temperature Unit
    #WriteRead ("AT+UBTGCHA=3967993db8f84cacbddf65c38e452592,12,1,1")        # Device Pressure Unit
    #WriteRead ("AT+UBTGCHA=c124f471567d40e89d7a761dd2731fa7,12,1,1")        # Device Vacuum Unit
    #WriteRead ("AT+UBTGCHA=979916f01fcd4bb89f79947cc0537f4d,12,1,1")        # Device Weight Unit
    #WriteRead ("AT+UBTGCHA=e780891363cb46b79898faa82dd4308f,12,1,1")        # Device Rotational Speed Unit
    #WriteRead ("AT+UBTGCHA=0af20aa48de1424da2dfc908b7f27b96,12,1,1")        # Device Valve Status
    Temp1Handle = \
    WriteRead ("AT+UBTGCHA=dd5ef8d7f96a42d4ba4cf4028a7232f5,12,1,1,{0}".format( StrToByteArray("0 C")))         # Device Temperature 1 Value
    Temp2Handle = \
    WriteRead ("AT+UBTGCHA=d4246dc425a040e0b34f45655882aa05,12,1,1,{0}".format(StrToByteArray("100 C")))        # Device Temperature 2 Value
    Pressure1Handle = \
    WriteRead ("AT+UBTGCHA=a4ac522539734fb987e5e8d86ff0a528,12,1,1,{0}".format(StrToByteArray("-10 bar")))      # Device Pressure 1 Value
    Pressure2Handle = \
    WriteRead ("AT+UBTGCHA=8739,12,1,1,{0}".format(StrToByteArray("20 bar")))       # Device Pressure 2 Value
    # WriteRead ("AT+UBTGCHA=87395d5d16774d6daa5a8242614c09d6,12,1,1,{0}".format(StrToByteArray("20 bar")))       # Device Pressure 2 Value
    # WriteRead ("AT+UBTGCHA=ef6111aec3ed4925af6e2f4c7183774b,12,1,1")        # Device Vacuum Value
    # #WriteRead ("AT+UBTGCHA=95ab2f3ccc0640d0a23741c3a9f0ac40,12,1,1")        # Device Weight Value
    # #WriteRead ("AT+UBTGCHA=c31201094d5e4d4b848de80ad27aa91e,12,1,1")        # Device Rotatational Speed Value
    # #WriteRead ("AT+UBTGCHA=bcbacc6c2c394d40ae3fc158c7216ec8,12,1,1")        # Device Set Value
    # WriteRead ("AT+UBTGCHA=619b13b76fb1492a98a24fdfb85970c7,12,1,1")        # Device Date
    # WriteRead ("AT+UBTGCHA=271cb57aa96c44e382eddb9443591c27,12,1,1")        # Device Time





def ReadRequest (StringIn):
    global RefrigerantHandle, Temp1Handle, Temp2Handle, Pressure1Handle, Pressure2Handle, VacuumHandle
    print ("Read Request service routine")
    print ("Message from Nina BLE: ""{0}""".format(StringIn))
    
    handle = StringIn.split(",")[1]
    if ( handle == str(RefrigerantHandle)):
        # dastring = "AT+UBTGRR={0},{1}".format(RefrigerantHandle,  str(codecs.encode(bytearray("R410A", "ascii"), "hex"), "ascii"))
        dastring = "AT+UBTGRR={0},{1}".format("0",  str(codecs.encode(bytearray("R410A", "ascii"), "hex"), "ascii"))
        WriteRead (dastring)
        return

    if (handle == str(Temp1Handle)):
        # currently send a random string based on the time in seconds since epoch
        TemperatureString = "{0} deg C".format (-40 + calendar.timegm(time.gmtime()) % 100)
        # dastring = "AT+UBTGRR={0},{1}".format(Temp1Handle,  str(codecs.encode(bytearray(TemperatureString, "ascii"), "hex"), "ascii"))
        dastring = "AT+UBTGRR={0},{1}".format("0",  str(codecs.encode(bytearray(TemperatureString, "ascii"), "hex"), "ascii"))
        WriteRead (dastring)
        return

    if (handle == str(Temp2Handle)):
        # currently send a random string based on the time in seconds since epoch
        TemperatureString = "{0} deg C".format (-40 + calendar.timegm(time.gmtime()) % 100)
        # dastring = "AT+UBTGRR={0},{1}".format(Temp2Handle,  str(codecs.encode(bytearray(TemperatureString, "ascii"), "hex"), "ascii"))
        dastring = "AT+UBTGRR={0},{1}".format("0",  str(codecs.encode(bytearray(TemperatureString, "ascii"), "hex"), "ascii"))
        WriteRead (dastring)
        return
    # return


# convert a string to a hex "byte array" of the type used by uBlox AT commands.
def StrToByteArray (InString):
    return str(codecs.encode(bytearray(InString, "ascii"), "hex"), "ascii")

# execute main() function
main()



# str(codecs.encode(b"Hello", "hex"), "ascii")
