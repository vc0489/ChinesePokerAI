"""Methods needed:
Choose splits from cards: cards -> splits
"""

from timeit import default_timer as timer
import pandas as pd
from datetime import datetime

from ChinesePokerLib.classes.CardGroupClass import CardGroupClassifier, CardGroupCode
from ChinesePokerLib.classes.DataClass import DataClass
from ChinesePokerLib.classes.ExceptionClasses import StrategyIDUsedError

import ChinesePokerLib.modules.DBFunctions as DBF

import ChinesePokerLib.vars.GameConstants as GConst
import ChinesePokerLib.vars.GlobalConstants as GlobConst


class StrategyClass:
  def __init__(self):
    
    return


class ChinesePokerStrategyClass(StrategyClass):
  game_type = GConst.ChinesePokerKey
  split_into = GConst.GEN_hands_split_into[game_type]
  strategy_table = GConst.CHINESE_POKER_db_consts['split_strategies_table']
  strategy_type_table = GConst.CHINESE_POKER_db_consts['split_strategy_types_table']
  
  
  def __init__(
    self,
    strategy_type,
    pick_max_elapsed_sec,
    pick_max_gen_splits,
    strategyID=None,
    strategy_name=None,
  ):
    super().__init__()
    self.strategy_type = strategy_type
    self.pick_max_elapsed_sec = pick_max_elapsed_sec
    self.pick_max_gen_splits = pick_max_gen_splits
    self.strategyID = strategyID
    self.strategy_name = strategy_name
    return

  def split_generator(self, cards, *args, **kwargs):
    """
    API:
    

    Args:
        cards ([type]): [description]
    """
    return
  
  def split_scorer(self, split_cards, *args, **kwargs):
    if split_codes is None:
      split_codes = ['Code1','Code2','Code3']
    
    return 666

  def split_picker(self, scores, sup_info=None):

    return scores.index(max(scores))
  
  """
  def yield_splits_data_from_json(
    self, 
    json_file=None, 
    start_deal_no=None, 
    end_deal_no=None
  ):
  """
  def pick_best_splits_from_json_splits_data(
    self, 
    json_file=None, 
    start_deal_no=None, 
    end_deal_no=None
  ):
    """Useful to generate best split for many dealt hands using same strategy

    Args:
        json_file ([type], optional): [description]. Defaults to None.
    """
    data_obj = DataClass()

    if json_file is None:
      json_file = GlobConst.DEFAULT_SPLITS_JSON_FILE

    dealt_splits_gen = data_obj.yield_splits_data_from_json(json_file, start_deal_no, end_deal_no)    
    
    best_splits = []
    
    while 1:
      deal_best_splits = {}
      deal_no, splits_data = next(dealt_splits_gen)
      if deal_no is None:
        break

      for player, splits_data in splits_data.items():
        output, _, _ = self.pick_single_split_from_full_split_data(splits_data)
        deal_best_splits[player] = {
          'Cards': [
            tuple([str(card) for split_cards in output[1] for card in split_cards]),
          ],
          'Scores': [
            output[5],
          ],
          'Codes': [
            [code.code for code in output[2]],
          ],
        }
      
      best_splits.append(deal_best_splits)
    return best_splits

  def pick_single_split_from_full_split_data(self, splits_data):
    """[summary]

    Args:
        splits_data (Dict): Dict with keys 'Cards', 'Scores' and 'Code'
                            Values are each lists of equal length, one entry in list is one split 
                            'Cards': list of ordered cards - the order determines the split 
                                    (first 3 = first set, next 5 = second set, final 5 = final set)
                            'Scores': list of split scores
                            'Codes': list of split codes, will be converted to CardGroupCode for output

    Returns:
        [type]: [description]
    """
    n_splits = len(splits_data['Cards'])
    splits_scores = []
    for split_ind in range(n_splits):
      if 'Scores' in splits_data:
        scorer_output = self.split_scorer(None, None, splits_data['Scores'][split_ind], None)

      splits_scores.append(scorer_output)
    
    picked_split_ind = self.split_picker([score[0] for score in splits_scores])
    output_split_cards = []
    cur_card_ind = 0
    for set_size in self.split_into:
      output_split_cards.append(tuple(splits_data['Cards'][picked_split_ind][cur_card_ind:cur_card_ind+set_size]))
      cur_card_ind += set_size

    output = (
      None, # Inds
      output_split_cards, # Cards
      [CardGroupCode(code) for code in splits_data['Codes'][picked_split_ind]], # Codes 
      splits_data['Scores'][picked_split_ind], # Scores,
      None,
      splits_scores[picked_split_ind][1],
      splits_scores[picked_split_ind][0],
    )

    return output, None, None

  def pick_single_split(self, cards, max_elapsed_sec=None, verbose=False):
    if max_elapsed_sec is None:
      max_elapsed_sec = self.pick_max_elapsed_sec

    start = timer()
    generator = self.split_generator(cards)
    
    splits_generated = []
    for sI in range(self.pick_max_gen_splits):
      next_split = next(generator, None)
      if verbose:
        print(f'Split {sI+1} - Total elasped time {timer()-start}s')
      if next_split is None:
        break

      splits_generated.append(next_split)
      if timer()-start > max_elapsed_sec:
        break
          
      
    # split_generator: split_inds, split_cards, split_codes, split_scores, weighted_score
    
    if isinstance(splits_generated[0][4], float):
      splits_scores = [(split[4], split[3]) for split in splits_generated]
    else:
      splits_scores = []
      for split in splits_generated:
        _, cards, codes, scores, weighted_score = split
        scorer_output = self.split_scorer(cards, codes, scores, weighted_score) 
        splits_scores.append(scorer_output) # VC: probably one of the items of split
      
    picked_split_ind = self.split_picker([score[0] for score in splits_scores])
    best_split = list(splits_generated[picked_split_ind])
    best_split.append(splits_scores[picked_split_ind][1])
    best_split.append(splits_scores[picked_split_ind][0])
    best_split = tuple(best_split)
    
    return best_split, list(zip(splits_generated, splits_scores)), timer()-start
  
  def gen_all_splits(self, cards, verbose=True):
    """Generate all feasible splits based on set group codes

    Args:
        cards ([type]): [description]
        verbose (bool, optional): [description]. Defaults to True.

    Returns:
        [type]: [description]
    """
    start = timer()
    
    # To generate all splits should not apply any score-based filtering or time restrictions
    generator = self.split_generator(cards, method='SystematicUnfiltered')
    
    splits_generated = []
    while 1:
      next_split = next(generator, None)
      if next_split is None:
        break
      if verbose:
        print(f'Split {len(splits_generated)} - Total elasped time {timer()-start}s')
      
      splits_generated.append(next_split)
    return splits_generated, timer()-start

class ChinesePokerPctileScoreStrategyClass(ChinesePokerStrategyClass):
  
  code_fill_val = -1
  weights_table = GConst.CHINESE_POKER_db_consts['percentile_strategy_weights_table']
  strategy_typeID = 1

  # Constructor 1
  def __init__(
    self,
    score_methods=None,
    #score_set_weights=None,
    #score_methods=None,
    #score_method_weights=None, 
    #score_columns=None, # MaxPrctile
    #score_column_transforms=None, # lambda x: 100-x
    score_code_lengths=None, # 3
    split_gen_filter_by_score = False,
    split_gen_score_filter_buffer = 0,
    pick_max_elapsed_sec = 120,
    pick_max_gen_splits = 5000,
    strategyID = None,
    strategy_name = None,
  ):
    super().__init__(
      'WeightedPercentiles',
      pick_max_elapsed_sec,
      pick_max_gen_splits,
      strategyID,
      strategy_name,
    )
    
    #if score_set_weights is None:
    #  score_set_weights = GConst.GEN_default_set_score_weights[self.game_type]
    #self.score_set_weights = score_set_weights

    if score_methods is None:
      score_methods = GConst.GEN_default_score_methods[self.game_type]
    self.score_methods = score_methods

    self.score_set_weights = []
    for set_methods in score_methods:
      self.score_set_weights.append(sum([method[2] for method in set_methods]))
    
    #if score_method_weights is None:
    #  score_method_weights = GConst.GEN_default_method_score_weights[self.game_type]
    #self.score_method_weights = score_method_weights

    #if score_columns is None:
    #  score_columns = GConst.GEN_default_score_columns[self.game_type]
    #self.score_columns = score_columns

    #if score_column_transforms is None:
    #  score_column_transforms = GConst.GEN_default_score_column_transforms[self.game_type]
    #self.score_column_transforms = score_column_transforms

    if score_code_lengths is None:
      score_code_lengths = GConst.GEN_default_score_code_lengths[self.game_type]
    self.score_code_lengths = score_code_lengths

    
    #self.score_dicts = []
    

    self.create_all_score_dicts()
    """
    for sI in range(len(self.split_into)):
      score_dict = self._create_score_dict(
        score_methods[sI], 
        score_method_weights[sI],
        score_columns[sI],
        score_column_transforms[sI],
        self.__class__.split_into[sI],
        score_code_lengths[sI],
      )
      self.score_dicts.append(score_dict)
    """

    # Generation parameters
    self.split_gen_params = {
      'FilterByScore': split_gen_filter_by_score,
      'ScoreFilterBuffer': split_gen_score_filter_buffer,
    }

    self.classifier = CardGroupClassifier()
    
    
    if split_gen_filter_by_score:
      self.code_map_set_3_to_1 = self.classifier.gen_code_map_diff_set_size(5, 3, self.score_code_lengths[2], self.score_code_lengths[0])
      self.code_map_set_3_to_2 = self.classifier.gen_code_map_diff_set_size(5, 5, self.score_code_lengths[2], self.score_code_lengths[1])
      self.code_map_set_2_to_1 = self.classifier.gen_code_map_diff_set_size(5, 3, self.score_code_lengths[1], self.score_code_lengths[0])
    
    
    return
  
  # Constructor 2 - load from DB
  @classmethod 
  def init_from_db(
    cls, 
    strategyID,
    split_gen_filter_by_score = False,
    split_gen_score_filter_buffer = 0,
    pick_max_elapsed_sec = 120,
    pick_max_gen_splits = 5000,
  ):
    strategy_dict = cls.load_strategy_from_db(strategyID)
    
    return cls(
      strategy_dict['score_methods'],
      strategy_dict['score_code_lengths'],
      split_gen_filter_by_score,
      split_gen_score_filter_buffer,
      pick_max_elapsed_sec,
      pick_max_gen_splits,
      strategyID = strategyID,
      strategy_name = strategy_dict['strategy_name'],
    )
  #  suits = [card.suit for card in cards]
  #  numbers = [card.number for card in cards]
  #  self.__init__(suits, numbers)
  #  return
  #################################
  ### START Generator functions ###
  #################################
  def split_generator(self, cards, method='Systematic'):
    if method=='Systematic':
      return self._yield_systematic_split(cards)
    elif method=='SystematicUnfiltered':
      return self._yield_systematic_split(cards, True)

  def _yield_systematic_split(
    self, 
    cards,
    do_not_filter_by_score=False,
  ):
    """[summary]
    
    VC TODO: add code_length and code_fil_val args?

    Arguments:
        cards    

    Yields:
        [type] -- [description]
    """
    
    # Unpack parameters
    
    filter_by_score = self.split_gen_params['FilterByScore']
    score_filter_buffer = self.split_gen_params['ScoreFilterBuffer']
    
    if do_not_filter_by_score:
      filter_by_score = False

    # FIRST, find all possible final set options
    min_top_level_code = self.classifier.top_level_code_from_label('OnePair')
    final_set_options = self.classifier.find_n_card_set_codes(
      cards, 
      set_size=self.split_into[-1],
      min_code=CardGroupCode([min_top_level_code,])
    )

    accepted_splits = []
    
    if filter_by_score:
      max_score = None
    max_first_set_code = CardGroupCode([999,0])
    # Merge final set options is code exactly the same
    
    final_setI = 1
    cur_code = final_set_options[0][0]
    merged_final_set_options = []
    agg_final_set_option = [final_set_options[0]]
    while final_setI < len(final_set_options):
      next_code = final_set_options[final_setI][0]
      if next_code == cur_code:
        agg_final_set_option.append(final_set_options[final_setI])
      else:
        merged_final_set_options.append(agg_final_set_option)
        agg_final_set_option = [final_set_options[final_setI]]
        cur_code = next_code
      final_setI += 1
    merged_final_set_options.append(agg_final_set_option)

    # SECOND, loop over final set codes. 
    # For each final code, find all possible valid second set options
    # (max code being the code of final set in consideration). 
    for merged_final_setI, merged_final_set_option in enumerate(merged_final_set_options):
      # This is shared between all options within the merged set
      final_set_code = merged_final_set_option[0][0]
      
      if final_set_code < max_first_set_code:
        break

      if filter_by_score and max_score is not None:
        filled_final_set_code = CardGroupCode.fill_code(final_set_code.code, self.score_code_lengths[2], self.code_fill_val, trim_if_needed=True)
        mapped_code_3_to_1 = CardGroupCode(self.code_map_set_3_to_1[filled_final_set_code])
        mapped_code_3_to_2 = CardGroupCode(self.code_map_set_3_to_2[filled_final_set_code])
        pot_score = self.split_scorer(
          None,
          [mapped_code_3_to_1, mapped_code_3_to_2, final_set_code],
        )[0]

        if pot_score < (max_score-score_filter_buffer):
          break
      
      accepted_for_this_final_set_code = []
      combs_for_this_final_set_code = []

      for final_set_option in merged_final_set_option:

        final_set_inds = tuple(sorted(final_set_option[2]))
        final_set_cards = tuple([cards[i] for i in final_set_inds])

        remaining_inds_and_cards = [(i,card) for i,card in enumerate(cards) if i not in final_set_inds]
        remaining_inds, remaining_cards = zip(*remaining_inds_and_cards)

        second_set_options = self.classifier.find_n_card_set_codes(
          remaining_cards,
          set_size=self.split_into[1],
          max_code=final_set_code,
        )
        
        if len(second_set_options) == 0:
          continue

        # THIRD, for final set in consideration loop over valid seconds sets and check 
        # if implied first set is valid. 
        # If valid, go through logic to check whether to accept split.
        for second_set_option in second_set_options:
          second_set_code = second_set_option[0]
          if second_set_code < max_first_set_code:
            break
          second_set_inds = [remaining_inds[i] for i in second_set_option[2]]
          second_set_inds = tuple(sorted(second_set_inds))
          second_set_cards = tuple([cards[i] for i in second_set_inds])
          
          first_set_cards = tuple([card for i,card in enumerate(remaining_cards) if i not in second_set_option[2]])
          first_set_inds = tuple([i for i in range(len(cards)) if i not in second_set_inds+final_set_inds])

          first_set = self.classifier.find_n_card_set_codes(
            first_set_cards,
            set_size=self.split_into[0],
            max_code = second_set_code,
          )
          
          if len(first_set) == 0:
            # First set code > second set code, so invalid
            continue
          else:
            first_set_code = first_set[0][0]
          

          if filter_by_score:
            
            if max_score is not None:
              filled_second_set_code = CardGroupCode.fill_code(second_set_code.code, self.score_code_lengths[1], self.code_fill_val, trim_if_needed=True)
              mapped_code_2_to_1 = CardGroupCode(self.code_map_set_2_to_1[filled_second_set_code])
              pot_score = self.split_scorer(
                None,
                [mapped_code_2_to_1, second_set_code, final_set_code],
              )[0]
              if pot_score < max_score-(score_filter_buffer):
                break

          
            split_score, set_scores = self.split_scorer(
              None,
              [first_set_code, second_set_code, final_set_code],
            )
          
            if max_score is None:
              max_score = split_score
            elif split_score > max_score:
              max_score = split_score

          else:
            split_score = None
            set_scores = None

          combs_for_this_final_set_code.append(
            (
              [first_set_inds, second_set_inds, final_set_inds],
              [first_set_cards, second_set_cards, final_set_cards],
              [first_set_code, second_set_code, final_set_code],
              set_scores,
              split_score,
            )
          )

      # Sort by 2nd set code then 1st set code, decsending in strength
      combs_for_this_final_set_code = sorted(combs_for_this_final_set_code, key=lambda x: (x[2][1], x[2][0]), reverse=True)

      # FOURTH, go through logic to determine whether to admit split into accepted list.
      for comb in combs_for_this_final_set_code:
        # (a) If accepted list empty, admit split into list.
        if len(accepted_for_this_final_set_code) == 0:
          accepted_for_this_final_set_code.append(comb)

        # (b) If accepted list not empty accept only if first set code is an improvement
        #     over the first set code of the last accepted split.
        #     If the second set code is same as second set code of the last accepted split
        #     then delete last accepted split.

        # If second set code is same as latest in accepted set, then only admit if first set code
        # is an improvement, in which case also delete the latest in accepted set.
        elif comb[2][1] == accepted_for_this_final_set_code[-1][2][1]: # Compare second set code
          if comb[2][0] > accepted_for_this_final_set_code[-1][2][0]:
            del accepted_for_this_final_set_code[-1]
            accepted_for_this_final_set_code.append(comb)
        # If second set code is worse than latest, the only admit if first set code is an 
        # improvement - don't need to delete latest in accepted set in this case.
        else:
          if comb[2][0] > accepted_for_this_final_set_code[-1][2][0]:
            accepted_for_this_final_set_code.append(comb)
        
      # FIFTH, update global accepted list.
      if len(accepted_splits) == 0:
        accepted_splits = accepted_splits + accepted_for_this_final_set_code
        for split_set in accepted_for_this_final_set_code:
          yield split_set
      else:
        splits_to_append = []
        
        for split_to_check in accepted_for_this_final_set_code:
          to_accept=True

          # Reversing accepted splits on average results in fewer checks before reject
          for checkI, existing_split in enumerate(accepted_splits[::-1]):
            
            # We know that final set code is worse than all current final set codes in the global
            # accepted list. So admission into global accepted list requires that either the 
            # first or second set is better than first or second set respectively for all splits 
            # in global accepted list.
            if split_to_check[2][0] <= existing_split[2][0] and split_to_check[2][1] <= existing_split[2][1]:
              # Reject
              to_accept=False              
              break

          # If not rejected, then accept
          if to_accept==True:
            splits_to_append.append(split_to_check)
            yield split_to_check
            
            if split_to_check[2][0] > max_first_set_code:
              max_first_set_code = split_to_check[2][0]

        accepted_splits = accepted_splits + splits_to_append
      
    return      
  
  ###########################
  ### START Score Functions #
  ###########################

  def split_scorer(self, split_cards, split_codes, split_scores=None, weighted_score=None):
    # split_cards not used in this function
    
    if split_scores is not None and weighted_score is not None:
      pass
    elif split_scores is not None and weighted_score is None:
      n_splits = len(self.split_into)
      weighted_score = sum([self.score_set_weights[sI]*split_scores[sI] for sI in range(n_splits)])
    else:
      weighted_score, split_scores = self._split_codes_weighted_score(
        split_codes,
        self.score_set_weights,
        self.score_dicts,
        self.score_code_lengths,
        self.code_fill_val,
      )

    return weighted_score, split_scores

  def _split_codes_weighted_score(
    self,
    split_codes=None,
    set_weights=None,
    score_dicts=None,
    code_lengths=3,
    code_fill_val=-1,
  ):
    if split_codes is None:
      split_codes = self.split_info['Codes']

    n_splits = len(self.split_into)

    splits_scores = [split_codes[sI].calc_code_score_from_dict(score_dicts[sI], code_lengths[sI], code_fill_val) for sI in range(n_splits)]
    weighted_score = sum([set_weights[sI]*splits_scores[sI] for sI in range(n_splits)])

    return weighted_score, splits_scores
    

  ##################################
  ### START Score Dict Functions ###
  ##################################
  def create_all_score_dicts(self):
    self.score_dicts = []
    for sI, set_size in enumerate(self.__class__.split_into):
      set_score_methods = self.score_methods[sI]

      score_dict = self._create_score_dict(
        set_score_methods,
        set_size,
        self.score_code_lengths[sI],
      )
      self.score_dicts.append(score_dict) 
    return

  def _create_score_dict(
    self, 
    score_methods,
    set_size=5, 
    max_code_length=3,
    min_score=0,
    max_score=100,
  ):
    """ Create dictionary mapping code to score for quick lookup.

     score_methods is a list of tuples e.g.
     [
      (5, 3, 1/3),
     ],

     PoolSize, SetSize, MethodWeight
     where MethodWeight is the weight across all sets.
    """
    # Single method
    #if isinstance(score_methods, str):
    #  score_methods = [score_methods]
    #  weights = [1]
    #elif weights is None:
    #  weights = [1/len(score_methods) for method in score_methods]
    
    #if isinstance(score_columns, str):
    #  score_columns = [score_columns for method in score_methods]
    
    #if score_column_transforms is None:
    #  score_column_transforms = [lambda x: 100-x for method in score_methods]

    #classifier = CardGroupClassifier()
    
    #all_possible_codes = classifier.all_possible_set_codes(set_size, max_code_length)

    full_score_table = self._gen_empty_full_score_table(set_size, max_code_length)
    full_score_table['WeightedScore'] = 0
    #full_score_table['NormWeightedScore'] = 0
    #join_list = [f'CodeLevel{level}' for level in range(1, max_code_length+1)]
    join_list = [f'L{level}Code' for level in range(1, max_code_length+1)]
    weights = [method[2] for method in score_methods]
    #normalised_weights = [weight/sum(weights) for weight in weights]
    score_column = 'Percentile'

    for mI, method in enumerate(score_methods):
      #method_score_table = self._load_single_score_table(method)
      method_score_table = self._load_percentiles_from_db(method[0], method[1], max_code_length)
      score_label = f'Score{mI+1}'

      # Remove everything except for code and score columns
      
      method_score_table = method_score_table[join_list + [score_column]]
      
      # Rename to standard
      method_score_table.rename(columns={score_column: score_label}, inplace=True)

      # Apply transformation
      #method_score_table[score_label] = method_score_table[score_label].apply(score_column_transforms[mI])
      
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
    
    for mI in range(len(score_methods)):
      full_score_table['WeightedScore'] += weights[mI] * full_score_table[f'Score{mI+1}']
      #full_score_table['NormWeightedScore'] = full_score_table['WeightedScore']/sum(weights)
    # Convert to dictionary
   
    keys = full_score_table[join_list].itertuples(index=False, name=None)
    vals = full_score_table['WeightedScore']

    score_dict = dict(zip(keys, vals))

    return score_dict

  def _load_single_score_table(self, scoring_method):
    return CardGroupCode.load_set_scoring_file(scoring_method)

  def _gen_empty_full_score_table(self, set_size, code_length, code_fill_val=-1):
    classifier = CardGroupClassifier()
    all_possible_codes = classifier.all_possible_set_codes(set_size, code_length, code_fill_val)
     
    score_table = pd.DataFrame()
    for level in range(1, code_length+1):
      score_table[f'L{level}Code'] = [code.code[level-1] for code in all_possible_codes]
      #score_table[f'CodeLevel{level}'] = [code.code[level-1] for code in all_possible_codes]
    return score_table
  
  ########################################
  ### START DB related functions START ###
  ########################################
  def _load_percentiles_from_db(self, pool_size, set_size, code_max_level):
    latest_gen_date = self._find_latest_percentiles_set_in_db(pool_size, set_size, code_max_level)
    table = GConst.CHINESE_POKER_db_consts['code_percentiles_table']
    query = 'SELECT ' 
    for level in range(1, code_max_level+1):
      query += f'L{level}Code, '
    query += f'Percentile, MeanHandRank, nSamples FROM {table} WHERE ' + \
             f'PoolSize={pool_size} AND SetSize={set_size} AND CodeMaxLevel={code_max_level} AND ' + \
             f"DateGenerated='{latest_gen_date}' "
    query += 'ORDER BY '
    for level in range(1, code_max_level):
      query += f'L{level}Code, '
    query = query[:-2]

    conn = DBF.connect_to_db()
    percentiles_df = pd.read_sql(query, conn)

    percentiles_df.fillna(self.__class__.code_fill_val, inplace=True, downcast='infer')
    return percentiles_df
  

  def _find_latest_percentiles_set_in_db(self, pool_size, set_size, code_max_level):
    """Find latest set of percentiles data in DB for given set of pool_size, set_size 
    and code_max_level.

    Args:
        pool_size (int): [description]
        set_size (int): [description]
        code_max_level (int): [description]

    Returns:
        str: Date string
    """
    table = GConst.CHINESE_POKER_db_consts['code_percentiles_table']
    query = f'SELECT Max(DateGenerated) FROM {table} WHERE PoolSize={pool_size} AND SetSize={set_size} AND CodeMaxLevel={code_max_level}'
    db_output, _ = DBF.select_query(query)

    return datetime.strftime(db_output[0][0], '%Y-%m-%d')
  
  @classmethod
  def load_strategy_from_db(cls, strategyID):
    
    query1 = f'SELECT StrategyName FROM {cls.strategy_table} WHERE StrategyID={strategyID}'
    db_output1, _ = DBF.select_query(query1)

    query2 = 'SELECT SetNo, PoolSize, SetSize, CodeMaxLevel, Weight ' + \
            f'FROM {cls.weights_table} ' \
            f'WHERE StrategyID={strategyID}'
    db_output2, _ = DBF.select_query(query2)

    score_methods = [[] for method in cls.split_into]
    score_code_lengths = [None for method in cls.split_into]

    for row in db_output2:
      method_tuple = (row[1], row[2], row[4])
      score_methods[row[0]-1].append(method_tuple)
      
      if score_code_lengths[row[0]-1] is None:
        score_code_lengths[row[0]-1] = row[3]
    
    strategy_dict = {
      'strategy_name': db_output1[0][0],
      'score_methods': tuple(score_methods),
      'score_code_lengths': tuple(score_code_lengths),
    }
    
    return strategy_dict

  def _get_next_unused_strategyID(self):
    query = f'SELECT MAX(StrategyID) FROM {self.__class__.strategy_table}'
    db_output, _ = DBF.select_query(query)

    if db_output[0][0] is None:
      strategyID = 1
    else:
      strategyID = db_output[0][0] + 1
    return strategyID

  def upload_strategy_to_db(self, overwrite=False):
    if self.strategyID is None:
      self.strategyID = self._get_next_unused_strategyID()
      print (f'This strategy has been assigned ID {self.strategyID}')
    
    query = f'SELECT COUNT(*) FROM {self.__class__.strategy_table} WHERE StrategyID={self.strategyID}'
    db_output, _ = DBF.select_query(query)
    if db_output[0][0] > 0:
      if overwrite is False:
        raise StrategyIDUsedError(f'strategyID {self.strategyID} already exists in the DB')
      elif overwrite is True:
        raise NotImplementedError('Overwrite strategy in upload_strategy_to_db not implemented yet.')
        
    # Insert data into split_strategies
    if self.strategy_name is None:
      temp_name = "NULL"
    else:
      temp_name = self.strategy_name
    query1 = f'INSERT INTO {self.__class__.strategy_table} ' + \
              '(StrategyID, StrategyTypeID, StrategyName) VALUES ' + \
             f'({self.strategyID}, {self.__class__.strategy_typeID}, {temp_name})'
    
    base_query2 = f'INSERT INTO {self.__class__.weights_table} ' + \
                   '(StrategyID, SetNo, PoolSize, SetSize, CodeMaxLevel, Weight) VALUES ' + \
                  f'(%s, %s, %s, %s, %s, %s)'
    query_values2 = []
    for set_i in range(len(self.__class__.split_into)):
      for method in self.score_methods[set_i]:
        row_values = (
          self.strategyID, 
          set_i+1, 
          method[0], 
          method[1], 
          self.score_code_lengths[set_i], 
          method[2],
        )
        query_values2.append(row_values)
    
    # Insert data
    all_queries = [query1, (base_query2, query_values2)]
    DBF.multiple_insert_queries(all_queries)
