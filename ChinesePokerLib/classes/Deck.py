import random
from itertools import product
from deprecated import deprecated

import ChinesePokerLib.vars.CardConstants as CConst
from ChinesePokerLib.classes.Card import Card

class Deck():
  def __init__(self, deck_type='STANDARD', order_type='Random'):
    #self.cards = []
    self.deck_type = deck_type

    suit_number_strength_order = CConst.suit_number_strength_orders[deck_type]
    self.suit_strength_order = suit_number_strength_order['Suits']
    self.number_strength_order = suit_number_strength_order['Numbers']
    
    # deck_card_order looks like: 
    # [
    #   ('S', 'A'),
    #   ('S', 'K'),
    #   ('S', 'Q'),
    #   ...
    #   ('S', '2'),
    #   ('H', 'A'),
    #   ...
    #   ('H', '2'),
    #   ('D', 'A'),
    #   ...
    #   ('D', '2'),
    #   ('C', 'A'),
    #   ...
    #   ('C', '2'),
    # ]
    self.deck_card_order = list(product(suit_number_strength_order['Suits'], suit_number_strength_order['Numbers']))
    
    self._gen_deck()
    
    if order_type == 'Random':
      self.shuffle()
    #if not deck_type or deck_type == 'Standard':
    #  self.initialise_deck(deck_type)
    return

  def __repr__(self):
    deck_string = ','.join([format(card) for card in self.deck])
    
    return_string = f'Deck Type: {self.deck_type}\n' + \
                    f'Deck: {deck_string}'
                     
    return return_string

  def _gen_deck(self):
      
    deck = [Card(suit,number) for suit, number in self.deck_card_order]

    self.deck = self._get_card_strength_indices(deck)
    self.inds_of_deck_card_order = list(range(len(self.deck)))

    return
  
  def _get_card_strength_indices(self, deck):
    for card in deck:
      card.number_strength_ind = self.number_strength_order.index(card.number)
      card.suit_strength_ind = self.suit_strength_order.index(card.suit)
      card.deck_card_ind = self.deck_card_order.index((card.suit,card.number))
    return deck
  
  def index(self, card_str, deck_card_strs=None):
    if deck_card_strs is None:
      deck_card_strs = self._gen_deck_card_strs()
    
    if isinstance(card_str, str):
      return deck_card_strs.index(card_str)
    elif isinstance(card_str, list):
      return [deck_card_strs.index(card) for card in card_str]
  
  def _gen_deck_card_strs(self):
    return [str(card) for card in self.deck]

  @deprecated
  def _find_cards_in_deck(self, card_strs):
    """Return indices of list of cards in current deck (self.deck)

    Args:
        card_strs (list[str]): e.g. ['S2', 'D5', 'CJ']

    Returns:
        [list]: List of indices of cards in deck
    """
    
    deck_card_strs = self.gen_deck_card_strs()
    card_inds = [deck_card_strs.index(card_str) for card_str in card_strs]
    return card_inds



  def shuffle(self):
    shuffled_deck = list(zip(self.deck, self.inds_of_deck_card_order))
    random.shuffle(shuffled_deck)
    
    new_inds = list(range(len(self.deck)))
    self.deck = [card[0] for card in shuffled_deck]
    shuffled_inds = [(card[1], new_inds[i]) for i, card in enumerate(shuffled_deck)]
    shuffled_inds = sorted(shuffled_inds, key=lambda x: x[0])
    self.inds_of_deck_card_order = [ind[1] for ind in shuffled_inds]
    return 

  def sort_deck_by_strength(self, deck=None, ascending=False, number_first=True, deck_type='Standard'):
    if deck is None:
      deck = self.deck

    number_inds = [card.number_strength_ind for card in deck]
    suit_inds = [card.suit_strength_ind for card in deck]

    if number_first:
        to_zip = [self.deck, number_inds, suit_inds]  
    else:
        to_zip = [self.deck, number_inds, suit_inds]
    
    zipped = list(zip(*to_zip))

    sorted_deck = sorted(zipped, reverse=ascending, key=lambda x: (x[1], x[2]))
    sorted_deck = [card[0] for card in sorted_deck]
    return sorted_deck

  #def initialise_deck(self, deck_type='Standard', order_type='Random'):
  #  return

  def add_cards(self, to_add):
    return
  
  def remove_cards(self, to_remove):
    return
  
  def deal_cards(self, n_hands=4, n_cards_per_hand=None, shuffle_first=True):
    #if deck is None:
    #  deck = self.deck

    if shuffle_first:
      self.shuffle()
    #  deck = self.shuffle(deck)


    if n_cards_per_hand is None:
      n_cards_to_deal = len(self.deck)  
    else:
      n_cards_to_deal = n_hands * n_cards_per_hand

    hands = [ [] for hI in range(n_hands)]
    for cI in range(n_cards_to_deal):
      hands[cI % n_hands].append(self.deck[cI])
    return hands
  
  def deal_partially_custom_cards(self, custom_cards, n_hands=4, n_cards_per_hand=None, shuffle_first=True):
    
    if shuffle_first:
      self.shuffle()
      
    if not isinstance(custom_cards[0], list):
      custom_cards = [custom_cards] + [[] for _ in range(n_hands-1)]
    hands_card_inds = []
    
    all_custom_card_inds = []
    n_custom_cards = 0
    for hI in range(n_hands):
      if len(custom_cards[hI]) == 0:
        hands_card_inds.append([])
      else:
        hand_custom_card_inds = self.deal_custom_hand(custom_cards[hI], True)
        all_custom_card_inds += hand_custom_card_inds
        n_custom_cards += len(hand_custom_card_inds)
        hands_card_inds.append(hand_custom_card_inds)

    if n_cards_per_hand is None:
      n_cards_per_hand = len(self.deck)/n_hands
      n_cards_to_deal = len(self.deck) 

    else:
      n_cards_to_deal = n_hands * n_cards_per_hand
    
    n_cards_to_deal -= n_custom_cards
    
    hI = 0 # Hand index
    cI = 0 # Actual card index in deck
    for dI in range(n_cards_to_deal): # Dealt card number index
      while cI in all_custom_card_inds:
        cI += 1
      
      while len(hands_card_inds[hI]) == n_cards_per_hand:
        hI = (hI+1) % n_hands
      
      hands_card_inds[hI].append(cI)
      cI += 1
      hI = (hI+1) % n_hands
    
    hands = [[self.deck[ind] for ind in inds] for inds in hands_card_inds]
    return hands
  
  def deal_custom_hand(self, these_cards, ret_inds=False):
    # these_cards possibilities
    # Option1: [(suit1, number1), (suit2, number2), etc.]
    # Option2: container of [suit][number] strings
    # Option3: single string of space- and/or comma-separated [suit][number] with or without brackets
    

    # Convert input cards to Option2
    these_cards = self._convert_list_of_cards_from_user(these_cards)

    card_inds = self.index(these_cards)
    
    if ret_inds:
      return card_inds

    hand = [self.deck[ind] for ind in card_inds]
    
    return hand

  def _convert_list_of_cards_from_user(self, cards_input):
    """Convert to list of [suit][number] strings

    Args:
        cards (list): Possible options:
          # [1]: [(suit1, number1), (suit2, number2), etc.]
          # [2]: container of [suit][number] strings  - no conversion required
          # [3]: single string of space- and/or comma-separated [suit][number] with or without brackets
    """
    if isinstance(cards_input[0], (tuple, list)) and len(cards_input[0]) == 2:
      # Simply concatenate strings
      cards_output = [item[0]+item[1] for item in cards_input]
    
    else:
      if isinstance(cards_input, str):

        remove_chars = "()[]"
        
        for char in remove_chars:
          cards_input = cards_input.replace(char, "")
        
        if ',' in cards_input:
          cards_input = [card_str.strip() for card_str in cards_input.split(',')]
        else:
          cards_input = cards_input.split()
      
      # Correct format already
      elif isinstance(cards_input[0], str):
        pass
      
      elif isinstance(cards_input[0], Card):
        cards_input = [str(card) for card in cards_input]
      cards_output = cards_input
      
    return cards_output
