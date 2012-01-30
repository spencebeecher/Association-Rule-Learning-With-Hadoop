#!/usr/bin/python



'''
Copyright (c) 2011, phi
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met: 

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer. 
2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution. 

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation are those
of the authors and should not be interpreted as representing official policies, 
either expressed or implied, of the author.

'''
import sys
import itertools

class FPNode:
    def __init__(self,id, parent):
        self.frequency = 0
        self.id = id
        self.next = None
        self.children = dict()
        self.parent = parent
    
    def __str__(self):
        return "id:%s freq:%s" % (self.id, self.frequency)
    
    def add(self,pattern, index,tree):
        if len(pattern) == index+1 and self.id == pattern[index][0]:
            self.frequency += pattern[index][1]
        else:
            
            if not self.children.has_key(pattern[index+1][0]):
                n = FPNode(pattern[index+1][0],self)
                self.children[pattern[index+1][0]] = n
                tree.insert_header(n)
            self.frequency += pattern[index][1]
            self.children[pattern[index+1][0]].add(pattern,index+1,tree)
            
    def str_val(self, mappings):
        
        return self.get_str_val('',mappings)
        
            
    def get_str_val(self,spaces,mappings):
        accum = ''
        if not self.id == 'root':
            accum = '%s%s: %s' % (spaces, str(mappings[self.id].item), str(self.frequency))+'\n'
        else:
            accum = 'root\n'
        for _,v in self.children.items():
            accum += v.get_str_val(spaces+ '    ',mappings) 
            
        return accum 
                        
        
class HeaderTableItem:
    def __init__(self,id,item,frequency):
        self.id = id
        self.item = item
        self.node = None
        self.frequency = frequency
    def __str__(self):
        s = 'item: %s id: %s freq: %s- ' % (self.item,self.id,self.frequency)
        curr = self.node
        while curr != None :
            s += ' '+str(curr)
            curr = curr.next
        return s
            
 
def create_fp_tree(datasource,support):
   datasource = [[(y,1) for y in x] for x in datasource]
   return FPTree(datasource,support)

class FPTree:
    
    def __init__(self,datasource, support, base_tree = None):
        self.base_tree = base_tree == None and self or base_tree
        self.support = support
        self.root = FPNode('root',None)
        self.lookup = {}
        
        header = dict()
        for transaction in datasource:
            for item in transaction:
                if not item[0] in header.keys():
                    header[item[0]] = 0
                header[item[0]] += item[1]
        self.header_table=[]
        self.mapping_table = dict()
        for x in sorted([(value,key) for (key,value) in header.items() if value >= self.support], reverse= True):
            self.header_table.append(HeaderTableItem(len(self.header_table),x[1],x[0]))
            self.mapping_table[x[1]] = len(self.header_table) - 1
        
        for transaction in datasource:
            trans = [(self.mapping_table[x[0]],x[1]) for x in transaction if self.mapping_table.has_key(x[0])]
            trans.sort()
            
            if len(trans) > 0:
                if  not self.root.children.has_key(trans[0][0]):
                    self.root.children[trans[0][0]] = FPNode(trans[0][0], self.root)
                    self.insert_header(self.root.children[trans[0][0]])
                
                self.root.children[trans[0][0]].add(trans,0,self)
        for i in range(len(self.header_table)):
            self.lookup[self.header_table[i].item] = i
            
    def __str__(self):
        return self.root.str_val(self.header_table)
    
    def insert_header(self, n):
        curr = self.header_table[n.id].node
        if curr == None:
            self.header_table[n.id].node = n
        else:
            while curr.next != None :
                curr = curr.next
            curr.next = n
            
    def conditional_tree_datasource(self,currlink):
        patterns = []
        while currlink != None:
            support = currlink.frequency
            currnode = currlink.parent
            pattern = []
            while currnode != self.root:
                pattern.append((self.header_table[ currnode.id].item,support))
                currnode = currnode.parent
            if len(pattern) > 0:
                patterns.append( pattern)

            currlink = currlink.next
        return patterns
            
    def single_chain(self):
        curr = self.root
        while curr != None:
            if len(curr.children) > 1:
                return False
            if len(curr.children) == 0:
                return True
            curr = curr.children.values()[0]
        return True

    def sort_pattern(self, pattern):
        return sorted(pattern, key=lambda x: self.lookup[x])
        

    def fp_growth(self):
       for px in self.fp_growth_raw():
            yield (self.sort_pattern([item[0] for item in px]), min([item[1] for item in px])) 
    
    def fp_growth_raw(self, pattern = []):
        if self.single_chain():
            optional = []
            if len(self.root.children) > 0:
                curr = self.root.children.values()[0]
               
                while True:
                    optional.append((self.header_table[curr.id].item,curr.frequency))
                    if len(curr.children) > 0:
                        curr = curr.children.values()[0]
                    else:
                        break
            for i in range(1,len(optional)+1):
                for permpat in itertools.combinations(optional, i):
                    p = [x for x in permpat]
                    p.extend(pattern)
                    yield p 
        else:
            for x in range(len(self.header_table)-1,-1,-1):
                if self.support <= self.header_table[x].frequency:
                    pattern_base = [y for y in pattern]
                    pattern_base.append((self.header_table[x].item,self.header_table[x].frequency))
                    yield pattern_base
                    tree = FPTree(self.conditional_tree_datasource(self.header_table[x].node), self.support)
                    for px in tree.fp_growth_raw(pattern_base):
                        yield px



arr = []
#loop through records, every 10000 make a FP Tree and generate patterns
for line in sys.stdin:
    line = line.strip()
    if len(arr) > 10000:
	# create a tree from arr with minimum frequency 0
        t = create_fp_tree(arr,0) 
        for p in t.fp_growth():
            print  "%s\t%d" %  (','.join(sorted(p[0])),p[1])
            arr = []
    if '\t' in line:
        arr.append(line.split('\t')[1].split(","))

#flush any remaining records to a tree and generate patterns
if len(arr) > 0:    
    t = create_fp_tree(arr,0) 
    for p in t.fp_growth():
        print  "%s\t%d" %  (','.join(sorted(p[0])),p[1])



    
