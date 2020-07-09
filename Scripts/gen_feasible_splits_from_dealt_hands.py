
#%%


import sys
import json
from timeit import default_timer as timer

from ChinesePokerLib.classes.StrategyClass import ChinesePokerPctileScoreStrategyClass
from ChinesePokerLib.classes.DataClass import DataClass

from ChinesePokerLib.modules.SlackFunctions import post_message_to_slack_channel

import ChinesePokerLib.vars.GlobalConstants as GlobC 


def main(start_game_id, end_game_id, send_slack_update=True):
  data_obj = DataClass()

  strategy = ChinesePokerPctileScoreStrategyClass()

  deal_split_gen = data_obj.yield_splits_from_dealt_hands(strategy, start_game_id, end_game_id, from_db=True)
  start = timer()
  if send_slack_update:
    msg =  'gen_feasible_splits_from_dealt_hands.py:\n' + \
          f'-->Generating feasible splits for GameID between {start_game_id} and {end_game_id}.'
    post_message_to_slack_channel(
      msg, 
      GlobC.DEFAULT_SLACK_VARS['channel'], 
      GlobC.DEFAULT_SLACK_VARS['token'], 
      GlobC.DEFAULT_SLACK_VARS['icon'], 
      GlobC.DEFAULT_SLACK_VARS['username']
    )
  while 1:

    game_id, splits_data = next(deal_split_gen, (None, None))
    if game_id is None:
      break
    data_obj.write_splits_data_to_db(game_id, splits_data)
    min_elapsed = (timer()-start) / 60
    print (f'GameID {game_id} - total {min_elapsed} min_elapsed')
    
    if send_slack_update:
      msg = f'-->Generated feasible splits for GameID {game_id} - {min_elapsed} min elapsed.'
      post_message_to_slack_channel(
        msg, 
        GlobC.DEFAULT_SLACK_VARS['channel'], 
        GlobC.DEFAULT_SLACK_VARS['token'], 
        GlobC.DEFAULT_SLACK_VARS['icon'], 
        GlobC.DEFAULT_SLACK_VARS['username']
      )
if __name__ == "__main__":
  if len(sys.argv) > 3 and sys.argv[3] in ('0','False'):
    sys.exit(main(int(sys.argv[1]), int(sys.argv[2]), False))    
  else:
    sys.exit(main(int(sys.argv[1]), int(sys.argv[2]), True))
  