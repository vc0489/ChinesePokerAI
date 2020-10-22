# define Python user-defined exceptions
class Error(Exception):
  """Base class for general exceptions"""
  pass



############################
### CardClass Exceptions ### 
############################
class CardError(Error):
  """Base class for exceptions relating to CardClass"""
  pass

class UnknownCardStrengthTypeError(CardError):
  """Raised when card strength type is not recognised"""
  pass

class InvalidCardNumberError(CardError):
  """Raised when invalid number is provided when instantiating a CardClass object"""
  pass


class InvalidCardSuitError(CardError):
  """Raised when invalid suit is provided when instantiating a CardClass object"""
  pass

class InvalidCardFormatSpecError(CardError):
  """Raised when invalid specification passed into __format__"""
  pass

############################
### HandClass Exceptions ### 
############################

class HandError(Error):
  """Base class for exceptions relating to HandClass"""
  pass

class HandSplitInfoError(HandError):
  """Raised when error occurs in the split info"""
  pass

class HandMissingScoringMethodError(HandError):
   """Raised when have scoring_tables but missing scoring_method"""
   pass 

############################
### GameClass Exceptions ### 
############################
class GameError(Error):
  """Base class for exceptions relating to GameClass"""
  pass

class InvalidGameModeError(GameError):
  """Raised when invalid game mode is provided when instantiating a GameClass object"""
  pass


###############################
### StrategyClass Exceptons ###
###############################
class StrategyError(Error):
  """Base class for exceptions relating to StrategyClass"""
  pass

class StrategyIDUsedError(StrategyError):
  """Raised when a strategy ID already exists in the DB"""
  pass

##############################
### DBFunctions Exceptions ###
##############################
class DBFunctionsError(Error):
  """Base class for exceptions relating to DBFunctions"""
  pass

class DBWriteError(DBFunctionsError):
  """Raised when failure when trying to write to DB"""
  pass


#################################
### CardGroupClass Exceptions ###
#################################
class CardGroupClassError(Error):
  """Base class for exceptions relating to CardGroupClass"""
  