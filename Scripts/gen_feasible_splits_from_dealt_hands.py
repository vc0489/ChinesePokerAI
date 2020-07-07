
#%%
from ChinesePokerLib.classes.StrategyClass import ChinesePokerPctileScoreStrategyClass
from ChinesePokerLib.classes.DataClass import DataClass
from timeit import default_timer as timer

import sys
import json
import ChinesePokerLib.vars.GlobalConstants as GlobC 


def main(start_game_id, end_game_id):
  data_obj = DataClass()

  strategy = ChinesePokerPctileScoreStrategyClass()

  deal_split_gen = data_obj.yield_splits_from_dealt_hands(strategy, start_game_id, end_game_id, from_db=True)
  start = timer()
  while 1:

    game_id, splits_data = next(deal_split_gen, (None, None))
    if game_id is None:
      break
    data_obj.write_splits_data_to_db(game_id, splits_data)
    min_elapsed = (timer()-start) / 60
    print (f'GameID {game_id} - total {min_elapsed} min_elapsed')

if __name__ == "__main__":
  sys.exit(main(int(sys.argv[1]), int(sys.argv[2])))