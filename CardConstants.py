import numpy as np
import pandas as pd
from UtilityClasses import TwoWayDict


###################### START Standard constants #########################
STANDARD_suit_name_map_raw = [
  ('C','Clubs'),
  ('D','Diamonds'),
  ('H','Hearts'),
  ('S','Spades')
]
STANDARD_suit_name_map = TwoWayDict()
for suit in STANDARD_suit_name_map_raw:
  STANDARD_suit_name_map[suit[0]] = suit[1]

STANDARD_full_suit_name_map = {s[0]:s[1] for s in STANDARD_suit_name_map_raw}
STANDARD_short_suit_name_map = {s[1]:s[0] for s in STANDARD_suit_name_map_raw}

STANDARD_number_name_map_raw = [
  ('2','Two'),
  ('3','Three'),
  ('4','Four'),
  ('5','Five'),
  ('6','Six'),
  ('7','Seven'),
  ('8','Eight'),
  ('9','Nine'),
  ('10','Ten'),
  ('J','Jack'),
  ('Q','Queen'),
  ('K','King'),
  ('A','Ace')
]

STANDARD_number_name_map = TwoWayDict()
for number in STANDARD_number_name_map_raw:
  STANDARD_number_name_map[number[0]] = number[1]

STANDARD_full_number_name_map = {n[0]:n[1] for n in STANDARD_number_name_map_raw}
STANDARD_short_number_name_map = {n[1]:n[0] for n in STANDARD_number_name_map_raw}

######################### END Standard Constants #######################

######################## START Strength Constants ######################

suit_number_strength_orders = {
  'STANDARD':{
    'Suits':(
      'Spades','Hearts','Diamonds','Clubs',
    ),
    'Numbers':(
      'A',
      'K',
      'Q',
      'J',
      '10',
      '9',
      '8',
      '7',
      '6',
      '5',
      '4',
      '3',
      '2',
    )
  }
}

######################### END Strength Constants #######################

####################### START Card Group Constants #####################

card_group_labels = {
  'CHINESE-POKER':{
    1:'Straight Flush',
    2:'4 of a Kind',
    3:'Full House',
    4:'Flush',
    5:'Straight',
    6:'Three of a Kind',
    7:'Two Pairs',
    8:'Single Pair',
    9:'Nothing',
  }
}

GEN_card_group_n_descriptors = {
  'StraightFlush':1,
  '4 of a Kind':1,
  'Full House':1,
  'Flush':5,
  'Straight':1,
  'Three of a Kind':1,
  'Two Pairs':3,
  'Single Pair':4,
  'Nothing':5,
}


######################## END Card Group Constants ######################