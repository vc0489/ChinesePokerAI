import random
import CardConstants as CConst
from CardClass import CardClass
import random

class DeckClass():
  def __init__(self, deck_type='STANDARD', order_type='Random'):
    self.cards = []
    self.deck_type = deck_type

    suit_number_strength_order = CConst.suit_number_strength_orders[deck_type]
    self.suit_strength_order = suit_number_strength_order['Suits']
    self.number_strength_order = suit_number_strength_order['Numbers']

    self.deck = self._gen_deck()
    

    #if not deck_type or deck_type == 'Standard':
    #  self.initialise_deck(deck_type)
    return

  def __repr__(self):
    deck_string = ','.join([format(card) for card in self.deck])
    
    return_string = f'Deck Type: {self.deck_type}\n' + \
                    f'Deck: {deck_string}'
                     
    return return_string

  def _gen_deck(self, deck_type=None, order_type='Random'):
    if deck_type is None:
      deck_type = self.deck_type

    if deck_type == 'STANDARD':
      
      suits = [item[0] for item in CConst.STANDARD_suit_name_map_raw]
      numbers = [item[0] for item in CConst.STANDARD_number_name_map_raw]
      
      deck = [CardClass(suit,number) for suit in suits for number in numbers]

      deck = self._get_card_strength_indices(deck)

      if order_type == 'Random':
        deck = self.shuffle(deck)  
    return deck
  
  def _get_card_strength_indices(self, deck):
    for card in deck:
      card.number_strength_ind = self.number_strength_order.index(card.number)
      card.suit_strength_ind = self.suit_strength_order.index(card.full_suit)
      
    return deck

  def shuffle(self, deck=None):
    if deck is None:
      deck = self.deck
    random.shuffle(deck)

    return deck

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
  
  def deal_cards(self, n_hands=4, n_cards_per_hand=None, deck=None, shuffle_first=True):
    if deck is None:
      deck = self.deck

    if shuffle_first:
      deck = self.shuffle(deck)

    if n_cards_per_hand is None:
      n_cards_to_deal = len(self.deck)  
    else:
      n_cards_to_deal = n_hands * n_cards_per_hand

    hands = [ [] for hI in range(n_hands)]
    for cI in range(n_cards_to_deal):
      hands[cI % n_hands].append(deck[cI])
    return hands