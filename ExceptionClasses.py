# define Python user-defined exceptions
class Error(Exception):
   """Base class for other exceptions"""
   pass

class UnknownCardStrengthTypeError(Error):
   """Raised when card strength type is not recognised"""
   pass

class InvalidCardNumberError(Error):
   """Raised when invalid number is provided when instantiating a CardClass object"""
   pass


class InvalidCardSuitError(Error):
   """Raised when invalid suit is provided when instantiating a CardClass object"""
   pass