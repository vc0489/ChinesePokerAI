class TestCardError(Exception):

class TestCardValueError(ValueError, TestCardError):
