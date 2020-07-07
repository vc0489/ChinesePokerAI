from ChinesePokerLib.classes.DeckClass import DeckClass
from ChinesePokerLib.classes.PlayerClass import ComputerChinesePokerPlayerClass
from ChinesePokerLib.classes.HandClass import ChinesePokerHandClass
from ChinesePokerLib.classes.CardGroupClass import CardGroupClassifier, CardGroupCode
from ChinesePokerLib.classes.StrategyClass import ChinesePokerPctileScoreStrategyClass

import ChinesePokerLib.vars.GameConstants as GConst
from ChinesePokerLib.classes.ExceptionClasses import InvalidGameModeError

from itertools import combinations
import scipy.stats as ss 
import numpy as np
from timeit import default_timer as timer

class ChinesePokerGameHistoryClass:
  def __init__(self):
    self.history = []

    return

  def add_round(self,
    history_data
  ):
    self.history.append(history_data)

    return

  # Various aggregation functions

  # Set level
  # Game, Seat, Set, Code, Score, Rank

  # Player level
  # Game, Seat, Code1, Code2, Code3, Score1, Score2, Score3, Rank1, Rank2, Rank3, WeightedScore, GamePoints
  """
  def add_round_to_history(self, game_obj):
    game_data = {}
    
    for seat_label in game_obj.player_seat_labels:
      game_data[seat_label] = {}
      game_data[seat_label]['PlayerID'] = game_obj.players[seat_label].id
      
      for set_no in range(1,4):
        game_data[seat_label][f'Set{set_no}'] = {
          'Cards': game_obj.players[seat_label].cur_hand.split_cards[set_no-1],
          'Code': game_obj.players[seat_label].cur_hand.split_codes[set_no-1],
          'CodeScore': game_obj.players[seat_label].cur_hand.split_scores[set_no-1],
          'Rank': None,
        }
      
      game_data[seat_label]['WeightedCodeScore'] = game_obj.players[seat_label].cur_hand.weighted_score

      game_data[seat_label]['GameScore'] = {
        'Tot': game_obj.cur_scores[seat_label]
      }

      for opp_seat_label in game_obj.player_seat_labels:
        if opp_seat_label == seat_label:
          continue
        game_data[seat_label]['GameScore'][opp_seat_label] = game_obj.cur_score_details[seat_label][opp_seat_label]

    return      
  """
      
    
    
  
class ChinesePokerGameClass:

  # Class attributes
  game_type = GConst.ChinesePokerKey
  player_seat_labels = GConst.GEN_seat_labels[game_type] # ('S', 'W', 'N', 'E')
  starting_dealer = GConst.GEN_default_starting_dealer[game_type] # 'S'
  hands_split_into = GConst.GEN_hands_split_into[game_type] # (3,5,5)
  splits_force_ascending = GConst.GEN_hands_split_ascending_required[game_type] # True

  hand_class = ChinesePokerHandClass

  def __init__(
    self, 
    game_mode='AUTO',
    players=None,
    strategies=None,
    random_seat=False,
    history=None,
  ):
    self.deck = DeckClass()
    self.n_players = len(ChinesePokerGameClass.player_seat_labels) # 4
    self.cur_dealer_ind = ChinesePokerGameClass.player_seat_labels.index(ChinesePokerGameClass.starting_dealer)
    self.cur_play_seq = None

    self.games_played = 0
    #self.games_history = ChinesePokerGameHistoryClass()

    self.game_mode = game_mode
    self.players = {}
    if strategies is None:
      strategies = [ChinesePokerPctileScoreStrategyClass() for pI in range(self.n_players)]
    elif not isinstance(strategies, (list, tuple)):
      strategies = [strategies for pI in range(self.n_players)]
    

    self.reset_cur_game_info()
    
    if game_mode == 'AUTO':
      if not random_seat:
        for i,label in enumerate(self.player_seat_labels):
          if players is None or players[i] is None:
            self.players[label] = ComputerChinesePokerPlayerClass(strategy=strategies[i])
          else:
            self.players[label] = players[i]
      else:    
        print('Need to implement random_seating')
    else:
      raise InvalidGameModeError(f'game_mode {game_mode} not valid.')

    if history is None:
      history = ChinesePokerGameHistoryClass()
    
    self.history = history

    return

  def reset_cur_game_info(self):
    self.cur_scores = None
    self.cur_score_details = None
    self.cur_split_ranks = None
    self.cur_round_time = None
    
    return

  def _create_computer_player(self):
    
    return

  def play_game(self, cards=None, deal_cards_from_dealer=False, splits_data=None):
    """Play single game of ChinesePoker
    """
    self._pregame_processes()

    start = timer()
    if self.game_mode == 'AUTO':
      self.play_auto_game(cards, deal_cards_from_dealer, splits_data)
    self.cur_round_time = timer()-start

    self._postgame_processes()
      
    return

  def play_auto_game(
    self,
    cards=None,
    deal_cards_from_dealer=False,
    splits_data=None, # Container of 4 dicts
  ):
    """Play single auto-game of Chinese Poker
    """
    if splits_data is not None:
      self._dist_splits_data(splits_data)
    elif splits_data is None:  
      if cards is not None:
        self._deal_specific_cards(cards, deal_cards_from_dealer)
      elif cards is None:
        _ = self._deal_random_cards()
    
    # Choose hands
    for player_ind in self.cur_play_seq:
      seat_label = self.player_seat_labels[player_ind]
      self.players[seat_label].play_hand()

    # Compare splits
    comparison_results, self.cur_split_ranks = self._compare_splits()
    self.cur_scores, self.cur_score_details = self._score_comparison(comparison_results)
    return 
  
  def _score_comparison(self, comparison_results):
    tot_scores = {}
    det_scores = {}
    for seat in self.player_seat_labels:
      player_score = 0
      det_scores[seat] = {}
      for opp_seat in self.player_seat_labels:
        if opp_seat != seat:
          comp_score = sum(comparison_results[seat][opp_seat])
          if abs(comp_score) == len(comparison_results[seat][opp_seat]):
            comp_score = 2*comp_score
          
          player_score += comp_score
          det_scores[seat][opp_seat] = comp_score
      tot_scores[seat] = player_score

    return tot_scores, det_scores

  def _compare_splits(self):
    seat_pairs = list(combinations(self.player_seat_labels,2))
    #classifier = CardGroupClassifier()
    
    comparison_results = {}
    for seat in self.player_seat_labels:
      comparison_results[seat] = {}

    all_ranks = {label:[] for label in self.player_seat_labels}

    # Do it by ranks instead 
    for set_i in range(len(self.hands_split_into)):
      set_codes = [self.players[label].split_info['Codes'][set_i] for label in self.player_seat_labels]
      ranks = ss.rankdata(set_codes)
      for sI, label in enumerate(self.player_seat_labels):
        all_ranks[label].append(ranks[sI])
    
    for pair in seat_pairs:
      pair_comparison_results = self._compare_pair_of_ranks(
        all_ranks[pair[0]],
        all_ranks[pair[1]],
      )

      #pair_comparison_results = self._compare_pair_of_splits(
      #  self.players[pair[0]],
      #  self.players[pair[1]],
      #)
      #  classifier,

      comparison_results[pair[0]][pair[1]] = pair_comparison_results
      comparison_results[pair[1]][pair[0]] = [-result for result in pair_comparison_results]
    return comparison_results, all_ranks

#        first_set = classifier._find_n_card_set_codes(
#          first_set_cards,
#          set_size=self.split_into[0],
#          max_code = second_set_code,
#        )
#
#        if len(first_set) == 0:
#          continue
#        else:
#          first_set_code = first_set[0][0]  

  def _get_all_codes(self):
    return

  def _compare_pair_of_ranks(self, ranks1, ranks2):
    n_splits = len(self.hands_split_into)
    comparison_results = []

    for sI in range(n_splits):
      if ranks1[sI] > ranks2[sI]:
        comparison_results.append(1)
      elif ranks1[sI] < ranks2[sI]:
        comparison_results.append(-1)
      else:
        comparison_results.append(0)
    return comparison_results

  def _compare_pair_of_splits(self, player1, player2):
    if classifier is None:
      classifier = CardGroupClassifier()
    
    n_splits = len(self.hands_split_into)

    comparison_results = []
    
    for sI in range(n_splits):
      p1_code = player1.cur_hand.split_codes[sI]
      p2_code = player2.cur_hand.split_codes[sI]
      #p1_inds = player1.cur_hand.split_inds[sI]
      #p1_cards = [player1.cur_hand.cards[i] for i in p1_inds]
      #p2_inds = player2.cur_hand.split_inds[sI]
      #p2_cards = [player2.cur_hand.cards[i] for i in p2_inds]
      #p1_code = classifier._find_n_card_set_codes(
      #  p1_cards, 
      #  self.hands_split_into[sI]
      #)[0][0]
      #p2_code = classifier._find_n_card_set_codes(
      #  p2_cards,
      #  self.hands_split_into[sI]
      #)[0][0]
      

      if p1_code > p2_code:
        comparison_results.append(1)
      elif p1_code < p2_code:
        comparison_results.append(-1)
      else:
        comparison_results.append(0)
    return comparison_results

  def _update_history(self):
    # Prepare data
    history_data = {'Players': {},
      'Dealer': None,
      'RoundTime': None, 
    }

    for seat_label in self.player_seat_labels:
      this_player = self.players[seat_label]
      history_data['Players'][seat_label] = {}
      history_data['Players'][seat_label]['PlayerID'] = this_player.id
      history_data['Players'][seat_label]['SplitCards'] = this_player.split_info['Cards']
      history_data['Players'][seat_label]['SplitCodes'] = this_player.split_info['Codes']
      history_data['Players'][seat_label]['SplitCodeScores'] = this_player.split_info['Scores']
      history_data['Players'][seat_label]['SplitRanks'] = self.cur_split_ranks[seat_label]
      history_data['Players'][seat_label]['WeightedCodeScore'] = this_player.split_info['WeightedScore']
      history_data['Players'][seat_label]['GameScoreDetails'] = self.cur_score_details[seat_label]
      history_data['Players'][seat_label]['TotGameScore'] = self.cur_scores[seat_label]
      history_data['Players'][seat_label]['SplitSelectionTime'] = this_player.split_info['SelectionTime']
      history_data['Players'][seat_label]['SplitsGenerated'] = this_player.split_info['SplitsGenerated']
    history_data['Dealer'] = self.player_seat_labels[self.cur_dealer_ind]
    history_data['RoundTime'] = self.cur_round_time
    

    self.history.add_round(history_data)
    # 
    return 

  def _pregame_processes(self):
    # Play seqeuence (start with one after dealer)
    self.cur_play_seq = [(self.cur_dealer_ind + 1 + i) % self.n_players for i in range(self.n_players)]
    return

  def _postgame_processes(self):
    
    self.games_played += 1
    
    # Update history/stats
    self._update_history()

    # Change dealer
    self._next_dealer()
    
    # Clear variables
    self.reset_cur_game_info()

    for seat_label in self.player_seat_labels:
      #self.players[seat_label].cur_hand.reset_split_info()
      self.players[seat_label].reset_cur_game_data()
    return
  
  def _next_dealer(self):
    #cur_dealer_ind = self.player_labels.index(self.cur_dealer)
    self.cur_dealer_ind = (self.cur_dealer_ind + 1) % self.n_players
    
    return
  
  def _deal_random_cards(self):
    """Deal random sets of hands

    Returns:
        [type]: [description]
    """
    
    dealt_cards = self.deck.deal_cards()

    self._update_player_hands(dealt_cards)

    return dealt_cards
  
  def _deal_specific_cards(self, cards_to_deal, deal_cards_from_dealer):
    """Deal specific hands

    Args:
        card_to_deal ([type]): Hands to deal
    """
    self._update_player_hands(cards_to_deal, deal_cards_from_dealer)
    return
  
  def _update_player_hands(self, dealt_cards, deal_cards_from_dealer):
    
    if deal_cards_from_dealer:
      for i, player_ind in enumerate(self.cur_play_seq):
        seat_label = self.player_seat_labels[player_ind]
        self.players[seat_label].cur_hand = self.hand_class(dealt_cards[i])
    else:
      for i, seat_label in enumerate(self.__class__.player_seat_labels):
        self.players[seat_label].cur_hand = self.hand_class(dealt_cards[i])
    return

  def _dist_splits_data(self, splits_data):
    for i, seat_label in enumerate(self.__class__.player_seat_labels):
      self.players[seat_label].cur_splits_data = splits_data[i]
    return