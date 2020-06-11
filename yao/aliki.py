import random
import json
import sys
import os
from pprint              import pprint
from hashlib             import sha256
from operator            import xor

# Implement BOB #

bool_op = {
    "AND" : lambda x, y: x & y,
    "OR"  : lambda x, y: x | y,
    "XOR" : lambda x, y: x ^ y,
}

assoc = {} # Dictionary of labels and their corresponding value
keys  = [] # Array of Alice's keys


def ret_val(res):
    for gid, v in res.items():
        for value in v:
            try:
               # pprint("gid: " + str(gid) + " - " + str(assoc[value]))
                return assoc[value]
            except:
               # print('err')
               pass


def byte_xor(ba1, ba2):
    return bytes([_a ^ _b for _a, _b in zip(ba1, ba2)])

def unary_gate(x, gid):

    # Constructing the labels
    k0x = bytes(os.urandom(32))
    k1x = bytes(os.urandom(32))
    k0z = bytes(os.urandom(32))
    k1z = bytes(os.urandom(32))

    encr    = {}
    encr[0] = sha256(k0x + gid).digest() 
    encr[1] = sha256(k1x + gid).digest()

    assoc   = {} # set containing resutls of operation
    c       = [] # Garbled table
    counter = 0
    tmp     = 0
    for i in range(0,2):
        res = not(int(x))
        if   res == 1:
            assoc[i] = 1
            tmp = k1x
        elif res == 0:
            assoc[i] = 0
            tmp = k0x
        
        c.append(byte_xor(encr[i], tmp)) 

    random.shuffle(c) # Permute the results
    print(assoc)

    keys = {}
    keys['x'] = k1x

    # Returns #
    # 1. the garbled table encrypted #
    # 2. the input value encrypted  #
    return c, keys 

def binary_gate(x, y, gid, gtype):

    global assoc
    global keys

    # Constructing the labels
    k0x  = bytes(os.urandom(32)); assoc[k0x] = 0
    k1x  = bytes(os.urandom(32)); assoc[k1x] = 1
    k0y  = bytes(os.urandom(32)); assoc[k0y] = 0
    k1y  = bytes(os.urandom(32)); assoc[k1y] = 1
    k0z  = bytes(os.urandom(32)); k1z  = bytes(os.urandom(32))

    # Hash-Digests of inputs
    encr    = {}
    encr[0] = sha256(k0x + k0y).digest() 
    encr[1] = sha256(k0x + k1y).digest()
    encr[2] = sha256(k1x + k0y).digest()
    encr[3] = sha256(k1x + k1y).digest()

    c = [] # Garbled table

    # Connect the labels with the actual values
    assoc[k0z] = (0)
    assoc[k1z] = (1)

    if   gtype == 'AND':                 #  AND  #
        c.append(byte_xor(k0z, encr[0])) # 0 0 0 # 
        c.append(byte_xor(k0z, encr[1])) # 0 1 0 #
        c.append(byte_xor(k0z, encr[2])) # 1 0 0 #
        c.append(byte_xor(k1z, encr[3])) # 1 1 1 #

    elif gtype == 'OR':                  #   OR  #
        c.append(byte_xor(k0z, encr[0])) # 0 0 0 # 
        c.append(byte_xor(k1z, encr[1])) # 0 1 1 #
        c.append(byte_xor(k1z, encr[2])) # 1 0 1 #
        c.append(byte_xor(k1z, encr[3])) # 1 1 1 #

    elif gtype == 'XOR':                 #  XOR  #
        c.append(byte_xor(k0z, encr[0])) # 0 0 0 #  
        c.append(byte_xor(k1z, encr[1])) # 0 1 1 #
        c.append(byte_xor(k1z, encr[2])) # 1 0 1 #
        c.append(byte_xor(k0z, encr[3])) # 1 1 0 #

    random.shuffle(c) # Permute the results


    # Alice's input
    if   x == 1: keys.append(k1x) 
    elif x == 0: keys.append(k0x)
    if   y == 1: keys.append(k1y) 
    elif y == 0: keys.append(k0y)

    # Returns #
    # 1. the garbled table encrypted #
    # 2. the input values encrypted  #
    return c, keys 

def full_adder():
    """

     Full adder Implementation
     2 XOR Gates
     2 AND Gates
     1 OR  Gate
     Input:  A, B, Cin
     Output: S, Cout


    """
    a = \
        """
        #  TRUTH TABLE  #
        # X Y Ci | Co S #
        # 0 0 0  | 0  0 #
        # 0 1 1  | 1  0 #
        # 1 0 0  | 0  1 #
        # 1 0 1  | 1  0 #
        # 1 1 0  | 1  0 #
        # 1 1 1  | 1  1 #
        # # # # # # # # # 
        """
    get_bin = lambda x: format(x, 'b')

    # Inputs
    x = 0   
    y = 1  
    cin = 0

    seq = ['XOR', 'XOR', 'AND', 'AND', 'OR']
    r_values = [0,1,2]

    
    global assoc
    garbled_tables = {}
    key_table      = {}

    # 1st XOR
    garbled_table, key_table[0] = binary_gate(x, y, 0, seq[0])
    garbled_tables[0] = garbled_table
    res = bob(garbled_tables, key_table)
    r_values[0] = ret_val(res)
    del(garbled_tables[0])


    # 2nd XOR
    garbled_table, key_table[1] = binary_gate(r_values[0], cin, 1, seq[1])
    garbled_tables[1] = garbled_table
    res = bob(garbled_tables, key_table)
    r_values[0] = ret_val(res)
    print(r_values[0])
    del(garbled_tables[1])

    # 1st AND
    garbled_table, key_table[2] = binary_gate(r_values[0], cin, 2, seq[2])
    garbled_tables[2] = garbled_table
    res = bob(garbled_tables, key_table)
    val = ret_val(res)
    del(garbled_tables[2])

    # 2nd AND
    garbled_table, key_table[3] = binary_gate(x, y, 3, seq[3])
    garbled_tables[3] = garbled_table
    res = bob(garbled_tables, key_table)
    r_values[1] = ret_val(res)
    del(garbled_tables[3])

    # OR
    garbled_table, key_table[4] = binary_gate(r_values[0], r_values[1], 4, seq[4])
    garbled_tables[4] = garbled_table
    res = bob(garbled_tables, key_table)
    r_values[2] = ret_val(res)
    print(r_values[2])
    del(garbled_tables[4])
    


    # Finding the key
    
    #garbled_tables, key_table = {}, {}

    #for i in range(2, 5):
    #    garbled_table, key_table[i] = binary_gate(x, y, i, seq[i])

    #    garbled_tables[i] = garbled_table

    #res = bob(garbled_tables, key_table)
    ## Finding the key
    #for gid, v in res.items():
    #    for value in v:
    #        try:
    #            pprint("gid: " + str(gid) + " - " + str(assoc[value]))
    #            break
    #        except:
    #            print('err')



def aliki():

    global assoc
    key_table = {}
    garbled_tables = {}             # Permuted garbled tables to be sent to bob

    x      = 0
    y      = 1
    g_id   = 1
    g_type = 'AND'

    garbled_table, key_table[g_id] = binary_gate(x, y, g_id, g_type)
    garbled_tables[g_id] = garbled_table

    res = bob(garbled_tables, key_table)
    # Finding the key
    for gid, v in res.items():
        for value in v:
            try:
                pprint("gid: " + str(gid) + " - " + str(assoc[value]))
                break
            except:
                print('err')

def bob(table, inputs):
    cipher_dict = {}
    ciphers     = []
    
    for gid, v in table.items():
        x = inputs[gid].pop(0)
        y = inputs[gid].pop(0)
        for i in range(4):
            ciphers.append(byte_xor(sha256(x + y).digest(), v[i]))

        cipher_dict[gid] = ciphers
        ciphers = [] # 

    return cipher_dict


full_adder()
