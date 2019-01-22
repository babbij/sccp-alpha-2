import hashlib
import urllib
import logging
import rdflib

import cbor2

from shared.repr import term_to_repr, repr_to_value


def hash_values(sub, pre, obj):
  # logging.debug(f'hash_values {sub} {pre} {obj}')
  
  canon = cbor2.dumps([sub, obj, pre])
  sha_signature = hashlib.sha256(canon).hexdigest()
  
  # prefixing 'a' here makes all signatures compatible
  # with OpenABE which doesn't like attributes beginning with digits
  # it also gives us an opportunity to version the hash!
  return 'a' + sha_signature


def hash_triple(triple):
  (sub, pre, obj) = triple
  return hash_values(
    repr_to_value(term_to_repr(sub)) if sub else None,
    repr_to_value(term_to_repr(pre)) if pre else None,
    repr_to_value(term_to_repr(obj)) if obj else None
  )


# function works on both fully filled out tuples and partials
def make_patterns(sub, pre, obj):
  logging.debug(f'make_patterns: {sub} {pre} {obj}')
  
  hash_patterns = set([
    (sub, pre, obj),
    (sub, pre, None), (None, pre, obj), (sub, None, obj),
    (sub, None, None), (None, None, obj)
  ])
  
  # remove patterns we never use just in case they crept in through
  # some odd combinations of the input parameters being 'None'.
  hash_patterns.discard((None, None, None))
  hash_patterns.discard((None, pre, None))
  
  # map to hash codes  
  hashes = { triple: hash_triple(triple) for triple in hash_patterns }
  logging.debug(f'hashes: {hashes}')
  return set([ hash for triple, hash in hashes.items() ])


def make_pattern(sub, pre, obj):
  logging.debug(f'make_pattern: {sub} {pre} {obj}')
  return hash_triple((sub, pre, obj))


if __name__ == '__main__':
  logging.basicConfig(level=logging.DEBUG, format='%(levelname)s\t%(message)s')

  sub = rdflib.term.URIRef( 'https://twitter.com/ijmadx' )
  pre = rdflib.term.URIRef( 'http://xmlns.com/foaf/0.1/name' )
  obj = rdflib.term.Literal( 'Ian Maddison' )
  
  print (make_patterns(sub, pre, obj))

