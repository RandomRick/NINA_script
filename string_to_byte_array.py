#!/usr/bin/python

import sys
import codecs


if (len(sys.argv) < 2):
    ToConvert = input("Please enter a string to convert:")
else:
    ToConvert = sys.argv[1]

if (len(ToConvert) < 1):
    print ("Can't really do much with that. Exiting.")
    quit()

print ("I am going to convert \"{0}\"".format(ToConvert))
print ( str(codecs.encode(bytearray(ToConvert, "ascii"), "hex"), "ascii").upper() )



