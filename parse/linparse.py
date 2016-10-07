#!/usr/bin/python3

'''
date: 10/07/2016
author: Jimmy Jin

This script:
    1) Creates classes for neatly representing bridge hands, play, and bids
    2) Provides functions for parsing BBO .lin files
'''

import re
from collections import deque

SUITS = {0:'S', 1:'H', 2:'D', 3:'C'}
PLAYERS = {0:'E', 1:'S', 2:'W', 3:'N'}
CARDMAP = {'2':2, '3':3, '4':4, '5':5, '6':6, '7':7, '8':8, '9':9, 'T':10, 'J':11, 'Q':12, 'K':13, 'A':14}

class Card(object):
    """Represents a standard playing card.
    
    Attributes:
      suit: integer 0-3
      rank: integer 1-13
    """

    suit_names = ['C', 'D', 'H', 'S']
    rank_names = [None, None, '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

    def __init__(self, suit=0, rank=2):
        self.suit = suit
        self.rank = rank

    def __str__(self):
        """Returns a human-readable string representation."""
        return '%s%s' % (Card.rank_names[self.rank], Card.suit_names[self.suit])

    def __eq__(self, other):
        return (self.suit == other.suit and self.rank == other.rank)

    def __cmp__(self, other):
        """Compares this card to other, first by suit, then rank.

        Returns a positive number if this > other; negative if other > this;
        and 0 if they are equivalent.
        """
        t1 = self.suit, self.rank
        t2 = other.suit, other.rank
        return cmp(t1, t2)

class Hand(object):
    """Represents a deck of cards.

    Args:
        initial: list of Card objects

    Attributes:
        cards: list of Card objects.
    """
    
    def __init__(self, initial=None):
        if initial is None:
            self.cards = []
        else:
            self.cards = initial

    def __str__(self):
        res = []
        for card in self.cards:
            res.append(str(card))
        return ','.join(res)

    def has(self, other):
        '''Checks whether a Card (other) is in hand'''
        return (other in self.cards)

    def add_card(self, card):
        """Adds a card to the deck."""
        self.cards.append(card)

    def remove_card(self, card):
        """Removes a card from the deck."""
        self.cards.remove(card)

    def pop_card(self, i=-1):
        """Removes and returns a card from the deck.

        i: index of the card to pop; by default, pops the last card.
        """
        return self.cards.pop(i)

    def sort(self):
        """Sorts the cards in ascending order."""
        self.cards.sort()

def full_hand():
    ''' Return a full (52-card) Hand object
    '''
    fullhand = Hand()
    for suit in range(4):
        for rank in range(2,15):
            fullhand.cards.append(Card(suit,rank))

    return fullhand

class BridgeHand:
    '''
    players: dict (keys: dirs)
    hands: dict (keys: dirs) of Hand objects 
    bids: list
    play: list of dicts (keys: dirs) 
    contract: str
    declarer: str (dir)
    doubled: {0,1,2}
    '''

    def __init__(self, players, hands, bids, play, contract, declarer, doubled, vuln):
        self.players = players
        self.hands = hands
        self.bids = bids
        self.play = play
        self.contract = contract
        self.declarer = declarer
        self.doubled = doubled
        self.vuln = vuln

    # might want to define a method for checking equality here

def get_players(lin):
    ''' Parses .lin files for the players

    args:
        lin: a .lin-formatted string

    returns:
        players: dict of players (keyed by direction)
    '''

    p_match = re.search('pn\|([^\|]+)', lin)
    p_str = p_match.group(1).split(',')

    # player order is S,W,N,E
    players = {'S':p_str[0], 'W':p_str[1], 'N':p_str[2], 'E':p_str[3]}
    return(players)

def get_initial_hands(lin):
    ''' Parses .lin files for initial hands

    args:
        lin: a .lin-formatted string

    returns:
        hands: dict of Hand objects (keyed by direction)
    '''
    def convert_cards(cstring):
        ''' Breaks up the .lin-format card blob by suit

        args:
            cstring: str (.lin-format card blob)

        returns:
            hand: Hand object
        '''

        hand = Hand()

        card_match = re.search('S([^HDC]*)H([^DC]*)D([^C]*)C(.*)', cstring)
        for s in range(4):
            for v in card_match.group(s+1):
                hand.add_card(Card(suit=s, rank=CARDMAP[v]))

        return hand 


    # get the hands of S, W, N
    hands = {}

    h_match = re.search('md\|([^\|]+)', lin)
    h_str = h_match.group(1).split(',')
    h_str[0] = h_str[0][1:]

    hands['S'] = convert_cards(h_str[0])
    hands['W'] = convert_cards(h_str[1])
    hands['N'] = convert_cards(h_str[2])
   
    # recover the hand of E
    hands['E'] = full_hand()
    for dir in 'SWN':
        for card in hands[dir].cards:
            assert card in hands['E'].cards
            hands['E'].remove_card(card)

    return(hands)

def get_bids(lin):
    ''' Parses .lin files for bid information 

    args:
        lin: a .lin-formatted string

    returns: triple (x,y,z) of:
        x (list): bid sequence
        y (str): declarer
        z (tuple): str (contract), {0,1} (doubled or not)
    '''

    # returns list of bids, declarer and contract
    # in the ACBL boards the dealer is always East

    # extract list of bids
    bids_match = re.search('mb\|(.+?)\|pg', lin)
    bids = bids_match.group(1).split('|mb|')
   
    # check for passout
    if (len(bids) == 4) and (bids[0] == 'p'):
        return bids, None, 'PO'

    # set the declarer: 0 = East (declarer)
    # note: adjust by -5 because len(bids) > 0 
    declarer =  PLAYERS[(len(bids)-5)%4]
    
    # get the contract and return
    doubles = []
    i = 1
    while (bids[-i] == 'd' or bids[-i] == 'p'):
        doubles.append(bids[-i])
        i += 1

    raw = bids[-i]
    if 'd' not in bids:
        return bids, declarer, (raw, 0)
    else:
        return bids, declarer, (raw, doubles.count('d'))


#####################################    
def parse_linfile(linfile):
#####################################    
    
    with open(linfile, 'r') as f:
        lin=f.read()
    
    players = get_players(lin)
    hands = get_initial_hands(lin)
    bids, declarer, (contract, doubled) = get_bids(lin)
    
    # need bids to process play
    play_match = re.search('pc\|(.+)\|pg\|\|', lin)
    play_str = play_match.group(1).split('|pg|')

    # split into cards
    suitlist = ['E','S','W','N']
    itersuit = deque('ESWN')
    rotated = itersuit.rotate(-(suitlist.index(declarer)+1))
    play = []
    for trick in play_str:
        cards = trick.split('|pc|')
        play.append(dict())
        for s in itersuit:
            play[-1][s] = cards.pop(0)

    return BridgeHand(players, hands, bids, play, contract, declarer, doubled, None)





