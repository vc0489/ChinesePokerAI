import itertools

def sliding_pairs_in_iterable(iterable):
  """Return iterable of sliding pairs from input iterable

  Arguments:
      iterable {iterable} -- [description]

  Returns:
      iterable -- [description]
  """
  a, b = itertools.tee(iterable) # Create two identical iterables
  next(b, None)
  
  return zip(list(a),list(b))

def flattened_list(container_of_containers):
  return list(itertools.chain.from_iterable(container_of_containers))