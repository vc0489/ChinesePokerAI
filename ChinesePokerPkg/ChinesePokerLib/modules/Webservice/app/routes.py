#from ChinesePokerLib.modules.Webservice.app import app
from flask import render_template, flash, redirect, url_for, session, send_file, request
from app import app, utils
from app.forms import SuggestForm
import base64
from io import StringIO
from pathlib import Path
from timeit import default_timer as timer
from random import shuffle

#card_images_dir = Path(app.root_path)
app_root_path = Path(app.root_path)
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

@app.route('/game')
def play_game():

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