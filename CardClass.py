from ExceptionClasses import UnknownCardStrengthTypeError, InvalidCardSuitError, InvalidCardNumberError
import CardConstants as CC
import itertools
# Suit
# C = Clubs
# D = Diamonds
# H = Hearts
# S = Spades

class CardClass:
  def __init__(self, suit, number, card_strength_type='Standard'):
    
    
    self.card_strength_type = card_strength_type.upper()
    self._validate_card_strength_type()

    self.suit_name_map = None
    self.full_suit_name_map = None
    self.short_suit_name_map = None
    self.full_number_name_map = None
    self.short_number_name_map = None
    self._initialise_card_strength_type_constants()
    
    number = str(number)
    self.number = None
    self.full_number = None
    self._validate_number(number)
    
    self.suit = None
    self.full_suit = None
    self._validate_suit(suit)

    # These will be initilialised by DeckClass
    self.number_strength_ind = None
    self.suit_strength_ind = None
    return
  
  def _validate_card_strength_type(self):
    if self.card_strength_type != 'STANDARD':
      print(self.card_strength_type + ' not valid, defaulting to STANDARD')
      self.card_strength_type = 'STANDARD'
    return

  def _initialise_card_strength_type_constants(self):
    self.suit_name_map = CC.__dict__[self.card_strength_type + '_suit_name_map']
    self.full_suit_name_map = CC.__dict__[self.card_strength_type + '_full_suit_name_map']
    self.short_suit_name_map = CC.__dict__[self.card_strength_type + '_short_suit_name_map']
    
    self.number_name_map = CC.__dict__[self.card_strength_type + '_number_name_map']
    self.full_number_name_map = CC.__dict__[self.card_strength_type + '_full_number_name_map']
    self.short_number_name_map = CC.__dict__[self.card_strength_type + '_short_number_name_map']

    #self._get_suit_number_strength_order()
    return
  
  def _validate_number(self, number):
    if number not in self.number_name_map:
      raise InvalidCardNumberError

    if number in self.full_number_name_map:
      self.full_number = self.full_number_name_map[number]
      self.number = number
    else:
      self.full_number = number
      self.number = self.short_number_name_map[number]
    return
  
  def _validate_suit(self, suit):
    if suit not in self.suit_name_map:
      raise InvalidCardSuitError
    
    if suit in self.full_suit_name_map:
      self.full_suit = self.full_suit_name_map[suit]
      self.suit = suit
    else:
      self.full_suit = suit
      self.suit = self.short_suit_name_map[suit]
    return

  def __repr__(self):
    return_string = f'{self.suit}{self.number}'
    return return_string
  
  def __format__(self, spec):
    if spec in (None, '', 'S'):
      return f'{self.suit}{self.number}'
    elif spec == 'F':
      return f'{self.full_number} of {self.full_suit}'
    else:
      return f'spec={spec} not supported'
  
  # This (apart from the indices) should be in a deck object otherwise will be redundant information
  def _get_suit_number_strength_order(self):
    if self.card_strength_type in CC.suit_number_strength_orders:
      self.suit_strength_order = CC.suit_number_strength_orders[self.card_strength_type]['Suits']
      self.number_strength_order = CC.suit_number_strength_orders[self.card_strength_type]['Numbers']
      self.card_strength_order = self._get_card_strength_order()
      self.number_strength_index = self.number_strength_order.index(self.number)
      self.suit_strength_index = self.suit_strength_order.index(self.full_suit)

    else:
      raise UnknownCardStrengthTypeError
    return
  
  def _get_card_strength_order(self, suit_strength_order=None, number_strength_order=None):
    if suit_strength_order is None:
      suit_strength_order = self.suit_strength_order
    if number_strength_order is None:
      number_strength_order = self.number_strength_order
    
    card_strength_order = list(itertools.product(number_strength_order, suit_strength_order))

    return card_strength_order

  def _get_full_suit_name(self, suit):
    if isinstance(suit,str):
      full_name = self.full_suit_name_map[suit]
    else:
      full_name = [self.full_suit_name_map[s] for s in suit]
    return full_name



  # Does not belong here as card strength is no longer a property of the card
  # UNLESS feed in card strength type as a variable
  def compare_strength(self, card):


    #if self.suit_strength_order == 'Standard':
    #  pass
    #else:
    #  raise UnknownSuitStrengthError
    #return
    return