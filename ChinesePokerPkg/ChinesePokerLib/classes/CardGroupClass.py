"""
"""
from collections import Counter
from itertools import combinations, product, permutations
from operator import attrgetter
import numpy as np
import pandas as pd
from deprecated import deprecated

from ChinesePokerLib.classes.CardClass import CardClass
import ChinesePokerLib.vars.CardConstants as CConst
import ChinesePokerLib.vars.GameConstants as GConst
from ChinesePokerLib.classes.UtilityClasses import VarChecker

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


class BaseCardGroupClass:
  def __init__(self, game_type, card_type):
    self.game_type = game_type
    self.card_type = card_type
    return

  @classmethod
  def fill_code(cls, code, fill_length=6, fill_element=999, trim_if_needed=False):

    if isinstance(code, tuple):
      code = list(code)
      is_tuple = True
    else:
      is_tuple = False
    filled_code = code + [fill_element for i in range(fill_length-len(code))]
    
    if trim_if_needed and len(code) > fill_length:
      filled_code = filled_code[:fill_length]
    if is_tuple:
      filled_code = tuple(filled_code)

    return filled_code
    
  

# Identify group type
class CardGroupClassifier(BaseCardGroupClass):
  """[summary]
  """
  def __init__(self, game_type='CHINESE-POKER', card_type='STANDARD'):
    self.game_type = game_type
    self.card_type = card_type
    return
  

  def _check_all_equal(self, elements):
    return len(set(elements)) == 1
  
  def _check_all_different(self, elements):
    return len(set(elements)) == len(elements)

  def _get_repeat_suits(self, cards):
    suits = [card.suit for card in cards]
    counts = list(Counter(suits).items())

    counts = sorted(counts, key=lambda x: x[1], reverse=True)

    return counts


  def _get_repeat_numbers(self, cards, return_indices=False):
    numbers = [(card.number, card.number_strength_ind) for card in cards]
    
    counts = Counter(numbers).items()
    
    to_return = [(count[0][0], count[0][1], count[1]) for count in counts]
    to_return = sorted(to_return, key=lambda x: (x[2], -x[1]), reverse=True)

    if not return_indices:
      return to_return
    else:
      to_return_indices = [[] for i in range(len(to_return))]
      for i,(num,_,_) in enumerate(to_return):
        num_inds = [i for i,card in enumerate(cards) if card.number == num]
        to_return_indices[i] = num_inds
      return to_return, to_return_indices

  
  def _sort_cards_by_suit_strength(self, cards, sort_by_number=True):
    if sort_by_number:
      sort_res = sorted([(i,card) for i,card in enumerate(cards)], key=lambda x: (x[1].suit_strength_ind, x[1].number_strength_ind))
    else:
      sort_res = sorted([(i,card) for i,card in enumerate(cards)], key=lambda x: x[1].suit_strength_ind)

    sorted_inds, sorted_cards = zip(*sort_res)
    
    return sorted_cards, sorted_inds

  def _sort_cards_by_number_strength(self, cards, sort_by_suit=True):
    if sort_by_suit:
      sort_res = sorted([(i,card) for i,card in enumerate(cards)], key=lambda x: (x[1].number_strength_ind, x[1].suit_strength_ind))
    else:
      sort_res = sorted([(i,card) for i,card in enumerate(cards)], key=lambda x: x[1].number_strength_ind)
    
    sorted_inds, sorted_cards = zip(*sort_res)

    return sorted_cards, sorted_inds

  def _sort_cards_by_attr_list(self, cards, attr_list=('number_strength_ind', 'suit_strength_ind')):
    cards = sorted(cards, key=attrgetter(*attr_list))
    return cards

  #def _has_straight_flush(self, cards):
  #  return

  def _find_straights(self, cards, n_cards_for_straight=5, sep_straight_flushes=False):
    # Returns
    # [0]: Whether there are straights within card set
    # [1]: If there are straights: 
    # [1][0]: Indices of cards that give straights (and not straight flushes)
    # [1][1]: Indices of cards that give straight flushes
    all_straights = {}
    all_straight_flushes = {}

    num_strength_inds = [card.number_strength_ind for card in cards]
    suit_strength_inds = [card.suit_strength_ind for card in cards]

    min_str_ind = min(num_strength_inds)
    max_str_ind = max(num_strength_inds)
    
    card_inds_per_strength_ind = [[] for i in range(max_str_ind+1)]
    for str_ind in range(min_str_ind, max_str_ind+1):
      card_inds_per_strength_ind[str_ind] = [c_ind for c_ind, s_ind in enumerate(num_strength_inds) if s_ind == str_ind]

    for s_ind in range(min_str_ind, max_str_ind-n_cards_for_straight+2):
      ind_set = card_inds_per_strength_ind[s_ind:s_ind+n_cards_for_straight]
      straight_combs = list(product(*ind_set))

      if len(straight_combs) == 0:
        continue
      
      all_straights[s_ind] = straight_combs

      if sep_straight_flushes:
        for comb in straight_combs:
          temp_suit_inds = [suit_strength_inds[i] for i in comb]
          if self._check_all_equal(temp_suit_inds):
            if s_ind in all_straight_flushes:
              all_straight_flushes[s_ind].append(comb)
            else:
              all_straight_flushes[s_ind] = [comb,]
            
    #has_straight = len(all_straights) + len(all_straight_flushes) > 0 
    return all_straights, all_straight_flushes

  def _find_flushes(self, cards, n_cards_for_flush=5, filter_straight_flushes=True):
    # Returns
    # [0]: Whether there are flushes within card set
    # [1]: If there are flushes:
    # [1][0]: Indices of cards that give flushes (and not straight flushes) 
    # [1][1]: Indices of cards that give straight flushes
    all_flushes = {}
    all_straight_flushes = {}

    if len(cards) < n_cards_for_flush:
      return (all_flushes, all_straight_flushes)
    elif len(cards) >= n_cards_for_flush:
      suit_counts = self._get_repeat_suits(cards)
      if suit_counts[0][1] < n_cards_for_flush:
        return all_flushes, all_straight_flushes

      for suit, suit_count in suit_counts:
        if suit_count < n_cards_for_flush:
          break

        # Identify indices in cards of given suit
        suit_cards = [card for card in cards if card.suit == suit]
        suit_cards_inds = [cards.index(card) for card in suit_cards]
        suit_cards_str_inds = [card.number_strength_ind for card in suit_cards]
        

        suit_cards_both_inds = list(zip(suit_cards_inds, suit_cards_str_inds))
        suit_cards_both_inds = sorted(suit_cards_both_inds, key=lambda x: x[1])
        #print(suit, suit_count, suit_cards_inds)

        # Generate all possible cards indices that give flushes
        flush_comb_inds = list(combinations(suit_cards_both_inds, n_cards_for_flush))
        
        for flush_ind_set in flush_comb_inds:
          flush_card_ind = tuple([c[0] for c in flush_ind_set])
          flush_card_str_ind = tuple([c[1] for c in flush_ind_set])
          #print('-'*20)
          #print(flush_card_ind, flush_card_str_ind)
          if filter_straight_flushes and flush_card_str_ind[-1]-flush_card_str_ind[0]==n_cards_for_flush-1:
            if flush_card_str_ind[0] in all_straight_flushes:
              all_straight_flushes[flush_card_str_ind[0]].append(flush_card_ind)
            else:
              all_straight_flushes[flush_card_str_ind[0]] = [flush_card_ind,]
          else:
            if flush_card_str_ind in all_flushes:
              all_flushes[flush_card_str_ind].append(flush_card_ind)
            else:
              all_flushes[flush_card_str_ind] = [flush_card_ind,]
          
      return (all_flushes, all_straight_flushes)
    
  def _find_num_repeat_groups(self, cards, min_group_size=1, max_group_size=4, find_full_houses=True):
    # Full House, 4,3,2 of a kind etc.
    num_counts, num_indices = self._get_repeat_numbers(cards, return_indices=True)
    all_full_houses = {}
    all_repeat_groups = {}

    for group_size in range(min_group_size, max_group_size+1):
      all_repeat_groups[group_size] = {}
    
    count_inds_min_2_rep = [i for (i, count_info) in enumerate(num_counts) if count_info[2] >= 2]

    for count_ind, (_,str_ind,num_count) in enumerate(num_counts):
            
      card_inds = num_indices[count_ind]
        
      #if num_count >= min_group_size and num_count <= max_group_size:
      if num_count >= min_group_size:
        for count in range(min_group_size, min(num_count, max_group_size)+1):
          group_combs = list(combinations(card_inds, count))
          all_repeat_groups[count][str_ind] = group_combs
      
      if find_full_houses==True and num_count >= 3 and len(count_inds_min_2_rep)>2:
        triple_inds = list(combinations(card_inds, 3))
        for count_ind_for_pair in count_inds_min_2_rep:
          if count_ind_for_pair == count_ind:
            continue

          _,str_ind_pair,_ = num_counts[count_ind_for_pair]
          pair_inds = list(combinations(num_indices[count_ind_for_pair],2))
        
          full_house_comb_inds = product(triple_inds, pair_inds)
          full_house_comb_inds = [t_inds + p_inds for t_inds, p_inds in full_house_comb_inds]
          all_full_houses[(str_ind,str_ind_pair)] = full_house_comb_inds
    
    return all_repeat_groups, all_full_houses

  def _identify_set_components(self, cards, max_component_size=5):
    """
    
    Returns:
      Dict of (set_label, Dict of (component code, List of (card indices tuples)))

      e.g.
      {'StraightFlush': {},
       'Quadruple': {},
       'Flush': {},
       'Straight': {},
       'Triple': {},
       'Pair': {0: [(0, 1)], 3: [(2, 3)]},
      'Single': {0: [(0,), (1,)], 3: [(2,), (3,)], 7: [(4,)]}}

    """
    # Arbitrary number of cards
    #sorted_cards, sort_inds = self._sort_cards_by_number_strength(cards)

    # Straight Flushes, Flushes and Straights
    if max_component_size >= 5:
      flush_groups, straight_flush_groups = self._find_flushes(cards)
      straight_groups, _ = self._find_straights(cards)
      for str_key in straight_flush_groups:
        for group in straight_flush_groups[str_key]:
          straight_groups[str_key].remove(group)
    else:
      straight_flush_groups = {}
      flush_groups = {}
      straight_groups = {}

    # Full houses, groups of 2,3,4
    rep_groups, _ = self._find_num_repeat_groups(
      cards, max_group_size=min(4, max_component_size), find_full_houses=False
    )
    
    for grp_size in range(1,5):
      if grp_size not in rep_groups:
        rep_groups[grp_size] = {}

    all_groups = {
      'StraightFlush': straight_flush_groups,
      'Quadruple': rep_groups[4],
      'Flush': flush_groups,
      'Straight': straight_groups,
      'Triple': rep_groups[3],
      'Pair': rep_groups[2],
      'Single': rep_groups[1],
    }
    return all_groups
  
  def _construct_5_card_2_rep_sets(self, rep1_groups, rep2_groups):
    sets = {}
    for str_ind_1 in rep1_groups:
      for str_ind_2 in rep2_groups:
        if str_ind_1 == str_ind_2:
          continue
        else:
          all_combs = product(rep1_groups[str_ind_1], rep2_groups[str_ind_2])
          all_card_inds = [card_ind_1 + card_ind_2 for card_ind_1, card_ind_2 in all_combs]
          sets[(str_ind_1, str_ind_2)] = all_card_inds
    return sets


  def _construct_two_type_comb_3_sets(self, type1_groups, type2_groups, repeated_types):
    sets = {}
    #rep1_groups = type1_groups
    
    #rep3_groups = type2_groups
    if repeated_types == (1,2):
      sets_1 = self._construct_one_type_n_rep_sets(type1_groups, 2)
      sets_2 = type2_groups
    elif repeated_types == (2,3):
      sets_1 = type1_groups
      sets_2 = self._construct_one_type_n_rep_sets(type2_groups, 2)

    sets = self._construct_two_type_comb_sets(sets_1, sets_2)  

    return sets

  def _intersect_generic(self, elements1, elements2):
    if isinstance(elements1, (int, float)):
      elements1 = (elements1,)
    if isinstance(elements2, (int, float)):
      elements2 = (elements2,)
    
    return set(elements1) & set(elements2)

  def _combined_tuple_generic(self, elements1, elements2):
    if isinstance(elements1, (int, float)):
      elements1 = (elements1,)
    if isinstance(elements2, (int, float)):
      elements2 = (elements2,)
    
    return elements1 + elements2

  def _construct_two_type_comb_sets(self, type1_groups, type2_groups):
    # Unlike in _construct_one_type_n_rep_sets
    # str_i will not be forced to be monotically increasing 
    # as groups are supposed to be of different types
    sets = {}
    for str_ind_1 in type1_groups.keys():
      for str_ind_2 in type2_groups.keys():
        #if len(set(str_ind_1) & set(str_ind_2)) > 0:
        
        if len(self._intersect_generic(str_ind_1, str_ind_2)) > 0:
          continue

        str_ind_comb = self._combined_tuple_generic(str_ind_1, str_ind_2)
        card_inds_to_combine = product(type1_groups[str_ind_1], type2_groups[str_ind_2])
        combined_inds = [card_inds1+card_inds2 for card_inds1,card_inds2 in card_inds_to_combine]
        sets[str_ind_comb] = combined_inds
    return sets


 
  def _construct_one_type_n_rep_sets(self, groups, n_set_reps=2, condition=None):
    """[summary]

    Args:
        groups (dict): Keys=strength_ind, Values=card indices
        n_set_reps (int, optional): [description]. Defaults to 2.
        condition ([type], optional): [description]. Defaults to None.

    Returns:
        [type]: [description]
    """
    # For all singles and flush need non-consecutive
    
    # str_i will be monotically increasing
    sets = {}
    
    all_str_inds = sorted(groups.keys()) # List of all strength inds
    n_inds = len(all_str_inds)
    if n_inds < n_set_reps:
      return sets
    
    def _is_sorted(x):
      return VarChecker.check_is_sorted(x, ascending=True, allow_equal=False)
    # Re-write
    # Find all combinations of n_set_reps items in all_str_inds that satisfy condition.
    # This will form the keys of sets
    if condition is not None:
      full_condition = lambda x: _is_sorted(x) and condition(x)
    else:
      full_condition = lambda x: _is_sorted(x)
    
    str_ind_combs = self._gen_conditional_combs(all_str_inds, n_set_reps, full_condition)
    
    # Then get cartesian product of each combination
    # This will form the value of the corresponding key
    for comb in str_ind_combs:
      temp_card_inds_lists = [groups[str_ind] for str_ind in comb]
      card_inds_comb = list(product(*temp_card_inds_lists))
      
      concat_combs = [tuple([i for sub in comb for i in sub]) for comb in card_inds_comb]
      sets[comb] = concat_combs
    
    """
    # VC: Old code to be deleted
    sets_old = {}
    #temp_sets = {}
    # Construct first set
    for i1 in range(n_inds-n_set_reps+1):
      str_ind_1 = all_str_inds[i1]
      sets_old[(str_ind_1,)] = groups[str_ind_1]

    for rep_no in range(2,n_set_reps+1):
      temp_sets = sets_old
      sets_old = {}
      for set_str_i in temp_sets.keys():
        for i in range(all_str_inds.index(set_str_i[-1])+1, n_inds-n_set_reps+rep_no):
          new_set_str_i = set_str_i + (all_str_inds[i],)
          card_inds_to_combine = product(temp_sets[set_str_i],groups[all_str_inds[i]])
          new_card_inds = [inds_old+inds_new for inds_old,inds_new in card_inds_to_combine]
          sets_old[new_set_str_i] = new_card_inds
    """
   
      
    return sets

  def _identify_n_card_sets(self, cards, set_size=5):
    """[summary]

    Args:
        cards ([type]): [description]
        set_size (int, optional): [description]. Defaults to 5.

    Returns:
        [type]: [description]
    """

    if set_size == 3:
      all_n_card_sets, components = self._identify_3_card_sets(cards)
    elif set_size == 5:
      all_n_card_sets, components = self._identify_5_card_sets(cards)
    return all_n_card_sets, components

  def _identify_3_card_sets(self, cards):
    components = self._identify_set_components(cards, 3)


    # Construct 3 of a kind hand if possible
    sets_3_of_a_kind = self._construct_one_type_n_rep_sets(components['Triple'], 1)
    
    # Construct single pair sets
    sets_1_pair = self._construct_two_type_comb_sets(components['Pair'], components['Single'])

    # Construct all singles sets
    sets_3_singles = self._construct_one_type_n_rep_sets(components['Single'], 3)
    
    all_3_card_sets = {}
    all_3_card_sets['ThreeOfAKind'] = sets_3_of_a_kind
    all_3_card_sets['OnePair'] = sets_1_pair
    all_3_card_sets['AllSingles'] = sets_3_singles
    return all_3_card_sets, components

  def _identify_5_card_sets(self, cards):
    """[summary]

    Args:
        cards ([type]): [description]

    Returns:
        [type]: [description]
    """

    components = self._identify_set_components(cards, 5)
    
    # Construct 4 of a kind hands
    sets_4_of_a_kind = self._construct_two_type_comb_sets(components['Quadruple'], components['Single'])

    # Construct full house hands
    sets_full_houses = self._construct_two_type_comb_sets(components['Triple'], components['Pair'])
    # Construct 3 of a kind hands
    sets_3_of_a_kind = self._construct_two_type_comb_3_sets(components['Triple'], components['Single'], (2,3))
    
    # Construct 2 pair sets
    sets_2_pairs = self._construct_two_type_comb_3_sets(components['Pair'], components['Single'], (1,2))
    
    # Construct single pair sets
    _sets_3_singles = self._construct_one_type_n_rep_sets(components['Single'], 3)
    sets_1_pair = self._construct_two_type_comb_sets(components['Pair'], _sets_3_singles)

    # Construct all singles sets
    sets_5_singles = self._construct_one_type_n_rep_sets(components['Single'], 5, lambda x: VarChecker.check_not_consecutive(x, ascending=True))

    all_5_card_sets = {}
    all_5_card_sets['StraightFlush'] = components['StraightFlush']
    all_5_card_sets['FourOfAKind'] = sets_4_of_a_kind
    all_5_card_sets['FullHouse'] = sets_full_houses
    all_5_card_sets['Flush'] = components['Flush']
    all_5_card_sets['Straight'] = components['Straight']
    all_5_card_sets['ThreeOfAKind'] = sets_3_of_a_kind
    all_5_card_sets['TwoPairs'] = sets_2_pairs
    all_5_card_sets['OnePair'] = sets_1_pair
    all_5_card_sets['AllSingles'] = sets_5_singles
    return all_5_card_sets, components
  
  def find_n_card_set_codes(
    self, 
    cards, 
    sort_by_code=True, 
    max_codes=None, 
    max_unique_codes=None,
    max_unique_top_level_codes=None,
    set_size=5,
    min_code=None,
    max_code=None,
  ):
    """Find all possible sets of n out of pool of cards. 
    This is the KEY method exposed by this class. 

    Arguments:
        cards {[type]} -- [description]

    Keyword Arguments:
        sort_by_code {bool} -- [description] (default: {True})
        max_codes {[type]} -- [description] (default: {None})
        max_unique_codes {[type]} -- [description] (default: {None})
        max_unique_top_level_codes {[type]} -- [description] (default: {None})
        set_size {int} -- [description] (default: {5})
        min_code {[type]} -- [description] (default: {None})
        max_code {[type]} -- [description] (default: {None})

    Returns:
        [list] -- List of all possible sets of n cards. Each item of the list represents a 
                  possibile set. Each item is a tuple of length 3. First tuple element is the
                  CardGroupCode, the second is the set of strength inds (basically the CardGroupCode
                  ignoring the top level code) and the third is the indices of the cards that
                  form the set.
    """

    # Generate possible sets
    all_n_card_sets, _ = self._identify_n_card_sets(cards, set_size)
    all_n_card_set_codes = []

    #print(list(all_5_card_sets.items()))
    #for set_label, set_label_det in all_5_card_sets.items():
    
    possible_set_types = CConst.GEN_valid_card_groups_given_set_size[set_size]  
    #n_set_types = int(len(CConst.card_group_labels_map[self.game_type].keys())/2)

    cum_n_codes = 0
    cum_n_unique_codes = 0
    cum_n_unique_top_level_codes = 0
    end_flag = False
    if max_unique_codes:
      unique_codes_so_far = []

    # Loop over possible set types given set size and check if any card combinations are of the set type 
    for set_i in possible_set_types:
      if (min_code is not None) and (set_i > min_code.code[0]):
        continue
      if (max_code is not None) and (set_i < max_code.code[0]):
        continue

      if end_flag == True:
        break
      set_label = CConst.card_group_labels_map[self.game_type][set_i]
      if set_label not in all_n_card_sets or len(all_n_card_sets[set_label]) == 0:
        continue
      else:
        cum_n_unique_top_level_codes += 1
        set_label_det = all_n_card_sets[set_label]
      #this_label_set_codes = self._gen_5_card_set_codes(set_label, list(all_5_card_sets[set_label].keys()))
      #print(set_label_det)
      for str_ind_set, card_ind_sets in set_label_det.items():
        
        temp_set_code = self._gen_n_card_set_codes(set_label, str_ind_set, set_size)
        if (min_code is not None) and (temp_set_code < min_code):
          continue
        if (max_code is not None) and (temp_set_code > max_code):
          continue

        cum_n_codes += len(card_ind_sets)
        if max_unique_codes and temp_set_code not in unique_codes_so_far:
          unique_codes_so_far.append(temp_set_code)
          cum_n_unique_codes += 1
        
        if max_unique_codes and cum_n_unique_codes > max_unique_codes:
          end_flag = True
          break

        for card_ind_set in card_ind_sets:
          all_n_card_set_codes.append((temp_set_code, str_ind_set, card_ind_set))
        
        if max_codes and cum_n_codes >= max_codes:
          end_flag = True
          break

      if max_unique_top_level_codes and cum_n_unique_top_level_codes == max_unique_top_level_codes:
        break

    if sort_by_code:
      all_n_card_set_codes = sorted(
        all_n_card_set_codes, 
        key=lambda x: (x[0], x[2]), 
        reverse=True
      )
    return all_n_card_set_codes

  def _is_flush_given_5_cards(self, cards):
    suits = [card.suit for card in cards]
    return self._check_all_equal(suits)
  
  def _is_straight_given_5_cards_no_repeat(self, cards):
    # Assume 5 cards
    return cards[-1].number_strength_ind-cards[0].number_strength_ind == 4

  @deprecated
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
    cards = self._sort_cards_by_attr_list(cards)

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
        #sup_info = cards[0].suit_strength_ind
      elif is_flush:
        info = 'Flush'
        group_code = [4,] + [card.number_strength_ind for card in cards]
        #sup_info = cards[0].suit_strength_ind
      elif is_straight:
        info = 'Straight'
        group_code = [5, cards[0].number_strength_ind]
        #sup_info = [card.suit_strength_ind for card in cards]
      elif not is_flush and not is_straight:
        info = 'AllSingles'
        group_code = [9,] + [card.number_strength_ind for card in cards]
        #sup_info = [card.suit_strength_ind for card in cards]
    else:
      rep_info = self._get_repeat_numbers(cards)
      if rep_info[0][2] == 4:
        is_4_of_a_kind = True
        info = 'FourOfAKind'
        group_code = [2, rep_info[0][1]]
        #sup_info = (card.number_srength_ind)
      elif rep_info[0][2] == 3:
        if rep_info[1][2] == 2:
          is_full_house = True
          info = 'FullHouse'
          group_code = [3, rep_info[0][1]]
        else:
          is_3_of_a_kind = True
          info = 'ThreeOfAKind'
          group_code = [6, rep_info[0][1]]
      elif rep_info[0][2] == 2:
        if rep_info[1][2] == 2:
          is_two_pairs = True
          info = 'TwoPairs'
          group_code = [7, rep_info[0][1], rep_info[1][1], rep_info[2][1]]
        else:
          is_single_pair = True
          info = 'OnePair'
          group_code = [8, rep_info[0][1], rep_info[1][1], rep_info[2][1], rep_info[3][1]]
    
    return info, CardGroupCode(group_code) 

  def top_level_code_from_label(self, set_label):
    """Get top level code from set label

    Args:
        set_label (str): Set label string. E.g. OnePair, TwoPairs, etc.

    Returns:
        [int]: Top level code
    """

    top_level_code = CConst.card_group_labels_map[self.game_type][set_label]
    return top_level_code
  


  def _gen_n_card_set_codes(self, set_label, set_str_inds, set_size=5):
    '''Generate set CardGroupCode object(s) of a single set type.
    The code consists of top level code + set of strength inds, 
    the length of which is found in CardConstants.GEN_card_group_n_descriptors.
    Assumes only one set_label, but set_str_inds can be list of multiple sets.

    Args:
        set_label (str): Set label string. E.g. OnePair, TwoPairs, etc.
        set_str_inds (int, tuple or list): Strength inds. 
        set_size (int): Number of cards in set

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
    '''
    
    # Single set
    if isinstance(set_str_inds, tuple):
      set_str_inds = [set_str_inds, ]
      single_set = True
    # Single set where the set strength is represented by only a single integer
    elif isinstance(set_str_inds, int):
      set_str_inds = [(set_str_inds, ), ]
      single_set = True
    # Multiple sets
    elif isinstance(set_str_inds, list):
      single_set = False
      out_group_codes = []

    # Get top level code for this set type
    set_top_code = CConst.card_group_labels_map[self.game_type][set_label]

    # Get number of desciptor codes for this set type
    n_desc_codes = CConst.GEN_card_group_n_descriptors[set_size][set_label]

    # Loop over sets and generate CardGroupCode objects
    for single_set_str_ind in set_str_inds:
      single_set_str_ind_ = single_set_str_ind
      if isinstance(single_set_str_ind_, int):
        single_set_str_ind_ = [single_set_str_ind_ ,]

      # code is formed of top level code + strength indicator code
      set_code = [set_top_code,] + list(single_set_str_ind_[:n_desc_codes])

      if single_set == False:
        out_group_codes.append(CardGroupCode(set_code))
      else: 
        out_group_codes = CardGroupCode(set_code)

    return out_group_codes



  def _encode_group_type(self, cards, info=None):
  # Hand Notation Examples: 
  # VC: -1 are now replaced by 999
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

  def all_possible_set_codes(self, set_size=5, code_length=3, code_fill_val=-1, ret_tuples=False):
    """
    1 StraightFlush 1 Maximum value is n_numbers-4
    2 FourOfAKind   1 N/A
    3 FullHouse     1 N/A
    4 Flush         5 All different, monotonically increasing but not consecutive
    5 Straight      1 Maximum value is n_numbers-4
    6 ThreeOfAKind  1 N/A 
    7 TwoPairs      3 All different and n1 < n2
    8 OnePair       4 All different, monotonically increasing from 2nd element onwards
    9 AllSingles    5 All different, monotonically increasing but not consecutive
    """
    var_check_obj=VarChecker()
    n_numbers = len(CConst.suit_number_strength_orders[self.card_type]['Numbers'])
    #min_card_str_ind = 0
    max_card_str_ind = n_numbers-1

    straight_type_cond = lambda x: x[0] <= max_card_str_ind-4 # Minimum strength ind
    
    
    ascending_cond = lambda x: var_check_obj.check_is_sorted(x, ascending=True, allow_equal=False) # Includes all different
    ascending_after_first_cond = lambda x: var_check_obj.check_is_sorted(x[1:], ascending=True, allow_equal=False) # Includes all different
    not_consec_cond = lambda x: var_check_obj.check_not_consecutive(x, ascending=True)
    
    singles_type_cond = lambda x: ascending_cond(x) and not_consec_cond(x)

    all_diff_cond = lambda x: var_check_obj.check_all_different(x)
    two_pairs_cond = lambda x: all_diff_cond(x) and x[0] < x[1]
    one_pair_cond = lambda x: all_diff_cond(x) and ascending_after_first_cond(x)
    
    if set_size == 5 and code_length >= 6:
      cond_map = {
        'StraightFlush': straight_type_cond,
        'FourOfAKind': None,
        'FullHouse': None,
        'Flush': singles_type_cond,
        'Straight': straight_type_cond,
        'ThreeOfAKind': None,
        'TwoPairs': two_pairs_cond,
        'OnePair': one_pair_cond,
        'AllSingles': singles_type_cond,
      }
    elif set_size == 5 and code_length < 6 and code_length >= 3:
      # Drop consecutive conditions

      # Need min and max index condition for flush and singles
      ind_cond = lambda x: (x[-1] <= max_card_str_ind - (set_size-code_length) - 1) and (x[0] < max_card_str_ind-4)
      singles_type_cond = lambda x: ascending_cond(x) and ind_cond(x)

      cond_map = {
        'StraightFlush': straight_type_cond,
        'FourOfAKind': None,
        'FullHouse': None,
        'Flush': singles_type_cond,
        'Straight': straight_type_cond,
        'ThreeOfAKind': None,
        'TwoPairs': two_pairs_cond,
        'OnePair': one_pair_cond,
        'AllSingles': singles_type_cond,
      }
      
    
    elif set_size == 3 and code_length >= 2:
      cond_map = {
        'ThreeOfAKind': None,
        'OnePair': all_diff_cond,
        'AllSingles': ascending_cond,
      }
    
    possible_set_types = CConst.GEN_valid_card_groups_given_set_size[set_size]  
    
    
    # Loop over possible set types given set size and check if any card combinations are of the set type 
    # Generate possible codes
    all_possible_codes = []
    inds = list(range(n_numbers))
    for set_i in possible_set_types:
      set_label = CConst.card_group_labels_map[self.game_type][set_i]
      
      n_descriptors = CConst.GEN_card_group_n_descriptors[set_size][set_label]

      # Top level code + descriptors
      set_codes = self._gen_conditional_combs(inds, min(code_length-1,n_descriptors), cond_map[set_label])
      set_codes = [self.fill_code([set_i,] + list(code), code_length, code_fill_val) for code in set_codes]
      if ret_tuples:
        set_codes = [tuple(code) for code in set_codes]
      else:
        set_codes = [CardGroupCode(code) for code in set_codes]
      all_possible_codes += set_codes

    return all_possible_codes
  
  def gen_code_map_diff_set_size(self, from_set_size, to_set_size, from_code_length, to_code_length, code_fill_val=-1):
    from_all_possible_codes = self.all_possible_set_codes(from_set_size, from_code_length, code_fill_val, ret_tuples=True)
    to_all_possible_codes = self.all_possible_set_codes(to_set_size, to_code_length, code_fill_val, ret_tuples=True)

    
    code_map = {}
    cur_ind_in_target = 0

    for cI, code in enumerate(from_all_possible_codes):
      if (from_code_length >= to_code_length) and code[:to_code_length] in to_all_possible_codes:
        code_map[code] = code[:to_code_length]
      elif (from_code_length < to_code_length) and CardGroupCode.fill_code(code, to_code_length, code_fill_val) in to_all_possible_codes:
        code_map[code] = CardGroupCode.fill_code(code, to_code_length, code_fill_val)
      else:
        # Check if simplified version exists
        if from_set_size > to_set_size and from_code_length >= to_code_length:
          temp_code = list(code[:to_code_length])
          found_simplified = False
          for i in range(to_code_length-1, 0, -1):
            temp_code[i] = code_fill_val
            if tuple(temp_code) in to_all_possible_codes:
              code_map[code] = temp_code
              found_simplified = True
              break
          
          if found_simplified:
            continue
        
        # Find first code in target list that is smaller
        while cur_ind_in_target < (len(to_all_possible_codes)-1):
          temp_code = [c for c in code if c != code_fill_val]
          if CardGroupCode(to_all_possible_codes[cur_ind_in_target]) < CardGroupCode(temp_code):
            if cur_ind_in_target > 0 and temp_code[0] == to_all_possible_codes[cur_ind_in_target][0]:
              cur_ind_in_target -= 1
            break
          cur_ind_in_target += 1
        code_map[code] = to_all_possible_codes[cur_ind_in_target]
    
    return code_map
  def _gen_conditional_combs(self, inds, comb_size, condition=None):
    combs = list(permutations(inds, comb_size))

    if condition is not None:
      combs = list(filter(condition, combs))
    return combs

class CardGroupCode(BaseCardGroupClass):
  def __init__(
    self, 
    code, 
    card_type='STANDARD', 
    game_type=GConst.ChinesePokerKey, 
    max_score=100,
    min_score=0,
    default_method_set_no=None,
  ):
    super().__init__(game_type, card_type)
    self.code = tuple(code)
    
    self.max_score = max_score
    self.min_score = min_score
    self.default_method_set_no = default_method_set_no
    return
  

  def get_code_fixed_length(self, code_length=3, fill_value=-1):
    if len(self.code) < code_length:
      code = self.fill_code(self.code, code_length, fill_value)
    else:
      code = self.code[:code_length]
    return code

  def __repr__(self):
    repr_str = f'CardGroupCode{str(self.code)}'
    return repr_str

  def __hash__(self):
    return hash(self.code)

  def __format__(self, spec):
    short_str = CConst.card_group_labels_map[self.game_type][self.code[0]]
    long_str = CConst.GEN_card_group_display_str[short_str]
      
    if spec == 'S':
      out_str = long_str  
    elif spec == 'F':
      number_str = [CConst.suit_number_strength_orders[self.card_type]['Numbers'][i] for i in self.code[1:]]
      number_str = '[' + ''.join(number_str) + ']'
      out_str = long_str + ' ' + number_str
      
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

  def __ge__(self, other):
    if self.__eq__(other) or self.__gt__(other):
      return True
    else:
      return False
  
  @classmethod
  def load_set_scoring_file(cls, method):
    prctile_data = pd.read_csv(GConst.data_files_for_set_scoring[method])

    if 'TopLevelCode' in prctile_data.columns:
      prctile_data.sort_values(['TopLevelCode','SecLevelCode','ThirdLevelCode'], inplace=True)
    else:
      prctile_data.sort_values(['CodeLevel1','CodeLevel2','CodeLevel3'], inplace=True)

    return prctile_data

  def calc_code_score_from_dict(self, score_dict, code_length=None, code_fill_val=-1):
    if code_length is None:
      code_length = len(list(score_dict.keys())[0])
    code_fixed_length = self.get_code_fixed_length(code_length, code_fill_val)

    return score_dict[code_fixed_length]
  
  def calc_code_score(
    self, 
    method=None, 
    prctile_data=None, 
    set_no=1, 
    default_method_set_no=None,
  ):
    """Calculate score of single set

    Keyword Arguments:
        method {[type]} -- [description] (default: {None})
        prctile_data {[type]} -- [description] (default: {None})
        set_no {int} -- [description] (default: {1})
        default_method_set_no {[type]} -- [description] (default: {None})

    Returns:
        [float] -- score of set
    """
    # Use default method for specific set. Note this overrides method
    if default_method_set_no is None and self.default_method_set_no is not None:
      default_method_set_no = self.default_method_set_no
    if default_method_set_no:
      method = GConst.GEN_default_scoring_methods[self.game_type][default_method_set_no-1]
      prctile_data = self.load_set_scoring_file(method)
    elif prctile_data is None:
      prctile_data = self.load_set_scoring_file(method)
    
    # Use specific method
    if method == 'Best5CardPrctile':
      #return prctile_data
      filt = (prctile_data['TopLevelCode'] == self.code[0]) & (prctile_data['SecLevelCode'] == self.code[1])
      if len(self.code) > 2:
        filt = filt & (prctile_data['ThirdLevelCode'] == self.code[2])

      score = prctile_data['Top3CodePctile'].loc[filt].values[0]
      #filt = (prctile_data.index.get_level_values(0) == self.code[0]) & (prctile_data.index.get_level_values(1) == self.code[1])
      #if len(self.code) > 2:
      #  filt = filt & (prctile_data.index.get_level_values(2) == self.code[2])

      #score = prctile_data[filt].values[0]
    elif method == 'GreedyFromSet1Prctile':
      filt = (prctile_data['TopLevelCode'] == self.code[0]) & (prctile_data['SecLevelCode'] == self.code[1])
      if len(self.code) > 2:
        filt = filt & (prctile_data['ThirdLevelCode'] == self.code[2])

      score = prctile_data[f'Set{set_no}MaxPctile'].loc[filt].values[0]
    else:
      filt = (prctile_data['CodeLevel1'] == self.code[0]) & (prctile_data['CodeLevel3'] == self.code[1])
      if len(self.code) > 2:
        filt = filt & (prctile_data['CodeLevel3'] == self.code[2])
      
      if filt.sum() == 1:
        score = prctile_data['MaxPctile'].loc[filt].values[0]
      elif filt.sum() == 0:
        code_values_list = list(prctile_data[['CodeLevel1','CodeLevel2','CodeLevel3']].iloc[0])
        code_values_list = [int(code) for code in code_values_list]
        max_code_in_file = CardGroupCode(code_values_list)
        code_values_list = list(prctile_data[['CodeLevel1','CodeLevel2','CodeLevel3']].iloc[-1])
        code_values_list = [int(code) for code in code_values_list]
        min_code_in_file = CardGroupCode(code_values_list)
          
        if self > max_code_in_file:
          #score = prctile_data['MaxPctile'].iloc[0]
          score = 100 - self.max_score  
        elif self < min_code_in_file:
          #score = prctile_data['MaxPctile'].iloc[-1]
          score = 100 - self.min_score

        # VC: can write better algorithm!  
        else:
          for r_ind in range(prctile_data.shape[0]):
            code_values_list = list(prctile_data[['CodeLevel1','CodeLevel2','CodeLevel3']].iloc[r_ind])
            code_values_list = [int(code) for code in code_values_list]
            temp_code = CardGroupCode(code_values_list)
            if self >= temp_code:
              score = prctile_data['MaxPctile'].iloc[r_ind]
              break

    score = 100-score
    return score


  def min_code_for_given_score(self, method='GreedyFromSet1Prctile', prctile_data=None, set_no=1):    
    if prctile_data == None:
      prctile_data = pd.read_csv(GConst.data_files_for_set_scoring[method])
    return
#def _describe_chinese_poker_card_group(self):
#  return
