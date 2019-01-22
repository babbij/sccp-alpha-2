import os, logging
import pickledb

import patterns
from shared.repr import from_n3


KEY_DB_PATH = os.environ['KEY_DB_PATH']

db = pickledb.load(KEY_DB_PATH, True) 

# print (db.db)


def record_key(pattern, key):
  # keys are a tuple of (public, share)
  # JSON doesn't distinguish lists from tuples
  # turn tuple in to list for exist check
  
  if key not in search_key(pattern):
    logging.debug(f'Recording key {pattern} -> ({key[0][0:10]}...{key[0][-10:]},{key[1][0:10]}...{key[1][-10:]})')

    if not db.exists(pattern):
      db.lcreate(pattern)

    db.ladd(pattern, list(key))


def search_key(pattern):
  logging.debug(f'Looking for key for {pattern}')
  if db.exists(pattern):
    # keys are a tuple of (public, share)
    # JSON doesn't distinguish lists from tuples
    # turn list back in to tuple
    return list(map(lambda l : tuple(l), db.lgetall(pattern)))
  else:
    return []
  

if __name__ == '__main__':
  pattern = patterns.make_pattern(
    from_n3('<http://foo/bar>'),
    None,
    from_n3('"32"')
  )
  
  print ('Recording Key:', pattern)
  record_key(pattern, ('blah', 'blee'))
  
  print('Search Result:', search_key(pattern))
  
  pattern = patterns.make_pattern(
    from_n3('<http://bar/foo>'),
    None,
    from_n3('"35"')
  )
  
  print ('Recording Key:', pattern)
  
  record_key(pattern, ('blam', 'blaaa'))
  print('Search Result:', search_key(pattern))