from itertools import tee
import numpy as np

from ChinesePokerLib.modules.UtilityFunctions import sliding_pairs_in_iterable

class TwoWayDict(dict):
  def __len__(self):
    return dict.__len__(self) / 2
  
  def __setitem__(self, key, value):
    dict.__setitem__(self, key, value)
    dict.__setitem__(self, value, key)


class VarChecker():
  def __init__(self):
    return

  def check_one_of_each_int_in_range(self, numbers, start_int, end_int):
    """Check that there is exactly one of each int between start_int and end_int inclusive
    in items.

    Arguments:
        items {[type]} -- [description]
        start_int {[type]} -- [description]
        end_int {[type]} -- [description]
    """

    # First check have expected number of items
    
    exp_n_nums = end_int-start_int+1
    if len(numbers) != exp_n_nums:
      return False
    expect_this = list(range(start_int, end_int+1))
    items = sorted(numbers)

    for i in range(exp_n_nums):
      if items[i] != expect_this[i]:
        return False

    return True
  
  def check_lengths_of_iterable(self, iterable, expected_lengths):
    if len(iterable) != len(expected_lengths):
      return False

    for i, item in enumerate(iterable):
      if len(item) != expected_lengths[i]:
        return False

    return True
  
  @classmethod
  def _check_pairwise_comparison_over_iterable(self, iterable, check_func):
    return all(check_func(a, b) for a, b in sliding_pairs_in_iterable(iterable))

  @classmethod
  def check_is_sorted(cls, iterable, ascending=True, allow_equal=True):
    """Check if iterable is sorted.

    Args:
        iterable ([type]): [description]
        ascending (bool, optional): [description]. Defaults to True.
        allow_equal (bool, optional): [description]. Defaults to True.

    Returns:
        [bool]: Whether iterable is sorted
    """
    
    if len(iterable) == 1:
      return True
    if ascending is True:
      if allow_equal is True:
        return cls._check_pairwise_comparison_over_iterable(iterable, lambda a, b: a <= b)
      else:
        return cls._check_pairwise_comparison_over_iterable(iterable, lambda a, b: a < b)
    elif ascending is False:
      if allow_equal is True:
        return self._check_pairwise_comparison_over_iterable(iterable, lambda a, b: a >= b)
      else:
        return self._check_pairwise_comparison_over_iterable(iterable, lambda a, b: a > b)
  
  @classmethod
  def check_all_elements_in_container_of_given_types(cls, container, types):
    return all([isinstance(item, types) for item in container])
  
  @classmethod
  def check_not_consecutive(cls, iterable, ascending=True):
    if len(iterable) == 1:
      return True

    iterable = np.array(iterable)
    diff = np.diff(iterable)
        
    if ascending is False:
      diff = -diff

    return ~np.all(diff==1)

  @classmethod
  def check_all_different(cls, iterable):
    return len(iterable) == len(set(iterable))
    
