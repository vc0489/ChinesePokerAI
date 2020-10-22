import os
from pathlib import Path
import base64
from io import BytesIO
import random
import ast
from itertools import combinations
from deprecated import deprecated
from datetime import datetime

from wtforms.validators import ValidationError

from ChinesePokerLib.classes.CardClass import CardClass
from ChinesePokerLib.classes.DeckClass import DeckClass
from ChinesePokerLib.classes.StrategyClass import ChinesePokerPctileScoreStrategyClass, ChinesePokerModelSetToGameScoreStrategyClass
from ChinesePokerLib.classes.CardGroupClass import CardGroupClassifier, CardGroupCode

import ChinesePokerLib.modules.DataFunctions as DF
import ChinesePokerLib.modules.DBFunctions as DBF
from ChinesePokerLib.modules.ImageFunctions import concat_images_from_file_list

import ChinesePokerLib.vars.CardConstants as CC
import ChinesePokerLib.vars.GlobalConstants as GConst

import ChinesePokerLib.modules.DBFunctions as DBF

def random_hand():

  deck = DeckClass()
  cards = [str(card) for card in deck.deal_cards()[0]]
  return cards

def get_suggestions(cards, n_best_splits, unique_code_levels, strategyID=1, ret_card_strs=True):
  deck = DeckClass()
  cards = deck.deal_custom_hand(cards)

  strategy = ChinesePokerPctileScoreStrategyClass.init_from_db(
    strategyID,
    split_gen_filter_by_score = True,
    sort_set_cards_by_group = True,
  )
    
  best_splits,_,_ = strategy.pick_n_best_splits(cards, n_best_splits, unique_code_levels=unique_code_levels)


  # Insert processing - sort cards, add desciprions of groups, scores
  
  #for split in best_splits:
  #  # inds = split[0]
  #  cards = split[1]
  #  codes = split[2]
  #  scores = split[3]
  #  weighted_score = split[4]
  split_code_scores = [split.StratSplitScore for split in best_splits]
  
  if ret_card_strs is True:
    return [[[str(c) for c in s] for s in split.Cards] for split in best_splits], split_code_scores
  else:
    return best_splits, split_code_scores

def submitted_cards_validator(form, to_validate):

  try:
    cards = [card.strip() for card in to_validate.data.upper().split(',')]
  except:
    raise ValidationError('Failed to split using comma as separator.')

  if len(cards) > 13:
    raise ValidationError('Too many cards provided. 13 cards required.')
  elif len(cards) < 13:
    raise ValidationError('Too few cards provided. 13 cards required.')
  for card in cards:
    if len(card) < 2 or len(card) > 3:
      raise ValidationError(f'Invalid card {card}')
    is_valid = CardClass.is_valid_suit_and_number(card[0], card[1:])
    if not is_valid:
      raise ValidationError(f'Invalid card {card}')


def construct_card_img_filename_list(cards):
  filename_list = []
  for card in cards:
    filename = CC.STANDARD_full_number_name_map[card[1:]] + CC.STANDARD_full_suit_name_map[card[0]]
    filename_list.append(filename)
  
  return filename_list

def _get_card_strings(cards):
  if ~isinstance(cards[0], str):
    cards = [str(card) for card in cards]
  return cards

def construct_concat_cards_img(cards, app_root_path=None):
  cards = _get_card_strings(cards)

  filename_list = []
  for card in cards:
    card_filename = CC.STANDARD_full_number_name_map[card[1:]] + CC.STANDARD_full_suit_name_map[card[0]] + 'Small.png'
    
    if app_root_path is not None:
      full_filename = Path(app_root_path) / 'static' / 'CardImages' / card_filename
    else:
      full_filename = Path('app') / 'static' / 'CardImages' / card_filename
    # ! This doesn't work: full_filename = Path('/static') / 'CardImages' / card_filename 
    filename_list.append(full_filename)
  concat_img = concat_images_from_file_list(filename_list)

  buffer = BytesIO()
  concat_img.save(buffer, "PNG")
  buffer.seek(0)
  img_str = base64.b64encode(buffer.getvalue()).decode('ascii')
  return img_str


def construct_selected_cards_img_filename_list(cards, inc_non_sel=True):
  if inc_non_sel is True:
    return construct_selected_cards_img_filename_list_inc_non_sel(cards)
  else:
    return construct_selected_cards_img_filename_list_only_sel(cards)
  return

def construct_selected_cards_img_filename_list_only_sel(cards):
  cards = _get_card_strings(cards)
  filename_list = []
  
  for card in cards:
    full_number = CC.STANDARD_full_number_name_map[card[1:]]
    full_suit = CC.STANDARD_full_suit_name_map[card[0]]
    
    filename_list.append(
      (
        f'{full_number}{full_suit}Small',
        f'{full_number} of {full_suit}',
      )
    )
  return filename_list

def construct_selected_cards_img_filename_list_inc_non_sel(cards):
  """Construct a set of card image filename lists.
  One list for each suit.
  Non-selected cards are represented by the back image. 

  Args:
      cards ([type]): [description]

  Returns:
      [type]: [description]
  """
  cards = _get_card_strings(cards)
  filename_list = []
  for suit in CC.STANDARD_full_suit_name_map.keys():
    filename_list.append([])
    full_suit = CC.STANDARD_full_suit_name_map[suit]
    for number in CC.STANDARD_full_number_name_map.keys():
      full_number = CC.STANDARD_full_number_name_map[number]
      if suit+number in cards:
        filename_list[-1].append(
          (
            f'{full_number}{full_suit}Small',
            f'{full_number} of {full_suit}',
          )
        )
      else:
        filename_list[-1].append(
          (
            f'{full_suit}Back',
            'Not selected',
          )
        )
  return filename_list

def construct_random_valid_split_img_filename_lists(cards, sets_card_inds):
  cards = _get_card_strings(cards)
  filename_list = []
  print(f'cards: {cards}')
  print(f'sets_card_inds: {sets_card_inds}')
  for set_inds in sets_card_inds:
    set_filename_list = []
    for ind in set_inds:
      card = cards[ind]
      full_number = CC.STANDARD_full_number_name_map[card[1:]]
      full_suit = CC.STANDARD_full_suit_name_map[card[0]]
    
      set_filename_list.append(
        (
          f'{full_number}{full_suit}Small',
          f'{full_number} of {full_suit}',
          f'{ind}'
        )
      )
    filename_list.append(set_filename_list)
  return filename_list
  

###################################
### START suggest() utils START ###
###################################
def construct_all_cards_img_info():
  info = []
  for suit in CC.STANDARD_full_suit_name_map.keys():
    full_suit = CC.STANDARD_full_suit_name_map[suit]
    for number in CC.STANDARD_full_number_name_map.keys():
      full_number = CC.STANDARD_full_number_name_map[number]
      info.append(
        (
          f'{full_number}{full_suit}Small',
          f'{full_number} of {full_suit}',
          f'{suit}{number}',
        )
      )
  return info


def parse_suggest_form_data(form_data, card_key_prefix):
  """[summary]
  Args:
      form_data ([type]): [description]
      card_key_prefix ([type]): [description]
  Returns:
      [type]: [description]
  """
  # @param high - hello
  # * high
  # ! hello
  # ? hello
  # TODO hello 
  # // hello
  
  #['cardimg-C10', 'cardimg-D8', 'cardimg-H7', 'cardimg-HJ', 'dropdown-suggestions', 'dropdown-variability', 'submit-cards']
  n_suggestions = int(form_data['dropdown-suggestions'])
  unique_top_code_levels = int(form_data['dropdown-variability'])

  cards = []
  for key in form_data.keys():
    if card_key_prefix in key:
      card = key[len(card_key_prefix):]
      cards.append(card)
  processed_form_data = {
    'Cards':cards,
    'nSuggestions':n_suggestions,
    'UniqueTopCodeLevels': unique_top_code_levels,
  }
  return processed_form_data

###############################
### END suggest() utils END ###
###############################


##############################
### START Game utils START ###
##############################
def random_game():
  game_info, game_hands = DF.random_game_setup_from_db()
  
  return game_info, game_hands

def get_random_valid_split(gameID, seatID):
  """[summary]

  Args:
      gameID (int): [description]
      seatID (int): Between 1 and 4
  """

  # First check number of valid splits in DB
  set_card_inds, split_seq_no  = DF.fetch_random_feasible_split_for_game_and_seat(gameID, seatID, True)
  
  return set_card_inds, split_seq_no

def card_ids_to_sets(orig_cards, id_order, card_id_prefix):
  prefix_len = len(card_id_prefix)
  ind_order = [int(id[prefix_len:]) for id in id_order]
  
  print(f'orig_cards: {orig_cards}')
  print(f'ind_order: {ind_order}')
  cur_card_order = [orig_cards[ind] for ind in ind_order]
  

  card_sets = [
    cur_card_order[:3],
    cur_card_order[3:8],
    cur_card_order[8:]
  ]
  return card_sets


def card_inds_to_cards(cards, inds):
  return [cards[ind] for ind in inds]

def card_ids_to_cards(orig_cards, ids, card_id_prefix):
  prefix_len = len(card_id_prefix)
  inds = [int(id[prefix_len:]) for id in ids]

  return card_inds_to_cards(orig_cards, inds)

def classify_group(cards=None, group_code=None):
  """[summary]

  Args:
      cards (list): List of card strings
  """
  
  classifier = CardGroupClassifier()
  
  if group_code is not None and cards is None:
    group_sorted_inds = None
    if isinstance(group_code, str):
      group_code = ast.literal_eval(group_code)
    if isinstance(group_code, tuple):
      group_code = CardGroupCode(group_code)
  else:
    group_code, group_sorted_inds = classifier.classify_card_group(cards)
  group_desc = classifier.get_code_description(group_code)
  
  return group_code, group_desc, group_sorted_inds

def check_valid_split(set1_code, set2_code, set3_code):
  """[summary]

  Args:
      set1_code (str or tuple): [description]
      set2_code (str or tuple): [description]
      set3_code (str or tuple): [description]

  Returns:
      [type]: [description]
  """
  if isinstance(set1_code, str):
    set1_code = ast.literal_eval(set1_code)
    set1_code = CardGroupCode(set1_code)
  if isinstance(set2_code, str):
    set2_code = ast.literal_eval(set2_code)
    set2_code = CardGroupCode(set2_code)
  if isinstance(set3_code, str):
    set3_code = ast.literal_eval(set3_code)
    set3_code = CardGroupCode(set3_code)
  
  if not set1_code.code or not set2_code.code or not set3_code.code:
    return False

  print(set1_code)
  print(set2_code)
  print(set3_code)
  
  if (set1_code > set2_code) | (set2_code > set3_code):
    return False
  else:
    return True


def get_computer_split(
  game_id,
  com_seat_id,
  strategy=None,
  cards=None,
  difficulty=100,
):
  if strategy is None:
    strategy = ChinesePokerModelSetToGameScoreStrategyClass.load_strategy_from_file(
  GConst.MODELDIR / 'FullGameScoreModelGradBoostHyperoptR1.pickle')

  splits_data = DF.get_splits_data_for_single_game_and_seat_from_db(game_id, com_seat_id, cards)
  com_split = strategy.com_pick_single_split(None, generated_splits=splits_data, difficulty=difficulty)[0]
  
  return com_split

@deprecated
def get_computer_best_split(game_id, com_seat_id, strategy=None, cards=None):
  """Return best split for specific game+seat with given strategy.
     This is equivalent to get_computer_split with difficulty 100.

  Args:
      game_id ([type]): [description]
      com_seat_id (int): Between 1-4
  """

  # Load strategy
  if strategy is None:
    strategy = ChinesePokerModelSetToGameScoreStrategyClass.load_strategy_from_file(
  GConst.MODELDIR / 'FullGameScoreModelGradBoostHyperoptR1.pickle')

  splits_data = DF.get_splits_data_for_single_game_and_seat_from_db(game_id, com_seat_id, cards)
  best_split = strategy.pick_single_split(None, generated_splits=splits_data)[0]
  # Load splits, codes
  #com_seat_id = user_seat_id
  #for cI in range(3):
  #  com_seat_id = (com_seat_id % 4) + 1
  #  splits_data = DF.get_splits_data_for_single_game_and_seat_from_db(game_id, com_seat_id, cards)
       
  #  best_split = strategy.pick_single_split(None, generated_splits=splits_data)[0]
    
  return best_split

def play_hand(user_codes, com1_codes, com2_codes, com3_codes):
  
  codes = [user_codes, com1_codes, com2_codes, com3_codes]
  for cI, code_split in enumerate(codes):
    if isinstance(code_split[0], str):
      code_split = [ast.literal_eval(code) for code in code_split]
    
    codes[cI] = [CardGroupCode(code) for code in code_split]
  
  print(f'codes: {codes}')
  compare_combs = combinations(range(4), 2)
  comp_res = [[[] for _ in range(4)] for _ in range(4)]
  game_scores = [[-999 for _ in range(4)] for _ in range(4)]
  tot_game_scores = [0 for _ in range(4)]

  for i1,i2 in compare_combs:
    temp_comp_res = [None, None, None]
    for sI in range(3):
      if codes[i1][sI] > codes[i2][sI]:
        temp_comp_res[sI] = 1
      elif codes[i1][sI] < codes[i2][sI]:
        temp_comp_res[sI] = -1
      elif codes[i1][sI] == codes[i2][sI]:
        temp_comp_res[sI] = 0
    comp_res[i1][i2] = temp_comp_res
    comp_res[i2][i1] = [-score for score in temp_comp_res]
    
    temp_game_score = sum(temp_comp_res)
    if abs(temp_game_score) == 3:
      temp_game_score *= 2
    
    game_scores[i1][i2] = temp_game_score
    game_scores[i2][i1] = -temp_game_score
    
    tot_game_scores[i1] += temp_game_score
    tot_game_scores[i2] -= temp_game_score
  
  #print(comp_res)
  #print(game_scores)

  return comp_res, game_scores, tot_game_scores

def get_com_seat_id(user_seat_id, com_id):
  com_seat_id = ((user_seat_id + com_id - 1) % 4) + 1
  return com_seat_id
##########################
### END Game utils END ###
##########################


CPT_game_table = 'CPT_games'
CPT_rounds_table = 'CPT_rounds'
##############################
### START DB related START ###
##############################
def create_CPT_game_row(clientIP, com_difficulties):
  query = f"INSERT INTO {CPT_game_table} (ClientIP, Com1Difficulty, Com2Difficulty, Com3Difficulty, StartTimeUTC) VALUES ('%s', %s, %s, %s, '%s')"
  cur_datetime = datetime.utcnow().strftime(GConst.SQL_DATETIME_FORMAT)
  query = query % (clientIP, com_difficulties[0], com_difficulties[1], com_difficulties[2], cur_datetime)
  print(query)
  _, app_game_ID = DBF.insert_query(query, None, False, True)
  return app_game_ID

def create_CPT_round_row(app_game_ID, app_round_no, hand_game_ID, hand_seat_ID):
  query = f"INSERT INTO {CPT_rounds_table} (AppGameID, RoundNo, HandGameID, HandSeatID, StartTimeUTC) VALUES (%s, %s, %s, %s, '%s')"
  cur_datetime = datetime.utcnow().strftime(GConst.SQL_DATETIME_FORMAT)
  query = query % (app_game_ID, app_round_no, hand_game_ID, hand_seat_ID, cur_datetime)
  #print(query)
  _, app_round_ID = DBF.insert_query(query, None, False, True)
  return app_round_ID

def update_CPT_round_row_with_com_split(app_round_ID, com_id, seq_no):
  #split_inds_str = DF._convert_card_inds_to_set_inds_str(split_inds)
  
  query = f"UPDATE {CPT_rounds_table} SET Com{com_id}SplitSeqNo = {seq_no} WHERE RoundID = {app_round_ID}"
  #print(query)
  _ = DBF.insert_query(query, None, False, False)
  return

def update_CPT_round_row_with_player_split_as_com_100(app_round_ID, seq_no):
  query = f"UPDATE {CPT_rounds_table} SET PlayerSplitSeqNoCom100 = {seq_no} WHERE RoundID = {app_round_ID}"
  #print(query)
  _ = DBF.insert_query(query, None, False, False)
  return

def update_CPT_round_row_with_player_split(app_round_ID, split_inds):
  split_str = DF._convert_card_inds_to_set_inds_str(split_inds)
  query = f"UPDATE {CPT_rounds_table} SET PlayerSplitInds = {split_str} WHERE RoundID = {app_round_ID}"
  #print(query)
  _ = DBF.insert_query(query, None, False, False)
  return

def update_CPT_round_row_with_game_scores(app_round_ID, game_scores, player_score_com_100):
  cur_datetime = datetime.utcnow().strftime(GConst.SQL_DATETIME_FORMAT)
  query = f"UPDATE {CPT_rounds_table} SET PlayerScore = {game_scores[0]}, Com1Score = {game_scores[1]}, Com2Score = {game_scores[2]}, Com3Score = {game_scores[3]}, PlayerScoreCom100 = {player_score_com_100}, EndTimeUTC = '{cur_datetime}' WHERE RoundID = {app_round_ID}"
  _ = DBF.insert_query(query, None, False, False)
  return

def end_of_game_CPT_game_row_update(app_game_ID, n_rounds, tot_score, tot_CPT_score):
  cur_datetime = datetime.utcnow().strftime(GConst.SQL_DATETIME_FORMAT)
  query = f"UPDATE {CPT_game_table} SET NoRounds={n_rounds}, TotScore={tot_score}, TotCptScore={tot_CPT_score}, EndTimeUTC='{cur_datetime}' WHERE AppGameID={app_game_ID}"
  _ = DBF.insert_query(query, None, False, False)
  return


def update_CPT_submit_score(app_game_ID, name, email=None):
  query = f"UPDATE {CPT_game_table} SET Name='{name}', Email='{email}', InLeaderboard=1 WHERE AppGameID={app_game_ID}"
  _ = DBF.insert_query(query, None, False, False)
  return

def gen_leaderboard(show_top_n_scores=10, cur_app_game_ID=None):
  query = f"SELECT AppGameID, Name, Com1Difficulty+Com2Difficulty+Com3Difficulty AS TotComDifficulty, NoRounds, TotScore, TotCptScore, CAST(EndTimeUTC AS DATE) AS GameDate FROM {CPT_game_table} WHERE InLeaderboard=1 ORDER BY (TotScore-TotCptScore)/NoRounds DESC, (Com1Difficulty+Com2Difficulty+Com3Difficulty) DESC, NoRounds DESC, EndTimeUTC ASC LIMIT {show_top_n_scores}"
  output, _ = DBF.select_query(query)

  processed_output = []

  for row_i, row in enumerate(output):
    is_user = 0
    if row[0] == cur_app_game_ID:
      is_user = 1
    print(row)
    row_data = [
      row_i+1, # Rank
      row[1], # Name
      row[2], # TotCompDifficulty
      row[3], # NoRounds
      row[4], # TotScore
      row[5], # TotCPTScore
      row[6].strftime('%Y/%m/%d'), # GameDate
      is_user, # IsUser
    ]
    processed_output.append(row_data)
  
  if cur_app_game_ID:
    if sum([row[-1] for row in processed_output]) == 0: 
      query = f"SELECT AppGameID, Name, Com1Difficulty+Com2Difficulty+Com3Difficulty AS TotComDifficulty, NoRounds, TotScore, TotCptScore, CAST(EndTimeUTC AS DATE) AS GameDate FROM {CPT_game_table} WHERE AppGameID={cur_app_game_ID} AND InLeaderboard=1"
      output, _ = DBF.select_query(query)
      if output:
        row_data = [
          None, # Rank
          output[0][1], # Name
          output[0][2], # TotCompDifficulty
          output[0][3], # NoRounds
          output[0][4], # TotScore
          output[0][5], # TotCPTScore
          output[0][6].strftime('%Y/%m/%d'), # GameDate
          1, # IsUser
        ]
        processed_output.append(row_data)
      #query = f"SELECT AppGameID, Name, Com1Difficulty+Com2Difficulty+Com3Difficulty AS TotComDifficulty, NoRounds, TotScore, TotCptScore, CAST(EndTimeUTC AS DATE) AS GameDate FROM {CPT_game_table} WHERE InLeaderboard=1 WHERE AppGameID={cur_app_game_ID}"
    
  # Fetch the rank of the cur_app_game_ID
  # If cur_app_game_ID not in the output, then run a separate query

  
  return processed_output

##########################
### END DB related END ###
##########################

