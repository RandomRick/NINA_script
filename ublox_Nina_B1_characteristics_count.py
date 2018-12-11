#!/usr/bin/python
# Right now, the message loop waits until ALL characteristics have been told to send notifcations
# (via UUBTGRW events).
# the code could be structured to send out notifications as soon as ANY of the characteristics have been
# set up on the smart phone.  But it needs changes. This is because if I do it this way now, I begin
# sending UBTGSN commands, and some in-coming events get swallowed in the WriteRead function, because it's 
# only looking for OK or ERROR.
# it would therefore be necessary to detect asynchronous events being received in WriteRead, and to
# inject them into the message loop.
import sys,os, serial, os, time, io, re
#import _thread as thread
#import threading
import binascii, codecs
import calendar # for creating timestamps, etc.
import uuid

#globals
COMPORT=13
theport = serial.Serial()
regex = re.compile (r'.*CHA:\d\d,\d+')
transactionglobal = 0
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
    print ("DEBUG: Setting up central + peripheral mode:")
    WriteRead ("AT+UBTLE=3")                    # 2 is peripheral, 3 is dual-mode
    # print ("DEBUG: Setting number of permissible conntions to 3:")
    WriteRead ("AT+UBTCFG=2,3")                 # 1st param=1 mean "max BLE links", 2nd param = num of links
    WriteRead ("AT+UDSC=0,0")                   # turn off SPS server to increase GATT characteristics capability
    WriteRead ("AT+UBTLECFG=26,2")              # fiddle with MTU size - as above.
    WriteRead ("AT+UBTLN=""REFCOperipheralserver""")
    WriteRead ("AT+UBTLEDIS=REFCO_Ltd,CLA,6.12,1")
    WriteRead ("AT&W")                          # reset 1
    WriteRead ("AT+CPWROFF")                    # reset 2
    #
    
    time.sleep (1)

    WriteRead ("AT+UBTGSER=b0897c037fdd42a499abef47e3fe574f")

    for x in range (1,100):
        print ("Defining Characteristic Number {0}".format (x))
        WriteRead ("AT+UBTGCHA={0},12,1,1,{1},0,20".format(uuid.uuid4().hex, StrToByteArray("0 KG")))       # Scale reading (Mass)






def WriteRead(stringIn):
    global transactionglobal#, Temp1Handle, Temp2Handle
    #global AsyncEvents
    debugplease = True
    returnvalue=""
    answer =""
    if debugplease:
        print()
        print ("Transaction " + str(transactionglobal))
        print ("OUT: " + stringIn)
    transactionglobal = transactionglobal+1
    #stringIn = stringIn + "\r"
    theport.write(stringIn.encode() + b'\r')
    # read output from NINA until OK or ERROR
    while ((answer != "OK") and (answer != "ERROR")):
        answer = theport.readline().rstrip().decode()
        if debugplease: print ("IN:  " + answer)

        # if answer[0:3] == "+UU":
        #     # we've got an event popped up that's nothing to do with the current message
        #     AsyncEvents.append(answer)
        #     print("DEBUG:")
        #     print  ("DEBUG: Parking this event for later: ", answer)
        #     print ("DEBUG:")

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
                if debugplease:  print ("IN: " + answer)
            finally:
                pass

    return returnvalue




# convert a string to a hex "byte array" of the type used by uBlox AT commands.
def StrToByteArray (InString):
    return str(codecs.encode(bytearray(InString, "ascii"), "hex"), "ascii")

# execute main() function
main()



# str(codecs.encode(b"Hello", "hex"), "ascii")
