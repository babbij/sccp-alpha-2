import logging

import rdflib
import json

from .base import BaseStore

__all__ = ['LocalStore']

# Store for local claims.
class LocalStore(BaseStore):
  def __init__(self):
    super(LocalStore, self).__init__()

  def triples(self, triplein, context = None):
    logging.debug(f'triples triplein= {triplein}')
    return super(LocalStore, self).triples(triplein, context)


if __name__ == '__main__':  
  store = LocalStore()
  graph = rdflib.Graph(store)
  
  
  
  graph.update("""
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>

    INSERT DATA { 
      <https://twitter.com/ijmad8x>  foaf:name 'Ian Maddison'.
      <https://twitter.com/ijmad8x>  foaf:age 35
    }
    """
  )
  
  store.add(('foo', 'bar', 'arooo'), context = 'alice')
  store.add(('foo', 'bar', 'arooo'), context = 'bob')
  store.add(('foo', 'bar', 'arooo'), context = 'charlie')
  
  for (triple, context) in store.triples(('foo', None, None)):
    print ('triple:', triple)
    print ('context:', list(context))