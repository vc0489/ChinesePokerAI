import random
from itertools import product

import ChinesePokerLib.vars.CardConstants as CConst
from ChinesePokerLib.classes.CardClass import CardClass

class DeckClass():
  def __init__(self, deck_type='STANDARD', order_type='Random'):
    #self.cards = []
    self.deck_type = deck_type

    suit_number_strength_order = CConst.suit_number_strength_orders[deck_type]
    self.suit_strength_order = suit_number_strength_order['Suits']
    self.number_strength_order = suit_number_strength_order['Numbers']
    
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
      
    deck = [CardClass(suit,number) for suit, number in self.deck_card_order]

    self.deck = self._get_card_strength_indices(deck)
    self.inds_of_deck_card_order = list(range(len(self.deck)))

    return
  
  def _get_card_strength_indices(self, deck):
    for card in deck:
      card.number_strength_ind = self.number_strength_order.index(card.number)
      card.suit_strength_ind = self.suit_strength_order.index(card.suit)
      card.deck_card_ind = self.deck_card_order.index((card.suit,card.number))
    return deck
  
  def _find_cards_in_deck(self, suit_number_sets):
    """[summary]

    Args:
        suit_number_sets ([type]): e.g. [('S','2'), ('D','5'), ('C','J')]

    Returns:
        [list]: List of indices of cards in deck
    """

    deck_suit_number_sets = [(card.suit, card.number) for card in self.deck]
    card_inds = [deck_suit_number_sets.index(sn_set) for sn_set in suit_number_sets]
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
  
  def deal_custom_hand(self, these_cards):
    # these_cards possibilities
    # Option1: [(suit1, number1), (suit2, number2), etc.]
    # Option2: container of [suit][number] strings
    # Option3: single string of space- and/or comma-separated [suit][number] with or without brackets
    

    # Detect input type
    if isinstance(these_cards[0], (tuple, list)) and len(these_cards[0]) == 2:
      pass
    else:
      if isinstance(these_cards, str):

        remove_chars = "()[]"
        
        for char in remove_chars:
          these_cards = these_cards.replace(char, "")
        
        if ',' in these_cards:
          these_cards = [card_str.strip() for card_str in these_cards.split(',')]
        else:
          these_cards = these_cards.split()
      
      elif isinstance(these_cards[0], str):
        pass
      
      these_cards = [(card_str[0], card_str[1:]) for card_str in these_cards]

    hand = []
    card_inds = self._find_cards_in_deck(these_cards)
    for card_ind in card_inds:
      hand.append(self.deck[card_ind])
    
    return hand