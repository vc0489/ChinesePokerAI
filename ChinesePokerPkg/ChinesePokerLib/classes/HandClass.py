from random import shuffle
from timeit import default_timer as timer
from typing import Tuple, Union 
import itertools
import numpy as np
import pandas as pd
from deprecated import deprecated

from ChinesePokerLib.classes.CardClass import CardClass
from ChinesePokerLib.classes.CardGroupClass import CardGroupClassifier, CardGroupCode
import ChinesePokerLib.vars.CardConstants as CConst
import ChinesePokerLib.vars.GameConstants as GConst
from ChinesePokerLib.classes.UtilityClasses import VarChecker
from ChinesePokerLib.classes.ExceptionClasses import HandSplitInfoError, HandMissingScoringMethodError

from ChinesePokerLib.modules.UtilityFunctions import flattened_list

class HandClass():
  # Constructor 1
  def __init__(
    self, 
    cards, 
    hand_type, 
    card_type='STANDARD',
  ):
    self.cards = cards
    self.hand_type = hand_type
    self.card_type = card_type
    return

  def __repr__(self):
    """
    ***| S  H  D  C |ALL
    ---+------------+---
      A| x  x       |  2
      K|       x  x |  2
      Q| x          |  1
      J|            | 
     10|    x  x  x |  3
      9|            |
      8| x          |  1
      7|    x       |  1
      6|            |
      5|       x    |  1
      4| x          |  1
      3|    x       |  1
      2|            |
    ---+------------+---
    ALL| 4  4  3  2 | 13
    """
    fill_width = 3
    vert_sep = '|'
    hor_sep = '-'
    cross_sep = '+'
    newline = '\n' 
    present_char = 'x'
    suits = CConst.suit_number_strength_orders[self.card_type]['Suits']
    numbers = CConst.suit_number_strength_orders[self.card_type]['Numbers']
    #_width = fill_width*len(suits) + 1

    # First line
    display_str = fill_width*'*' + vert_sep 
    for suit in suits:
      display_str += suit.center(fill_width)
    display_str += vert_sep + 'ALL'.center(fill_width)
    display_str += newline
    
    
    # Second line - separator line
    sep_line = fill_width*hor_sep + cross_sep + \
               fill_width*len(suits)*hor_sep + cross_sep + \
               fill_width*hor_sep + newline
    display_str += sep_line

    suit_number_combs = []
    for card in self.cards:
      suit_number_combs.append((card.suit, card.number))

    # Line for each number
    for number in numbers:
      number_line = number.rjust(fill_width) + vert_sep
      n_suits = 0
      for suit in suits:
        if (suit, number) in suit_number_combs:
          number_line += present_char.center(fill_width)
          n_suits += 1
        else:
          number_line += ' '*fill_width
      number_line += vert_sep
      if n_suits > 0:
        number_line += str(n_suits).rjust(fill_width)
      else:
        number_line += ' '*fill_width
      number_line += newline
      display_str += number_line
    
    display_str += sep_line

    # Final line, sum over all suits
    display_str += 'ALL' + vert_sep

    for suit in suits:
      n_numbers = len([1 for comb in suit_number_combs if comb[0]==suit])
      display_str += str(n_numbers).center(fill_width)
    display_str += vert_sep + str(len(suit_number_combs)).rjust(fill_width) + newline

    return display_str

  def _shuffle_cards(self, cards=None):
    """Shuffle cards in hand

    Keyword Arguments:
        cards {[type]} -- [description] (default: {None})

    Returns:
        [type] -- [description]
    """
    if cards is None:
      cards = self.cards
    
    cards_with_inds = [(i, card) for i, card in enumerate(cards)]
    shuffle(cards_with_inds)

    orig_inds, shuffled_cards = zip(*cards_with_inds)
    
    return list(shuffled_cards), list(orig_inds)

  # Constructor 2
  #@classmethod 
  #def from_card_objs(self, cards, hand_type='ChinesePoker'):
  #  suits = [card.suit for card in cards]
  #  numbers = [card.number for card in cards]
  #  self.__init__(suits, numbers)
  #  return

  #def compare_strength(self, to_compare_with):
  #
  #  return

class SplitHandClass(HandClass):
  """[summary]

  Arguments:
      HandClass {[type]} -- [description]
  
  """

  def __init__(
    self, 
    cards, 
    hand_type, 
    split_into, 
    force_ascending,
  ):
    super().__init__(cards, hand_type)
    
    self.split_into = split_into
    self.force_ascending = force_ascending
    return
  
  def _random_split(self, cards=None, split_into=None):
    if cards is None:
      cards = self.cards
    if split_into is None:
      split_into = self.split_into

    cards, orig_inds = self._shuffle_cards(cards)
    split_cards = []
    split_inds = []

    cum_split_into = list(np.cumsum(split_into))
    cum_split_into = [0, ] + cum_split_into
    for setI in range(len(split_into)):

      # Sort inds
      temp_set = cards[cum_split_into[setI]:cum_split_into[setI+1]]
      temp_inds = orig_inds[cum_split_into[setI]:cum_split_into[setI+1]]
      temp_set_inds = zip(temp_inds, temp_set)
      temp_set_inds = sorted(temp_set_inds, key=lambda x: x[0])
      temp_inds, temp_set = zip(*temp_set_inds)
      split_cards.append(temp_set)
      split_inds.append(temp_inds)
    return split_cards, split_inds

  def _check_ascending(self, codes):
    for cI in range(len(codes)-1):
      if codes[cI+1] < codes[cI]:
        return False
    return True

  def _get_codes_of_split(self, split_hand):
    codes = []
    classifier = CardGroupClassifier()
    for card_set in split_hand:
      code = classifier.find_n_card_set_codes(card_set, set_size=len(card_set))[0][0]
      codes.append(code)

    return codes


  def _random_ascending_split(self):

    while True:
      test_split, test_split_inds = self._random_split()
      
      codes = self._get_codes_of_split(test_split)
      
      is_ascending = self._check_ascending(codes)
      if is_ascending:
        break

      elif self.hand_type == GConst.ChinesePokerKey:
        # If not ascending and hand type is Chinese Poker, try switching 2nd and 3rd sets
        if (codes[2] < codes[1]) and (codes[2] > codes[0]):
          codes = [codes[0], codes[2], codes[1]]
          test_split_inds = [test_split_inds[0], test_split_inds[2], test_split_inds[1]]
          test_split = [test_split[0], test_split[2], test_split[1]]

    return test_split, test_split_inds, codes

  def _update_code_comb_pool(self, cur_codes, new_codes, filter_strength='LIGHT'):
    """Helper function for updating ?

    Arguments:
        cur_codes {[type]} -- [description]
        new_codes {[type]} -- [description]

    Keyword Arguments:
        filter_strength {str} -- [description] (default: {'LIGHT'})

    Returns:
        [type] -- [description]
    """

    if len(cur_codes) == 0:
      accept_new_code = True
      to_remove_inds = []
    else:
      if filter_strength.upper() == 'LIGHT':
        max_first_set_code = max([codes[0] for codes in cur_codes])
        if new_codes[-1] <= max_first_set_code:
          # Reject new split
          accept_new_code = False
          to_remove_inds = None
        else:
          # Aceept new split, check for any existing to be removed
          accept_new_code = True
          to_remove_inds = [i for i,codes in enumerate(cur_codes) if codes[-1] <= new_codes[0]]
      elif filter_strength.upper() == 'STRONG':
        n_sets = len(new_codes)
        to_remove_inds = []
        accept_new_code = True
        for cI, codes in enumerate(cur_codes):
          comparison = [new_codes[sI] < codes[sI] for sI in range(n_sets)]
          unique_bools = list(set(comparison))
          
          if len(unique_bools) == 1:
            if unique_bools[0] is True:
              # All codes are worse, reject instantly
              accept_new_code = False
              to_remove_inds = None
              break
            elif unique_bools[0] is False:
              # All codes, adding existing to to_remove_inds, keep checking
              #accept_new_code = True
              to_remove_inds.append(cI)
          
    return accept_new_code, to_remove_inds

  def _random_valid_sets(self, n_set_combs=10, max_sec=60, filter_strength=None):
    
    all_inds = []
    all_codes = []
    all_cards = []
    
    start = timer()
    
    n_tested_splits = 0
    while len(all_codes) < n_set_combs:
      if self.force_ascending:
        test_split, test_split_inds, test_codes = self._random_ascending_split()
        n_tested_splits += 1
        if test_codes not in all_codes:
          
          if filter_strength is not None:
            to_accept, to_remove_inds = self._update_code_comb_pool(all_codes, test_codes, filter_strength)

            if to_accept:
              if len(to_remove_inds) > 0:
                to_remove_inds = sorted(to_remove_inds, reverse=True)
                for ind in to_remove_inds:
                  del all_inds[ind]
                  del all_codes[ind]
                  del all_cards[ind]
              all_inds.append(test_split_inds)
              all_cards.append(test_split)
              all_codes.append(test_codes)  
          else:      
            all_inds.append(test_split_inds)
            all_cards.append(test_split)
            all_codes.append(test_codes)
        else:
          continue
      else:
        print ('VC: _random_valid_sets not implemented for self.force_ascending==False')
        pass
      
      if max_sec is not None and (timer()-start) > max_sec:
        print('_random_valid_sets out of time')
        break
    sets = list(zip(all_inds, all_cards, all_codes))
    return sets, n_tested_splits

  
  
  def _yield_random_valid_set(self):
    all_codes = []
    
    while True:
      if self.force_ascending:
        test_split, test_split_inds, test_code = self._random_ascending_split()
        if test_codes not in all_codes:
          all_codes.append(test_codes)
          yield (test_split_inds, test_split, test_code)
        
      else:
        print ('VC: _random_valid_sets not implemented for self.force_ascending==False')
        yield None        
  
  #@classmethod
  #def from_suits_and_numbers(self, suits, numbers, hand_type='ChinesePoker'):
  #  return


class ChinesePokerHandClass(SplitHandClass):
  """[summary]

  Arguments:
      SplitHandClass {[type]} -- [description]
  """

  def __init__(
    self, 
    cards, 
  ):
    # VC TODO: need to add variable checking

    hand_type=GConst.ChinesePokerKey # CHINESE-POKER
    split_into=GConst.GEN_hands_split_into[hand_type] # (3,5,5)
    force_ascending = GConst.GEN_hands_split_ascending_required[hand_type] # True
    super().__init__(cards, hand_type, split_into, force_ascending)
    
    return

  @classmethod
  def from_suits_and_numbers(self, suits, numbers):
    """Alternative constructor using separate lists of suits and numbers

    Arguments:
        suits {[type]} -- List of suits
        numbers {[type]} -- List of numbers
    """
    cards = []
    for suit, number in zip(suits, numbers):
      cards.append(CardClass(suit, number))
    self.__init__(cards)
    
    return
  

  #######################################
  ### START SCORING RELATED FUNCTIONS ###
  #######################################
  
  def _create_scoring_dict(
    self, 
    scoring_methods, 
    weights=None, 
    score_columns=None, 
    score_column_transforms=None,
    set_size=5, 
    max_code_length=3,
    min_score=0,
    max_score=100,
  ):
    """ Create dictionary mapping code to score for quick lookup.

     scoring_methods can be:
       
       [1] A single string - use one method only. 
           E.g. 'method_name'
            
       [2] Container of strings - combine two or more methods.
           E.g. ['method1_name', 'method2_name'] 


    """
    # Single method
    if isinstance(scoring_methods, str):
      scoring_methods = [scoring_methods]
      weights = [1]
    elif weights is None:
      weights = [1/len(scoring_methods) for method in scoring_methods]
    
    if isinstance(score_columns, str):
      score_columns = [score_columns for method in scoring_methods]
    
    if score_column_transforms is None:
      score_column_transforms = [lambda x: 100-x for method in scoring_methods]

    classifier = CardGroupClassifier()
    
    #all_possible_codes = classifier.all_possible_set_codes(set_size, max_code_length)

    full_score_table = self._gen_empty_full_scoring_table(set_size, max_code_length)
    full_score_table['WeightedScore'] = 0
    join_list = [f'CodeLevel{level}' for level in range(1, max_code_length+1)]
    for mI, method in enumerate(scoring_methods):
      method_score_table = self._load_single_scoring_table(method)
      score_label = f'Score{mI+1}'

      # Remove everything except for code and score columns
      score_column= score_columns[mI]
      method_score_table = method_score_table[join_list + [score_column]]
      
      # Rename to standard
      method_score_table.rename(columns={score_column: score_label}, inplace=True)

      # Apply transformation
      method_score_table[score_label] = method_score_table[score_label].apply(score_column_transforms[mI])
      
      # Join on code
      full_score_table = full_score_table.merge(method_score_table, on=join_list, how='left')
      
      # Fill missing
      # -> Use back fill first, then fill the rest with 0
      bfill_score = full_score_table[score_label].fillna(method='bfill')
      bfill_score = bfill_score.fillna(value=min_score)


      ffill_score = full_score_table[score_label].fillna(method='ffill')
      ffill_score = ffill_score.fillna(value=max_score)

      full_score_table[score_label] = (bfill_score + ffill_score)/2
      

    # Calculate weighted score
    
    for mI in range(len(scoring_methods)):
      full_score_table['WeightedScore'] += weights[mI] * full_score_table[f'Score{mI+1}']
  
    # Convert to dictionary
   
    keys = full_score_table[join_list].itertuples(index=False, name=None)
    vals = full_score_table['WeightedScore']

    score_dict = dict(zip(keys, vals))

    return score_dict

  def _gen_empty_full_scoring_table(self, set_size, code_length, code_fill_val=-1):
    classifier = CardGroupClassifier()
    all_possible_codes = classifier.all_possible_set_codes(set_size, code_length, code_fill_val)
     
    scoring_table = pd.DataFrame()
    for level in range(1, code_length+1):
      scoring_table[f'CodeLevel{level}'] = [code.code[level-1] for code in all_possible_codes]
    return scoring_table
  
  def load_default_scoring_tables(self):
    return self._load_scoring_tables(GConst.GEN_default_scoring_methods[self.hand_type])
  
  def _load_single_scoring_table(self, scoring_method):
    return CardGroupCode.load_set_scoring_file(scoring_method)

  def _load_scoring_tables(self, scoring_methods):
    """Loads tables for all three sets.

    Args:
        scoring_methods ([type]): [description]

    Returns:
        [type]: [description]
    """
    if isinstance(scoring_methods, str):
      n_splits = len(self.split_into)
      scoring_methods = [scoring_methods in range(n_splits)]
    
    scoring_tables = [self._load_single_scoring_table(method) for method in scoring_methods]
  
    return scoring_tables

  def _score_code_sets(
    self,
    code_sets,
    set_weights=None,
    scoring_dicts=None,
  ):
    #n_splits = len(self.split_into)
    n_codes = len(code_sets)
    
    #if isinstance(scoring_methods, str):
    #  scoring_methods = [scoring_methods in range(n_splits)]
    
    all_scores = []

    set_weights, scoring_diots = self._initialise_scoring_vars(
      set_weights, scoring_dicts,
    )

    for i, code_set in enumerate(code_sets):
      #print(f'{i+1}/{n_codes}')
      
      set_score = self.split_codes_weighted_score(
        code_set, set_weights, scoring_dicts
      )
      all_scores.append(set_score)
  
    return all_scores
  
  def split_codes_weighted_score(
    self,
    split_codes=None,
    set_weights=None,
    scoring_dicts=None, #scoring_tables=None,
    code_length=3,
    code_fill_val=-1,
  ):
    if split_codes is None:
      split_codes = self.split_info['Codes']

    n_splits = len(self.split_into)

    set_weights, scoring_dicts = self._initialise_scoring_vars(
      set_weights, scoring_dicts
    )

    splits_scores = [split_codes[sI].calc_code_score_from_dict(scoring_dicts[sI], code_length, code_fill_val) for sI in range(n_splits)]
    #splits_scores = [split_codes[sI].calc_code_score(method=scoring_methods[sI], prctile_data=scoring_tables[sI]) for sI in range(n_splits)]
    weighted_score = sum([set_weights[sI]*splits_scores[sI] for sI in range(n_splits)])

    return weighted_score, splits_scores
  
  """
  def _initialise_scoring_vars(self, set_weights, scoring_dicts):
    
    if scoring_dicts is None:
      scoring_dicts = self.scoring_dicts  

    
    if set_weights is None:
      set_weights = self.set_weights

    
    return set_weights, scoring_dicts
  """
  #####################################
  ### END SCORING RELATED FUNCTIONS ###
  #####################################



  ###########################################
  ### START VERIFICATION HELPER FUNCTIONS ###
  ###########################################
  def _verify_split_inds(self, split_inds, var_check_obj=VarChecker()):
    """Check set of split inds.

    Arguments:
        split_inds {Container of constainers} -- [description]

    Keyword Arguments:
        var_check_obj {[type]} -- [description] (default: {VarChecker()})

    Raises:
        HandSplitInfoError: [description]
        HandSplitInfoError: [description]
    """

    # Check split correctly
    correct_split = var_check_obj.check_lengths_of_iterable(split_inds, self.split_into)
    
    if not correct_split:
      raise HandSplitInfoError(f'Split inds incorrect. Expect split lengths of {self.split_into}.')

    # Check have all cards
    all_inds = flattened_list(split_inds)

    have_all_inds = var_check_obj.check_one_of_each_int_in_range(all_inds,0,sum(self.split_into)-1)
    
    if not have_all_inds:
      raise HandSplitInfoError('Do not have all expected cards in split.')
    
    return

  def _verify_split_codes(self, split_codes, var_check_obj=VarChecker()):
    
    # Check have right number of codes
    exp_n_codes = len(self.split_into)
    if len(split_codes) != exp_n_codes:
      raise HandSplitInfoError(f'Expect {exp_n_codes} codes.')

    # Check have increasing code strength
    is_increasing_strength = var_check_obj.check_is_sorted(split_codes, ascending=True, allow_equal=True)
    if not is_increasing_strength:
      raise HandSplitInfoError(f'Code strengths not non-decreasing.')

    return

  def _verify_split_scores(self, split_scores, var_check_obj=VarChecker()):
    # Check have right number of scores
    exp_n_scores = len(self.split_into)
    if len(split_scores) != exp_n_scores:
      raise HandSplitInfoError(f'Expect {exp_n_scores} scores.')

    # Check have valid scores (of int or float type)
    all_numerical = var_check_obj.check_all_elements_in_container_of_given_types(split_scores,(int, float))
    if not all_numerical:
      raise HandSplitInfoError(f'Expect split scores to be numerical.')
  
  def _verify_split_cards(self, split_cards, var_check_obj=VarChecker()):
    
    # Check split correctly
    correct_split = var_check_obj.check_lengths_of_iterable(split_cards, self.split_into)
    
    if not correct_split:
      raise HandSplitInfoError(f'Cards split incorrectly. Expect split lengths of {self.split_into}.')

    # Check cards are same as original
    all_cards = flattened_list(split_cards)
    if set(self.cards) != set(all_cards):
      raise HandSplitInfoError(f'Combined split cards do not match original set of cards.')

    return

  #########################################
  ### END VERIFICATION HELPER FUNCTIONS ###
  #########################################
  