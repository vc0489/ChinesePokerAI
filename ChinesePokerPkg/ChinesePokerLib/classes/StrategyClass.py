"""Methods needed:
Choose splits from cards: cards -> splits
"""

from timeit import default_timer as timer
import pandas as pd
import numpy as np
from datetime import datetime
from collections import namedtuple
from deprecated import deprecated
import pickle
from itertools import compress
import random

from ChinesePokerLib.classes.CardGroupClass import CardGroupClassifier, CardGroupCode
#from ChinesePokerLib.classes.DataClass import DataClass
from ChinesePokerLib.classes.ExceptionClasses import StrategyIDUsedError

import ChinesePokerLib.modules.DBFunctions as DBF
from ChinesePokerLib.modules.UtilityFunctions import flattened_list, nth_largest

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
  default_score_column = 'Percentile'
  code_fill_val = -1
  
  ranked_split_info_factory = namedtuple(
    'RankedSplitInfo',
    [
      "Inds",                 # List of tuples
      "Cards",                # List of tuples
      "Codes",                # List of codes
      "GenFilterSupScores",   # ?
      "GenFilterSplitScore",  # None or float
      "StratSupScores",       # ?
      "StratSplitScore",      # None or float
      "Rank",                 # None or integer
      "SeqNo",                # None or integer
    ]
  )
  def __init__(
    self,
    strategy_type,
    score_code_lengths,
    pick_max_elapsed_sec,
    pick_max_gen_splits,
    strategyID=None,
    strategy_name=None,
    sort_set_cards_by_group=False,
    split_gen_filter_by_score=False,
    split_gen_filter_strategy=None,
    split_gen_filter_score_buffer=0,
    split_pick_filter_by_score=False,
    split_pick_filter_strategy=None,
    split_pick_filter_score_buffer=20,
  ):
    super().__init__()
    self.strategy_type = strategy_type
    
    if score_code_lengths is None:
      score_code_lengths = GConst.GEN_default_score_code_lengths[self.game_type]
    self.score_code_lengths = score_code_lengths
    
    self.pick_max_elapsed_sec = pick_max_elapsed_sec
    self.pick_max_gen_splits = pick_max_gen_splits
    self.strategyID = strategyID
    self.strategy_name = strategy_name
    self.sort_set_cards_by_group = sort_set_cards_by_group
    self.classifier = CardGroupClassifier()

    # Split generation parameters
    if split_gen_filter_by_score and split_gen_filter_strategy is None:
      split_gen_filter_strategy = ChinesePokerPctileScoreStrategyClass(split_gen_filter_by_score=False)

    self.split_gen_params = {
      'FilterByScore': split_gen_filter_by_score,
      'FilterStrategy': split_gen_filter_strategy,
      'FilterScoreBuffer': split_gen_filter_score_buffer,
    }    

    if split_gen_filter_by_score:
      self.code_map_set_3_to_1 = self.classifier.gen_code_map_diff_set_size(5, 3, score_code_lengths[2], score_code_lengths[0])
      self.code_map_set_3_to_2 = self.classifier.gen_code_map_diff_set_size(5, 5, score_code_lengths[2], score_code_lengths[1])
      self.code_map_set_2_to_1 = self.classifier.gen_code_map_diff_set_size(5, 3, score_code_lengths[1], score_code_lengths[0])
    
    # Split picker parameters
    if split_pick_filter_by_score and split_pick_filter_strategy is None:
      split_pick_filter_strategy = ChinesePokerPctileScoreStrategyClass()

    self.split_pick_params = {
      'FilterByScore': split_pick_filter_by_score,
      'FilterStrategy': split_pick_filter_strategy,
      'FilterScoreBuffer': split_pick_filter_score_buffer,
    }
    
    return

  #################################
  ### START Generator functions ###
  #################################
  def split_generator(self, cards):
    if self.split_gen_params['FilterByScore']:
      return self._yield_systematic_split(cards, True)
    else:
      return self._yield_systematic_split(cards)

  
  def split_scorer(self, split_cards, split_codes, **kwargs):
    if split_codes is None:
      split_codes = ['Code1','Code2','Code3']
    
    return 666

  def split_picker(self, scores, pick_n=1, unique_code_levels=None, codes=None):
    
    n_scores = len(scores)
    scores_with_inds = list(zip(range(n_scores), scores))
    scores_with_inds = sorted(scores_with_inds, key=lambda x: x[1], reverse=True)

    if unique_code_levels is not None and unique_code_levels > 0:
      cur_split_top_codes = []
      top_n_inds = []
      for sI in range(n_scores):
        orig_ind = scores_with_inds[sI][0]
        split_top_codes = tuple([code.get_code_fixed_length(unique_code_levels) for code in codes[orig_ind]])
        if split_top_codes not in cur_split_top_codes:
          cur_split_top_codes.append(split_top_codes)
          top_n_inds.append(orig_ind)

          if len(top_n_inds) == pick_n:
            break
      
    else:
      if len(scores) < pick_n:
        pick_n = len(scores)
        
      top_n_inds = [item[0] for item in scores_with_inds[:pick_n]]
    return top_n_inds

    
  
  """
  def yield_splits_data_from_json(
    self, 
    json_file=None, 
    start_deal_no=None, 
    end_deal_no=None
  ):
  """

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
    if isinstance(splits_data['Cards'][0][0], (tuple, list)):
      splits_data['Cards'] = [flattened_list(split_cards) for split_cards in splits_data['Cards']]
    splits_scores = []
    for split_ind in range(n_splits):
      if 'Scores' in splits_data:
        scorer_output = self.split_scorer(None, None, sup_scores=splits_data['Scores'][split_ind])
      else:
        scorer_output = self.split_scorer(None, splits_data['Codes'][split_ind])

      splits_scores.append(scorer_output)
    
    picked_split_ind = self.split_picker([score[0] for score in splits_scores], 1)[0]
    output_split_cards = []
    cur_card_ind = 0
    for set_size in self.__class__.split_into:
      output_split_cards.append(tuple(splits_data['Cards'][picked_split_ind][cur_card_ind:cur_card_ind+set_size]))
      cur_card_ind += set_size

    output = self.__class__.ranked_split_info_factory(
      None, # Inds
      output_split_cards, # Cards
      [CardGroupCode(code) for code in splits_data['Codes'][picked_split_ind]], # Codes 
      splits_data['Scores'][picked_split_ind], # Scores,
      None, # SplitScore
      splits_scores[picked_split_ind][1],
      splits_scores[picked_split_ind][0],
      None,
    )

    return output, None, None
  
  def _apply_score_filter_to_generated_splits(
    self,
    generated_splits,
    n_splits_picked,
    filter_strategy,
    filter_score_buffer,
    verbose=False,
  ):
    """Use a different (quicker) scoring strategy to pre-filter splits

    Args:
        generated_splits ([type]): [description]
        n_splits_picked ([type]): [description]
        filter_strategy ([type]): [description]
        filter_score_buffer ([type]): [description]
        verbose (bool, optional): [description]. Defaults to False.

    Returns:
        [type]: [description]
    """
    filter_scores = [filter_strategy.split_scorer(
        split.Cards,
        split.Codes,
      )[0] for split in generated_splits]
    filter_boundary = nth_largest(n_splits_picked, filter_scores)

    threshold_score = filter_boundary-filter_score_buffer
    keep_split = [score > threshold_score for score in filter_scores]
    
    if verbose:
      n_removed = len(generated_splits) - sum(keep_split)
      print(f'_apply_score_filter_to_generated_splits: threshold score={threshold_score}; removed {n_removed} of {len(generated_splits)} splits.')
  
    return list(compress(generated_splits, keep_split))
  
  def _generate_splits(
    self,
    cards,
    max_elapsed_sec=None,
    verbose=True,
    output_every_n_splits=100,
  ):
    if max_elapsed_sec is None:
      max_elapsed_sec = self.pick_max_elapsed_sec
    
      
    generator = self.split_generator(cards)
    
    generated_splits = []
      
    n_splits_gen = 0
    while 1:
      next_split = next(generator, None)
      n_splits_gen += 1
      if verbose and n_splits_gen % output_every_n_splits == 0:
        print(f'Split {n_splits_gen} - Total elasped time {timer()-start}s')
      if next_split is None:
        break
      generated_splits.append(next_split)
      if max_elapsed_sec is not None and timer()-start > max_elapsed_sec:
        break
      if self.pick_max_gen_splits is not None and len(generated_splits) >= self.pick_max_gen_splits:
        break
    return generated_splits
  
  def _score_splits(
    self,
    generated_splits,
  ):
    """Utility function to score list of splits

    Args:
        generated_splits (list): List of splits (as generated by _generate_splits)

    Returns:
        list: List of tuples, one tuple for each split. First element of tuple is the
              overall strategy score, second is the supplementary score.
    """
    if type(self) == type(self.split_gen_params['FilterStrategy']):
      splits_scores = [self.split_scorer(
        split.Cards,
        split.Codes,
        sup_scores=split.GenFilterSupScores,
        split_score=split.GenFilterSplitScore
        ) for split in generated_splits]
    else:
      splits_scores = [self.split_scorer(
        split.Cards,
        split.Codes,
        ) for split in generated_splits]
    
    return splits_scores

  def pick_n_best_splits(
    self, 
    cards,
    n_best_splits,
    max_elapsed_sec=None,
    unique_code_levels=None,
    verbose=False,
    generated_splits=None,
    output_every_n_splits=100,
  ):
    
    if verbose and output_every_n_splits is None:
      output_every_n_splits = 100

    if self.split_pick_params['FilterByScore']:
      apply_score_filter = True
      
    else:
      apply_score_filter = False
    start = timer()
    if not generated_splits:
      generated_splits = self._generate_splits(cards, max_elapsed_sec, verbose, output_every_n_splits)
    
    if apply_score_filter and len(generated_splits) > n_best_splits+20:
      generated_splits = self._apply_score_filter_to_generated_splits(
        generated_splits,
        n_best_splits,
        self.split_pick_params['FilterStrategy'],
        self.split_pick_params['FilterScoreBuffer'],
        verbose,
      )
     
    splits_scores = self._score_splits(generated_splits)

    if unique_code_levels is not None and unique_code_levels > 0:
      top_n_inds = self.split_picker(
        [score[0] for score in splits_scores], 
        n_best_splits, 
        unique_code_levels, 
        [split.Codes for split in generated_splits] # Codes
      )
    else:
      top_n_inds = self.split_picker(
        [score[0] for score in splits_scores], 
        n_best_splits
      )

    best_splits = []
    generated_splits_raw_data = []
    
    for sI, generated_split in enumerate(generated_splits):
      temp_split_info = generated_split._asdict()
      temp_split_info['StratSupScores'] = splits_scores[sI][1]
      temp_split_info['StratSplitScore'] = splits_scores[sI][0]
      temp_split_info['Rank'] = None
      
      generated_splits_raw_data.append(self.__class__.ranked_split_info_factory(**temp_split_info))

      if sI in top_n_inds:
        temp_split_info['Rank'] = top_n_inds.index(sI)+1
        best_splits.append(self.__class__.ranked_split_info_factory(**temp_split_info))

    best_splits = sorted(best_splits, key=lambda x: x.Rank)
    return best_splits, generated_splits_raw_data, timer()-start

  def pick_single_split(
    self, 
    cards, 
    max_elapsed_sec=None, 
    verbose=False, 
    generated_splits=None,
    randomness=0,
  ):
    """[summary]

    Args:
        cards ([type]): [description]
        max_elapsed_sec ([type], optional): [description]. Defaults to None.
        verbose (bool, optional): [description]. Defaults to False.
        generated_splits ([type], optional): [description]. Defaults to None.
        randomness (int, optional): Value between 0 and 1. 
            Represents the mixture of randomness in choosing the split.
            Defaults to 0.

    Returns:
        [type]: [description]
    """

    # How many to pick
    # -- if: randomness=0 - pick only 1
    # -- else: pick floor(randomness*n_splits)47


    best_splits, all_splits, sec_elapsed = self.pick_n_best_splits(
      cards,
      1,
      max_elapsed_sec,
      verbose=verbose,
      generated_splits=generated_splits,
    )
    
    return best_splits[0], all_splits, sec_elapsed

  def gen_all_splits(self, cards, progress_every_n_splits=None):
    """Generate all feasible splits based on set group codes

    Args:
        cards ([type]): [description]
        verbose (bool, optional): [description]. Defaults to True.

    Returns:
        [type]: [description]
    """
    start = timer()
    
    # To generate all splits should not apply any score-based filtering or time restrictions
    generator = self._yield_systematic_split(cards)
    
    splits_generated = []
    while 1:
      next_split = next(generator, None)
      if next_split is None:
        break
      if progress_every_n_splits is not None and (len(splits_generated)+1) % progress_every_n_splits == 0:
        print(f'Split {len(splits_generated)+1} - Total elasped time {timer()-start}s')
      
      splits_generated.append(next_split)
    return splits_generated, timer()-start
  
  
  def _yield_systematic_split(
    self, 
    cards,
    filter_by_score=False,
  ):
    """Similar to _yield_unfiltered_systematic_split except for various logic to 
    use scores to filter out splits.
    
    Arguments:
        cards    

    Yields:
        [type] -- [description]
    """
    
    # Unpack parameters
    if filter_by_score:
      filter_score_buffer = self.split_gen_params['FilterScoreBuffer']
      if filter_score_buffer is None:
        filter_score_buffer = 0
      filter_strat = self.split_gen_params['FilterStrategy']

    # FIRST, find all possible final set options
    min_top_level_code = self.classifier.top_level_code_from_label('OnePair')
    final_set_options = self.classifier.find_n_card_set_codes(
      cards, 
      set_size=self.__class__.split_into[-1],
      min_code=CardGroupCode([min_top_level_code,])
    )

    accepted_splits = []
    seq_no = 1

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
        pot_score = filter_strat.split_scorer(
          None,
          [mapped_code_3_to_1, mapped_code_3_to_2, final_set_code],
        )[0]

        if pot_score < (max_score-filter_score_buffer):
          break
      
      accepted_for_this_final_set_code = []
      combs_for_this_final_set_code = []

      for final_set_option in merged_final_set_option:
        
        if self.sort_set_cards_by_group:
          final_set_inds = tuple(final_set_option[2])
        else:
          final_set_inds = tuple(sorted(final_set_option[2]))
        final_set_cards = tuple([cards[i] for i in final_set_inds])

        remaining_inds_and_cards = [(i,card) for i,card in enumerate(cards) if i not in final_set_inds]
        remaining_inds, remaining_cards = zip(*remaining_inds_and_cards)

        second_set_options = self.classifier.find_n_card_set_codes(
          remaining_cards,
          set_size=self.__class__.split_into[1],
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
          if self.sort_set_cards_by_group:
            second_set_inds = tuple(second_set_inds)
          else:
            second_set_inds = tuple(sorted(second_set_inds))
          second_set_cards = tuple([cards[i] for i in second_set_inds])
          
          first_set_cards = tuple([card for i,card in enumerate(remaining_cards) if i not in second_set_option[2]])
          
          first_set_inds = tuple([i for i in range(len(cards)) if i not in second_set_inds+final_set_inds])

          first_set = self.classifier.find_n_card_set_codes(
            first_set_cards,
            set_size=self.__class__.split_into[0],
            max_code = second_set_code,
          )
          
          if len(first_set) == 0:
            # First set code > second set code, so invalid
            continue
          else:
            first_set_code = first_set[0][0]
            
            if self.sort_set_cards_by_group:
              first_set_inds = tuple([first_set_inds[ind] for ind in first_set[0][2]])
              first_set_cards = tuple([cards[i] for i in first_set_inds])
          
          if filter_by_score:
            if max_score is not None:
              filled_second_set_code = CardGroupCode.fill_code(second_set_code.code, self.score_code_lengths[1], self.code_fill_val, trim_if_needed=True)
              mapped_code_2_to_1 = CardGroupCode(self.code_map_set_2_to_1[filled_second_set_code])
              pot_score = filter_strat.split_scorer(
                None,
                [mapped_code_2_to_1, second_set_code, final_set_code],
              )[0]
              if pot_score < max_score-(filter_score_buffer):
                break

          
            split_score, set_scores = filter_strat.split_scorer(
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
            self.__class__.ranked_split_info_factory(
              [first_set_inds, second_set_inds, final_set_inds],
              [first_set_cards, second_set_cards, final_set_cards],
              [first_set_code, second_set_code, final_set_code],
              set_scores,
              split_score,
              None,
              None,
              None,
              seq_no,
            )
          )

          seq_no += 1

      # Sort by 2nd set code then 1st set code, decsending in strength
      combs_for_this_final_set_code = sorted(combs_for_this_final_set_code, key=lambda x: (x.Codes[1], x.Codes[0]), reverse=True)

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
        elif comb.Codes[1] == accepted_for_this_final_set_code[-1].Codes[1]: # Compare second set code
          if comb.Codes[0] > accepted_for_this_final_set_code[-1].Codes[0]:
            del accepted_for_this_final_set_code[-1]
            accepted_for_this_final_set_code.append(comb)
        # If second set code is worse than latest, the only admit if first set code is an 
        # improvement - don't need to delete latest in accepted set in this case.
        else:
          if comb.Codes[0] > accepted_for_this_final_set_code[-1].Codes[0]:
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
            if split_to_check.Codes[0] <= existing_split.Codes[0] and split_to_check.Codes[1] <= existing_split.Codes[1]:
              # Reject
              to_accept=False              
              break

          # If not rejected, then accept
          if to_accept is True:
            splits_to_append.append(split_to_check)
            yield split_to_check
            
            if split_to_check.Codes[0] > max_first_set_code:
              max_first_set_code = split_to_check.Codes[0]

        accepted_splits = accepted_splits + splits_to_append
      
    return      

  ###############################################
  ### START score table related methods START ###
  ###############################################
  #@deprecated
  #def _load_single_score_table(self, scoring_method):
  #  return CardGroupCode.load_set_scoring_file(scoring_method)

  def _gen_empty_full_score_table(self, set_size, code_length, code_fill_val=-1):
    classifier = CardGroupClassifier()
    all_possible_codes = classifier.all_possible_set_codes(set_size, code_length, code_fill_val)
     
    score_table = pd.DataFrame()
    for level in range(1, code_length+1):
      score_table[f'L{level}Code'] = [code.code[level-1] for code in all_possible_codes]
      #score_table[f'CodeLevel{level}'] = [code.code[level-1] for code in all_possible_codes]
    return score_table
  
  def _add_method_scores_to_table(
    self,
    score_table,
    pool_size,
    set_size,
    join_list,
    max_code_length,
    score_column,
    score_label,
    min_score=0,
    max_score=100,
  ):
    
    #join_list = [f'L{level}Code' for level in range(1, max_code_length+1)]

    method_score_table = self._load_percentiles_from_db(pool_size, set_size, max_code_length)

    # Remove everything except for code and score columns
    method_score_table = method_score_table[join_list + [score_column]]
    
    # Rename to standard
    method_score_table.rename(columns={score_column: score_label}, inplace=True)

    # Join on code
    score_table = score_table.merge(method_score_table, on=join_list, how='left')
    
    # Fill missing
    # -> Use back fill first, then fill the rest with 0
    bfill_score = score_table[score_label].fillna(method='bfill')
    bfill_score = bfill_score.fillna(value=min_score)

    ffill_score = score_table[score_label].fillna(method='ffill')
    ffill_score = ffill_score.fillna(value=max_score)

    score_table[score_label] = (bfill_score + ffill_score)/2

    return score_table

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
  
  ###########################################
  ### END score table related methods END ###
  ###########################################
  
  @classmethod
  def _remove_similar_splits(cls, splits, unique_top_levels=3, randomise=True):
    """ Removes splits that are similar in code. Splits are deemed to be "similar"
        if the top unique_top_levels code levels across all sets are identical.
        The first unique split splits is kept and all other similar splits are discarded.
        If randomise is set to True, splits is randomised prior to filtering.

    Args:
        splits (list): List of splits
        unique_top_levels (int, optional): Used to determine similarity. Defaults to 3.
        randomise (bool, optional): Whether to shuffle splits prior to removal of similar splits. Defaults to True.

    Returns:
        list: List of splits with similar splits removed.
    """
    df_data = []

    for sI, split in enumerate(splits):
      split_fingerprint = list(split.Codes[0].get_code_fixed_length(unique_top_levels)) + list(split.Codes[1].get_code_fixed_length(unique_top_levels)) + list(split.Codes[2].get_code_fixed_length(unique_top_levels))
      df_data.append(split_fingerprint)
    #df = pd.DataFrame(df_data, columns=['Ind', 'C11','C12','C13','C21','C22','C23','C31','C32','C33'])
    df = pd.DataFrame(df_data)
    if randomise:
      df = df.sample(frac=1)
    
    df.drop_duplicates(inplace=True)
    splits_filt = [splits[sI] for sI in range(len(splits)) if sI in df.index.values]
    return splits_filt, sorted(df.index.values)
  
class ChinesePokerPctileScoreStrategyClass(ChinesePokerStrategyClass):
  
  
  weights_table = GConst.CHINESE_POKER_db_consts['percentile_strategy_weights_table']
  strategy_typeID = 1

  # Constructor 1
  def __init__(
    self,
    score_methods=None,
    score_code_lengths=None, # 3
    split_gen_filter_by_score = False,
    split_gen_filter_strategy = None,
    split_gen_filter_score_buffer = 0,
    pick_max_elapsed_sec = 120,
    pick_max_gen_splits = 5000,
    strategyID = None,
    strategy_name = None,
    sort_set_cards_by_group = False,
  ):
    super().__init__(
      'WeightedPercentiles',
      score_code_lengths,
      pick_max_elapsed_sec,
      pick_max_gen_splits,
      strategyID,
      strategy_name,
      sort_set_cards_by_group,
      split_gen_filter_by_score,
      split_gen_filter_strategy,
      split_gen_filter_score_buffer,
    )
    
    #if score_set_weights is None:
    #  score_set_weights = GConst.GEN_default_set_score_weights[self.game_type]
    #self.score_set_weights = score_set_weights


    # Example score_methods:
    # (
    #   [
    #     (5, 3, 1/3)
    #   ],
    #   [
    #     (8, 5, 1/3)
    #   ],
    #   [
    #     (11, 5, 1/3)7485
    #   ],
    # )
  
    if score_methods is None:
      score_methods = GConst.GEN_default_score_methods[self.game_type]
    self.score_methods = score_methods

    self.score_set_weights = []
    for set_methods in score_methods:
      self.score_set_weights.append(sum([method[2] for method in set_methods]))
    

    
    self.create_all_score_dicts()

    return
  
  # Constructor 2 - load from DB
  @classmethod 
  def init_from_db(
    cls, 
    strategyID,
    split_gen_filter_by_score = False,
    split_gen_filter_strategy = None,
    split_gen_filter_score_buffer = 0,
    pick_max_elapsed_sec = 120,
    pick_max_gen_splits = 5000,
    sort_set_cards_by_group = False,
  ):
    strategy_dict = cls.load_strategy_from_db(strategyID)
    
    return cls(
      strategy_dict['score_methods'],
      strategy_dict['score_code_lengths'],
      split_gen_filter_by_score,
      split_gen_filter_strategy,
      split_gen_filter_score_buffer,
      pick_max_elapsed_sec,
      pick_max_gen_splits,
      strategyID = strategyID,
      strategy_name = strategy_dict['strategy_name'],
      sort_set_cards_by_group = sort_set_cards_by_group,
    )
  #  suits = [card.suit for card in cards]
  #  numbers = [card.number for card in cards]
  #  self.__init__(suits, numbers)
  #  return
  
  
  ###########################
  ### START Score Functions #
  ###########################

  def split_scorer(self, split_cards, split_codes, sup_scores=None, split_score=None):
    # split_cards not used in this function
    
    if sup_scores is not None and split_score is not None:
      pass
    elif sup_scores is not None and split_score is None:
      n_splits = len(self.__class__.split_into)
      split_score = sum([self.score_set_weights[sI]*sup_scores[sI] for sI in range(n_splits)])
    else:
      split_score, sup_scores = self._split_codes_weighted_score(
        split_codes,
        self.score_set_weights,
        self.score_dicts,
        self.score_code_lengths,
        self.code_fill_val,
      )

    return split_score, sup_scores

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

    n_sets = len(self.__class__.split_into)

    set_scores = [split_codes[sI].calc_code_score_from_dict(score_dicts[sI], code_lengths[sI], code_fill_val) for sI in range(n_sets)]
    weighted_score = sum([set_weights[sI]*set_scores[sI] for sI in range(n_sets)])

    return weighted_score, set_scores
    
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
     where MethodWeight is the weight across all sets 
     (i.e. doesn't have to sum to one within set).
    """

    full_score_table = self._gen_empty_full_score_table(set_size, max_code_length)
    full_score_table['WeightedScore'] = 0
    
    join_list = [f'L{level}Code' for level in range(1, max_code_length+1)]
    
    weights = [method[2] for method in score_methods]
    weight_sum = sum(weights)
    weights = [weight/weight_sum for weight in weights]
     
    score_column = self.__class__.default_score_column
    
    for mI, method in enumerate(score_methods):
      
      full_score_table = self._add_method_scores_to_table(
        full_score_table,
        method[0],
        method[1],
        join_list,
        max_code_length,
        score_column,
        f'Score{mI+1}',
        min_score,
        max_score,        
      )

    # Calculate weighted score
    
    for mI in range(len(score_methods)):
      full_score_table['WeightedScore'] += weights[mI] * full_score_table[f'Score{mI+1}']

    # Convert to dictionary   
    keys = full_score_table[join_list].itertuples(index=False, name=None)
    vals = full_score_table['WeightedScore']

    score_dict = dict(zip(keys, vals))

    return score_dict

  
  ########################################
  ### START DB related functions START ###
  ########################################
  
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

class ChinesePokerModelSetToGameScoreStrategyClass(ChinesePokerStrategyClass):
  """

  
      
  """

  def __init__(
    self,
    score_methods,
    score_code_lengths=None,
    base_score_model=None,
    bonus_score_model=None,
    base_bonus_weights=None,
    pick_max_elapsed_sec=None,
    pick_max_gen_splits=None,
    strategyID=None,
    strategy_name=None,
    sort_set_cards_by_group=False,
    split_gen_filter_by_score=False,
    split_gen_filter_strategy=None,
    split_gen_filter_score_buffer=0,
    split_pick_filter_by_score=False,
    split_pick_filter_strategy=None,
    split_pick_filter_score_buffer=20,
  ):
    
    super().__init__(
      'SetToGameScoreModel',
      score_code_lengths,
      pick_max_elapsed_sec,
      pick_max_gen_splits,
      strategyID,
      strategy_name,
      sort_set_cards_by_group,
      split_gen_filter_by_score,
      split_gen_filter_strategy,
      split_gen_filter_score_buffer,
      split_pick_filter_by_score,
      split_pick_filter_strategy,
      split_pick_filter_score_buffer,
    )

    #if score_methods is None:
    #  score_methods = GConst.GEN_default_score_methods[self.game_type]
    self.score_methods = score_methods
    
    self.create_all_score_dicts()
  
    self.base_score_model = base_score_model
    self.bonus_score_model = bonus_score_model
    
    if base_bonus_weights is None:
      base_bonus_weights = GConst.CHINESE_POKER_default_base_bonus_score_weights
    self.base_bonus_weights = base_bonus_weights
    
    return

  @classmethod
  def load_strategy_from_file(
    cls,
    strat_filepath,
    base_bonus_weights=None,
    pick_max_elapsed_sec=None,
    pick_max_gen_splits=None,
    strategyID=None,
    strategy_name=None,
    sort_set_cards_by_group=False,
    split_gen_filter_by_score=False,
    split_gen_filter_strategy=None,
    split_gen_filter_score_buffer=0,
    split_pick_filter_by_score=False,
    split_pick_filter_strategy=None,
    split_pick_filter_score_buffer=20, # 20
  ):
    with open(strat_filepath, "rb") as f:
      model_info = pickle.load(f)
    
    if 'ScoreCodeLengths' in model_info:
      score_code_lengths = model_info['ScoreCodeLengths']
    else:
      score_code_lengths = None
    
    if strategyID is None and 'StrategyID' in model_info:
      strategyID = model_info['StrategyID']

    return cls(
      model_info['ScoreMethods'],
      score_code_lengths,
      model_info['BaseModel'],
      model_info['BonusModel'],
      base_bonus_weights,
      pick_max_elapsed_sec,
      pick_max_gen_splits,
      strategyID,
      strategy_name,
      sort_set_cards_by_group,
      split_gen_filter_by_score,
      split_gen_filter_strategy,
      split_gen_filter_score_buffer,
      split_pick_filter_by_score,
      split_pick_filter_strategy,
      split_pick_filter_score_buffer
    )
  
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

  # Dictionary with keys of group code and values that are list of unweighted raw 
  # code scores of the group code using the set score_methods.
  def _create_score_dict(
    self,
    score_methods,
    set_size=5, 
    max_code_length=3,
    min_score=0,
    max_score=100,      
  ):

    full_score_table = self._gen_empty_full_score_table(set_size, max_code_length)
    
    join_list = [f'L{level}Code' for level in range(1, max_code_length+1)]
    
    score_column = self.__class__.default_score_column
    
    score_col_prefix = 'Score'
    for mI, method in enumerate(score_methods):
      
      full_score_table = self._add_method_scores_to_table(
        full_score_table,
        method[0],
        method[1],
        join_list,
        max_code_length,
        score_column,
        f'{score_col_prefix}{mI+1}',
        min_score,
        max_score,
      )

    # Convert to dictionary
    val_col_list = [f'{score_col_prefix}{mI+1}' for mI in range(len(score_methods))]
    keys = full_score_table[join_list].itertuples(index=False, name=None)
    vals = full_score_table[val_col_list].itertuples(index=False, name=None)
    
    score_dict = dict(zip(keys, vals))

    return score_dict
  
  def _convert_codes_into_percentiles(self, split_codes):
    
    all_percentiles = []
    for sI in range(len(self.__class__.split_into)):
      all_percentiles += list(
        self.score_dicts[sI][split_codes[sI].get_code_fixed_length(
          self.score_code_lengths[sI],
          self.__class__.code_fill_val
        )]
      )
    
    all_percentiles = np.array(all_percentiles).reshape(1,-1) # Force 2D array
    return all_percentiles

  def split_scorer(self, split_cards, split_codes, sup_scores=None, split_score=None):
    """VC: return standard error?

    Args:
        split_cards ([type]): [description]
        split_codes ([type]): [description]
        set_scores ([type], optional): [description]. Defaults to None.
        split_score ([type], optional): [description]. Defaults to None.

    Returns:
        [type]: [description]
    """

    if sup_scores is not None and split_score is not None:
      pass
    else:
      # Convert codes into list of percentiles
      percentiles = self._convert_codes_into_percentiles(split_codes)

      # Run through base and bonus models
      base_score = self.base_score_model.predict(percentiles)[0]
      bonus_score = self.bonus_score_model.predict(percentiles)[0]
      
      weight_sum = sum(self.base_bonus_weights)
      weights = [self.base_bonus_weights[0]/weight_sum*2, self.base_bonus_weights[1]/weight_sum*2] 

      split_score = weights[0] * base_score + weights[1] * bonus_score
      sup_scores = (base_score, bonus_score)
      
    return split_score, sup_scores


  def gen_processed_data_for_fitting(self, fit_data):
    for setI in range(3):
      set_scores = [self.score_dicts[setI][CardGroupCode(set_code).code] for set_code in fit_data[f'Set{setI+1}Code']]
      
      n_scores = len(set_scores[0])

      for sI in range(n_scores):
        fit_data[f'Set{setI+1}Score{sI+1}'] = [score[sI] for score in set_scores]

    return fit_data
    
  def com_pick_single_split(
    self,
    cards=None,
    generated_splits=None,
    difficulty=100, # Between 0 and 100
  ):
    if not generated_splits:
      generated_splits = self._generate_splits(cards, None, False, None)
    difficulty = int(difficulty)
    if difficulty == 100:
      picked_split = self.pick_single_split(cards, generated_splits=generated_splits)[0]
      pick_info = {
        'MaxPossibleScore': picked_split.StratSplitScore,
        'SplitScore': picked_split.StratSplitScore,
        'DifficultyThreshold': 0,
        'NoOrigSplits': len(generated_splits),
        'NoFiltSplits': None,
        'PickedOrigInd': picked_split.SeqNo-1,
        'PickedFiltInd': None,
        'BestSplitOrigInd': picked_split.SeqNo-1,
      }
      best_split = picked_split
    else:
      score_thresholds = GConst.CHINESE_POKER_strategy_constants[self.strategyID]['ScoreThresholdsByComDifficulty']
      print(score_thresholds)
      print(difficulty)
      difficulties = [item[0] for item in score_thresholds]
      print(difficulties)
      difficulty_ind = difficulties.index(difficulty)
      score_threshold = score_thresholds[difficulty_ind][1]
      print(score_threshold)
      score_threshold = float(score_threshold)

    
      
      n_orig_splits = len(generated_splits)
      generated_splits, orig_split_inds = self.__class__._remove_similar_splits(generated_splits)
      
      #if apply_score_filter and len(generated_splits) > n_best_splits+20:
      #  generated_splits = self._apply_score_filter_to_generated_splits(
      #    generated_splits,
      #    n_best_splits,
      #    self.split_pick_params['FilterStrategy'],
      #    self.split_pick_params['FilterScoreBuffer'],
      #  )
      #    verbose,
      
      splits_scores = self._score_splits(generated_splits)
      strat_scores = [score[0] for score in splits_scores]

      max_strat_score_ind = strat_scores.index(max(strat_scores))
      max_strat_score = strat_scores[max_strat_score_ind]
      
      diff_from_max = list(enumerate([max_strat_score - score for score in strat_scores]))
      #diff_from_max = sorted(diff_from_max, key=lambda x: x[1])
      filtered_inds = [item[0] for item in diff_from_max if item[1] <= score_threshold]
      
      chosen_ind = random.choice(filtered_inds)
      
      picked_split = generated_splits[chosen_ind]
      picked_orig_ind = orig_split_inds[chosen_ind]
      
      picked_split = picked_split._replace(
        StratSplitScore=splits_scores[chosen_ind][0],
        StratSupScores=splits_scores[chosen_ind][1]
      )
      
      best_split = generated_splits[max_strat_score_ind]
      best_split_orig_ind = orig_split_inds[max_strat_score_ind]
      
      best_split = best_split._replace(
        StratSplitScore=splits_scores[max_strat_score_ind][0],
        StratSupScores=splits_scores[max_strat_score_ind][1]
      )
      
      #best_split = self.pick_single_split(cards, generated_splits=generated_splits)
      pick_info = {
        'MaxPossibleScore': max_strat_score,
        'SplitScore': splits_scores[chosen_ind][0],
        'DifficultyThreshold': score_threshold,
        'NoOrigSplits': n_orig_splits,
        'NoFiltSplits': len(generated_splits),
        'PickedOrigInd': picked_orig_ind,
        'PickedFiltInd': chosen_ind,
        'BestSplitOrigInd': best_split_orig_ind,
      }
    return picked_split, best_split, pick_info