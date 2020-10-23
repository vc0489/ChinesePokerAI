from datetime import datetime
from timeit import default_timer as timer
import pathlib
import re
import glob
import json
from deprecated import deprecated
import random


from ChinesePokerLib.classes.DeckClass import DeckClass
from ChinesePokerLib.classes.CardClass import CardClass
import ChinesePokerLib.modules.DBFunctions as DBF
from ChinesePokerLib.classes.CardGroupClass import CardGroupCode
from ChinesePokerLib.classes.StrategyClass import ChinesePokerStrategyClass

#from ChinesePokerLib.classes.StrategyClass import ChinesePokerPctileScoreStrategyClass

import ChinesePokerLib.vars.GameConstants as GameC 
import ChinesePokerLib.vars.GlobalConstants as GlobC 

deck_type = 'STANDARD'
deck_obj = DeckClass(deck_type)

def get_latest_dealt_hands_dump(min_n_games=10000):
  files = glob.glob(str(GlobC.DEALT_HANDS_DUMP_DIR / '*.txt'))

  p = re.compile('.*?/DealtCardsDump_([0-9]*?)Games_([0-9]{8}).txt')
  matches = [(p.match(filename).group(0), p.match(filename).group(1), p.match(filename).group(2)) for filename in files if p.match(filename) and int(p.match(filename).group(1)) >= min_n_games]

  datetimes = [datetime.strptime(item[2], '%Y%m%d') for item in matches]
  max_date_ind = datetimes.index(max(datetimes))

  latest_file = matches[max_date_ind][0]
  return latest_file
  

  
def gen_dealt_hands_and_add_to_db(
  n_games, 
  table=GameC.CHINESE_POKER_db_consts['dealt_hands_table'], 
  write_every=1000
):
  
  conn = DBF.connect_to_db()
  cursor = conn.cursor()
  start = timer()
  to_be_inserted = []
  base_query = f'INSERT INTO {table} (DealtHandsStr) VALUES '
  for i in range(1, n_games+1):
    dealt_cards = deck_obj.deal_cards()
    dealt_cards_str = _convert_dealt_cards_to_rep_str(dealt_cards)
    to_be_inserted.append(dealt_cards_str)
    if i % write_every == 0:
      query = base_query
      for dealt_cards_str in to_be_inserted:
        query += f'({dealt_cards_str}),'
      #insert_query = """INSERT INTO random_dealt_hands (DealtHandsStr) VALUES (%s)"""
      #cursor.executemany(insert_query, to_be_inserted)
      query = query[:-1]
      cursor.execute(query)
      conn.commit()
      min_elapsed = (timer()-start)/60
      print(f'Inserted {i} of {n_games} DealtHandsStr rows into {table} - {min_elapsed} min elasped.')
      to_be_inserted = []
  return
      
@deprecated
def gen_dealt_hands_text_dump(
  n_games,
  output_file=None,
  output_progress_every=1000
):
  
  if output_file is None:
    today_str = datetime.today().strftime('%Y%m%d')
    output_file = pathlib.Path(GlobC.DEALT_HANDS_DUMP_DIR) / f'DealtCardsDump_{n_games}Games_{today_str}.txt'

  with open(output_file,'w') as f:
    for gI in range(n_games):
      if output_progress_every and (gI+1) % output_progress_every == 0:
        print(f'Dealt {gI+1} of {n_games}')
      #dealt_deck_rep = undealt_deck_rep.copy()
      dealt_cards = deck_obj.deal_cards()
      dealt_cards_str = _convert_dealt_cards_to_rep_str(dealt_cards)
      f.write(dealt_cards_str + '\n')
  return


def yield_dealt_hands_from_db(
  start_game_no,
  end_game_no,
  db_connector=None,
  db_load_batch_size=1000,
  cards_as_str=False,
):
  """Generator that yields dealt cards from DB one game at a time for a range of GameIDs.

  Args:
      start_game_no (int): Start game number.
      end_game_no (int): End game number.
      db_connector ([type], optional): [description]. Defaults to None.
      db_load_batch_size (int, optional): [description]. Defaults to 1000.
      cards_as_str (bool, optional): Return cards as string rather then CardClass objects. Defaults to False.

  Yields:
      [type]: [description]
  """
  dealt_hands_table = GameC.CHINESE_POKER_db_consts["dealt_hands_table"]
  base_query = f'SELECT GameID, DealtHandsStr FROM {dealt_hands_table} WHERE GameID BETWEEN %s AND %s'
  #deck_obj = DeckClass()

  if start_game_no is None:
    start_game_no = 1
  
  temp_start_game_no = start_game_no

  while 1:
    temp_end_game_no = min(end_game_no, temp_start_game_no + db_load_batch_size-1)
    query = base_query % (temp_start_game_no, temp_end_game_no)

    db_output, _ = DBF.select_query(query)
    for row in db_output:
      dealt_cards = _convert_rep_str_to_dealt_cards(row[1])
      if cards_as_str:
        dealt_cards = [[str(card) for card in hand] for hand in dealt_cards]
      yield row[0], dealt_cards
    if temp_end_game_no >= end_game_no:
      break
    
    temp_start_game_no += db_load_batch_size
  yield None, None

    
def _convert_dealt_cards_to_rep_str(dealt_cards):
  """Go from set of dealt cards to single DealtHandsStr to be uploaded to the 
  random_dealt_hands table in the DB.

  Args:
      dealt_cards ([type]): [description]

  Returns:
      str: 52 character string. The characters correspond to cards in the deck in
           order defined by deck.deck_card_order.


  E.g. '2421213...' means 
    SA -> Player 2
    SK -> Player 4
    SQ -> Player 2
    SJ -> Player 1
    S10 -> Player 2
    S9 -> Player 1
    S8 -> Player 3
  ...and so on
  """
  dealt_deck_rep = ['0' for card in deck_obj.deck]
  for pI, player_cards in enumerate(dealt_cards):
    for card in player_cards:
      dealt_deck_rep[card.deck_card_ind] = str(pI+1)
      dealt_cards_str = ''.join(dealt_deck_rep)
  return dealt_cards_str

def _convert_rep_str_to_dealt_cards(rep_str):
  """Convert DealtHandsStr to set of dealt cards. This is the reverse of 
  _convert_dealt_card_to_rep_str.

  Args:
      rep_str (str): 52-character DealtHandsStr
      n_players (int, optional): [description]. Defaults to 4.

  Returns:
      list: [description]

  """
  player_inds = [int(char) for char in rep_str.strip()]
  
  n_players = max(player_inds)
    
  dealt_cards = [[] for _ in range(n_players)]
  
  for card_strength_ind, player_ind in enumerate(player_inds):
    card_deck_ind = deck_obj.inds_of_deck_card_order[card_strength_ind]
    dealt_cards[player_ind-1].append(deck_obj.deck[card_deck_ind])
  
  return dealt_cards

  
def yield_splits_from_dealt_hands(
  strategy,
  start_game_id=None, 
  end_game_id=None, 
  verbose=False,
):
  """Gets dealt hands from DB then uses strategy to generate all splits

  Args:
      strategy ([type]): Strategy used to generate splits on hands via .gen_all_splits
      start_game_id (int, optional): Generate splits starting from this GameID. Defaults to None.
      end_game_id (int, optional): Generate splits up to this GameID. Defaults to None.
      verbose (bool, optional): [description]. Defaults to False.

  Yields:
      [type]: [description]
  """
  # VC TODO: verbose -> progress_every_n_splits
  dealt_cards_generator = yield_dealt_hands_from_db(start_game_id, end_game_id)
    
  while 1:
    game_id, dealt_cards = next(dealt_cards_generator)

    if game_id is None:
      break

    if start_game_id is not None and game_id < start_game_id:
      continue
    
    if end_game_id is not None and game_id > end_game_id:
      break

    data = {}
    for player_ind in range(4):
      splits, sec_elapsed = strategy.gen_all_splits(dealt_cards[player_ind])
      
      cards = []
      codes = []
      card_inds = []
      split_inds_strs = []
      for split in splits:
        cards.append([str(card) for split_set in split[1] for card in split_set])
        card_inds.append([ind for split_set in split[0] for ind in split_set])
        codes.append([code.code for code in split[2]])
        split_inds_strs.append(_convert_card_inds_to_set_inds_str(split[0]))

      data[f'P{player_ind+1}'] = {
        'CardInds':card_inds, 
        'SplitIndsStrs':split_inds_strs, 
        'Cards':cards, 
        'Codes':codes, 
        'DealtCards': dealt_cards[player_ind],
        'SecElapsed': sec_elapsed,
      }
      
    yield game_id, data
    
  yield None, None
  return


def write_splits_data_to_db(game_id, splits_data):
  """Function for writing splits data generated by 
  yield_splits_from_dealt_hands to db.
  
  Writes to: feasible_hand_splits - GameID, SeatID, SplitSeqNo, SplitStr, DateGen
             split_set_codes - SplitID, SeatID, SetNo, L1Code, L2Code, L3Code, L4Code, L5Code, L6Code

  Args:
      game_id (int): Game ID - Should match what is in
                                random_dealt_hands
      splits_data ([type]): Dict with following structure:
        ('P{PLAYERNO}':player_splits_data) where PLAYERNO between 1 and 4 inclusive
        player_splits_data itself is a dict with the following structure:
          'DealtCards': Dealt cards in original order
          'CardInds': List of indices lists.
                      Each outer list corresponds to a possible split.
                      The indices refer to the indices of the DealtCards list. 
                      The order combined with the split_into attribute of the strategy object infers the split card sets.
          'Codes': List of list of tuples.
                    Each outer list corresponds to a possible split.
                    Each inner list consists of tuples representing the card group codes of the sets.
          'Scores': List of score lists.
                    Each outer list corresponds to a possible split.
                    Each inner list contains the set scores.  
          'WeightedScores': List of weighted scores.
                            One score for each possible split.    
          'SplitIndsStrs': List of strings, each of length 13, the characters correspond to the dealt cards.
                            Each string corresponds to a possible split.
                            The characters refer to the set number where each card is split into.
                            E.g. '1112222233333' means the first 3 cards (of DealtCards) are in the first set, 
                              the next 5 cards are in the second set and the last 5 cards are in the third set. 
  """
  
  date_gen = datetime.today().strftime('%Y-%m-%d')
  splits_table = GameC.CHINESE_POKER_db_consts['splits_table']
  
  codes_table = GameC.CHINESE_POKER_db_consts['split_codes_table']
  
  db_connector = DBF.connect_to_db()
  # First check that there are no existing splits in the DB. If there are, delete them.
  check_query = f"SELECT COUNT(*) FROM {splits_table} WHERE GameID={game_id} AND DateGenerated ='{date_gen}'"
  db_output, db_connector = DBF.select_query(check_query, db_connector)
  if db_output[0][0] > 0:
    delete_query = f"DELETE FROM {splits_table} WHERE GameID={game_id} AND DataGenerated='{date_gen}'"
    db_connector, rows_deleted = DBF.delete_query(delete_query, db_connector)
    print(f'***Deleted {rows_deleted} rows with identical GameID ({game_id}) and DateGenerated ({date_gen}).***')

  for seat_ID in range(1,5):

    player_splits_data = splits_data[f'P{seat_ID}']
    #n_splits = len(player_splits_data['SplitIndsStrs']
    for seqI, split_str in enumerate(player_splits_data['SplitIndsStrs']):
      splits_query = f'INSERT INTO {splits_table} (GameID, SeatID, SplitSeqNo, SplitStr, DateGenerated) VALUES (%s, %s, %s, %s, %s)'
      splits_query = splits_query % (game_id, seat_ID, seqI+1, split_str, f"'{date_gen}'")

      db_connector, split_id = DBF.insert_query(splits_query, db_connector, False, True)

      base_codes_query = f'INSERT INTO {codes_table} ' + \
                          '(SplitID, SetNo, L1Code, L2Code, L3Code, L4Code, L5Code, L6Code) VALUES ' + \
                          '(%s, %s, %s, %s, %s, %s, %s, %s)'
      
      values_list = []
      for setI, set_code in enumerate(player_splits_data['Codes'][seqI]):
        base_val = [None for i in range(8)]
        base_val[0] = split_id
        base_val[1] = setI+1
        for levelI, level_code in enumerate(set_code):
          base_val[2+levelI] = level_code
        values_list.append(tuple(base_val))  
      
      db_connector = DBF.insert_many_query(base_codes_query, values_list, db_connector, True)
      
      db_connector = DBF.try_commit(db_connector)

  return

def _convert_card_inds_to_set_inds_str(card_inds, n_cards=13):
  """Convert List of card ind lists to single split string (of 1,2,3) to store in DB

  Args:
      card_inds ([type]): [description]
      n_cards (int, optional): [description]. Defaults to 13.

  Returns:
      [type]: [description]
  """
  if not n_cards:
    n_cards = sum([len(card_set) for card_set in card_inds])
  
  char_list = ['' for i in range(n_cards)]

  for set_i, card_set_inds in enumerate(card_inds):
    for ind in card_set_inds:
      char_list[ind] = str(set_i+1)

  set_inds_str = ''.join(char_list)  
  
  return set_inds_str
  
def _convert_split_str_to_split_cards(
  cards,
  split_str,
):
  card_set_inds = [int(c)-1 for c in list(split_str)]
  n_sets = max(card_set_inds)+1
  
  card_sets = [[] for _ in range(n_sets)]
  card_inds = [[] for _ in range(n_sets)]

  for cI, card in enumerate(cards):
    card_sets[card_set_inds[cI]].append(card)
    card_inds[card_set_inds[cI]].append(cI)
  card_sets = [tuple(card_set) for card_set in card_sets]

  return card_sets, card_inds

def get_splits_data_for_single_game_and_seat_from_db(
  game_id, seat_id, cards=None,
):
  """[summary]

  Args:
      game_id (int): GameID
      seat_id (int): Between 1 and 4
      cards (List): List of CardClass objects or card strings. 
  """

  if cards is None:
    hands = next(yield_dealt_hands_from_db(game_id, game_id))[1]
    cards = hands[seat_id-1]
  elif isinstance(cards[0], str):
    deck = DeckClass()
    cards = deck.deal_custom_hand(cards)

  splits_table = GameC.CHINESE_POKER_db_consts['splits_table']
  codes_table = GameC.CHINESE_POKER_db_consts['split_codes_table']
  query = f'SELECT SplitSeqNo, SplitStr, + ' \
          f'c1.L1Code AS S1L1Code, c1.L2Code AS S1L2Code, c1.L3Code AS S1L3Code, c1.L4Code AS S1L4Code, c1.L5Code AS S1L5Code, c1.L6Code AS S1L6Code, ' + \
          f'c2.L1Code AS S2L1Code, c2.L2Code AS S2L2Code, c2.L3Code AS S2L3Code, c2.L4Code AS S2L4Code, c2.L5Code AS S2L5Code, c2.L6Code AS S2L6Code, ' + \
          f'c3.L1Code AS S3L1Code, c3.L2Code AS S3L2Code, c3.L3Code AS S3L3Code, c3.L4Code AS S3L4Code, c3.L5Code AS S3L5Code, c3.L6Code AS S3L6Code ' + \
          f'FROM {splits_table} s ' + \
          f'JOIN {codes_table} c1 ON s.SplitID=c1.SplitID ' + \
          f'JOIN {codes_table} c2 ON s.SplitID=c2.SplitID ' + \
          f'JOIN {codes_table} c3 ON s.SplitID=c3.SplitID ' + \
          f'WHERE s.GameID={game_id} AND s.SeatID={seat_id} ' + \
          f'AND c1.SetNo=1 AND c2.SetNo=2 AND c3.SetNo=3'
  db_output, _ = DBF.select_query(query)
  hand_splits = []
  for row in db_output:
    split_seq_no, split_str, s1c1,s1c2,s1c3,s1c4,s1c5,s1c6, s2c1,s2c2,s2c3,s2c4,s2c5,s2c6, s3c1,s3c2,s3c3,s3c4,s3c5,s3c6 = row

    split_cards, split_inds = _convert_split_str_to_split_cards(cards, split_str)
    s1code = [s1c1, s1c2, s1c3, s1c4, s1c5, s1c6]
    s2code = [s2c1, s2c2, s2c3, s2c4, s2c5, s2c6]
    s3code = [s3c1, s3c2, s3c3, s3c4, s3c5, s3c6]

    s1code = CardGroupCode([code for code in s1code if code is not None])
    s2code = CardGroupCode([code for code in s2code if code is not None])
    s3code = CardGroupCode([code for code in s3code if code is not None])
    
    split_info_factory = ChinesePokerStrategyClass.ranked_split_info_factory

    split_info = split_info_factory(
      split_inds,
      split_cards,
      (s1code, s2code, s3code),
      None,
      None,
      None,
      None,
      None,
      split_seq_no,
    )
    hand_splits.append(split_info)  
  
  hand_splits = sorted(hand_splits, key=lambda x: x.SeqNo)
  return hand_splits

def yield_splits_data_from_db(
  start_game_id = None,
  end_game_id = None,
):

  #db_connector = DBF.connect_to_db()
  #splits_table = GameC.CHINESE_POKER_db_consts['splits_table']
  #codes_table = GameC.CHINESE_POKER_db_consts['split_codes_table']
  #base_query = f'SELECT SplitSeqNo, SplitStr, + ' \
  #              f'c1.L1Code AS S1L1Code, c1.L2Code AS S1L2Code, c1.L3Code AS S1L3Code, c1.L4Code AS S1L4Code, c1.L5Code AS S1L5Code, c1.L6Code AS S1L6Code, ' + \
  #              f'c2.L1Code AS S2L1Code, c2.L2Code AS S2L2Code, c2.L3Code AS S2L3Code, c2.L4Code AS S2L4Code, c2.L5Code AS S2L5Code, c2.L6Code AS S2L6Code, ' + \
  #              f'c3.L1Code AS S3L1Code, c3.L2Code AS S3L2Code, c3.L3Code AS S3L3Code, c3.L4Code AS S3L4Code, c3.L5Code AS S3L5Code, c3.L6Code AS S3L6Code ' + \
  #              f'FROM {splits_table} s ' + \
  #              f'JOIN {codes_table} c1 ON s.SplitID=c1.SplitID ' + \
  #              f'JOIN {codes_table} c2 ON s.SplitID=c2.SplitID ' + \
  #              f'JOIN {codes_table} c3 ON s.SplitID=c3.SplitID ' + \
  #              f'WHERE s.GameID=%s AND s.SeatID=%s ' + \
  #              f'AND c1.SetNo=1 AND c2.SetNo=2 AND c3.SetNo=3'

  for game_id in range(start_game_id, end_game_id+1):
    hands = next(yield_dealt_hands_from_db(game_id, game_id))[1]
    game_splits = []

    for seat_id in range(1,5):
      
      #query = base_query  % (game_id, seat_id)
      cards = hands[seat_id-1]
      hand_splits = get_splits_data_for_single_game_and_seat_from_db(game_id, seat_id, cards)
      
      """
      db_output, _ = DBF.select_query(query)
      
      hand_splits = []
      for row in db_output:
        split_seq_no, split_str, s1c1,s1c2,s1c3,s1c4,s1c5,s1c6, s2c1,s2c2,s2c3,s2c4,s2c5,s2c6, s3c1,s3c2,s3c3,s3c4,s3c5,s3c6 = row

        split_cards = _convert_split_str_to_split_cards(cards, split_str)
        s1code = [s1c1, s1c2, s1c3, s1c4, s1c5, s1c6]
        s2code = [s2c1, s2c2, s2c3, s2c4, s2c5, s2c6]
        s3code = [s3c1, s3c2, s3c3, s3c4, s3c5, s3c6]

        s1code = CardGroupCode([code for code in s1code if code is not None])
        s2code = CardGroupCode([code for code in s2code if code is not None])
        s3code = CardGroupCode([code for code in s3code if code is not None])
        
        split_info_factory = ChinesePokerStrategyClass.ranked_split_info_factory

        split_info = split_info_factory(
          None,
          split_cards,
          (s1code, s2code, s3code),
          None,
          None,
          None,
          None,
          None,
          split_seq_no,
        )
        hand_splits.append(split_info)
      """
      game_splits.append(hand_splits)
    
    yield game_id, game_splits
          

        # TODO Convert each row to RankedSplitInfo named tuple
        # (Inds, Cards, Codes, )
  return



def select_random_game_id_with_splits():
  max_game_id = max_game_id_in_splits_table()
  random_game_id = random.randint(1, max_game_id-1)
  
  return random_game_id

def random_game_setup_from_db():
  
  game_id = select_random_game_id_with_splits()

  hand_no = random.randint(1,4)
  game_setup = load_game_setup(game_id, hand_no)

  return (game_id, hand_no), game_setup

  
def load_game_setup(game_id, hand_no):
  """[summary]

  Args:
      game_id (int): GameID
      hand_no (int): Integer between 1 and 4 inclusive
  """
  dealt_cards = next(yield_dealt_hands_from_db(game_id, game_id))[1]
  
  return dealt_cards[hand_no-1:] + dealt_cards[:hand_no-1]
  

def _get_split(game_id, seat_id, split_seq_no):
  splits_table = GameC.CHINESE_POKER_db_consts['splits_table']
  query = f'SELECT SplitStr FROM {splits_table} WHERE GameID={game_id} AND SeatID={seat_id} AND SplitSeqNo={split_seq_no}'
  db_output, _ = DBF.select_query(query)
  return db_output[0][0]

def fetch_random_feasible_split_for_game_and_seat(game_id, seat_id, inds_only=True):

  # TODO get code as well
  n_feasible_splits = number_of_feasible_splits_for_game_and_seat(game_id, seat_id)

  random_split = random.randint(1, n_feasible_splits)
  split_str = _get_split(game_id, seat_id, random_split)
  split_set_inds = [int(c) for c in split_str]
  print(f'split_set_inds: {split_set_inds}')
  n_sets = max(split_set_inds)
  set_inds = [[] for _ in range(n_sets)]
  if inds_only:
    for card_ind,set_ind in enumerate(split_set_inds):
      set_inds[set_ind-1].append(card_ind)
    return set_inds, random_split
  else:
    raise NotImplementedError('VC: Not implemented yet.')


##########################################
### START Useful query functions START ###
##########################################
  

def max_game_id_in_splits_table():
  splits_table = GameC.CHINESE_POKER_db_consts['splits_table']
  query = f'SELECT MAX(GameID) FROM {splits_table}'
  db_output, _ = DBF.select_query(query)

  return db_output[0][0]

def number_of_feasible_splits_for_game_and_seat(game_id, seat_id):

  splits_table = GameC.CHINESE_POKER_db_consts['splits_table']
  query = f'SELECT Max(SplitSeqNo) FROM {splits_table} WHERE GameID={game_id} AND SeatID={seat_id}'
  db_output, _ = DBF.select_query(query)

  return db_output[0][0]
######################################
### END Useful query functions END ###
######################################