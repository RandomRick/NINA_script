#!/usr/bin/python

# let's see how exceptions work!

class A:
    def StaticFn(self):
        try:
            for i in range(5):
                print ("i =", i)
                print ("1/i = {0:+10.8f".format (1.0/i))
        except Exception as thisone:
            print ("Exception in StaticFn", thisone)
            raise thisone
a = 1
b = 0
for b in range (5):
    try:
        print ("b = {0}".format (b))
        print ("a/b = {0:+010.8f}".format (a/b))
    except:
        print ("An exception was raised!")

try:
    classintance = A()
    classintance.StaticFn()
except Exception as thisone:
    print ("Another exception")
    print ("Exception = ", thisone)



