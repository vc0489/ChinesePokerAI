class TestBaseClass:
  class_var = 0

  def __init__(self):
    print(TestBaseClass.class_var)
    print(self.__class__)
    print(self.__class__.class_var)
    return

  def A(self):
    return 1

  def run_A(self):
    return self.A()
class TestClass(TestBaseClass):

  class_var = 1

  def __init__(self):
    super().__init__()
    print (TestClass.class_var)
    print (self.__class__)
    print (self.__class__.class_var)

  def A(self):
    return 2