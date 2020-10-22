"""Constants relating to games

VC TODO: use pathlib instead of os.path for paths
"""
import os.path as op
import glob
import re
from datetime import datetime
import pathlib
import numpy as np

import ChinesePokerLib.modules.DBFunctions as DBF


ChinesePokerKey = 'CHINESE-POKER'
GEN_seat_labels = {
  ChinesePokerKey: ('S','W','N','E')
}

GEN_default_starting_dealer = {
  ChinesePokerKey: 'S'
}

GEN_hands_split_into = {
  ChinesePokerKey: (3,5,5)
}

GEN_hands_split_ascending_required = {
  ChinesePokerKey: True
}



# Separate list for each set
# PoolSize, SetSize, Weight
GEN_default_score_methods = {
  ChinesePokerKey: (
    [
      (5, 3, 1/3),
    ],
    [
      (8, 5, 1/3),
    ],
    [
      (11, 5, 1/3),
    ],
  )
}

GEN_default_score_code_lengths = {
  ChinesePokerKey: (3, 3, 3)
}

###################################
### START Will be defunct START ###
###################################
# Default methods for scoring sets
old_GEN_default_score_methods = {
  ChinesePokerKey: (
    ['Best3CardSetOutOf5'], 
    ['Best5CardSetOutOf8'], 
    ['Best5CardSetOutOf11'],
  )
}

# Score weights of sets
GEN_default_set_score_weights = {
  ChinesePokerKey: (1/3, 1/3, 1/3)
}

# Score weights of methods within each set
GEN_default_method_score_weights = {
  ChinesePokerKey: ([1], [1], [1])
}

GEN_default_score_columns = {
  ChinesePokerKey: (['MaxPctile'], ['MaxPctile'], ['MaxPctile'])
}

GEN_default_score_column_transforms = {
  ChinesePokerKey: ([lambda x: 100-x], [lambda x: 100-x], [lambda x: 100-x])
}

CHINESE_POKER_default_base_bonus_score_weights = (0.5, 0.5)

CHINESE_POKER_default_code_fill_value = -1

###############################
### END Will be defunct END ###
###############################

"""
DATADIR = op.join(
  '/Users',
  'vhc08',
  'Work',
  'ChinesePoker',
  'Data'
)

data_files_for_set_scoring = {
  'Best5CardPrctile': op.join(DATADIR, 'best5CardSetData.csv'),
  'GreedyFromSet1Prctile': op.join(DATADIR, 'best5CardSet1And2Data_20200430.csv'),
}

def _find_latest_score_file(n_cards, set_size, ret_max_date=False):
  base_filename = f'best{set_size}CardSetOf{n_cards}CardHand_'
  files = glob.glob(op.join(DATADIR, base_filename + '*.csv'))
  
  p = re.compile('.*?Hand_([0-9]*?)\.csv')
  dates = [p.match(filename).group(1) for filename in files if p.match(filename)]
  datetimes = [datetime.strptime(date_str, '%Y%m%d') for date_str in dates]
  max_date = max(datetimes)

  latest_file = base_filename + datetime.strftime(max_date, '%Y%m%d') + '.csv'
  
  latest_file = op.join(DATADIR, latest_file)
  
  if ret_max_date:
    return latest_file, max_date
  else:
    return latest_file


#
set_size = 5

for n_cards in range(5,14):
  data_files_for_set_scoring[f'Best{set_size}CardSetOutOf{n_cards}'] = \
    _find_latest_score_file(n_cards, set_size)

set_size = 3

for n_cards in range(3,9):
  data_files_for_set_scoring[f'Best{set_size}CardSetOutOf{n_cards}'] = \
    _find_latest_score_file(n_cards, set_size)
"""

########################################
### START DB related constants START ###
########################################

CHINESE_POKER_db_consts = {
  'instance':'chinesepoker',
  'dev_db':'DevDB',
  'dev_user':'devUser',
  'dev_password':'devPass',
  'dealt_hands_table':'random_dealt_hands',
  'splits_table':'feasible_hand_splits',
  'split_codes_table':'split_set_codes',
  'split_scores_table':'split_scores',
  'split_strategies_table':'split_strategies',
  'split_strategy_types_table':'split_strategy_types',
  'percentile_strategy_weights_table':'percentile_strategy_weights',  
  'code_percentiles_table':'code_percentiles',
}


####################################
### END DB related constants END ###
####################################

##############################################
### START Strategy related constants START ###
##############################################
# Key = strategyID
CHINESE_POKER_strategy_constants = {
  3: {
    'ScoreThresholdsByComDifficulty': [# (Difficulty, Game score threshold)
      [  0, 12.000],
      [  5, 3.5203],
      [ 10, 2.9522],
      [ 15, 2.6029],
      [ 20, 2.3213],
      [ 25, 2.0811],
      [ 30, 1.8887],
      [ 35, 1.7213],
      [ 40, 1.5711],
      [ 45, 1.4249],
      [ 50, 1.2861],
      [ 55, 1.1543],
      [ 60, 1.0146],
      [ 65, 0.8698],
      [ 70, 0.7276],
      [ 75, 0.5687],
      [ 80, 0.4043],
      [ 85, 0.2313],
      [ 90, 0.1044],
      [ 95, 0.0261],
      [100, 0.0000],
    ]
  }
}

##########################################
### END Strategy related constants END ###
##########################################
