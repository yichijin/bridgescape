#!/usr/bin/python3

'''
analyze.py

Last updated: 7/20/17
Author: Jimmy Jin

This script provides tools for analyzing the BridgeHand objects returned
from parsing the .lin files.
'''
    

from collections import Counter

SUITMAP = {'C':0, 'D':1, 'H':2, 'S':3}

def detect_incomplete(b):
    '''
    A non-trivial proportion of the .lin files are incomplete--
    that is, they are missing key information -OR- (more commonly)
    they have incomplete play information without a claimed tricks flag

    This is a small convenience function for indicating whether a
    board is incomplete.

    inputs:
        b: a BridgeHand object

    returns:
        bool
    '''

    
    return (b is None) or (len(b.play)<13 and b.claimed==False)

def partner(pos):
    '''
    Helper function to return the position of the partner of 'pos'

    input:
      pos: str (position)

    return:
      str
    '''
    dirs = ['E','S','W','N']
    pos_index = dirs.index(pos)

    return dirs[(pos_index+2)%4]
  

def hcp(hand, shortness=False):
    '''
    Count the HCP in a hand by the usual 4/3/2/1 scale.
    If shortness=True, add points for suit shortness.

    inputs:
        hand: a Hand object

    returns:
        int
    '''

    # if shortness is on, get shortness points
    voids = 0
    sps = 0

    if shortness==True:
        sp_list = [3,2,1]
        
        # pass list of card suits to collections.Counter
        vals = list(map(lambda x: x.suit, hand))
        counts = Counter(vals)

        void = (4-len(counts))*3
        sps = sum([sp_list[v] for v in counts.values() if v<3])

    # get normal hcps
    hcps = 0
    hcp_list = [1,2,3,4]

    facecards = [card.rank for card in hand if card.rank>10]
    hcps = sum([hcp_list[x-11] for x in facecards])

    return hcps+sps+voids

        
