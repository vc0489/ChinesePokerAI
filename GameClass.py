from DeckClass import DeckClass
from PlayerClass import PlayerClass

class GameClass:
  
  def __init__(self):
    self.deck = DeckClass()

    return
  
  
  def play_game(self):
    hands = self.deal_cards()
    return
  
  def deal_cards(self):
    hands = self.deck.deal_card()
    return hands