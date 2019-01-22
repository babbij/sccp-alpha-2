import logging

import dht, patterns, search, keys

from claim import create_claim, Pointer, Claim
from abe.abe import DEFAULT_ABE

from shared.kahn import kahnsort


def try_decrypt(sub, pre, obj, pointer):
  # we have searched for a pointer based on (sub, pre, obj)
  # this will be decryptable with various share keys
  # either matching (sub, pre, obj) directly but also potentially
  # being less specific. so we will anticipate thoss less
  # specific patterns and look for a key that might enable
  # access to the data by doing a full pattern generation
  
  possible_patterns = list(patterns.make_patterns(sub, pre, obj))
  logging.debug(f'possible_patterns = {possible_patterns}')
  for hash in possible_patterns:
    found = False
    for key in keys.search_key(hash):
      found = True
      try:
        logging.debug(f'Trying decrypt {pointer[0:10]}...{pointer[-10:]} with ({key[0][0:10]}...{key[0][-10:]},{key[1][0:10]}...{key[1][-10:]})')
        cleartext = DEFAULT_ABE.decrypt(pointer, key)
        return Pointer.from_hex(cleartext)
      except Exception as e:
        logging.debug('Failed to decrypt')

    if not found:
      logging.debug('No share key, moving on...')

  return None


def matches_with_decrypt(triple, decrypt_fn):
  (sub, pre, obj) = triple
  logging.debug(f'Find matches for({sub}, {pre}, {obj})')
  
  # protect against bad requests for (None, None, None) or (?, None, ?)
  if not sub and not obj:
    raise RuntimeException('Searching for (None, None, None) or (None, ?, None) is prohibited)')
  
  # get matching pointer
  pointer_pattern = patterns.make_pattern(sub, pre, obj)
  pointers_raw = dht.get_pointers(pointer_pattern)
  
  # gotta see if we can decrypt these pointers
  pointers = map(lambda p : decrypt_fn(sub, pre, obj, p), pointers_raw)
  claims = {}
  
  for pointer in pointers:
    if pointer:
      claim = Claim.from_hex(dht.get_claim(pointer.id), pointer.key)
      logging.info(f'Claim found= {pointer.id[0:10]}...{pointer.id[-10:]}')
      claims[claim.get_id()] = claim
  
  # topgraphical sort + return
  return kahnsort(claims.values())


def matches(triple):
  return matches_with_decrypt(triple, try_decrypt)