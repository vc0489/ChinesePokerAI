import itertools
from typing import Union, Iterable, List, Tuple
from deprecated import deprecated

from ChinesePokerLib.classes.ExceptionClasses import UnknownCardStrengthTypeError, InvalidCardSuitError, InvalidCardNumberError, InvalidCardFormatSpecError
import ChinesePokerLib.vars.CardConstants as CC

# Suit
# C = Clubs
# D = Diamonds
# H = Hearts
# S = Spades

class CardClass:
  card_strength_type='STANDARD'
  suit_name_map = CC.__dict__[card_strength_type + '_suit_name_map']
  full_suit_name_map = CC.__dict__[card_strength_type + '_full_suit_name_map']
  short_suit_name_map = CC.__dict__[card_strength_type + '_short_suit_name_map']

  number_name_map = CC.__dict__[card_strength_type + '_number_name_map']
  full_number_name_map = CC.__dict__[card_strength_type + '_full_number_name_map']
  short_number_name_map = CC.__dict__[card_strength_type + '_short_number_name_map']

  def __init__(
    self, 
    suit: str, 
    number: Union[str, int],
    #card_strength_type: str='STANDARD',
  ):
    
    #self.card_strength_type = card_strength_type.upper()
    #self._validate_card_strength_type()

    #self._initialise_card_strength_type_constants()
    
    number = str(number)
    self._validate_number(number)
    
    self._validate_suit(suit)

    # These will be initilialised by DeckClass
    self.number_strength_ind = None
    self.suit_strength_ind = None
    self.deck_card_ind = None
    return
  
  @classmethod
  def init_from_str(cls, card_str):
    return cls(card_str[0], card_str[1:])
  """
  def _validate_card_strength_type(self):
    if self.card_strength_type != 'STANDARD':
      raise UnknownCardStrengthTypeError(f'card_stregnth_type {self.card_strength_type} not valid.')
      
    return
  """

  """
  def _initialise_card_strength_type_constants(self):
    #self.suit_name_map = CC.__dict__[self.card_strength_type + '_suit_name_map']
    #self.full_suit_name_map = CC.__dict__[self.card_strength_type + '_full_suit_name_map']
    #self.short_suit_name_map = CC.__dict__[self.card_strength_type + '_short_suit_name_map']

    #self.number_name_map = CC.__dict__[self.card_strength_type + '_number_name_map']
    #self.full_number_name_map = CC.__dict__[self.card_strength_type + '_full_number_name_map']
    #self.short_number_name_map = CC.__dict__[self.card_strength_type + '_short_number_name_map']

    #self._get_suit_number_strength_order()
    return
  """

  def _validate_number(self, number: str):
    self.number = None
    self.full_number = None

    if number not in self.number_name_map:
      raise InvalidCardNumberError(f'number {number} not valid.')

    if number in self.full_number_name_map:
      self.full_number = self.full_number_name_map[number]
      self.number = number
    else:
      self.full_number = number
      self.number = self.short_number_name_map[number]
    return
  
  def _validate_suit(self, suit: str):
    self.suit = None
    self.full_suit = None

    if suit not in self.suit_name_map:
      raise InvalidCardSuitError(f'suit {suit} not valid.')
    
    if suit in self.full_suit_name_map:
      self.full_suit = self.full_suit_name_map[suit]
      self.suit = suit
    else:
      self.full_suit = suit
      self.suit = self.short_suit_name_map[suit]
    return
  
  @classmethod
  def is_valid_suit_and_number(cls, suit, number):
    if suit in cls.full_suit_name_map and number in cls.full_number_name_map:
      return True
    else:
      return False
    
  def __repr__(self):
    """Representation = [Suit][number]

    Returns:
        [str] -- Representation
    """
    return_string = f'{self.suit}{self.number}'
    return return_string
  
  def __format__(self, spec):
    spec = spec.upper()
    if spec in (None, '', 'S'):
      return f'{self.suit}{self.number}'
    elif spec == 'F':
      return f'{self.full_number} of {self.full_suit}'
    else:
      raise InvalidCardFormatSpecError(f'spec {spec} not supported')
  
  # This (apart from the indices) should be in a deck object otherwise will be redundant information
  def _get_suit_number_strength_order(self):
    if self.card_strength_type in CC.suit_number_strength_orders:
      self.suit_strength_order = CC.suit_number_strength_orders[self.card_strength_type]['Suits']
      self.number_strength_order = CC.suit_number_strength_orders[self.card_strength_type]['Numbers']
      self.card_strength_order = self._get_card_strength_order()
      self.number_strength_index = self.number_strength_order.index(self.number)
      self.suit_strength_index = self.suit_strength_order.index(self.suit)

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

  def _get_full_suit_name(self, suit: Union[str, List[str], Tuple[str]]) -> Union[str, List[str]]:
    """Get full suit name(s) from shorthand

    Arguments:
        suit {str or List/Tuple of str} -- Shorthand suit string

    Returns:
        str or List[str] -- Full suit string
    """
    if isinstance(suit, str):
      full_name = self.full_suit_name_map[suit]
    else:
      full_name = [self.full_suit_name_map[s] for s in suit]
    return full_name



  # Does not belong here as card strength is no longer a property of the card
  # UNLESS feed in card strength type as a variable
  @deprecated
  def compare_strength(self, card):
    """[summary]

    Arguments:
        card {[type]} -- [description]

    Raises:
        UnknownSuitStrengthError: [description]
    """

    #if self.suit_strength_order == 'Standard':
    #  pass
    #else:
    #  raise UnknownSuitStrengthError
    #return
    return