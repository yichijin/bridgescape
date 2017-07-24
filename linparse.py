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
from functools import cmp_to_key

PLAYERS = {0:'E', 1:'S', 2:'W', 3:'N'}
SUITMAP = {'C':0, 'D':1, 'H':2, 'S':3}
CARDMAP = {'2':2, '3':3, '4':4, '5':5, '6':6, '7':7, '8':8, '9':9, 'T':10, 'J':11, 'Q':12, 'K':13, 'A':14}

# for readability...
def rindex(list, elt):
    '''Get the index of the last position matching elt in list

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
    rank_names = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

    def __init__(self, suit=0, rank=2):
        self.suit = suit
        self.rank = rank
        self.suitname = self.suit_names[suit]
        self.rankname = self.rank_names[rank-2]

    def __repr__(self):
        """Returns a human-readable string representation."""
        return '%s%s' % (Card.rank_names[self.rank-2], Card.suit_names[self.suit])

    '''
    NOTE:
    
    default comparison is deliberately not implemented so as
    not to confuse users who may implicitly assume a certain 
    suit rank (which is ambiguous outside of bridge).

    Comparison with flexible suit order is implemented below
    in the compare() method.
    '''
    
    def __eq__(self, other):
        return (self.suit == other.suit and self.rank == other.rank)

    def compare(self, other, sorder=(0,1,2,3)):
        '''
        Python 2-style cmp() operation on Card objects. Note:
        suit order defaults to standard bridge order: Clubs <
        Diamonds < Hearts < Spades.

        suitorder: tuple of suits (numerical) from low-to-high
        '''

        self_srank = sorder.index(self.suit)
        other_srank = sorder.index(other.suit)

        if self==other:
            return 0
        elif (self_srank < other_srank):
            return -1
        elif (self_srank == other_srank) and (self.rank < other.rank):
            return -1
        else:
            return 1

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

    def __len__(self):
        return len(self.cards)

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
    
    def sort(self, sorder=(0,1,2,3)):
        """Since comparison is not implemented for Card we
        have to implement card order here. Note that suitorder
        must be passed to the compare method of Card.

        suitorder: tuple of suits (numerical) from low-to-high
        """

        keyfunc = cmp_to_key(lambda x,y: x.compare(y, sorder))

        return Hand(initial=sorted(self, key=keyfunc))

class BridgeHand:
    '''
    players: dict (keys: positions)
    dealer: str (position)    
    hands: dict (keys: positions) of Hand objects 
    bids: list
    play: list of dicts (keys: 'E', 'S', 'W', 'N', 'lead') 
    contract: str
    declarer: str (postion)
    doubled: {0,1,2}
    vuln: str of 'NS','EW','none', or 'both'
    made: int
    claimed: bool
    '''

    def __init__(self, players, dealer, hands, bids, play, contract, declarer, doubled, vuln, made, claimed):
        self.players = players
        self.dealer = dealer
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

    # player order is always S,W,N,E
    players = {'S':p_str[0], 'W':p_str[1], 'N':p_str[2], 'E':p_str[3]}
    return(players)
    
def get_dealer(lin):
    '''
    Recover the position of the dealer: in the linfile, this is 
    the first integer after the 'md|' flag which comes 
    immediately after the list of players.

    Since the player order is always SWNE (see above)

    1 = first player in the list, i.e. 'S'
    2 = second player in the list, i.e. 'W'
    3 = third, i.e. 'N'
    4 = fourth, i.e. 'E'

    input:
        lin: a .lin-formatted string

    returns:
        str (position)
    '''

    match = re.search(r'md\|([1-4])', lin)
    dealer_no = int(match.group(1))

    # have to %4 since BBO indexes 1-4 while we use 0-3
    return PLAYERS[dealer_no%4]


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

        card_match = re.search('S([^HDC]*)?H([^DC]*)?D([^C]*)?C(.*)?', cstring)
        for s in range(4):
            for v in card_match.group(s+1):
                hand.add_card(Card(suit=(3-s), rank=CARDMAP[v]))

        return hand 


    # get the hands of S, W, N
    hands = {}

    h_match = re.search('\|md\|([^\|]+)', lin)
    if not(h_match):
        return None

    h_str = h_match.group(1).split(',')

    # strip the dealer flag from the first blob
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

def get_bids(lin, dealer):
    ''' Parses .lin files for bid information. Returns None
    if no bid information found.

    args:
        lin: a .lin-formatted string

    returns: triple (x,y,z) of:
        x (list): bid sequence
        y (str): declarer
        z (tuple): str (contract), {0,1} (doubled or not)
    '''
    
    '''
    First, set the dealer. When we calculate who the declarer is
    we will need the dealer to be in the first position of
    the direction list.
    '''
    BID_PLAYERS = rotate_to(dealer)

    # extract raw bid string 
    bids_match = re.search(r'mb\|(.+?)\|pg', lin)
    if not(bids_match):
        return None

    # extract the bid sequence
    bids = bids_match.group(1).split('|mb|')

    '''
    Check for annotations
    
    During bidding a user can annotate their bid. If they do, 
    the .lin appends a '!' onto the bid and follows it with
    an 'an' flag and an annotation cell.

    Check for these and delete them.
    '''
    bids = [re.sub(r'(\|?an\|(.*)?$)|\!', '', x) for x in bids]
    

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

    '''
    This next section extracts the declarer, which is the
    person on the winning team who first bid the suit of 
    the winning contract.
    
    get_snd() is a helper function to get only the SUIT
    of each bid.
    '''
    
    csuit = contract[1]
    cindex = bids.index(contract)
    
    def get_snd(str):
        if len(str) == 1: return None
        else: return str[1]
    bidsuits = list(map(get_snd, bids))

    '''
    We need to count the number of bids beween
        1) the contract-setting bid
        2) the first bid (on the winning team) of the contract suit
    
    And check if it's a multiple of 2 or 4.
    '''
    firstmatch = rindex(bidsuits[cindex::-2], csuit)
    
    if firstmatch % 2 == 0:
        declarer = BID_PLAYERS[cindex % 4]
    else:
        declarer = BID_PLAYERS[(cindex-2) % 4]

    return bids, declarer, (contract, len(doubles))

def get_vulnerability(lin):
    '''
    Parses .lin files for vulnerability.

    args:
        lin: a .lin-formatted string

    returns:
        str of 'NS','EW','none', or 'both'
    '''

    match = re.search(r'sv\|(.)\|', lin)
    vuln_str = match.group(1) 

    if vuln_str in 'NnSs':
        return 'NS'
    elif vuln_str in 'EeWw':
        return 'WE'
    elif vuln_str in 'oO0':
        return 'none'
    elif vuln_str in 'Bb':
        return 'both'

def get_play(lin, declarer, contract):
    ''' Parses .lin files for play information 

    depends:
        requires declarer and contract information output
        from get_bids()

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
    
    play_match = re.search(r'\|pc\|(.+)(\|pg\|\|)|(\|mc\|)', lin)
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
    dealer = get_dealer(lin)
    hands = get_initial_hands(lin)
    bids_triple = get_bids(lin, dealer)
    
    if not(players and hands and bids_triple):
        return None
    else:
        bids, declarer, (contract, doubled) = bids_triple

    vuln = get_vulnerability(lin)

    # process play using declarer/contract from get_bids()
    play, made = get_play(lin, declarer, contract)
    
    # check if play ended on claimed tricks
    claim_str = re.search(r'\|mc\|([0-9]+)\|', lin)
    if claim_str:
        claimed = True
        made = claim_str.group(1) 
    else:
        claimed = False

    return BridgeHand(players, dealer, hands, bids, play, contract, declarer, doubled, vuln, made, claimed)





