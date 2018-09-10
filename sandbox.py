#!/usr/bin/python


class Fred:
    a = None
    def __init__(self, ain):
        self.a = ain

    def DoStuff(self):
        Fred.a = 99

print ("Fred.a = ",Fred.a)

classinstance = Fred(55)
print ("classinstance.a = ",classinstance.a)
print ("Fred.a = ",Fred.a)

classinstance.DoStuff()
print ("classinstance.a = ",classinstance.a)
print ("Fred.a = ",Fred.a)

classinstance.a = 100
print ("classinstance.a = ",classinstance.a)
print ("Fred.a = ",Fred.a)
