import os, logging
import json
import requests
import binascii
import traceback

import cbor2

from expiringdict import ExpiringDict
from shared.repr import repr_to_triple, triple_to_repr
from shared.kahn import kahnsort


DHT_ENDPOINT = os.environ['DHT_ENDPOINT']
DHT_CACHE = {}#ExpiringDict(max_len=100, max_age_seconds=60)


# define a class for extensiblity reasons
class CachedMatch:
  def __init__(self, triple, ids):
    self.triple = triple
    self.ids = ids
    
def make_cache_key(triple):
  return binascii.hexlify(cbor2.dumps(triple_to_repr(triple))).decode('US-ASCII')


class FetchedClaim:
  def __init__(self, json):
    self.id = json['inner_envelope']['hashkey']
    
    self.removed = list(map(
      repr_to_triple, json['inner_envelope']['contents']['removed']
    ))
    
    self.added = list(map(
      repr_to_triple, json['inner_envelope']['contents']['added']
    ))
    
    self.links = list(map(
      lambda link: link['ref'], json['links']
    ))

  def get_id(self):
    return self.id

  def get_removed(self):
    return self.removed

  def get_added(self):
    return self.added
    
  def get_predecessors(self):
    return self.links

  def __repr__(self):
    return f'FetchedClaim(ID={self.id}, REMOVED={self.removed}, ADDED={self.added} LINKS={self.links})'


def fetch_matches(triple, store, context):  
  logging.debug(f'Fetch matches for {triple}')
  (sub, pre, obj) = triple

  # we don't support retrieval of all triples
  # or predicate-only searches
  if sub is None and obj is None:
    raise ValueError('Searching for (?, p, ?) or (?, ?, ?) is not supported')

  # check cache
  # don't need to store the whole claim (as triples themselves go to store)
  # but still need the IDs because we have to track links
  cache_key = make_cache_key(triple)
  cached_match = DHT_CACHE.get(cache_key)
  if cached_match:
    logging.debug(f'Cache hit for {cache_key}')
    return None
  else:
    logging.debug(f'Cache miss for {cache_key}')

  # build a request to fetch triples matching this pattern
  response = requests.get(DHT_ENDPOINT + '/matches', params={
    'pattern': json.dumps(triple_to_repr(triple))
  })

  if response.status_code != 200:
    raise RuntimeError(f'DHT returned {response.status_code}')

  # this will be the claims
  claims = list(map(lambda c : FetchedClaim(c), response.json()))
  return kahnsort(claims)
