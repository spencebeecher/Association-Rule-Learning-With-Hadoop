#!/usr/bin/python

import sys

#for each pattern create the class rule.  we still will have to scale by the 
# pattern in the left hand side
for line in sys.stdin:
    line = line.strip().split('\t')
    pattern = line[0].split(',')
    if len(pattern) > 1:
        for p in pattern:
            print "%s\t%s.%s" % (','.join( sorted([x for x in pattern if x != p])),','.join(pattern),line[1])

#emit the original pattern, this is used by the reducer to scale the 
#  left hand side by the approprate ammount
    print "%s\t%s" % (line[0],line[1])

