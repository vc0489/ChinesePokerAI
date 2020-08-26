import os
from pathlib import Path
import base64
from io import BytesIO
import random

from wtforms.validators import ValidationError

from ChinesePokerLib.classes.CardClass import CardClass
from ChinesePokerLib.classes.DeckClass import DeckClass
from ChinesePokerLib.classes.StrategyClass import ChinesePokerPctileScoreStrategyClass

import ChinesePokerLib.modules.DataFunctions as DF
from ChinesePokerLib.modules.ImageFunctions import concat_images_from_file_list

import ChinesePokerLib.vars.CardConstants as CC

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

def construct_concat_cards_img(cards, app_root_path=None):
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

def construct_selected_cards_img_filename_list(cards):
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


##########################
### END Game utils END ###
##########################