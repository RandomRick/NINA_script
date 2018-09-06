#!/usr/bin/python

class Fred:
    def __init__(self,
            name=None,
            a="default name",
            UUID = None
            ):
        self.name = name
        self.a = a
        self.UUID = UUID
    def PrintShit(self):
        print ("I am a wibble")
    def UUIDdefined (self):
        if (self.UUID == None):
            return False
        return True


b = Fred("wibble")
c = Fred()
b.a = "I am a variable"

b.PrintShit()
# c.UUID = "ABC"
if (c.UUIDdefined()):
    print("The UUID is \"{}\"".format (c.UUID))
else:
    print ("It has no UUID")
print ("It's ", c.UUIDdefined())
