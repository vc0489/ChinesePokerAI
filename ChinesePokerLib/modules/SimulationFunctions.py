from timeit import default_timer as timer
import numpy as np
from functools import namedtuple
from datetime import datetime
import pickle
import os
import random
from itertools import permutations
import pandas as pd

from ChinesePokerLib.classes.GameClass import ChinesePokerGameClass
from ChinesePokerLib.classes.DeckClass import DeckClass
from ChinesePokerLib.classes.DataClass import DataClass
from ChinesePokerLib.classes.CardClass import CardClass
from ChinesePokerLib.classes.StrategyClass import ChinesePokerPctileScoreStrategyClass
from ChinesePokerLib.classes.CardGroupClass import CardGroupCode

from ChinesePokerLib.modules.UtilityFunctions import flattened_list

import ChinesePokerLib.vars.GameConstants as GameC
import ChinesePokerLib.vars.GlobalConstants as GlobC

from sklearn.model_selection import RandomizedSearchCV
from sklearn.metrics import make_scorer
from sklearn.metrics import mean_squared_error

config_factory = namedtuple(
  'ModelConfig',
  [
    'ModelName',
    'ModelConstructor',
    'FixedHyperParams',
    'FactorList',
    'HyperParamOptMethod',
    'HyperParamOptObj',
  ]
)

#####################################
### START metrics functions START ###
#####################################
mse_scorer = make_scorer(mean_squared_error, greater_is_better=False)

#################################
### END metrics functions END ###
#################################


def gen_code_combs_set(strategy=None, score_round_fac=1):
  """Generate code combs across sets, with optional filtering
  

  Args:
      strategy ([type]): [description]
      round_fac (int, optional): [description]. Defaults to 1.

  Returns:
      [type]: [description]
  """
  
  if strategy is None:
    strategy = ChinesePokerPctileScoreStrategyClass()

  combs = []
  existing_scores = [[], [], []]
  #prev_scores = (None, None, None)
  
  for code_set1, score_set1 in strategy.score_dicts[0].items():
    print(score_set1)
    if round(score_set1/score_round_fac) in existing_scores[0]:
      continue
    univ_score1 = CardGroupCode.get_universal_score(code_set1)

    existing_scores[1] = []
    for code_set2, score_set2 in strategy.score_dicts[1].items():
      if (round(score_set2/score_round_fac) in existing_scores[1]) or (CardGroupCode(code_set2) < CardGroupCode(code_set1)):
        continue
      univ_score2 = CardGroupCode.get_universal_score(code_set2)

      existing_scores[2] = []
      for code_set3, score_set3 in strategy.score_dicts[2].items():
        if (round(score_set3/score_round_fac) in existing_scores[2]) or (CardGroupCode(code_set3) < CardGroupCode(code_set2)):
          continue
        univ_score3 = CardGroupCode.get_universal_score(code_set3)

        combs.append(
          (
            code_set1, 
            code_set2, 
            code_set3, 
            score_set1, 
            score_set2, 
            score_set3, 
            univ_score1,
            univ_score2,
            univ_score3,
          )
        )
        existing_scores[2].append(round(score_set3/score_round_fac))
      
      existing_scores[1].append(round(score_set2/score_round_fac))
    existing_scores[0].append(round(score_set1/score_round_fac))
  return combs

"""
@deprecated
def gen_all_possible_strategy_score_combs(strategy, round_fac=1):
  combs = []
  existing_scores = [[], [], []]
  #prev_scores = (None, None, None)
  
  for code_set1, score_set1 in strategy.score_dicts[0].items():
    print(score_set1)
    if round(score_set1/round_fac) in existing_scores[0]:
      continue
    
    existing_scores[1] = []
    for code_set2, score_set2 in strategy.score_dicts[1].items():
      if (round(score_set2/round_fac) in existing_scores[1]) or (CardGroupCode(code_set2) < CardGroupCode(code_set1)):
        continue
      
      
      existing_scores[2] = []
      for code_set3, score_set3 in strategy.score_dicts[2].items():
        if (round(score_set3/round_fac) in existing_scores[2]) or (CardGroupCode(code_set3) < CardGroupCode(code_set2)):
          continue
        
        combs.append((code_set1, code_set2, code_set3, score_set1, score_set2, score_set3))
        existing_scores[2].append(round(score_set3/round_fac))
        #prev_scores = (round(score_set1/round_fac,1), round(score_set2/round_fac,1), round(score_set3/round_fac,1))
      
      existing_scores[1].append(round(score_set2/round_fac))
    existing_scores[0].append(round(score_set1/round_fac))
  return combs
"""

def gen_best_split_data(
  n_hands,
  strategy=None,
  output_progress_every=None,
  split_gen_strategy=None,
):
  
  if strategy is None:
    strategy = ChinesePokerPctileScoreStrategyClass(split_gen_filter_by_score = True)
  start = timer()
  deck = DeckClass()
  
  split_codes = []
  split_scores = []
  split_sup_scores = []
  split_cards = []

  split_gen_filter_scores = []
  split_gen_filter_sup_scores = []
  for hI in range(n_hands):
    cards = deck.deal_cards()[0]
    if split_gen_strategy is not None:
      splits_pool = split_gen_strategy.gen_all_splits(cards)[0]
    else:
      splits_pool = None
    best_split, _, _ = strategy.pick_single_split(cards, generated_splits=splits_pool)
    
    split_codes.append(best_split.Codes)
    split_sup_scores.append(best_split.StratSupScores)
    split_scores.append(best_split.StratSplitScore)

    split_gen_filter_sup_scores.append(best_split.GenFilterSupScores)
    split_gen_filter_scores.append(best_split.GenFilterSplitScore)

    temp_cards = flattened_list(best_split.Cards)
    split_cards.append([str(card) for card in temp_cards])

    if output_progress_every is not None and (hI+1)%output_progress_every == 0:
      min_elapsed = (timer()-start)/60
      print (f'Processed {hI+1} of {n_hands} hands. {min_elapsed} min elasped.')
  data = {
    'Codes':split_codes,
    'Scores':split_scores,
    'SupScores':split_sup_scores,
    'Cards':split_cards,
    'GenFilterScores':split_gen_filter_scores,
    'GenFilterSupScores':split_gen_filter_sup_scores,
  }
  return data

def repeated_games_with_hand(
  cards, 
  n_games, 
  strategies=None, 
  test_n_best_splits=None, 
  verbose=True,
  unique_code_levels=None,
):
  start = timer()
  #data_obj = DataClass()
  deck = DeckClass()

  if strategies is None:
    strategy = ChinesePokerPctileScoreStrategyClass(split_gen_filter_by_score = True)
    strategies = [strategy for _ in range(4)]
  elif not isinstance(strategies, list):
    strategies = [strategies for _ in range(4)]

  if test_n_best_splits is None:
    test_n_best_splits = 1
  

  cards = deck.deal_custom_hand(cards)
  #if isinstance(cards, str):
  #  cards = deck._convert_list_of_cards_from_user(cards)
  #  cards = [CardClass.init_from_str(card) for card in cards]
  #elif isinstance(cards[0], str):
  #  cards = [CardClass.init_from_str(card) for card in cards]
  
  if verbose:
    print(f'Cards: {cards}')
  
  best_splits_P0, _, _ = strategies[0].pick_n_best_splits(cards, test_n_best_splits, unique_code_levels=unique_code_levels)
  best_splits_P0_dict = {
    'Cards': [flattened_list(split[1]) for split in best_splits_P0],
    'Scores': [split[5] for split in best_splits_P0],
    'Codes': [[set_code.code for set_code in split[2]] for split in best_splits_P0],
  }

  
  
  game_obj = ChinesePokerGameClass(strategies=strategies)
  for gI in range(n_games):
    

    hands = deck.deal_partially_custom_cards(cards)
    
    #other_player_best_splits = []
    game_splits_data = {}
    for pI in range(1, 4):
      player_best_split, _, _ = strategies[pI].pick_single_split(hands[pI])
      
      player_split_dict = {
        'Cards': [flattened_list(player_best_split[1])],
        'Scores': [player_best_split[5]],
        'Codes': [[set_code.code for set_code in player_best_split[2]]],
      }
      
      game_splits_data[f'P{pI}'] = player_split_dict

    for splitI in range(len(best_splits_P0)):
      split_P0_dict = {
        'Cards': [best_splits_P0_dict['Cards'][splitI]],
        'Scores': [best_splits_P0_dict['Scores'][splitI]],
        'Codes': [best_splits_P0_dict['Codes'][splitI]],
      }    
      game_splits_data['P0'] = split_P0_dict
      game_obj.play_game(splits_data=game_splits_data)
    
    if verbose:
      min_elapsed = (timer()-start)/60
      print(f'-->Completed game {gI+1}/{n_games}. Time elapsed={min_elapsed} min.')
  return game_obj.history, best_splits_P0_dict

def extract_key_info_from_history(game_history):
  """Get ranks, score details, total score
  """
  seat_labels = GameC.GEN_seat_labels['CHINESE-POKER']
  split_ranks = {seat_label:[] for seat_label in seat_labels}
  game_score_details = {}
  for seat_label in seat_labels:
    game_score_details[seat_label] = {opp_seat_label:[] for opp_seat_label in seat_labels if opp_seat_label != seat_label}
  game_tot_scores = {seat_label:[] for seat_label in seat_labels}
  split_sup_scores = {seat_label:[] for seat_label in seat_labels}
  split_scores = {seat_label:[] for seat_label in seat_labels}
  split_codes = {seat_label:[] for seat_label in seat_labels}
  base_game_scores = {seat_label:[] for seat_label in seat_labels}
  bonus_game_scores = {seat_label:[] for seat_label in seat_labels}
  for single_game_info in game_history:
    for seat_label in seat_labels:
      player_game_info = single_game_info['Players'][seat_label]
      split_ranks[seat_label].append(player_game_info['SplitRanks'])
      
      for opp_seat_label in game_score_details[seat_label].keys():
        game_score_details[seat_label][opp_seat_label].append(player_game_info['GameScoreDetails'][opp_seat_label])
      game_tot_scores[seat_label].append(player_game_info['TotGameScore'])
      
      split_sup_scores[seat_label].append(player_game_info['SplitCodeSupScores'])
      split_scores[seat_label].append(player_game_info['SplitCodeScore'])
      split_codes[seat_label].append(player_game_info['SplitCodes'])
      base_game_scores[seat_label].append(player_game_info['BaseGameScore'])
      bonus_game_scores[seat_label].append(player_game_info['TotGameScore']-player_game_info['BaseGameScore'])
  key_info = {
    'SplitRanks': split_ranks,
    'TotGameScores': game_tot_scores,
    'GameScoreDetails':game_score_details,
    'SplitCodes': split_codes,
    'SplitCodeScores':split_scores,
    'SplitCodeSupScores':split_sup_scores,
    'BaseGameScores': base_game_scores,
    'BonusGameScores':bonus_game_scores,
  }
  return key_info

#####################################
### START Fitting functions START ###
#####################################
def fit_cv_models(
  fit_data, 
  kfold_obj, 
  model_configs, 
  target, 
  metric_func,
  folds_to_fit=None,
  save_model_obj=True,
  save_hyperparam_opt_det=True,
  save_folder=None,
):
  all_metrics = np.full((len(model_configs),2), np.nan) # IS, OOS
  all_oos_pred = np.full((fit_data.shape[0], len(model_configs)), np.nan)
  
  n_folds = kfold_obj.n_splits
  fold_metrics = np.full((len(model_configs),n_folds,2), np.nan)
  #all_models = []
  all_times = []
  
  # Convert to numpy array if necessary
  if not isinstance(target, np.ndarray):
    target = target.values

  start = timer()
  if (save_model_obj or save_hyperparam_opt_obj) and save_folder is None:
    date_str = datetime.today().strftime('%Y%m%d')
    save_folder = GlobC.MODELDIR / f'CVModels_{date_str}' 

  if not os.path.exists(save_folder):
    os.makedirs(save_folder)

  for mI, model_config in enumerate(model_configs):
    #temp_models = []
    temp_times = []
    print(f'Model {mI+1} of {len(model_configs)} - {model_config.ModelName}')
    is_pred = np.full((fit_data.shape[0],10), np.nan)
    oos_pred = np.full((fit_data.shape[0],), np.nan)
    
    for fI, (train_inds, test_inds) in enumerate(kfold_obj.split(fit_data)):
      fit_start = timer()
      if folds_to_fit is not None and (fI+1) not in folds_to_fit:
        print(f'Skipping fold {fI+1}.')
        continue
      # Fit hyperparams + model
      if save_hyperparam_opt_det:
        hyperparam_opt_obj_save_path = save_folder / f'{model_config.ModelName}_HyperparamOptDetails_Fold{fI+1}.pickle'
      else:
        hyperparam_opt_obj_save_path = None

      if save_model_obj:
        model_obj_save_path = save_folder / f'{model_config.ModelName}_Fold{fI+1}.pickle'
      else:
        model_obj_save_path = None
      model = _fit_single_model(
        fit_data.iloc[train_inds], 
        model_config, 
        target[train_inds],
        model_obj_save_path,
        hyperparam_opt_obj_save_path
      )
          
      oos_pred[test_inds] = model.predict(fit_data[model_config.FactorList].iloc[test_inds])
      is_pred[train_inds, fI] = model.predict(fit_data[model_config.FactorList].iloc[train_inds])
      
      min_elapsed = (timer()-fit_start)/60
      cum_min_elapsed = (timer()-start)/60
      print(f'Fold {fI+1} of {n_folds} complete. Min elapsed = {cum_min_elapsed}')
      temp_times.append(min_elapsed*60)
      #temp_models.append(model)
      fold_metrics[mI,fI,0] = metric_func(target[train_inds], is_pred[train_inds, fI])
      fold_metrics[mI,fI,1] = metric_func(target[test_inds], oos_pred[test_inds])
    is_pred_avg = np.nanmean(is_pred, axis=1)
    is_metric = metric_func(target, is_pred_avg)
    oos_metric = metric_func(target, oos_pred)
    all_metrics[mI,0] = is_metric
    all_metrics[mI,1] = oos_metric
    all_oos_pred[:,mI] = oos_pred
    all_times.append(temp_times)
  
  output = {
    'FullMetrics': all_metrics,
    'FoldMetrics': fold_metrics,
    'OOSPredictions': all_oos_pred,
    'SecElapsed': all_times,
  }
  return output

def fit_full_models(
  fit_data,
  model_configs,
  target,
  save_model_obj=True,
  save_hyperparam_opt_det=True,
  rel_save_folder=None, # Relative to MODELDIR
):
  start = timer()
  if not isinstance(model_configs, (list, tuple)):
    single_model = True
    model_configs = [model_configs, ]
  all_models = []
  all_models_rel_save_files = []
  if (save_model_obj or save_hyperparam_opt_det) and save_folder is None:
    date_str = datetime.today().strftime('%Y%m%d')
    save_folder = GlobC.MODELDIR / f'FullModels_{date_str}' 

  if not os.path.exists(save_folder):
    os.makedirs(save_folder)
  
  
  for mI, model_config in enumerate(model_configs):
    print(f'Model {mI+1} of {len(model_configs)} - {model_config.ModelName}')

    if save_hyperparam_opt_det:
      hyperparam_opt_obj_save_path = save_folder / f'{model_config.ModelName}_HyperparamOptDetails_Full.pickle'
    else:
      hyperparam_opt_obj_save_path = None

    if save_model_obj:
      rel_model_obj_save_path = save_folder / f'{model_config.ModelName}_Full.pickle'
      model_obj_save_path = GlobC.MODELDIR / rel_model_obj_save_path
    else:
      model_obj_save_path = None
  
    model = _fit_single_model(
      fit_data,
      model_config,
      target,
      model_obj_save_path,
      hyperparam_opt_obj_save_path,
    )
    
    all_models.append(model)
    all_models_rel_save_files.append(rel_model_obj_save_path)
    cum_min_elapsed = (timer()-start)/60
    print(f'Fit complete. Min elapsed = {cum_min_elapsed}')
  if single_model:
    return all_models[0], all_models_rel_save_files[0]
  else:
    return all_models, all_models_rel_save_files



def _fit_single_model(
  fit_data, 
  model_config, 
  target, 
  model_obj_save_path=None, 
  hyperparm_opt_det_save_path=None
):
  if model_config.FixedHyperParams:
    model = model_config.ModelConstructor(**model_config.FixedHyperParams)
  else:
    model = model_config.ModelConstructor()
  
  if model_config.HyperParamOptMethod in ('random_grid', 'hyperopt'):
    model_config.HyperParamOptObj.fit(fit_data[model_config.FactorList], target)
    for param, value in model_config.HyperParamOptObj.best_params_.items():
      setattr(model, param, value)

    if hyperparm_opt_det_save_path is not None:
      model_config.HyperParamOptObj.save_hyperparam_opt_details(hyperparm_opt_det_save_path)
  elif model_config.HyperParamOptMethod is not None:
    print(f'HyperParamOptMethod {model_config.HyperParamOptMethod} not recognised, no hyper param optimisation.')
    # Assign best params to model obj
  
  model.fit(fit_data[model_config.FactorList], target)
  
  if model_obj_save_path is not None:
    with open(model_obj_save_path, 'wb') as f:
      pickle.dump(model, f)
  return model

#################################
### END Fitting functions END ###
#################################



#################################################
### START Strategy comparison functions START ###
#################################################

def compare_strategies_same_hand(strategy_list, n_hands, n_best_splits=1, include_split_gen=False, split_gen_strategy=None):
  all_best_splits = []
  n_gen_splits_data = []
  time_data = []

  compare_timer_start = timer()

  for hI in range(n_hands):
    print(f'Hand {hI+1} of {n_hands}:')
    hand_best_splits = []
    hand_n_gen_splits = []
    hand_times = []
    deck = DeckClass()
    cards = deck.deal_cards()[0]
    
    

    if include_split_gen is False:
      if split_gen_strategy is None:
        split_gen_strategy = ChinesePokerPctileScoreStrategyClass(
          pick_max_gen_splits=None,
          pick_max_elapsed_sec=None
        )
      
      start = timer()
      all_splits = split_gen_strategy.gen_all_splits(cards, True)[0]
      hand_n_gen_splits = len(all_splits)
      hand_times.append(timer()-start)
      
      min_elapsed = (timer()-compare_timer_start)/60
      print(f'-->{len(all_splits)} feasible hands generated. Cum. {min_elapsed} min elapsed.')

      for sI, strategy in enumerate(strategy_list):
        strat_best_splits, _, sec_elapsed = strategy.pick_n_best_splits(
          None, 
          n_best_splits, 
          max_elapsed_sec=None, 
          unique_code_levels=None, 
          verbose=False, 
          generated_splits=all_splits,
        )
        hand_best_splits.append(strat_best_splits)
        hand_times.append(sec_elapsed)
        
        min_elapsed = (timer()-compare_timer_start)/60
        print(f'-->Picked best split using strategy {sI+1}. Cum. {min_elapsed} min elapsed.')
    else:
      for sI, strategy in enumerate(strategy_list):
        strat_best_splits, raw_splits_data, sec_elapsed = strategy.pick_n_best_splits(
          cards,
          n_best_splits,
        )
        hand_n_gen_splits.append(len(raw_splits_data))
        hand_times.append(sec_elapsed)
        
        min_elapsed = (timer()-compare_timer_start)/60
        print(f'-->Generated splits and picked best split using strategy {sI+1}. Cum. {min_elapsed} min elapsed.')
    all_best_splits.append(hand_best_splits)
    n_gen_splits_data.append(hand_n_gen_splits)
    time_data.append(hand_times)
    
  return all_best_splits, n_gen_splits_data, time_data


def _compare_codes(code_set1, code_set2):
  n_codes = len(code_set1)
  comp_res = []
  for cI in range(n_codes):
    if code_set1[cI] > code_set2[cI]:
      comp_res.append(1)
    elif code_set1[cI] < code_set2[cI]:
      comp_res.append(-1)
    else:
      comp_res.append(0)
  return comp_res

def compare_strategies_h2h_diff_hands(
  strats, # List of 2-4 strats
  n_games,
  hands_from_db=True,
  split_gen_strat=None
):
  all_best_splits = []
  n_gen_splits_data = []
  time_data = []
  #all_comp_res = []
  compare_timer_start = timer()
  
  n_strats = len(strats)

  if hands_from_db:
    max_game_id = DataClass.max_game_id_in_splits_table()
    game_ids = random.sample(range(1,max_game_id+1), n_games)
    data_obj = DataClass()
  else:
    deck = DeckClass()
  
  data_dict = {
    'GameSeqNo':[],
    'GameID':[],
    'Strat':[],
    'OppStrat':[],
    'Hand':[],
    'OppHand':[],
    'BaseScore':[],
    'BonusScore':[],
    'TotScore':[],
    'CompSet1':[],
    'CompSet2':[],
    'CompSet3':[],
  }
  for gI in range(n_games):
    print(f'Game {gI+1} of {n_games}:')
    hand_best_splits = []
    hand_n_gen_splits = []
    hand_times = []
     
    # Load or gen all splits 
    if hands_from_db is True:
      game_id = game_ids[gI]
      _, all_splits = next(data_obj.yield_splits_data_from_db(game_id, game_id))
      #all_splits = all_splits[:n_strats]
      cards = [None for _ in range(4)]
    else:
      cards = deck.deal_cards() #[0:n_strats]
      
      if split_gen_strat is not None:
        all_splits = []
        
        #for sI in range(n_strats):
        for hI, hand in enumerate(cards):
          all_splits.append(split_gen_strat.gen_all_splits(hand)[0])
          hand_n_gen_splits.append(len(all_splits[-1]))
          min_elapsed = (timer()-compare_timer_start)/60
          print(f'-->Generated {len(all_splits[-1])} feasible splits on hand {hI+1}. Cum. {min_elapsed} min elapsed.')
      else:
        all_splits = None
          
    
    game_strat_best_splits = []
    for sI, strat in enumerate(strats):
      strat_best_splits = []
      for hI in range(4):
        if hands_from_db or split_gen_strat is not None:
          strat_best_split, _, sec_elapsed = strat.pick_single_split(None, generated_splits=all_splits[hI])
          min_elapsed = (timer()-compare_timer_start)/60
          print(f'-->Picked best split on hand {hI+1} using strat {sI+1}. Cum. {min_elapsed} min elapsed.')
        
        else:
          strat_best_split, raw_splits_data, sec_elapsed = strat.pick_single_split(cards[hI])
          hand_n_gen_splits.append(len(raw_splits_data))
          min_elapsed = (timer()-compare_timer_start)/60
          print(f'-->Generated {len(raw_splits_data)} splits and picked best using strat {sI+1} on hand {hI+1}. Cum. {min_elapsed} min elapsed.')
        
        hand_times.append(sec_elapsed)
        strat_best_splits.append(strat_best_split)
      game_strat_best_splits.append(strat_best_splits)

    h2h_matchups = list(permutations(range(4), 2))
    
    for s1I in range(n_strats):
      for s2I in range(s1I+1, n_strats):
        for matchup in h2h_matchups:
          s1_split = game_strat_best_splits[s1I][matchup[0]]
          s2_split = game_strat_best_splits[s2I][matchup[1]]
          comp_res = _compare_codes(s1_split.Codes,s2_split.Codes)
          
          base_score = sum(comp_res)
          
          if abs(base_score) == 3:
            tot_score = base_score*2
            bonus_score = base_score
          else:
            tot_score = base_score
            bonus_score = 0
          data_dict['GameSeqNo'].append(gI+1)
          data_dict['GameSeqNo'].append(gI+1)
          
          if hands_from_db:
            data_dict['GameID'].append(game_id)
            data_dict['GameID'].append(game_id)
          else:
            data_dict['GameID'].append(np.nan)
            data_dict['GameID'].append(np.nan)

          data_dict['Strat'].append(s1I+1)
          data_dict['Strat'].append(s2I+1)

          data_dict['OppStrat'].append(s2I+1)
          data_dict['OppStrat'].append(s1I+1)

          data_dict['Hand'].append(matchup[0]+1)
          data_dict['Hand'].append(matchup[1]+1)

          data_dict['OppHand'].append(matchup[1]+1)
          data_dict['OppHand'].append(matchup[0]+1)

          data_dict['BaseScore'].append(base_score)
          data_dict['BaseScore'].append(-base_score)

          data_dict['BonusScore'].append(bonus_score)
          data_dict['BonusScore'].append(-bonus_score)

          data_dict['TotScore'].append(tot_score)
          data_dict['TotScore'].append(-tot_score)
          
          for sI in range(3):
            data_dict[f'CompSet{sI+1}'].append(comp_res[sI])
            data_dict[f'CompSet{sI+1}'].append(-comp_res[sI])

    """
    strat_perms = list(permutations(range(n_strats)))
    base_scores = np.full((n_strats,n_strats,len(strat_perms)), np.nan)
    tot_scores = base_scores.copy()
    comp_res_det = np.full((n_strats,n_strats,len(strat_perms),3), np.nan)
    for permI, strat_perm in enumerate(strat_perms):
      # Pick best split 
      for hI, stratI in enumerate(strat_perm):          
        if hands_from_db or split_gen_strat is not None:
          strat_best_split, _, sec_elapsed = strats[stratI].pick_single_split(cards[hI], generated_splits=all_splits[hI])
          min_elapsed = (timer()-compare_timer_start)/60
          print(f'-->Picked best split on hand {hI+1} using strat {stratI+1}. Cum. {min_elapsed} min elapsed.')
        
        else:
          strat_best_split, raw_splits_data, sec_elapsed = strats[stratI].pick_single_split(cards[hI])
          hand_n_gen_splits.append(len(raw_splits_data))
          min_elapsed = (timer()-compare_timer_start)/60
          print(f'-->Generated {len(raw_splits_data)} splits and picked best using strat {stratI+1} on hand {hI+1}. Cum. {min_elapsed} min elapsed.')
        
        hand_times.append(sec_elapsed)
        hand_best_splits.append(strat_best_split)
      
      # Compare best splits
      for s1I in range(n_strats):
        for s2I in range(s1I+1, n_strats):
          comp_res = _compare_codes(hand_best_splits[s1I].Codes,hand_best_splits[s2I].Codes)
          
          base_score = sum(comp_res)
          
          if abs(base_score) == 3:
            tot_score = base_score*2
          else:
            tot_score = base_score
          base_scores[strat_perm[s1I], strat_perm[s2I], permI] = base_score
          base_scores[strat_perm[s2I], strat_perm[s1I], permI] = -base_score
          tot_scores[strat_perm[s1I], strat_perm[s2I], permI] = tot_score
          tot_scores[strat_perm[s2I], strat_perm[s1I], permI] = -tot_score
          comp_res_det[strat_perm[s1I], strat_perm[s2I], permI, :] = comp_res
          comp_res_det[strat_perm[s2I], strat_perm[s1I], permI, :] = -comp_res_det[strat_perm[s1I], strat_perm[s2I], permI, :]

    
    hand_comp_res = (
      tot_scores,
      base_scores,
      comp_res_det,
    )
    
    """
    comp_data = pd.DataFrame(data_dict)
    #all_comp_res.append(hand_comp_res)
    all_best_splits.append(hand_best_splits)
    n_gen_splits_data.append(hand_n_gen_splits)
    time_data.append(hand_times)
    
    #if tot_score1 + tot_score2 != 0:
    #  print('***Difference in outcome detected***')
    #  print(f'S1H1vS2H2: {hand_best_splits[0].Codes} vs. {hand_best_splits[1].Codes}')
    #  print(f'S1H2vS2H1: {hand_best_splits[2].Codes} vs. {hand_best_splits[3].Codes}')
    #  print(hand_comp_res)
      
  return comp_data, all_best_splits, n_gen_splits_data, time_data


#############################################
### END Strategy comparison functions END ###
#############################################