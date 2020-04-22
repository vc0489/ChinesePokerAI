from CardClass import CardClass
import CardConstants as CConst
from collections import Counter
import numpy as np

# Group classifications and Ranks
# [1] Royal Flush
# [2] 4 of a Kind
# [3] Full House
# [4] Flush
# [5] Straight
# [6] 3 of a Kind
# [7] 2 Pairs
# [8] 1 Pair
# [9] Nothing



# Identify group type


class CardGroupClassifier:

  def __init__(self):
    return
  

  def _check_all_equal(self, elements):
    return len(set(elements)) == 1
  
  def _check_all_different(self, elements):
    return len(set(elements)) == len(elements)

  def _get_number_indices(self, cards):
    
    return

  def _is_flush_given_5_cards(self, cards):
    suits = [card.suit for card in cards]
    return self._check_all_equal(suits)
  
  def _is_straight_given_5_cards_no_repeat(self, cards):
    # Assume 5 cards
    return cards[-1].number_strength_ind-cards[0].number_strength_ind == 4
    
  #def _has_4_of_a_kind(self, cards):
  #  return
  
  #def _has_3_of_a_kind(self, cards):
  #  return
  
  def _get_repeat_numbers(self, cards):
    numbers = [(card.number, card.number_strength_ind) for card in cards]
    
    counts = Counter(numbers).items()
    
    to_return = [(count[0][0], count[0][1], count[1]) for count in counts]
    to_return = sorted(to_return, key=lambda x: x[2], reverse=True)
    return to_return

  
  def _sort_cards_by_number_strength(self, cards):
    cards = sorted(cards, key=lambda x: x.number_strength_ind)
    return (cards)

  def _identify_groups(self, cards):
    # Arbitrary number of cards

    return

  def _identify_group_type_3_or_5_cards(self, cards):
    # Assume 5 cards 
    # VC: May be able to apply to 3 card set
    # Components:
    # [1] Straight-Flush (5 card only)
    # [2] Flush (5 card only)
    # [3] Straight (5 card only)
    # [4] Four of a kind (5 card only)
    # [5] Three of a kind
    # [6] Pair(s)
    # [7] Singles
    
    n_cards = len(cards)
    cards = self._sort_cards_by_number_strength(cards)

    numbers = [card.number for card in cards]
    no_repeat_num = self._check_all_different(numbers)
    
    is_straight_flush = False
    is_4_of_a_kind = False
    is_full_house = False
    is_flush = False
    is_straight = False
    is_two_pairs = False
    is_3_of_a_kind = False
    is_single_pair = False

    if no_repeat_num and n_cards==5:
      is_flush = self._is_flush_given_5_cards(cards)
      is_straight = self._is_straight_given_5_cards_no_repeat(cards)
      if is_flush and is_straight:
        is_straight_flush = True
        is_flush = False
        is_straight = False
        info = 'StraightFlush'
        group_code = [1, cards[0].number_strength_ind]
      elif is_flush:
        info = 'Flush'
        group_code = [4,] + [card.number_strength_ind for card in cards]
      elif is_straight:
        info = 'Straight'
        group_code = [5, cards[0].number_strength_ind]
      elif not is_flush and not is_straight:
        info = 'Nothing'
        group_code = [9,] + [card.number_strength_ind for card in cards]

    else:
      rep_info = self._get_repeat_numbers(cards)
      if rep_info[0][2] == 4:
        is_4_of_a_kind = True
        info = '4OfAKind'
        group_code = [2, rep_info[0][1]]
      elif rep_info[0][2] == 3:
        if rep_info[1][2] == 2:
          is_full_house = True
          info = 'FullHouse'
          group_code = [3, rep_info[0][1]]
        else:
          is_3_of_a_kind = True
          info = '3OfAKind'
          group_code = [6, rep_info[0][1]]
      elif rep_info[0][2] == 2:
        if rep_info[1][2] == 2:
          is_two_pairs = True
          info = 'TwoPairs'
          group_code = [7, rep_info[0][1], rep_info[1][1], rep_info[2][1]]
        else:
          is_single_pair = True
          info = 'Pair'
          group_code = [8, rep_info[0][1], rep_info[1][1], rep_info[2][1], rep_info[3][1]]
    

    #full_info = f'Straight Flush:{is_straight_flush}\n' + \
    #       f'4 of a Kind:{is_4_of_a_kind}\n' + \
    #       f'Full House:{is_full_house}\n' + \
    #       f'Flush:{is_flush}\n' + \
    #       f'Straight:{is_straight}\n' + \
    #       f'3 of a kind:{is_3_of_a_kind}\n' + \
    #       f'Two Pairs:{is_two_pairs}\n' + \
    #       f'Single Pair:{is_single_pair}'
    return info, CardGroupCode(group_code) #self._fill_group_code(group_code)

  def _fill_group_code(self, group_code, fill_length=6, fill_element=-1):
    full_group_code = group_code + [fill_element for i in range(fill_length-len(group_code))]
    return full_group_code

  def _encode_group_type(self, cards, info=None):
  # Hand Notation Examples: 
  # [A1] Royal Flush with Ace high
  #     -- (1,0,-1,-1,-1,-1)
  # [A2] Royal Flush with Ten high
  #     -- (1,4,-1,-1,-1,-1)
  # [B1] 4 Kings
  #     -- (2,1,-1,-1,-1,-1)
  # [B2] 4 Threes
  #     -- (2,11,-1,-1,-1,-1)
  # [C1] Full House with 3 Tens
  #     -- (3,4,-1,-1,-1,-1)
  # [C2] Full House with 3 Fives
  #     -- (3,9,-1,-1,-1,-1)
  # [D1] Flush with (Q,10,8,4,3)
  #     -- (4,1,3,5,10,11)
  # [D2] Flush with (K,7,6,5,2)
  #     -- (4,1,7,8,9,12)
  # [E1] Straight with Queen high
  #     -- (5,2,-1,-1,-1,-1)
  # [E2] Straight with Eight high
  #     -- (5,6,-1,-1,-1,-1)
  # [F1] 3 Nines
  #     -- (6,5,-1,-1,-1,-1)
  # [F2] 3 Twos
  #     -- (6,12,-1,-1,-1,-1)
  # [G1] 2 Aces, 2 Sevens and a King
  #     -- (7,0,7,1,-1,-1)
  # [G2] 2 Eights, 2 Fives and a Six
  #     -- (7,6,9,8,-1,-1)
  # [H1] 2 Jacks and single Ace, Ten, Six
  #     -- (8,3,0,4,8,-1)
  # [H2] 2 Nines and single Queen, Eight, Three
  #     -- (8,5,2,6,11,-1)
  # [H3] 2 Queens and a single King (3 card example)
  #     -- (8,2,1,-1,-1,-1)
  # [I1] Queen, Ten, Seven, Four, Two
  #     -- (9,2,4,7,10,12)
  # [I2] Jack, Nine, Eight, Five, Three
  #     -- (9,3,5,6,9,11)
  # [I3] Ace, Six, Three (3 card example)
  #     -- (9,0,8,11,-1,-1)
    return
  def classify_card_group(self, cards):
    #card_number_indices = self._get_number_indices(cards)
    # card.number_strength_ind
    
    return

class CardGroupCode:
  def __init__(self, code, card_strength_type='STANDARD', game_type='CHINESE-POKER'):
    self.code = tuple(code)
    self.ind_map_to_number = CConst.suit_number_strength_orders[card_strength_type]
    self.card_strength_type = card_strength_type
    self.game_type = game_type
    return
  
  def __repr__(self):
    repr_str = f'CardGroupCode{str(self.code)}'
    return repr_str

  def __hash__(self):
    return hash(self.code)

  def __format__(self, spec):
    if spec == 'S':
      out_str = CConst.card_group_labels[self.game_type][self.code[0]]
    elif spec == 'F':
      number_str = [CConst.suit_number_strength_orders[self.card_strength_type]['Numbers'][i] for i in self.code[1:]]
      number_str = '[' + ''.join(number_str) + ']'
      out_str = CConst.card_group_labels[self.game_type][self.code[0]] + ' ' + number_str
      
    return out_str


  def __eq__(self, other):
    return self.code == other.code
  
  def __gt__(self, other):
    for i, item in enumerate(self.code):
      if i == len(other.code):
        return True
      elif item < other.code[i]:
        return True
      elif item > other.code[i]:
        return False
    return False



def _describe_chinese_poker_card_group(self):
  return
