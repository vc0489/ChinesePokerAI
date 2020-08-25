from timeit import default_timer as timer

from ChinesePokerLib.classes.HandClass import ChinesePokerHandClass


class ChinesePokerPlayerClass:
  _players_created = 0

  def __init__(
    self, 
    game_type='CHINESE-POKER',
    name=None,
  ):
    self.cur_hand = None
    self.game_type = game_type
    self.name = name
    self.cur_splits_data = None

    self._add_id()
    self._reset_split_info()
    #self.cur_played_hand = None
    return

  def _add_id(self):
    ChinesePokerPlayerClass._players_created += 1
    self.id = ChinesePokerPlayerClass._players_created

  def _get_game_history(self):
    return
  
  def reset_cur_game_data(self):
    """Reset player game data - should be run after each game
    """
    self.cur_hand = None
    self.cur_splits_data = None
    self._reset_split_info
    return
  
    
  def _reset_split_info(self):
    """Reset info of last split
    """

    self.split_info = {
      'Inds':None,
      'Codes':None,
      'SupScores':None,
      'Cards':None,
      'SplitScore':None,
      'SelectionTime':None,
      'SplitsGenerated':None,
    }

class HumanChinesePokerPlayerClass(ChinesePokerPlayerClass):
  def __init__(self):
    super().__init__()
    return

"""
class ComputerPlayerClass(PlayerClass):
  def __init__(
    self,
    
  ):
    super().__init__()
    
    return
"""

class ComputerChinesePokerPlayerClass(ChinesePokerPlayerClass):
  def __init__(
    self, 
    strategy,
    choose_split_max_sec = 10,
  ):
    super().__init__()
    self.strategy = strategy
    self.choose_split_max_sec = choose_split_max_sec
    return
  
  def play_hand(self):
    """Play hand (choose split) according to the strategy defined in the strategy 
    attribute (dict).
    """

    if self.cur_splits_data is not None:
      split_info, split_det, time_to_choose_split = self.strategy.pick_single_split_from_full_split_data(self.cur_splits_data)
    else:
      split_info, split_det, time_to_choose_split = self.strategy.pick_single_split(self.cur_hand.cards)
      
    # VC TODO: add var checking (see HandClass)
    self.split_info['Inds'] = split_info.Inds
    self.split_info['Cards'] = split_info.Cards
    self.split_info['Codes'] = split_info.Codes
    self.split_info['SupScores'] = split_info.StratSupScores
    self.split_info['SplitScore'] = split_info.StratSplitScore
    if split_det:
      self.split_info['SplitsGenerated'] = len(split_det)
    else:
      self.split_info['SplitsGenerated'] = None
    self.split_info['SelectionTime'] = time_to_choose_split

    return 