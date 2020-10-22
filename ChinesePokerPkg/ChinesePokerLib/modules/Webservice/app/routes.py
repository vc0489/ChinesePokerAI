#from ChinesePokerLib.modules.Webservice.app import app
from flask import render_template, flash, redirect, url_for, session, send_file, request, jsonify, current_app
from app import app, utils
from app.forms import SuggestForm
import base64
from io import StringIO
from pathlib import Path
from timeit import default_timer as timer
from random import shuffle

#card_images_dir = Path(app.root_path)
app_root_path = Path(app.root_path)
card_img_id_prefix = 'c'

@app.route('/')
@app.route('/index')
def index():
    user = {'username':'Guest'}
    hand_queries = [
      {'cards':'SA,SK,SQ,SJ,S10,S9,S8,S7,S6,S5,S4,S3,S2'},
      {'cards':'HA,HK,HQ,HJ,H10,H9,H8,H7,H6,H5,H4,H3,H2'},
      {'cards':'DA,DK,DQ,DJ,D10,D9,D8,D7,D6,D5,D4,D3,D2'},
      {'cards':'CA,CK,CQ,CJ,C10,C9,C8,C7,C6,C5,C4,C3,C2'}
    ]
    
    return render_template('index.html', title='Home', user=user, hand_queries=hand_queries)

    #return "Hello, World!"

@app.route('/suggest', methods=['GET', 'POST'])
def suggest():
  card_img_prefix = 'cardimg-'
  if request.method == 'POST':
    print('POST!')
    print(request.form)
    # Validate form - i.e. check cards
    
    processed_form_data = utils.parse_suggest_form_data(request.form, card_img_prefix)
    print(processed_form_data)
    n_cards = len(processed_form_data['Cards'])
    if n_cards < 13:
      flash(f'Not enough cards ({n_cards}) selected. Please select 13 cards.') 
    elif len(processed_form_data['Cards']) > 13:
      flash(f'Too many cards ({n_cards}) selected. Please select 13 cards.') 
    else:
      flash(f'Correct form')
      session['cards'] = processed_form_data['Cards']
      session['unique_code_levels'] = processed_form_data['UniqueTopCodeLevels']
      session['n_suggestions'] = processed_form_data['nSuggestions']
    
      if session.get('suggested_splits') is not None:
        del session['suggested_splits']
    
      return redirect(url_for('suggested_splits'))
  else:    
    print('GET!')
  all_card_img_info=utils.construct_all_cards_img_info()
  
  return render_template(
    'suggest.html',
    title='Split Suggester',
    all_card_img_info=all_card_img_info,
    card_img_prefix=card_img_prefix,
  )

  #form_old = SuggestForm()
  """
  if form_old.validate_on_submit():
    
    if form_old.choose_random:
      
      cards = utils.random_hand()
      flash(f'Randomly selected {cards}.') 
    else:
      cards = []
      for number in form_old.spades.data:
        cards.append('S' + number)
      for number in form_old.hearts.data:
        cards.append('H' + number)
      for number in form_old.diamonds.data:
        cards.append('D' + number)
      for number in form_old.clubs.data:
        cards.append('C' + number)
      flash(f'User selected {cards}.')  
    
    
    
    unique_code_levels = int(form_old.unique_code_levels.data)
    if unique_code_levels == 0:
      unique_code_levels = None
    n_suggestions = form_old.n_suggestions.data

    session['cards'] = cards
    session['unique_code_levels'] = unique_code_levels
    session['n_suggestions'] = n_suggestions
    
    if session.get('suggested_splits') is not None:
      del session['suggested_splits']
    
    return redirect(url_for('suggested_splits'))
  """
  #return render_template('suggest.html', title='Split Suggester', form=form)
  


@app.route('/suggested')
def suggested_splits():
  
  if session.get('cards') is None:
    return redirect(url_for('suggest'))
  
  if session.get('suggested_splits') is None:
    cards = session['cards']
    n_suggestions = session['n_suggestions']
    unique_code_levels = session['unique_code_levels']

    print(f'Cards: {cards}')
    print('Getting suggestions...')
    suggested_splits_cards, _ = utils.get_suggestions(cards, int(n_suggestions), int(unique_code_levels))
    #suggested_splits_cards = [[[str(c) for c in s] for s in split[1]] for split in suggested_splits]
    session['suggested_splits'] = suggested_splits_cards
    
  else:
    print('Loading suggested splits from session')
    suggested_splits_cards = session['suggested_splits']
    cards = session['cards']
  
  sel_card_img_filenames = utils.construct_selected_cards_img_filename_list(cards)

  #start = timer()
  suggested_splits_imgs = [[utils.construct_concat_cards_img(card_set, app_root_path) for card_set in card_split] for card_split in suggested_splits_cards]
  #print(f'Suggested splits img gen time: {timer()-start}')

  return render_template(
    'suggested.html',
    title='Suggested Splits',
    sel_card_img_filenames=sel_card_img_filenames,
    suggested_split_imgs=suggested_splits_imgs
  )
    
@app.route('/simulate/<split_no>')
def simulate(split_no):
  if session.get('suggested_splits') is None:
    return redirect(url_for('suggest'))

  # Code to run simulation
  return render_template('simulate.html', title=f'Simulatation With Split {split_no}')


@app.route('/post/random_valid_split', methods=['POST'])
def random_valid_split():
  sets_card_inds, split_seq_no = utils.get_random_valid_split(session['GameID'], session['SeatID'])
  session['RandomSplitSeqNo'] = split_seq_no
  
  set_descs = []
  set_codes = []
  sorted_sets_card_inds = []
  for set_card_inds in sets_card_inds:
    set_cards = utils.card_inds_to_cards(session['game_cards'][0], set_card_inds)
    set_code, set_desc, set_sorted_inds = utils.classify_group(set_cards)
    
    print(f'set_sorted_inds: {set_sorted_inds}')
    sorted_set_card_inds = [set_card_inds[ind] for ind in set_sorted_inds]

    set_codes.append(set_code)
    set_descs.append(set_desc)
    
    sorted_sets_card_inds.append(sorted_set_card_inds)

  # Build set images
  file_list = utils.construct_random_valid_split_img_filename_lists(session['game_cards'][0], sorted_sets_card_inds)

  return jsonify(
    {
      'set1Files':file_list[0],
      'set2Files':file_list[1],
      'set3Files':file_list[2],
      'SplitSeqNo':split_seq_no,
      'set1Code':str(set_codes[0].code),
      'set2Code':str(set_codes[1].code),
      'set3Code':str(set_codes[2].code),
      'set1Desc':set_descs[0],
      'set2Desc':set_descs[1],
      'set3Desc':set_descs[2],
      'CardIdPrefix': card_img_id_prefix,
    }
  )


@app.route('/post/play_hand', methods=['POST'])
def play_hand():
  data = request.get_json()

  player_split_codes = (
    data['Set1Code'],
    data['Set2Code'],
    data['Set3Code']
  )
  
  player_split_codes_com_100 = (
    data['Set1CodeCom100'],
    data['Set2CodeCom100'],
    data['Set3CodeCom100']
  )

  print('Player split codes')
  print(player_split_codes)
  
  # Update DB with player split
  utils.update_CPT_round_row_with_player_split(data['AppRoundID'], data['SplitInds'])

  # Get scores
  comp_res, game_scores, tot_game_scores = utils.play_hand(
    player_split_codes, 
    data['Com1SplitInfo']['SplitCodes'],
    data['Com2SplitInfo']['SplitCodes'],
    data['Com3SplitInfo']['SplitCodes'],
  )

  # Get scores if player was com with ability 100 
  _, game_scores_com_100, tot_game_scores_com_100 = utils.play_hand(
    player_split_codes_com_100, 
    data['Com1SplitInfo']['SplitCodes'],
    data['Com2SplitInfo']['SplitCodes'],
    data['Com3SplitInfo']['SplitCodes'],
  )

  # Update DB with game scores
  utils.update_CPT_round_row_with_game_scores(data['AppRoundID'], tot_game_scores, tot_game_scores_com_100[0])

  output = {
    'SplitComp': comp_res,
    'GameScores': game_scores,
    'TotGameScores': tot_game_scores,
    'GameScoresCom100': game_scores_com_100,
    'TotGameScoresCom100': tot_game_scores_com_100,
  }
  

  # Get computer splits img files
  for com_id in range(1,4):
    com_split_desc = [] # Set descriptions
    com_ordered_card_inds = [] # Set card inds
    for sI, set_code in enumerate(data[f'Com{com_id}SplitInfo']['SplitCodes']):
      temp_card_set = [session['game_cards'][com_id][ind] for ind in data[f'Com{com_id}SplitInfo']['SplitInds'][sI]]
      _, temp_desc, temp_inds = utils.classify_group(temp_card_set, set_code)
      com_split_desc.append(temp_desc)
      com_ordered_card_inds.append([data[f'Com{com_id}SplitInfo']['SplitInds'][sI][ind] for ind in temp_inds])

    #com_seat_id = utils.get_com_seat_id(session['SeatID'], com_id)
    comp_file_list = utils.construct_random_valid_split_img_filename_lists(session['game_cards'][com_id], com_ordered_card_inds)

    
    output[f'Com{com_id}Files'] = comp_file_list
    output[f'Com{com_id}SplitDesc'] = com_split_desc
  
  return jsonify(output)

@app.route('/post/check_valid_split', methods=['POST'])
def check_valid_split():
  data = request.get_json()
  
  print(data['set1Code'])
  print(type(data['set1Code']))
  is_valid = utils.check_valid_split(data['set1Code'],data['set2Code'],data['set3Code'])

  if is_valid:
    return jsonify({'isValid':1})
  else:
    return jsonify({'isValid':0})
  
@app.route('/post/get_computer_split', methods=['POST'])
def get_computer_split():
  data = request.get_json()
  com_id = data['ComID']
  com_difficulty = data['Difficulty']
  app_round_id = data['AppRoundID']
  is_true_com = data['IsTrueCom']

  #if com_id == 1:
  #  raise ValueError
  if is_true_com:
    com_seat_id = utils.get_com_seat_id(session['SeatID'], com_id)
  else:
    com_seat_id = session['SeatID']

  com_split = utils.get_computer_split(
    session['GameID'], 
    com_seat_id, 
    current_app.com_strat, 
    session['game_cards'][com_id],
    com_difficulty
  )
  
  output = {}
  
  if is_true_com:
    utils.update_CPT_round_row_with_com_split(app_round_id, com_id, com_split.SeqNo)
  else:
    utils.update_CPT_round_row_with_player_split_as_com_100(app_round_id, com_split.SeqNo)
  output[f'SplitInds'] = com_split.Inds
  output[f'SplitCodes'] = [str(code.code) for code in com_split.Codes]
  
  
  return jsonify(output)
  
@app.route('/post/update_set_descriptions', methods=['POST'])
def update_set_descriptions():
  data = request.get_json()
  print(data)

  cards = utils.card_ids_to_cards(session['game_cards'][0], data['cardIds'], card_img_id_prefix)
  print(cards)

  group_code, group_desc, _ = utils.classify_group(cards)
  target_set = data['targetSet']
  data[f"set{target_set}Code"] = group_code
  is_valid = utils.check_valid_split(data['set1Code'],data['set2Code'],data['set3Code'])
  print(is_valid)
  return jsonify({'Description': group_desc, 'SetCode': str(group_code.code), 'ValidSplit':int(is_valid)})

@app.route('/post/end_game', methods=['POST'])
def end_game():
  data = request.get_json()

  utils.end_of_game_CPT_game_row_update(data['AppGameID'], data['NoRounds'], data['TotScore'], data['TotCptScore'])
  return jsonify({})

@app.route('/post/submit_score', methods=['POST'])
def submit_score():
  data = request.get_json()

  if not data['Email']:
    email = None
  else:
    email = data['Email']
  utils.update_CPT_submit_score(data['AppGameID'], data['Name'], email)
  
  return jsonify({})
  
@app.route('/post/get_leaderboard', methods=['POST'])
def get_leaderboard():
  data = request.get_json()

  if 'AppGameID' in data:
    app_game_ID = data['AppGameID']
  else:
    app_game_ID = None
  
  if 'ShowTop' in data:
    show_top = data['ShowTop']
  else:
    show_top = 10
  #print(app_game_ID)

  leaderboard_info = utils.gen_leaderboard(show_top, app_game_ID)
  print(leaderboard_info)
  return jsonify({'Leaders':leaderboard_info})


@app.route('/post/gen_app_game_id', methods=['POST'])
def get_app_game_id():
  data = request.get_json()
  
  app_game_id = utils.create_CPT_game_row(data['ClientIP'], data['ComDifficulty'])
  return jsonify({'AppGameID':app_game_id})

@app.route('/post/add_round_info_to_db', methods=['POST'])
def add_round_info_to_db():
  data = request.get_json()
  app_round_id = utils.create_CPT_round_row(
    data['AppGameID'],
    data['RoundNo'],
    data['HandGameID'],
    data['HandSeatID'],
  )
  return jsonify({'AppRoundID':app_round_id})

@app.route('/post/update_rounds_table_with_com_splits', methods=['POST'])
def add_com_splits_to_db():
  return

@app.route('/game', methods=['GET'])
def play_game():

    
  return render_template(
    'game.html',
    title='Play Game',
  )


@app.route('/get/initialise')
def initilialise_game():
  """ Get constants etc.

  Returns:
      [type]: [description]
  """
  return jsonify({'CardIdPrefix': card_img_id_prefix})

@app.route('/post/deal_new_round', methods=['POST'])
def new_round():

  # Can contain specific game/hand IDs
  data = request.get_json()
  
  # Random hand
  (game_id, seat_id), cards_dealt = utils.random_game()
  cards_dealt = [[str(card) for card in hand] for hand in cards_dealt]
  
  # Generate card img file info
  dealt_cards_img_filenames_full = utils.construct_selected_cards_img_filename_list(cards_dealt[0], True)
  dealt_cards_img_filenames = utils.construct_selected_cards_img_filename_list(cards_dealt[0], False)
  
  # Store game data in server cookie
  session['GameID'] = game_id
  session['SeatID'] = seat_id
  session['game_cards'] = cards_dealt

  # Create output
  output = {
    'GameID': game_id,
    'SeatID': seat_id,
    'DealtCardsImgFilenamesFull': dealt_cards_img_filenames_full,
    'DealtCardsImgFilenames': dealt_cards_img_filenames,
  }
  return jsonify(output)

@app.route('/choose_split')
def play_choose_split():

  cards = utils.random_hand()
  dealt_card_img_filenames = utils.construct_selected_cards_img_filename_list(cards)
  session['game_cards'] = cards
  
  n_suggestions = 16
  unique_code_levels = 2

  suggested_splits_cards, split_code_scores = utils.get_suggestions(cards, int(n_suggestions), int(unique_code_levels))
  # Shuffle order
  max_code_score = max(split_code_scores)
  rel_split_code_scores = [round(100*score/max_code_score,1) for score in split_code_scores]
  rank = list(range(1, len(suggested_splits_cards)+1))
  split_options = list(zip(suggested_splits_cards, rel_split_code_scores, rank))
  
  shuffle(split_options)
  session['game_split_options'] =  split_options

  suggested_splits_imgs = [[utils.construct_concat_cards_img(card_set, app_root_path) for card_set in split_det[0]] for split_det in split_options]

  return render_template(
    'game.html', 
    title='Game', 
    dealt_img_filenames=dealt_card_img_filenames,
    suggested_split_imgs=suggested_splits_imgs
  )

@app.route('/game-play-split/<split_no>')
def game_play_split(split_no):
  split_no = int(split_no)
  if session.get('game_split_options') is None:
    return redirect(url_for('play_game'))
  split_options = session['game_split_options']
  rel_score = split_options[split_no-1][1]
  rank = split_options[split_no-1][2]
  n_splits = len(split_options)

  split_options = sorted(split_options, key=lambda x: x[2])
  print(f'split_options: {split_options}')
  ranked_splits_imgs = [[utils.construct_concat_cards_img(card_set, app_root_path) for card_set in split_det[0]] for split_det in split_options]
  split_scores = [split[1] for split in split_options]
  del session['game_cards']
  del session['game_split_options']
  return render_template(
    'gameplay.html', 
    title='Game Results',
    rel_score=rel_score, 
    rank=rank, 
    n_splits=n_splits, 
    ranked_splits_imgs=ranked_splits_imgs,
    split_scores=split_scores
  )