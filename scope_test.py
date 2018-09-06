#!/usr/bin/python

class Characteristic:
    """GATT characteristic"""
    handle = None       # value returned by +UBTGCHA command
    UUID = None         # value given to +UBTGCHA command
    ServiceOwner = None # GAP handle of parent service
    value = None        # characteristic value
    def f (self):
        return "Hello world"
    # def __init__(self):
    #     #self.UUID = 0xFF
    #     print ("I am a constructor, by any other name")
    def __init__(self, UUIDval=None, valueVal=None):
        self.UUID = UUIDval
        self.value = valueVal



def scope_test():
    def do_local():
        spam = "local spam"
        print ("within the function, the variable is ", spam)

    def do_nonlocal():
        nonlocal spam
        spam = "nonlocal spam"

    def do_global():
        global spam
        spam = "global spam"

    spam = "test spam"
    do_local()
    print ("After local assignment: ", spam)
    do_nonlocal()
    print ("After nonlocal assigmment: ", spam)
    do_global()
    print ("After global assigment: ", spam)

scope_test()
print ("In global scope: ", spam)

        
valinst = Characteristic(UUIDval=99)
print ("The UUID is " , valinst.UUID)
print ("The val  is " , valinst.value)
if (valinst.value == None):
    print ("No value yet")

