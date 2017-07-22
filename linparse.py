#!/usr/bin/python3

'''
linparse.py

Last updated: 7/20/17
Author: Jimmy Jin

This script:
    1) Creates classes for neatly representing bridge hands, play, and bids
    2) Provides functions for parsing BBO .lin files
'''

import re
from collections import deque

PLAYERS = {0:'E', 1:'S', 2:'W', 3:'N'}
SUITMAP = {'C':0, 'D':1, 'H':2, 'S':3}
CARDMAP = {'2':2, '3':3, '4':4, '5':5, '6':6, '7':7, '8':8, '9':9, 'T':10, 'J':11, 'Q':12, 'K':13, 'A':14}

# for readability...
def rindex(list, elt):
    '''Return the reverse index of elt in list

    inputs:
        list: list
        elt: an element inside list

    outputs:
        int
    '''
    
    return len(list) - list[::-1].index(elt) -1
   

class Card(object):
    """Represents a standard playing card.
    
    Attributes:
      suit: integer 0-3
      rank: integer 2-14
      suitname: str in {'C','D','H','S'}
      rankname: str in {'2','3','4','5','6','7','8','9','10','J','Q','K','A'}

    Constructor takes:
      arg1: integer 0-3 corresponding to suit
      arg2: integer 2-14 corresponding to value
    """

    suit_names = ['C', 'D', 'H', 'S']
    rank_names = [None, None, '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

    def __init__(self, suit=0, rank=2):
        self.suit = suit
        self.rank = rank
        self.suitname = self.suit_names[suit]
        self.rankname = self.rank_names[rank]

    def __repr__(self):
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
    """Represents a hand/deck of cards.

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

    def __repr__(self):
        res = []
        for card in self.cards:
            res.append(str(card))
        return ','.join(res)

    def __getitem__(self, item):
        '''Implementing getitem so that we get iteration and slicing'''
        return self.cards[item]

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

class BridgeHand:
    '''
    players: dict (keys: dirs)
    hands: dict (keys: dirs) of Hand objects 
    bids: list
    play: list of dicts (keys: 'E', 'S', 'W', 'N', 'lead') 
    contract: str
    declarer: str (dir)
    doubled: {0,1,2}
    made: int
    '''

    def __init__(self, players, hands, bids, play, contract, declarer, doubled, vuln, made, claimed):
        self.players = players
        self.hands = hands
        self.bids = bids
        self.play = play
        self.contract = contract
        self.declarer = declarer
        self.doubled = doubled
        self.vuln = vuln
        self.made = made
        self.claimed = claimed

    # might want to define a method for checking equality here

def full_hand():
    '''
    Return a full (52-card) Hand object
    '''
    
    fullhand = Hand()
    for suit in range(4):
        for rank in range(2,15):
            fullhand.cards.append(Card(suit,rank))

    return fullhand

def convert_card(lincard):
    '''
    Convert lin-style 2-char notation to Card()
    '''
    
    linsuit = lincard[0]
    linval = lincard[1]
    return Card(SUITMAP[linsuit], CARDMAP[linval])

def get_trick_winner(cards, leader, trump=None):
    '''
    Returns the winner of a trick

    input:
        trick: length-4 dict (keys: dirs, values: Cards)
        leader: str
        trump: str

    returns:
        winner: str (direction)
        top: Card (winning card in the trick)
    '''
    
    if trump == 'N':
        trumpsuit = None
    else:
        trumpsuit = SUITMAP[trump]

    suitlist = ['E','S','W','N']
    suitlist.remove(leader)

    # default winner is leader's card
    winner = leader
    top = cards[leader]
    ledsuit = top.suit

    
    # if contract is NT, then trumpsuit == 'N' and the elif is skipped
    for dir in suitlist:
        if (cards[dir].suit == top.suit) & (cards[dir].rank > top.rank):
            top = cards[dir]
            winner = dir
        elif (cards[dir].suit == trumpsuit) & (top.suit is not trumpsuit):
            top = cards[dir]
            winner = dir

    return winner, top 


def rotate_to(dir, offset=0, list='ESWN'):
    '''
    Rotates a list (default 'ESWN') to start from a specified
    direction (going clockwise)

        args:
            dir: str
            offset: int (advance rotation by __)

        example:
            rotate_to('W', 1) rotates to the play order 'NESW'
    '''

    suits = ['E','S','W','N']
    rotation = suits.index(dir)+offset

    return list[rotation:] + list[:rotation]

def get_players(lin):
    '''
    Parses .lin files for the players. Returns None if 
    no players found.

    args:
        lin: a .lin-formatted string

    returns:
        players: dict of players (keyed by direction)

    '''

    p_match = re.search('pn\|([^\|]+)', lin)
    if not(p_match):
        return None
    
    p_str = p_match.group(1).split(',')

    # player order is S,W,N,E
    players = {'S':p_str[0], 'W':p_str[1], 'N':p_str[2], 'E':p_str[3]}
    return(players)

def get_initial_hands(lin):
    '''
    Parses .lin files for initial hands. Returns None if
    no hands found.

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

    h_match = re.search('\|md\|([^\|]+)', lin)
    if not(h_match):
        return None

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

def process_bids(lin):
    ''' Parses .lin files for bid information. Returns None
    if no bid information found.

    args:
        lin: a .lin-formatted string

    returns: triple (x,y,z) of:
        x (list): bid sequence
        y (str): declarer
        z (tuple): str (contract), {0,1} (doubled or not)
    '''

    # returns list of bids, declarer and contract
    # in the ACBL boards the dealer is always East

    # extract raw bid string 
    bids_match = re.search('mb\|(.+?)\|pg', lin)
    if not(bids_match):
        return None

    # extract the bid sequence
    bids = bids_match.group(1).split('|mb|')

    '''
    Check for 'an' flags:

    Apparently, occasionally in the bid string there will be
    a special 'an' flag which signals that the next '|'-delineated
    field contains a comment, i.e. not a proper bid.

    Check for these and delete them.
    '''
    bids = [re.sub(r'\|?an\|(.*)?$', '', x) for x in bids]
    

    # check for passout
    if (len(bids) == 4) and (bids[0] == 'p'):
        return bids, None, 'PO'
    
    # get the contract
    '''
    Do this by peeling backwards from the end of the bid
    sequence: if 'd', 'r', 'p', or 'p!' are encountered, then
    advance backwards by one index. When we stop encountering
    those flags, then we have arrived at the final contract bid.

    If in addition 'r' or 'd' are encountered, append to doubles
    (list) and count the number of doubles at the end of this
    function.
    '''

    doubles = []
    i = 1
    while (bids[-i] in 'drp') or (bids[-i] == 'p!'):
        if bids[-i] in 'dr':
            doubles.append(bids[-i])
        i += 1
    contract = bids[-i]

    # set the declarer: 0 = East (declarer)
    def get_snd(str):
        if len(str) == 1: return None
        else: return str[1]

    csuit = contract[1]
    bidsuits = list(map(get_snd, bids))

    # extract bids only from winning team and reverse
    bidsuits = bidsuits[bids.index(contract)::-2]

    # check that earliest suit match is even or odd
    #   even = declarer is player who set contract
    #   odd = declarer is opposite of player who set contract
    
    firstmatch = rindex(bidsuits, csuit)
    if firstmatch % 2 == 0:
        declarer = PLAYERS[(len(bids)-2)%4]
    else:
        declarer = PLAYERS[(len(bids))%4]

    return bids, declarer, (contract, len(doubles))

def process_play(lin, declarer, contract):
    ''' Parses .lin files for play information 

    depends:
        requires declarer and contract information output
        from process_bids()

    args:
        lin: a .lin-formatted string

    returns: 
        play: list of dicts (see definition of BridgeHand)
        made: int
    '''

    # process the play portion of the linfile 
    '''
    Explanation of this regex:

    The play sequence begins with the 'pc' flag and ends on either
        1) '|pg||' if all tricks are played
        2) '|mc|' if tricks were claimed
    '''
    
    play_match = re.search(r'pc\|(.+)(\|pg\|\|)|(\|mc\|)', lin)
    play_str = play_match.group(1).split('|pg|')
    
    # split into cards
    order = rotate_to(declarer, 1)
    dummy = order[1]
    
    play = []
    made = 0

    for trick in play_str:

        play.append(dict())
        
        # record who led this trick
        play[-1]['lead'] = order[0]
        
        # strip leading '|pc|' in 2nd-onwards elements of play_str
        trick = re.sub('^\|pc\|', '', trick)

        # split the trick string into individual cards played
        cards = trick.split('|pc|')

        '''
        if tricks were claimed, then the last trick in the string
        might have less than four cards played.

        then only convert the remaining cards and exit the loop.
        '''
        if len(cards)<4:
            for s in order[:len(cards)]:
                play[-1][s] = convert_card(cards.pop(0))
            break 
            
        for s in order:
            play[-1][s] = convert_card(cards.pop(0))

        # update order based on who won last trick
        winner, top = get_trick_winner(play[-1], order[0], contract[1])
        order = rotate_to(winner)

        # update running count of tricks won by declaring team
        if (winner==declarer) or (winner==dummy):
            made += 1

    return play, made

#####################################    
def parse_linfile(linfile):
#####################################    
    
    with open(linfile, 'r') as f:
        lin=f.read()
    
    players = get_players(lin)
    hands = get_initial_hands(lin)
    bids_triple = process_bids(lin)
    
    if not(players and hands and bids_triple):
        return None
    else:
        bids, declarer, (contract, doubled) = bids_triple

    # process play using declarer/contract from process_bids()
    play, made = process_play(lin, declarer, contract)
    
    # check if play ended on claimed tricks
    claim_str = re.search(r'\|mc\|([0-9]+)\|', lin)
    if claim_str:
        claimed = True
        made = claim_str.group(1) 
    else:
        claimed = False

    return BridgeHand(players, hands, bids, play, contract, declarer, doubled, None, made, claimed)





