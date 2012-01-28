#!/usr/bin/python

import sys

'''into the reducer we get a list of entries in one of two formats:
    a,b\t2   

    OR  

    a,b\ta,b,c.1
    a,b\ta,b,d.1
    ....

the first type is the frequency of that pattern in the corpus
the second type's value is the frequency of that VALUE's pattern in the corpus

since both types make it to the reducer we can take a,b\t2 AND a,b\ta,b,c.1 to get:
a,b IMPLIES a,b,c .5
in other words a,b => c 50%
'''

prevKey = None
arr = []  
# by using a second sort we can get rid of keeping content in @arr 
# for class association rule mining this should not be a big deal

freq = 0
for line in sys.stdin:
    line = line.strip().split('\t')

    if line[0] != prevKey: #the current line is a new key, done with old
        if prevKey != None:
            for item in arr:
                print "%s\t%s   %f" %(prevKey,item[0],float(item[1])/freq)
        arr = []
        prevKey = line[0]

    if '.' in line[1]:#this is apart of a rule
        conditional = line[1].split('.')
        arr.append(conditional)
    else:#this is the frequency of the key
        freq = float(line[1])
        
