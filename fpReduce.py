#!/usr/bin/python
import sys


#aggregate values of patterns
# a,b,c : 1
# a,b,c : 4
#becomes-
#         a,b,c : 5
prevKey = None
value = 0 
for line in sys.stdin:
    kv = line.split('\t')
    if prevKey == kv[0]:
        value+=int(kv[1])
    else:
        if prevKey != None:
            print "%s\t%d" % (prevKey,value)
        prevKey = kv[0]
        value=int(kv[1])
if prevKey != None:
    print "%s\t%d" % (prevKey,value)


