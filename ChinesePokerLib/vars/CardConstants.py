import numpy as np
import pandas as pd

from ChinesePokerLib.classes.Utility import TwoWayDict


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
      'S','H','D','C',
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

card_group_labels_raw = {
  'CHINESE-POKER':[
    (1,'StraightFlush'),
    (2,'FourOfAKind'),
    (3,'FullHouse'),
    (4,'Flush'),
    (5,'Straight'),
    (6,'ThreeOfAKind'),
    (7,'TwoPairs'),
    (8,'OnePair'),
    (9,'AllSingles'),
  ]
}

card_group_labels_map = {}
for game_type in card_group_labels_raw:
  temp_dict = TwoWayDict()
  for item in card_group_labels_raw[game_type]:
    temp_dict[item[0]] = item[1]
  card_group_labels_map[game_type] = temp_dict


GEN_valid_card_groups_given_set_size = {
  3:(6,8,9),
  5:(1,2,3,4,5,6,7,8,9),
}

# Number of elements in CardGroupCode per set size and type
GEN_card_group_n_descriptors = {
  5:{
    'StraightFlush':1,
    'FourOfAKind':1,
    'FullHouse':1,
    'Flush':5,
    'Straight':1,
    'ThreeOfAKind':1,
    'TwoPairs':3,
    'OnePair':4,
    'AllSingles':5,
  },
  3:{
    'ThreeOfAKind':1,
    'OnePair':2,
    'AllSingles':3,
  }
}


GEN_card_group_display_str = {
  'StraightFlush':'Straight Flush',
  'FourOfAKind':'Four of a Kind',
  'FullHouse':'Full House',
  'Flush':'Flush',
  'Straight':'Straight',
  'ThreeOfAKind':'Three of a Kind',
  'TwoPairs':'Two Pairs',
  'OnePair':'One Pair',
  'AllSingles':'All Singles',
}


######################## END Card Group Constants ######################